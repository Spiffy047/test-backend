# Database models for ticket management system
from app import db
from datetime import datetime
from sqlalchemy import func

class Ticket(db.Model):
    """Main ticket model with SLA tracking"""
    __tablename__ = 'tickets'
    
    # Core ticket fields
    id = db.Column(db.String(20), primary_key=True)  # TKT-0001 format
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='New')  # New, Open, Pending, Closed
    priority = db.Column(db.String(20), nullable=False, default='Medium')  # Critical, High, Medium, Low
    category = db.Column(db.String(100), nullable=False)  # Hardware, Software, etc.
    
    # Assignment and ownership
    assigned_to = db.Column(db.String(50), db.ForeignKey('agents.id'), nullable=True)
    created_by = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)
    
    # SLA tracking
    resolution_time_hours = db.Column(db.Float, nullable=True)
    sla_violated = db.Column(db.Boolean, default=False)
    
    # Relationships
    messages = db.relationship('TicketMessage', backref='ticket', lazy=True, cascade='all, delete-orphan')
    activities = db.relationship('TicketActivity', backref='ticket', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Ticket {self.id}>'
    
    @property
    def hours_open(self):
        """Calculate how long ticket has been open (in hours)"""
        if self.status == 'Closed' and self.resolved_at:
            return (self.resolved_at - self.created_at).total_seconds() / 3600
        return (datetime.utcnow() - self.created_at).total_seconds() / 3600
    
    def check_sla_violation(self):
        """Check if ticket has exceeded SLA time limits"""
        sla_targets = {
            'Critical': 4,   # 4 hours
            'High': 8,       # 8 hours
            'Medium': 24,    # 24 hours
            'Low': 72        # 72 hours
        }
        target_hours = sla_targets.get(self.priority, 24)
        return self.hours_open > target_hours

class TicketMessage(db.Model):
    """Chat messages within tickets"""
    __tablename__ = 'ticket_messages'
    
    id = db.Column(db.String(50), primary_key=True)
    ticket_id = db.Column(db.String(20), db.ForeignKey('tickets.id'), nullable=False)
    sender_id = db.Column(db.String(50), nullable=False)
    sender_name = db.Column(db.String(100), nullable=False)
    sender_role = db.Column(db.String(50), nullable=False)  # User role for display
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    attachments = db.Column(db.JSON, default=list)  # File attachments
    
    def __repr__(self):
        return f'<TicketMessage {self.id}>'

class TicketActivity(db.Model):
    """Activity log for ticket changes (status, priority, assignment)"""
    __tablename__ = 'ticket_activities'
    
    id = db.Column(db.String(50), primary_key=True)
    ticket_id = db.Column(db.String(20), db.ForeignKey('tickets.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)  # status_change, assignment, etc.
    description = db.Column(db.Text, nullable=False)  # Human-readable description
    performed_by = db.Column(db.String(50), nullable=False)  # User ID
    performed_by_name = db.Column(db.String(100), nullable=False)  # User name
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<TicketActivity {self.id}>'