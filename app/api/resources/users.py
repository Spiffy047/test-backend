from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from app import db
from app.models.user import User
from app.schemas.user_schema import user_schema, users_schema
# from flasgger import swag_from  # Disabled for deployment

class UserListResource(Resource):
    # @jwt_required()  # Disabled for deployment testing
    # Swagger documentation disabled for deployment
    def get(self):
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        
        query = User.query
        
        if request.args.get('role'):
            query = query.filter(User.role == request.args.get('role'))
        
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return {
            'users': users_schema.dump(pagination.items),
            'pagination': {
                'page': page,
                'pages': pagination.pages,
                'per_page': per_page,
                'total': pagination.total,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }

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