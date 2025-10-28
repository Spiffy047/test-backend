from flask import Blueprint, jsonify
from app import db
from app.models.ticket import Ticket
from sqlalchemy import text

fix_bp = Blueprint('fix', __name__)

@fix_bp.route('/fix-ticket-ids', methods=['POST'])
def fix_ticket_ids():
    """Fix ticket IDs to TKT-XXXX format"""
    try:
        # Update ticket IDs
        db.session.execute(text("""
            UPDATE tickets 
            SET id = 'TKT-' || LPAD((ROW_NUMBER() OVER (ORDER BY created_at) + 1000)::text, 4, '0')
            WHERE id NOT LIKE 'TKT-%'
        """))
        
        # Create sequence
        db.session.execute(text("""
            CREATE SEQUENCE IF NOT EXISTS ticket_id_seq 
            START WITH 1002 
            INCREMENT BY 1
        """))
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Ticket IDs fixed successfully"
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500