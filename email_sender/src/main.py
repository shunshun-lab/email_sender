import os
import sys

# Add the src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, current_dir)

# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(parent_dir, '.env'))

from flask import Flask, send_from_directory, render_template, request, jsonify
from models.user import db
from models.email_tracking import EmailTracking
from routes.user import user_bp
from routes.csv.routes import csv_bp
from routes.template.routes import template_bp
from routes.email.routes import email_bp
from routes.ui.routes import ui_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'),
           template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(csv_bp, url_prefix='/api/csv')
app.register_blueprint(template_bp, url_prefix='/api/template')
app.register_blueprint(email_bp, url_prefix='/api/email')
app.register_blueprint(ui_bp, url_prefix='')

# Enable database for email tracking
# app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USERNAME', 'root')}:{os.getenv('DB_PASSWORD', 'password')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'mydb')}"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///email_sender.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/templates')
def templates():
    return render_template('templates.html')

@app.route('/send')
def send():
    return render_template('send.html')

@app.route('/tracking')
def tracking():
    return render_template('tracking.html')

if __name__ == '__main__':
    # 本番環境とローカル環境の自動判定
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
