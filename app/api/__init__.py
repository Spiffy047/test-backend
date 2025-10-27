from flask import Blueprint
from flask_restful import Api

# Create API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')
api = Api(api_bp)

# Import and register resources
from .resources.tickets import TicketListResource, TicketResource
from .resources.users import UserListResource, UserResource
from .resources.auth import LoginResource, RegisterResource
from .resources.alerts import AlertListResource, AlertResource

# Register API resources
api.add_resource(TicketListResource, '/tickets')
api.add_resource(TicketResource, '/tickets/<string:ticket_id>')
api.add_resource(UserListResource, '/users')
api.add_resource(UserResource, '/users/<string:user_id>')
api.add_resource(LoginResource, '/auth/login')
api.add_resource(RegisterResource, '/auth/register')
api.add_resource(AlertListResource, '/alerts/<string:user_id>')
api.add_resource(AlertResource, '/alerts/<string:alert_id>')