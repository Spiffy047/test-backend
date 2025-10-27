from app import db
from datetime import datetime

class Alert(db.Model):
    __tablename__ = 'alerts'
    
    id = db.Column(db.String(50), primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)
    ticket_id = db.Column(db.String(20), db.ForeignKey('tickets.id'), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)  # 'status_change', 'assignment', 'priority_change', 'new_message'
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Alert {self.id}>'