from flask import Blueprint, request, jsonify
from app import db
from app.models.user import User
from app.schemas.user_schema import user_schema, users_schema

users_bp = Blueprint('users', __name__)

@users_bp.route('/', methods=['GET'])
def get_users():
    """Get all users"""
    role = request.args.get('role')
    
    query = User.query
    if role:
        query = query.filter(User.role == role)
    
    users = query.order_by(User.name).all()
    return jsonify(users_schema.dump(users))

@users_bp.route('/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get a specific user"""
    user = User.query.get_or_404(user_id)
    return jsonify(user_schema.dump(user))

@users_bp.route('/', methods=['POST'])
def create_user():
    """Create a new user"""
    data = request.get_json()
    
    user = User(
        id=data['id'],
        name=data['name'],
        email=data['email'],
        role=data['role']
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user_schema.dump(user)), 201

@users_bp.route('/<user_id>', methods=['PUT'])
def update_user(user_id):
    """Update a user"""
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    for field in ['name', 'email', 'role']:
        if field in data:
            setattr(user, field, data[field])
    
    db.session.commit()
    return jsonify(user_schema.dump(user))

@users_bp.route('/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user"""
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    
    return '', 204