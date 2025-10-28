from app import create_app, db
from app.models import User, Ticket, Message

def init_database():
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if users already exist
        if User.query.count() == 0:
            # Create sample users
            users_data = [
                {'name': 'John Smith', 'email': 'john.smith@company.com', 'role': 'Normal User'},
                {'name': 'Maria Garcia', 'email': 'maria.garcia@company.com', 'role': 'Technical User'},
                {'name': 'Robert Chen', 'email': 'robert.chen@company.com', 'role': 'Technical Supervisor'},
                {'name': 'Admin User', 'email': 'mwanikijoe1@gmail.com', 'role': 'System Admin'},
            ]
            
            for user_data in users_data:
                user = User(
                    name=user_data['name'],
                    email=user_data['email'],
                    role=user_data['role']
                )
                user.set_password('password123')
                db.session.add(user)
            
            db.session.commit()
            print("Sample users created successfully!")
        
        # Check if tickets already exist
        if Ticket.query.count() == 0:
            # Get user IDs for ticket creation
            john = User.query.filter_by(email='john.smith@company.com').first()
            maria = User.query.filter_by(email='maria.garcia@company.com').first()
            
            if john and maria:
                # Create sample tickets with proper TKT-XXXX format
                tickets_data = [
                    {
                        'ticket_id': 'TKT-1001',
                        'title': 'Unable to access company email',
                        'description': 'I cannot log into my email account. Getting authentication failed error.',
                        'priority': 'High',
                        'category': 'Email & Communication',
                        'status': 'Open',
                        'created_by': john.id,
                        'assigned_to': maria.id
                    },
                    {
                        'ticket_id': 'TKT-1002',
                        'title': 'Laptop running very slow',
                        'description': 'My laptop has become extremely slow over the past few days.',
                        'priority': 'Medium',
                        'category': 'Hardware',
                        'status': 'New',
                        'created_by': john.id
                    },
                    {
                        'ticket_id': 'TKT-1003',
                        'title': 'VPN connection issues',
                        'description': 'Cannot connect to company VPN from home.',
                        'priority': 'High',
                        'category': 'Network & Connectivity',
                        'status': 'Pending',
                        'created_by': john.id,
                        'assigned_to': maria.id,
                        'sla_violated': True
                    }
                ]
                
                for ticket_data in tickets_data:
                    ticket = Ticket(
                        ticket_id=ticket_data['ticket_id'],
                        title=ticket_data['title'],
                        description=ticket_data['description'],
                        priority=ticket_data['priority'],
                        category=ticket_data['category'],
                        status=ticket_data['status'],
                        created_by=ticket_data['created_by'],
                        assigned_to=ticket_data.get('assigned_to'),
                        sla_violated=ticket_data.get('sla_violated', False)
                    )
                    db.session.add(ticket)
                
                db.session.commit()
                print("Sample tickets created successfully!")
        
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_database()