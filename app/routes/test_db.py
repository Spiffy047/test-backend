"""
Test database connectivity and data
"""

from flask import Blueprint, jsonify
from app import db
from sqlalchemy import text

test_db_bp = Blueprint('test_db', __name__)

@test_db_bp.route('/test-db', methods=['GET'])
def test_database():
    """Test database connectivity and show data"""
    try:
        # Test users
        users = db.session.execute(text("SELECT id, name, email, role FROM users LIMIT 5")).fetchall()
        
        # Test tickets  
        tickets = db.session.execute(text("SELECT id, ticket_id, title, status, priority FROM tickets LIMIT 5")).fetchall()
        
        # Test counts
        user_count = db.session.execute(text("SELECT COUNT(*) FROM users")).scalar()
        ticket_count = db.session.execute(text("SELECT COUNT(*) FROM tickets")).scalar()
        
        return jsonify({
            'success': True,
            'database': 'connected',
            'counts': {
                'users': user_count,
                'tickets': ticket_count
            },
            'sample_users': [
                {
                    'id': row[0],
                    'name': row[1], 
                    'email': row[2],
                    'role': row[3]
                } for row in users
            ],
            'sample_tickets': [
                {
                    'id': row[0],
                    'ticket_id': row[1],
                    'title': row[2],
                    'status': row[3],
                    'priority': row[4]
                } for row in tickets
            ]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500