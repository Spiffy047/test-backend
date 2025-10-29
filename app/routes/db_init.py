from flask import Blueprint, jsonify
from app import db

db_init_bp = Blueprint('db_init', __name__)

@db_init_bp.route('/create-tables', methods=['POST'])
def create_tables():
    """Create all database tables using SQLAlchemy ORM"""
    try:
        db.create_all()
        return jsonify({
            'success': True,
            'message': 'All tables created successfully using ORM'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500