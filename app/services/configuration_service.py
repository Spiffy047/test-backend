"""
Configuration service for managing dynamic system settings
Provides methods to retrieve and manage configuration data
"""

from typing import Dict, List, Optional, Any
from app import db
from app.models import (
    UserRole, TicketStatus, TicketPriority, 
    TicketCategory
)

class ConfigurationService:
    """Service for managing system configuration"""
    
    @staticmethod
    def get_user_roles() -> List[UserRole]:
        """Get all active user roles"""
        return UserRole.query.filter_by(is_active=True).all()
    
    @staticmethod
    def get_role_by_name(name: str) -> Optional[UserRole]:
        """Get user role by name"""
        return UserRole.query.filter_by(name=name, is_active=True).first()
    
    @staticmethod
    def get_ticket_statuses() -> List[TicketStatus]:
        """Get all active ticket statuses"""
        return TicketStatus.query.filter_by(is_active=True).order_by(TicketStatus.sort_order).all()
    
    @staticmethod
    def get_status_by_name(name: str) -> Optional[TicketStatus]:
        """Get ticket status by name"""
        return TicketStatus.query.filter_by(name=name, is_active=True).first()
    
    @staticmethod
    def get_default_status() -> Optional[TicketStatus]:
        """Get default ticket status (first in sort order)"""
        return TicketStatus.query.filter_by(is_active=True).order_by(TicketStatus.sort_order).first()
    
    @staticmethod
    def get_ticket_priorities() -> List[TicketPriority]:
        """Get all active ticket priorities"""
        return TicketPriority.query.filter_by(is_active=True).order_by(TicketPriority.sort_order).all()
    
    @staticmethod
    def get_priority_by_name(name: str) -> Optional[TicketPriority]:
        """Get ticket priority by name"""
        return TicketPriority.query.filter_by(name=name, is_active=True).first()
    
    @staticmethod
    def get_ticket_categories() -> List[TicketCategory]:
        """Get all active ticket categories"""
        return TicketCategory.query.filter_by(is_active=True).all()
    
    @staticmethod
    def get_category_by_name(name: str) -> Optional[TicketCategory]:
        """Get ticket category by name"""
        return TicketCategory.query.filter_by(name=name, is_active=True).first()
    

    
    @staticmethod
    def initialize_default_configuration():
        """Initialize default configuration data"""
        
        # Default user roles
        default_roles = [
            {'name': 'Normal User', 'description': 'Can create and view own tickets', 'permissions': ['create_ticket', 'view_own_tickets']},
            {'name': 'Technical User', 'description': 'Can be assigned tickets and respond', 'permissions': ['view_assigned_tickets', 'update_tickets', 'create_messages']},
            {'name': 'Technical Supervisor', 'description': 'Can manage assignments and view analytics', 'permissions': ['view_all_tickets', 'assign_tickets', 'view_analytics']},
            {'name': 'System Admin', 'description': 'Full system access', 'permissions': ['*']}
        ]
        
        for role_data in default_roles:
            if not UserRole.query.filter_by(name=role_data['name']).first():
                role = UserRole(**role_data)
                db.session.add(role)
        
        # Default ticket statuses
        default_statuses = [
            {'name': 'New', 'description': 'Newly created ticket', 'sort_order': 1},
            {'name': 'Open', 'description': 'Ticket is being worked on', 'sort_order': 2},
            {'name': 'In Progress', 'description': 'Actively being resolved', 'sort_order': 3},
            {'name': 'Pending', 'description': 'Waiting for user response', 'sort_order': 4},
            {'name': 'Resolved', 'description': 'Issue has been resolved', 'is_closed_status': True, 'sort_order': 5},
            {'name': 'Closed', 'description': 'Ticket is closed', 'is_closed_status': True, 'sort_order': 6}
        ]
        
        for status_data in default_statuses:
            if not TicketStatus.query.filter_by(name=status_data['name']).first():
                status = TicketStatus(**status_data)
                db.session.add(status)
        
        # Default ticket priorities
        default_priorities = [
            {'name': 'Critical', 'description': 'Urgent system outages', 'sla_hours': 4, 'escalation_hours': 2, 'color_code': '#dc2626', 'sort_order': 1},
            {'name': 'High', 'description': 'Significant impact', 'sla_hours': 8, 'escalation_hours': 4, 'color_code': '#ea580c', 'sort_order': 2},
            {'name': 'Medium', 'description': 'Standard issues', 'sla_hours': 24, 'escalation_hours': 12, 'color_code': '#ca8a04', 'sort_order': 3},
            {'name': 'Low', 'description': 'Minor requests', 'sla_hours': 72, 'escalation_hours': 48, 'color_code': '#16a34a', 'sort_order': 4}
        ]
        
        for priority_data in default_priorities:
            if not TicketPriority.query.filter_by(name=priority_data['name']).first():
                priority = TicketPriority(**priority_data)
                db.session.add(priority)
        
        # Default ticket categories
        default_categories = [
            {'name': 'Hardware', 'description': 'Hardware-related issues'},
            {'name': 'Software', 'description': 'Software installation and issues'},
            {'name': 'Network', 'description': 'Network connectivity problems'},
            {'name': 'Access', 'description': 'Account and permission issues'},
            {'name': 'Email', 'description': 'Email system problems'},
            {'name': 'Security', 'description': 'Security-related concerns'}
        ]
        
        for category_data in default_categories:
            if not TicketCategory.query.filter_by(name=category_data['name']).first():
                category = TicketCategory(**category_data)
                db.session.add(category)
        

        
        db.session.commit()