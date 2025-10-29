from flask import Blueprint, request, jsonify
from app import db
from app.models import Ticket
from app.schemas.ticket_schema import ticket_schema, tickets_schema
from app.services.assignment_service import AssignmentService
from app.services.notification_service import NotificationService
from app.services.configuration_service import ConfigurationService
from datetime import datetime
import uuid

tickets_bp = Blueprint('tickets', __name__)

@tickets_bp.route('/', methods=['GET'])
def get_tickets():
    """Get all tickets with optional filtering and real-time SLA calculation"""
    status = request.args.get('status')
    priority = request.args.get('priority')
    assigned_to = request.args.get('assigned_to')
    created_by = request.args.get('created_by')
    
    query = Ticket.query
    
    if status:
        status_obj = ConfigurationService.get_status_by_name(status)
        if status_obj:
            query = query.filter(Ticket.status_id == status_obj.id)
    if priority:
        priority_obj = ConfigurationService.get_priority_by_name(priority)
        if priority_obj:
            query = query.filter(Ticket.priority_id == priority_obj.id)
    if assigned_to:
        query = query.filter(Ticket.assigned_to == assigned_to)
    if created_by:
        query = query.filter(Ticket.created_by == created_by)
    
    tickets = query.order_by(Ticket.created_at.desc()).all()
    
    # Real-time SLA violation check for open tickets
    for ticket in tickets:
        if not (ticket.status and ticket.status.is_closed_status):
            ticket.sla_violated = ticket.check_sla_violation()
    
    db.session.commit()
    
    return jsonify(tickets_schema.dump(tickets))

@tickets_bp.route('/<ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    """Get a specific ticket"""
    ticket = Ticket.query.get_or_404(ticket_id)
    
    # Update SLA violation status
    if not (ticket.status and ticket.status.is_closed_status):
        ticket.sla_violated = ticket.check_sla_violation()
        db.session.commit()
    
    return jsonify(ticket_schema.dump(ticket))

@tickets_bp.route('/', methods=['POST'])
def create_ticket():
    """Create a new ticket"""
    data = request.get_json()
    
    # Generate ticket ID using PostgreSQL sequence
    result = db.session.execute("SELECT nextval('ticket_id_seq')")
    ticket_number = result.scalar()
    ticket_id = f"TKT-{ticket_number:04d}"
    
    # Get configuration objects
    priority = ConfigurationService.get_priority_by_name(data.get('priority', 'Medium'))
    category = ConfigurationService.get_category_by_name(data['category'])
    status = ConfigurationService.get_default_status()
    
    if not priority or not category or not status:
        return jsonify({'error': 'Invalid priority, category, or status'}), 400
    
    ticket = Ticket(
        ticket_id=ticket_id,
        title=data['title'],
        description=data['description'],
        priority_id=priority.id,
        category_id=category.id,
        status_id=status.id,
        created_by=data['created_by']
    )
    
    db.session.add(ticket)
    db.session.flush()  # Get ticket ID before auto-assignment
    
    # Auto-assign to agent with least workload
    AssignmentService.auto_assign_ticket(ticket)
    
    # Notify about new ticket creation
    NotificationService.notify_ticket_created(ticket)
    
    db.session.commit()
    
    return jsonify(ticket_schema.dump(ticket)), 201

@tickets_bp.route('/<ticket_id>', methods=['PUT'])
def update_ticket(ticket_id):
    """Update a ticket"""
    ticket = Ticket.query.get_or_404(ticket_id)
    data = request.get_json()
    
    old_status = ticket.status
    old_priority = ticket.priority
    old_assigned_to = ticket.assigned_to
    
    # Update basic fields
    for field in ['title', 'description', 'assigned_to']:
        if field in data:
            setattr(ticket, field, data[field])
    
    # Update configuration-based fields
    if 'status' in data:
        status_obj = ConfigurationService.get_status_by_name(data['status'])
        if status_obj:
            ticket.status_id = status_obj.id
    
    if 'priority' in data:
        priority_obj = ConfigurationService.get_priority_by_name(data['priority'])
        if priority_obj:
            ticket.priority_id = priority_obj.id
    
    if 'category' in data:
        category_obj = ConfigurationService.get_category_by_name(data['category'])
        if category_obj:
            ticket.category_id = category_obj.id
    
    ticket.updated_at = datetime.utcnow()
    
    # Handle status change to closed status
    new_status = ticket.status
    old_status_closed = old_status and hasattr(old_status, 'is_closed_status') and old_status.is_closed_status
    new_status_closed = new_status and new_status.is_closed_status
    
    if new_status_closed and not old_status_closed:
        ticket.resolved_at = datetime.utcnow()
    
    # Log activities for changes and send notifications
    activities = []
    performed_by = data.get('performed_by', 'system')
    
    if 'status' in data and data['status'] != old_status:
        activity = TicketActivity(
            id=str(uuid.uuid4()),
            ticket_id=ticket_id,
            activity_type='status_change',
            description=f'Status changed from {old_status} to {data["status"]}',
            performed_by=performed_by,
            performed_by_name=data.get('performed_by_name', 'System')
        )
        activities.append(activity)
        
        # Send notification
        NotificationService.notify_status_change(ticket, old_status, data['status'], performed_by)
    
    if 'priority' in data and data['priority'] != old_priority:
        activity = TicketActivity(
            id=str(uuid.uuid4()),
            ticket_id=ticket_id,
            activity_type='priority_change',
            description=f'Priority changed from {old_priority} to {data["priority"]}',
            performed_by=performed_by,
            performed_by_name=data.get('performed_by_name', 'System')
        )
        activities.append(activity)
        
        # Send notification
        NotificationService.notify_ticket_update(
            ticket, 'priority_change', 
            f'Priority changed from {old_priority} to {data["priority"]}',
            performed_by
        )
    
    if 'assigned_to' in data and data['assigned_to'] != old_assigned_to:
        if data['assigned_to']:
            description = f'Ticket assigned to agent {data["assigned_to"]}'
        else:
            description = 'Ticket unassigned'
        
        activity = TicketActivity(
            id=str(uuid.uuid4()),
            ticket_id=ticket_id,
            activity_type='assignment',
            description=description,
            performed_by=performed_by,
            performed_by_name=data.get('performed_by_name', 'System')
        )
        activities.append(activity)
        
        # Send notification
        NotificationService.notify_ticket_update(
            ticket, 'assignment', description, performed_by
        )
    
    for activity in activities:
        db.session.add(activity)
    
    db.session.commit()
    
    return jsonify(ticket_schema.dump(ticket))

@tickets_bp.route('/<ticket_id>', methods=['DELETE'])
def delete_ticket(ticket_id):
    """Delete a ticket"""
    ticket = Ticket.query.get_or_404(ticket_id)
    db.session.delete(ticket)
    db.session.commit()
    
    return '', 204

@tickets_bp.route('/analytics/sla-adherence', methods=['GET'])
def get_sla_adherence():
    """Get SLA adherence analytics - ALL tickets in system"""
    all_tickets = Ticket.query.all()
    
    if not all_tickets:
        return jsonify({
            'total_tickets': 0,
            'met_sla': 0,
            'violated_sla': 0,
            'adherence_percentage': 0
        })
    
    met_sla = len([t for t in all_tickets if not t.sla_violated])
    violated_sla = len([t for t in all_tickets if t.sla_violated])
    adherence_percentage = (met_sla / len(all_tickets)) * 100
    
    return jsonify({
        'total_tickets': len(all_tickets),
        'met_sla': met_sla,
        'violated_sla': violated_sla,
        'adherence_percentage': round(adherence_percentage, 2)
    })

@tickets_bp.route('/analytics/aging', methods=['GET'])
def get_ticket_aging():
    """Get ticket aging analysis"""
    open_tickets = Ticket.query.filter(Ticket.status != 'Closed').all()
    
    aging_buckets = {
        '0-24 hours': [],
        '24-48 hours': [],
        '48-72 hours': [],
        '72+ hours': []
    }
    
    for ticket in open_tickets:
        hours_open = ticket.hours_open
        
        if hours_open < 24:
            aging_buckets['0-24 hours'].append(ticket)
        elif hours_open < 48:
            aging_buckets['24-48 hours'].append(ticket)
        elif hours_open < 72:
            aging_buckets['48-72 hours'].append(ticket)
        else:
            aging_buckets['72+ hours'].append(ticket)
    
    result = {}
    for bucket, tickets in aging_buckets.items():
        result[bucket] = {
            'count': len(tickets),
            'tickets': tickets_schema.dump(tickets)
        }
    
    return jsonify(result)