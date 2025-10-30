from marshmallow import Schema, fields, validate, post_load
from app.models import User, Ticket, Message

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(required=True)
    role = fields.Str(required=True, validate=validate.OneOf([
        'Normal User', 'Technical User', 'Technical Supervisor', 'System Admin'
    ]))
    password = fields.Str(load_only=True, validate=validate.Length(min=6))
    is_verified = fields.Bool(dump_only=True, allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    
    class Meta:
        load_instance = True

class TicketSchema(Schema):
    id = fields.Int(dump_only=True)
    ticket_id = fields.Str(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=5, max=200))
    description = fields.Str(required=True, validate=validate.Length(min=10))
    status = fields.Str()
    priority = fields.Str(required=True, validate=validate.OneOf(['Low', 'Medium', 'High', 'Critical']))
    category = fields.Str(required=True)
    created_by = fields.Int(required=True)
    assigned_to = fields.Int(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    resolved_at = fields.DateTime(allow_none=True)
    sla_violated = fields.Bool(dump_only=True)
    
    # Nested fields
    creator = fields.Nested(UserSchema, only=['id', 'name', 'email'], dump_only=True)
    assignee = fields.Nested(UserSchema, only=['id', 'name', 'email'], dump_only=True)
    
    class Meta:
        load_instance = True

class MessageSchema(Schema):
    id = fields.Int(dump_only=True)
    ticket_id = fields.Int(required=True)
    sender_id = fields.Int(required=True)
    message = fields.Str(required=True, validate=validate.Length(min=1))
    created_at = fields.DateTime(dump_only=True)
    
    # Nested fields
    sender = fields.Nested(UserSchema, only=['id', 'name', 'role'], dump_only=True)
    
    class Meta:
        load_instance = True

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))

# Schema instances
user_schema = UserSchema()
users_schema = UserSchema(many=True)
ticket_schema = TicketSchema()
tickets_schema = TicketSchema(many=True)
message_schema = MessageSchema()
messages_schema = MessageSchema(many=True)
login_schema = LoginSchema()