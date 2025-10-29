# Marshmallow schemas for API serialization/deserialization
from app import ma
from app.models import User
from marshmallow import fields

# User model serialization schema
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True  # Return model instance instead of dict

# Schema instances for single/multiple records
user_schema = UserSchema()
users_schema = UserSchema(many=True)