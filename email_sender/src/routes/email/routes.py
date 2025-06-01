import os
import uuid
import smtplib
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from flask import Blueprint, request, jsonify, current_app, url_for
from datetime import datetime, timezone, timedelta
from models.email_tracking import EmailTracking, db
from routes.template.routes import replace_variables

email_bp = Blueprint('email', __name__)

# JST（日本標準時）のタイムゾーン定義
JST = timezone(timedelta(hours=9))

@email_bp.route('/send', methods=['POST'])
def send_email():
    data = request.json
    if not data or 'template_id' not in data or 'recipients' not in data or 'smtp' not in data:
        return jsonify({'error': 'Missing required data'}), 400
    
    template_id = data['template_id']
    recipients = data['recipients']
    smtp_config = data['smtp']
    
    # Validate SMTP configuration
    required_smtp_fields = ['host', 'port', 'username', 'password', 'sender_email', 'sender_name']
    for field in required_smtp_fields:
        if field not in smtp_config:
            return jsonify({'error': f'Missing SMTP configuration: {field}'}), 400
    
    # Get template
    template_path = os.path.join(current_app.root_path, 'static', 'templates', f"{template_id}.json")
    if not os.path.exists(template_path):
        return jsonify({'error': 'Template not found'}), 404
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            import json
            template_data = json.load(f)
        
        template_content = template_data['content']
        subject_template = template_data['subject']
        
        # Send emails
        results = []
        for recipient in recipients:
            tracking_id = str(uuid.uuid4())
            
            # Add tracking pixel to email content
            tracking_pixel_url = url_for('email.track_open', tracking_id=tracking_id, _external=True)
            tracking_pixel = f'<img src="{tracking_pixel_url}" width="1" height="1" alt="" style="display:none;" />'
            
            # Replace variables in template
            rendered_content = replace_variables(template_content, recipient)
            rendered_subject = replace_variables(subject_template, recipient)
            
            # Add tracking pixel to HTML content
            if '</body>' in rendered_content.lower():
                # </body>タグの直前に挿入
                rendered_content = rendered_content.replace('</body>', f'{tracking_pixel}</body>')
                rendered_content = rendered_content.replace('</BODY>', f'{tracking_pixel}</BODY>')
            elif '</html>' in rendered_content.lower():
                # </html>タグの直前に挿入
                rendered_content = rendered_content.replace('</html>', f'{tracking_pixel}</html>')
                rendered_content = rendered_content.replace('</HTML>', f'{tracking_pixel}</HTML>')
            else:
                # HTMLタグが見つからない場合は末尾に追加
                rendered_content += tracking_pixel
            
            # Send email
            try:
                # メールアドレスを取得（mail > メールアドレス > email の優先順位）
                recipient_email = ''
                if 'mail' in recipient:
                    recipient_email = recipient['mail']
                elif 'メールアドレス' in recipient:
                    recipient_email = recipient['メールアドレス']
                elif 'email' in recipient:
                    recipient_email = recipient['email']
                
                send_result = send_smtp_email(
                    smtp_config,
                    recipient_email,
                    rendered_subject,
                    rendered_content,
                    tracking_id
                )
                
                results.append({
                    'email': recipient_email,
                    'status': 'sent' if send_result else 'failed',
                    'tracking_id': tracking_id
                })
                
            except Exception as e:
                # メールアドレスを取得（mail > メールアドレス > email の優先順位）
                recipient_email = ''
                if 'mail' in recipient:
                    recipient_email = recipient['mail']
                elif 'メールアドレス' in recipient:
                    recipient_email = recipient['メールアドレス']
                elif 'email' in recipient:
                    recipient_email = recipient['email']
                
                results.append({
                    'email': recipient_email,
                    'status': 'failed',
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': f'Error sending emails: {str(e)}'}), 500

@email_bp.route('/track/<tracking_id>', methods=['GET'])
def track_open(tracking_id):
    """Track email open via 1x1 transparent pixel"""
    try:
        # Update tracking record
        tracking = EmailTracking.query.filter_by(tracking_id=tracking_id).first()
        if tracking:
            tracking.opened = True
            tracking.opened_at = datetime.now(JST)  # JSTで記録
            db.session.commit()
        
        # Return 1x1 transparent pixel
        pixel = base64.b64decode('R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7')
        response = current_app.make_response(pixel)
        response.headers.set('Content-Type', 'image/gif')
        return response
    except Exception as e:
        # Still return pixel even if tracking fails
        pixel = base64.b64decode('R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7')
        response = current_app.make_response(pixel)
        response.headers.set('Content-Type', 'image/gif')
        return response

@email_bp.route('/status', methods=['GET'])
def get_status():
    """Get email tracking status"""
    try:
        tracking_records = EmailTracking.query.all()
        results = []
        
        for record in tracking_records:
            results.append({
                'id': record.id,
                'email': record.email,
                'subject': record.subject,
                'sent_at': record.sent_at.isoformat() if record.sent_at else None,
                'status': record.status,
                'opened': record.opened,
                'opened_at': record.opened_at.isoformat() if record.opened_at else None,
                'tracking_id': record.tracking_id
            })
        
        return jsonify({
            'success': True,
            'tracking': results
        })
    except Exception as e:
        return jsonify({'error': f'Error retrieving tracking status: {str(e)}'}), 500

def send_smtp_email(smtp_config, recipient_email, subject, html_content, tracking_id):
    """Send email via SMTP and record tracking information"""
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{smtp_config['sender_name']} <{smtp_config['sender_email']}>"
        msg['To'] = recipient_email
        
        # Attach HTML content
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Connect to SMTP server and send
        with smtplib.SMTP(smtp_config['host'], int(smtp_config['port'])) as server:
            if smtp_config.get('use_tls', True):
                server.starttls()
            
            server.login(smtp_config['username'], smtp_config['password'])
            server.send_message(msg)
        
        # Record tracking information
        tracking = EmailTracking(
            email=recipient_email,
            subject=subject,
            status='sent',
            tracking_id=tracking_id,
            sent_at=datetime.now(JST)  # JSTで記録
        )
        db.session.add(tracking)
        db.session.commit()
        
        return True
    except Exception as e:
        # Record failed tracking
        try:
            tracking = EmailTracking(
                email=recipient_email,
                subject=subject,
                status='failed',
                tracking_id=tracking_id,
                sent_at=datetime.now(JST)  # JSTで記録
            )
            db.session.add(tracking)
            db.session.commit()
        except:
            pass
        
        raise e
