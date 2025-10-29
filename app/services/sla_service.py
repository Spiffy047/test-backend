from typing import Dict, List, Optional
from datetime import datetime, timedelta
from app import db
from app.models import Ticket
from app.services.configuration_service import ConfigurationService

class SLAService:
    """Service for SLA management and monitoring"""
    
    @staticmethod
    def get_sla_target(priority_name: str) -> int:
        """Get SLA target hours for priority from database configuration"""
        priority = ConfigurationService.get_priority_by_name(priority_name)
        return priority.sla_hours if priority else 24
    
    @staticmethod
    def calculate_violation_risk(ticket: Ticket) -> float:
        """Calculate SLA violation risk (0.0 to 1.0)"""
        if ticket.status and ticket.status.is_closed_status:
            return 0.0
            
        target_hours = ticket.priority.sla_hours if ticket.priority else 24
        elapsed_hours = (datetime.utcnow() - ticket.created_at).total_seconds() / 3600
        
        risk = elapsed_hours / target_hours
        return min(risk, 1.0)
    
    @staticmethod
    def check_sla_violations() -> List[Ticket]:
        """Check for SLA violations and return violating tickets"""
        violations = []
        # Get all tickets that are not in closed status
        closed_statuses = [s.id for s in ConfigurationService.get_ticket_statuses() if s.is_closed_status]
        open_tickets = Ticket.query.filter(~Ticket.status_id.in_(closed_statuses)).all()
        
        for ticket in open_tickets:
            risk = SLAService.calculate_violation_risk(ticket)
            if risk >= 1.0 and not ticket.sla_violated:
                ticket.sla_violated = True
                violations.append(ticket)
        
        if violations:
            db.session.commit()
        
        return violations
    
    @staticmethod
    def get_sla_dashboard() -> Dict:
        """Get SLA dashboard metrics"""
        # Get all closed tickets
        closed_statuses = [s.id for s in ConfigurationService.get_ticket_statuses() if s.is_closed_status]
        closed_tickets = Ticket.query.filter(Ticket.status_id.in_(closed_statuses)).all()
        
        if not closed_tickets:
            return {
                'adherence_rate': 0,
                'total_tickets': 0,
                'violations': 0,
                'by_priority': {}
            }
        
        violations = len([t for t in closed_tickets if t.sla_violated])
        adherence_rate = ((len(closed_tickets) - violations) / len(closed_tickets)) * 100
        
        # By priority breakdown
        by_priority = {}
        priorities = ConfigurationService.get_ticket_priorities()
        for priority in priorities:
            priority_tickets = [t for t in closed_tickets if t.priority_id == priority.id]
            if priority_tickets:
                priority_violations = len([t for t in priority_tickets if t.sla_violated])
                priority_adherence = ((len(priority_tickets) - priority_violations) / len(priority_tickets)) * 100
                by_priority[priority.name] = {
                    'total': len(priority_tickets),
                    'violations': priority_violations,
                    'adherence_rate': round(priority_adherence, 2)
                }
        
        return {
            'adherence_rate': round(adherence_rate, 2),
            'total_tickets': len(closed_tickets),
            'violations': violations,
            'by_priority': by_priority
        }