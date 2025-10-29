"""
Production-scale database seeding for comprehensive system demonstration
"""

from flask import Blueprint, jsonify
from app import db
from werkzeug.security import generate_password_hash
from sqlalchemy import text
from datetime import datetime, timedelta
import random

production_seed_bp = Blueprint('production_seed', __name__)

@production_seed_bp.route('/production-seed', methods=['POST'])
def production_seed():
    """Create production-scale database with comprehensive data"""
    try:
        # Drop and recreate schema
        db.session.execute(text("DROP TABLE IF EXISTS alerts CASCADE"))
        db.session.execute(text("DROP TABLE IF EXISTS messages CASCADE"))
        db.session.execute(text("DROP TABLE IF EXISTS tickets CASCADE"))
        db.session.execute(text("DROP TABLE IF EXISTS users CASCADE"))
        
        # Create tables with proper schema
        db.session.execute(text("""
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(50) NOT NULL DEFAULT 'Normal User',
                is_verified BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
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
        
        db.session.execute(text("""
            CREATE TABLE messages (
                id SERIAL PRIMARY KEY,
                ticket_id INTEGER NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
                sender_id INTEGER NOT NULL REFERENCES users(id),
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
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
        
        # === COMPREHENSIVE USER BASE ===
        users_data = [
            # Normal Users (30 users)
            ('John Smith', 'john.smith@company.com', 'Normal User'),
            ('Jane Doe', 'jane.doe@company.com', 'Normal User'),
            ('Bob Wilson', 'bob.wilson@company.com', 'Normal User'),
            ('Alice Johnson', 'alice.johnson@company.com', 'Normal User'),
            ('Charlie Brown', 'charlie.brown@company.com', 'Normal User'),
            ('Diana Prince', 'diana.prince@company.com', 'Normal User'),
            ('Edward Norton', 'edward.norton@company.com', 'Normal User'),
            ('Fiona Green', 'fiona.green@company.com', 'Normal User'),
            ('George Miller', 'george.miller@company.com', 'Normal User'),
            ('Helen Davis', 'helen.davis@company.com', 'Normal User'),
            ('Ian Thompson', 'ian.thompson@company.com', 'Normal User'),
            ('Julia Roberts', 'julia.roberts@company.com', 'Normal User'),
            ('Kevin Hart', 'kevin.hart@company.com', 'Normal User'),
            ('Linda Carter', 'linda.carter@company.com', 'Normal User'),
            ('Mark Taylor', 'mark.taylor@company.com', 'Normal User'),
            ('Nancy Drew', 'nancy.drew@company.com', 'Normal User'),
            ('Oscar Wilde', 'oscar.wilde@company.com', 'Normal User'),
            ('Paula Abdul', 'paula.abdul@company.com', 'Normal User'),
            ('Quinn Adams', 'quinn.adams@company.com', 'Normal User'),
            ('Rachel Green', 'rachel.green@company.com', 'Normal User'),
            ('Steve Jobs', 'steve.jobs@company.com', 'Normal User'),
            ('Tina Turner', 'tina.turner@company.com', 'Normal User'),
            ('Uma Thurman', 'uma.thurman@company.com', 'Normal User'),
            ('Victor Hugo', 'victor.hugo@company.com', 'Normal User'),
            ('Wendy Williams', 'wendy.williams@company.com', 'Normal User'),
            ('Xavier Woods', 'xavier.woods@company.com', 'Normal User'),
            ('Yolanda King', 'yolanda.king@company.com', 'Normal User'),
            ('Zoe Saldana', 'zoe.saldana@company.com', 'Normal User'),
            ('Aaron Paul', 'aaron.paul@company.com', 'Normal User'),
            ('Betty White', 'betty.white@company.com', 'Normal User'),
            
            # Technical Users (15 users)
            ('Sarah Johnson', 'sarah.johnson@company.com', 'Technical User'),
            ('Mike Chen', 'mike.chen@company.com', 'Technical User'),
            ('Alex Rivera', 'alex.rivera@company.com', 'Technical User'),
            ('Emma Watson', 'emma.watson@company.com', 'Technical User'),
            ('Ryan Gosling', 'ryan.gosling@company.com', 'Technical User'),
            ('Sophia Loren', 'sophia.loren@company.com', 'Technical User'),
            ('Daniel Craig', 'daniel.craig@company.com', 'Technical User'),
            ('Natalie Portman', 'natalie.portman@company.com', 'Technical User'),
            ('Chris Evans', 'chris.evans@company.com', 'Technical User'),
            ('Scarlett Johansson', 'scarlett.johansson@company.com', 'Technical User'),
            ('Tom Holland', 'tom.holland@company.com', 'Technical User'),
            ('Zendaya Coleman', 'zendaya.coleman@company.com', 'Technical User'),
            ('Robert Downey', 'robert.downey@company.com', 'Technical User'),
            ('Jennifer Lawrence', 'jennifer.lawrence@company.com', 'Technical User'),
            ('Leonardo DiCaprio', 'leonardo.dicaprio@company.com', 'Technical User'),
            
            # Technical Supervisors (8 users)
            ('Lisa Rodriguez', 'lisa.rodriguez@company.com', 'Technical Supervisor'),
            ('David Kim', 'david.kim@company.com', 'Technical Supervisor'),
            ('Maria Garcia', 'maria.garcia@company.com', 'Technical Supervisor'),
            ('James Wilson', 'james.wilson@company.com', 'Technical Supervisor'),
            ('Anna Thompson', 'anna.thompson@company.com', 'Technical Supervisor'),
            ('Carlos Martinez', 'carlos.martinez@company.com', 'Technical Supervisor'),
            ('Rebecca Lee', 'rebecca.lee@company.com', 'Technical Supervisor'),
            ('Michael Brown', 'michael.brown@company.com', 'Technical Supervisor'),
            
            # System Admins (5 users)
            ('Admin User', 'admin@company.com', 'System Admin'),
            ('Super Admin', 'superadmin@company.com', 'System Admin'),
            ('IT Director', 'it.director@company.com', 'System Admin'),
            ('System Manager', 'system.manager@company.com', 'System Admin'),
            ('Security Admin', 'security.admin@company.com', 'System Admin')
        ]
        
        # Insert users with proper password hashing
        for i, (name, email, role) in enumerate(users_data, 1):
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
                'created_at': datetime.utcnow() - timedelta(days=random.randint(1, 365))
            })
        
        db.session.commit()
        
        # === COMPREHENSIVE TICKET DATASET ===
        now = datetime.utcnow()
        ticket_templates = [
            # Critical Priority Tickets
            ('Server Down - Production Outage', 'Main production server is completely down. All services affected.', 'Critical', 'Hardware'),
            ('Database Connection Failure', 'Cannot connect to main database. Critical business operations halted.', 'Critical', 'Software'),
            ('Network Infrastructure Failure', 'Complete network outage affecting all departments.', 'Critical', 'Network'),
            ('Security Breach Detected', 'Potential security breach detected in main systems.', 'Critical', 'Security'),
            ('Email Server Crash', 'Email server has crashed, no emails being sent or received.', 'Critical', 'Software'),
            
            # High Priority Tickets
            ('VPN Access Issues', 'Remote workers cannot connect to company VPN.', 'High', 'Network'),
            ('File Server Unavailable', 'Main file server is not accessible to users.', 'High', 'Hardware'),
            ('Application Performance Issues', 'Core business application running extremely slow.', 'High', 'Software'),
            ('Printer Network Down', 'All network printers are offline.', 'High', 'Hardware'),
            ('WiFi Connectivity Problems', 'WiFi network unstable across all floors.', 'High', 'Network'),
            
            # Medium Priority Tickets
            ('Software Installation Request', 'Need Adobe Creative Suite installed on workstation.', 'Medium', 'Software'),
            ('Password Reset Request', 'Forgot password for company portal access.', 'Medium', 'Access'),
            ('New Employee Setup', 'Complete IT setup for new hire starting Monday.', 'Medium', 'Access'),
            ('Monitor Replacement', 'Second monitor flickering, needs replacement.', 'Medium', 'Hardware'),
            ('Software License Renewal', 'Microsoft Office licenses expiring next month.', 'Medium', 'Software'),
            
            # Low Priority Tickets
            ('Printer Paper Jam', 'Office printer keeps showing paper jam error.', 'Low', 'Hardware'),
            ('Keyboard Replacement', 'Keyboard keys are sticking, need replacement.', 'Low', 'Hardware'),
            ('Software Training Request', 'Need training on new CRM system.', 'Low', 'Other'),
            ('Desk Phone Issues', 'Desk phone occasionally drops calls.', 'Low', 'Hardware'),
            ('Mouse Not Working', 'Wireless mouse connection issues.', 'Low', 'Hardware')
        ]
        
        statuses = ['New', 'Open', 'Pending', 'Closed']
        categories = ['Hardware', 'Software', 'Network', 'Access', 'Security', 'Other']
        
        # Create 150 tickets with realistic distribution
        ticket_counter = 1001
        for i in range(150):
            template = random.choice(ticket_templates)
            title = f"{template[0]} - Dept {random.randint(1, 10)}"
            description = template[1]
            priority = template[2]
            category = template[3]
            
            # Realistic status distribution
            if priority == 'Critical':
                status = random.choice(['Open', 'Open', 'Pending', 'Closed'])
                sla_violated = random.choice([True, False, False])
            elif priority == 'High':
                status = random.choice(['New', 'Open', 'Open', 'Pending', 'Closed'])
                sla_violated = random.choice([True, False, False, False])
            else:
                status = random.choice(['New', 'Open', 'Pending', 'Closed', 'Closed'])
                sla_violated = False
            
            # Random user assignment
            created_by = random.randint(1, 30)  # Normal users
            assigned_to = random.randint(31, 45) if status != 'New' else None  # Technical users
            
            # Realistic timestamps
            days_ago = random.randint(1, 90)
            hours_ago = random.randint(1, 23)
            created_at = now - timedelta(days=days_ago, hours=hours_ago)
            
            resolved_at = None
            if status == 'Closed':
                resolved_at = created_at + timedelta(hours=random.randint(1, 72))
            
            db.session.execute(text("""
                INSERT INTO tickets (ticket_id, title, description, priority, category, status, 
                                   created_by, assigned_to, created_at, resolved_at, sla_violated)
                VALUES (:ticket_id, :title, :description, :priority, :category, :status,
                        :created_by, :assigned_to, :created_at, :resolved_at, :sla_violated)
            """), {
                'ticket_id': f'TKT-{ticket_counter:04d}',
                'title': title,
                'description': description,
                'priority': priority,
                'category': category,
                'status': status,
                'created_by': created_by,
                'assigned_to': assigned_to,
                'created_at': created_at,
                'resolved_at': resolved_at,
                'sla_violated': sla_violated
            })
            ticket_counter += 1
        
        db.session.commit()
        
        # === COMPREHENSIVE MESSAGES ===
        message_templates = [
            "I'm experiencing this issue since this morning.",
            "The problem started after the latest update.",
            "This is affecting my daily work significantly.",
            "I've tried restarting but the issue persists.",
            "Can someone please look into this urgently?",
            "I'm investigating this issue now.",
            "I've identified the root cause and working on a fix.",
            "The issue has been resolved. Please test and confirm.",
            "I've escalated this to the appropriate team.",
            "A temporary workaround has been implemented.",
            "The fix has been deployed. Please verify.",
            "This issue is now resolved. Closing the ticket."
        ]
        
        # Create 500 messages across tickets
        for i in range(500):
            ticket_id = random.randint(1, 150)
            sender_id = random.randint(1, 58)  # Any user can send messages
            message = random.choice(message_templates)
            created_at = now - timedelta(days=random.randint(1, 30), hours=random.randint(1, 23))
            
            db.session.execute(text("""
                INSERT INTO messages (ticket_id, sender_id, message, created_at)
                VALUES (:ticket_id, :sender_id, :message, :created_at)
            """), {
                'ticket_id': ticket_id,
                'sender_id': sender_id,
                'message': message,
                'created_at': created_at
            })
        
        # === COMPREHENSIVE ALERTS ===
        alert_types = ['sla_violation', 'assignment', 'status_change', 'escalation', 'unassigned']
        alert_templates = {
            'sla_violation': 'Ticket {} has violated SLA - {} priority ticket overdue',
            'assignment': 'You have been assigned ticket {} - {}',
            'status_change': 'Ticket {} status changed to {}',
            'escalation': 'Ticket {} has been escalated due to priority',
            'unassigned': 'Ticket {} requires assignment to an agent'
        }
        
        # Create 200 alerts
        for i in range(200):
            user_id = random.randint(31, 58)  # Technical users and supervisors
            ticket_id = random.randint(1, 150)
            alert_type = random.choice(alert_types)
            
            if alert_type == 'sla_violation':
                title = 'SLA Violation Alert'
                message = alert_templates[alert_type].format(f'TKT-{1000+ticket_id}', 'High')
            elif alert_type == 'assignment':
                title = 'New Ticket Assignment'
                message = alert_templates[alert_type].format(f'TKT-{1000+ticket_id}', 'System Issue')
            else:
                title = f'{alert_type.replace("_", " ").title()} Alert'
                message = alert_templates[alert_type].format(f'TKT-{1000+ticket_id}', 'Open')
            
            is_read = random.choice([True, False, False])  # 33% read, 67% unread
            created_at = now - timedelta(days=random.randint(1, 14))
            
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
                'created_at': created_at
            })
        
        db.session.commit()
        
        # Get comprehensive statistics
        stats = {}
        
        # User statistics
        for role in ['Normal User', 'Technical User', 'Technical Supervisor', 'System Admin']:
            count = db.session.execute(text("SELECT COUNT(*) FROM users WHERE role = :role"), {'role': role}).scalar()
            stats[f'{role.lower().replace(" ", "_")}_count'] = count
        
        # Ticket statistics
        for status in ['New', 'Open', 'Pending', 'Closed']:
            count = db.session.execute(text("SELECT COUNT(*) FROM tickets WHERE status = :status"), {'status': status}).scalar()
            stats[f'{status.lower()}_tickets'] = count
        
        for priority in ['Critical', 'High', 'Medium', 'Low']:
            count = db.session.execute(text("SELECT COUNT(*) FROM tickets WHERE priority = :priority"), {'priority': priority}).scalar()
            stats[f'{priority.lower()}_priority'] = count
        
        # SLA statistics
        sla_violated = db.session.execute(text("SELECT COUNT(*) FROM tickets WHERE sla_violated = true")).scalar()
        stats['sla_violations'] = sla_violated
        
        # Message and alert counts
        stats['total_messages'] = db.session.execute(text("SELECT COUNT(*) FROM messages")).scalar()
        stats['total_alerts'] = db.session.execute(text("SELECT COUNT(*) FROM alerts")).scalar()
        stats['unread_alerts'] = db.session.execute(text("SELECT COUNT(*) FROM alerts WHERE is_read = false")).scalar()
        
        return jsonify({
            'success': True,
            'message': 'Production-scale database created successfully',
            'scale': 'Enterprise-level demonstration data',
            'data': {
                'users': 58,
                'tickets': 150,
                'messages': 500,
                'alerts': 200
            },
            'statistics': stats,
            'features_demonstrated': [
                'Role-based authentication (4 roles, 58 users)',
                'Comprehensive ticket management (150 tickets)',
                'SLA tracking with realistic violations',
                'Extensive messaging system (500 messages)',
                'Advanced alert system (200 alerts)',
                'Analytics with meaningful data',
                'Agent workload distribution',
                'Realistic priority and status distributions',
                'Historical data spanning 90 days',
                'Enterprise-scale user base'
            ],
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
            'error': str(e)
        }), 500