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
        """Retrieve all tickets from database with proper formatting"""
        try:
            # Import SQLAlchemy text for raw SQL queries
            from sqlalchemy import text
            from app import db
            
            # Execute raw SQL query to get all ticket data
            # Using raw SQL for better performance and compatibility
            result = db.session.execute(text("""
                SELECT id, ticket_id, title, description, priority, category, status, 
                       created_by, assigned_to, created_at, updated_at, sla_violated
                FROM tickets 
                ORDER BY created_at DESC
            """))
            
            # Transform database rows into JSON-serializable format
            tickets = []
            for row in result:
                tickets.append({
                    # Use ticket_id if available, otherwise generate from numeric id
                    'id': row[1] or f'TKT-{row[0]}',
                    'ticket_id': row[1] or f'TKT-{row[0]}',
                    'title': row[2],
                    'description': row[3],
                    'priority': row[4],
                    'category': row[5],
                    'status': row[6],
                    'created_by': row[7],
                    'assigned_to': row[8],
                    # Convert datetime objects to ISO format strings
                    'created_at': row[9].isoformat() if row[9] else None,
                    'updated_at': row[10].isoformat() if row[10] else None,
                    'sla_violated': row[11] or False
                })
            
            return {'tickets': tickets}
        except Exception as e:
            # Log error and return empty list to prevent frontend crashes
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
            # Generate sequential ticket ID starting from TKT-1001
            from sqlalchemy import text
            
            # Count existing tickets to generate next sequential ID
            result = db.session.execute(text("SELECT COUNT(*) FROM tickets"))
            ticket_count = result.scalar() + 1001  # Start numbering from 1001
            ticket_id = f"TKT-{ticket_count}"
            
            # Insert new ticket using raw SQL for database compatibility
            # Using parameterized queries to prevent SQL injection
            db.session.execute(text("""
                INSERT INTO tickets (ticket_id, title, description, priority, category, status, created_by, created_at, updated_at)
                VALUES (:ticket_id, :title, :description, :priority, :category, 'New', :created_by, NOW(), NOW())
            """), {
                'ticket_id': ticket_id,
                'title': data['title'],
                'description': data['description'],
                'priority': data.get('priority', 'Medium'),  # Default to Medium if not specified
                'category': data['category'],
                'created_by': user_id
            })
            
            # Commit transaction to database
            db.session.commit()
            
            # Return created ticket data for frontend confirmation
            return {
                'id': ticket_id,
                'ticket_id': ticket_id,
                'title': data['title'],
                'description': data['description'],
                'priority': data.get('priority', 'Medium'),
                'category': data['category'],
                'status': 'New',
                'created_by': user_id,
                'created_at': datetime.utcnow().isoformat() + 'Z'
            }, 201
            
        except Exception as e:
            # Rollback transaction on error to maintain data integrity
            db.session.rollback()
            print(f"Error creating ticket: {e}")
            return {'error': 'Failed to create ticket'}, 500

class TicketResource(Resource):
    """Handle individual ticket operations (GET, PUT, DELETE)"""
    
    def get(self, ticket_id):
        """Retrieve specific ticket by ID"""
        try:
            from sqlalchemy import text
            
            # Query specific ticket from database - handle both ticket_id and numeric id
            if ticket_id.startswith('TKT-'):
                # Search by ticket_id
                result = db.session.execute(text("""
                    SELECT id, ticket_id, title, description, priority, category, status, 
                           created_by, assigned_to, created_at, updated_at, sla_violated
                    FROM tickets 
                    WHERE ticket_id = :ticket_id
                """), {'ticket_id': ticket_id})
            else:
                # Search by numeric id
                result = db.session.execute(text("""
                    SELECT id, ticket_id, title, description, priority, category, status, 
                           created_by, assigned_to, created_at, updated_at, sla_violated
                    FROM tickets 
                    WHERE id = :id
                """), {'id': ticket_id})
            
            row = result.fetchone()
            if not row:
                return {'error': 'Ticket not found'}, 404
            
            return {
                'id': row[1] or f'TKT-{row[0]}',
                'ticket_id': row[1] or f'TKT-{row[0]}',
                'title': row[2],
                'description': row[3],
                'priority': row[4],
                'category': row[5],
                'status': row[6],
                'created_by': row[7],
                'assigned_to': row[8],
                'created_at': row[9].isoformat() if row[9] else None,
                'updated_at': row[10].isoformat() if row[10] else None,
                'sla_violated': row[11] or False
            }
        except Exception as e:
            print(f"Error fetching ticket {ticket_id}: {e}")
            return {'error': 'Failed to retrieve ticket'}, 500
    
    def put(self, ticket_id):
        """Update existing ticket (status, assignment, etc.)"""
        data = request.get_json()
        
        try:
            from sqlalchemy import text
            
            # Build dynamic update query based on provided fields
            update_fields = []
            params = {}
            
            if 'status' in data:
                update_fields.append('status = :status')
                params['status'] = data['status']
                
                # Set resolved_at timestamp when ticket is resolved
                if data['status'] in ['Resolved', 'Closed']:
                    update_fields.append('resolved_at = NOW()')
            
            if 'assigned_to' in data:
                update_fields.append('assigned_to = :assigned_to')
                params['assigned_to'] = data['assigned_to']
            
            if 'priority' in data:
                update_fields.append('priority = :priority')
                params['priority'] = data['priority']
            
            if not update_fields:
                return {'error': 'No valid fields to update'}, 400
            
            # Add updated_at timestamp
            update_fields.append('updated_at = NOW()')
            
            # Handle both ticket_id and numeric id formats
            if ticket_id.startswith('TKT-'):
                where_clause = 'ticket_id = :ticket_id'
                params['ticket_id'] = ticket_id
            else:
                where_clause = 'id = :id'
                params['id'] = ticket_id
            
            # Execute update query
            query = f"UPDATE tickets SET {', '.join(update_fields)} WHERE {where_clause}"
            result = db.session.execute(text(query), params)
            
            if result.rowcount == 0:
                return {'error': 'Ticket not found'}, 404
            
            db.session.commit()
            
            return {
                'id': ticket_id,
                'message': 'Ticket updated successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            print(f"Error updating ticket {ticket_id}: {e}")
            return {'error': 'Failed to update ticket'}, 500
    
    def delete(self, ticket_id):
        """Delete ticket by ID"""
        try:
            from sqlalchemy import text
            
            # Delete ticket from database
            result = db.session.execute(text("""
                DELETE FROM tickets WHERE ticket_id = :ticket_id
            """), {'ticket_id': ticket_id})
            
            if result.rowcount == 0:
                return {'error': 'Ticket not found'}, 404
            
            db.session.commit()
            return {'message': 'Ticket deleted'}, 204
            
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting ticket {ticket_id}: {e}")
            return {'error': 'Failed to delete ticket'}, 500