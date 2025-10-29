#!/usr/bin/env python3
"""
PostgreSQL Database Initialization Script

This script initializes the IT ServiceDesk database with:
1. Creates all database tables using SQLAlchemy ORM
2. Seeds the database with realistic sample data
3. Sets up user accounts with different roles
4. Creates sample tickets with proper relationships
5. Adds conversation messages and alerts

Usage:
    python init_postgres_db.py
    
Requirements:
    - DATABASE_URL environment variable must be set
    - PostgreSQL database must be accessible
"""

# System imports
import os
import sys

# Add project root to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Flask application and database
from app import create_app, db

# Database models
from app.models import User, Ticket, Message, Alert
from app.models.attachment import FileAttachment
from app.models.sla import SLAPolicy, SLAViolation

# Utilities
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

def init_database():
    """Initialize database using Flask-SQLAlchemy ORM
    
    This function:
    1. Creates Flask app in production mode
    2. Drops existing tables (WARNING: destroys all data)
    3. Creates fresh tables from ORM models
    4. Seeds database with sample data
    5. Commits all changes as a single transaction
    
    Returns:
        bool: True if successful, False if error occurred
    """
    # Create Flask application in production configuration
    app = create_app('production')
    
    # Use application context for database operations
    with app.app_context():
        try:
            print("Initializing database with ORM models...")
            
            # WARNING: This destroys all existing data
            print("Dropping existing tables...")
            db.drop_all()
            
            # Create all tables based on ORM model definitions
            print("Creating tables...")
            db.create_all()
        
            # === SEED USERS ===
            # Create sample users representing different roles in the system
            print("Seeding users...")
            users = [
                # Normal users - can create tickets and view their own tickets
                User(name='John Smith', email='john.smith@company.com', role='Normal User'),
                User(name='Jane Doe', email='jane.doe@company.com', role='Normal User'),
                
                # Technical users - can be assigned tickets and provide support
                User(name='Sarah Johnson', email='sarah.johnson@company.com', role='Technical User'),
                User(name='Mike Chen', email='mike.chen@company.com', role='Technical User'),
                
                # Technical supervisor - can manage assignments and view analytics
                User(name='Lisa Rodriguez', email='lisa.rodriguez@company.com', role='Technical Supervisor'),
                
                # System admin - full access to all system features
                User(name='Admin User', email='admin@company.com', role='System Admin')
            ]
            
            # Set secure passwords for all users (same password for demo purposes)
            for user in users:
                user.set_password('password123')  # In production, use unique secure passwords
                db.session.add(user)
            
            # Flush to get auto-generated user IDs for foreign key relationships
            db.session.flush()
        
            # === SEED TICKETS ===
            # Create sample tickets with realistic scenarios and proper TKT-XXXX format
            print("Seeding tickets...")
            tickets = [
                # Medium priority account access issue (5 days old, assigned)
                Ticket(
                    ticket_id='TKT-1001',
                    title='Password Reset Request',
                    description='Unable to access email account after recent password policy update.',
                    priority='Medium',
                    category='Account Access',
                    status='Open',
                    created_by=users[0].id,  # John Smith
                    assigned_to=users[2].id,  # Sarah Johnson
                    created_at=datetime.utcnow() - timedelta(days=5)
                ),
                
                # High priority software issue (3 days old, in progress)
                Ticket(
                    ticket_id='TKT-1002',
                    title='Software Installation Issue',
                    description='Microsoft Office installation failing on Windows 10 workstation.',
                    priority='High',
                    category='Software',
                    status='In Progress',
                    created_by=users[0].id,  # John Smith
                    assigned_to=users[2].id,  # Sarah Johnson
                    created_at=datetime.utcnow() - timedelta(days=3)
                ),
                
                # High priority network issue (2 days old, SLA violated)
                Ticket(
                    ticket_id='TKT-1003',
                    title='Network Connectivity Problem',
                    description='Cannot connect to company VPN from home office.',
                    priority='High',
                    category='Network',
                    status='Open',
                    created_by=users[1].id,  # Jane Doe
                    assigned_to=users[3].id,  # Mike Chen
                    created_at=datetime.utcnow() - timedelta(days=2),
                    sla_violated=True  # Exceeded 8-hour SLA for High priority
                ),
                
                # Low priority hardware issue (resolved)
                Ticket(
                    ticket_id='TKT-1004',
                    title='Printer Not Working',
                    description='Office printer showing paper jam error but no paper is jammed.',
                    priority='Low',
                    category='Hardware',
                    status='Resolved',
                    created_by=users[0].id,  # John Smith
                    assigned_to=users[2].id,  # Sarah Johnson
                    created_at=datetime.utcnow() - timedelta(days=7),
                    resolved_at=datetime.utcnow() - timedelta(days=1)  # Resolved yesterday
                )
            ]
            
            # Add all tickets to database session
            for ticket in tickets:
                db.session.add(ticket)
            
            # Flush to get auto-generated ticket IDs for foreign key relationships
            db.session.flush()
        
            # === SEED MESSAGES ===
            # Create realistic conversation threads for tickets
            print("Seeding messages...")
            messages = [
                # Conversation for TKT-1001 (Password Reset)
                Message(
                    ticket_id=tickets[0].id,
                    sender_id=users[0].id,  # John Smith (ticket creator)
                    message='I am having trouble accessing my email. The error message says authentication failed.',
                    created_at=tickets[0].created_at + timedelta(minutes=5)  # 5 minutes after ticket creation
                ),
                Message(
                    ticket_id=tickets[0].id,
                    sender_id=users[2].id,  # Sarah Johnson (assigned agent)
                    message='Hi John, I can help you with this. Can you please try resetting your password first?',
                    created_at=tickets[0].created_at + timedelta(hours=1)  # Agent response after 1 hour
                ),
                
                # Initial message for TKT-1002 (Software Installation)
                Message(
                    ticket_id=tickets[1].id,
                    sender_id=users[0].id,  # John Smith
                    message='Microsoft Office installation keeps failing with error code 0x80070005.',
                    created_at=tickets[1].created_at + timedelta(minutes=10)  # Additional details
                ),
                
                # Urgent message for TKT-1003 (Network Issue)
                Message(
                    ticket_id=tickets[2].id,
                    sender_id=users[1].id,  # Jane Doe
                    message='VPN connection times out after authentication. Need urgent help.',
                    created_at=tickets[2].created_at + timedelta(minutes=15)  # Urgent follow-up
                )
            ]
            
            # Add all messages to database session
            for message in messages:
                db.session.add(message)
        
            # === SEED ALERTS ===
            # Create system notifications for users
            print("Seeding alerts...")
            alerts = [
                # SLA violation alert for supervisor (unread)
                Alert(
                    user_id=users[4].id,  # Lisa Rodriguez (Technical Supervisor)
                    ticket_id=tickets[2].id,  # TKT-1003 (Network issue with SLA violation)
                    alert_type='sla_violation',
                    title='SLA Violation Alert',
                    message=f'Ticket {tickets[2].ticket_id} has violated SLA - High priority ticket open for 2+ days',
                    is_read=False  # Unread alert requiring attention
                ),
                
                # Assignment notification for technical user (read)
                Alert(
                    user_id=users[2].id,  # Sarah Johnson (Technical User)
                    ticket_id=tickets[0].id,  # TKT-1001 (Password reset)
                    alert_type='assignment',
                    title='New Ticket Assignment',
                    message=f'You have been assigned ticket {tickets[0].ticket_id} - Password Reset Request',
                    is_read=True  # Already acknowledged by agent
                )
            ]
            
            # Add all alerts to database session
            for alert in alerts:
                db.session.add(alert)
        
            # === COMMIT TRANSACTION ===
            # Commit all changes as a single atomic transaction
            db.session.commit()
            
            # === VERIFY SEEDING SUCCESS ===
            # Count records to confirm seeding worked correctly
            user_count = User.query.count()
            ticket_count = Ticket.query.count()
            message_count = Message.query.count()
            alert_count = Alert.query.count()
            
            # Display success summary
            print(f"\n{'='*50}")
            print("DATABASE INITIALIZATION COMPLETED SUCCESSFULLY!")
            print(f"{'='*50}")
            print(f"Users created: {user_count}")
            print(f"Tickets created: {ticket_count}")
            print(f"Messages created: {message_count}")
            print(f"Alerts created: {alert_count}")
            print(f"\nSample login credentials:")
            print(f"- Normal User: john.smith@company.com / password123")
            print(f"- Technical User: sarah.johnson@company.com / password123")
            print(f"- Supervisor: lisa.rodriguez@company.com / password123")
            print(f"- Admin: admin@company.com / password123")
            
            return True
            
        except Exception as e:
            # Rollback transaction on any error to maintain data integrity
            db.session.rollback()
            print(f"\nERROR: Database initialization failed: {e}")
            print("All changes have been rolled back.")
            return False

# === SCRIPT ENTRY POINT ===
if __name__ == "__main__":
    print("Starting PostgreSQL database initialization...")
    print("WARNING: This will destroy all existing data!")
    
    # Run the initialization
    success = init_database()
    
    # Exit with appropriate code
    if success:
        print("\nDatabase ready for use!")
        exit(0)
    else:
        print("\nDatabase initialization failed!")
        exit(1)