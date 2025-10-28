from flask import Blueprint
from flask_restful import Api

api_bp = Blueprint('api', __name__)
api = Api(api_bp)

# Import resources after creating api instance
from app.api.resources import (
    AuthResource,
    TicketListResource,
    TicketResource,
    UserListResource,
    UserResource,
    MessageListResource,
    AnalyticsResource,
    EmailNotificationResource
)

# Register API resources
api.add_resource(AuthResource, '/auth/login')
api.add_resource(TicketListResource, '/tickets')
api.add_resource(TicketResource, '/tickets/<string:ticket_id>')
api.add_resource(UserListResource, '/users')
api.add_resource(UserResource, '/users/<int:user_id>')
api.add_resource(MessageListResource, '/messages')
api.add_resource(AnalyticsResource, '/analytics/<string:endpoint>')
api.add_resource(EmailNotificationResource, '/notifications/email')