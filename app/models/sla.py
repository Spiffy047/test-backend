from app import db
from datetime import datetime
from sqlalchemy import func

class SLAPolicy(db.Model):
    __tablename__ = 'sla_policies'
    
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    priority = db.Column(db.String(20), nullable=False)
    target_hours = db.Column(db.Integer, nullable=False)
    escalation_hours = db.Column(db.Integer, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SLAPolicy {self.name}>'

class SLAViolation(db.Model):
    __tablename__ = 'sla_violations'
    
    id = db.Column(db.String(50), primary_key=True)
    ticket_id = db.Column(db.String(20), db.ForeignKey('tickets.id'), nullable=False)
    policy_id = db.Column(db.String(50), db.ForeignKey('sla_policies.id'), nullable=False)
    violation_type = db.Column(db.String(50), nullable=False)  # 'breach', 'warning', 'escalation'
    violation_time = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    ticket = db.relationship('Ticket', backref='sla_violations')
    policy = db.relationship('SLAPolicy', backref='violations')
    
    def __repr__(self):
        return f'<SLAViolation {self.ticket_id}>'