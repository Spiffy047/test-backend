from flask_socketio import emit, join_room, leave_room, rooms
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app import socketio, db
from app.models.ticket import TicketMessage
import uuid

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        
        # Join user-specific room for notifications
        join_room(f'user_{user_id}')
        
        # Join technical users room if applicable
        from app.models.user import User
        user = User.query.get(user_id)
        if user and user.role in ['Technical User', 'Technical Supervisor']:
            join_room('technical_users')
        
        emit('connected', {'status': 'Connected', 'user_id': user_id})
    except Exception as e:
        emit('error', {'message': 'Authentication required'})
        return False

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        leave_room(f'user_{user_id}')
        leave_room('technical_users')
        print(f'Client {user_id} disconnected')
    except:
        print('Client disconnected')

@socketio.on('join_ticket')
def handle_join_ticket(data):
    """Join a ticket room for real-time updates"""
    try:
        verify_jwt_in_request()
        ticket_id = data.get('ticket_id')
        if ticket_id:
            join_room(f'ticket_{ticket_id}')
            emit('joined_ticket', {'ticket_id': ticket_id})
    except Exception as e:
        emit('error', {'message': 'Failed to join ticket room'})

@socketio.on('leave_ticket')
def handle_leave_ticket(data):
    """Leave a ticket room"""
    try:
        ticket_id = data.get('ticket_id')
        if ticket_id:
            leave_room(f'ticket_{ticket_id}')
            emit('left_ticket', {'ticket_id': ticket_id})
    except Exception as e:
        emit('error', {'message': 'Failed to leave ticket room'})

@socketio.on('send_message')
def handle_send_message(data):
    """Handle real-time message sending"""
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        
        # Create message in database
        message = TicketMessage(
            id=str(uuid.uuid4()),
            ticket_id=data['ticket_id'],
            sender_id=user_id,
            sender_name=data['sender_name'],
            sender_role=data['sender_role'],
            message=data['message']
        )
        
        db.session.add(message)
        db.session.commit()
        
        # Broadcast to ticket room
        socketio.emit('new_message', {
            'id': message.id,
            'ticket_id': message.ticket_id,
            'sender_name': message.sender_name,
            'sender_role': message.sender_role,
            'message': message.message,
            'timestamp': message.timestamp.isoformat()
        }, room=f'ticket_{data["ticket_id"]}')
        
    except Exception as e:
        emit('error', {'message': 'Failed to send message'})

@socketio.on('typing_start')
def handle_typing_start(data):
    """Handle typing indicator start"""
    try:
        verify_jwt_in_request()
        ticket_id = data.get('ticket_id')
        user_name = data.get('user_name')
        
        socketio.emit('user_typing', {
            'ticket_id': ticket_id,
            'user_name': user_name,
            'typing': True
        }, room=f'ticket_{ticket_id}', include_self=False)
        
    except Exception as e:
        emit('error', {'message': 'Failed to send typing indicator'})

@socketio.on('typing_stop')
def handle_typing_stop(data):
    """Handle typing indicator stop"""
    try:
        verify_jwt_in_request()
        ticket_id = data.get('ticket_id')
        user_name = data.get('user_name')
        
        socketio.emit('user_typing', {
            'ticket_id': ticket_id,
            'user_name': user_name,
            'typing': False
        }, room=f'ticket_{ticket_id}', include_self=False)
        
    except Exception as e:
        emit('error', {'message': 'Failed to stop typing indicator'})

@socketio.on('ticket_update')
def handle_ticket_update(data):
    """Handle ticket status/priority updates"""
    try:
        verify_jwt_in_request()
        ticket_id = data.get('ticket_id')
        
        # Broadcast update to ticket room
        socketio.emit('ticket_updated', {
            'ticket_id': ticket_id,
            'updates': data.get('updates', {}),
            'updated_by': data.get('updated_by')
        }, room=f'ticket_{ticket_id}')
        
    except Exception as e:
        emit('error', {'message': 'Failed to broadcast ticket update'})