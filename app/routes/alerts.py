from flask import Blueprint, request, jsonify
from app.models.alert import Alert
from app.services.notification_service import NotificationService

alerts_bp = Blueprint('alerts', __name__)

@alerts_bp.route('/<user_id>', methods=['GET'])
def get_user_alerts(user_id):
    """Get alerts for a specific user"""
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    alerts = NotificationService.get_user_alerts(user_id, unread_only)
    
    return jsonify([{
        'id': alert.id,
        'ticket_id': alert.ticket_id,
        'alert_type': alert.alert_type,
        'title': alert.title,
        'message': alert.message,
        'is_read': alert.is_read,
        'created_at': alert.created_at.isoformat()
    } for alert in alerts])

@alerts_bp.route('/<alert_id>/read', methods=['PUT'])
def mark_alert_read(alert_id):
    """Mark an alert as read"""
    success = NotificationService.mark_alert_read(alert_id)
    return jsonify({'success': success})

@alerts_bp.route('/<user_id>/read-all', methods=['PUT'])
def mark_all_alerts_read(user_id):
    """Mark all alerts as read for a user"""
    success = NotificationService.mark_all_alerts_read(user_id)
    return jsonify({'success': success})

@alerts_bp.route('/<user_id>/count', methods=['GET'])
def get_unread_count(user_id):
    """Get count of unread alerts for a user"""
    alerts = NotificationService.get_user_alerts(user_id, unread_only=True)
    return jsonify({'count': len(alerts)})