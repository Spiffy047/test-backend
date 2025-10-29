"""
Database setup endpoint - properly structures and seeds database
"""

from flask import Blueprint, jsonify
from app import db
from app.models import User, Ticket, Message, Alert
from datetime import datetime, timedelta

setup_db_bp = Blueprint('setup_db', __name__)

@setup_db_bp.route('/setup-database', methods=['POST'])
def setup_database():
    """Properly structure database schema and seed with data"""
    try:
        # Drop and recreate all tables with proper schema
        db.drop_all()
        db.create_all()
        
        # Create users with proper ORM
        users_data = [
            ('John Smith', 'john.smith@company.com', 'Normal User'),
            ('Jane Doe', 'jane.doe@company.com', 'Normal User'),
            ('Sarah Johnson', 'sarah.johnson@company.com', 'Technical User'),
            ('Mike Chen', 'mike.chen@company.com', 'Technical User'),
            ('Lisa Rodriguez', 'lisa.rodriguez@company.com', 'Technical Supervisor'),
            ('Admin User', 'admin@company.com', 'System Admin')
        ]
        
        users = []
        for name, email, role in users_data:
            user = User(
                name=name,
                email=email,
                role=role,
                is_verified=True,
                created_at=datetime.utcnow()
            )
            user.set_password('password123')
            db.session.add(user)
            users.append(user)
        
        # Commit users first
        db.session.commit()
        
        # Create tickets
        now = datetime.utcnow()
        tickets_data = [
            {
                'ticket_id': 'TKT-1001',
                'title': 'Server Down - Production Outage',
                'description': 'Main production server is completely down.',
                'priority': 'Critical',
                'category': 'Hardware',
                'status': 'Open',
                'created_by': users[0].id,
                'assigned_to': users[2].id,
                'created_at': now - timedelta(hours=2),
                'sla_violated': False
            },
            {
                'ticket_id': 'TKT-1002',
                'title': 'Database Connection Failure',
                'description': 'Cannot connect to main database.',
                'priority': 'Critical',
                'category': 'Software',
                'status': 'Open',
                'created_by': users[1].id,
                'assigned_to': users[3].id,
                'created_at': now - timedelta(hours=6),
                'sla_violated': True
            },
            {
                'ticket_id': 'TKT-1003',
                'title': 'Password Reset Request',
                'description': 'Forgot password for company portal.',
                'priority': 'Medium',
                'category': 'Access',
                'status': 'Closed',
                'created_by': users[0].id,
                'assigned_to': users[2].id,
                'created_at': now - timedelta(days=3),
                'resolved_at': now - timedelta(days=2)
            },
            {
                'ticket_id': 'TKT-1004',
                'title': 'New Employee Setup',
                'description': 'Complete IT setup for new hire.',
                'priority': 'Medium',
                'category': 'Access',
                'status': 'New',
                'created_by': users[4].id,
                'assigned_to': None,
                'created_at': now - timedelta(hours=4)
            }
        ]
        
        tickets = []
        for ticket_data in tickets_data:
            ticket = Ticket(**ticket_data)
            db.session.add(ticket)
            tickets.append(ticket)
        
        # Commit tickets
        db.session.commit()
        
        # Create messages
        messages_data = [
            {
                'ticket_id': tickets[0].id,
                'sender_id': users[0].id,
                'message': 'Server went down 2 hours ago. Getting 500 errors.',
                'created_at': tickets[0].created_at + timedelta(minutes=5)
            },
            {
                'ticket_id': tickets[0].id,
                'sender_id': users[2].id,
                'message': 'Investigating the issue. Checking server logs.',
                'created_at': tickets[0].created_at + timedelta(minutes=15)
            }
        ]
        
        for message_data in messages_data:
            message = Message(**message_data)
            db.session.add(message)
        
        # Create alerts
        alerts_data = [
            {
                'user_id': users[4].id,
                'ticket_id': tickets[1].id,
                'alert_type': 'sla_violation',
                'title': 'Critical SLA Violation',
                'message': f'Ticket {tickets[1].ticket_id} has violated SLA',
                'is_read': False,
                'created_at': datetime.utcnow()
            }
        ]
        
        for alert_data in alerts_data:
            alert = Alert(**alert_data)
            db.session.add(alert)
        
        # Final commit
        db.session.commit()
        
        # Get counts
        counts = {
            'users': User.query.count(),
            'tickets': Ticket.query.count(),
            'messages': Message.query.count(),
            'alerts': Alert.query.count()
        }
        
        # Role distribution
        role_counts = {}
        for role in ['Normal User', 'Technical User', 'Technical Supervisor', 'System Admin']:
            role_counts[role] = User.query.filter_by(role=role).count()
        
        return jsonify({
            'success': True,
            'message': 'Database properly structured and seeded',
            'schema': 'Recreated with proper SQLAlchemy ORM',
            'data': counts,
            'roles': role_counts,
            'credentials': {
                'admin': 'admin@company.com / password123',
                'user': 'john.smith@company.com / password123',
                'tech': 'sarah.johnson@company.com / password123',
                'supervisor': 'lisa.rodriguez@company.com / password123'
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Database setup failed'
        }), 500