"""
Direct database seeding using raw SQL with proper password hashing
"""

from flask import Blueprint, jsonify
from app import db
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

direct_seed_bp = Blueprint('direct_seed', __name__)

@direct_seed_bp.route('/direct-seed', methods=['POST'])
def direct_seed():
    """Direct SQL seeding with proper password hashing"""
    try:
        # Use raw SQL to ensure proper database structure
        from sqlalchemy import text
        
        # Drop and recreate tables
        db.session.execute(text("DROP TABLE IF EXISTS alerts CASCADE"))
        db.session.execute(text("DROP TABLE IF EXISTS messages CASCADE"))
        db.session.execute(text("DROP TABLE IF EXISTS tickets CASCADE"))
        db.session.execute(text("DROP TABLE IF EXISTS users CASCADE"))
        
        # Create users table
        db.session.execute(text("""
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(50) NOT NULL DEFAULT 'Normal User',
                is_verified BOOLEAN DEFAULT true,
                verification_token VARCHAR(100),
                token_expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Create tickets table
        db.session.execute(text("""
            CREATE TABLE tickets (
                id SERIAL PRIMARY KEY,
                ticket_id VARCHAR(20) UNIQUE NOT NULL,
                title VARCHAR(200) NOT NULL,
                description TEXT NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'New',
                priority VARCHAR(20) NOT NULL,
                category VARCHAR(50) NOT NULL,
                created_by INTEGER NOT NULL REFERENCES users(id),
                assigned_to INTEGER REFERENCES users(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP,
                sla_violated BOOLEAN DEFAULT false
            )
        """))
        
        # Create messages table
        db.session.execute(text("""
            CREATE TABLE messages (
                id SERIAL PRIMARY KEY,
                ticket_id INTEGER NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
                sender_id INTEGER NOT NULL REFERENCES users(id),
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Create alerts table
        db.session.execute(text("""
            CREATE TABLE alerts (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                ticket_id INTEGER NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
                alert_type VARCHAR(50) NOT NULL,
                title VARCHAR(200) NOT NULL,
                message TEXT NOT NULL,
                is_read BOOLEAN DEFAULT false,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        db.session.commit()
        
        # Insert users with properly hashed passwords
        users_data = [
            ('John Smith', 'john.smith@company.com', 'Normal User'),
            ('Jane Doe', 'jane.doe@company.com', 'Normal User'),
            ('Sarah Johnson', 'sarah.johnson@company.com', 'Technical User'),
            ('Mike Chen', 'mike.chen@company.com', 'Technical User'),
            ('Lisa Rodriguez', 'lisa.rodriguez@company.com', 'Technical Supervisor'),
            ('Admin User', 'admin@company.com', 'System Admin')
        ]
        
        for name, email, role in users_data:
            password_hash = generate_password_hash('password123')
            db.session.execute(text("""
                INSERT INTO users (name, email, password_hash, role, is_verified, created_at)
                VALUES (:name, :email, :password_hash, :role, :is_verified, :created_at)
            """), {
                'name': name,
                'email': email,
                'password_hash': password_hash,
                'role': role,
                'is_verified': True,
                'created_at': datetime.utcnow()
            })
        
        # Insert tickets
        now = datetime.utcnow()
        tickets_data = [
            ('TKT-1001', 'Server Down - Production Outage', 'Main production server is completely down.', 'Critical', 'Hardware', 'Open', 1, 3, now - timedelta(hours=2), False),
            ('TKT-1002', 'Database Connection Failure', 'Cannot connect to main database.', 'Critical', 'Software', 'Open', 2, 4, now - timedelta(hours=6), True),
            ('TKT-1003', 'Password Reset Request', 'Forgot password for company portal.', 'Medium', 'Access', 'Closed', 1, 3, now - timedelta(days=3), False),
            ('TKT-1004', 'New Employee Setup', 'Complete IT setup for new hire.', 'Medium', 'Access', 'New', 5, None, now - timedelta(hours=4), False)
        ]
        
        for ticket_id, title, description, priority, category, status, created_by, assigned_to, created_at, sla_violated in tickets_data:
            db.session.execute(text("""
                INSERT INTO tickets (ticket_id, title, description, priority, category, status, created_by, assigned_to, created_at, sla_violated)
                VALUES (:ticket_id, :title, :description, :priority, :category, :status, :created_by, :assigned_to, :created_at, :sla_violated)
            """), {
                'ticket_id': ticket_id,
                'title': title,
                'description': description,
                'priority': priority,
                'category': category,
                'status': status,
                'created_by': created_by,
                'assigned_to': assigned_to,
                'created_at': created_at,
                'sla_violated': sla_violated
            })
        
        # Insert messages
        messages_data = [
            (1, 1, 'Server went down 2 hours ago. Getting 500 errors on all pages.', now - timedelta(hours=1, minutes=55)),
            (1, 3, 'Investigating the issue. Checking server logs now.', now - timedelta(hours=1, minutes=45)),
            (2, 2, 'Database connection timeout errors since this morning.', now - timedelta(hours=5, minutes=50))
        ]
        
        for ticket_id, sender_id, message, created_at in messages_data:
            db.session.execute(text("""
                INSERT INTO messages (ticket_id, sender_id, message, created_at)
                VALUES (:ticket_id, :sender_id, :message, :created_at)
            """), {
                'ticket_id': ticket_id,
                'sender_id': sender_id,
                'message': message,
                'created_at': created_at
            })
        
        # Insert alerts
        alerts_data = [
            (5, 2, 'sla_violation', 'Critical SLA Violation', 'Ticket TKT-1002 has violated SLA', False),
            (3, 1, 'assignment', 'Critical Ticket Assigned', 'You have been assigned critical ticket TKT-1001', True)
        ]
        
        for user_id, ticket_id, alert_type, title, message, is_read in alerts_data:
            db.session.execute(text("""
                INSERT INTO alerts (user_id, ticket_id, alert_type, title, message, is_read, created_at)
                VALUES (:user_id, :ticket_id, :alert_type, :title, :message, :is_read, :created_at)
            """), {
                'user_id': user_id,
                'ticket_id': ticket_id,
                'alert_type': alert_type,
                'title': title,
                'message': message,
                'is_read': is_read,
                'created_at': datetime.utcnow()
            })
        
        db.session.commit()
        
        # Get counts
        user_count = db.session.execute(text("SELECT COUNT(*) FROM users")).scalar()
        ticket_count = db.session.execute(text("SELECT COUNT(*) FROM tickets")).scalar()
        message_count = db.session.execute(text("SELECT COUNT(*) FROM messages")).scalar()
        alert_count = db.session.execute(text("SELECT COUNT(*) FROM alerts")).scalar()
        
        return jsonify({
            'success': True,
            'message': 'Database directly seeded with proper schema and password hashing',
            'method': 'Raw SQL with SQLAlchemy text()',
            'data': {
                'users': user_count,
                'tickets': ticket_count,
                'messages': message_count,
                'alerts': alert_count
            },
            'credentials': {
                'admin': 'admin@company.com / password123',
                'user': 'john.smith@company.com / password123',
                'tech': 'sarah.johnson@company.com / password123',
                'supervisor': 'lisa.rodriguez@company.com / password123'
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Direct seeding failed'
        }), 500