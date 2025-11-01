# Ticket Status Management Routes
# Defines clear status workflow and transitions

from flask import Blueprint, jsonify

status_bp = Blueprint('status', __name__)

@status_bp.route('/workflow', methods=['GET'])
def get_status_workflow():
    """Get complete ticket status workflow and allowed transitions"""
    return {
        'statuses': [
            {
                'name': 'New',
                'description': 'Ticket just created, awaiting assignment',
                'color': '#3b82f6',
                'order': 1,
                'is_open': True
            },
            {
                'name': 'Open',
                'description': 'Ticket assigned and being worked on',
                'color': '#10b981',
                'order': 2,
                'is_open': True
            },
            {
                'name': 'Pending',
                'description': 'Waiting for customer response or external dependency',
                'color': '#f59e0b',
                'order': 3,
                'is_open': True
            },
            {
                'name': 'Resolved',
                'description': 'Issue fixed, awaiting customer confirmation',
                'color': '#8b5cf6',
                'order': 4,
                'is_open': False
            },
            {
                'name': 'Closed',
                'description': 'Ticket completed and closed',
                'color': '#6b7280',
                'order': 5,
                'is_open': False
            }
        ],
        'transitions': {
            'New': ['Open', 'Closed'],
            'Open': ['Pending', 'Resolved', 'Closed'],
            'Pending': ['Open', 'Resolved', 'Closed'],
            'Resolved': ['Open', 'Closed'],
            'Closed': ['Open']  # Reopen if needed
        },
        'role_permissions': {
            'Normal User': {
                'can_create': True,
                'can_update': ['New'],  # Only own tickets in New status
                'can_close': False,
                'can_reopen': True
            },
            'Technical User': {
                'can_create': True,
                'can_update': ['New', 'Open', 'Pending', 'Resolved'],
                'can_close': True,
                'can_reopen': True
            },
            'Technical Supervisor': {
                'can_create': True,
                'can_update': ['New', 'Open', 'Pending', 'Resolved', 'Closed'],
                'can_close': True,
                'can_reopen': True
            },
            'System Admin': {
                'can_create': True,
                'can_update': ['New', 'Open', 'Pending', 'Resolved', 'Closed'],
                'can_close': True,
                'can_reopen': True
            }
        }
    }

@status_bp.route('/allowed-transitions/<current_status>', methods=['GET'])
def get_allowed_transitions(current_status):
    """Get allowed status transitions for current status"""
    workflow = get_status_workflow()
    transitions = workflow['transitions'].get(current_status, [])
    
    return {
        'current_status': current_status,
        'allowed_transitions': transitions,
        'statuses': [s for s in workflow['statuses'] if s['name'] in transitions]
    }