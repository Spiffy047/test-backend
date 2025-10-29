#!/usr/bin/env python3
"""
Proper Database Setup and Seeding with SQLAlchemy ORM
1. Creates proper database schema
2. Seeds with comprehensive data
"""

import os
import sys
from datetime import datetime, timedelta

# Set environment
os.environ['DATABASE_URL'] = 'postgresql://hotfix_user:UlNqxVgaEpb5aDMUKRQ97fZkwPn7LsSB@dpg-d3vie4ndiees73f0rtc0-a/hotfix'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_and_seed():
    try:
        from app import create_app, db
        from app.models import User, Ticket, Message, Alert
        
        app = create_app('production')
        
        with app.app_context():
            print("🔄 Dropping and recreating database schema...")
            
            # Drop all tables and recreate with proper schema
            db.drop_all()
            db.create_all()
            
            print("✅ Database schema created successfully")
            
            # === SEED USERS ===
            print("👥 Creating users...")
            users_data = [
                ('John Smith', 'john.smith@company.com', 'Normal User'),
                ('Jane Doe', 'jane.doe@company.com', 'Normal User'),
                ('Bob Wilson', 'bob.wilson@company.com', 'Normal User'),
                ('Sarah Johnson', 'sarah.johnson@company.com', 'Technical User'),
                ('Mike Chen', 'mike.chen@company.com', 'Technical User'),
                ('Alex Rivera', 'alex.rivera@company.com', 'Technical User'),
                ('Lisa Rodriguez', 'lisa.rodriguez@company.com', 'Technical Supervisor'),
                ('David Kim', 'david.kim@company.com', 'Technical Supervisor'),
                ('Admin User', 'admin@company.com', 'System Admin'),
                ('Super Admin', 'superadmin@company.com', 'System Admin')
            ]
            
            users = []
            for name, email, role in users_data:
                user = User(
                    name=name,
                    email=email,
                    role=role,
                    is_verified=True,
                    created_at=datetime.utcnow()
                )
                user.set_password('password123')
                db.session.add(user)
                users.append(user)
                print(f"  ✅ {name} ({role})")
            
            # Commit users first to get IDs
            db.session.commit()
            
            # === SEED TICKETS ===
            print("🎫 Creating tickets...")
            now = datetime.utcnow()
            
            tickets_data = [
                {
                    'ticket_id': 'TKT-1001',
                    'title': 'Server Down - Production Outage',
                    'description': 'Main production server is completely down. All services affected.',
                    'priority': 'Critical',
                    'category': 'Hardware',
                    'status': 'Open',
                    'created_by': users[0].id,
                    'assigned_to': users[3].id,
                    'created_at': now - timedelta(hours=2),
                    'sla_violated': False
                },
                {
                    'ticket_id': 'TKT-1002',
                    'title': 'Database Connection Failure',
                    'description': 'Cannot connect to main database. Critical business operations halted.',
                    'priority': 'Critical',
                    'category': 'Software',
                    'status': 'Open',
                    'created_by': users[1].id,
                    'assigned_to': users[4].id,
                    'created_at': now - timedelta(hours=6),
                    'sla_violated': True
                },
                {
                    'ticket_id': 'TKT-1003',
                    'title': 'Email System Not Working',
                    'description': 'Company email system down for all users.',
                    'priority': 'High',
                    'category': 'Network',
                    'status': 'Pending',
                    'created_by': users[2].id,
                    'assigned_to': users[3].id,
                    'created_at': now - timedelta(hours=10),
                    'sla_violated': True
                },
                {
                    'ticket_id': 'TKT-1004',
                    'title': 'VPN Access Issues',
                    'description': 'Remote workers cannot connect to company VPN.',
                    'priority': 'High',
                    'category': 'Network',
                    'status': 'Open',
                    'created_by': users[0].id,
                    'assigned_to': users[5].id,
                    'created_at': now - timedelta(days=1),
                    'sla_violated': False
                },
                {
                    'ticket_id': 'TKT-1005',
                    'title': 'Software Installation Request',
                    'description': 'Need Adobe Creative Suite installed on workstation.',
                    'priority': 'Medium',
                    'category': 'Software',
                    'status': 'Open',
                    'created_by': users[1].id,
                    'assigned_to': users[4].id,
                    'created_at': now - timedelta(days=2)
                },
                {
                    'ticket_id': 'TKT-1006',
                    'title': 'Password Reset Request',
                    'description': 'Forgot password for company portal access.',
                    'priority': 'Medium',
                    'category': 'Access',
                    'status': 'Closed',
                    'created_by': users[2].id,
                    'assigned_to': users[3].id,
                    'created_at': now - timedelta(days=3),
                    'resolved_at': now - timedelta(days=2)
                },
                {
                    'ticket_id': 'TKT-1007',
                    'title': 'Printer Paper Jam',
                    'description': 'Office printer keeps showing paper jam error.',
                    'priority': 'Low',
                    'category': 'Hardware',
                    'status': 'Closed',
                    'created_by': users[0].id,
                    'assigned_to': users[5].id,
                    'created_at': now - timedelta(days=5),
                    'resolved_at': now - timedelta(days=4)
                },
                {
                    'ticket_id': 'TKT-1008',
                    'title': 'New Employee Setup',
                    'description': 'Need complete IT setup for new hire starting Monday.',
                    'priority': 'Medium',
                    'category': 'Access',
                    'status': 'New',
                    'created_by': users[6].id,
                    'assigned_to': None,
                    'created_at': now - timedelta(hours=4)
                }
            ]
            
            tickets = []
            for ticket_data in tickets_data:
                ticket = Ticket(**ticket_data)
                db.session.add(ticket)
                tickets.append(ticket)
                print(f"  ✅ {ticket_data['ticket_id']} - {ticket_data['title']}")
            
            # Commit tickets to get IDs
            db.session.commit()
            
            # === SEED MESSAGES ===
            print("💬 Creating messages...")
            messages_data = [
                {
                    'ticket_id': tickets[0].id,
                    'sender_id': users[0].id,
                    'message': 'Server went down around 2 hours ago. Getting 500 errors on all pages.',
                    'created_at': tickets[0].created_at + timedelta(minutes=5)
                },
                {
                    'ticket_id': tickets[0].id,
                    'sender_id': users[3].id,
                    'message': 'I\'m investigating the issue. Checking server logs now.',
                    'created_at': tickets[0].created_at + timedelta(minutes=15)
                },
                {
                    'ticket_id': tickets[1].id,
                    'sender_id': users[1].id,
                    'message': 'Database connection timeout errors since this morning.',
                    'created_at': tickets[1].created_at + timedelta(minutes=10)
                },
                {
                    'ticket_id': tickets[5].id,
                    'sender_id': users[2].id,
                    'message': 'I forgot my password and the reset email isn\'t coming through.',
                    'created_at': tickets[5].created_at + timedelta(minutes=5)
                },
                {
                    'ticket_id': tickets[5].id,
                    'sender_id': users[3].id,
                    'message': 'I\'ve reset your password manually. Check your email for the new temporary password.',
                    'created_at': tickets[5].created_at + timedelta(hours=2)
                }
            ]
            
            for message_data in messages_data:
                message = Message(**message_data)
                db.session.add(message)
                print(f"  ✅ Message for ticket {message_data['ticket_id']}")
            
            # === SEED ALERTS ===
            print("🚨 Creating alerts...")
            alerts_data = [
                {
                    'user_id': users[6].id,  # Lisa Rodriguez (Supervisor)
                    'ticket_id': tickets[1].id,  # Database issue
                    'alert_type': 'sla_violation',
                    'title': 'Critical SLA Violation',
                    'message': f'Ticket {tickets[1].ticket_id} has violated SLA - Critical priority ticket open for 6+ hours',
                    'is_read': False,
                    'created_at': datetime.utcnow()
                },
                {
                    'user_id': users[7].id,  # David Kim (Supervisor)
                    'ticket_id': tickets[2].id,  # Email issue
                    'alert_type': 'sla_violation',
                    'title': 'High Priority SLA Violation',
                    'message': f'Ticket {tickets[2].ticket_id} has violated SLA - High priority ticket open for 10+ hours',
                    'is_read': False,
                    'created_at': datetime.utcnow()
                },
                {
                    'user_id': users[3].id,  # Sarah Johnson
                    'ticket_id': tickets[0].id,  # Server issue
                    'alert_type': 'assignment',
                    'title': 'Critical Ticket Assigned',
                    'message': f'You have been assigned critical ticket {tickets[0].ticket_id}',
                    'is_read': True,
                    'created_at': datetime.utcnow()
                }
            ]
            
            for alert_data in alerts_data:
                alert = Alert(**alert_data)
                db.session.add(alert)
                print(f"  ✅ Alert for user {alert_data['user_id']}")
            
            # Final commit
            db.session.commit()
            
            # === VERIFICATION ===
            user_count = User.query.count()
            ticket_count = Ticket.query.count()
            message_count = Message.query.count()
            alert_count = Alert.query.count()
            
            # Role distribution
            role_counts = {}
            for role in ['Normal User', 'Technical User', 'Technical Supervisor', 'System Admin']:
                role_counts[role] = User.query.filter_by(role=role).count()
            
            # Status distribution
            status_counts = {}
            for status in ['New', 'Open', 'Pending', 'Closed']:
                status_counts[status] = Ticket.query.filter_by(status=status).count()
            
            print(f"\n{'='*60}")
            print("✅ DATABASE SETUP AND SEEDING COMPLETED!")
            print(f"{'='*60}")
            print(f"👥 Users: {user_count}")
            for role, count in role_counts.items():
                print(f"   • {role}: {count}")
            
            print(f"\n🎫 Tickets: {ticket_count}")
            for status, count in status_counts.items():
                print(f"   • {status}: {count}")
            
            print(f"\n💬 Messages: {message_count}")
            print(f"🚨 Alerts: {alert_count}")
            
            print(f"\n🔑 Login Credentials:")
            print(f"   • Normal User: john.smith@company.com / password123")
            print(f"   • Technical User: sarah.johnson@company.com / password123")
            print(f"   • Supervisor: lisa.rodriguez@company.com / password123")
            print(f"   • Admin: admin@company.com / password123")
            
            return True
            
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🏗️ Setting up database schema and seeding...")
    success = setup_and_seed()
    
    if success:
        print("\n🎉 Database is properly structured and seeded!")
        exit(0)
    else:
        print("\n💥 Setup failed!")
        exit(1)