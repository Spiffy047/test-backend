from flask import Blueprint, jsonify
from app import db
from sqlalchemy import text

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/database-info', methods=['GET'])
def database_info():
    """Get current database tables and structure"""
    try:
        # Get all tables using ORM introspection
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        table_names = inspector.get_table_names()
        
        tables_info = {}
        
        for table_name in sorted(table_names):
            # Get columns for each table using introspection
            columns_info = inspector.get_columns(table_name)
            
            columns = []
            for col_info in columns_info:
                columns.append({
                    'name': col_info['name'],
                    'type': str(col_info['type']),
                    'nullable': col_info['nullable'],
                    'default': str(col_info['default']) if col_info['default'] else None
                })
            
            # Get row count using ORM
            try:
                # Try to get the model class dynamically
                model_class = None
                if table_name == 'users':
                    from app.models import User
                    model_class = User
                elif table_name == 'tickets':
                    from app.models import Ticket
                    model_class = Ticket
                elif table_name == 'messages':
                    from app.models import Message
                    model_class = Message
                elif table_name == 'alerts':
                    from app.models import Alert
                    model_class = Alert
                
                if model_class:
                    row_count = model_class.query.count()
                else:
                    # Fallback for tables without models
                    from sqlalchemy import text
                    count_result = db.session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    row_count = count_result.scalar()
            except:
                row_count = 0
            
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
        # Get all tickets ordered by creation date using ORM
        from app.models import Ticket
        tickets = Ticket.query.order_by(Ticket.created_at).all()
        
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