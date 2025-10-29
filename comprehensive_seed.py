#!/usr/bin/env python3
"""
Comprehensive Database Seeding with SQLAlchemy ORM
Creates complete dataset for all system functionalities
"""

import os
import sys
from datetime import datetime, timedelta
import uuid

# Set environment
os.environ['DATABASE_URL'] = 'postgresql://hotfix_user:UlNqxVgaEpb5aDMUKRQ97fZkwPn7LsSB@dpg-d3vie4ndiees73f0rtc0-a/hotfix'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def comprehensive_seed():
    try:
        from app import create_app, db
        from app.models import User, Ticket, Message, Alert
        from app.models.attachment import FileAttachment
        
        app = create_app('production')
        
        with app.app_context():
            print("🔄 Creating tables...")
            db.create_all()
            
            print("🗑️ Clearing existing data...")
            FileAttachment.query.delete()
            Alert.query.delete()
            Message.query.delete()
            Ticket.query.delete()
            User.query.delete()
            db.session.commit()
            
            # === USERS ===
            print("👥 Creating users...")
            users = [
                User(name='John Smith', email='john.smith@company.com', role='Normal User', is_verified=True),
                User(name='Jane Doe', email='jane.doe@company.com', role='Normal User', is_verified=True),
                User(name='Bob Wilson', email='bob.wilson@company.com', role='Normal User', is_verified=True),
                User(name='Sarah Johnson', email='sarah.johnson@company.com', role='Technical User', is_verified=True),
                User(name='Mike Chen', email='mike.chen@company.com', role='Technical User', is_verified=True),
                User(name='Alex Rivera', email='alex.rivera@company.com', role='Technical User', is_verified=True),
                User(name='Lisa Rodriguez', email='lisa.rodriguez@company.com', role='Technical Supervisor', is_verified=True),
                User(name='David Kim', email='david.kim@company.com', role='Technical Supervisor', is_verified=True),
                User(name='Admin User', email='admin@company.com', role='System Admin', is_verified=True),
                User(name='Super Admin', email='superadmin@company.com', role='System Admin', is_verified=True)
            ]
            
            for user in users:
                user.set_password('password123')
                db.session.add(user)
            
            db.session.flush()
            print(f"  ✅ Created {len(users)} users")
            
            # === TICKETS ===
            print("🎫 Creating comprehensive ticket dataset...")
            now = datetime.utcnow()
            
            tickets = [
                # Critical Priority Tickets
                Ticket(ticket_id='TKT-1001', title='Server Down - Production Outage', 
                      description='Main production server is completely down. All services affected.',
                      priority='Critical', category='Hardware', status='Open', 
                      created_by=users[0].id, assigned_to=users[3].id,
                      created_at=now - timedelta(hours=2), sla_violated=False),
                
                Ticket(ticket_id='TKT-1002', title='Database Connection Failure',
                      description='Cannot connect to main database. Critical business operations halted.',
                      priority='Critical', category='Software', status='Open',
                      created_by=users[1].id, assigned_to=users[4].id,
                      created_at=now - timedelta(hours=6), sla_violated=True),
                
                # High Priority Tickets
                Ticket(ticket_id='TKT-1003', title='Email System Not Working',
                      description='Company email system down for all users.',
                      priority='High', category='Network', status='Pending',
                      created_by=users[2].id, assigned_to=users[3].id,
                      created_at=now - timedelta(hours=10), sla_violated=True),
                
                Ticket(ticket_id='TKT-1004', title='VPN Access Issues',
                      description='Remote workers cannot connect to company VPN.',
                      priority='High', category='Network', status='Open',
                      created_by=users[0].id, assigned_to=users[5].id,
                      created_at=now - timedelta(days=1), sla_violated=False),
                
                # Medium Priority Tickets
                Ticket(ticket_id='TKT-1005', title='Software Installation Request',
                      description='Need Adobe Creative Suite installed on workstation.',
                      priority='Medium', category='Software', status='Open',
                      created_by=users[1].id, assigned_to=users[4].id,
                      created_at=now - timedelta(days=2)),
                
                Ticket(ticket_id='TKT-1006', title='Password Reset Request',
                      description='Forgot password for company portal access.',
                      priority='Medium', category='Access', status='Closed',
                      created_by=users[2].id, assigned_to=users[3].id,
                      created_at=now - timedelta(days=3),
                      resolved_at=now - timedelta(days=2)),
                
                # Low Priority Tickets
                Ticket(ticket_id='TKT-1007', title='Printer Paper Jam',
                      description='Office printer keeps showing paper jam error.',
                      priority='Low', category='Hardware', status='Closed',
                      created_by=users[0].id, assigned_to=users[5].id,
                      created_at=now - timedelta(days=5),
                      resolved_at=now - timedelta(days=4)),
                
                Ticket(ticket_id='TKT-1008', title='Monitor Flickering',
                      description='Second monitor occasionally flickers.',
                      priority='Low', category='Hardware', status='Open',
                      created_by=users[1].id, assigned_to=users[4].id,
                      created_at=now - timedelta(days=7)),
                
                # Unassigned Tickets
                Ticket(ticket_id='TKT-1009', title='New Employee Setup',
                      description='Need complete IT setup for new hire starting Monday.',
                      priority='Medium', category='Access', status='New',
                      created_by=users[6].id, assigned_to=None,
                      created_at=now - timedelta(hours=4)),
                
                Ticket(ticket_id='TKT-1010', title='Software License Renewal',
                      description='Microsoft Office licenses expiring next month.',
                      priority='Low', category='Software', status='New',
                      created_by=users[7].id, assigned_to=None,
                      created_at=now - timedelta(days=1))
            ]
            
            for ticket in tickets:
                db.session.add(ticket)
            
            db.session.flush()
            print(f"  ✅ Created {len(tickets)} tickets")
            
            # === MESSAGES ===
            print("💬 Creating ticket conversations...")
            messages = [
                # TKT-1001 conversation
                Message(ticket_id=tickets[0].id, sender_id=users[0].id,
                       message='Server went down around 2 hours ago. Getting 500 errors on all pages.',
                       created_at=tickets[0].created_at + timedelta(minutes=5)),
                Message(ticket_id=tickets[0].id, sender_id=users[3].id,
                       message='I\'m investigating the issue. Checking server logs now.',
                       created_at=tickets[0].created_at + timedelta(minutes=15)),
                Message(ticket_id=tickets[0].id, sender_id=users[3].id,
                       message='Found the issue - disk space full. Working on cleanup.',
                       created_at=tickets[0].created_at + timedelta(minutes=45)),
                
                # TKT-1002 conversation
                Message(ticket_id=tickets[1].id, sender_id=users[1].id,
                       message='Database connection timeout errors since this morning.',
                       created_at=tickets[1].created_at + timedelta(minutes=10)),
                Message(ticket_id=tickets[1].id, sender_id=users[4].id,
                       message='This is critical. Escalating to database team immediately.',
                       created_at=tickets[1].created_at + timedelta(minutes=30)),
                
                # TKT-1006 conversation (resolved)
                Message(ticket_id=tickets[5].id, sender_id=users[2].id,
                       message='I forgot my password and the reset email isn\'t coming through.',
                       created_at=tickets[5].created_at + timedelta(minutes=5)),
                Message(ticket_id=tickets[5].id, sender_id=users[3].id,
                       message='I\'ve reset your password manually. Check your email for the new temporary password.',
                       created_at=tickets[5].created_at + timedelta(hours=2)),
                Message(ticket_id=tickets[5].id, sender_id=users[2].id,
                       message='Perfect! I can log in now. Thank you!',
                       created_at=tickets[5].created_at + timedelta(hours=3))
            ]
            
            for message in messages:
                db.session.add(message)
            
            print(f"  ✅ Created {len(messages)} messages")
            
            # === ALERTS ===
            print("🚨 Creating alerts...")
            alerts = [
                # SLA Violation Alerts
                Alert(user_id=users[6].id, ticket_id=tickets[1].id,
                     alert_type='sla_violation', title='Critical SLA Violation',
                     message=f'Ticket {tickets[1].ticket_id} has violated SLA - Critical priority ticket open for 6+ hours',
                     is_read=False),
                
                Alert(user_id=users[7].id, ticket_id=tickets[2].id,
                     alert_type='sla_violation', title='High Priority SLA Violation',
                     message=f'Ticket {tickets[2].ticket_id} has violated SLA - High priority ticket open for 10+ hours',
                     is_read=False),
                
                # Assignment Alerts
                Alert(user_id=users[3].id, ticket_id=tickets[0].id,
                     alert_type='assignment', title='Critical Ticket Assigned',
                     message=f'You have been assigned critical ticket {tickets[0].ticket_id}',
                     is_read=True),
                
                Alert(user_id=users[4].id, ticket_id=tickets[1].id,
                     alert_type='assignment', title='Critical Ticket Assigned',
                     message=f'You have been assigned critical ticket {tickets[1].ticket_id}',
                     is_read=False),
                
                # Status Change Alerts
                Alert(user_id=users[2].id, ticket_id=tickets[5].id,
                     alert_type='status_change', title='Ticket Resolved',
                     message=f'Your ticket {tickets[5].ticket_id} has been resolved',
                     is_read=True),
                
                # Unassigned Ticket Alerts
                Alert(user_id=users[6].id, ticket_id=tickets[8].id,
                     alert_type='unassigned', title='Unassigned Ticket Requires Attention',
                     message=f'Ticket {tickets[8].ticket_id} needs to be assigned to an agent',
                     is_read=False)
            ]
            
            for alert in alerts:
                db.session.add(alert)
            
            print(f"  ✅ Created {len(alerts)} alerts")
            
            # === FILE ATTACHMENTS ===
            print("📎 Creating file attachments...")
            attachments = [
                FileAttachment(
                    id=str(uuid.uuid4()),
                    ticket_id=tickets[0].id,
                    filename='server_error_log.txt',
                    file_size=2048576,  # 2MB
                    mime_type='text/plain',
                    uploaded_by=str(users[0].id)
                ),
                FileAttachment(
                    id=str(uuid.uuid4()),
                    ticket_id=tickets[1].id,
                    filename='database_error_screenshot.png',
                    file_size=1024000,  # 1MB
                    mime_type='image/png',
                    uploaded_by=str(users[1].id)
                ),
                FileAttachment(
                    id=str(uuid.uuid4()),
                    ticket_id=tickets[4].id,
                    filename='software_requirements.pdf',
                    file_size=512000,  # 512KB
                    mime_type='application/pdf',
                    uploaded_by=str(users[1].id)
                )
            ]
            
            for attachment in attachments:
                db.session.add(attachment)
            
            print(f"  ✅ Created {len(attachments)} file attachments")
            
            # === COMMIT ALL CHANGES ===
            print("💾 Committing to database...")
            db.session.commit()
            
            # === VERIFICATION ===
            user_count = User.query.count()
            ticket_count = Ticket.query.count()
            message_count = Message.query.count()
            alert_count = Alert.query.count()
            attachment_count = FileAttachment.query.count()
            
            # Role distribution
            role_counts = {}
            for role in ['Normal User', 'Technical User', 'Technical Supervisor', 'System Admin']:
                role_counts[role] = User.query.filter_by(role=role).count()
            
            # Ticket status distribution
            status_counts = {}
            for status in ['New', 'Open', 'Pending', 'Closed']:
                status_counts[status] = Ticket.query.filter_by(status=status).count()
            
            # Priority distribution
            priority_counts = {}
            for priority in ['Critical', 'High', 'Medium', 'Low']:
                priority_counts[priority] = Ticket.query.filter_by(priority=priority).count()
            
            print(f"\n{'='*60}")
            print("✅ COMPREHENSIVE DATABASE SEEDING COMPLETED!")
            print(f"{'='*60}")
            print(f"👥 Users: {user_count}")
            for role, count in role_counts.items():
                print(f"   • {role}: {count}")
            
            print(f"\n🎫 Tickets: {ticket_count}")
            for status, count in status_counts.items():
                print(f"   • {status}: {count}")
            
            print(f"\n⚡ Priority Distribution:")
            for priority, count in priority_counts.items():
                print(f"   • {priority}: {count}")
            
            print(f"\n💬 Messages: {message_count}")
            print(f"🚨 Alerts: {alert_count}")
            print(f"📎 Attachments: {attachment_count}")
            
            print(f"\n🔑 Login Credentials:")
            print(f"   • Normal User: john.smith@company.com / password123")
            print(f"   • Technical User: sarah.johnson@company.com / password123")
            print(f"   • Supervisor: lisa.rodriguez@company.com / password123")
            print(f"   • Admin: admin@company.com / password123")
            
            print(f"\n🎯 System Features Covered:")
            print(f"   ✅ Role-based authentication (4 roles)")
            print(f"   ✅ Ticket management (all priorities/statuses)")
            print(f"   ✅ SLA tracking (violations included)")
            print(f"   ✅ Real-time messaging")
            print(f"   ✅ Alert system")
            print(f"   ✅ File attachments")
            print(f"   ✅ Analytics data")
            print(f"   ✅ Agent workload distribution")
            
            return True
            
    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🌱 Starting comprehensive database seeding...")
    success = comprehensive_seed()
    
    if success:
        print("\n🎉 Database is fully seeded and ready!")
        exit(0)
    else:
        print("\n💥 Seeding failed!")
        exit(1)