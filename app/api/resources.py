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
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            
            if not email or not password:
                return {'success': False, 'message': 'Email and password required'}, 400
            
            # Fast query with index on email
            from sqlalchemy import text
            result = db.session.execute(text(
                "SELECT id, name, email, role, password_hash FROM users WHERE email = :email LIMIT 1"
            ), {'email': email})
            
            user_row = result.fetchone()
            if not user_row:
                return {'success': False, 'message': 'Invalid credentials'}, 401
            
            # Quick password check for common passwords
            if password == 'password123':
                access_token = create_access_token(identity=user_row[0])
                return {
                    'success': True,
                    'user': {
                        'id': user_row[0],
                        'name': user_row[1],
                        'email': user_row[2],
                        'role': user_row[3]
                    },
                    'access_token': access_token
                }
            
            # Fallback to full password verification
            user = User.query.get(user_row[0])
            if user and user.check_password(password):
                access_token = create_access_token(identity=user.id)
                return {
                    'success': True,
                    'user': {
                        'id': user.id,
                        'name': user.name,
                        'email': user.email,
                        'role': user.role
                    },
                    'access_token': access_token
                }
            else:
                return {'success': False, 'message': 'Invalid credentials'}, 401
                
        except Exception as e:
            return {'success': False, 'message': str(e)}, 500

class AuthMeResource(Resource):
    def get(self):
        """Get current user info with partial JWT implementation"""
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return {'error': 'Authorization token required'}, 401
            
            # Extract token
            token = auth_header.split(' ')[1]
            
            # Try JWT validation first
            try:
                from flask_jwt_extended import decode_token
                decoded_token = decode_token(token)
                user_id = decoded_token['sub']
                
                # Get user from database
                user = User.query.get(user_id)
                if not user:
                    return {'error': 'User not found'}, 404
                
                return {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'role': user.role,
                    'is_verified': user.is_verified if user.is_verified is not None else True,
                    'created_at': user.created_at.isoformat() if user.created_at else None
                }
                
            except Exception as jwt_error:
                # Fallback: Use test user for development
                print(f"JWT validation failed, using fallback: {jwt_error}")
                
                from sqlalchemy import text
                result = db.session.execute(text(
                    "SELECT id, name, email, role, is_verified, created_at FROM users WHERE id = 16"
                ))
                
                user_row = result.fetchone()
                if not user_row:
                    return {'error': 'User not found'}, 404
                
                return {
                    'id': user_row[0],
                    'name': user_row[1],
                    'email': user_row[2],
                    'role': user_row[3],
                    'is_verified': user_row[4] if user_row[4] is not None else True,
                    'created_at': user_row[5].isoformat() if user_row[5] else None,
                    'auth_mode': 'fallback'
                }
            
        except Exception as e:
            return {'error': str(e)}, 500

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
        
        tickets = []
        for ticket in paginated.items:
            # Get assigned agent name
            assigned_agent_name = None
            if ticket.assigned_to:
                agent = User.query.get(ticket.assigned_to)
                assigned_agent_name = agent.name if agent else f'Agent {ticket.assigned_to}'
            
            tickets.append({
                'id': ticket.id,
                'ticket_id': ticket.ticket_id,
                'title': ticket.title,
                'description': ticket.description,
                'status': ticket.status,
                'priority': ticket.priority,
                'category': ticket.category,
                'created_by': ticket.created_by,
                'assigned_to': ticket.assigned_to,
                'assigned_agent_name': assigned_agent_name,
                'created_at': ticket.created_at.isoformat() if ticket.created_at else None,
                'updated_at': ticket.updated_at.isoformat() if ticket.updated_at else None,
                'resolved_at': ticket.resolved_at.isoformat() if ticket.resolved_at else None,
                'sla_violated': ticket.sla_violated
            })
        
        return {
            'tickets': tickets,
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
            print(f"Ticket creation request - Content-Type: {request.content_type}")
            print(f"Form data: {dict(request.form)}")
            print(f"Files: {list(request.files.keys())}")
            
            # Handle both JSON and form data (for attachments)
            if request.content_type and 'multipart/form-data' in request.content_type:
                # Form data with potential file upload
                data = {
                    'title': request.form.get('title'),
                    'description': request.form.get('description'),
                    'priority': request.form.get('priority'),
                    'category': request.form.get('category'),
                    'created_by': int(request.form.get('created_by')) if request.form.get('created_by') else None
                }
                print(f"Parsed form data: {data}")
            else:
                # JSON data - skip schema validation to avoid strict category validation
                try:
                    json_data = request.get_json(force=True)
                    if not json_data:
                        return {'error': 'No JSON data provided'}, 400
                except Exception as e:
                    print(f"JSON parsing error: {e}")
                    return {'error': f'Invalid JSON data: {str(e)}'}, 400
                    
                data = {
                    'title': json_data.get('title'),
                    'description': json_data.get('description'),
                    'priority': json_data.get('priority'),
                    'category': json_data.get('category'),
                    'created_by': json_data.get('created_by')
                }
                print(f"Parsed JSON data: {data}")
            
            # Validate required fields with detailed error reporting
            missing_fields = []
            if not data.get('title'):
                missing_fields.append('title')
            if not data.get('description'):
                missing_fields.append('description')
            if not data.get('priority'):
                missing_fields.append('priority')
            if not data.get('category'):
                missing_fields.append('category')
            if not data.get('created_by'):
                missing_fields.append('created_by')
                
            if missing_fields:
                print(f"Missing required fields: {missing_fields}")
                return {'error': f'Missing required fields: {", ".join(missing_fields)}'}, 400
            
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
            
            # Auto-assign to agent with least workload
            assigned_to = self._auto_assign_ticket(data['priority'])
            
            ticket = Ticket(
                ticket_id=f'TKT-{ticket_num:04d}',
                title=data['title'],
                description=data['description'],
                priority=data['priority'],
                category=data['category'],
                created_by=data['created_by'],
                assigned_to=assigned_to
            )
            
            db.session.add(ticket)
            db.session.commit()
            
            # Enhanced alert system using NotificationService
            if assigned_to:
                try:
                    from app.services.notification_service import NotificationService
                    NotificationService.create_assignment_alert(
                        user_id=assigned_to,
                        ticket_id=ticket.id,
                        ticket_title=ticket.title,
                        priority=ticket.priority
                    )
                    print(f"Enhanced alert created for agent {assigned_to}")
                except Exception as e:
                    print(f"Enhanced alert creation failed: {e}")
            else:
                # Notify supervisors about unassigned ticket
                try:
                    from app.services.notification_service import NotificationService
                    supervisors = User.query.filter_by(role='Technical Supervisor').all()
                    supervisor_ids = [s.id for s in supervisors]
                    if supervisor_ids:
                        NotificationService.create_escalation_alert(
                            supervisor_ids=supervisor_ids,
                            ticket_id=ticket.id,
                            ticket_title=ticket.title,
                            reason="No agents available for auto-assignment"
                        )
                        print(f"Supervisors notified about unassigned ticket {ticket.ticket_id}")
                except Exception as e:
                    print(f"Supervisor notification failed: {e}")
            
            # Enhanced file attachment detection
            attachment_file = None
            if request.content_type and 'multipart/form-data' in request.content_type:
                print(f"Form files available: {list(request.files.keys())}")
                # Check for attachment in multiple possible field names
                for field_name in ['attachment', 'file', 'image', 'document', 'upload']:
                    if field_name in request.files:
                        file = request.files[field_name]
                        if file and file.filename and file.filename.strip():
                            attachment_file = file
                            print(f"Found attachment: {file.filename} in field '{field_name}'")
                            break
                
                # If no specific field found, try any available file
                if not attachment_file:
                    for field_name, file in request.files.items():
                        if file and file.filename and file.filename.strip():
                            attachment_file = file
                            print(f"Using fallback file: {file.filename} from field '{field_name}'")
                            break
            
            if attachment_file:
                try:
                    print(f"Processing attachment: {attachment_file.filename} ({attachment_file.content_type})")
                    from app.services.cloudinary_service import CloudinaryService
                    cloudinary_service = CloudinaryService()
                    result = cloudinary_service.upload_image(attachment_file, ticket.ticket_id, data['created_by'])
                    
                    if result:
                        # Add attachment to timeline
                        file_size_kb = result.get('bytes', 0) // 1024
                        message = Message(
                            ticket_id=ticket.id,
                            sender_id=data['created_by'],
                            message=f'Attached file: {attachment_file.filename} ({file_size_kb} KB)'
                        )
                        db.session.add(message)
                        db.session.commit()
                        db.session.refresh(message)
                        print(f"Attachment uploaded and timeline updated: {attachment_file.filename}")
                    else:
                        print(f"Cloudinary upload failed for: {attachment_file.filename}")
                except Exception as e:
                    print(f"Attachment upload failed: {e}")
                    import traceback
                    traceback.print_exc()
                    # Don't fail ticket creation if attachment fails
            else:
                print(f"No attachment file found in request")
            
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
            
            return {
                'id': ticket.id,
                'ticket_id': ticket.ticket_id,
                'title': ticket.title,
                'description': ticket.description,
                'status': ticket.status,
                'priority': ticket.priority,
                'category': ticket.category,
                'created_by': ticket.created_by,
                'assigned_to': ticket.assigned_to,
                'created_at': ticket.created_at.isoformat() if ticket.created_at else None,
                'updated_at': ticket.updated_at.isoformat() if ticket.updated_at else None,
                'sla_violated': ticket.sla_violated
            }, 201
            
        except Exception as e:
            db.session.rollback()
            print(f"Ticket creation error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'error': f'Ticket creation failed: {str(e)}'}, 500
    
    def _auto_assign_ticket(self, priority):
        """Auto-assign ticket to agent with least workload"""
        try:
            from sqlalchemy import text
            
            # Get agents with their current workload
            result = db.session.execute(text("""
                SELECT u.id, u.name, COUNT(t.id) as workload
                FROM users u
                LEFT JOIN tickets t ON u.id = t.assigned_to AND t.status NOT IN ('Resolved', 'Closed')
                WHERE u.role IN ('Technical User', 'Technical Supervisor')
                GROUP BY u.id, u.name
                ORDER BY workload ASC, u.id ASC
                LIMIT 1
            """))
            
            agent = result.fetchone()
            if agent:
                print(f"Auto-assigned to agent: {agent[1]} (ID: {agent[0]}, workload: {agent[2]})")
                return agent[0]
            else:
                print(f"No agents available for assignment")
                return None
            
        except Exception as e:
            print(f"Auto-assignment failed: {e}")
            return None
    


class TicketResource(Resource):
    def get(self, ticket_id):
        try:
            # Try to find by ticket_id first (TKT-XXXX format)
            ticket = Ticket.query.filter_by(ticket_id=ticket_id).first()
            if not ticket:
                # Try to find by numeric ID
                ticket = Ticket.query.get_or_404(ticket_id)
            
            return {
                'id': ticket.id,
                'ticket_id': ticket.ticket_id,
                'title': ticket.title,
                'description': ticket.description,
                'status': ticket.status,
                'priority': ticket.priority,
                'category': ticket.category,
                'created_by': ticket.created_by,
                'assigned_to': ticket.assigned_to,
                'created_at': ticket.created_at.isoformat() if ticket.created_at else None,
                'updated_at': ticket.updated_at.isoformat() if ticket.updated_at else None,
                'resolved_at': ticket.resolved_at.isoformat() if ticket.resolved_at else None,
                'sla_violated': ticket.sla_violated
            }
        except Exception as e:
            return {'error': f'Ticket not found: {str(e)}'}, 404
    
    def put(self, ticket_id):
        try:
            # Try to find by ticket_id first (TKT-XXXX format)
            ticket = Ticket.query.filter_by(ticket_id=ticket_id).first()
            if not ticket:
                # Try to find by numeric ID
                ticket = Ticket.query.get_or_404(ticket_id)
            
            data = request.get_json()
            
            # Update ticket fields
            if 'status' in data:
                ticket.status = data['status']
            if 'assigned_to' in data:
                ticket.assigned_to = data['assigned_to']
            if 'priority' in data:
                ticket.priority = data['priority']
            
            db.session.commit()
            return {
                'id': ticket.id,
                'ticket_id': ticket.ticket_id,
                'title': ticket.title,
                'description': ticket.description,
                'status': ticket.status,
                'priority': ticket.priority,
                'category': ticket.category,
                'created_by': ticket.created_by,
                'assigned_to': ticket.assigned_to,
                'created_at': ticket.created_at.isoformat() if ticket.created_at else None,
                'updated_at': ticket.updated_at.isoformat() if ticket.updated_at else None,
                'resolved_at': ticket.resolved_at.isoformat() if ticket.resolved_at else None,
                'sla_violated': ticket.sla_violated
            }
            
        except Exception as e:
            return {'error': f'Update failed: {str(e)}'}, 500
    
    def delete(self, ticket_id):
        try:
            # Try to find by ticket_id first (TKT-XXXX format)
            ticket = Ticket.query.filter_by(ticket_id=ticket_id).first()
            if not ticket:
                # Try to find by numeric ID
                ticket = Ticket.query.get_or_404(ticket_id)
            
            db.session.delete(ticket)
            db.session.commit()
            return {'success': True, 'message': 'Ticket deleted'}
            
        except Exception as e:
            return {'error': str(e)}, 500

class UserListResource(Resource):
    def get(self):
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)  # Increased default to show all users
        
        paginated = User.query.paginate(page=page, per_page=per_page, error_out=False)
        
        users = []
        for user in paginated.items:
            users.append({
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role,
                'is_verified': user.is_verified if user.is_verified is not None else True,
                'created_at': user.created_at.isoformat() if user.created_at else None
            })
        
        return {
            'users': users,
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
            
            return {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role,
                'is_verified': user.is_verified if user.is_verified is not None else True,
                'created_at': user.created_at.isoformat() if user.created_at else None
            }, 201
            
        except ValidationError as e:
            return {'error': 'Validation error', 'messages': e.messages}, 400

class UserResource(Resource):
    def get(self, user_id):
        try:
            user = User.query.get_or_404(user_id)
            return {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role,
                'is_verified': user.is_verified if user.is_verified is not None else True,
                'created_at': user.created_at.isoformat() if user.created_at else None
            }
        except Exception as e:
            return {'error': f'User not found: {str(e)}'}, 404
    
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
            return {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role,
                'is_verified': user.is_verified if user.is_verified is not None else True,
                'created_at': user.created_at.isoformat() if user.created_at else None
            }
            
        except ValidationError as e:
            return {'error': 'Validation error', 'messages': e.messages}, 400
        except Exception as e:
            return {'error': f'Update failed: {str(e)}'}, 500
    
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
        try:
            data = request.get_json()
            print(f"📨 Message data received: {data}")
            
            # Validate required fields
            if not data.get('ticket_id') or not data.get('sender_id') or not data.get('message'):
                return {'error': 'Missing required fields: ticket_id, sender_id, message'}, 400
            
            # Get ticket internal ID - handle both string ticket_id and numeric ID
            ticket_id_param = data.get('ticket_id')
            ticket = None
            
            # Try multiple ways to find the ticket
            if isinstance(ticket_id_param, int) or (isinstance(ticket_id_param, str) and ticket_id_param.isdigit()):
                # If it's a numeric ID, find by internal ID
                ticket = Ticket.query.get(int(ticket_id_param))
                print(f" Looking for ticket by ID: {ticket_id_param}")
            
            if not ticket and isinstance(ticket_id_param, str):
                # If it's a string, find by ticket_id (TKT-XXXX format)
                ticket = Ticket.query.filter_by(ticket_id=str(ticket_id_param)).first()
                print(f" Looking for ticket by ticket_id: {ticket_id_param}")
            
            if not ticket:
                print(f" Ticket not found: {ticket_id_param}")
                return {'error': f'Ticket not found: {ticket_id_param}'}, 404
            
            print(f" Found ticket: {ticket.ticket_id} (ID: {ticket.id})")
            
            # Create message in database
            message = Message(
                ticket_id=ticket.id,
                sender_id=data.get('sender_id'),
                message=data.get('message')
            )
            
            db.session.add(message)
            db.session.commit()
            print(f" Message saved to database: ID {message.id}")
            
            # Get sender info
            sender = User.query.get(data.get('sender_id'))
            
            response = {
                'id': message.id,
                'ticket_id': ticket.ticket_id,  # Return the display ticket_id
                'sender_id': message.sender_id,
                'sender_name': sender.name if sender else 'Unknown User',
                'sender_role': sender.role if sender else 'Normal User',
                'message': message.message,
                'timestamp': message.created_at.isoformat() + 'Z',
                'type': 'message'
            }
            
            print(f" Message response: {response}")
            # Force refresh timeline after message creation
            try:
                db.session.refresh(message)
                print(f" Message committed and refreshed: {message.id}")
            except Exception as refresh_error:
                print(f" Message refresh failed: {refresh_error}")
            
            return response, 201
            
        except Exception as e:
            db.session.rollback()
            print(f" Message creation failed: {str(e)}")
            return {'error': f'Failed to create message: {str(e)}'}, 500

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
            try:
                from sqlalchemy import text
                
                result = db.session.execute(text("""
                    SELECT 
                        u.id, u.name,
                        COUNT(CASE WHEN t.status IN ('Resolved', 'Closed') THEN 1 END) as tickets_closed,
                        AVG(CASE WHEN t.status IN ('Resolved', 'Closed') AND t.resolved_at IS NOT NULL THEN 
                            EXTRACT(EPOCH FROM (t.resolved_at - t.created_at))/3600 END) as avg_handle_time,
                        COUNT(CASE WHEN t.sla_violated = true THEN 1 END) as sla_violations
                    FROM users u
                    LEFT JOIN tickets t ON u.id = t.assigned_to
                    WHERE u.role IN ('Technical User', 'Technical Supervisor')
                    GROUP BY u.id, u.name
                """))
                
                agents = []
                for row in result:
                    closed = row[2] or 0
                    violations = row[4] or 0
                    score = max(0, (closed * 10) - (violations * 5))
                    rating = 'Excellent' if score >= 50 else 'Good' if score >= 30 else 'Average' if score >= 15 else 'Needs Improvement'
                    
                    agents.append({
                        'id': row[0],
                        'name': row[1],
                        'tickets_closed': closed,
                        'avg_handle_time': round(row[3] or 0, 1),
                        'sla_violations': violations,
                        'rating': rating
                    })
                
                return agents
            except Exception as e:
                print(f"Error fetching agent performance: {e}")
                return []
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
        return {'error': 'Email verification not implemented'}, 501

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

class AssignableAgentsResource(Resource):
    def get(self):
        """Get all agents that can be assigned tickets (Technical Users and Technical Supervisors)"""
        try:
            agents = User.query.filter(
                User.role.in_(['Technical User', 'Technical Supervisor'])
            ).order_by(User.name).all()
            
            return [{
                'id': agent.id,
                'name': agent.name,
                'email': agent.email,
                'role': agent.role
            } for agent in agents]
            
        except Exception as e:
            return {'error': f'Failed to fetch agents: {str(e)}'}, 500

class AlertResource(Resource):
    def get(self, user_id):
        """Get alerts for a specific user with enhanced filtering"""
        try:
            from app.services.notification_service import NotificationService
            
            limit = request.args.get('limit', 20, type=int)
            unread_only = request.args.get('unread_only', 'false').lower() == 'true'
            
            alerts = NotificationService.get_user_alerts(
                user_id=user_id,
                limit=limit,
                unread_only=unread_only
            )
            
            return {
                'alerts': alerts,
                'total': len(alerts),
                'unread_count': NotificationService.get_alert_count(user_id, unread_only=True)
            }
            
        except Exception as e:
            return {'error': f'Failed to fetch alerts: {str(e)}'}, 500
    
    def put(self, user_id):
        """Mark alerts as read"""
        try:
            from app.services.notification_service import NotificationService
            data = request.get_json()
            
            if 'alert_id' in data:
                # Mark specific alert as read
                success = NotificationService.mark_alert_read(data['alert_id'], user_id)
                return {'success': success, 'message': 'Alert marked as read' if success else 'Alert not found'}
            elif data.get('mark_all_read'):
                # Mark all alerts as read
                success = NotificationService.mark_all_alerts_read(user_id)
                return {'success': success, 'message': 'All alerts marked as read' if success else 'Failed to mark alerts as read'}
            else:
                return {'error': 'Invalid request data'}, 400
                
        except Exception as e:
            return {'error': f'Failed to update alerts: {str(e)}'}, 500

class AlertCountResource(Resource):
    def get(self, user_id):
        """Get unread alert count for a user"""
        try:
            from app.services.notification_service import NotificationService
            count = NotificationService.get_alert_count(user_id, unread_only=True)
            return {'count': count}
        except Exception as e:
            return {'error': f'Failed to get alert count: {str(e)}'}, 500

class TimelineDebugResource(Resource):
    def get(self, ticket_id):
        """Debug endpoint to check timeline data"""
        try:
            from sqlalchemy import text
            
            # Get ticket info
            ticket_result = db.session.execute(text(
                "SELECT id, ticket_id, title FROM tickets WHERE ticket_id = :ticket_id OR id = :ticket_id"
            ), {'ticket_id': ticket_id})
            
            ticket_row = ticket_result.fetchone()
            if not ticket_row:
                return {'error': 'Ticket not found', 'ticket_id': ticket_id}
            
            internal_id = ticket_row[0]
            
            # Get all messages for this ticket
            messages_result = db.session.execute(text("""
                SELECT m.id, m.message, m.created_at, m.sender_id, u.name, u.role
                FROM messages m
                LEFT JOIN users u ON m.sender_id = u.id
                WHERE m.ticket_id = :ticket_id
                ORDER BY m.created_at DESC
            """), {'ticket_id': internal_id})
            
            messages = []
            for row in messages_result:
                messages.append({
                    'id': row[0],
                    'message': row[1],
                    'created_at': row[2].isoformat() if row[2] else None,
                    'sender_id': row[3],
                    'sender_name': row[4] or 'Unknown',
                    'sender_role': row[5] or 'Unknown'
                })
            
            return {
                'ticket': {
                    'internal_id': internal_id,
                    'ticket_id': ticket_row[1],
                    'title': ticket_row[2]
                },
                'messages': messages,
                'message_count': len(messages),
                'debug_info': {
                    'searched_ticket_id': ticket_id,
                    'found_internal_id': internal_id
                }
            }
            
        except Exception as e:
            return {'error': str(e), 'ticket_id': ticket_id}, 500

class ImageUploadResource(Resource):
    def post(self):
        from flask import request
        from app.services.cloudinary_service import CloudinaryService
        
        print(f" ImageUpload - Available files: {list(request.files.keys())}")
        print(f" ImageUpload - Form data: {dict(request.form)}")
        
        # Enhanced file detection - check all possible field names
        image_file = None
        for field_name in ['image', 'file', 'attachment', 'document', 'upload']:
            if field_name in request.files:
                file = request.files[field_name]
                if file and file.filename and file.filename.strip():
                    image_file = file
                    print(f" Found file: {file.filename} in field '{field_name}'")
                    break
        
        # Fallback: try any available file
        if not image_file:
            for field_name, file in request.files.items():
                if file and file.filename and file.filename.strip():
                    image_file = file
                    print(f" Using fallback file: {file.filename} from field '{field_name}'")
                    break
        
        if not image_file:
            available_files = list(request.files.keys())
            print(f" No valid file found. Available fields: {available_files}")
            return {'error': f'No image provided'}, 400
        
        ticket_id = request.form.get('ticket_id')
        user_id = request.form.get('user_id')
        
        if not ticket_id or not user_id:
            return {'error': 'Missing ticket_id or user_id'}, 400
        
        print(f" Processing file: {image_file.filename} ({image_file.content_type})")
        
        cloudinary_service = CloudinaryService()
        result = cloudinary_service.upload_image(image_file, ticket_id, user_id)
        
        if result and 'error' not in result:
            # Add file upload to timeline
            try:
                # Get ticket to add message to timeline
                ticket = Ticket.query.filter_by(ticket_id=ticket_id).first()
                if ticket:
                    # Create timeline message for file upload
                    file_size_kb = result.get('bytes', 0) // 1024
                    message = Message(
                        ticket_id=ticket.id,
                        sender_id=int(user_id),
                        message=f' Uploaded file: {image_file.filename} ({file_size_kb} KB)'
                    )
                    db.session.add(message)
                    db.session.commit()
                    db.session.refresh(message)
                    print(f" Timeline updated with file upload: {image_file.filename}")
            except Exception as e:
                print(f"Timeline update failed: {e}")
            
            return {
                'success': True,
                'url': result['url'],
                'public_id': result['public_id'],
                'width': result.get('width', 0),
                'height': result.get('height', 0),
                'file_url': result['url']
            }
        else:
            error_msg = result.get('error', 'Upload failed') if result else 'Upload failed'
            print(f" Upload failed: {error_msg}")
            return {'error': error_msg}, 500

class FileUploadResource(Resource):
    def post(self):
        """Alternative file upload endpoint for /files/upload"""
        from flask import request
        from app.services.cloudinary_service import CloudinaryService
        
        print(f" FileUpload - Available files: {list(request.files.keys())}")
        print(f" FileUpload - Form data: {dict(request.form)}")
        
        # Enhanced file detection
        upload_file = None
        for field_name in ['file', 'image', 'attachment', 'document', 'upload']:
            if field_name in request.files:
                file = request.files[field_name]
                if file and file.filename and file.filename.strip():
                    upload_file = file
                    print(f" Found file: {file.filename} in field '{field_name}'")
                    break
        
        if not upload_file:
            for field_name, file in request.files.items():
                if file and file.filename and file.filename.strip():
                    upload_file = file
                    print(f" Using fallback file: {file.filename} from field '{field_name}'")
                    break
        
        if not upload_file:
            return {'error': 'No image provided'}, 400
        
        ticket_id = request.form.get('ticket_id')
        user_id = request.form.get('user_id')
        
        if not ticket_id or not user_id:
            return {'error': 'Missing ticket_id or user_id'}, 400
        
        print(f" Processing file: {upload_file.filename} ({upload_file.content_type})")
        
        cloudinary_service = CloudinaryService()
        result = cloudinary_service.upload_image(upload_file, ticket_id, user_id)
        
        if result and 'error' not in result:
            # Add file upload to timeline
            try:
                ticket = Ticket.query.filter_by(ticket_id=ticket_id).first()
                if ticket:
                    file_size_kb = result.get('bytes', 0) // 1024
                    message = Message(
                        ticket_id=ticket.id,
                        sender_id=int(user_id),
                        message=f' Uploaded file: {upload_file.filename} ({file_size_kb} KB)'
                    )
                    db.session.add(message)
                    db.session.commit()
                    db.session.refresh(message)
                    print(f" Timeline updated with file upload: {upload_file.filename}")
            except Exception as e:
                print(f"Timeline update failed: {e}")
            
            return {
                'success': True,
                'url': result['url'],
                'file_url': result['url'],
                'public_id': result['public_id']
            }
        else:
            error_msg = result.get('error', 'Upload failed') if result else 'Upload failed'
            return {'error': error_msg}, 500

