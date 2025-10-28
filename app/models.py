from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='Normal User')
    is_verified = db.Column(db.Boolean, default=True, nullable=True)
    verification_token = db.Column(db.String(100), nullable=True)
    token_expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    created_tickets = db.relationship('Ticket', foreign_keys='Ticket.created_by', backref='creator', lazy='dynamic')
    assigned_tickets = db.relationship('Ticket', foreign_keys='Ticket.assigned_to', backref='assignee', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_verification_token(self):
        import secrets
        from datetime import timedelta
        self.verification_token = secrets.token_urlsafe(32)
        self.token_expires_at = datetime.utcnow() + timedelta(hours=24)
        return self.verification_token
    
    def verify_email(self, token):
        if (self.verification_token == token and 
            self.token_expires_at and 
            datetime.utcnow() < self.token_expires_at):
            self.is_verified = True
            self.verification_token = None
            self.token_expires_at = None
            return True
        return False

class Ticket(db.Model):
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
    
    # Relationships
    messages = db.relationship('Message', backref='ticket', lazy='dynamic', cascade='all, delete-orphan')

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sender = db.relationship('User', backref='messages')