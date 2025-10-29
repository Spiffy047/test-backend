from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from werkzeug.security import check_password_hash
from sqlalchemy import text
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint using direct SQL"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    try:
        # Find user using direct SQL
        result = db.session.execute(text("""
            SELECT id, name, email, password_hash, role 
            FROM users 
            WHERE email = :email AND is_verified = true
        """), {'email': email})
        
        user_row = result.fetchone()
        
        if not user_row or not check_password_hash(user_row[3], password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Create access token
        access_token = create_access_token(identity=user_row[0])
        
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user_row[0],
                'name': user_row[1],
                'email': user_row[2],
                'role': user_row[4]
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user details"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'role': user.role
    })

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """User logout endpoint"""
    # In a real app, you'd blacklist the token
    return jsonify({'message': 'Logged out successfully'})