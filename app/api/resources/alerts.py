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
        try:
            from app.models import Alert, Ticket
            from app import db
            
            alerts_query = db.session.query(
                Alert.id,
                Alert.title,
                Alert.message,
                Alert.alert_type,
                Alert.is_read,
                Alert.created_at,
                Ticket.ticket_id
            ).outerjoin(
                Ticket, Alert.ticket_id == Ticket.id
            ).filter(
                Alert.user_id == user_id
            ).order_by(
                Alert.created_at.desc()
            ).limit(20).all()
            
            alerts = []
            for row in alerts_query:
                alerts.append({
                    'id': row.id,
                    'title': row.title,
                    'message': row.message,
                    'alert_type': row.alert_type,
                    'is_read': row.is_read,
                    'created_at': row.created_at.isoformat() + 'Z' if row.created_at else None,
                    'ticket_id': row.ticket_id
                })
            
            return alerts
        except Exception as e:
            print(f"Error fetching alerts for user {user_id}: {e}")
            return []

class AlertResource(Resource):
    # @jwt_required()  # Disabled for deployment testing
    # Swagger documentation disabled for deployment
    def put(self, alert_id):
        success = NotificationService.mark_alert_read(alert_id)
        return {'success': success}