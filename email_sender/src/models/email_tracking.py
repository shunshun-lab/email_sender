from datetime import datetime, timezone, timedelta
from .user import db

# JST（日本標準時）のタイムゾーン定義
JST = timezone(timedelta(hours=9))

def get_jst_now():
    """現在のJST時刻を返す"""
    return datetime.now(JST)

class EmailTracking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    sent_at = db.Column(db.DateTime, default=get_jst_now)
    status = db.Column(db.String(50), default='sent')  # sent, delivered, failed
    opened = db.Column(db.Boolean, default=False)
    opened_at = db.Column(db.DateTime, nullable=True)
    tracking_id = db.Column(db.String(64), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<EmailTracking {self.email}>'
