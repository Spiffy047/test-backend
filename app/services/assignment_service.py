from typing import Optional
from app import db
from app.models import User, Ticket

class AssignmentService:
    """Service for automatic ticket assignment"""
    
    @staticmethod
    def get_agent_with_least_tickets() -> Optional[User]:
        """Get agent with the least number of active tickets"""
        agents = User.query.filter(User.role.in_(['Technical User', 'Technical Supervisor'])).all()
        
        if not agents:
            return None
        
        # Calculate active ticket count for each agent
        agent_workloads = []
        for agent in agents:
            active_count = Ticket.query.filter(
                Ticket.assigned_to == agent.id,
                Ticket.status != 'Closed'
            ).count()
            agent_workloads.append((agent, active_count))
        
        # Sort by workload and return agent with least tickets
        agent_workloads.sort(key=lambda x: x[1])
        return agent_workloads[0][0]
    
    @staticmethod
    def auto_assign_ticket(ticket: Ticket) -> bool:
        """Automatically assign ticket to agent with least workload"""
        if ticket.assigned_to:
            return False  # Already assigned
        
        agent = AssignmentService.get_agent_with_least_tickets()
        if agent:
            ticket.assigned_to = agent.id
            return True
        
        return False