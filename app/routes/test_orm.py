"""
Test ORM connectivity with existing database
"""

from flask import Blueprint, jsonify
from app.models import User, Ticket, Message, Alert

test_orm_bp = Blueprint('test_orm', __name__)

@test_orm_bp.route('/test-orm', methods=['GET'])
def test_orm():
    """Test ORM models with existing database"""
    try:
        # Test User model
        users = User.query.limit(5).all()
        user_count = User.query.count()
        
        # Test Ticket model
        tickets = Ticket.query.limit(5).all()
        ticket_count = Ticket.query.count()
        
        # Test admin user specifically
        admin_user = User.query.filter_by(email='admin@company.com').first()
        
        return jsonify({
            'success': True,
            'orm_status': 'working',
            'counts': {
                'users': user_count,
                'tickets': ticket_count
            },
            'sample_users': [
                {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'role': user.role
                } for user in users
            ],
            'admin_user': {
                'found': admin_user is not None,
                'id': admin_user.id if admin_user else None,
                'name': admin_user.name if admin_user else None,
                'email': admin_user.email if admin_user else None,
                'role': admin_user.role if admin_user else None,
                'password_check': admin_user.check_password('password123') if admin_user else False
            } if admin_user else {'found': False}
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'orm_status': 'failed'
        }), 500