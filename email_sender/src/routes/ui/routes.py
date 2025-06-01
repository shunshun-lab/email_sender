import os
import csv
import json
from flask import Blueprint, render_template, current_app, send_from_directory, request, jsonify
from werkzeug.utils import secure_filename

ui_bp = Blueprint('ui', __name__, template_folder='templates')

@ui_bp.route('/')
def index():
    return render_template('index.html')

@ui_bp.route('/templates')
def templates():
    return render_template('templates.html')

@ui_bp.route('/send')
def send():
    return render_template('send.html')

@ui_bp.route('/tracking')
def tracking():
    return render_template('tracking.html')

@ui_bp.route('/api/upload-csv', methods=['POST'])
def upload_csv():
    """CSVファイルをアップロードして内容を返す"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'ファイルが選択されていません'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'ファイルが選択されていません'}), 400
        
        if not file.filename.lower().endswith('.csv'):
            return jsonify({'error': 'CSVファイルを選択してください'}), 400
        
        # CSVファイルを読み込み
        content = file.read().decode('utf-8')
        csv_reader = csv.DictReader(content.splitlines())
        
        # ヘッダーとデータを取得
        headers = csv_reader.fieldnames
        rows = list(csv_reader)
        
        # メールアドレス列の確認
        email_column = None
        for col in ['mail', 'メールアドレス', 'email']:
            if col in headers:
                email_column = col
                break
        
        if not email_column:
            return jsonify({'error': 'メールアドレス列（mail、メールアドレス、email）が見つかりません'}), 400
        
        return jsonify({
            'success': True,
            'headers': headers,
            'rows': rows[:10],  # 最初の10行のみプレビュー
            'total_count': len(rows),
            'email_column': email_column
        })
        
    except Exception as e:
        return jsonify({'error': f'CSVファイルの読み込みに失敗しました: {str(e)}'}), 500

@ui_bp.route('/api/templates', methods=['GET'])
def get_templates():
    """テンプレート一覧を取得"""
    try:
        templates_dir = os.path.join(current_app.root_path, 'static', 'templates')
        if not os.path.exists(templates_dir):
            os.makedirs(templates_dir)
        
        templates = []
        for filename in os.listdir(templates_dir):
            if filename.endswith('.json'):
                template_id = filename[:-5]  # .jsonを除去
                template_path = os.path.join(templates_dir, filename)
                
                try:
                    with open(template_path, 'r', encoding='utf-8') as f:
                        template_data = json.load(f)
                    
                    templates.append({
                        'id': template_id,
                        'name': template_data.get('name', template_id),
                        'subject': template_data.get('subject', ''),
                        'content': template_data.get('content', '')
                    })
                except:
                    continue
        
        return jsonify({
            'success': True,
            'templates': templates
        })
        
    except Exception as e:
        return jsonify({'error': f'テンプレート一覧の取得に失敗しました: {str(e)}'}), 500

@ui_bp.route('/api/templates', methods=['POST'])
def save_template():
    """テンプレートを保存"""
    try:
        data = request.json
        if not data or 'name' not in data or 'subject' not in data or 'content' not in data:
            return jsonify({'error': '必要なデータが不足しています'}), 400
        
        template_id = secure_filename(data['name'].replace(' ', '_'))
        templates_dir = os.path.join(current_app.root_path, 'static', 'templates')
        
        if not os.path.exists(templates_dir):
            os.makedirs(templates_dir)
        
        template_data = {
            'name': data['name'],
            'subject': data['subject'],
            'content': data['content']
        }
        
        template_path = os.path.join(templates_dir, f"{template_id}.json")
        with open(template_path, 'w', encoding='utf-8') as f:
            json.dump(template_data, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            'success': True,
            'template_id': template_id,
            'message': 'テンプレートが保存されました'
        })
        
    except Exception as e:
        return jsonify({'error': f'テンプレートの保存に失敗しました: {str(e)}'}), 500
