# Ticket-related schemas for API serialization
from app import ma
from app.models import Ticket
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

# Schema instances for API responses
ticket_schema = TicketSchema()
tickets_schema = TicketSchema(many=True)