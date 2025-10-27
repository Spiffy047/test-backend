# Flask-RESTful API resources for ticket management
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.ticket import Ticket
from app.schemas.ticket_schema import ticket_schema, tickets_schema
from app.services.assignment_service import AssignmentService
from app.services.notification_service import NotificationService
# from flasgger import swag_from  # Disabled for deployment
import uuid

class TicketListResource(Resource):
    """Handle ticket list operations (GET all, POST new)"""
    # @jwt_required()  # Disabled for deployment testing
    # Swagger documentation disabled for deployment
    def get(self):
        """Get list of tickets"""
        tickets = Ticket.query.all()
        return tickets_schema.dump(tickets)
    
    # @jwt_required()  # Disabled for deployment testing
    # Swagger documentation disabled for deployment
    def post(self):
        """Create new ticket with auto-assignment"""
        data = request.get_json()
        user_id = 'user1'  # Default for testing
        
        # Generate sequential ticket ID (TKT-0001, TKT-0002, etc.)
        ticket_count = Ticket.query.count() + 1
        ticket_id = f"TKT-{ticket_count:04d}"
        
        ticket = Ticket(
            id=ticket_id,
            title=data['title'],
            description=data['description'],
            priority=data.get('priority', 'Medium'),
            category=data['category'],
            created_by=user_id
        )
        
        db.session.add(ticket)
        db.session.flush()  # Get ticket ID before auto-assignment
        
        # Auto-assign to agent with least workload
        AssignmentService.auto_assign_ticket(ticket)
        # Notify technical team about new ticket
        NotificationService.notify_ticket_created(ticket)
        
        db.session.commit()
        
        return ticket_schema.dump(ticket), 201

class TicketResource(Resource):
    """Handle individual ticket operations (GET, PUT, DELETE)"""
    # @jwt_required()  # Disabled for deployment testing
    # Swagger documentation disabled for deployment
    def get(self, ticket_id):
        ticket = Ticket.query.get_or_404(ticket_id)
        return ticket_schema.dump(ticket)
    
    # @jwt_required()  # Disabled for deployment testing
    # Swagger documentation disabled for deployment
    def put(self, ticket_id):
        ticket = Ticket.query.get_or_404(ticket_id)
        data = request.get_json()
        user_id = 'user1'  # Default for testing
        
        old_status = ticket.status
        
        # Update fields
        for field in ['title', 'description', 'status', 'priority', 'assigned_to', 'category']:
            if field in data:
                setattr(ticket, field, data[field])
        
        # Send notifications for status changes
        if 'status' in data and data['status'] != old_status:
            NotificationService.notify_status_change(ticket, old_status, data['status'], user_id)
        
        db.session.commit()
        return ticket_schema.dump(ticket)
    
    # @jwt_required()  # Disabled for deployment testing
    # Swagger documentation disabled for deployment
    def delete(self, ticket_id):
        ticket = Ticket.query.get_or_404(ticket_id)
        db.session.delete(ticket)
        db.session.commit()
        return '', 204