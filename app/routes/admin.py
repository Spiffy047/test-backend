from flask import Blueprint, jsonify
from app import db
from app.models.ticket import Ticket
from sqlalchemy import text

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/fix-ticket-numbering', methods=['POST'])
def fix_ticket_numbering():
    """Fix ticket numbering to TKT-XXXX format"""
    try:
        # Get all tickets ordered by creation date
        tickets = Ticket.query.order_by(Ticket.created_at).all()
        
        # Update each ticket with proper TKT-XXXX format
        for i, ticket in enumerate(tickets, start=1001):
            new_id = f"TKT-{i:04d}"
            
            # Update related tables first
            db.session.execute(text("""
                UPDATE ticket_messages SET ticket_id = :new_id WHERE ticket_id = :old_id
            """), {"new_id": new_id, "old_id": ticket.id})
            
            db.session.execute(text("""
                UPDATE ticket_activities SET ticket_id = :new_id WHERE ticket_id = :old_id
            """), {"new_id": new_id, "old_id": ticket.id})
            
            # Update ticket ID
            ticket.id = new_id
        
        # Create sequence for future tickets
        next_number = len(tickets) + 1001
        db.session.execute(text("DROP SEQUENCE IF EXISTS ticket_id_seq CASCADE"))
        db.session.execute(text(f"CREATE SEQUENCE ticket_id_seq START WITH {next_number} INCREMENT BY 1"))
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Fixed {len(tickets)} tickets. Next ticket will be TKT-{next_number:04d}",
            "tickets_updated": len(tickets)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500