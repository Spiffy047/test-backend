from flask import Blueprint, request, jsonify
from app import db
from app.models.ticket import Ticket
from app.models.user import Agent
from sqlalchemy import func, case
from datetime import datetime, timedelta

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/ticket-status-counts', methods=['GET'])
def get_ticket_status_counts():
    """Get count of tickets by status"""
    status_counts = db.session.query(
        Ticket.status,
        func.count(Ticket.id).label('count')
    ).group_by(Ticket.status).all()
    
    result = {status: count for status, count in status_counts}
    return jsonify(result)

@analytics_bp.route('/agent-workload', methods=['GET'])
def get_agent_workload():
    """Get current workload distribution across agents"""
    workload = db.session.query(
        Agent.id,
        Agent.name,
        Agent.email,
        func.count(case((Ticket.status != 'Closed', Ticket.id))).label('active_tickets'),
        func.count(case((Ticket.status == 'Closed', Ticket.id))).label('closed_tickets')
    ).outerjoin(Ticket, Agent.id == Ticket.assigned_to)\
     .group_by(Agent.id, Agent.name, Agent.email)\
     .all()
    
    result = []
    for agent_id, name, email, active, closed in workload:
        result.append({
            'agent_id': agent_id,
            'name': name,
            'email': email,
            'active_tickets': active or 0,
            'closed_tickets': closed or 0
        })
    
    return jsonify(result)

@analytics_bp.route('/unassigned-tickets', methods=['GET'])
def get_unassigned_tickets():
    """Get list of unassigned tickets"""
    unassigned = Ticket.query.filter(
        Ticket.assigned_to.is_(None),
        Ticket.status.in_(['New', 'Open'])
    ).order_by(Ticket.priority.desc(), Ticket.created_at.asc()).all()
    
    from app.schemas.ticket_schema import tickets_schema
    return jsonify({
        'count': len(unassigned),
        'tickets': tickets_schema.dump(unassigned)
    })

@analytics_bp.route('/resolution-time-trends', methods=['GET'])
def get_resolution_time_trends():
    """Get resolution time trends over the last 30 days"""
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    trends = db.session.query(
        func.date(Ticket.resolved_at).label('date'),
        func.avg(Ticket.resolution_time_hours).label('avg_resolution_time'),
        func.count(Ticket.id).label('tickets_resolved'),
        Ticket.priority
    ).filter(
        Ticket.status == 'Closed',
        Ticket.resolved_at >= thirty_days_ago,
        Ticket.resolution_time_hours.isnot(None)
    ).group_by(
        func.date(Ticket.resolved_at),
        Ticket.priority
    ).order_by(func.date(Ticket.resolved_at)).all()
    
    result = []
    for date, avg_time, count, priority in trends:
        result.append({
            'date': date.isoformat() if date else None,
            'avg_resolution_time': round(float(avg_time), 2) if avg_time else 0,
            'tickets_resolved': count,
            'priority': priority
        })
    
    return jsonify(result)

@analytics_bp.route('/sla-performance', methods=['GET'])
def get_sla_performance():
    """Get detailed SLA performance metrics"""
    # Overall SLA adherence - ALL tickets in system
    total_tickets = Ticket.query.count()
    sla_violations = Ticket.query.filter(Ticket.sla_violated == True).count()
    
    adherence_rate = ((total_tickets - sla_violations) / total_tickets * 100) if total_tickets > 0 else 0
    
    # SLA performance by priority
    priority_performance = db.session.query(
        Ticket.priority,
        func.count(Ticket.id).label('total'),
        func.count(case((Ticket.sla_violated == True, Ticket.id))).label('violations')
    ).filter(Ticket.status == 'Closed')\
     .group_by(Ticket.priority).all()
    
    priority_breakdown = []
    for priority, total, violations in priority_performance:
        adherence = ((total - violations) / total * 100) if total > 0 else 0
        priority_breakdown.append({
            'priority': priority,
            'total_tickets': total,
            'violations': violations,
            'adherence_percentage': round(adherence, 2)
        })
    
    return jsonify({
        'overall_adherence_percentage': round(adherence_rate, 2),
        'total_tickets': total_tickets,
        'total_violations': sla_violations,
        'priority_breakdown': priority_breakdown
    })

@analytics_bp.route('/agent-performance-detailed', methods=['GET'])
def get_agent_performance_detailed():
    """Get detailed agent performance metrics"""
    performance = db.session.query(
        Agent.id,
        Agent.name,
        Agent.email,
        func.count(case((Ticket.status != 'Closed', Ticket.id))).label('active_tickets'),
        func.count(case((Ticket.status == 'Closed', Ticket.id))).label('closed_tickets'),
        func.avg(case((Ticket.status == 'Closed', Ticket.resolution_time_hours))).label('avg_handle_time'),
        func.count(case((Ticket.sla_violated == 1, Ticket.id))).label('sla_violations')
    ).outerjoin(Ticket, Agent.id == Ticket.assigned_to)\
     .group_by(Agent.id, Agent.name, Agent.email)\
     .all()
    
    result = []
    for agent_id, name, email, active, closed, avg_time, violations in performance:
        # Calculate performance score
        score = (closed or 0) * 10 - (violations or 0) * 5
        
        # Determine rating
        if score >= 50:
            rating = 'Excellent'
        elif score >= 30:
            rating = 'Good'
        elif score >= 15:
            rating = 'Average'
        else:
            rating = 'Needs Improvement'
        
        result.append({
            'agent_id': agent_id,
            'name': name,
            'email': email,
            'active_tickets': active or 0,
            'closed_tickets': closed or 0,
            'avg_handle_time': round(float(avg_time), 2) if avg_time else 0,
            'sla_violations': violations or 0,
            'performance_score': max(0, score),
            'performance_rating': rating
        })
    
    # Sort by performance score
    result.sort(key=lambda x: x['performance_score'], reverse=True)
    
    return jsonify(result)