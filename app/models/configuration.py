"""
Configuration models for dynamic system settings
Removes hardcoded values and makes the system configurable via database
"""

from app import db
from datetime import datetime
from sqlalchemy import func

class UserRole(db.Model):
    """User roles configuration"""
    __tablename__ = 'user_roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    permissions = db.Column(db.JSON)  # Store permissions as JSON
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserRole {self.name}>'

class TicketStatus(db.Model):
    """Ticket status configuration"""
    __tablename__ = 'ticket_statuses'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    is_closed_status = db.Column(db.Boolean, default=False)
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<TicketStatus {self.name}>'

class TicketPriority(db.Model):
    """Ticket priority configuration with SLA targets"""
    __tablename__ = 'ticket_priorities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    sla_hours = db.Column(db.Integer, nullable=False)
    escalation_hours = db.Column(db.Integer)
    sort_order = db.Column(db.Integer, default=0)
    color_code = db.Column(db.String(7))  # Hex color for UI
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<TicketPriority {self.name}>'

class TicketCategory(db.Model):
    """Ticket category configuration"""
    __tablename__ = 'ticket_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    default_priority_id = db.Column(db.Integer, db.ForeignKey('ticket_priorities.id'))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    default_priority = db.relationship('TicketPriority', backref='categories')
    
    def __repr__(self):
        return f'<TicketCategory {self.name}>'

class AlertType(db.Model):
    """Alert type configuration"""
    __tablename__ = 'alert_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    template = db.Column(db.Text)  # Message template with placeholders
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AlertType {self.name}>'

class SystemSetting(db.Model):
    """System-wide configuration settings"""
    __tablename__ = 'system_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    data_type = db.Column(db.String(20), default='string')  # string, integer, boolean, json
    description = db.Column(db.String(200))
    is_editable = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_typed_value(self):
        """Return value with proper type conversion"""
        if self.data_type == 'integer':
            return int(self.value)
        elif self.data_type == 'boolean':
            return self.value.lower() in ('true', '1', 'yes')
        elif self.data_type == 'json':
            import json
            return json.loads(self.value)
        return self.value
    
    def __repr__(self):
        return f'<SystemSetting {self.key}>'