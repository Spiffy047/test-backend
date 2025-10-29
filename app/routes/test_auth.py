"""
Test authentication specifically
"""

from flask import Blueprint, jsonify, request
from app import db
from sqlalchemy import text
from werkzeug.security import check_password_hash

test_auth_bp = Blueprint('test_auth', __name__)

@test_auth_bp.route('/test-auth', methods=['POST'])
def test_auth():
    """Test authentication step by step"""
    try:
        data = request.get_json()
        email = data.get('email', 'admin@company.com')
        password = data.get('password', 'password123')
        
        # Step 1: Check if user exists
        result = db.session.execute(text("""
            SELECT id, name, email, password_hash, role, is_verified
            FROM users 
            WHERE email = :email
        """), {'email': email})
        
        user_row = result.fetchone()
        
        if not user_row:
            return jsonify({
                'success': False,
                'step': 'user_lookup',
                'message': f'User {email} not found in database',
                'all_users': [row[0] for row in db.session.execute(text("SELECT email FROM users")).fetchall()]
            })
        
        # Step 2: Check password
        password_valid = check_password_hash(user_row[3], password)
        
        return jsonify({
            'success': True,
            'step': 'complete',
            'user_found': True,
            'password_valid': password_valid,
            'user_data': {
                'id': user_row[0],
                'name': user_row[1],
                'email': user_row[2],
                'role': user_row[4],
                'is_verified': user_row[5]
            },
            'password_hash_sample': user_row[3][:20] + '...'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500