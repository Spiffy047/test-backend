from flask import Blueprint, jsonify
from app.services.configuration_service import ConfigurationService
from app.models import TicketPriority, TicketStatus, TicketCategory, UserRole

config_bp = Blueprint('config', __name__)

@config_bp.route('/init', methods=['POST'])
def init_config():
    """Initialize configuration tables"""
    try:
        ConfigurationService.initialize_default_configuration()
        return jsonify({'success': True, 'message': 'Configuration initialized'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@config_bp.route('/priorities', methods=['GET'])
def get_priorities():
    """Get all priorities with SLA targets"""
    priorities = TicketPriority.query.filter_by(is_active=True).order_by(TicketPriority.sort_order).all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'sla_hours': p.sla_hours,
        'color_code': p.color_code
    } for p in priorities])

@config_bp.route('/statuses', methods=['GET'])
def get_statuses():
    """Get all ticket statuses"""
    statuses = TicketStatus.query.filter_by(is_active=True).order_by(TicketStatus.sort_order).all()
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'is_closed_status': s.is_closed_status
    } for s in statuses])

@config_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all categories"""
    categories = TicketCategory.query.filter_by(is_active=True).all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'description': c.description
    } for c in categories])

@config_bp.route('/roles', methods=['GET'])
def get_roles():
    """Get all user roles"""
    roles = UserRole.query.filter_by(is_active=True).all()
    return jsonify([{
        'id': r.id,
        'name': r.name,
        'description': r.description,
        'permissions': r.permissions
    } for r in roles])