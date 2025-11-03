# Flask-RESTful API resources for ticket management
# This module handles all ticket-related API endpoints including CRUD operations

# Core Flask imports
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

# Database and models
from app import db
from app.models import Ticket
from app.schemas.ticket_schema import ticket_schema, tickets_schema

# Business logic services
from app.services.assignment_service import AssignmentService
from app.services.notification_service import NotificationService

# Utilities
from datetime import datetime
import uuid

# Note: JWT authentication and Swagger docs disabled for deployment testing

class TicketListResource(Resource):
    """Handle ticket list operations (GET all, POST new)"""
    
    def get(self):
        """Retrieve all tickets using ORM"""
        try:
            # Use ORM to get all tickets
            tickets_query = Ticket.query.order_by(Ticket.created_at.desc()).all()
            
            # Transform ORM objects into JSON-serializable format
            tickets = []
            for ticket in tickets_query:
                tickets.append({
                    'id': ticket.ticket_id or f'TKT-{ticket.id}',
                    'ticket_id': ticket.ticket_id or f'TKT-{ticket.id}',
                    'title': ticket.title,
                    'description': ticket.description,
                    'priority': ticket.priority,
                    'category': ticket.category,
                    'status': ticket.status,
                    'created_by': ticket.created_by,
                    'assigned_to': ticket.assigned_to,
                    'created_at': ticket.created_at.isoformat() if ticket.created_at else None,
                    'updated_at': ticket.updated_at.isoformat() if ticket.updated_at else None,
                    'sla_violated': ticket.sla_violated or False
                })
            
            return {'tickets': tickets}
        except Exception as e:
            print(f"Error fetching tickets: {e}")
            return {'tickets': []}

    
    def post(self):
        """Create new ticket with auto-generated TKT-XXXX ID"""
        # Extract JSON data from request body
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return {'error': 'No data provided'}, 400
        
        required_fields = ['title', 'description', 'category']
        for field in required_fields:
            if not data.get(field) or str(data.get(field)).strip() == '':
                return {'error': f'Missing required field: {field}'}, 400
        
        user_id = data.get('created_by')
        if not user_id:
            return {'error': 'created_by field is required'}, 400
        
        try:
            # Generate sequential ticket ID using ORM
            ticket_count = Ticket.query.count() + 1001  # Start numbering from 1001
            ticket_id = f"TKT-{ticket_count}"
            
            # Create new ticket using ORM
            ticket = Ticket(
                ticket_id=ticket_id,
                title=data['title'],
                description=data['description'],
                priority=data.get('priority', 'Medium'),
                category=data['category'],
                status='New',
                created_by=user_id
            )
            
            db.session.add(ticket)
            db.session.commit()
            
            # Return created ticket data for frontend confirmation
            return {
                'id': ticket.ticket_id,
                'ticket_id': ticket.ticket_id,
                'title': ticket.title,
                'description': ticket.description,
                'priority': ticket.priority,
                'category': ticket.category,
                'status': ticket.status,
                'created_by': ticket.created_by,
                'created_at': ticket.created_at.isoformat() + 'Z' if ticket.created_at else None
            }, 201
            
        except Exception as e:
            # Rollback transaction on error to maintain data integrity
            db.session.rollback()
            print(f"Error creating ticket: {e}")
            return {'error': 'Failed to create ticket'}, 500

class TicketResource(Resource):
    """Handle individual ticket operations (GET, PUT, DELETE)"""
    
    def get(self, ticket_id):
        """Retrieve specific ticket using ORM"""
        try:
            # Query specific ticket using ORM - handle both ticket_id and numeric id
            ticket = None
            if ticket_id.startswith('TKT-'):
                ticket = Ticket.query.filter_by(ticket_id=ticket_id).first()
            else:
                ticket = Ticket.query.get(ticket_id)
            
            if not ticket:
                return {'error': 'Ticket not found'}, 404
            
            return {
                'id': ticket.ticket_id or f'TKT-{ticket.id}',
                'ticket_id': ticket.ticket_id or f'TKT-{ticket.id}',
                'title': ticket.title,
                'description': ticket.description,
                'priority': ticket.priority,
                'category': ticket.category,
                'status': ticket.status,
                'created_by': ticket.created_by,
                'assigned_to': ticket.assigned_to,
                'created_at': ticket.created_at.isoformat() if ticket.created_at else None,
                'updated_at': ticket.updated_at.isoformat() if ticket.updated_at else None,
                'sla_violated': ticket.sla_violated or False
            }
        except Exception as e:
            print(f"Error fetching ticket {ticket_id}: {e}")
            return {'error': 'Failed to retrieve ticket'}, 500
    
    def put(self, ticket_id):
        """Update existing ticket using ORM"""
        data = request.get_json()
        
        try:
            # Find ticket using ORM
            ticket = None
            if ticket_id.startswith('TKT-'):
                ticket = Ticket.query.filter_by(ticket_id=ticket_id).first()
            else:
                ticket = Ticket.query.get(ticket_id)
            
            if not ticket:
                return {'error': 'Ticket not found'}, 404
            
            # Update fields using ORM
            updated = False
            
            if 'status' in data:
                ticket.status = data['status']
                updated = True
                
                # Set resolved_at timestamp when ticket is resolved
                if data['status'] in ['Resolved', 'Closed']:
                    ticket.resolved_at = datetime.utcnow()
            
            if 'assigned_to' in data:
                ticket.assigned_to = data['assigned_to']
                updated = True
            
            if 'priority' in data:
                ticket.priority = data['priority']
                updated = True
            
            if not updated:
                return {'error': 'No valid fields to update'}, 400
            
            # ORM automatically handles updated_at if configured
            db.session.commit()
            
            return {
                'id': ticket.ticket_id or f'TKT-{ticket.id}',
                'message': 'Ticket updated successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            print(f"Error updating ticket {ticket_id}: {e}")
            return {'error': 'Failed to update ticket'}, 500
    
    def delete(self, ticket_id):
        """Delete ticket using ORM"""
        try:
            # Find and delete ticket using ORM
            ticket = None
            if ticket_id.startswith('TKT-'):
                ticket = Ticket.query.filter_by(ticket_id=ticket_id).first()
            else:
                ticket = Ticket.query.get(ticket_id)
            
            if not ticket:
                return {'error': 'Ticket not found'}, 404
            
            db.session.delete(ticket)
            db.session.commit()
            return {'message': 'Ticket deleted'}, 204
            
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting ticket {ticket_id}: {e}")
            return {'error': 'Failed to delete ticket'}, 500