from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from app.models.alert import Alert
from app.services.notification_service import NotificationService
# from flasgger import swag_from  # Disabled for deployment

class AlertListResource(Resource):
    @jwt_required()
    # Swagger documentation disabled for deployment
    def get(self, user_id):
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        alerts = NotificationService.get_user_alerts(user_id, unread_only)
        
        return [{
            'id': alert.id,
            'ticket_id': alert.ticket_id,
            'alert_type': alert.alert_type,
            'title': alert.title,
            'message': alert.message,
            'is_read': alert.is_read,
            'created_at': alert.created_at.isoformat()
        } for alert in alerts]

class AlertResource(Resource):
    @jwt_required()
    # Swagger documentation disabled for deployment
    def put(self, alert_id):
        success = NotificationService.mark_alert_read(alert_id)
        return {'success': success}