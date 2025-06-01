import os
import csv
import json
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

csv_bp = Blueprint('csv', __name__)

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@csv_bp.route('/upload', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        # Parse CSV headers and first few rows for preview
        preview_data = []
        headers = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as csvfile:
                csv_reader = csv.reader(csvfile)
                headers = next(csv_reader)  # Get headers
                
                # Get first 5 rows for preview
                for i, row in enumerate(csv_reader):
                    if i >= 5:  # Limit to 5 rows for preview
                        break
                    
                    row_data = {}
                    for j, value in enumerate(row):
                        if j < len(headers):
                            row_data[headers[j]] = value
                    
                    preview_data.append(row_data)
                
            return jsonify({
                'success': True,
                'filename': filename,
                'headers': headers,
                'preview': preview_data
            })
            
        except Exception as e:
            return jsonify({'error': f'Error parsing CSV: {str(e)}'}), 500
    
    return jsonify({'error': 'Invalid file format. Please upload a CSV file.'}), 400

@csv_bp.route('/parse/<filename>', methods=['GET'])
def parse_csv(filename):
    filepath = os.path.join(current_app.root_path, 'static', 'uploads', secure_filename(filename))
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    try:
        data = []
        headers = []
        
        with open(filepath, 'r', encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile)
            headers = next(csv_reader)  # Get headers
            
            for row in csv_reader:
                row_data = {}
                for j, value in enumerate(row):
                    if j < len(headers):
                        row_data[headers[j]] = value
                
                data.append(row_data)
        
        return jsonify({
            'success': True,
            'headers': headers,
            'data': data
        })
        
    except Exception as e:
        return jsonify({'error': f'Error parsing CSV: {str(e)}'}), 500
