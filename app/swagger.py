from flask_restx import Api, Resource, fields, Namespace
from flask import Blueprint

# Create Swagger API blueprint
swagger_bp = Blueprint('swagger', __name__)

# Initialize Flask-RESTX API with comprehensive Swagger documentation
api = Api(
    swagger_bp,
    version='3.0',
    title='IT ServiceDesk API',
    description='Complete REST API for IT ServiceDesk Platform with intelligent auto-assignment, advanced file upload system, and comprehensive analytics. Live at https://hotfix.onrender.com/api with frontend at https://hotfix-ochre.vercel.app',
    doc='/',
    contact={
        'name': 'IT ServiceDesk Support',
        'email': 'mwanikijoe1@gmail.com'
    },
    license={
        'name': 'MIT License',
        'url': 'https://opensource.org/licenses/MIT'
    },
    authorizations={
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'JWT Bearer token format: Bearer <token>'
        }
    },
    security='Bearer'
)

# Create namespaces for API organization
auth_ns = Namespace('auth', description='Authentication and user session management')
tickets_ns = Namespace('tickets', description='Ticket management with intelligent auto-assignment and SLA tracking')
users_ns = Namespace('users', description='User management with role-based access control')
messages_ns = Namespace('messages', description='Real-time messaging and ticket timeline')
upload_ns = Namespace('upload', description='File and image uploads via Cloudinary with timeline integration')
analytics_ns = Namespace('analytics', description='Real-time analytics, reporting, and dashboard metrics')
config_ns = Namespace('config', description='Dynamic system configuration and settings management')
agents_ns = Namespace('agents', description='Agent management and workload tracking')
alerts_ns = Namespace('alerts', description='Notification and alert system')

api.add_namespace(auth_ns)
api.add_namespace(tickets_ns)
api.add_namespace(users_ns)
api.add_namespace(messages_ns)
api.add_namespace(upload_ns)
api.add_namespace(analytics_ns)
api.add_namespace(config_ns)
api.add_namespace(agents_ns)
api.add_namespace(alerts_ns)

# Define API models for documentation
login_model = api.model('Login', {
    'email': fields.String(required=True, description='User email', example='john.smith@company.com'),
    'password': fields.String(required=True, description='User password', example='password123')
})

user_model = api.model('User', {
    'id': fields.Integer(description='User ID'),
    'name': fields.String(required=True, description='Full name', example='John Smith'),
    'email': fields.String(required=True, description='Email address', example='john.smith@company.com'),
    'role': fields.String(required=True, description='User role', enum=['Normal User', 'Technical User', 'Technical Supervisor', 'System Admin']),
    'is_verified': fields.Boolean(description='Email verification status'),
    'created_at': fields.DateTime(description='Account creation timestamp')
})

ticket_create_model = api.model('TicketCreate', {
    'title': fields.String(required=True, description='Ticket title', example='Email server down'),
    'description': fields.String(required=True, description='Detailed description', example='Users cannot access email since 9 AM'),
    'priority': fields.String(required=True, description='Priority level', enum=['Critical', 'High', 'Medium', 'Low']),
    'category': fields.String(required=True, description='Ticket category', enum=['Hardware', 'Software', 'Network', 'Access', 'Other']),
    'created_by': fields.Integer(required=True, description='Creator user ID', example=16),
    'attachment': fields.Raw(description='Optional file attachment (multipart form data)')
})

ticket_update_model = api.model('TicketUpdate', {
    'status': fields.String(description='Update status', enum=['New', 'Open', 'Pending', 'Resolved', 'Closed']),
    'assigned_to': fields.Integer(description='Assign to agent ID'),
    'priority': fields.String(description='Update priority', enum=['Critical', 'High', 'Medium', 'Low'])
})

ticket_model = api.model('Ticket', {
    'id': fields.Integer(description='Internal ticket ID'),
    'ticket_id': fields.String(description='Display ticket ID', example='TKT-1001'),
    'title': fields.String(description='Ticket title'),
    'description': fields.String(description='Ticket description'),
    'priority': fields.String(description='Priority level'),
    'category': fields.String(description='Ticket category'),
    'status': fields.String(description='Current status'),
    'created_by': fields.Integer(description='Creator user ID'),
    'assigned_to': fields.Integer(description='Assigned agent ID'),
    'assigned_agent_name': fields.String(description='Assigned agent name'),
    'created_at': fields.DateTime(description='Creation timestamp'),
    'updated_at': fields.DateTime(description='Last update timestamp'),
    'resolved_at': fields.DateTime(description='Resolution timestamp'),
    'sla_violated': fields.Boolean(description='SLA violation status')
})

pagination_model = api.model('Pagination', {
    'page': fields.Integer(description='Current page number'),
    'per_page': fields.Integer(description='Items per page'),
    'total': fields.Integer(description='Total items'),
    'pages': fields.Integer(description='Total pages'),
    'has_next': fields.Boolean(description='Has next page'),
    'has_prev': fields.Boolean(description='Has previous page')
})

ticket_list_response = api.model('TicketListResponse', {
    'tickets': fields.List(fields.Nested(ticket_model)),
    'pagination': fields.Nested(pagination_model)
})

message_create_model = api.model('MessageCreate', {
    'ticket_id': fields.String(required=True, description='Ticket ID', example='TKT-1001'),
    'sender_id': fields.Integer(required=True, description='Sender user ID', example=16),
    'message': fields.String(required=True, description='Message content', example='Issue has been resolved')
})

message_model = api.model('Message', {
    'id': fields.Integer(description='Message ID'),
    'ticket_id': fields.String(description='Ticket ID'),
    'sender_id': fields.Integer(description='Sender user ID'),
    'sender_name': fields.String(description='Sender name'),
    'sender_role': fields.String(description='Sender role'),
    'message': fields.String(description='Message content'),
    'timestamp': fields.DateTime(description='Message timestamp'),
    'type': fields.String(description='Message type', example='message')
})

file_upload_model = api.model('FileUpload', {
    'file': fields.Raw(required=True, description='File to upload'),
    'ticket_id': fields.String(required=True, description='Ticket ID'),
    'user_id': fields.Integer(required=True, description='User ID')
})

file_upload_response = api.model('FileUploadResponse', {
    'success': fields.Boolean(description='Upload success status'),
    'url': fields.String(description='File URL'),
    'public_id': fields.String(description='Cloudinary public ID'),
    'width': fields.Integer(description='Image width (if applicable)'),
    'height': fields.Integer(description='Image height (if applicable)')
})

alert_model = api.model('Alert', {
    'id': fields.Integer(description='Alert ID'),
    'title': fields.String(description='Alert title'),
    'message': fields.String(description='Alert message'),
    'alert_type': fields.String(description='Alert type'),
    'is_read': fields.Boolean(description='Read status'),
    'created_at': fields.DateTime(description='Creation timestamp'),
    'ticket_id': fields.String(description='Related ticket ID')
})

agent_model = api.model('Agent', {
    'id': fields.Integer(description='Agent ID'),
    'name': fields.String(description='Agent name'),
    'email': fields.String(description='Agent email'),
    'role': fields.String(description='Agent role')
})

workload_model = api.model('AgentWorkload', {
    'agent_id': fields.Integer(description='Agent ID'),
    'name': fields.String(description='Agent name'),
    'active_tickets': fields.Integer(description='Active tickets count'),
    'pending_tickets': fields.Integer(description='Pending tickets count'),
    'closed_tickets': fields.Integer(description='Closed tickets count')
})

# Authentication endpoints
@auth_ns.route('/login')
class LoginDoc(Resource):
    @auth_ns.expect(login_model)
    @auth_ns.doc('login_user', responses={
        200: 'Login successful',
        401: 'Invalid credentials',
        400: 'Missing email or password'
    })
    def post(self):
        """Authenticate user with email and password
        
        Returns user information and JWT token for subsequent requests.
        Common password for demo: 'password123'
        """
        return {
            'success': True,
            'user': {
                'id': 16,
                'name': 'Demo User',
                'email': 'demo@example.com',
                'role': 'Normal User'
            },
            'access_token': 'jwt_token_here',
            'message': 'Login successful'
        }

@auth_ns.route('/me')
class AuthMeDoc(Resource):
    @auth_ns.doc('get_current_user', 
                 security='Bearer',
                 responses={
                     200: 'User information retrieved',
                     401: 'Invalid or missing token'
                 })
    def get(self):
        """Get current authenticated user information
        
        Requires valid JWT token in Authorization header.
        """
        return {
            'id': 16,
            'name': 'Demo User',
            'email': 'demo@example.com',
            'role': 'Normal User',
            'is_verified': True,
            'created_at': '2024-01-01T00:00:00Z'
        }

@tickets_ns.route('')
class TicketsDoc(Resource):
    @tickets_ns.doc('list_tickets', 
                    params={
                        'page': 'Page number (default: 1)',
                        'per_page': 'Items per page (default: 10)',
                        'created_by': 'Filter by creator user ID',
                        'status': 'Filter by status'
                    },
                    responses={
                        200: ('Success', ticket_list_response)
                    })
    def get(self):
        """Get paginated list of tickets with intelligent filtering
        
        Returns tickets with resolved agent names and comprehensive pagination.
        Supports filtering by creator and status.
        """
        return {
            'tickets': [{
                'id': 1,
                'ticket_id': 'TKT-1001',
                'title': 'Email server down',
                'status': 'Open',
                'priority': 'Critical',
                'assigned_agent_name': 'Sarah Johnson',
                'created_at': '2024-01-01T10:00:00Z'
            }],
            'pagination': {
                'page': 1,
                'per_page': 10,
                'total': 54,
                'pages': 6,
                'has_next': True,
                'has_prev': False
            }
        }
    
    @tickets_ns.expect(ticket_create_model)
    @tickets_ns.doc('create_ticket', 
                    responses={
                        201: ('Ticket created', ticket_model),
                        400: 'Validation error'
                    })
    def post(self):
        """Create new support ticket with intelligent auto-assignment
        
        Supports both JSON and multipart form data for file attachments.
        Automatically assigns to agent with least workload.
        Creates assignment notifications.
        """
        return {
            'id': 1,
            'ticket_id': 'TKT-1001',
            'title': 'Email server down',
            'status': 'New',
            'priority': 'Critical',
            'assigned_to': 13,
            'assigned_agent_name': 'Sarah Johnson',
            'created_at': '2024-01-01T10:00:00Z'
        }

@tickets_ns.route('/<string:ticket_id>')
class TicketDoc(Resource):
    @tickets_ns.doc('get_ticket', 
                    responses={
                        200: ('Ticket found', ticket_model),
                        404: 'Ticket not found'
                    })
    def get(self, ticket_id):
        """Get specific ticket by ID
        
        Supports both TKT-XXXX format and numeric IDs.
        Returns complete ticket information with agent names.
        """
        return {
            'id': 1,
            'ticket_id': 'TKT-1001',
            'title': 'Email server down',
            'description': 'Users cannot access email since 9 AM',
            'status': 'Open',
            'priority': 'Critical',
            'category': 'Network',
            'created_by': 16,
            'assigned_to': 13,
            'assigned_agent_name': 'Sarah Johnson',
            'created_at': '2024-01-01T10:00:00Z',
            'sla_violated': False
        }
    
    @tickets_ns.expect(ticket_update_model)
    @tickets_ns.doc('update_ticket',
                    responses={
                        200: ('Ticket updated', ticket_model),
                        404: 'Ticket not found'
                    })
    def put(self, ticket_id):
        """Update ticket status, assignment, or priority
        
        Allows agents and supervisors to update ticket properties.
        Creates activity timeline entries.
        """
        return {
            'ticket_id': ticket_id,
            'status': 'Updated',
            'updated_at': '2024-01-01T11:00:00Z'
        }
    
    @tickets_ns.doc('delete_ticket',
                    responses={
                        200: 'Ticket deleted',
                        403: 'Insufficient permissions',
                        404: 'Ticket not found'
                    })
    def delete(self, ticket_id):
        """Delete ticket (System Admin only)
        
        Permanently removes ticket and all associated data.
        """
        return {'success': True, 'message': 'Ticket deleted'}

@users_ns.route('')
class UsersDoc(Resource):
    @users_ns.doc('list_users')
    def get(self):
        """Get all users"""
        return []
    
    @users_ns.expect(user_model)
    @users_ns.doc('create_user')
    def post(self):
        """Create new user"""
        return {}

@users_ns.route('/<int:user_id>')
class UserDoc(Resource):
    @users_ns.doc('get_user')
    def get(self, user_id):
        """Get specific user"""
        return {}
    
    @users_ns.expect(user_model)
    @users_ns.doc('update_user')
    def put(self, user_id):
        """Update user"""
        return {}
    
    @users_ns.doc('delete_user')
    def delete(self, user_id):
        """Delete user"""
        return {'message': 'User deleted'}

# File upload endpoints with Cloudinary integration
@upload_ns.route('/image')
class ImageUploadDoc(Resource):
    @upload_ns.expect(file_upload_model)
    @upload_ns.doc('upload_image',
                   responses={
                       200: ('Upload successful', file_upload_response),
                       400: 'No file provided or invalid format'
                   })
    def post(self):
        """Upload image to Cloudinary with timeline integration
        
        Supports multiple file formats and automatically adds upload
        notification to ticket timeline.
        """
        return {
            'success': True,
            'url': 'https://res.cloudinary.com/dn1dznhej/image/upload/v1234567890/servicedesk/tickets/TKT-1001/attachment_16_TKT-1001.png',
            'public_id': 'servicedesk/tickets/TKT-1001/attachment_16_TKT-1001',
            'width': 1920,
            'height': 1080,
            'file_url': 'https://res.cloudinary.com/dn1dznhej/image/upload/v1234567890/servicedesk/tickets/TKT-1001/attachment_16_TKT-1001.png'
        }

@upload_ns.route('/files/upload')
class FileUploadDoc(Resource):
    @upload_ns.expect(file_upload_model)
    @upload_ns.doc('upload_file',
                   responses={
                       200: ('Upload successful', file_upload_response),
                       400: 'No file provided'
                   })
    def post(self):
        """Upload file to timeline with enhanced field detection
        
        Alternative endpoint for timeline file uploads.
        Automatically detects files in various form field names.
        """
        return {
            'success': True,
            'url': 'https://res.cloudinary.com/dn1dznhej/raw/upload/v1234567890/servicedesk/tickets/TKT-1001/document.pdf',
            'file_url': 'https://res.cloudinary.com/dn1dznhej/raw/upload/v1234567890/servicedesk/tickets/TKT-1001/document.pdf',
            'public_id': 'servicedesk/tickets/TKT-1001/document'
        }

# Analytics endpoints
@analytics_ns.route('/ticket-status-counts')
class TicketStatusCountsDoc(Resource):
    @analytics_ns.doc('ticket_status_counts')
    def get(self):
        """Get real-time ticket status distribution"""
        return {'new': 3, 'open': 17, 'pending': 5, 'closed': 16}

@analytics_ns.route('/sla-violations')
class SLAViolationsDoc(Resource):
    @analytics_ns.doc('sla_violations')
    def get(self):
        """Get current SLA violations"""
        return [{
            'ticket_id': 'TKT-1001',
            'title': 'Critical server issue',
            'priority': 'Critical',
            'hours_overdue': 12.5,
            'assigned_to': 9
        }]

@analytics_ns.route('/ticket-aging')
class TicketAgingDoc(Resource):
    @analytics_ns.doc('ticket_aging')
    def get(self):
        """Get ticket aging analysis with buckets"""
        return {
            'aging_data': [
                {'age_range': '0-24h', 'count': 15},
                {'age_range': '24-48h', 'count': 8},
                {'age_range': '48-72h', 'count': 5},
                {'age_range': '72h+', 'count': 7}
            ],
            'total_open_tickets': 35,
            'average_age_hours': 48.2
        }

@analytics_ns.route('/agent-workload')
class AgentWorkloadDoc(Resource):
    @analytics_ns.doc('agent_workload')
    def get(self):
        """Get agent workload distribution"""
        return [{
            'agent_id': 9,
            'name': 'Sarah Johnson',
            'active_tickets': 12,
            'pending_tickets': 3,
            'closed_tickets': 45
        }]

# Configuration endpoints
@config_ns.route('/priorities')
class PrioritiesDoc(Resource):
    @config_ns.doc('get_priorities')
    def get(self):
        """Get all ticket priorities with SLA targets"""
        return [{
            'id': 1,
            'name': 'Critical',
            'sla_hours': 4,
            'color_code': '#dc2626'
        }]

@config_ns.route('/statuses')
class StatusesDoc(Resource):
    @config_ns.doc('get_statuses')
    def get(self):
        """Get all ticket statuses"""
        return [{
            'id': 1,
            'name': 'New',
            'is_closed_status': False
        }]

@config_ns.route('/categories')
class CategoriesDoc(Resource):
    @config_ns.doc('get_categories')
    def get(self):
        """Get all ticket categories"""
        return [{
            'id': 1,
            'name': 'Hardware',
            'description': 'Hardware related issues'
        }]

@config_ns.route('/initialize')
class ConfigInitDoc(Resource):
    @config_ns.doc('init_config',
                   responses={
                       200: 'Configuration initialized',
                       500: 'Initialization failed'
                   })
    def post(self):
        """Initialize configuration tables with default data
        
        Sets up default priorities, statuses, categories, and roles.
        Safe to run multiple times.
        """
        return {
            'success': True,
            'message': 'Configuration initialized',
            'tables_created': ['priorities', 'statuses', 'categories', 'roles']
        }

# Messages and Timeline
@messages_ns.route('')
class MessagesDoc(Resource):
    @messages_ns.expect(message_create_model)
    @messages_ns.doc('send_message',
                     responses={
                         201: ('Message sent', message_model),
                         400: 'Missing required fields',
                         404: 'Ticket not found'
                     })
    def post(self):
        """Send message to ticket timeline
        
        Adds message to ticket conversation with sender information.
        Supports flexible ticket identification.
        """
        return {
            'id': 123,
            'ticket_id': 'TKT-1001',
            'sender_id': 16,
            'sender_name': 'Demo User',
            'sender_role': 'Normal User',
            'message': 'Issue has been resolved',
            'timestamp': '2024-01-01T12:00:00Z',
            'type': 'message'
        }

@messages_ns.route('/ticket/<string:ticket_id>/timeline')
class TimelineDoc(Resource):
    @messages_ns.doc('get_timeline',
                     responses={
                         200: ('Timeline retrieved', [message_model]),
                         404: 'Ticket not found'
                     })
    def get(self, ticket_id):
        """Get complete ticket timeline with messages and activities"""
        return [{
            'id': 123,
            'ticket_id': 'TKT-1001',
            'sender_name': 'Demo User',
            'sender_role': 'Normal User',
            'message': 'Issue has been resolved',
            'timestamp': '2024-01-01T12:00:00Z',
            'type': 'message'
        }]

# Agent Management
@agents_ns.route('/assignable')
class AssignableAgentsDoc(Resource):
    @agents_ns.doc('get_assignable_agents',
                   responses={
                       200: ('Agents retrieved', [agent_model])
                   })
    def get(self):
        """Get all assignable agents
        
        Returns Technical Users and Technical Supervisors available for assignment.
        """
        return [{
            'id': 13,
            'name': 'Sarah Johnson',
            'email': 'sarah.johnson@company.com',
            'role': 'Technical User'
        }]

# Alert System
@alerts_ns.route('/<int:user_id>')
class UserAlertsDoc(Resource):
    @alerts_ns.doc('get_user_alerts',
                   params={
                       'limit': 'Maximum alerts to return (default: 20)',
                       'unread_only': 'Return only unread alerts (default: false)'
                   },
                   responses={
                       200: ('Alerts retrieved', [alert_model])
                   })
    def get(self, user_id):
        """Get user alerts with filtering options
        
        Returns notifications for assignment, SLA violations, and updates.
        """
        return {
            'alerts': [{
                'id': 1,
                'title': 'New Ticket Assignment',
                'message': 'You have been assigned ticket TKT-1001',
                'alert_type': 'assignment',
                'is_read': False,
                'created_at': '2024-01-01T10:00:00Z',
                'ticket_id': 'TKT-1001'
            }],
            'total': 1,
            'unread_count': 1
        }

@alerts_ns.route('/<int:user_id>/count')
class AlertCountDoc(Resource):
    @alerts_ns.doc('get_alert_count')
    def get(self, user_id):
        """Get unread alert count for notification badge"""
        return {'count': 3}

# Enhanced Analytics
@analytics_ns.route('/agent-workload')
class AgentWorkloadDoc(Resource):
    @analytics_ns.doc('agent_workload',
                      responses={
                          200: ('Workload data', [workload_model])
                      })
    def get(self):
        """Get real-time agent workload distribution
        
        Used for intelligent auto-assignment and supervisor oversight.
        """
        return [{
            'agent_id': 13,
            'name': 'Sarah Johnson',
            'active_tickets': 8,
            'pending_tickets': 2,
            'closed_tickets': 45
        }]

# Additional endpoints available in main API:
# - /api/messages - Message management
# - /api/tickets/{id}/timeline - Ticket timeline
# - /api/files/upload - File upload with timeline integration
# - /api/export/tickets - CSV export
# 
# Live API: https://hotfix.onrender.com/api
# Frontend: https://hotfix-ochre.vercel.app