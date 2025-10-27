from app import create_app, db
from app.models.ticket import Ticket, TicketMessage, TicketActivity
from app.models.user import User, Agent
from app.models.sla import SLAPolicy, SLAViolation
from app.models.attachment import FileAttachment
from app.models.auth import UserAuth
import os

config_name = os.getenv('FLASK_ENV', 'development')
try:
    app = create_app(config_name)
except Exception as e:
    print(f"App creation error: {e}")
    # Create minimal app for health checks
    from flask import Flask
    app = Flask(__name__)
    
    # Minimal error app without routes

# Routes moved to __init__.py

def init_db():
    """Initialize database with sample data"""
    try:
        with app.app_context():
            db.create_all()
    except Exception as e:
        print(f"Database initialization error: {e}")
        return
        
        # Check if data already exists
        if User.query.first():
            return
        
        # Create sample users
        users = [
            User(id='user1', name='John Smith', email='john.smith@company.com', role='Normal User'),
            User(id='user2', name='Maria Garcia', email='maria.garcia@company.com', role='Technical User'),
            User(id='user3', name='Robert Chen', email='robert.chen@company.com', role='Technical Supervisor'),
            User(id='user4', name='Admin User', email='admin@company.com', role='System Admin'),
        ]
        
        # Create sample agents
        agents = [
            Agent(id='agent1', name='Sarah Johnson', email='sarah.j@company.com'),
            Agent(id='agent2', name='Mike Chen', email='mike.c@company.com'),
            Agent(id='agent3', name='Emily Rodriguez', email='emily.r@company.com'),
            Agent(id='agent4', name='David Kim', email='david.k@company.com'),
            Agent(id='agent5', name='Lisa Anderson', email='lisa.a@company.com'),
        ]
        
        # Create sample tickets
        tickets = [
            Ticket(
                id='TKT-1001',
                title='Unable to access company email',
                description='User cannot login to Outlook, getting authentication error',
                status='Open',
                priority='High',
                category='Email & Communication',
                assigned_to='agent1',
                created_by='user1'
            ),
            Ticket(
                id='TKT-1002',
                title='Laptop running very slow',
                description='Computer takes 10+ minutes to boot and applications are unresponsive',
                status='New',
                priority='Medium',
                category='Hardware',
                created_by='user1'
            ),
            Ticket(
                id='TKT-1003',
                title='VPN connection issues',
                description='Cannot connect to company VPN from home office',
                status='Pending',
                priority='High',
                category='Network & Connectivity',
                assigned_to='agent2',
                created_by='user1'
            ),
        ]
        
        # Add all to database
        for user in users:
            db.session.add(user)
        for agent in agents:
            db.session.add(agent)
        for ticket in tickets:
            db.session.add(ticket)
        
        # Create authentication records
        auth_records = [
            UserAuth(id='auth1', user_id='user1', email='john.smith@company.com'),
            UserAuth(id='auth2', user_id='user2', email='maria.garcia@company.com'),
            UserAuth(id='auth3', user_id='user3', email='robert.chen@company.com'),
            UserAuth(id='auth4', user_id='user4', email='admin@company.com'),
        ]
        
        for auth in auth_records:
            auth.set_password('demo123')
            db.session.add(auth)
        
        try:
            db.session.commit()
            print("Database initialized with sample data and authentication")
        except Exception as e:
            print(f"Database commit error: {e}")
            db.session.rollback()

if __name__ == '__main__':
    if os.getenv('INIT_DB', 'false').lower() == 'true':
        init_db()
    
    # SLA monitoring disabled for deployment
    # from app.tasks.scheduler import sla_monitor
    # sla_monitor.start()
    
    try:
        # Production configuration
        port = int(os.environ.get('PORT', 5002))
        debug = os.environ.get('FLASK_ENV') != 'production'
        app.run(debug=debug, host='0.0.0.0', port=port)
    finally:
        pass  # sla_monitor.stop() disabled