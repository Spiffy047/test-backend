from flask import Blueprint, jsonify
from app import db
from sqlalchemy import text

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/database-info', methods=['GET'])
def database_info():
    try:

        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        table_names = inspector.get_table_names()
        
        tables_info = {}
        
        for table_name in sorted(table_names):

            columns_info = inspector.get_columns(table_name)
            
            columns = []
            for col_info in columns_info:
                columns.append({
                    'name': col_info['name'],
                    'type': str(col_info['type']),
                    'nullable': col_info['nullable'],
                    'default': str(col_info['default']) if col_info['default'] else None
                })
            

            try:

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

                    try:
    
                        from sqlalchemy import MetaData, Table
                        metadata = MetaData()
                        table = Table(table_name, metadata, autoload_with=db.engine)
                        row_count = db.session.query(table).count()
                    except:
                        row_count = 0
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
    try:

        from app.models import Ticket
        tickets = Ticket.query.order_by(Ticket.created_at).all()
        

        ticket_counter = 1001
        for ticket in tickets:

            new_ticket_id = f'TKT-{ticket_counter:04d}'
            

            while Ticket.query.filter_by(ticket_id=new_ticket_id).first():
                ticket_counter += 1
                new_ticket_id = f'TKT-{ticket_counter:04d}'
            

            ticket.ticket_id = new_ticket_id
            ticket_counter += 1
        

        next_number = len(tickets) + 1001
        from sqlalchemy import text
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