from flask import Blueprint, request, jsonify
from app import db
from app.models import Message
from app.schemas.ticket_schema import ticket_schema, tickets_schema
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
    from app.models import Ticket
    from sqlalchemy import text
    
    data = request.get_json()
    
    if not data or not data.get('ticket_id') or not data.get('message'):
        return {'error': 'Missing required fields'}, 400
    
    try:
        # Get ticket internal ID
        if data['ticket_id'].startswith('TKT-'):
            ticket_result = db.session.execute(text("""
                SELECT id FROM tickets WHERE ticket_id = :ticket_id
            """), {'ticket_id': data['ticket_id']})
        else:
            ticket_result = db.session.execute(text("""
                SELECT id FROM tickets WHERE id = :id
            """), {'id': data['ticket_id']})
        
        ticket_row = ticket_result.fetchone()
        if not ticket_row:
            return {'error': 'Ticket not found'}, 404
        
        internal_ticket_id = ticket_row[0]
        
        sender_id = data.get('sender_id')
        if not sender_id:
            return {'error': 'sender_id field is required'}, 400
        
        message = Message(
            ticket_id=internal_ticket_id,
            sender_id=sender_id,
            message=data['message']
        )
        
        db.session.add(message)
        db.session.commit()
        
        return {
            'id': message.id,
            'message': message.message,
            'created_at': message.created_at.isoformat() if message.created_at else None
        }, 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating message: {e}")
        return {'error': 'Failed to create message'}, 500

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