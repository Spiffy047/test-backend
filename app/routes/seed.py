"""
Database seeding endpoint for remote initialization
"""

from flask import Blueprint, jsonify
from app import db
from app.models import User, Ticket, Message, Alert
from datetime import datetime, timedelta

seed_bp = Blueprint('seed', __name__)

@seed_bp.route('/comprehensive-seed', methods=['POST'])
def comprehensive_seed():
    """Comprehensive database seeding with all system functionalities"""
    try:
        import uuid
        # Import FileAttachment if available, otherwise skip attachments
        try:
            from app.models.attachment import FileAttachment
            has_attachments = True
        except ImportError:
            has_attachments = False
            FileAttachment = None
        
        # Clear existing data
        if has_attachments and FileAttachment:
            FileAttachment.query.delete()
        Alert.query.delete()
        Message.query.delete()
        Ticket.query.delete()
        User.query.delete()
        db.session.commit()
        
        # Create comprehensive user set
        users = [
            User(name='John Smith', email='john.smith@company.com', role='Normal User', is_verified=True),
            User(name='Jane Doe', email='jane.doe@company.com', role='Normal User', is_verified=True),
            User(name='Bob Wilson', email='bob.wilson@company.com', role='Normal User', is_verified=True),
            User(name='Sarah Johnson', email='sarah.johnson@company.com', role='Technical User', is_verified=True),
            User(name='Mike Chen', email='mike.chen@company.com', role='Technical User', is_verified=True),
            User(name='Alex Rivera', email='alex.rivera@company.com', role='Technical User', is_verified=True),
            User(name='Lisa Rodriguez', email='lisa.rodriguez@company.com', role='Technical Supervisor', is_verified=True),
            User(name='David Kim', email='david.kim@company.com', role='Technical Supervisor', is_verified=True),
            User(name='Admin User', email='admin@company.com', role='System Admin', is_verified=True),
            User(name='Super Admin', email='superadmin@company.com', role='System Admin', is_verified=True)
        ]
        
        for user in users:
            user.set_password('password123')
            db.session.add(user)
        
        db.session.flush()
        
        # Create comprehensive ticket dataset
        now = datetime.utcnow()
        tickets = [
            # Critical tickets
            Ticket(ticket_id='TKT-1001', title='Server Down - Production Outage', 
                  description='Main production server is completely down.',
                  priority='Critical', category='Hardware', status='Open', 
                  created_by=users[0].id, assigned_to=users[3].id,
                  created_at=now - timedelta(hours=2), sla_violated=False),
            
            Ticket(ticket_id='TKT-1002', title='Database Connection Failure',
                  description='Cannot connect to main database.',
                  priority='Critical', category='Software', status='Open',
                  created_by=users[1].id, assigned_to=users[4].id,
                  created_at=now - timedelta(hours=6), sla_violated=True),
            
            # High priority tickets
            Ticket(ticket_id='TKT-1003', title='Email System Not Working',
                  description='Company email system down for all users.',
                  priority='High', category='Network', status='Pending',
                  created_by=users[2].id, assigned_to=users[3].id,
                  created_at=now - timedelta(hours=10), sla_violated=True),
            
            # Medium and Low priority tickets
            Ticket(ticket_id='TKT-1004', title='Software Installation Request',
                  description='Need Adobe Creative Suite installed.',
                  priority='Medium', category='Software', status='Open',
                  created_by=users[1].id, assigned_to=users[4].id,
                  created_at=now - timedelta(days=2)),
            
            Ticket(ticket_id='TKT-1005', title='Password Reset Request',
                  description='Forgot password for company portal.',
                  priority='Medium', category='Access', status='Closed',
                  created_by=users[2].id, assigned_to=users[3].id,
                  created_at=now - timedelta(days=3),
                  resolved_at=now - timedelta(days=2)),
            
            # Unassigned tickets
            Ticket(ticket_id='TKT-1006', title='New Employee Setup',
                  description='Complete IT setup for new hire.',
                  priority='Medium', category='Access', status='New',
                  created_by=users[6].id, assigned_to=None,
                  created_at=now - timedelta(hours=4))
        ]
        
        for ticket in tickets:
            db.session.add(ticket)
        
        db.session.flush()
        
        # Create messages and alerts
        messages = [
            Message(ticket_id=tickets[0].id, sender_id=users[0].id,
                   message='Server went down 2 hours ago. Getting 500 errors.',
                   created_at=tickets[0].created_at + timedelta(minutes=5)),
            Message(ticket_id=tickets[0].id, sender_id=users[3].id,
                   message='Investigating the issue. Checking server logs.',
                   created_at=tickets[0].created_at + timedelta(minutes=15))
        ]
        
        alerts = [
            Alert(user_id=users[6].id, ticket_id=tickets[1].id,
                 alert_type='sla_violation', title='Critical SLA Violation',
                 message=f'Ticket {tickets[1].ticket_id} has violated SLA',
                 is_read=False),
            Alert(user_id=users[3].id, ticket_id=tickets[0].id,
                 alert_type='assignment', title='Critical Ticket Assigned',
                 message=f'Assigned critical ticket {tickets[0].ticket_id}',
                 is_read=True)
        ]
        
        # Create file attachments (if model available)
        attachments = []
        if has_attachments and FileAttachment:
            attachments = [
                FileAttachment(
                    id=str(uuid.uuid4()),
                    ticket_id=tickets[0].id,
                    filename='server_error_log.txt',
                    file_size=2048576,
                    mime_type='text/plain',
                    uploaded_by=str(users[0].id)
                )
            ]
        
        for item in messages + alerts + attachments:
            db.session.add(item)
        
        db.session.commit()
        
        # Get final counts
        counts = {
            'users': User.query.count(),
            'tickets': Ticket.query.count(),
            'messages': Message.query.count(),
            'alerts': Alert.query.count(),
            'attachments': FileAttachment.query.count() if has_attachments and FileAttachment else 0
        }
        
        return jsonify({
            'success': True,
            'message': 'Comprehensive database seeding completed',
            'data': counts,
            'credentials': {
                'admin': 'admin@company.com / password123',
                'user': 'john.smith@company.com / password123',
                'tech': 'sarah.johnson@company.com / password123',
                'supervisor': 'lisa.rodriguez@company.com / password123'
            },
            'features': [
                'Role-based authentication (4 roles)',
                'Ticket management (all priorities/statuses)',
                'SLA tracking with violations',
                'Real-time messaging',
                'Alert system',
                'File attachments',
                'Analytics data',
                'Agent workload distribution'
            ]
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500