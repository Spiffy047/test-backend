from flask_restx import Api, Resource, fields, Namespace
from flask import Blueprint

# Create Swagger API blueprint
swagger_bp = Blueprint('swagger', __name__)

# Initialize Flask-RESTX API with Swagger documentation
api = Api(
    swagger_bp,
    version='1.0',
    title='Hotfix ServiceDesk API',
    description='REST API for Hotfix ServiceDesk ticket management system',
    doc='/docs/',
    authorizations={
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'JWT Bearer token. Format: Bearer <token>'
        }
    },
    security='Bearer'
)

# Create namespaces
auth_ns = Namespace('auth', description='Authentication operations')
tickets_ns = Namespace('tickets', description='Ticket management')
users_ns = Namespace('users', description='User management')
files_ns = Namespace('files', description='File operations')
analytics_ns = Namespace('analytics', description='Analytics and reporting')
agents_ns = Namespace('agents', description='Agent management')
messages_ns = Namespace('messages', description='Messaging system')
alerts_ns = Namespace('alerts', description='Alert system')
export_ns = Namespace('export', description='Data export')
admin_ns = Namespace('admin', description='Administration')

api.add_namespace(auth_ns)
api.add_namespace(tickets_ns)
api.add_namespace(users_ns)
api.add_namespace(files_ns)
api.add_namespace(analytics_ns)
api.add_namespace(agents_ns)
api.add_namespace(messages_ns)
api.add_namespace(alerts_ns)
api.add_namespace(export_ns)
api.add_namespace(admin_ns)

# Define API models for documentation
user_model = api.model('User', {
    'id': fields.Integer(description='User ID'),
    'name': fields.String(required=True, description='Full name'),
    'email': fields.String(required=True, description='Email address'),
    'role': fields.String(required=True, description='User role')
})

ticket_model = api.model('Ticket', {
    'id': fields.String(description='Ticket ID'),
    'ticket_id': fields.String(description='Display ticket ID (TKT-XXXX)'),
    'title': fields.String(required=True, description='Ticket title'),
    'description': fields.String(required=True, description='Ticket description'),
    'priority': fields.String(required=True, description='Priority level'),
    'category': fields.String(required=True, description='Ticket category'),
    'status': fields.String(description='Current status'),
    'created_by': fields.Integer(required=True, description='Creator user ID')
})

message_model = api.model('Message', {
    'id': fields.Integer(description='Message ID'),
    'ticket_id': fields.String(required=True, description='Ticket ID'),
    'message': fields.String(required=True, description='Message content'),
    'sender_id': fields.Integer(required=True, description='Sender user ID')
})

login_model = api.model('Login', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

# Add sample endpoints to show in documentation
@auth_ns.route('/login')
class LoginDoc(Resource):
    @auth_ns.expect(login_model)
    @auth_ns.doc('login_user')
    def post(self):
        """User login"""
        return {'access_token': 'jwt_token_here', 'user': {}}

@tickets_ns.route('')
class TicketsDoc(Resource):
    @tickets_ns.doc('list_tickets')
    def get(self):
        """Get all tickets"""
        return []
    
    @tickets_ns.expect(ticket_model)
    @tickets_ns.doc('create_ticket')
    def post(self):
        """Create new ticket"""
        return {}

@tickets_ns.route('/<string:ticket_id>')
class TicketDoc(Resource):
    @tickets_ns.doc('get_ticket')
    def get(self, ticket_id):
        """Get specific ticket"""
        return {}
    
    @tickets_ns.expect(ticket_model)
    @tickets_ns.doc('update_ticket')
    def put(self, ticket_id):
        """Update ticket"""
        return {}
    
    @tickets_ns.doc('delete_ticket')
    def delete(self, ticket_id):
        """Delete ticket"""
        return {'message': 'Ticket deleted'}

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

@files_ns.route('/cloudinary/upload')
class FileUploadDoc(Resource):
    @files_ns.doc('upload_file')
    def post(self):
        """Upload file to Cloudinary"""
        return {'url': 'cloudinary_url', 'public_id': 'file_id'}

@files_ns.route('/upload')
class LocalFileUploadDoc(Resource):
    @files_ns.doc('upload_local_file')
    def post(self):
        """Upload file locally"""
        return {'id': 'file_id', 'filename': 'file.pdf'}

@files_ns.route('/ticket/<string:ticket_id>')
class TicketFilesDoc(Resource):
    @files_ns.doc('get_ticket_files')
    def get(self, ticket_id):
        """Get files for ticket"""
        return []

# Analytics endpoints
@analytics_ns.route('/ticket-status-counts')
class TicketStatusCountsDoc(Resource):
    @analytics_ns.doc('ticket_status_counts')
    def get(self):
        """Get ticket status distribution"""
        return {'new': 0, 'open': 0, 'pending': 0, 'closed': 0}

@analytics_ns.route('/sla-violations')
class SLAViolationsDoc(Resource):
    @analytics_ns.doc('sla_violations')
    def get(self):
        """Get SLA violations"""
        return []

@analytics_ns.route('/ticket-aging')
class TicketAgingDoc(Resource):
    @analytics_ns.doc('ticket_aging')
    def get(self):
        """Get ticket aging analysis"""
        return {'aging_data': [], 'total_open_tickets': 0}

@analytics_ns.route('/unassigned-tickets')
class UnassignedTicketsDoc(Resource):
    @analytics_ns.doc('unassigned_tickets')
    def get(self):
        """Get unassigned tickets"""
        return {'tickets': []}

@analytics_ns.route('/agent-workload')
class AgentWorkloadDoc(Resource):
    @analytics_ns.doc('agent_workload')
    def get(self):
        """Get agent workload distribution"""
        return []

# Agent endpoints
@agents_ns.route('/performance')
class AgentPerformanceDoc(Resource):
    @agents_ns.doc('agent_performance')
    def get(self):
        """Get agent performance metrics"""
        return []

@agents_ns.route('')
class AgentsListDoc(Resource):
    @agents_ns.doc('list_agents')
    def get(self):
        """Get all agents"""
        return []

# Messages endpoints
@messages_ns.route('')
class MessagesDoc(Resource):
    @messages_ns.doc('create_message')
    def post(self):
        """Create new message"""
        return {}

@messages_ns.route('/ticket/<string:ticket_id>/timeline')
class TicketTimelineDoc(Resource):
    @messages_ns.doc('ticket_timeline')
    def get(self, ticket_id):
        """Get ticket message timeline"""
        return []

# Alerts endpoints
@alerts_ns.route('/<string:user_id>')
class UserAlertsDoc(Resource):
    @alerts_ns.doc('user_alerts')
    def get(self, user_id):
        """Get user alerts"""
        return []

@alerts_ns.route('/<string:user_id>/count')
class AlertCountDoc(Resource):
    @alerts_ns.doc('alert_count')
    def get(self, user_id):
        """Get alert count for user"""
        return {'count': 0}

# Export endpoints
@export_ns.route('/tickets/excel')
class ExportTicketsDoc(Resource):
    @export_ns.doc('export_tickets')
    def get(self):
        """Export tickets to CSV"""
        return 'CSV data'

# Admin endpoints
@admin_ns.route('/migrate-ticket-ids')
class MigrateTicketIDsDoc(Resource):
    @admin_ns.doc('migrate_ticket_ids')
    def post(self):
        """Migrate ticket IDs to TKT-XXXX format"""
        return {'migrated': 0}

@admin_ns.route('/fix-ticket-numbering')
class FixTicketNumberingDoc(Resource):
    @admin_ns.doc('fix_ticket_numbering')
    def post(self):
        """Fix ticket numbering"""
        return {'success': True}