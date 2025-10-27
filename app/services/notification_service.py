# Notification service for real-time alerts and email notifications
from typing import Dict, List, Optional
from datetime import datetime
from app.models.ticket import Ticket
from app.models.user import User, Agent
from app.models.alert import Alert
from app import db
# socketio disabled for deployment
import uuid

class NotificationService:
    """Handles all notification types: SLA, tickets, messages"""
    
    @staticmethod
    def notify_sla_violation(ticket: Ticket) -> bool:
        """Send SLA breach alerts to agents and supervisors"""
        print(f"SLA VIOLATION ALERT: Ticket {ticket.id} has violated SLA")
        
        # Alert assigned agent
        if ticket.assigned_to:
            NotificationService._create_sla_alert(ticket, ticket.assigned_to)
        
        # Alert all supervisors
        supervisors = User.query.filter_by(role='Technical Supervisor').all()
        for supervisor in supervisors:
            NotificationService._create_sla_alert(ticket, supervisor.id)
        
        # WebSocket notifications disabled for deployment
        # NotificationService._emit_sla_breach(ticket)
        
        return True
    
    @staticmethod
    def _create_sla_alert(ticket: Ticket, user_id: str):
        """Create SLA violation alert for user"""
        alert = Alert(
            id=str(uuid.uuid4()),
            user_id=user_id,
            ticket_id=ticket.id,
            alert_type='sla_violation',
            title=f'SLA BREACH: {ticket.id}',
            message=f'Ticket {ticket.id} ({ticket.title}) has breached SLA. Priority: {ticket.priority}'
        )
        db.session.add(alert)
    
    # WebSocket methods disabled for deployment
    
    @staticmethod
    def notify_ticket_assignment(ticket: Ticket, agent: Agent, performed_by: str = None) -> bool:
        """Notify agent about ticket assignment with real-time updates"""
        print(f"ASSIGNMENT: Ticket {ticket.id} assigned to {agent.name}")
        
        # Create alert for assigned agent
        NotificationService._create_ticket_alert(
            ticket=ticket,
            alert_type='assignment',
            title=f'New Ticket Assigned: {ticket.id}',
            message=f'You have been assigned ticket {ticket.id}: {ticket.title}',
            performed_by=performed_by
        )
        
        # Real-time notifications disabled for deployment
        
        return True
    
    @staticmethod
    def notify_status_change(ticket: Ticket, old_status: str, new_status: str, performed_by: str = None) -> bool:
        """Notify stakeholders about status change with real-time updates"""
        print(f"STATUS CHANGE: Ticket {ticket.id} changed from {old_status} to {new_status}")
        
        # Create alerts for ticket creator and assigned agent
        NotificationService._create_ticket_alert(
            ticket=ticket,
            alert_type='status_change',
            title=f'Ticket {ticket.id} Status Updated',
            message=f'Status changed from {old_status} to {new_status}',
            performed_by=performed_by
        )
        
        # Real-time notifications disabled for deployment
        
        return True
    
    @staticmethod
    def get_notification_preferences(user_id: str) -> Dict:
        """Get user notification preferences (placeholder)"""
        # Future: Return user's notification settings
        return {
            'email_enabled': True,
            'sms_enabled': False,
            'push_enabled': True,
            'frequency': 'immediate'  # 'immediate', 'daily', 'weekly'
        }
    
    @staticmethod
    def send_daily_digest(user_id: str) -> bool:
        """Send daily digest of tickets (placeholder)"""
        # Future: Generate and send daily summary
        return True
    
    @staticmethod
    def notify_ticket_update(ticket: Ticket, update_type: str, message: str, performed_by: str = None) -> bool:
        """Generic method to notify about ticket updates with real-time alerts"""
        NotificationService._create_ticket_alert(
            ticket=ticket,
            alert_type=update_type,
            title=f'Ticket {ticket.id} Updated',
            message=message,
            performed_by=performed_by
        )
        
        # Real-time notifications disabled for deployment
        
        return True
    
    @staticmethod
    def notify_new_message(ticket: Ticket, message: str, sender_name: str, sender_role: str) -> bool:
        """Notify about new chat messages"""
        # Create alerts for relevant users
        users_to_notify = []
        
        # Notify ticket creator
        if ticket.created_by:
            users_to_notify.append(ticket.created_by)
        
        # Notify assigned agent
        if ticket.assigned_to and ticket.assigned_to != ticket.created_by:
            users_to_notify.append(ticket.assigned_to)
        
        for user_id in users_to_notify:
            alert = Alert(
                id=str(uuid.uuid4()),
                user_id=user_id,
                ticket_id=ticket.id,
                alert_type='new_message',
                title=f'New message in {ticket.id}',
                message=f'{sender_name} ({sender_role}): {message[:100]}...'
            )
            db.session.add(alert)
        
        # Real-time notifications disabled for deployment
        
        return True
    
    @staticmethod
    def notify_ticket_created(ticket: Ticket) -> bool:
        """Notify about new ticket creation"""
        # Notify technical users about new tickets
        technical_users = User.query.filter(
            User.role.in_(['Technical User', 'Technical Supervisor'])
        ).all()
        
        for user in technical_users:
            alert = Alert(
                id=str(uuid.uuid4()),
                user_id=user.id,
                ticket_id=ticket.id,
                alert_type='ticket_created',
                title=f'New Ticket Created: {ticket.id}',
                message=f'New {ticket.priority} priority ticket: {ticket.title}'
            )
            db.session.add(alert)
        
        # Real-time notifications disabled for deployment
        
        return True
    
    @staticmethod
    def _create_ticket_alert(ticket: Ticket, alert_type: str, title: str, message: str, performed_by: str = None):
        """Create alerts for relevant users"""
        users_to_notify = []
        
        # Always notify ticket creator
        if ticket.created_by:
            users_to_notify.append(ticket.created_by)
        
        # Notify assigned agent if different from creator
        if ticket.assigned_to and ticket.assigned_to != ticket.created_by:
            users_to_notify.append(ticket.assigned_to)
        
        # Don't notify the person who made the change
        if performed_by and performed_by in users_to_notify:
            users_to_notify.remove(performed_by)
        
        for user_id in users_to_notify:
            alert = Alert(
                id=str(uuid.uuid4()),
                user_id=user_id,
                ticket_id=ticket.id,
                alert_type=alert_type,
                title=title,
                message=message
            )
            db.session.add(alert)
    
    @staticmethod
    def get_user_alerts(user_id: str, unread_only: bool = False) -> List[Alert]:
        """Get alerts for a specific user"""
        query = Alert.query.filter_by(user_id=user_id)
        if unread_only:
            query = query.filter_by(is_read=False)
        return query.order_by(Alert.created_at.desc()).all()
    
    @staticmethod
    def mark_alert_read(alert_id: str) -> bool:
        """Mark an alert as read"""
        alert = Alert.query.get(alert_id)
        if alert:
            alert.is_read = True
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def mark_all_alerts_read(user_id: str) -> bool:
        """Mark all alerts as read for a user"""
        Alert.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
        db.session.commit()
        return True
    
    @staticmethod
    def get_unread_count(user_id: str) -> int:
        """Get count of unread alerts for user"""
        return Alert.query.filter_by(user_id=user_id, is_read=False).count()
    
    @staticmethod
    def check_and_notify_sla_violations():
        """Background task: Check all open tickets for SLA breaches"""
        from app.services.sla_service import SLAService
        
        # Get all open tickets
        open_tickets = Ticket.query.filter(Ticket.status != 'Closed').all()
        
        for ticket in open_tickets:
            risk = SLAService.calculate_violation_risk(ticket)
            
            # Mark and notify if newly breached
            if risk >= 1.0 and not ticket.sla_violated:
                ticket.sla_violated = True
                NotificationService.notify_sla_violation(ticket)
        
        db.session.commit()