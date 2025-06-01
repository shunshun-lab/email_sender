import os
import uuid
import re
from flask import Blueprint, request, jsonify, current_app, render_template

template_bp = Blueprint('template', __name__)

@template_bp.route('/save', methods=['POST'])
def save_template():
    data = request.json
    if not data or 'template' not in data or 'subject' not in data:
        return jsonify({'error': 'Missing template or subject'}), 400
    
    template_content = data['template']
    subject = data['subject']
    template_id = str(uuid.uuid4())
    
    # Create templates directory if it doesn't exist
    templates_dir = os.path.join(current_app.root_path, 'static', 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    # Save template to file
    template_path = os.path.join(templates_dir, f"{template_id}.json")
    
    try:
        with open(template_path, 'w', encoding='utf-8') as f:
            import json
            json.dump({
                'id': template_id,
                'subject': subject,
                'content': template_content,
                'created_at': str(os.path.getmtime(template_path)) if os.path.exists(template_path) else None
            }, f, ensure_ascii=False)
        
        # Extract variables from template
        variables = extract_variables(template_content)
        
        return jsonify({
            'success': True,
            'template_id': template_id,
            'variables': variables
        })
    except Exception as e:
        return jsonify({'error': f'Error saving template: {str(e)}'}), 500

@template_bp.route('/get/<template_id>', methods=['GET'])
def get_template(template_id):
    template_path = os.path.join(current_app.root_path, 'static', 'templates', f"{template_id}.json")
    
    if not os.path.exists(template_path):
        return jsonify({'error': 'Template not found'}), 404
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            import json
            template_data = json.load(f)
        
        # Extract variables from template
        variables = extract_variables(template_data['content'])
        template_data['variables'] = variables
        
        return jsonify({
            'success': True,
            'template': template_data
        })
    except Exception as e:
        return jsonify({'error': f'Error retrieving template: {str(e)}'}), 500

@template_bp.route('/preview', methods=['POST'])
def preview_template():
    data = request.json
    if not data or 'template' not in data or 'data' not in data:
        return jsonify({'error': 'Missing template or data'}), 400
    
    template_content = data['template']
    replacement_data = data['data']
    subject = data.get('subject', '')
    
    try:
        # Replace variables in template
        rendered_content = replace_variables(template_content, replacement_data)
        rendered_subject = replace_variables(subject, replacement_data)
        
        return jsonify({
            'success': True,
            'rendered_content': rendered_content,
            'rendered_subject': rendered_subject
        })
    except Exception as e:
        return jsonify({'error': f'Error rendering template: {str(e)}'}), 500

def extract_variables(text):
    """Extract variables in the format [variable_name] from text"""
    pattern = r'\[([^\]]+)\]'
    matches = re.findall(pattern, text)
    return list(set(matches))  # Return unique variables

def replace_variables(text, data):
    """Replace variables in the format [variable_name] with corresponding values from data"""
    if not text:
        return text
        
    for key, value in data.items():
        placeholder = f'[{key}]'
        text = text.replace(placeholder, str(value))
    
    return text
