"""
Configuration management routes
Provides endpoints for managing system configuration
"""

from flask import Blueprint, request, jsonify
from app import db
from app.services.configuration_service import ConfigurationService
from app.models.configuration import (
    UserRole, TicketStatus, TicketPriority, 
    TicketCategory, AlertType, SystemSetting
)

config_bp = Blueprint('configuration', __name__)

@config_bp.route('/initialize', methods=['POST'])
def initialize_configuration():
    """Initialize default configuration data"""
    try:
        ConfigurationService.initialize_default_configuration()
        return jsonify({
            'success': True,
            'message': 'Configuration initialized successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@config_bp.route('/roles', methods=['GET'])
def get_user_roles():
    """Get all user roles"""
    roles = ConfigurationService.get_user_roles()
    return jsonify([{
        'id': role.id,
        'name': role.name,
        'description': role.description,
        'permissions': role.permissions,
        'is_active': role.is_active
    } for role in roles])

@config_bp.route('/statuses', methods=['GET'])
def get_ticket_statuses():
    """Get all ticket statuses"""
    statuses = ConfigurationService.get_ticket_statuses()
    return jsonify([{
        'id': status.id,
        'name': status.name,
        'description': status.description,
        'is_closed_status': status.is_closed_status,
        'sort_order': status.sort_order,
        'is_active': status.is_active
    } for status in statuses])

@config_bp.route('/priorities', methods=['GET'])
def get_ticket_priorities():
    """Get all ticket priorities"""
    priorities = ConfigurationService.get_ticket_priorities()
    return jsonify([{
        'id': priority.id,
        'name': priority.name,
        'description': priority.description,
        'sla_hours': priority.sla_hours,
        'escalation_hours': priority.escalation_hours,
        'color_code': priority.color_code,
        'sort_order': priority.sort_order,
        'is_active': priority.is_active
    } for priority in priorities])

@config_bp.route('/categories', methods=['GET'])
def get_ticket_categories():
    """Get all ticket categories"""
    categories = ConfigurationService.get_ticket_categories()
    return jsonify([{
        'id': category.id,
        'name': category.name,
        'description': category.description,
        'default_priority_id': category.default_priority_id,
        'is_active': category.is_active
    } for category in categories])

@config_bp.route('/alert-types', methods=['GET'])
def get_alert_types():
    """Get all alert types"""
    alert_types = ConfigurationService.get_alert_types()
    return jsonify([{
        'id': alert_type.id,
        'name': alert_type.name,
        'description': alert_type.description,
        'template': alert_type.template,
        'is_active': alert_type.is_active
    } for alert_type in alert_types])

@config_bp.route('/settings', methods=['GET'])
def get_system_settings():
    """Get all system settings"""
    settings = SystemSetting.query.all()
    return jsonify([{
        'id': setting.id,
        'key': setting.key,
        'value': setting.get_typed_value(),
        'data_type': setting.data_type,
        'description': setting.description,
        'is_editable': setting.is_editable
    } for setting in settings])

@config_bp.route('/settings/<key>', methods=['PUT'])
def update_system_setting(key):
    """Update a system setting"""
    data = request.get_json()
    
    try:
        setting = ConfigurationService.set_system_setting(
            key=key,
            value=data['value'],
            data_type=data.get('data_type', 'string'),
            description=data.get('description')
        )
        
        return jsonify({
            'success': True,
            'setting': {
                'key': setting.key,
                'value': setting.get_typed_value(),
                'data_type': setting.data_type,
                'description': setting.description
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500