from flask_restx import Api, Resource, fields, Namespace
from flask import Blueprint

# Create Swagger API blueprint
swagger_bp = Blueprint('swagger', __name__)

# Initialize Flask-RESTX API with Swagger documentation
api = Api(
    swagger_bp,
    version='1.0',
    title='IT ServiceDesk API',
    description='REST API for IT ServiceDesk ticket management system',
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

api.add_namespace(auth_ns)
api.add_namespace(tickets_ns)
api.add_namespace(users_ns)
api.add_namespace(files_ns)

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

@users_ns.route('')
class UsersDoc(Resource):
    @users_ns.doc('list_users')
    def get(self):
        """Get all users"""
        return []

@files_ns.route('/cloudinary/upload')
class FileUploadDoc(Resource):
    @files_ns.doc('upload_file')
    def post(self):
        """Upload file to Cloudinary"""
        return {'url': 'cloudinary_url', 'public_id': 'file_id'}