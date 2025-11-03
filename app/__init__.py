
# Creates and configures Flask application with intelligent auto-assignment,
# advanced file upload support, and comprehensive analytics capabilities.

# Core Flask imports
from flask import Flask, request, jsonify, Response

# Database and ORM
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Security and authentication
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

# Serialization and validation
from flask_marshmallow import Marshmallow
from marshmallow import ValidationError

# Configuration and utilities
from dotenv import load_dotenv
from datetime import datetime
import os
import uuid

# Load environment variables from .env file
load_dotenv()

# Initialize Flask extensions (will be bound to app in create_app)
db = SQLAlchemy()  # Database ORM
migrate = Migrate()  # Database migrations
jwt = JWTManager()  # JWT token management (currently disabled)
ma = Marshmallow()  # Object serialization/deserialization

def create_app(config_name='default'):
    """Flask application factory with enhanced features
    
    Creates Flask app with intelligent auto-assignment, file upload support,
    and comprehensive analytics. Includes database initialization, JWT auth,
    and dynamic configuration management.
    
    Args:
        config_name (str): Environment configuration
    
    Returns:
        Flask: Fully configured application instance
    """
    # Create Flask application instance
    app = Flask(__name__)
    
    # === CONFIGURATION LOADING ===
    # Load configuration based on environment
    from config import config
    app.config.from_object(config[config_name])
    
    # === DATABASE INITIALIZATION ===
    # Initialize PostgreSQL with configuration tables and fallback support
    try:
        # Bind SQLAlchemy and Flask-Migrate to app
        db.init_app(app)
        migrate.init_app(app, db)
        print("[OK] Database initialized successfully")
        
        # Create database tables if they don't exist
        with app.app_context():
            try:
                db.create_all()
                print("[OK] Database tables initialized successfully")
                
                # Initialize configuration tables (safe - won't affect existing data)
                try:
                    from app.services.configuration_service import ConfigurationService
                    ConfigurationService.initialize_default_configuration()
                    print("[OK] Configuration tables initialized")
                except Exception as config_error:
                    print(f"[WARNING] Configuration init warning: {config_error}")
            except Exception as e:
                print(f"[WARNING] Database table creation error: {e}")
                
    except Exception as e:
        print(f"[ERROR] Database initialization failed: {e}")
        # Fallback to in-memory SQLite for basic functionality
        print("[RETRY] Falling back to in-memory SQLite database")
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        db.init_app(app)
    
    # === EXTENSION INITIALIZATION ===
    # Configure JWT authentication and serialization
    
    # JWT Configuration
    app.config['JWT_SECRET_KEY'] = 'hardcoded-jwt-secret-key-for-testing-12345'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  
    
    jwt.init_app(app)  # JWT authentication
    ma.init_app(app)   # Marshmallow serialization
    
    # JWT Error Handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {'error': 'Token has expired'}, 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {'error': 'Invalid token'}, 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return {'error': 'Authorization token required'}, 401
    
    
    
    # === CORS CONFIGURATION ===
    # Enable cross-origin requests for React frontend integration
    # Configured for development with production-ready security options
    CORS(app, 
         resources={r"/*": {"origins": "*"}},  # Allow all origins (dev only)
         allow_headers=["Content-Type", "Authorization", "X-Requested-With", "X-CSRF-Token"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         supports_credentials=False  # Disabled for deployment compatibility
    )
    
    # === BLUEPRINT REGISTRATION ===
    # Register API endpoints with intelligent auto-assignment and file upload support
    
    # Configuration management
    from app.routes.config import config_bp
    app.register_blueprint(config_bp, url_prefix='/api/config')
    print("[OK] Configuration routes registered")
    
    # Database initialization
    from app.routes.db_init import db_init_bp
    app.register_blueprint(db_init_bp, url_prefix='/api/db')
    print("[OK] Database init routes registered")
    
    # Main RESTful API endpoints (tickets, users, etc.) - MUST BE FIRST
    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    print("[OK] RESTful API routes registered")
    
    # Register Swagger documentation (after API to avoid conflicts)
    from app.swagger import swagger_bp
    app.register_blueprint(swagger_bp, url_prefix='/api/docs')
    print("[OK] Swagger documentation registered at /api/docs/")
    
    # Administrative endpoints (system management)
    from app.routes.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    print(" Admin routes registered")
    
    # Migration endpoints
    from app.routes.migration import migration_bp
    app.register_blueprint(migration_bp, url_prefix='/api/migration')
    print("[OK] Migration routes registered")
    
    # Status workflow management
    from app.routes.status import status_bp
    app.register_blueprint(status_bp, url_prefix='/api/status')
    print("[OK] Status workflow routes registered")
    
    # File routes removed - using frontend Cloudinary integration
    
    
    # === CORE API ENDPOINTS ===
    # System health, testing, and analytics endpoints
    
    @app.route('/')
    def index():
        """API root endpoint - returns basic system information"""
        return {
            'message': 'Hotfix ServiceDesk API', 
            'version': '2.0.0', 
            'status': 'healthy',
            'documentation': 'Contact system administrator for API documentation'
        }
    
    # Health check endpoint removed - using /api/test instead
    
    @app.route('/api/test')
    def test_api():
        """Simple API test endpoint for connectivity verification"""
        return {
            'message': 'API is working', 
            'status': 'ok',
            'timestamp': datetime.utcnow().isoformat()
        }
    
    @app.route('/api/test/users')
    def test_users():
        """Test endpoint to check users without JWT protection"""
        try:
            from app.models import User
            users_query = User.query.limit(5).all()
            users = []
            for user in users_query:
                users.append({
                    'id': user.id,
                    'name': user.name, 
                    'email': user.email,
                    'role': user.role
                })
            return {'users': users, 'count': len(users)}
        except Exception as e:
            return {'error': str(e), 'users': []}
    
    @app.route('/api/test/create-user', methods=['POST'])
    def create_test_user():
        """Create a test user for JWT testing"""
        try:
            from app.models import User
            
            # Check if test user already exists
            existing = User.query.filter_by(email='test@test.com').first()
            if existing:
                return {'message': 'Test user already exists', 'email': 'test@test.com'}
            
            # Create test user
            user = User(
                name='Test User',
                email='test@test.com',
                role='System Admin'
            )
            user.set_password('test123')
            
            db.session.add(user)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Test user created',
                'email': 'test@test.com',
                'password': 'test123'
            }
        except Exception as e:
            return {'error': str(e)}, 500
    

    
    # Note: Authentication endpoints moved to Flask-RESTful resources
    
    # === ANALYTICS ENDPOINTS ===
    # Real-time dashboard metrics with live database queries
    
    @app.route('/api/tickets/analytics/sla-adherence')
    def sla_adherence():
        """Real-time SLA adherence calculation from live database
        
        Calculates current SLA performance metrics with null safety
        and percentage calculations for dashboard display.
        """
        try:
            # Use raw SQL for better performance on analytics queries
            from sqlalchemy import text
            
            # Query ticket SLA statistics from database
            result = db.session.execute(text("""
                SELECT 
                    COUNT(*) as total_tickets,
                    COUNT(CASE WHEN sla_violated = false THEN 1 END) as on_time,
                    COUNT(CASE WHEN sla_violated = true THEN 1 END) as violations
                FROM tickets
            """))
            
            # Extract results with null safety
            row = result.fetchone()
            total_tickets = row[0] if row else 0
            on_time = row[1] if row else 0
            violations = row[2] if row else 0
            
            # Calculate SLA adherence percentage (avoid division by zero)
            sla_adherence = (on_time / total_tickets * 100) if total_tickets > 0 else 0
            
            return {
                'sla_adherence': round(sla_adherence, 1),
                'total_tickets': total_tickets,
                'violations': violations,
                'on_time': on_time,
                'trend': 'stable'
            }
        except Exception as e:
            print(f"Error fetching SLA adherence: {e}")
            return {
                'sla_adherence': 0,
                'total_tickets': 0,
                'violations': 0,
                'on_time': 0,
                'trend': 'stable'
            }
    
    @app.route('/api/agents/performance')
    def agent_performance():
        """Agent performance metrics with workload and SLA tracking"""
        try:
            from sqlalchemy import text
            
            result = db.session.execute(text("""
                SELECT 
                    u.id, u.name, u.email, u.role,
                    COALESCE(COUNT(CASE WHEN t.status IN ('Resolved', 'Closed') THEN 1 END), 0) as tickets_closed,
                    COALESCE(AVG(CASE WHEN t.status IN ('Resolved', 'Closed') AND t.resolved_at IS NOT NULL THEN 
                        EXTRACT(EPOCH FROM (t.resolved_at - t.created_at))/3600 END), 0) as avg_handle_time,
                    COALESCE(COUNT(CASE WHEN t.sla_violated = true THEN 1 END), 0) as sla_violations,
                    COALESCE(COUNT(CASE WHEN t.assigned_to = u.id THEN 1 END), 0) as total_assigned
                FROM users u
                LEFT JOIN tickets t ON u.id = t.assigned_to
                WHERE u.role IN ('Technical User', 'Technical Supervisor')
                GROUP BY u.id, u.name, u.email, u.role
                ORDER BY u.name
            """))
            
            agents = []
            for row in result:
                closed = row[4] or 0
                violations = row[6] or 0
                total_assigned = row[7] or 0
                score = max(0, (closed * 10) - (violations * 5))
                rating = 'Excellent' if score >= 50 else 'Good' if score >= 30 else 'Average' if score >= 15 else 'Needs Improvement'
                
                agents.append({
                    'id': row[0],
                    'name': row[1],
                    'email': row[2],
                    'role': row[3],
                    'tickets_closed': closed,
                    'total_assigned': total_assigned,
                    'avg_handle_time': round(row[5] or 0, 1),
                    'sla_violations': violations,
                    'rating': rating
                })
            
            return agents
        except Exception as e:
            print(f"Error fetching agent performance: {e}")
            return []
    
    @app.route('/api/agents')
    def agents_list():
        """Get list of all agents from database"""
        try:
            from sqlalchemy import text
            
            result = db.session.execute(text("""
                SELECT id, name, email, role
                FROM users 
                WHERE role IN ('Technical User', 'Technical Supervisor')
                ORDER BY name
            """))
            
            agents = []
            for row in result:
                agents.append({
                    'id': row[0],
                    'name': row[1],
                    'email': row[2],
                    'role': row[3]
                })
            
            return agents
        except Exception as e:
            print(f"Error fetching agents: {e}")
            return []
    
    @app.route('/api/analytics/ticket-status-counts')
    def ticket_status_counts():
        try:
            from sqlalchemy import text
            result = db.session.execute(text("""
                SELECT status, COUNT(*) as count 
                FROM tickets 
                GROUP BY status
            """))
            
            counts = {'new': 0, 'open': 0, 'pending': 0, 'closed': 0}
            for row in result:
                status = row[0].lower()
                # Map database status values to expected keys
                if status == 'resolved':
                    counts['closed'] += row[1]
                elif status == 'in progress':
                    counts['open'] += row[1]
                elif status in ['new', 'open', 'pending']:
                    counts[status] = row[1]
                else:
                    # Handle any other status by mapping to appropriate category
                    if 'close' in status or 'resolve' in status:
                        counts['closed'] += row[1]
                    elif 'progress' in status or 'active' in status:
                        counts['open'] += row[1]
                    else:
                        counts['new'] += row[1]
            
            return counts
        except Exception as e:
            print(f"Error fetching ticket counts: {e}")
            return {'new': 0, 'open': 0, 'pending': 0, 'closed': 0}
    
    @app.route('/api/analytics/unassigned-tickets')
    def unassigned_tickets():
        try:
            from sqlalchemy import text
            
            result = db.session.execute(text("""
                SELECT 
                    id,
                    ticket_id,
                    title,
                    priority,
                    category,
                    status,
                    created_at,
                    EXTRACT(EPOCH FROM (NOW() - created_at))/3600 as hours_open
                FROM tickets 
                WHERE assigned_to IS NULL AND status NOT IN ('Closed', 'Resolved')
                ORDER BY created_at DESC
                LIMIT 20
            """))
            
            tickets = []
            for row in result:
                tickets.append({
                    'id': row[1] or f'TKT-{row[0]}',  # Use ticket_id or generate from id
                    'ticket_id': row[1] or f'TKT-{row[0]}',
                    'title': row[2],
                    'priority': row[3],
                    'category': row[4],
                    'status': row[5],
                    'created_at': row[6].isoformat() if row[6] else None,
                    'hours_open': round(float(row[7]), 1) if row[7] else 0
                })
            
            return {'tickets': tickets}
        except Exception as e:
            print(f"Error fetching unassigned tickets: {e}")
            return {'tickets': []}
    
    @app.route('/api/analytics/agent-workload')
    def agent_workload():
        try:
            from sqlalchemy import text
            
            result = db.session.execute(text("""
                SELECT 
                    u.id,
                    u.name,
                    u.email,
                    u.role,
                    COALESCE(COUNT(t.id), 0) as total_tickets,
                    COALESCE(COUNT(CASE WHEN t.status NOT IN ('Resolved', 'Closed') THEN 1 END), 0) as active_tickets,
                    COALESCE(COUNT(CASE WHEN t.status = 'Pending' THEN 1 END), 0) as pending_tickets,
                    COALESCE(COUNT(CASE WHEN t.status IN ('Resolved', 'Closed') THEN 1 END), 0) as closed_tickets
                FROM users u
                LEFT JOIN tickets t ON u.id = t.assigned_to
                WHERE u.role IN ('Technical User', 'Technical Supervisor')
                GROUP BY u.id, u.name, u.email, u.role
                ORDER BY u.name
            """))
            
            agents = []
            for row in result:
                agents.append({
                    'agent_id': row[0],
                    'id': row[0],
                    'name': row[1],
                    'email': row[2],
                    'role': row[3],
                    'ticket_count': row[4],
                    'active_tickets': row[5],
                    'pending_tickets': row[6],
                    'closed_tickets': row[7]
                })
            
            return agents
        except Exception as e:
            print(f"Error fetching agent workload: {e}")
            return []
    
    @app.route('/api/analytics/agent-performance-detailed')
    def agent_performance_detailed():
        try:
            from sqlalchemy import text
            
            result = db.session.execute(text("""
                SELECT 
                    u.id,
                    u.name,
                    u.email,
                    u.role,
                    COALESCE(COUNT(CASE WHEN t.status NOT IN ('Resolved', 'Closed') THEN 1 END), 0) as active_tickets,
                    COALESCE(COUNT(CASE WHEN t.status IN ('Resolved', 'Closed') THEN 1 END), 0) as closed_tickets,
                    COALESCE(COUNT(CASE WHEN t.sla_violated = true THEN 1 END), 0) as sla_violations,
                    COALESCE(AVG(CASE WHEN t.status IN ('Resolved', 'Closed') THEN 
                        EXTRACT(EPOCH FROM (t.updated_at - t.created_at))/3600 END), 0) as avg_handle_time
                FROM users u
                LEFT JOIN tickets t ON u.id = t.assigned_to
                WHERE u.role IN ('Technical User', 'Technical Supervisor')
                GROUP BY u.id, u.name, u.email, u.role
                ORDER BY u.name
            """))
            
            agents = []
            for row in result:
                closed_tickets = row[5] or 0
                sla_violations = row[6] or 0
                score = max(0, (closed_tickets * 10) - (sla_violations * 5))
                rating = 'Excellent' if score >= 50 else 'Good' if score >= 30 else 'Average' if score >= 15 else 'Needs Improvement'
                
                agents.append({
                    'agent_id': row[0],
                    'id': row[0],
                    'name': row[1],
                    'email': row[2],
                    'role': row[3],
                    'active_tickets': row[4],
                    'closed_tickets': closed_tickets,
                    'avg_handle_time': round(row[7] or 0, 1),
                    'sla_violations': sla_violations,
                    'rating': rating,
                    'performance_rating': rating,
                    'performance_score': score,
                    'satisfaction_score': 4.0
                })
            
            return agents
        except Exception as e:
            print(f"Error fetching agent performance: {e}")
            return []
    
    @app.route('/api/alerts/<user_id>/count', methods=['GET', 'OPTIONS'])
    def alert_count(user_id):
        if request.method == 'OPTIONS':
            return '', 200
        
        try:
            from sqlalchemy import text
            
            result = db.session.execute(text("""
                SELECT COUNT(*) FROM alerts WHERE user_id = :user_id AND is_read = false
            """), {'user_id': user_id})
            
            count = result.scalar() or 0
            return {'count': count}
        except Exception as e:
            print(f"Error fetching alert count for user {user_id}: {e}")
            return {'count': 0}
    
    @app.route('/api/messages/ticket/<ticket_id>/timeline')
    def ticket_timeline(ticket_id):
        try:
            from sqlalchemy import text
            
            # Get ticket ID from ticket_id string
            ticket_result = db.session.execute(text("""
                SELECT id FROM tickets WHERE ticket_id = :ticket_id
            """), {'ticket_id': ticket_id})
            
            ticket_row = ticket_result.fetchone()
            if not ticket_row:
                return []
            
            internal_ticket_id = ticket_row[0]
            
            # Get messages from database
            result = db.session.execute(text("""
                SELECT m.id, m.message, m.created_at, m.sender_id, u.name, u.role, m.image_url
                FROM messages m
                LEFT JOIN users u ON m.sender_id = u.id
                WHERE m.ticket_id = :ticket_id
                ORDER BY m.created_at ASC
            """), {'ticket_id': internal_ticket_id})
            
            messages = []
            for row in result:
                messages.append({
                    'id': row[0],
                    'ticket_id': ticket_id,
                    'sender_id': row[3],
                    'sender_name': row[4] or 'Unknown User',
                    'sender_role': row[5] or 'Normal User',
                    'message': row[1],
                    'image_url': row[6],  # Include Cloudinary URL
                    'timestamp': row[2].isoformat() + 'Z' if row[2] else None,
                    'type': 'message'
                })
            
            # Add any new messages from memory store
            if ticket_id in messages_store:
                messages.extend(messages_store[ticket_id])
            
            return messages
        except Exception as e:
            print(f"Error fetching timeline for {ticket_id}: {e}")
            return []
    
    @app.route('/api/tickets/<ticket_id>/activities')
    def ticket_activities(ticket_id):
        try:
            from sqlalchemy import text
            
            activities = []
            
            # Get ticket creation activity
            ticket_result = db.session.execute(text("""
                SELECT t.created_at, u.name as creator_name, t.status, t.assigned_to, t.updated_at
                FROM tickets t
                LEFT JOIN users u ON t.created_by = u.id
                WHERE t.ticket_id = :ticket_id OR t.id = :ticket_id
            """), {'ticket_id': ticket_id})
            
            ticket_row = ticket_result.fetchone()
            if ticket_row:
                # Ticket creation
                activities.append({
                    'id': f'create_{ticket_id}',
                    'ticket_id': ticket_id,
                    'description': f'Ticket created by {ticket_row[1] or "Unknown User"}',
                    'performed_by': 'system',
                    'performed_by_name': 'System',
                    'created_at': ticket_row[0].isoformat() + 'Z' if ticket_row[0] else None,
                    'timestamp': ticket_row[0].isoformat() + 'Z' if ticket_row[0] else None
                })
                
                # Status change activity (if updated)
                if ticket_row[4] and ticket_row[4] != ticket_row[0]:  # updated_at != created_at
                    activities.append({
                        'id': f'status_{ticket_id}',
                        'ticket_id': ticket_id,
                        'description': f'Status changed to {ticket_row[2]}',
                        'performed_by': 'system',
                        'performed_by_name': 'System',
                        'created_at': ticket_row[4].isoformat() + 'Z' if ticket_row[4] else None,
                        'timestamp': ticket_row[4].isoformat() + 'Z' if ticket_row[4] else None
                    })
                
                # Assignment activity (if assigned)
                if ticket_row[3]:  # assigned_to exists
                    agent_result = db.session.execute(text("""
                        SELECT name FROM users WHERE id = :agent_id
                    """), {'agent_id': ticket_row[3]})
                    agent_row = agent_result.fetchone()
                    agent_name = agent_row[0] if agent_row else f'Agent {ticket_row[3]}'
                    
                    activities.append({
                        'id': f'assign_{ticket_id}',
                        'ticket_id': ticket_id,
                        'description': f'Assigned to {agent_name}',
                        'performed_by': 'system',
                        'performed_by_name': 'System',
                        'created_at': ticket_row[4].isoformat() + 'Z' if ticket_row[4] else None,
                        'timestamp': ticket_row[4].isoformat() + 'Z' if ticket_row[4] else None
                    })
            
            # Add any stored activities from memory
            if ticket_id in activity_store:
                activities.extend(activity_store[ticket_id])
            
            # Sort by timestamp
            activities.sort(key=lambda x: x.get('timestamp', x.get('created_at', '')))
            
            return activities
        except Exception as e:
            print(f"Error fetching activities for {ticket_id}: {e}")
            return []
    
    # File upload removed - using frontend Cloudinary integration
    
    # Global message and activity storage per ticket (in production, use database)
    messages_store = {}
    activity_store = {}
    
    # Messages endpoint moved to Flask-RESTful resources
    
    @app.route('/api/alerts/<alert_id>/read', methods=['PUT'])
    def mark_alert_read(alert_id):
        return {'success': True, 'message': 'Alert marked as read'}
    
    @app.route('/api/alerts/<user_id>/read-all', methods=['PUT'])
    def mark_all_alerts_read(user_id):
        return {'success': True, 'message': 'All alerts marked as read'}
    
    @app.route('/api/analytics/ticket-aging')
    def ticket_aging():
        try:
            from sqlalchemy import text
            from datetime import datetime
            
            result = db.session.execute(text("""
                SELECT 
                    id,
                    ticket_id,
                    title,
                    status,
                    priority,
                    category,
                    created_by,
                    assigned_to,
                    created_at,
                    sla_violated,
                    EXTRACT(EPOCH FROM (NOW() - created_at))/3600 as hours_old
                FROM tickets 
                WHERE status != 'Closed'
                ORDER BY created_at DESC
            """))
            
            aging_buckets = {
                '0-24h': [],
                '24-48h': [],
                '48-72h': [],
                '72h+': []
            }
            
            total_hours = 0
            ticket_count = 0
            
            for row in result:
                ticket = {
                    'id': row[0],
                    'ticket_id': row[1],
                    'title': row[2],
                    'status': row[3],
                    'priority': row[4],
                    'category': row[5],
                    'created_by': row[6],
                    'assigned_to': row[7],
                    'created_at': row[8].isoformat() if row[8] else None,
                    'sla_violated': row[9],
                    'hours_old': float(row[10]) if row[10] else 0
                }
                
                hours_old = ticket['hours_old']
                total_hours += hours_old
                ticket_count += 1
                
                if hours_old <= 24:
                    aging_buckets['0-24h'].append(ticket)
                elif hours_old <= 48:
                    aging_buckets['24-48h'].append(ticket)
                elif hours_old <= 72:
                    aging_buckets['48-72h'].append(ticket)
                else:
                    aging_buckets['72h+'].append(ticket)
            
            avg_age = (total_hours / ticket_count) if ticket_count > 0 else 0
            
            return {
                'aging_data': [
                    {'age_range': '0-24h', 'count': len(aging_buckets['0-24h'])},
                    {'age_range': '24-48h', 'count': len(aging_buckets['24-48h'])},
                    {'age_range': '48-72h', 'count': len(aging_buckets['48-72h'])},
                    {'age_range': '72h+', 'count': len(aging_buckets['72h+'])}
                ],
                'buckets': aging_buckets,
                'total_open_tickets': ticket_count,
                'average_age_hours': round(avg_age, 1)
            }
        except Exception as e:
            print(f"Error fetching aging data: {e}")
            return {
                'aging_data': [
                    {'age_range': '0-24h', 'count': 0},
                    {'age_range': '24-48h', 'count': 0},
                    {'age_range': '48-72h', 'count': 0},
                    {'age_range': '72h+', 'count': 0}
                ],
                'buckets': {'0-24h': [], '24-48h': [], '48-72h': [], '72h+': []},
                'total_open_tickets': 0,
                'average_age_hours': 0
            }
    
    @app.route('/api/analytics/sla-violations')
    def sla_violations():
        try:
            from sqlalchemy import text
            
            result = db.session.execute(text("""
                SELECT 
                    id,
                    ticket_id,
                    title,
                    priority,
                    category,
                    status,
                    created_by,
                    assigned_to,
                    created_at,
                    EXTRACT(EPOCH FROM (NOW() - created_at))/3600 as hours_old
                FROM tickets 
                WHERE sla_violated = true AND status != 'Closed'
                ORDER BY created_at ASC
            """))
            
            violations = []
            for row in result:
                violations.append({
                    'id': row[0],
                    'ticket_id': row[1],
                    'title': row[2],
                    'priority': row[3],
                    'category': row[4],
                    'status': row[5],
                    'created_by': row[6],
                    'assigned_to': row[7],
                    'created_at': row[8].isoformat() if row[8] else None,
                    'hours_overdue': round(float(row[9]), 1) if row[9] else 0
                })
            
            return violations
        except Exception as e:
            print(f"Error fetching SLA violations: {e}")
            return []
    
    @app.route('/api/export/tickets/excel')
    def export_tickets():
        try:
            from sqlalchemy import text
            from flask import Response
            
            result = db.session.execute(text("""
                SELECT t.ticket_id, t.title, t.status, t.priority, t.category, 
                       t.created_at, u.name as assigned_name
                FROM tickets t
                LEFT JOIN users u ON t.assigned_to = u.id
                ORDER BY t.created_at DESC
            """))
            
            csv_lines = ['ID,Title,Status,Priority,Category,Created,Assigned']
            for row in result:
                created_date = row[5].strftime('%Y-%m-%d') if row[5] else ''
                assigned_name = row[6] or ''
                csv_lines.append(f'{row[0]},{row[1]},{row[2]},{row[3]},{row[4]},{created_date},{assigned_name}')
            
            csv_data = '\n'.join(csv_lines)
            
            return Response(
                csv_data,
                mimetype='text/csv',
                headers={'Content-Disposition': 'attachment; filename=tickets.csv'}
            )
        except Exception as e:
            print(f"Error exporting tickets: {e}")
            return Response(
                'ID,Title,Status,Priority,Category,Created,Assigned\n',
                mimetype='text/csv',
                headers={'Content-Disposition': 'attachment; filename=tickets.csv'}
            )
    
    # Global ticket storage (in production, use database)
    tickets_store = []
    
    # Global counter for new tickets
    ticket_counter = 5000
    
    # Tickets endpoint moved to Flask-RESTful resources
    
    # Ticket update endpoint moved to Flask-RESTful resources
    
    # Users endpoint moved to Flask-RESTful resources
    
    # User detail endpoint moved to Flask-RESTful resources
    
    @app.route('/api/alerts/<user_id>', methods=['GET', 'OPTIONS'])
    def user_alerts(user_id):
        if request.method == 'OPTIONS':
            return '', 200
        
        try:
            from sqlalchemy import text
            
            result = db.session.execute(text("""
                SELECT a.id, a.title, a.message, a.alert_type, a.is_read, a.created_at, t.ticket_id
                FROM alerts a
                LEFT JOIN tickets t ON a.ticket_id = t.id
                WHERE a.user_id = :user_id
                ORDER BY a.created_at DESC
                LIMIT 20
            """), {'user_id': user_id})
            
            alerts = []
            for row in result:
                alerts.append({
                    'id': row[0],
                    'title': row[1],
                    'message': row[2],
                    'alert_type': row[3],
                    'is_read': row[4],
                    'created_at': row[5].isoformat() + 'Z' if row[5] else None,
                    'ticket_id': row[6]
                })
            
            return alerts
        except Exception as e:
            print(f"Error fetching alerts for user {user_id}: {e}")
            return []
    
    # File download removed - files served directly from Cloudinary
    
    @app.route('/api/sla/realtime-adherence')
    def realtime_sla_adherence():
        try:
            from sqlalchemy import text
            
            # Overall stats
            overall_result = db.session.execute(text("""
                SELECT 
                    COUNT(*) as total_tickets,
                    COUNT(CASE WHEN status IN ('Resolved', 'Closed') AND sla_violated = false THEN 1 END) as closed_met_sla,
                    COUNT(CASE WHEN status IN ('Resolved', 'Closed') AND sla_violated = true THEN 1 END) as closed_violated_sla,
                    COUNT(CASE WHEN status NOT IN ('Resolved', 'Closed') AND sla_violated = true THEN 1 END) as open_violated
                FROM tickets
            """))
            
            overall_row = overall_result.fetchone()
            total = overall_row[0] or 0
            closed_met = overall_row[1] or 0
            closed_violated = overall_row[2] or 0
            open_violated = overall_row[3] or 0
            
            closed_total = closed_met + closed_violated
            adherence_pct = (closed_met / closed_total * 100) if closed_total > 0 else 0
            
            # Priority breakdown
            priority_result = db.session.execute(text("""
                SELECT 
                    priority,
                    COUNT(CASE WHEN status IN ('Resolved', 'Closed') AND sla_violated = false THEN 1 END) as met_sla,
                    COUNT(CASE WHEN status IN ('Resolved', 'Closed') AND sla_violated = true THEN 1 END) as violated_sla,
                    AVG(CASE WHEN status IN ('Resolved', 'Closed') AND resolved_at IS NOT NULL THEN 
                        EXTRACT(EPOCH FROM (resolved_at - created_at))/3600 END) as avg_resolution_hours
                FROM tickets
                WHERE priority IN ('Critical', 'High', 'Medium', 'Low')
                GROUP BY priority
            """))
            
            sla_targets = {'Critical': 4, 'High': 8, 'Medium': 24, 'Low': 72}
            priority_breakdown = {}
            average_resolution_times = {}
            
            for row in priority_result:
                priority = row[0]
                met = row[1] or 0
                violated = row[2] or 0
                avg_hours = row[3] or 0
                total_priority = met + violated
                
                priority_breakdown[priority] = {
                    'met_sla': met,
                    'violated_sla': violated,
                    'adherence_percentage': round((met / total_priority * 100) if total_priority > 0 else 0, 1),
                    'target_hours': sla_targets[priority]
                }
                
                average_resolution_times[priority] = {
                    'average_hours': round(avg_hours, 1),
                    'target_hours': sla_targets[priority],
                    'within_target': avg_hours <= sla_targets[priority]
                }
            
            return {
                'overall': {
                    'total_tickets': total,
                    'closed_met_sla': closed_met,
                    'closed_violated_sla': closed_violated,
                    'closed_adherence_percentage': round(adherence_pct, 1),
                    'open_violated': open_violated,
                    'open_at_risk': 0  # Would need additional logic to calculate
                },
                'priority_breakdown': priority_breakdown,
                'average_resolution_times': average_resolution_times,
                'sla_targets': sla_targets
            }
        except Exception as e:
            print(f"Error fetching SLA adherence: {e}")
            return {
                'overall': {'total_tickets': 0, 'closed_met_sla': 0, 'closed_violated_sla': 0, 'closed_adherence_percentage': 0, 'open_violated': 0, 'open_at_risk': 0},
                'priority_breakdown': {},
                'average_resolution_times': {},
                'sla_targets': {'Critical': 4, 'High': 8, 'Medium': 24, 'Low': 72}
            }
    
    return app