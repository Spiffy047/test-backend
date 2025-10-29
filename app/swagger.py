from flask_restx import Api, Resource, fields
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