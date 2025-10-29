# Core database models for IT ServiceDesk application
# This module defines the main database schema using SQLAlchemy ORM

# Database and utilities
from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func

class User(db.Model):
    """User model for authentication and role management
    
    Handles user accounts with different roles:
    - Normal User: Can create and view their own tickets
    - Technical User: Can be assigned tickets and respond
    - Technical Supervisor: Can manage assignments and view analytics
    - System Admin: Full system access
    """
    __tablename__ = 'users'
    
    # Primary key and basic info
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Full display name
    email = db.Column(db.String(120), unique=True, nullable=False)  # Login email (unique)
    password_hash = db.Column(db.String(255), nullable=False)  # Hashed password for security
    
    # Role-based access control
    role = db.Column(db.String(50), nullable=False, default='Normal User')
    
    # Email verification system
    is_verified = db.Column(db.Boolean, default=True, nullable=True)  # Email verification status
    verification_token = db.Column(db.String(100), nullable=True)  # Token for email verification
    token_expires_at = db.Column(db.DateTime, nullable=True)  # Token expiration time
    
    # Audit timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Account creation time
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Last update
    
    # Database relationships - define how users relate to other entities
    created_tickets = db.relationship('Ticket', foreign_keys='Ticket.created_by', backref='creator', lazy='dynamic')
    assigned_tickets = db.relationship('Ticket', foreign_keys='Ticket.assigned_to', backref='assignee', lazy='dynamic')
    sent_messages = db.relationship('Message', backref='sender', lazy='dynamic')
    alerts = db.relationship('Alert', backref='user', lazy='dynamic')
    
    # Password management methods
    def set_password(self, password):
        """Hash and store password securely using Werkzeug"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against stored hash"""
        return check_password_hash(self.password_hash, password)
    
    # Email verification methods
    def generate_verification_token(self):
        """Generate secure token for email verification (24-hour expiry)"""
        import secrets
        from datetime import timedelta
        self.verification_token = secrets.token_urlsafe(32)  # Cryptographically secure token
        self.token_expires_at = datetime.utcnow() + timedelta(hours=24)  # 24-hour expiry
        return self.verification_token
    
    def verify_email(self, token):
        """Verify email using provided token"""
        # Check if token matches and hasn't expired
        if (self.verification_token == token and 
            self.token_expires_at and 
            datetime.utcnow() < self.token_expires_at):
            # Mark as verified and clear token
            self.is_verified = True
            self.verification_token = None
            self.token_expires_at = None
            return True
        return False
    
    def __repr__(self):
        return f'<User {self.email}>'

class Ticket(db.Model):
    """Ticket model with SLA tracking and proper relationships
    
    Represents support tickets with the following lifecycle:
    New -> Open -> In Progress -> Pending -> Resolved/Closed
    
    Includes SLA (Service Level Agreement) tracking based on priority:
    - Critical: 4 hours
    - High: 8 hours  
    - Medium: 24 hours
    - Low: 72 hours
    """
    __tablename__ = 'tickets'
    
    # Primary keys and identifiers
    id = db.Column(db.Integer, primary_key=True)  # Internal database ID
    ticket_id = db.Column(db.String(20), unique=True, nullable=False)  # User-facing ID (TKT-XXXX)
    
    # Ticket content
    title = db.Column(db.String(200), nullable=False)  # Brief description
    description = db.Column(db.Text, nullable=False)  # Detailed problem description
    
    # Ticket classification
    status = db.Column(db.String(20), nullable=False, default='New')  # Current status
    priority = db.Column(db.String(20), nullable=False)  # Critical/High/Medium/Low
    category = db.Column(db.String(50), nullable=False)  # Hardware/Software/Network/etc
    
    # Assignment and ownership
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Ticket creator
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Assigned agent
    
    # Timestamp tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Creation time
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Last update
    resolved_at = db.Column(db.DateTime, nullable=True)  # Resolution time
    
    # SLA tracking
    sla_violated = db.Column(db.Boolean, default=False)  # Whether SLA was breached
    
    # Database relationships - cascade delete ensures cleanup
    messages = db.relationship('Message', backref='ticket', lazy='dynamic', cascade='all, delete-orphan')
    alerts = db.relationship('Alert', backref='ticket', lazy='dynamic', cascade='all, delete-orphan')
    
    # Computed properties for SLA tracking
    @property
    def hours_open(self):
        """Calculate how long ticket has been open (in hours)
        
        For resolved tickets: time from creation to resolution
        For open tickets: time from creation to now
        """
        if self.status in ['Resolved', 'Closed'] and self.resolved_at:
            # Use actual resolution time for closed tickets
            return (self.resolved_at - self.created_at).total_seconds() / 3600
        # Use current time for open tickets
        return (datetime.utcnow() - self.created_at).total_seconds() / 3600
    
    def check_sla_violation(self):
        """Check if ticket has exceeded SLA time limits based on priority
        
        SLA targets by priority:
        - Critical: 4 hours (urgent system outages)
        - High: 8 hours (significant impact)
        - Medium: 24 hours (standard issues)
        - Low: 72 hours (minor requests)
        """
        sla_targets = {
            'Critical': 4,   # 4 hours - urgent system issues
            'High': 8,       # 8 hours - high impact problems
            'Medium': 24,    # 24 hours - standard support
            'Low': 72        # 72 hours - low priority requests
        }
        target_hours = sla_targets.get(self.priority, 24)  # Default to 24 hours
        return self.hours_open > target_hours
    
    def __repr__(self):
        return f'<Ticket {self.ticket_id}>'

class Message(db.Model):
    """Message model for ticket conversations
    
    Stores chat messages between users and support agents within tickets.
    Creates a timeline of communication for each ticket.
    """
    __tablename__ = 'messages'
    
    # Primary key and relationships
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)  # Parent ticket
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Message author
    
    # Message content and metadata
    message = db.Column(db.Text, nullable=False)  # Message text content
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # When message was sent
    
    def __repr__(self):
        return f'<Message {self.id}>'

class Alert(db.Model):
    """Alert model for notifications
    
    Manages system notifications for users including:
    - New ticket assignments
    - Status changes
    - SLA violations
    - Priority escalations
    """
    __tablename__ = 'alerts'
    
    # Primary key and relationships
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Alert recipient
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)  # Related ticket
    
    # Alert classification and content
    alert_type = db.Column(db.String(50), nullable=False)  # Type: assignment, sla_violation, etc.
    title = db.Column(db.String(200), nullable=False)  # Brief alert title
    message = db.Column(db.Text, nullable=False)  # Detailed alert message
    
    # Alert state and timing
    is_read = db.Column(db.Boolean, default=False)  # Whether user has seen the alert
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # When alert was created
    
    def __repr__(self):
        return f'<Alert {self.id}>'