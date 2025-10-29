from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from app import db
from app.models import User
from app.schemas.user_schema import user_schema, users_schema
# from flasgger import swag_from  # Disabled for deployment

class UserListResource(Resource):
    # @jwt_required()  # Disabled for deployment testing
    # Swagger documentation disabled for deployment
    def get(self):
        # Return simple array for frontend compatibility
        users = User.query.all()
        return users_schema.dump(users)

class UserResource(Resource):
    # @jwt_required()  # Disabled for deployment testing
    # Swagger documentation disabled for deployment
    def get(self, user_id):
        user = User.query.get_or_404(user_id)
        return user_schema.dump(user)
    
    # @jwt_required()  # Disabled for deployment testing
    # Swagger documentation disabled for deployment
    def put(self, user_id):
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        for field in ['name', 'email', 'role']:
            if field in data:
                setattr(user, field, data[field])
        
        db.session.commit()
        return user_schema.dump(user)