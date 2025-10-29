#!/usr/bin/env python3
"""
Database Seeding Script with SQLAlchemy ORM
Seeds the PostgreSQL database with sample users, tickets, and data
"""

import os
import sys
from datetime import datetime, timedelta

# Set environment variables
os.environ['DATABASE_URL'] = 'postgresql://hotfix_user:UlNqxVgaEpb5aDMUKRQ97fZkwPn7LsSB@dpg-d3vie4ndiees73f0rtc0-a/hotfix'
os.environ['FLASK_ENV'] = 'production'

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def seed_database():
    """Seed database using SQLAlchemy ORM"""
    try:
        # Import after setting environment
        from app import create_app, db
        from app.models import User, Ticket, Message, Alert
        
        # Create Flask app
        app = create_app('production')
        
        with app.app_context():
            print("🔄 Creating database tables...")
            db.create_all()
            
            # Clear existing data
            print("🗑️ Clearing existing data...")
            Alert.query.delete()
            Message.query.delete() 
            Ticket.query.delete()
            User.query.delete()
            db.session.commit()
            
            print("👥 Creating users...")
            
            # Create users with proper ORM
            users_data = [
                {'name': 'John Smith', 'email': 'john.smith@company.com', 'role': 'Normal User'},
                {'name': 'Jane Doe', 'email': 'jane.doe@company.com', 'role': 'Normal User'},
                {'name': 'Sarah Johnson', 'email': 'sarah.johnson@company.com', 'role': 'Technical User'},
                {'name': 'Mike Chen', 'email': 'mike.chen@company.com', 'role': 'Technical User'},
                {'name': 'Lisa Rodriguez', 'email': 'lisa.rodriguez@company.com', 'role': 'Technical Supervisor'},
                {'name': 'Admin User', 'email': 'admin@company.com', 'role': 'System Admin'}
            ]
            
            users = []
            for user_data in users_data:
                user = User(
                    name=user_data['name'],
                    email=user_data['email'], 
                    role=user_data['role'],
                    is_verified=True
                )
                user.set_password('password123')
                db.session.add(user)
                users.append(user)
                print(f"  ✅ {user_data['name']} ({user_data['role']})")
            
            db.session.flush()  # Get user IDs
            
            print("🎫 Creating tickets...")
            
            # Create tickets with proper relationships
            tickets_data = [
                {
                    'ticket_id': 'TKT-1001',
                    'title': 'Password Reset Request',
                    'description': 'Unable to access email account after recent password policy update.',
                    'priority': 'Medium',
                    'category': 'Access',
                    'status': 'Open',
                    'created_by': users[0].id,  # John Smith
                    'assigned_to': users[2].id,  # Sarah Johnson
                    'created_at': datetime.utcnow() - timedelta(days=5)
                },
                {
                    'ticket_id': 'TKT-1002', 
                    'title': 'Software Installation Issue',
                    'description': 'Microsoft Office installation failing on Windows 10 workstation.',
                    'priority': 'High',
                    'category': 'Software',
                    'status': 'Open',
                    'created_by': users[0].id,  # John Smith
                    'assigned_to': users[2].id,  # Sarah Johnson
                    'created_at': datetime.utcnow() - timedelta(days=3)
                },
                {
                    'ticket_id': 'TKT-1003',
                    'title': 'Network Connectivity Problem', 
                    'description': 'Cannot connect to company VPN from home office.',
                    'priority': 'High',
                    'category': 'Network',
                    'status': 'Open',
                    'created_by': users[1].id,  # Jane Doe
                    'assigned_to': users[3].id,  # Mike Chen
                    'created_at': datetime.utcnow() - timedelta(days=2),
                    'sla_violated': True
                },
                {
                    'ticket_id': 'TKT-1004',
                    'title': 'Printer Not Working',
                    'description': 'Office printer showing paper jam error but no paper is jammed.',
                    'priority': 'Low', 
                    'category': 'Hardware',
                    'status': 'Closed',
                    'created_by': users[0].id,  # John Smith
                    'assigned_to': users[2].id,  # Sarah Johnson
                    'created_at': datetime.utcnow() - timedelta(days=7),
                    'resolved_at': datetime.utcnow() - timedelta(days=1)
                }
            ]
            
            tickets = []
            for ticket_data in tickets_data:
                ticket = Ticket(**ticket_data)
                db.session.add(ticket)
                tickets.append(ticket)
                print(f"  ✅ {ticket_data['ticket_id']} - {ticket_data['title']}")
            
            db.session.flush()  # Get ticket IDs
            
            print("💬 Creating messages...")
            
            # Create messages
            messages_data = [
                {
                    'ticket_id': tickets[0].id,
                    'sender_id': users[0].id,  # John Smith
                    'message': 'I am having trouble accessing my email. The error message says authentication failed.',
                    'created_at': tickets[0].created_at + timedelta(minutes=5)
                },
                {
                    'ticket_id': tickets[0].id,
                    'sender_id': users[2].id,  # Sarah Johnson
                    'message': 'Hi John, I can help you with this. Can you please try resetting your password first?',
                    'created_at': tickets[0].created_at + timedelta(hours=1)
                },
                {
                    'ticket_id': tickets[1].id,
                    'sender_id': users[0].id,  # John Smith
                    'message': 'Microsoft Office installation keeps failing with error code 0x80070005.',
                    'created_at': tickets[1].created_at + timedelta(minutes=10)
                },
                {
                    'ticket_id': tickets[2].id,
                    'sender_id': users[1].id,  # Jane Doe
                    'message': 'VPN connection times out after authentication. Need urgent help.',
                    'created_at': tickets[2].created_at + timedelta(minutes=15)
                }
            ]
            
            for message_data in messages_data:
                message = Message(**message_data)
                db.session.add(message)
                print(f"  ✅ Message for {tickets[0].ticket_id if message_data['ticket_id'] == tickets[0].id else 'ticket'}")
            
            print("🚨 Creating alerts...")
            
            # Create alerts
            alerts_data = [
                {
                    'user_id': users[4].id,  # Lisa Rodriguez (Supervisor)
                    'ticket_id': tickets[2].id,  # Network issue
                    'alert_type': 'sla_violation',
                    'title': 'SLA Violation Alert',
                    'message': f'Ticket {tickets[2].ticket_id} has violated SLA - High priority ticket open for 2+ days',
                    'is_read': False
                },
                {
                    'user_id': users[2].id,  # Sarah Johnson
                    'ticket_id': tickets[0].id,  # Password reset
                    'alert_type': 'assignment',
                    'title': 'New Ticket Assignment',
                    'message': f'You have been assigned ticket {tickets[0].ticket_id} - Password Reset Request',
                    'is_read': True
                }
            ]
            
            for alert_data in alerts_data:
                alert = Alert(**alert_data)
                db.session.add(alert)
                print(f"  ✅ Alert for user {alert_data['user_id']}")
            
            # Commit all changes
            print("💾 Committing to database...")
            db.session.commit()
            
            # Verify seeding
            user_count = User.query.count()
            ticket_count = Ticket.query.count()
            message_count = Message.query.count()
            alert_count = Alert.query.count()
            
            print(f"\n{'='*50}")
            print("✅ DATABASE SEEDING COMPLETED SUCCESSFULLY!")
            print(f"{'='*50}")
            print(f"👥 Users created: {user_count}")
            print(f"🎫 Tickets created: {ticket_count}")
            print(f"💬 Messages created: {message_count}")
            print(f"🚨 Alerts created: {alert_count}")
            print(f"\n🔑 Login credentials:")
            print(f"  • Normal User: john.smith@company.com / password123")
            print(f"  • Technical User: sarah.johnson@company.com / password123")
            print(f"  • Supervisor: lisa.rodriguez@company.com / password123")
            print(f"  • Admin: admin@company.com / password123")
            
            return True
            
    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🌱 Starting database seeding with SQLAlchemy ORM...")
    success = seed_database()
    
    if success:
        print("\n🎉 Database is ready for use!")
        exit(0)
    else:
        print("\n💥 Seeding failed!")
        exit(1)