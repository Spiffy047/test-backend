# Ticket-related schemas for API serialization
from app import ma
from app.models.ticket import Ticket, TicketMessage, TicketActivity
from marshmallow import fields

# Main ticket schema with SLA calculations
class TicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Ticket
        load_instance = True
        include_fk = True  # Include foreign key relationships
    
    # Calculated fields for frontend display
    hours_open = fields.Float(dump_only=True)
    sla_violation_check = fields.Method('check_sla')
    
    def check_sla(self, obj):
        """Calculate SLA violation status"""
        return obj.check_sla_violation()

# Chat message schema
class TicketMessageSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TicketMessage
        load_instance = True
        include_fk = True

# Activity log schema for ticket timeline
class TicketActivitySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TicketActivity
        load_instance = True
        include_fk = True

# Schema instances for API responses
ticket_schema = TicketSchema()
tickets_schema = TicketSchema(many=True)
message_schema = TicketMessageSchema()
messages_schema = TicketMessageSchema(many=True)
activity_schema = TicketActivitySchema()
activities_schema = TicketActivitySchema(many=True)