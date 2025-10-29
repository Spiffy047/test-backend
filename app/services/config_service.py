from app import db
from app.models.config import UserRole, TicketPriority, TicketStatus, TicketCategory

class ConfigService:
    @staticmethod
    def get_sla_hours(priority_name):
        """Get SLA hours for priority, fallback to hardcoded if not in DB"""
        priority = TicketPriority.query.filter_by(name=priority_name, is_active=True).first()
        if priority:
            return priority.sla_hours
        
        # Fallback to original hardcoded values
        fallback = {'Critical': 4, 'High': 8, 'Medium': 24, 'Low': 72}
        return fallback.get(priority_name, 24)
    
    @staticmethod
    def is_closed_status(status_name):
        """Check if status is closed, fallback to hardcoded if not in DB"""
        status = TicketStatus.query.filter_by(name=status_name, is_active=True).first()
        if status:
            return status.is_closed_status
        
        # Fallback to original logic
        return status_name in ['Closed', 'Resolved']
    
    @staticmethod
    def init_config():
        """Initialize configuration tables with current system values"""
        # Add priorities
        priorities = [
            {'name': 'Critical', 'sla_hours': 4, 'color_code': '#dc2626', 'sort_order': 1},
            {'name': 'High', 'sla_hours': 8, 'color_code': '#ea580c', 'sort_order': 2},
            {'name': 'Medium', 'sla_hours': 24, 'color_code': '#ca8a04', 'sort_order': 3},
            {'name': 'Low', 'sla_hours': 72, 'color_code': '#16a34a', 'sort_order': 4}
        ]
        
        for p in priorities:
            if not TicketPriority.query.filter_by(name=p['name']).first():
                priority = TicketPriority(**p)
                db.session.add(priority)
        
        # Add statuses
        statuses = [
            {'name': 'New', 'is_closed_status': False, 'sort_order': 1},
            {'name': 'Open', 'is_closed_status': False, 'sort_order': 2},
            {'name': 'In Progress', 'is_closed_status': False, 'sort_order': 3},
            {'name': 'Pending', 'is_closed_status': False, 'sort_order': 4},
            {'name': 'Resolved', 'is_closed_status': True, 'sort_order': 5},
            {'name': 'Closed', 'is_closed_status': True, 'sort_order': 6}
        ]
        
        for s in statuses:
            if not TicketStatus.query.filter_by(name=s['name']).first():
                status = TicketStatus(**s)
                db.session.add(status)
        
        # Add categories
        categories = [
            {'name': 'Hardware'}, {'name': 'Software'}, {'name': 'Network'},
            {'name': 'Access'}, {'name': 'Email'}, {'name': 'Security'}
        ]
        
        for c in categories:
            if not TicketCategory.query.filter_by(name=c['name']).first():
                category = TicketCategory(**c)
                db.session.add(category)
        
        # Add roles
        roles = [
            {'name': 'Normal User', 'permissions': ['create_ticket', 'view_own_tickets']},
            {'name': 'Technical User', 'permissions': ['view_assigned_tickets', 'update_tickets']},
            {'name': 'Technical Supervisor', 'permissions': ['view_all_tickets', 'assign_tickets']},
            {'name': 'System Admin', 'permissions': ['*']}
        ]
        
        for r in roles:
            if not UserRole.query.filter_by(name=r['name']).first():
                role = UserRole(**r)
                db.session.add(role)
        
        db.session.commit()