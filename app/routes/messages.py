from flask import Blueprint, request, jsonify
from app import db
from app.models.ticket import TicketMessage, TicketActivity
from app.schemas.ticket_schema import message_schema, messages_schema, activity_schema, activities_schema
import uuid

messages_bp = Blueprint('messages', __name__)

@messages_bp.route('/ticket/<ticket_id>', methods=['GET'])
def get_ticket_messages(ticket_id):
    """Get all messages for a ticket"""
    messages = TicketMessage.query.filter_by(ticket_id=ticket_id).order_by(TicketMessage.timestamp).all()
    return jsonify(messages_schema.dump(messages))

@messages_bp.route('/ticket/<ticket_id>/timeline', methods=['GET'])
def get_ticket_timeline(ticket_id):
    """Get combined timeline of messages and activities for a ticket"""
    messages = TicketMessage.query.filter_by(ticket_id=ticket_id).all()
    activities = TicketActivity.query.filter_by(ticket_id=ticket_id).all()
    
    timeline = []
    
    # Add messages to timeline
    for message in messages:
        timeline.append({
            'id': message.id,
            'type': 'message',
            'timestamp': message.timestamp.isoformat(),
            'sender_name': message.sender_name,
            'sender_role': message.sender_role,
            'message': message.message,
            'attachments': message.attachments
        })
    
    # Add activities to timeline
    for activity in activities:
        timeline.append({
            'id': activity.id,
            'type': 'activity',
            'timestamp': activity.timestamp.isoformat(),
            'performed_by_name': activity.performed_by_name,
            'description': activity.description,
            'activity_type': activity.activity_type
        })
    
    # Sort by timestamp
    timeline.sort(key=lambda x: x['timestamp'])
    
    return jsonify(timeline)

@messages_bp.route('', methods=['POST'])
def create_message():
    """Create a new message"""
    from app.models.ticket import Ticket
    from app.services.notification_service import NotificationService
    
    data = request.get_json()
    
    message = TicketMessage(
        id=str(uuid.uuid4()),
        ticket_id=data['ticket_id'],
        sender_id=data['sender_id'],
        sender_name=data['sender_name'],
        sender_role=data['sender_role'],
        message=data['message'],
        attachments=data.get('attachments', [])
    )
    
    db.session.add(message)
    
    # Get ticket and send notification
    ticket = Ticket.query.get(data['ticket_id'])
    if ticket:
        NotificationService.notify_new_message(
            ticket, 
            data['message'], 
            data['sender_name'], 
            data['sender_role']
        )
    
    db.session.commit()
    
    return jsonify(message_schema.dump(message)), 201

@messages_bp.route('/<message_id>', methods=['PUT'])
def update_message(message_id):
    """Update a message"""
    message = TicketMessage.query.get_or_404(message_id)
    data = request.get_json()
    
    if 'message' in data:
        message.message = data['message']
    if 'attachments' in data:
        message.attachments = data['attachments']
    
    db.session.commit()
    return jsonify(message_schema.dump(message))

@messages_bp.route('/<message_id>', methods=['DELETE'])
def delete_message(message_id):
    """Delete a message"""
    message = TicketMessage.query.get_or_404(message_id)
    db.session.delete(message)
    db.session.commit()
    
    return '', 204