from flask import Blueprint, jsonify
from app import db
from sqlalchemy import text

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/fix-ticket-numbering', methods=['POST'])
def fix_ticket_numbering():
    """Fix ticket numbering to TKT-XXXX format"""
    try:
        # Get all tickets ordered by creation date using raw SQL
        result = db.session.execute(text("""
            SELECT id, created_at FROM tickets ORDER BY created_at
        """))
        tickets = result.fetchall()
        
        # Update all tickets with proper TKT-XXXX format using SQL
        db.session.execute(text("""
            UPDATE tickets 
            SET id = 'TKT-' || LPAD((ROW_NUMBER() OVER (ORDER BY created_at) + 1000)::text, 4, '0')
            WHERE id NOT LIKE 'TKT-%'
        """))
        
        # Update related tables
        db.session.execute(text("""
            UPDATE ticket_messages 
            SET ticket_id = t.id
            FROM tickets t
            WHERE ticket_messages.ticket_id = t.id
        """))
        
        db.session.execute(text("""
            UPDATE ticket_activities 
            SET ticket_id = t.id
            FROM tickets t
            WHERE ticket_activities.ticket_id = t.id
        """))
        
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