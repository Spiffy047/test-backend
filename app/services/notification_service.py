"""
Notification Service for IT ServiceDesk
Handles alert creation, management, and delivery
"""

from datetime import datetime
from app import db
from app.models import Alert, User, Ticket
from sqlalchemy import text

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
            query = db.session.execute(text("""
                SELECT a.id, a.title, a.message, a.alert_type, a.is_read, a.created_at,
                       COALESCE(t.ticket_id, CAST(a.ticket_id AS VARCHAR)) as ticket_id,
                       t.status as ticket_status, t.priority as ticket_priority
                FROM alerts a
                LEFT JOIN tickets t ON a.ticket_id = t.id
                WHERE a.user_id = :user_id
                """ + (" AND a.is_read = false" if unread_only else "") + """
                ORDER BY a.created_at DESC
                LIMIT :limit
            """), {'user_id': user_id, 'limit': limit})
            
            alerts = []
            for row in query:
                alerts.append({
                    'id': row[0],
                    'title': row[1],
                    'message': row[2],
                    'alert_type': row[3],
                    'is_read': row[4],
                    'created_at': row[5].isoformat() + 'Z' if row[5] else None,
                    'ticket_id': row[6],
                    'ticket_status': row[7],
                    'ticket_priority': row[8],
                    'clickable': bool(row[6])  # Can click if has ticket_id
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
            db.session.execute(text("""
                UPDATE alerts SET is_read = true 
                WHERE user_id = :user_id AND is_read = false
            """), {'user_id': user_id})
            
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
            query = text("""
                SELECT COUNT(*) FROM alerts 
                WHERE user_id = :user_id
            """ + (" AND is_read = false" if unread_only else ""))
            
            result = db.session.execute(query, {'user_id': user_id})
            return result.scalar() or 0
            
        except Exception as e:
            print(f"[ERROR] Error getting alert count for user {user_id}: {e}")
            return 0
    
    @staticmethod
    def cleanup_old_alerts(days_old=30):
        """Clean up old read alerts to maintain performance"""
        try:
            from datetime import timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            result = db.session.execute(text("""
                DELETE FROM alerts 
                WHERE is_read = true AND created_at < :cutoff_date
            """), {'cutoff_date': cutoff_date})
            
            db.session.commit()
            deleted_count = result.rowcount
            print(f"🧹 Cleaned up {deleted_count} old alerts")
            return deleted_count
            
        except Exception as e:
            db.session.rollback()
            print(f"[ERROR] Error cleaning up old alerts: {e}")
            return 0