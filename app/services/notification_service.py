"""
Notification Service for IT ServiceDesk
Handles alert creation, management, and delivery
"""

from datetime import datetime
from app import db
from app.models import Alert, User, Ticket

class NotificationService:
    """Enhanced notification service for comprehensive alert management"""
    
    @staticmethod
    def create_alert(user_id, ticket_id, alert_type, title, message):
        """Create a new alert with validation"""
        try:
            # Validate user exists
            user = User.query.get(user_id)
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            # Validate ticket exists if provided
            if ticket_id:
                ticket = Ticket.query.get(ticket_id)
                if not ticket:
                    raise ValueError(f"Ticket {ticket_id} not found")
            
            alert = Alert(
                user_id=user_id,
                ticket_id=ticket_id,
                alert_type=alert_type,
                title=title,
                message=message
            )
            
            db.session.add(alert)
            db.session.commit()
            
            print(f"[SUCCESS] Alert created: {title} for user {user.name}")
            return alert
            
        except Exception as e:
            db.session.rollback()
            print(f"[ERROR] Alert creation failed: {e}")
            raise
    
    @staticmethod
    def create_assignment_alert(user_id, ticket_id, ticket_title, priority):
        """Create assignment alert with enhanced details"""
        title = f"New Ticket Assigned"
        message = f"You have been assigned ticket {ticket_id}: {ticket_title} (Priority: {priority})"
        
        return NotificationService.create_alert(
            user_id=user_id,
            ticket_id=ticket_id,
            alert_type='assignment',
            title=title,
            message=message
        )
    
    @staticmethod
    def create_sla_alert(user_id, ticket_id, ticket_title, hours_remaining):
        """Create SLA violation warning alert"""
        title = f"SLA Warning: {ticket_id}"
        message = f"Ticket {ticket_id}: {ticket_title} has {hours_remaining} hours remaining before SLA violation"
        
        return NotificationService.create_alert(
            user_id=user_id,
            ticket_id=ticket_id,
            alert_type='sla_warning',
            title=title,
            message=message
        )
    
    @staticmethod
    def create_escalation_alert(supervisor_ids, ticket_id, ticket_title, reason):
        """Create escalation alerts for supervisors"""
        alerts = []
        title = f"Ticket Escalated: {ticket_id}"
        message = f"Ticket {ticket_id}: {ticket_title} has been escalated. Reason: {reason}"
        
        for supervisor_id in supervisor_ids:
            alert = NotificationService.create_alert(
                user_id=supervisor_id,
                ticket_id=ticket_id,
                alert_type='escalation',
                title=title,
                message=message
            )
            alerts.append(alert)
        
        return alerts
    
    @staticmethod
    def get_user_alerts(user_id, limit=20, unread_only=False):
        """Get alerts for a specific user with enhanced filtering"""
        try:
            # Use ORM query with joins
            query = db.session.query(
                Alert.id,
                Alert.title,
                Alert.message,
                Alert.alert_type,
                Alert.is_read,
                Alert.created_at,
                Ticket.ticket_id,
                Ticket.status,
                Ticket.priority
            ).outerjoin(
                Ticket, Alert.ticket_id == Ticket.id
            ).filter(
                Alert.user_id == user_id
            )
            
            if unread_only:
                query = query.filter(Alert.is_read == False)
            
            query = query.order_by(Alert.created_at.desc()).limit(limit)
            
            alerts = []
            for row in query:
                alerts.append({
                    'id': row.id,
                    'title': row.title,
                    'message': row.message,
                    'alert_type': row.alert_type,
                    'is_read': row.is_read,
                    'created_at': row.created_at.isoformat() + 'Z' if row.created_at else None,
                    'ticket_id': row.ticket_id,
                    'ticket_status': row.status,
                    'ticket_priority': row.priority,
                    'clickable': bool(row.ticket_id)  # Can click if has ticket_id
                })
            
            return alerts
            
        except Exception as e:
            print(f"[ERROR] Error fetching alerts for user {user_id}: {e}")
            return []
    
    @staticmethod
    def mark_alert_read(alert_id, user_id=None):
        """Mark specific alert as read with user validation"""
        try:
            query = Alert.query.filter_by(id=alert_id)
            if user_id:
                query = query.filter_by(user_id=user_id)
            
            alert = query.first()
            if not alert:
                return False
            
            alert.is_read = True
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"[ERROR] Error marking alert {alert_id} as read: {e}")
            return False
    
    @staticmethod
    def mark_all_alerts_read(user_id):
        """Mark all alerts as read for a user"""
        try:
            # Use ORM update
            Alert.query.filter_by(
                user_id=user_id, 
                is_read=False
            ).update({'is_read': True})
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"[ERROR] Error marking all alerts as read for user {user_id}: {e}")
            return False
    
    @staticmethod
    def get_alert_count(user_id, unread_only=True):
        """Get count of alerts for a user"""
        try:
            # Use ORM count
            query = Alert.query.filter_by(user_id=user_id)
            if unread_only:
                query = query.filter_by(is_read=False)
            
            return query.count()
            
        except Exception as e:
            print(f"[ERROR] Error getting alert count for user {user_id}: {e}")
            return 0
    
    @staticmethod
    def cleanup_old_alerts(days_old=30):
        """Clean up old read alerts to maintain performance"""
        try:
            from datetime import timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            # Use ORM delete
            old_alerts = Alert.query.filter(
                Alert.is_read == True,
                Alert.created_at < cutoff_date
            ).all()
            
            deleted_count = len(old_alerts)
            for alert in old_alerts:
                db.session.delete(alert)
            
            db.session.commit()
            print(f"🧹 Cleaned up {deleted_count} old alerts")
            return deleted_count
            
        except Exception as e:
            db.session.rollback()
            print(f"[ERROR] Error cleaning up old alerts: {e}")
            return 0