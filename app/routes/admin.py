from flask import Blueprint, jsonify
from app import db
from sqlalchemy import text

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/database-info', methods=['GET'])
def database_info():
    """Get current database tables and structure"""
    try:
        # Get all tables
        tables_result = db.session.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """))
        
        tables_info = {}
        
        for table_row in tables_result:
            table_name = table_row[0]
            
            # Get columns for each table
            columns_result = db.session.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = :table_name
                ORDER BY ordinal_position
            """), {'table_name': table_name})
            
            columns = []
            for col_row in columns_result:
                columns.append({
                    'name': col_row[0],
                    'type': col_row[1],
                    'nullable': col_row[2] == 'YES',
                    'default': col_row[3]
                })
            
            # Get row count
            count_result = db.session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            row_count = count_result.scalar()
            
            tables_info[table_name] = {
                'columns': columns,
                'row_count': row_count
            }
        
        return jsonify({
            "success": True,
            "tables": tables_info,
            "total_tables": len(tables_info)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

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