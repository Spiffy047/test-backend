"""
Simple database seeding endpoint - users and tickets only
"""

from flask import Blueprint, jsonify
from app import db
from app.models import User, Ticket
from datetime import datetime, timedelta

simple_seed_bp = Blueprint('simple_seed', __name__)

@simple_seed_bp.route('/simple-seed', methods=['POST'])
def simple_seed():
    """Simple database seeding with users and tickets only"""
    try:
        # Clear existing data
        Ticket.query.delete()
        User.query.delete()
        db.session.commit()
        
        # Create users
        users = [
            User(name='John Smith', email='john.smith@company.com', role='Normal User', is_verified=True),
            User(name='Jane Doe', email='jane.doe@company.com', role='Normal User', is_verified=True),
            User(name='Sarah Johnson', email='sarah.johnson@company.com', role='Technical User', is_verified=True),
            User(name='Mike Chen', email='mike.chen@company.com', role='Technical User', is_verified=True),
            User(name='Lisa Rodriguez', email='lisa.rodriguez@company.com', role='Technical Supervisor', is_verified=True),
            User(name='Admin User', email='admin@company.com', role='System Admin', is_verified=True)
        ]
        
        for user in users:
            user.set_password('password123')
            db.session.add(user)
        
        db.session.flush()  # Get user IDs
        
        # Create tickets
        now = datetime.utcnow()
        tickets = [
            Ticket(
                ticket_id='TKT-1001',
                title='Password Reset Request',
                description='Unable to access email account after recent password policy update.',
                priority='Medium',
                category='Access',
                status='Open',
                created_by=users[0].id,
                assigned_to=users[2].id,
                created_at=now - timedelta(days=5)
            ),
            Ticket(
                ticket_id='TKT-1002',
                title='Software Installation Issue',
                description='Microsoft Office installation failing on Windows 10 workstation.',
                priority='High',
                category='Software',
                status='Open',
                created_by=users[0].id,
                assigned_to=users[2].id,
                created_at=now - timedelta(days=3)
            ),
            Ticket(
                ticket_id='TKT-1003',
                title='Network Connectivity Problem',
                description='Cannot connect to company VPN from home office.',
                priority='High',
                category='Network',
                status='Open',
                created_by=users[1].id,
                assigned_to=users[3].id,
                created_at=now - timedelta(days=2),
                sla_violated=True
            ),
            Ticket(
                ticket_id='TKT-1004',
                title='Printer Not Working',
                description='Office printer showing paper jam error but no paper is jammed.',
                priority='Low',
                category='Hardware',
                status='Closed',
                created_by=users[0].id,
                assigned_to=users[2].id,
                created_at=now - timedelta(days=7),
                resolved_at=now - timedelta(days=1)
            )
        ]
        
        for ticket in tickets:
            db.session.add(ticket)
        
        db.session.commit()
        
        # Get final counts
        user_count = User.query.count()
        ticket_count = Ticket.query.count()
        
        return jsonify({
            'success': True,
            'message': 'Simple database seeding completed successfully',
            'data': {
                'users': user_count,
                'tickets': ticket_count
            },
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
            'error': str(e)
        }), 500