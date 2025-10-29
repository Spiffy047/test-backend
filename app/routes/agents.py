# Agent management routes for IT ServiceDesk
# Manages technical users (agents) who handle ticket assignments and resolution
# Uses User model with role filtering for 'Technical User' and 'Technical Supervisor'

from flask import Blueprint, request, jsonify
from app import db
from app.models import User
from app.schemas.user_schema import user_schema, users_schema

# Blueprint for agent-related endpoints
agents_bp = Blueprint('agents', __name__)

@agents_bp.route('/', methods=['GET'])
def get_agents():
    """Get all agents (Technical Users and Supervisors)
    
    Query parameters:
        active_only (bool): Filter for verified agents only (default: true)
    
    Returns:
        JSON array of agent objects with basic information
    """
    active_only = request.args.get('active_only', 'true').lower() == 'true'
    
    # Query users with technical roles
    query = User.query.filter(User.role.in_(['Technical User', 'Technical Supervisor']))
    if active_only:
        query = query.filter(User.is_verified == True)
    
    agents = query.order_by(User.name).all()
    return jsonify(users_schema.dump(agents))

@agents_bp.route('/<agent_id>', methods=['GET'])
def get_agent(agent_id):
    """Get a specific agent by ID
    
    Args:
        agent_id (str): Unique identifier for the agent
    
    Returns:
        JSON object with agent details
    """
    # Query user with technical role
    agent = User.query.filter(
        User.id == agent_id,
        User.role.in_(['Technical User', 'Technical Supervisor'])
    ).first_or_404()
    return jsonify(user_schema.dump(agent))

@agents_bp.route('/', methods=['POST'])
def create_agent():
    """Create a new agent account
    
    Request body should contain:
        - name: Full name of the agent
        - email: Email address (must be unique)
        - password: Initial password
        - role: Either 'Technical User' or 'Technical Supervisor' (defaults to 'Technical User')
    
    Returns:
        JSON object of created agent with 201 status
    """
    data = request.get_json()
    
    # Create User with technical role
    agent = User(
        name=data['name'],
        email=data['email'],
        role=data.get('role', 'Technical User'),
        is_verified=True  # Agents are pre-verified
    )
    
    if 'password' in data:
        agent.set_password(data['password'])
    
    db.session.add(agent)
    db.session.commit()
    
    return jsonify(user_schema.dump(agent)), 201

@agents_bp.route('/<agent_id>', methods=['PUT'])
def update_agent(agent_id):
    """Update an existing agent's information
    
    Args:
        agent_id (str): Unique identifier for the agent
    
    Request body can contain:
        - name: Updated full name
        - email: Updated email address
        - role: Updated role (Technical User/Technical Supervisor)
        - is_verified: Updated verification status
    
    Returns:
        JSON object of updated agent
    """
    # Query user with technical role
    agent = User.query.filter(
        User.id == agent_id,
        User.role.in_(['Technical User', 'Technical Supervisor'])
    ).first_or_404()
    data = request.get_json()
    
    # Update only provided fields to avoid overwriting unchanged data
    for field in ['name', 'email', 'role', 'is_verified']:
        if field in data:
            setattr(agent, field, data[field])
    
    db.session.commit()
    return jsonify(user_schema.dump(agent))

@agents_bp.route('/<agent_id>', methods=['DELETE'])
def delete_agent(agent_id):
    """Delete an agent account
    
    Args:
        agent_id (str): Unique identifier for the agent to delete
    
    Returns:
        Empty response with 204 status
    
    WARNING: This will permanently delete the agent and may affect
    ticket assignments. Consider setting is_verified=False instead.
    """
    # Query user with technical role
    agent = User.query.filter(
        User.id == agent_id,
        User.role.in_(['Technical User', 'Technical Supervisor'])
    ).first_or_404()
    db.session.delete(agent)
    db.session.commit()
    
    return '', 204

@agents_bp.route('/performance', methods=['GET'])
def get_agent_performance():
    """Get comprehensive performance metrics for all active agents
    
    Calculates and returns performance data including:
    - Active ticket count (assigned and not resolved)
    - Closed ticket count (resolved tickets)
    - Average handle time (calculated from ticket timestamps)
    - SLA violations (tickets that exceeded time limits)
    - Performance score (closed tickets * 10 - violations * 5)
    
    Returns:
        JSON array of agent performance objects sorted by performance score
    
    NOTE: Performance score calculation:
    - +10 points per closed ticket
    - -5 points per SLA violation
    - Minimum score is 0
    """
    from app.models import Ticket
    from sqlalchemy import func
    
    # Query verified users with technical roles
    agents = User.query.filter(
        User.role.in_(['Technical User', 'Technical Supervisor']),
        User.is_verified == True
    ).all()
    
    performance_data = []
    for agent in agents:
        # Count active tickets (assigned but not resolved)
        active_tickets = Ticket.query.filter(
            Ticket.assigned_to == agent.id,
            ~Ticket.status.in_(['Resolved', 'Closed'])
        ).count()
        
        # Count closed tickets
        closed_tickets = Ticket.query.filter(
            Ticket.assigned_to == agent.id,
            Ticket.status.in_(['Resolved', 'Closed'])
        ).count()
        
        # Calculate SLA violations
        sla_violations = Ticket.query.filter(
            Ticket.assigned_to == agent.id,
            Ticket.sla_violated == True
        ).count()
        
        # Calculate average handle time for resolved tickets
        resolved_tickets = Ticket.query.filter(
            Ticket.assigned_to == agent.id,
            Ticket.status.in_(['Resolved', 'Closed']),
            Ticket.resolved_at.isnot(None)
        ).all()
        
        if resolved_tickets:
            total_hours = sum([(t.resolved_at - t.created_at).total_seconds() / 3600 for t in resolved_tickets])
            average_handle_time = total_hours / len(resolved_tickets)
        else:
            average_handle_time = 0.0
        
        # Calculate performance score
        performance_score = max(0, (closed_tickets * 10) - (sla_violations * 5))
        
        performance_data.append({
            'id': agent.id,
            'name': agent.name,
            'email': agent.email,
            'role': agent.role,
            'active_tickets': active_tickets,
            'closed_tickets': closed_tickets,
            'average_handle_time': round(average_handle_time, 2),
            'sla_violations': sla_violations,
            'performance_score': performance_score
        })
    
    # Sort agents by performance score (highest first)
    performance_data.sort(key=lambda x: x['performance_score'], reverse=True)
    
    return jsonify(performance_data)