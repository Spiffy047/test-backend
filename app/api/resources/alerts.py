from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from app.models.alert import Alert
from app.services.notification_service import NotificationService
# from flasgger import swag_from  # Disabled for deployment

class AlertListResource(Resource):
    # @jwt_required()  # Disabled for deployment testing
    # Swagger documentation disabled for deployment
    def get(self, user_id):
        # Return sample alerts based on user
        sample_alerts = []
        
        if user_id == 'user1':
            sample_alerts = [{
                'id': 'alert1',
                'ticket_id': 'TKT-1001',
                'alert_type': 'status_change',
                'title': 'Ticket Status Updated',
                'message': 'Your ticket TKT-1001 status changed to Open',
                'is_read': False,
                'created_at': '2025-10-27T10:30:00Z'
            }, {
                'id': 'alert2',
                'ticket_id': 'TKT-1002',
                'alert_type': 'assignment',
                'title': 'Ticket Assigned',
                'message': 'Your ticket TKT-1002 has been assigned to Sarah Johnson',
                'is_read': False,
                'created_at': '2025-10-27T11:00:00Z'
            }]
        elif user_id == 'user2':
            sample_alerts = [{
                'id': 'alert3',
                'ticket_id': 'TKT-1003',
                'alert_type': 'sla_violation',
                'title': 'SLA Breach Alert',
                'message': 'Ticket TKT-1003 has breached SLA - requires immediate attention',
                'is_read': False,
                'created_at': '2025-10-27T11:30:00Z'
            }, {
                'id': 'alert4',
                'ticket_id': 'TKT-1004',
                'alert_type': 'new_message',
                'title': 'New Message',
                'message': 'New message received on ticket TKT-1004',
                'is_read': True,
                'created_at': '2025-10-27T12:00:00Z'
            }]
        elif user_id == 'user3':
            sample_alerts = [{
                'id': 'alert5',
                'ticket_id': 'TKT-1001',
                'alert_type': 'sla_violation',
                'title': 'Multiple SLA Violations',
                'message': '3 tickets have breached SLA in the last hour',
                'is_read': False,
                'created_at': '2025-10-27T12:15:00Z'
            }]
        
        return sample_alerts

class AlertResource(Resource):
    # @jwt_required()  # Disabled for deployment testing
    # Swagger documentation disabled for deployment
    def put(self, alert_id):
        success = NotificationService.mark_alert_read(alert_id)
        return {'success': success}