from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token, create_refresh_token
from app import db
from app.models import User
from app.models.auth import UserAuth
from app.services.email_service import EmailService
# from flasgger import swag_from  # Disabled for deployment
import uuid

class LoginResource(Resource):
    # Swagger documentation disabled for deployment
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        auth = UserAuth.query.filter_by(email=email).first()
        
        if auth and auth.check_password(password):
            user = User.query.get(auth.user_id)
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)
            
            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'role': user.role
                }
            }
        
        return {'message': 'Invalid credentials'}, 401

class RegisterResource(Resource):
    # Swagger documentation disabled for deployment
    def post(self):
        data = request.get_json()
        
        # Check if email already exists
        if UserAuth.query.filter_by(email=data['email']).first():
            return {'message': 'Email already exists'}, 400
        
        # Create user
        user_id = str(uuid.uuid4())
        user = User(
            id=user_id,
            name=data['name'],
            email=data['email'],
            role=data.get('role', 'Normal User')
        )
        
        # Create auth record
        auth = UserAuth(
            id=str(uuid.uuid4()),
            user_id=user_id,
            email=data['email']
        )
        auth.set_password(data['password'])
        
        db.session.add(user)
        db.session.add(auth)
        
        # Send welcome email
        EmailService.send_welcome_email(user.email, user.name)
        
        db.session.commit()
        
        return {'message': 'User registered successfully'}, 201