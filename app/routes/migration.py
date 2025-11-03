from flask import Blueprint, jsonify
from app import db
from sqlalchemy import text

migration_bp = Blueprint('migration', __name__)

@migration_bp.route('/add-image-url-column', methods=['POST'])
def add_image_url_column():
    """Add image_url column to messages table for file upload support"""
    try:
        # Check if column already exists using introspection
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        columns = inspector.get_columns('messages')
        column_names = [col['name'] for col in columns]
        
        if 'image_url' in column_names:
            return jsonify({
                "success": True,
                "message": "image_url column already exists in messages table",
                "action": "none"
            })
        
        # Add the column using raw SQL (DDL operations require raw SQL)
        from sqlalchemy import text
        db.session.execute(text("""
            ALTER TABLE messages 
            ADD COLUMN image_url VARCHAR(500)
        """))
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Successfully added image_url column to messages table",
            "action": "column_added"
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500