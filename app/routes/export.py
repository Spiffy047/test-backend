from flask import Blueprint, request, jsonify, make_response
from app.models.ticket import Ticket
from app.schemas.ticket_schema import tickets_schema
import csv
from io import StringIO
from datetime import datetime

export_bp = Blueprint('export', __name__)

@export_bp.route('/tickets/excel', methods=['GET'])
def export_tickets_excel():
    """Export tickets to CSV format"""
    status = request.args.get('status')
    priority = request.args.get('priority')
    
    query = Ticket.query
    if status:
        query = query.filter(Ticket.status == status)
    if priority:
        query = query.filter(Ticket.priority == priority)
    
    tickets = query.order_by(Ticket.created_at.desc()).all()
    
    output = StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['ID', 'Title', 'Status', 'Priority', 'Category', 'Assigned To', 'Created By', 'Created At', 'SLA Violated'])
    
    for ticket in tickets:
        writer.writerow([
            ticket.id,
            ticket.title,
            ticket.status,
            ticket.priority,
            ticket.category,
            ticket.assigned_to or 'Unassigned',
            ticket.created_by,
            ticket.created_at.strftime('%Y-%m-%d %H:%M'),
            'Yes' if ticket.sla_violated else 'No'
        ])
    
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename=tickets_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    response.headers['Content-Type'] = 'text/csv'
    
    return response
