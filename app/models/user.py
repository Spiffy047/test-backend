from app import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    created_tickets = db.relationship('Ticket', backref='creator', lazy=True, foreign_keys='Ticket.created_by')
    
    def __repr__(self):
        return f'<User {self.email}>'

class Agent(db.Model):
    __tablename__ = 'agents'
    
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    assigned_tickets = db.relationship('Ticket', backref='assigned_agent', lazy=True, foreign_keys='Ticket.assigned_to')
    
    def __repr__(self):
        return f'<Agent {self.email}>'
    
    @property
    def ticket_count(self):
        return len([t for t in self.assigned_tickets if t.status != 'Closed'])
    
    @property
    def closed_tickets(self):
        return len([t for t in self.assigned_tickets if t.status == 'Closed'])
    
    @property
    def average_handle_time(self):
        closed = [t for t in self.assigned_tickets if t.status == 'Closed' and t.resolution_time_hours]
        if not closed:
            return 0
        return sum(t.resolution_time_hours for t in closed) / len(closed)
    
    @property
    def sla_violations(self):
        return len([t for t in self.assigned_tickets if t.sla_violated])