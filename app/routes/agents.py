from flask import Blueprint, request, jsonify
from app import db
from app.models.user import Agent
from app.schemas.user_schema import agent_schema, agents_schema

agents_bp = Blueprint('agents', __name__)

@agents_bp.route('/', methods=['GET'])
def get_agents():
    """Get all agents"""
    active_only = request.args.get('active_only', 'true').lower() == 'true'
    
    query = Agent.query
    if active_only:
        query = query.filter(Agent.is_active == True)
    
    agents = query.order_by(Agent.name).all()
    return jsonify(agents_schema.dump(agents))

@agents_bp.route('/<agent_id>', methods=['GET'])
def get_agent(agent_id):
    """Get a specific agent"""
    agent = Agent.query.get_or_404(agent_id)
    return jsonify(agent_schema.dump(agent))

@agents_bp.route('/', methods=['POST'])
def create_agent():
    """Create a new agent"""
    data = request.get_json()
    
    agent = Agent(
        id=data['id'],
        name=data['name'],
        email=data['email'],
        is_active=data.get('is_active', True)
    )
    
    db.session.add(agent)
    db.session.commit()
    
    return jsonify(agent_schema.dump(agent)), 201

@agents_bp.route('/<agent_id>', methods=['PUT'])
def update_agent(agent_id):
    """Update an agent"""
    agent = Agent.query.get_or_404(agent_id)
    data = request.get_json()
    
    for field in ['name', 'email', 'is_active']:
        if field in data:
            setattr(agent, field, data[field])
    
    db.session.commit()
    return jsonify(agent_schema.dump(agent))

@agents_bp.route('/<agent_id>', methods=['DELETE'])
def delete_agent(agent_id):
    """Delete an agent"""
    agent = Agent.query.get_or_404(agent_id)
    db.session.delete(agent)
    db.session.commit()
    
    return '', 204

@agents_bp.route('/performance', methods=['GET'])
def get_agent_performance():
    """Get agent performance metrics"""
    agents = Agent.query.filter(Agent.is_active == True).all()
    
    performance_data = []
    for agent in agents:
        performance_data.append({
            'id': agent.id,
            'name': agent.name,
            'email': agent.email,
            'active_tickets': agent.ticket_count,
            'closed_tickets': agent.closed_tickets,
            'average_handle_time': round(agent.average_handle_time, 2),
            'sla_violations': agent.sla_violations,
            'performance_score': max(0, (agent.closed_tickets * 10) - (agent.sla_violations * 5))
        })
    
    # Sort by performance score
    performance_data.sort(key=lambda x: x['performance_score'], reverse=True)
    
    return jsonify(performance_data)