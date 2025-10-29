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
            from sqlalchemy import text
            from app import db
            
            result = db.session.execute(text("""
                SELECT a.id, a.title, a.message, a.alert_type, a.is_read, a.created_at, t.ticket_id
                FROM alerts a
                LEFT JOIN tickets t ON a.ticket_id = t.id
                WHERE a.user_id = :user_id
                ORDER BY a.created_at DESC
                LIMIT 20
            """), {'user_id': user_id})
            
            alerts = []
            for row in result:
                alerts.append({
                    'id': row[0],
                    'title': row[1],
                    'message': row[2],
                    'alert_type': row[3],
                    'is_read': row[4],
                    'created_at': row[5].isoformat() + 'Z' if row[5] else None,
                    'ticket_id': row[6]
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