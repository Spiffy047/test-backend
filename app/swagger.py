from flask_restx import Api, Resource, fields, Namespace
from flask import Blueprint

# Create Swagger API blueprint
swagger_bp = Blueprint('swagger', __name__)

# Initialize Flask-RESTX API with Swagger documentation
api = Api(
    swagger_bp,
    version='2.0',
    title='Hotfix ServiceDesk API',
    description='Complete REST API for Hotfix ServiceDesk with authentication, tickets, messaging, file uploads, and analytics. Live deployment at https://hotfix.onrender.com',
    doc='/docs/',
    authorizations={
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'JWT Bearer token (currently disabled for deployment)'
        }
    }
)

# Create namespaces for current working endpoints
auth_ns = Namespace('auth', description='Authentication operations')
tickets_ns = Namespace('tickets', description='Ticket management with SLA tracking')
users_ns = Namespace('users', description='User management with role-based access')
upload_ns = Namespace('upload', description='File and image uploads via Cloudinary')
analytics_ns = Namespace('analytics', description='Real-time analytics and reporting')
config_ns = Namespace('config', description='Dynamic system configuration')

api.add_namespace(auth_ns)
api.add_namespace(tickets_ns)
api.add_namespace(users_ns)
api.add_namespace(upload_ns)
api.add_namespace(analytics_ns)
api.add_namespace(config_ns)

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
    'category': fields.String(required=True, description='Ticket category', enum=['Hardware', 'Software', 'Network', 'Access', 'Email', 'Security']),
    'created_by': fields.Integer(required=True, description='Creator user ID', example=1),
    'attachment': fields.Raw(description='Optional file attachment (multipart form data)')
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
    'created_at': fields.DateTime(description='Creation timestamp'),
    'updated_at': fields.DateTime(description='Last update timestamp'),
    'sla_violated': fields.Boolean(description='SLA violation status')
})

message_model = api.model('Message', {
    'ticket_id': fields.String(required=True, description='Ticket ID', example='TKT-1001'),
    'sender_id': fields.Integer(required=True, description='Sender user ID', example=1),
    'message': fields.String(required=True, description='Message content', example='Issue has been resolved')
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
        """Authenticate user (JWT disabled for deployment)"""
        return {
            'success': True,
            'user': {
                'id': 1,
                'name': 'John Smith',
                'email': 'john.smith@company.com',
                'role': 'Normal User'
            },
            'message': 'Login successful'
        }

@tickets_ns.route('')
class TicketsDoc(Resource):
    @tickets_ns.doc('list_tickets', params={
        'page': 'Page number (default: 1)',
        'per_page': 'Items per page (default: 10)',
        'created_by': 'Filter by creator user ID',
        'status': 'Filter by status'
    })
    def get(self):
        """Get paginated list of tickets with optional filters"""
        return {
            'tickets': [],
            'pagination': {
                'page': 1,
                'per_page': 10,
                'total': 0,
                'pages': 0,
                'has_next': False,
                'has_prev': False
            }
        }
    
    @tickets_ns.expect(ticket_create_model)
    @tickets_ns.doc('create_ticket', responses={
        201: 'Ticket created successfully',
        400: 'Validation error'
    })
    def post(self):
        """Create new support ticket (supports both JSON and multipart form data with attachments)"""
        return {
            'ticket_id': 'TKT-1001',
            'title': 'Email server down',
            'status': 'New',
            'priority': 'Critical',
            'attachment_uploaded': True
        }

@tickets_ns.route('/<string:ticket_id>')
class TicketDoc(Resource):
    @tickets_ns.doc('get_ticket', responses={
        200: 'Ticket found',
        404: 'Ticket not found'
    })
    def get(self, ticket_id):
        """Get specific ticket by ID (TKT-XXXX or numeric ID)"""
        return {
            'ticket_id': 'TKT-1001',
            'title': 'Email server down',
            'status': 'Open',
            'priority': 'Critical',
            'assigned_to': 9
        }
    
    @tickets_ns.expect(api.model('TicketUpdate', {
        'status': fields.String(description='New status'),
        'assigned_to': fields.Integer(description='Assign to user ID'),
        'priority': fields.String(description='Update priority')
    }))
    @tickets_ns.doc('update_ticket')
    def put(self, ticket_id):
        """Update ticket status, assignment, or priority"""
        return {'ticket_id': ticket_id, 'status': 'Updated'}
    
    @tickets_ns.doc('delete_ticket')
    def delete(self, ticket_id):
        """Delete ticket (admin only)"""
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

# File upload endpoints
@upload_ns.route('/image')
class ImageUploadDoc(Resource):
    @upload_ns.doc('upload_image', params={
        'image': 'Image file to upload',
        'ticket_id': 'Ticket ID',
        'user_id': 'User ID'
    })
    def post(self):
        """Upload image to Cloudinary"""
        return {
            'success': True,
            'url': 'https://res.cloudinary.com/dn1dznhej/image/upload/v1234567890/servicedesk/tickets/TKT-1001/attachment_1_TKT-1001.png',
            'public_id': 'servicedesk/tickets/TKT-1001/attachment_1_TKT-1001',
            'width': 1920,
            'height': 1080
        }

@upload_ns.route('/file', methods=['POST'])
class FileUploadDoc(Resource):
    @upload_ns.doc('upload_file', params={
        'file': 'File to upload',
        'ticket_id': 'Ticket ID',
        'uploaded_by': 'User ID'
    })
    def post(self):
        """Upload file and add to timeline"""
        return {
            'id': 'file_123',
            'filename': 'document.pdf',
            'file_size_mb': 2.5,
            'uploaded_at': '2025-10-29T17:56:54.399628Z'
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

@config_ns.route('/init')
class ConfigInitDoc(Resource):
    @config_ns.doc('init_config')
    def post(self):
        """Initialize configuration tables with default data"""
        return {'success': True, 'message': 'Configuration initialized'}

# Note: Additional endpoints are available in the main API:
# - /api/messages - Message management (built into Flask-RESTful resources)
# - /api/tickets/{id}/timeline - Ticket timeline with messages and activities  
# - /api/files/upload - File upload with timeline integration
# - /api/export/tickets - CSV export functionality
# - /api/db/create-tables - Database table creation
# 
# Live API Base URL: https://hotfix.onrender.com/api/
# Frontend: https://hotfix-ochre.vercel.app
# 
# System Status:
# - Database: PostgreSQL (Live with existing data)
# - File Storage: Cloudinary
# - Authentication: Simplified (JWT disabled for deployment)
# - Real-time Features: Polling-based updates