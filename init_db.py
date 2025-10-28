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
        
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_database()