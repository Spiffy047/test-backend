from flask import Blueprint, jsonify
from app import db
from app.models.ticket import Ticket
from datetime import datetime, timedelta
from sqlalchemy import func

sla_bp = Blueprint('sla', __name__)

@sla_bp.route('/realtime-adherence', methods=['GET'])
def get_realtime_sla_adherence():
    """Get real-time SLA adherence metrics with detailed breakdown"""
    
    # SLA targets in hours
    sla_targets = {
        'Critical': 4,
        'High': 8,
        'Medium': 24,
        'Low': 72
    }
    
    # Get all tickets
    all_tickets = Ticket.query.all()
    
    # Update SLA status for open tickets in real-time
    for ticket in all_tickets:
        if ticket.status != 'Closed':
            ticket.sla_violated = ticket.check_sla_violation()
    db.session.commit()
    
    # Calculate overall metrics
    total_tickets = len(all_tickets)
    closed_tickets = [t for t in all_tickets if t.status == 'Closed']
    open_tickets = [t for t in all_tickets if t.status != 'Closed']
    
    # Closed tickets SLA adherence
    closed_met_sla = len([t for t in closed_tickets if not t.sla_violated])
    closed_violated_sla = len([t for t in closed_tickets if t.sla_violated])
    closed_adherence = (closed_met_sla / len(closed_tickets) * 100) if closed_tickets else 0
    
    # Open tickets at risk
    open_violated = len([t for t in open_tickets if t.sla_violated])
    open_at_risk = len([t for t in open_tickets if not t.sla_violated and t.hours_open > sla_targets.get(t.priority, 24) * 0.8])
    
    # Priority breakdown
    priority_breakdown = {}
    for priority in ['Critical', 'High', 'Medium', 'Low']:
        priority_tickets = [t for t in all_tickets if t.priority == priority]
        if priority_tickets:
            met = len([t for t in priority_tickets if not t.sla_violated])
            violated = len([t for t in priority_tickets if t.sla_violated])
            priority_breakdown[priority] = {
                'total': len(priority_tickets),
                'met_sla': met,
                'violated_sla': violated,
                'adherence_percentage': round((met / len(priority_tickets)) * 100, 2),
                'target_hours': sla_targets[priority]
            }
    
    # Time-based analysis (last 24 hours, 7 days, 30 days)
    now = datetime.utcnow()
    time_periods = {
        'last_24h': now - timedelta(hours=24),
        'last_7d': now - timedelta(days=7),
        'last_30d': now - timedelta(days=30)
    }
    
    time_analysis = {}
    for period_name, start_time in time_periods.items():
        period_tickets = [t for t in all_tickets if t.created_at >= start_time]
        if period_tickets:
            met = len([t for t in period_tickets if not t.sla_violated])
            time_analysis[period_name] = {
                'total': len(period_tickets),
                'met_sla': met,
                'violated_sla': len(period_tickets) - met,
                'adherence_percentage': round((met / len(period_tickets)) * 100, 2)
            }
    
    # Average resolution time by priority
    avg_resolution_times = {}
    for priority in ['Critical', 'High', 'Medium', 'Low']:
        priority_closed = [t for t in closed_tickets if t.priority == priority and t.resolution_time_hours]
        if priority_closed:
            avg_time = sum(t.resolution_time_hours for t in priority_closed) / len(priority_closed)
            avg_resolution_times[priority] = {
                'average_hours': round(avg_time, 2),
                'target_hours': sla_targets[priority],
                'within_target': avg_time <= sla_targets[priority]
            }
    
    return jsonify({
        'timestamp': now.isoformat(),
        'overall': {
            'total_tickets': total_tickets,
            'closed_tickets': len(closed_tickets),
            'open_tickets': len(open_tickets),
            'closed_met_sla': closed_met_sla,
            'closed_violated_sla': closed_violated_sla,
            'closed_adherence_percentage': round(closed_adherence, 2),
            'open_violated': open_violated,
            'open_at_risk': open_at_risk
        },
        'priority_breakdown': priority_breakdown,
        'time_analysis': time_analysis,
        'average_resolution_times': avg_resolution_times,
        'sla_targets': sla_targets
    })

@sla_bp.route('/ticket-timeline/<ticket_id>', methods=['GET'])
def get_ticket_sla_timeline(ticket_id):
    """Get detailed SLA timeline for a specific ticket"""
    ticket = Ticket.query.get_or_404(ticket_id)
    
    sla_targets = {
        'Critical': 4,
        'High': 8,
        'Medium': 24,
        'Low': 72
    }
    
    target_hours = sla_targets.get(ticket.priority, 24)
    hours_open = ticket.hours_open
    
    # Calculate SLA deadline
    from datetime import timedelta
    sla_deadline = ticket.created_at + timedelta(hours=target_hours)
    
    # Calculate time remaining or overdue
    if ticket.status == 'Closed':
        time_to_resolution = ticket.resolution_time_hours
        time_remaining = target_hours - time_to_resolution
    else:
        now = datetime.utcnow()
        time_remaining = (sla_deadline - now).total_seconds() / 3600
    
    # Calculate percentage of SLA time used
    sla_percentage_used = (hours_open / target_hours) * 100
    
    return jsonify({
        'ticket_id': ticket.id,
        'priority': ticket.priority,
        'status': ticket.status,
        'created_at': ticket.created_at.isoformat(),
        'resolved_at': ticket.resolved_at.isoformat() if ticket.resolved_at else None,
        'sla_target_hours': target_hours,
        'sla_deadline': sla_deadline.isoformat(),
        'hours_open': round(hours_open, 2),
        'time_remaining_hours': round(time_remaining, 2),
        'sla_percentage_used': round(sla_percentage_used, 2),
        'sla_violated': ticket.sla_violated,
        'resolution_time_hours': ticket.resolution_time_hours
    })
