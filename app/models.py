# Database models for IT ServiceDesk application

from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func

class User(db.Model):
    """User model with role-based access control"""
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='Normal User')
    is_verified = db.Column(db.Boolean, default=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    created_tickets = db.relationship('Ticket', foreign_keys='Ticket.created_by', backref='creator', lazy='dynamic')
    assigned_tickets = db.relationship('Ticket', foreign_keys='Ticket.assigned_to', backref='assignee', lazy='dynamic')
    sent_messages = db.relationship('Message', backref='sender', lazy='dynamic')
    alerts = db.relationship('Alert', backref='user', lazy='dynamic')
    
    def __init__(self, **kwargs):
        kwargs.pop('verification_token', None)
        kwargs.pop('token_expires_at', None)
        super(User, self).__init__(**kwargs)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    

    
    def __repr__(self):
        return f'<User {self.email}>'

class Ticket(db.Model):
    """Ticket model with SLA tracking"""
    __tablename__ = 'tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='New')
    priority = db.Column(db.String(20), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)
    sla_violated = db.Column(db.Boolean, default=False)
    
    messages = db.relationship('Message', backref='ticket', lazy='dynamic', cascade='all, delete-orphan')
    alerts = db.relationship('Alert', backref='ticket', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def hours_open(self):
        if self.status in ['Resolved', 'Closed'] and self.resolved_at:
            return (self.resolved_at - self.created_at).total_seconds() / 3600
        return (datetime.utcnow() - self.created_at).total_seconds() / 3600
    
    def check_sla_violation(self):
        try:
            from app.services.configuration_service import ConfigurationService
            priority = ConfigurationService.get_priority_by_name(self.priority)
            target_hours = priority.sla_hours if priority else self._get_fallback_sla_hours()
        except:
            target_hours = self._get_fallback_sla_hours()
        return self.hours_open > target_hours
    
    def _get_fallback_sla_hours(self):
        fallback = {'Critical': 4, 'High': 8, 'Medium': 24, 'Low': 72}
        return fallback.get(self.priority, 24)
    
    def __repr__(self):
        return f'<Ticket {self.ticket_id}>'

class Message(db.Model):
    """Message model for ticket timeline"""
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Message {self.id}>'

class Alert(db.Model):
    """Alert model for user notifications"""
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Alert {self.id}>'

class UserRole(db.Model):
    __tablename__ = 'user_roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    permissions = db.Column(db.JSON)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TicketPriority(db.Model):
    __tablename__ = 'ticket_priorities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    sla_hours = db.Column(db.Integer, nullable=False)
    color_code = db.Column(db.String(7))
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)

class TicketStatus(db.Model):
    __tablename__ = 'ticket_statuses'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    is_closed_status = db.Column(db.Boolean, default=False)
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)

class TicketCategory(db.Model):
    __tablename__ = 'ticket_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)