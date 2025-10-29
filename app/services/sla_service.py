from typing import Dict, List, Optional
from datetime import datetime, timedelta
from app import db
from app.models import Ticket

class SLAService:
    """Service for SLA management and monitoring"""
    
    @staticmethod
    def get_sla_target(priority: str) -> int:
        """Get SLA target hours for priority"""
        targets = {
            'Critical': 4,
            'High': 8, 
            'Medium': 24,
            'Low': 72
        }
        return targets.get(priority, 24)
    
    @staticmethod
    def calculate_violation_risk(ticket: Ticket) -> float:
        """Calculate SLA violation risk (0.0 to 1.0)"""
        if ticket.status == 'Closed':
            return 0.0
            
        target_hours = SLAService.get_sla_target(ticket.priority)
        elapsed_hours = (datetime.utcnow() - ticket.created_at).total_seconds() / 3600
        
        risk = elapsed_hours / target_hours
        return min(risk, 1.0)
    
    @staticmethod
    def check_sla_violations() -> List[Ticket]:
        """Check for SLA violations and return violating tickets"""
        violations = []
        open_tickets = Ticket.query.filter(Ticket.status != 'Closed').all()
        
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
        closed_tickets = Ticket.query.filter(Ticket.status == 'Closed').all()
        
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
        for priority in ['Critical', 'High', 'Medium', 'Low']:
            priority_tickets = [t for t in closed_tickets if t.priority == priority]
            if priority_tickets:
                priority_violations = len([t for t in priority_tickets if t.sla_violated])
                priority_adherence = ((len(priority_tickets) - priority_violations) / len(priority_tickets)) * 100
                by_priority[priority] = {
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