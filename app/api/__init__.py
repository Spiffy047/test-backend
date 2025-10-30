from flask import Blueprint
from flask_restful import Api

api_bp = Blueprint('api', __name__)
api = Api(api_bp)

# Import resources after creating api instance
from app.api.resources import (
    AuthResource,
    AuthMeResource,
    TicketListResource,
    TicketResource,
    UserListResource,
    UserResource,
    MessageListResource,
    AnalyticsResource,
    EmailNotificationResource,
    EmailVerificationResource,
    ImageUploadResource,
    FileUploadResource,
    MigrateTicketIDsResource,
    AssignableAgentsResource,
    AlertResource,
    AlertCountResource,
    TimelineDebugResource
)

# Register API resources
api.add_resource(AuthResource, '/auth/login')
api.add_resource(AuthMeResource, '/auth/me')
api.add_resource(TicketListResource, '/tickets')
api.add_resource(TicketResource, '/tickets/<string:ticket_id>')
api.add_resource(UserListResource, '/users')
api.add_resource(UserResource, '/users/<int:user_id>')
api.add_resource(MessageListResource, '/messages')
api.add_resource(AnalyticsResource, '/analytics/<string:endpoint>')
api.add_resource(EmailNotificationResource, '/notifications/email')
api.add_resource(EmailVerificationResource, '/auth/verify-email')
api.add_resource(ImageUploadResource, '/upload/image')
api.add_resource(FileUploadResource, '/files/upload')
api.add_resource(MigrateTicketIDsResource, '/admin/migrate-ticket-ids')
api.add_resource(AssignableAgentsResource, '/agents/assignable')
api.add_resource(AlertResource, '/alerts/<int:user_id>')
api.add_resource(AlertCountResource, '/alerts/<int:user_id>/count')
api.add_resource(TimelineDebugResource, '/debug/timeline/<string:ticket_id>')