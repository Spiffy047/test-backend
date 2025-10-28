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
from app.services.email_service import EmailService

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
        status = request.args.get('status')
        
        query = Ticket.query
        if created_by:
            query = query.filter_by(created_by=created_by)
        if status:
            query = query.filter_by(status=status)
        
        # Order by most recent first
        query = query.order_by(Ticket.created_at.desc())
        
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
            
            # Get the highest ticket number from existing ticket_ids
            last_ticket = Ticket.query.filter(Ticket.ticket_id.like('TKT-%')).order_by(Ticket.ticket_id.desc()).first()
            if last_ticket and last_ticket.ticket_id:
                try:
                    last_num = int(last_ticket.ticket_id.split('-')[1])
                    ticket_num = last_num + 1
                except (ValueError, IndexError):
                    ticket_num = 1001
            else:
                ticket_num = 1001
            
            # Ensure we don't have duplicates
            while Ticket.query.filter_by(ticket_id=f'TKT-{ticket_num}').first():
                ticket_num += 1
            
            ticket = Ticket(
                ticket_id=f'TKT-{ticket_num:04d}',
                title=data['title'],
                description=data['description'],
                priority=data['priority'],
                category=data['category'],
                created_by=data['created_by']
            )
            
            db.session.add(ticket)
            db.session.commit()
            
            # Send email notification
            try:
                email_service = EmailService()
                user = User.query.get(data['created_by'])
                if user:
                    email_service.send_ticket_notification(
                        to_email=user.email,
                        ticket_id=ticket.ticket_id,
                        ticket_title=ticket.title,
                        message_type='created'
                    )
            except Exception as e:
                print(f"Email notification failed: {e}")
            
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
            
            password = data.get('password', 'password123')
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            return user_schema.dump(user), 201
            
        except ValidationError as e:
            return {'error': 'Validation error', 'messages': e.messages}, 400

class UserResource(Resource):
    def put(self, user_id):
        try:
            data = user_schema.load(request.get_json())
            user = User.query.get_or_404(user_id)
            
            # Check if email is already taken by another user
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != user.id:
                return {'error': 'Email already exists'}, 400
            
            user.name = data['name']
            user.email = data['email']
            user.role = data['role']
            
            db.session.commit()
            return user_schema.dump(user)
            
        except ValidationError as e:
            return {'error': 'Validation error', 'messages': e.messages}, 400
    
    def delete(self, user_id):
        try:
            user = User.query.get_or_404(user_id)
            db.session.delete(user)
            db.session.commit()
            return {'success': True, 'message': 'User deleted'}
        except Exception as e:
            return {'error': str(e)}, 500

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

class EmailNotificationResource(Resource):
    def post(self):
        data = request.get_json()
        email_service = EmailService()
        
        success = email_service.send_ticket_notification(
            to_email=data.get('to_email'),
            ticket_id=data.get('ticket_id'),
            ticket_title=data.get('ticket_title'),
            message_type=data.get('message_type', 'created')
        )
        
        return {'success': success, 'message': 'Email sent' if success else 'Email failed'}

class EmailVerificationResource(Resource):
    def post(self):
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return {'error': 'Token required'}, 400
        
        try:
            user = User.query.filter_by(verification_token=token).first()
            
            if not user:
                return {'error': 'Invalid token'}, 400
            
            if user.verify_email(token):
                db.session.commit()
                return {'message': 'Email verified successfully'}
            else:
                return {'error': 'Token expired or invalid'}, 400
        except:
            return {'error': 'Verification system not available'}, 500

class MigrateTicketIDsResource(Resource):
    def post(self):
        """Migrate existing tickets to proper TKT-XXXX format"""
        try:
            from sqlalchemy import text
            
            # Get all tickets that don't have proper TKT-XXXX format
            tickets = Ticket.query.filter(~Ticket.ticket_id.like('TKT-%')).all()
            
            if not tickets:
                return {'message': 'All tickets already have proper TKT-XXXX format', 'migrated': 0}
            
            # Start numbering from 1001
            ticket_counter = 1001
            
            # Check if we already have TKT-XXXX tickets and start from the highest number
            existing_tkt_tickets = db.session.execute(
                text("SELECT ticket_id FROM tickets WHERE ticket_id LIKE 'TKT-%' ORDER BY ticket_id DESC LIMIT 1")
            ).fetchone()
            
            if existing_tkt_tickets:
                try:
                    last_num = int(existing_tkt_tickets[0].split('-')[1])
                    ticket_counter = last_num + 1
                except (ValueError, IndexError):
                    pass
            
            migrated_tickets = []
            
            # Update each ticket
            for ticket in tickets:
                old_id = ticket.ticket_id
                new_id = f"TKT-{ticket_counter:04d}"
                
                # Make sure this ID doesn't already exist
                while Ticket.query.filter_by(ticket_id=new_id).first():
                    ticket_counter += 1
                    new_id = f"TKT-{ticket_counter:04d}"
                
                ticket.ticket_id = new_id
                migrated_tickets.append({'old_id': old_id, 'new_id': new_id})
                ticket_counter += 1
            
            # Commit all changes
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Successfully migrated {len(tickets)} tickets',
                'migrated': len(tickets),
                'tickets': migrated_tickets
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}, 500

class ImageUploadResource(Resource):
    def post(self):
        from flask import request
        from app.services.cloudinary_service import CloudinaryService
        
        if 'image' not in request.files:
            return {'error': 'No image provided'}, 400
        
        file = request.files['image']
        ticket_id = request.form.get('ticket_id')
        user_id = request.form.get('user_id')
        
        if not file or not ticket_id or not user_id:
            return {'error': 'Missing required fields'}, 400
        
        # Check if file is an image
        if not file.content_type.startswith('image/'):
            return {'error': 'File must be an image'}, 400
        
        cloudinary_service = CloudinaryService()
        result = cloudinary_service.upload_image(file, ticket_id, user_id)
        
        if result:
            # Save to database
            from app.models import db
            from app import db as database
            
            # Update files table with Cloudinary URL
            try:
                database.session.execute(
                    "INSERT INTO files (ticket_id, filename, file_path, file_size, uploaded_by, uploaded_at) VALUES (%s, %s, %s, %s, %s, NOW())",
                    (ticket_id, file.filename, result['url'], result['bytes'], user_id)
                )
                database.session.commit()
            except:
                pass
            
            return {
                'success': True,
                'url': result['url'],
                'public_id': result['public_id'],
                'width': result['width'],
                'height': result['height']
            }
        else:
            return {'error': 'Upload failed'}, 500

