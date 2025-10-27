#!/usr/bin/env python3
import os
os.environ['FLASK_ENV'] = 'development'

from app import create_app, db
from app.models.user import User, Agent
from app.models.auth import UserAuth
from app.models.ticket import Ticket

app = create_app('development')

with app.app_context():
    # Drop all tables
    db.drop_all()
    print("✓ Dropped all tables")
    
    # Create all tables
    db.create_all()
    print("✓ Created all tables")
    
    # Create users
    users = [
        User(id='user1', name='John Smith', email='john.smith@company.com', role='Normal User'),
        User(id='user2', name='Maria Garcia', email='maria.garcia@company.com', role='Technical User'),
        User(id='user3', name='Robert Chen', email='robert.chen@company.com', role='Technical Supervisor'),
        User(id='user4', name='Admin User', email='admin@company.com', role='System Admin'),
        User(id='user5', name='Alice Johnson', email='alice.johnson@company.com', role='Normal User'),
        User(id='user6', name='Bob Williams', email='bob.williams@company.com', role='Normal User'),
        User(id='user7', name='Carol Davis', email='carol.davis@company.com', role='Normal User'),
        User(id='user8', name='David Brown', email='david.brown@company.com', role='Technical User'),
        User(id='user9', name='Emma Wilson', email='emma.wilson@company.com', role='Technical User'),
        User(id='user10', name='Frank Miller', email='frank.miller@company.com', role='Technical Supervisor'),
    ]
    
    for user in users:
        db.session.add(user)
    db.session.commit()
    print("✓ Created 10 users")
    
    # Create agents - Technical Users from LOGIN_USERS.md
    agents = [
        Agent(id='user2', name='Maria Garcia', email='maria.garcia@company.com'),
        Agent(id='user8', name='David Brown', email='david.brown@company.com'),
        Agent(id='user9', name='Emma Wilson', email='emma.wilson@company.com'),
    ]
    
    for agent in agents:
        db.session.add(agent)
    db.session.commit()
    print("✓ Created 3 agents (Technical Users)")
    
    # Create auth records
    auth_records = [
        UserAuth(id='auth1', user_id='user1', email='john.smith@company.com'),
        UserAuth(id='auth2', user_id='user2', email='maria.garcia@company.com'),
        UserAuth(id='auth3', user_id='user3', email='robert.chen@company.com'),
        UserAuth(id='auth4', user_id='user4', email='admin@company.com'),
        UserAuth(id='auth5', user_id='user5', email='alice.johnson@company.com'),
        UserAuth(id='auth6', user_id='user6', email='bob.williams@company.com'),
        UserAuth(id='auth7', user_id='user7', email='carol.davis@company.com'),
        UserAuth(id='auth8', user_id='user8', email='david.brown@company.com'),
        UserAuth(id='auth9', user_id='user9', email='emma.wilson@company.com'),
        UserAuth(id='auth10', user_id='user10', email='frank.miller@company.com'),
    ]
    
    for auth in auth_records:
        auth.set_password('demo123')
        db.session.add(auth)
    db.session.commit()
    print("✓ Created 10 auth records (password: demo123)")
    
    # Create sample tickets aligned with LOGIN_USERS.md
    tickets = [
        Ticket(
            id='TKT-1001',
            title='Unable to access company email',
            description='User cannot login to Outlook',
            status='Open',
            priority='High',
            category='Email & Communication',
            assigned_to='user2',
            created_by='user1'
        ),
        Ticket(
            id='TKT-1002',
            title='Laptop running very slow',
            description='Computer takes 10+ minutes to boot',
            status='New',
            priority='Medium',
            category='Hardware',
            created_by='user1'
        ),
        Ticket(
            id='TKT-1003',
            title='VPN connection issues',
            description='Cannot connect to company VPN from home',
            status='Pending',
            priority='High',
            category='Network & Connectivity',
            assigned_to='user2',
            created_by='user1',
            sla_violated=1
        ),
        Ticket(
            id='TKT-1004',
            title='Software installation request',
            description='Need Adobe Photoshop installed on workstation',
            status='Closed',
            priority='Low',
            category='Software',
            assigned_to='user9',
            created_by='user1'
        ),
        Ticket(
            id='TKT-1005',
            title='Critical server outage - Production down',
            description='Main production server is not responding. All services affected.',
            status='Open',
            priority='Critical',
            category='Infrastructure',
            assigned_to='user8',
            created_by='user5'
        ),
        Ticket(
            id='TKT-1006',
            title='Security breach detected',
            description='Unusual login attempts detected from unknown IP addresses',
            status='Open',
            priority='Critical',
            category='Security',
            assigned_to='user2',
            created_by='user6',
            sla_violated=1
        ),
        Ticket(
            id='TKT-1007',
            title='Database backup failure',
            description='Automated backup failed for 3 consecutive days',
            status='Pending',
            priority='High',
            category='Database',
            assigned_to='user8',
            created_by='user7',
            sla_violated=1
        ),
        Ticket(
            id='TKT-1008',
            title='Network connectivity issues',
            description='Intermittent network drops affecting multiple users',
            status='Open',
            priority='High',
            category='Network & Connectivity',
            assigned_to='user8',
            created_by='user5'
        ),
        Ticket(
            id='TKT-1009',
            title='Software license expired',
            description='Adobe Creative Suite license needs renewal',
            status='New',
            priority='Low',
            category='Software',
            created_by='user6'
        ),
        Ticket(
            id='TKT-1010',
            title='Printer not working',
            description='Office printer shows error code E-52',
            status='Open',
            priority='Medium',
            category='Hardware',
            assigned_to='user9',
            created_by='user1'
        ),
        Ticket(
            id='TKT-1011',
            title='Password reset request',
            description='User forgot password and needs reset',
            status='Closed',
            priority='Low',
            category='Access',
            assigned_to='user2',
            created_by='user5'
        ),
        Ticket(
            id='TKT-1012',
            title='Application crash on startup',
            description='CRM application crashes immediately after launch',
            status='Open',
            priority='High',
            category='Software',
            assigned_to='user8',
            created_by='user6',
            sla_violated=1
        ),
        Ticket(
            id='TKT-1013',
            title='New employee onboarding',
            description='Setup workstation and accounts for new hire',
            status='Pending',
            priority='Medium',
            category='Access',
            assigned_to='user9',
            created_by='user3'
        ),
        Ticket(
            id='TKT-1014',
            title='Slow internet connection',
            description='Download speeds significantly reduced',
            status='Open',
            priority='Medium',
            category='Network & Connectivity',
            assigned_to='user2',
            created_by='user7'
        ),
        Ticket(
            id='TKT-1015',
            title='Data recovery needed',
            description='Accidentally deleted important files from shared drive',
            status='Closed',
            priority='High',
            category='Database',
            assigned_to='user8',
            created_by='user5'
        ),
        Ticket(
            id='TKT-1016',
            title='Mobile device setup',
            description='Configure company email on new iPhone',
            status='Closed',
            priority='Low',
            category='Email & Communication',
            assigned_to='user9',
            created_by='user1'
        ),
        Ticket(
            id='TKT-1017',
            title='System performance degradation',
            description='Database queries taking 10x longer than normal',
            status='Open',
            priority='Critical',
            category='Infrastructure',
            assigned_to='user2',
            created_by='user3',
            sla_violated=1
        ),
        Ticket(
            id='TKT-1018',
            title='Firewall rule update',
            description='Need to whitelist new vendor IP addresses',
            status='Pending',
            priority='Medium',
            category='Security',
            assigned_to='user8',
            created_by='user3'
        ),
        Ticket(
            id='TKT-1019',
            title='Keyboard malfunction',
            description='Several keys not responding on laptop keyboard',
            status='New',
            priority='Medium',
            category='Hardware',
            created_by='user7'
        ),
        Ticket(
            id='TKT-1020',
            title='Shared folder access issue',
            description='Cannot access department shared folder',
            status='Closed',
            priority='Medium',
            category='Access',
            assigned_to='user2',
            created_by='user6'
        )
    ]
    
    for ticket in tickets:
        db.session.add(ticket)
    db.session.commit()
    print("✓ Created 20 sample tickets for SLA and performance testing)")
    
    print("\n✅ Database recreated successfully!")
    print(f"   Location: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print("\n📧 Test Users (all password: demo123):")
    print("\n   Normal Users:")
    print("   - john.smith@company.com")
    print("   - alice.johnson@company.com")
    print("   - bob.williams@company.com")
    print("   - carol.davis@company.com")
    print("\n   Technical Users (Agents):")
    print("   - maria.garcia@company.com (user2)")
    print("   - david.brown@company.com (user8)")
    print("   - emma.wilson@company.com (user9)")
    print("\n   Supervisors:")
    print("   - robert.chen@company.com")
    print("   - frank.miller@company.com")
    print("\n   Admin:")
    print("   - admin@company.com")
    print("\n🎫 Sample Tickets:")
    print("   - 20 tickets created for comprehensive testing")
    print("   - 5 tickets with SLA violations")
    print("   - 6 closed tickets for performance scoring")
    print("   - 2 unassigned tickets (TKT-1002, TKT-1009, TKT-1019)")
    print("   - Distributed across all 3 technical users")
