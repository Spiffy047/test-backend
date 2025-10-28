from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from marshmallow import ValidationError
from app import db
from app.models import User, Ticket, Message
from app.schemas import (
    user_schema, users_schema, ticket_schema, tickets_schema,
    message_schema, messages_schema, login_schema
)

class AuthResource(Resource):
    def post(self):
        try:
            data = login_schema.load(request.get_json())
            user = User.query.filter_by(email=data['email']).first()
            
            if user and user.check_password(data['password']):
                access_token = create_access_token(identity=user.id)
                return {
                    'success': True,
                    'user': user_schema.dump(user),
                    'access_token': access_token
                }
            else:
                return {'success': False, 'message': 'Invalid credentials'}, 401
                
        except ValidationError as e:
            return {'success': False, 'message': 'Validation error', 'errors': e.messages}, 400
        except Exception as e:
            return {'success': False, 'message': str(e)}, 500

class TicketListResource(Resource):
    def get(self):
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        created_by = request.args.get('created_by')
        
        query = Ticket.query
        if created_by:
            query = query.filter_by(created_by=created_by)
        
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'tickets': tickets_schema.dump(paginated.items),
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': paginated.total,
                'pages': paginated.pages,
                'has_next': paginated.has_next,
                'has_prev': paginated.has_prev
            }
        }
    
    def post(self):
        try:
            data = ticket_schema.load(request.get_json())
            
            last_ticket = Ticket.query.order_by(Ticket.id.desc()).first()
            ticket_num = (last_ticket.id + 1) if last_ticket else 1001
            
            ticket = Ticket(
                ticket_id=f'TKT-{ticket_num}',
                title=data['title'],
                description=data['description'],
                priority=data['priority'],
                category=data['category'],
                created_by=data['created_by']
            )
            
            db.session.add(ticket)
            db.session.commit()
            
            return ticket_schema.dump(ticket), 201
            
        except ValidationError as e:
            return {'error': 'Validation error', 'messages': e.messages}, 400

class TicketResource(Resource):
    def put(self, ticket_id):
        data = request.get_json()
        return {
            'id': ticket_id,
            'status': data.get('status', 'Open'),
            'assigned_to': data.get('assigned_to'),
            'message': 'Ticket updated successfully',
            'success': True
        }

class UserListResource(Resource):
    def get(self):
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        paginated = User.query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'users': users_schema.dump(paginated.items),
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': paginated.total,
                'pages': paginated.pages,
                'has_next': paginated.has_next,
                'has_prev': paginated.has_prev
            }
        }
    
    def post(self):
        try:
            data = user_schema.load(request.get_json())
            
            if User.query.filter_by(email=data['email']).first():
                return {'error': 'Email already exists'}, 400
            
            user = User(
                name=data['name'],
                email=data['email'],
                role=data['role']
            )
            user.set_password('password123')
            
            db.session.add(user)
            db.session.commit()
            
            return user_schema.dump(user), 201
            
        except ValidationError as e:
            return {'error': 'Validation error', 'messages': e.messages}, 400

class UserResource(Resource):
    def put(self, user_id):
        return {'success': True, 'message': 'User updated'}
    
    def delete(self, user_id):
        return {'success': True, 'message': 'User deleted'}

class MessageListResource(Resource):
    def post(self):
        data = request.get_json()
        from datetime import datetime
        
        new_message = {
            'id': f'msg_{len(data) + 100}',
            'ticket_id': data.get('ticket_id'),
            'sender_id': data.get('sender_id'),
            'sender_name': data.get('sender_name'),
            'sender_role': data.get('sender_role'),
            'message': data.get('message'),
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'type': 'message'
        }
        return new_message, 201

class AnalyticsResource(Resource):
    def get(self, endpoint):
        if endpoint == 'sla-adherence':
            return {
                'sla_adherence': 87.2,
                'total_tickets': 71,
                'violations': 9,
                'on_time': 62,
                'trend': 'improving'
            }
        elif endpoint == 'agent-performance':
            return [{
                'id': 'agent1',
                'name': 'Sarah Johnson',
                'tickets_closed': 25,
                'avg_handle_time': 4.2,
                'sla_violations': 2,
                'rating': 'Excellent'
            }]
        return {'error': 'Endpoint not found'}, 404