# Marshmallow schemas for API serialization/deserialization
from app import ma
from app.models.user import User, Agent
from marshmallow import fields

# User model serialization schema
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True  # Return model instance instead of dict

# Agent model with performance metrics
class AgentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Agent
        load_instance = True
    
    # Performance metrics (output only)
    ticket_count = fields.Integer(dump_only=True)
    closed_tickets = fields.Integer(dump_only=True)
    average_handle_time = fields.Float(dump_only=True)
    sla_violations = fields.Integer(dump_only=True)

# Schema instances for single/multiple records
user_schema = UserSchema()
users_schema = UserSchema(many=True)
agent_schema = AgentSchema()
agents_schema = AgentSchema(many=True)