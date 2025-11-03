
# Flask application factory for IT ServiceDesk

# Core Flask and database imports
from flask import Flask, request, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_marshmallow import Marshmallow
from marshmallow import ValidationError
from dotenv import load_dotenv
from datetime import datetime
import os
import uuid

# Load environment variables from .env file
load_dotenv()

# Initialize Flask extensions
db = SQLAlchemy()  # Database ORM
migrate = Migrate()  # Database migrations
jwt = JWTManager()  # JWT authentication
ma = Marshmallow()  # Object serialization

def create_app(config_name='default'):
    """Create and configure Flask application"""
    # Create Flask app instance
    app = Flask(__name__)
    
    # Load configuration based on environment
    from config import config
    app.config.from_object(config[config_name])
    # Initialize database with error handling and fallback
    try:
        # Bind database extensions to app
        db.init_app(app)
        migrate.init_app(app, db)
        print("[OK] Database initialized successfully")
        
        # Create database tables and initialize configuration
        with app.app_context():
            try:
                # Create all database tables
                db.create_all()
                print("[OK] Database tables initialized successfully")
                
                # Initialize default configuration data
                try:
                    from app.services.configuration_service import ConfigurationService
                    ConfigurationService.initialize_default_configuration()
                    print("[OK] Configuration tables initialized")
                except Exception as config_error:
                    print(f"[WARNING] Configuration init warning: {config_error}")
            except Exception as e:
                print(f"[WARNING] Database table creation error: {e}")
                
    except Exception as e:
        # Fallback to in-memory SQLite if PostgreSQL fails
        print(f"[ERROR] Database initialization failed: {e}")
        print("[RETRY] Falling back to in-memory SQLite database")
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        db.init_app(app)
    
    # Configure JWT authentication
    app.config['JWT_SECRET_KEY'] = 'hardcoded-jwt-secret-key-for-testing-12345'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Tokens don't expire for development
    
    # Initialize JWT and Marshmallow extensions
    jwt.init_app(app)
    ma.init_app(app)
    
    # JWT error handlers for authentication failures
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {'error': 'Token has expired'}, 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {'error': 'Invalid token'}, 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return {'error': 'Authorization token required'}, 401
    
    
    
    # Configure CORS for React frontend communication
    CORS(app, 
         resources={r"/*": {"origins": "*"}},  # Allow all origins for development
         allow_headers=["Content-Type", "Authorization", "X-Requested-With", "X-CSRF-Token"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         supports_credentials=False  # Disabled for deployment compatibility
    )
    
    # Register API blueprints for modular routing
    
    # Configuration management endpoints
    from app.routes.config import config_bp
    app.register_blueprint(config_bp, url_prefix='/api/config')
    print("[OK] Configuration routes registered")
    
    # Database initialization endpoints
    from app.routes.db_init import db_init_bp
    app.register_blueprint(db_init_bp, url_prefix='/api/db')
    print("[OK] Database init routes registered")
    
    # Main RESTful API endpoints (tickets, users, messages)
    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    print("[OK] RESTful API routes registered")
    
    # Swagger API documentation
    from app.swagger import swagger_bp
    app.register_blueprint(swagger_bp, url_prefix='/api/docs')
    print("[OK] Swagger documentation registered at /api/docs/")
    
    # Administrative endpoints
    from app.routes.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    print("[OK] Admin routes registered")
    
    # Database migration utilities
    from app.routes.migration import migration_bp
    app.register_blueprint(migration_bp, url_prefix='/api/migration')
    print("[OK] Migration routes registered")
    
    # Status workflow management
    from app.routes.status import status_bp
    app.register_blueprint(status_bp, url_prefix='/api/status')
    print("[OK] Status workflow routes registered")
    
    
    # Core API endpoints for system health and testing
    
    @app.route('/')
    def index():
        """API root - returns system status and version info"""
        return {
            'message': 'Hotfix ServiceDesk API', 
            'version': '2.0.0', 
            'status': 'healthy',
            'documentation': 'Contact system administrator for API documentation'
        }
    
    @app.route('/api/test')
    def test_api():
        """Basic connectivity test endpoint"""
        return {
            'message': 'API is working', 
            'status': 'ok',
            'timestamp': datetime.utcnow().isoformat()
        }
    
    @app.route('/api/test/users')
    def test_users():
        """Test database connectivity by fetching sample users"""
        try:
            from app.models import User
            # Get first 5 users to test database connection
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
    
    @app.route('/api/test/tickets')
    def test_tickets():
        """Test ticket data and SLA fields"""
        try:
            from app.models import Ticket
            from sqlalchemy import func
            
            # Get basic counts
            total_tickets = Ticket.query.count()
            sla_true = Ticket.query.filter_by(sla_violated=True).count()
            sla_false = Ticket.query.filter_by(sla_violated=False).count()
            sla_null = Ticket.query.filter(Ticket.sla_violated.is_(None)).count()
            
            # Get sample tickets
            sample_tickets = Ticket.query.limit(5).all()
            samples = []
            for ticket in sample_tickets:
                samples.append({
                    'id': ticket.id,
                    'ticket_id': ticket.ticket_id,
                    'title': ticket.title,
                    'status': ticket.status,
                    'priority': ticket.priority,
                    'sla_violated': ticket.sla_violated,
                    'created_at': ticket.created_at.isoformat() if ticket.created_at else None
                })
            
            return {
                'total_tickets': total_tickets,
                'sla_counts': {
                    'violated': sla_true,
                    'met': sla_false,
                    'null': sla_null
                },
                'sample_tickets': samples
            }
        except Exception as e:
            return {'error': str(e)}
    
    @app.route('/api/test/create-user', methods=['POST'])
    def create_test_user():
        """Create test user for development and testing"""
        try:
            from app.models import User
            
            # Check if test user already exists to avoid duplicates
            existing = User.query.filter_by(email='test@test.com').first()
            if existing:
                return {'message': 'Test user already exists', 'email': 'test@test.com'}
            
            # Create new test user with admin privileges
            user = User(
                name='Test User',
                email='test@test.com',
                role='System Admin'
            )
            user.set_password('test123')
            
            # Save to database
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
    

    
    # Analytics endpoints for dashboard metrics
    
    @app.route('/api/tickets/analytics/sla-adherence')
    def sla_adherence():
        """Calculate SLA adherence percentage from ticket data"""
        try:
            from app.models import Ticket
            from sqlalchemy import func, case
            
            # Debug: Check total tickets first
            total_count = Ticket.query.count()
            print(f"Debug: Total tickets in DB: {total_count}")
            
            if total_count == 0:
                print("Debug: No tickets found")
                return {
                    'sla_adherence': 0,
                    'total_tickets': 0,
                    'violations': 0,
                    'on_time': 0,
                    'trend': 'stable'
                }
            
            # Query SLA statistics with explicit null handling
            result = db.session.query(
                func.count(Ticket.id).label('total_tickets'),
                func.count(case([(Ticket.sla_violated == False, 1)])).label('on_time'),
                func.count(case([(Ticket.sla_violated == True, 1)])).label('violations'),
                func.count(case([(Ticket.sla_violated.is_(None), 1)])).label('null_sla')
            ).first()
            
            # Extract values with null safety
            total_tickets = result.total_tickets or 0
            on_time = result.on_time or 0
            violations = result.violations or 0
            null_sla = result.null_sla or 0
            
            print(f"Debug SLA query: Total={total_tickets}, On-time={on_time}, Violations={violations}, Null={null_sla}")
            
            # Calculate adherence percentage with division by zero protection
            sla_adherence = (on_time / total_tickets * 100) if total_tickets > 0 else 0
            
            return {
                'sla_adherence': round(sla_adherence, 1),
                'total_tickets': total_tickets,
                'violations': violations,
                'on_time': on_time,
                'trend': 'stable',
                'debug': {
                    'null_sla_count': null_sla,
                    'query_total': total_count
                }
            }
        except Exception as e:
            print(f"Error fetching SLA adherence: {e}")
            import traceback
            traceback.print_exc()
            return {
                'sla_adherence': 0,
                'total_tickets': 0,
                'violations': 0,
                'on_time': 0,
                'trend': 'stable',
                'error': str(e)
            }
    
    @app.route('/api/agents/performance')
    def agent_performance():
        """Get performance metrics for all technical agents"""
        try:
            from app.models import User, Ticket
            from sqlalchemy import func, case, extract
            
            result = db.session.query(
                User.id,
                User.name,
                User.email,
                User.role,
                func.coalesce(func.count(case([(Ticket.status.in_(['Resolved', 'Closed']), 1)])), 0).label('tickets_closed'),
                func.coalesce(
                    func.avg(
                        case([
                            ((Ticket.status.in_(['Resolved', 'Closed'])) & (Ticket.resolved_at.isnot(None)),
                             extract('epoch', Ticket.resolved_at - Ticket.created_at) / 3600)
                        ])
                    ), 0
                ).label('avg_handle_time'),
                func.coalesce(func.count(case([(Ticket.sla_violated == True, 1)])), 0).label('sla_violations'),
                func.coalesce(func.count(case([(Ticket.assigned_to == User.id, 1)])), 0).label('total_assigned')
            ).outerjoin(
                Ticket, User.id == Ticket.assigned_to
            ).filter(
                User.role.in_(['Technical User', 'Technical Supervisor'])
            ).group_by(
                User.id, User.name, User.email, User.role
            ).order_by(User.name).all()
            
            agents = []
            for row in result:
                closed = row.tickets_closed or 0
                violations = row.sla_violations or 0
                total_assigned = row.total_assigned or 0
                score = max(0, (closed * 10) - (violations * 5))
                rating = 'Excellent' if score >= 50 else 'Good' if score >= 30 else 'Average' if score >= 15 else 'Needs Improvement'
                
                agents.append({
                    'id': row.id,
                    'name': row.name,
                    'email': row.email,
                    'role': row.role,
                    'tickets_closed': closed,
                    'total_assigned': total_assigned,
                    'avg_handle_time': round(row.avg_handle_time or 0, 1),
                    'sla_violations': violations,
                    'rating': rating
                })
            
            return agents
        except Exception as e:
            print(f"Error fetching agent performance: {e}")
            return []
    
    @app.route('/api/agents')
    def agents_list():
        """Get list of all assignable agents (Technical Users and Supervisors)"""
        try:
            from app.models import User
            
            agents = User.query.filter(
                User.role.in_(['Technical User', 'Technical Supervisor'])
            ).order_by(User.name).all()
            
            return [{
                'id': agent.id,
                'name': agent.name,
                'email': agent.email,
                'role': agent.role
            } for agent in agents]
            
        except Exception as e:
            print(f"Error fetching agents: {e}")
            return []
    
    @app.route('/api/analytics/ticket-status-counts')
    def ticket_status_counts():
        """Get ticket counts grouped by status for dashboard widgets"""
        try:
            from app.models import Ticket
            from sqlalchemy import func
            
            # Query ticket counts by status
            result = db.session.query(
                Ticket.status,
                func.count(Ticket.id).label('count')
            ).group_by(Ticket.status).all()
            
            # Initialize standard status categories (New and Open combined)
            counts = {'open': 0, 'pending': 0, 'closed': 0}
            
            # Map database statuses to standard categories
            for row in result:
                status = row.status.lower()
                if status == 'resolved':
                    counts['closed'] += row.count
                elif status == 'in progress':
                    counts['open'] += row.count
                elif status in ['new', 'open']:
                    counts['open'] += row.count
                elif status == 'pending':
                    counts['pending'] = row.count
                else:
                    # Handle custom statuses by keyword matching
                    if 'close' in status or 'resolve' in status:
                        counts['closed'] += row.count
                    elif 'progress' in status or 'active' in status:
                        counts['open'] += row.count
                    else:
                        counts['open'] += row.count
            
            return counts
        except Exception as e:
            print(f"Error fetching ticket counts: {e}")
            return {'open': 0, 'pending': 0, 'closed': 0}
    
    @app.route('/api/analytics/unassigned-tickets')
    def unassigned_tickets():
        """Get list of tickets that need agent assignment"""
        try:
            from app.models import Ticket
            from datetime import datetime
            
            # Query unassigned open tickets
            tickets_query = Ticket.query.filter(
                Ticket.assigned_to.is_(None),  # No agent assigned
                ~Ticket.status.in_(['Closed', 'Resolved'])  # Still open
            ).order_by(Ticket.created_at.desc()).limit(20).all()
            
            tickets = []
            for ticket in tickets_query:
                # Calculate how long ticket has been open
                if ticket.created_at:
                    hours_open = (datetime.utcnow() - ticket.created_at).total_seconds() / 3600
                else:
                    hours_open = 0
                
                tickets.append({
                    'id': ticket.ticket_id or f'TKT-{ticket.id}',
                    'ticket_id': ticket.ticket_id or f'TKT-{ticket.id}',
                    'title': ticket.title,
                    'priority': ticket.priority,
                    'category': ticket.category,
                    'status': ticket.status,
                    'created_at': ticket.created_at.isoformat() if ticket.created_at else None,
                    'hours_open': round(hours_open, 1)
                })
            
            return {'tickets': tickets}
        except Exception as e:
            print(f"Error fetching unassigned tickets: {e}")
            return {'tickets': []}
    
    @app.route('/api/analytics/agent-workload')
    def agent_workload():
        """Get current workload distribution across all agents"""
        try:
            from app.models import User, Ticket
            from sqlalchemy import func, case
            
            # Query agent workload using ORM with ticket counts by status
            result = db.session.query(
                User.id,
                User.name,
                User.email,
                User.role,
                func.coalesce(func.count(Ticket.id), 0).label('total_tickets'),
                func.coalesce(func.count(case([(~Ticket.status.in_(['Resolved', 'Closed']), 1)])), 0).label('active_tickets'),
                func.coalesce(func.count(case([(Ticket.status == 'Pending', 1)])), 0).label('pending_tickets'),
                func.coalesce(func.count(case([(Ticket.status.in_(['Resolved', 'Closed']), 1)])), 0).label('closed_tickets')
            ).outerjoin(
                Ticket, User.id == Ticket.assigned_to
            ).filter(
                User.role.in_(['Technical User', 'Technical Supervisor'])
            ).group_by(
                User.id, User.name, User.email, User.role
            ).order_by(User.name).all()
            
            # Format response data
            agents = []
            for row in result:
                agents.append({
                    'agent_id': row.id,
                    'id': row.id,
                    'name': row.name,
                    'email': row.email,
                    'role': row.role,
                    'ticket_count': row.total_tickets,
                    'active_tickets': row.active_tickets,
                    'pending_tickets': row.pending_tickets,
                    'closed_tickets': row.closed_tickets
                })
            
            return agents
        except Exception as e:
            print(f"Error fetching agent workload: {e}")
            return []
    
    @app.route('/api/analytics/agent-performance-detailed')
    def agent_performance_detailed():
        """Get detailed performance metrics with ratings and scores"""
        try:
            from app.models import User, Ticket
            from sqlalchemy import func, case, extract
            
            # Get all technical users first
            technical_users = User.query.filter(
                User.role.in_(['Technical User', 'Technical Supervisor'])
            ).all()
            
            agents = []
            for user in technical_users:
                # Count tickets for each user
                active_tickets = Ticket.query.filter(
                    Ticket.assigned_to == user.id,
                    ~Ticket.status.in_(['Resolved', 'Closed'])
                ).count()
                
                closed_tickets = Ticket.query.filter(
                    Ticket.assigned_to == user.id,
                    Ticket.status.in_(['Resolved', 'Closed'])
                ).count()
                
                sla_violations = Ticket.query.filter(
                    Ticket.assigned_to == user.id,
                    Ticket.sla_violated == True
                ).count()
                
                # Calculate average handle time
                resolved_tickets = Ticket.query.filter(
                    Ticket.assigned_to == user.id,
                    Ticket.status.in_(['Resolved', 'Closed']),
                    Ticket.resolved_at.isnot(None)
                ).all()
                
                avg_handle_time = 0
                if resolved_tickets:
                    total_hours = sum([
                        (ticket.resolved_at - ticket.created_at).total_seconds() / 3600
                        for ticket in resolved_tickets
                        if ticket.resolved_at and ticket.created_at
                    ])
                    avg_handle_time = total_hours / len(resolved_tickets) if resolved_tickets else 0
                
                # Performance scoring algorithm
                score = max(0, (closed_tickets * 10) - (sla_violations * 5))
                
                # Rating based on performance score
                if score >= 50:
                    rating = 'Excellent'
                elif score >= 30:
                    rating = 'Good'
                elif score >= 15:
                    rating = 'Average'
                else:
                    rating = 'Needs Improvement'
                
                agents.append({
                    'agent_id': user.id,
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'role': user.role,
                    'active_tickets': active_tickets,
                    'closed_tickets': closed_tickets,
                    'avg_handle_time': round(avg_handle_time, 1),
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
        """Get unread alert count for notification bell"""
        # Handle CORS preflight request
        if request.method == 'OPTIONS':
            return '', 200
        
        try:
            from app.models import Alert
            
            # Count unread alerts for specific user
            count = Alert.query.filter_by(
                user_id=user_id,
                is_read=False
            ).count()
            
            return {'count': count}
        except Exception as e:
            print(f"Error fetching alert count for user {user_id}: {e}")
            return {'count': 0}
    
    @app.route('/api/messages/ticket/<ticket_id>/timeline')
    def ticket_timeline(ticket_id):
        """Get chronological message timeline for a ticket"""
        try:
            from app.models import Ticket, Message, User
            
            # Find ticket by ticket_id (TKT-XXXX format)
            ticket = Ticket.query.filter_by(ticket_id=ticket_id).first()
            if not ticket:
                return []
            
            # Get all messages for this ticket with sender info
            messages_query = db.session.query(
                Message.id,
                Message.message,
                Message.created_at,
                Message.sender_id,
                User.name,
                User.role,
                Message.image_url
            ).outerjoin(
                User, Message.sender_id == User.id
            ).filter(
                Message.ticket_id == ticket.id
            ).order_by(Message.created_at.asc()).all()
            
            # Format messages for frontend
            messages = []
            for row in messages_query:
                messages.append({
                    'id': row.id,
                    'ticket_id': ticket_id,
                    'sender_id': row.sender_id,
                    'sender_name': row.name or 'Unknown User',
                    'sender_role': row.role or 'Normal User',
                    'message': row.message,
                    'image_url': row.image_url,  # Cloudinary file URL
                    'timestamp': row.created_at.isoformat() + 'Z' if row.created_at else None,
                    'type': 'message'
                })
            
            # Include any temporary messages from memory store
            if ticket_id in messages_store:
                messages.extend(messages_store[ticket_id])
            
            return messages
        except Exception as e:
            print(f"Error fetching timeline for {ticket_id}: {e}")
            return []
    
    @app.route('/api/tickets/<ticket_id>/activities')
    def ticket_activities(ticket_id):
        """Get activity log for a ticket (creation, status changes, assignments)"""
        try:
            from app.models import Ticket, User
            
            activities = []
            
            # Find ticket by ID or ticket_id
            ticket = None
            if ticket_id.isdigit():
                ticket = Ticket.query.get(int(ticket_id))
            if not ticket:
                ticket = Ticket.query.filter_by(ticket_id=ticket_id).first()
            
            if ticket:
                # Get ticket creator information
                creator = User.query.get(ticket.created_by) if ticket.created_by else None
                creator_name = creator.name if creator else "Unknown User"
                
                # Add ticket creation activity
                activities.append({
                    'id': f'create_{ticket_id}',
                    'ticket_id': ticket_id,
                    'description': f'Ticket created by {creator_name}',
                    'performed_by': 'system',
                    'performed_by_name': 'System',
                    'created_at': ticket.created_at.isoformat() + 'Z' if ticket.created_at else None,
                    'timestamp': ticket.created_at.isoformat() + 'Z' if ticket.created_at else None
                })
                
                # Add status change activity if ticket was updated
                if ticket.updated_at and ticket.updated_at != ticket.created_at:
                    activities.append({
                        'id': f'status_{ticket_id}',
                        'ticket_id': ticket_id,
                        'description': f'Status changed to {ticket.status}',
                        'performed_by': 'system',
                        'performed_by_name': 'System',
                        'created_at': ticket.updated_at.isoformat() + 'Z' if ticket.updated_at else None,
                        'timestamp': ticket.updated_at.isoformat() + 'Z' if ticket.updated_at else None
                    })
                
                # Add assignment activity if ticket is assigned
                if ticket.assigned_to:
                    agent = User.query.get(ticket.assigned_to)
                    agent_name = agent.name if agent else f'Agent {ticket.assigned_to}'
                    
                    activities.append({
                        'id': f'assign_{ticket_id}',
                        'ticket_id': ticket_id,
                        'description': f'Assigned to {agent_name}',
                        'performed_by': 'system',
                        'performed_by_name': 'System',
                        'created_at': ticket.updated_at.isoformat() + 'Z' if ticket.updated_at else None,
                        'timestamp': ticket.updated_at.isoformat() + 'Z' if ticket.updated_at else None
                    })
            
            # Include any temporary activities from memory store
            if ticket_id in activity_store:
                activities.extend(activity_store[ticket_id])
            
            # Sort activities chronologically
            activities.sort(key=lambda x: x.get('timestamp', x.get('created_at', '')))
            
            return activities
        except Exception as e:
            print(f"Error fetching activities for {ticket_id}: {e}")
            return []
    
    # In-memory storage for development (production should use database)
    messages_store = {}  # Temporary message storage per ticket
    activity_store = {}  # Temporary activity log storage per ticket
    
    @app.route('/api/alerts/<alert_id>/read', methods=['PUT'])
    def mark_alert_read(alert_id):
        """Mark specific alert as read (placeholder implementation)"""
        return {'success': True, 'message': 'Alert marked as read'}
    
    @app.route('/api/alerts/<user_id>/read-all', methods=['PUT'])
    def mark_all_alerts_read(user_id):
        """Mark all user alerts as read (placeholder implementation)"""
        return {'success': True, 'message': 'All alerts marked as read'}
    
    @app.route('/api/analytics/ticket-aging')
    def ticket_aging():
        """Analyze ticket aging patterns by time buckets"""
        try:
            from app.models import Ticket
            from datetime import datetime
            
            # Get all open tickets
            tickets = Ticket.query.filter(
                Ticket.status != 'Closed'
            ).order_by(Ticket.created_at.desc()).all()
            
            # Initialize aging buckets
            aging_buckets = {
                '0-24h': [],
                '24-48h': [],
                '48-72h': [],
                '72h+': []
            }
            
            total_hours = 0
            ticket_count = 0
            
            # Categorize tickets by age
            for ticket in tickets:
                # Calculate ticket age in hours
                if ticket.created_at:
                    hours_old = (datetime.utcnow() - ticket.created_at).total_seconds() / 3600
                else:
                    hours_old = 0
                
                # Create ticket data object
                ticket_data = {
                    'id': ticket.id,
                    'ticket_id': ticket.ticket_id,
                    'title': ticket.title,
                    'status': ticket.status,
                    'priority': ticket.priority,
                    'category': ticket.category,
                    'created_by': ticket.created_by,
                    'assigned_to': ticket.assigned_to,
                    'created_at': ticket.created_at.isoformat() if ticket.created_at else None,
                    'sla_violated': ticket.sla_violated,
                    'hours_old': hours_old
                }
                
                # Update totals for average calculation
                total_hours += hours_old
                ticket_count += 1
                
                # Sort into appropriate aging bucket
                if hours_old <= 24:
                    aging_buckets['0-24h'].append(ticket_data)
                elif hours_old <= 48:
                    aging_buckets['24-48h'].append(ticket_data)
                elif hours_old <= 72:
                    aging_buckets['48-72h'].append(ticket_data)
                else:
                    aging_buckets['72h+'].append(ticket_data)
            
            # Calculate average age
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
            # Return empty structure on error
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
        """Get list of tickets that have violated SLA targets"""
        try:
            from app.models import Ticket
            from datetime import datetime
            
            # Query tickets with SLA violations that are still open
            tickets = Ticket.query.filter(
                Ticket.sla_violated == True,
                Ticket.status != 'Closed'
            ).order_by(Ticket.created_at.asc()).all()
            
            violations = []
            for ticket in tickets:
                # Calculate how many hours overdue
                if ticket.created_at:
                    hours_overdue = (datetime.utcnow() - ticket.created_at).total_seconds() / 3600
                else:
                    hours_overdue = 0
                
                violations.append({
                    'id': ticket.id,
                    'ticket_id': ticket.ticket_id,
                    'title': ticket.title,
                    'priority': ticket.priority,
                    'category': ticket.category,
                    'status': ticket.status,
                    'created_by': ticket.created_by,
                    'assigned_to': ticket.assigned_to,
                    'created_at': ticket.created_at.isoformat() if ticket.created_at else None,
                    'hours_overdue': round(hours_overdue, 1)
                })
            
            return violations
        except Exception as e:
            print(f"Error fetching SLA violations: {e}")
            return []
    
    @app.route('/api/export/tickets/excel')
    def export_tickets():
        """Export all tickets to CSV format for download"""
        try:
            from app.models import Ticket, User
            from flask import Response
            
            # Query all tickets with assigned agent names
            tickets_query = db.session.query(
                Ticket.ticket_id,
                Ticket.title,
                Ticket.status,
                Ticket.priority,
                Ticket.category,
                Ticket.created_at,
                User.name.label('assigned_name')
            ).outerjoin(
                User, Ticket.assigned_to == User.id
            ).order_by(Ticket.created_at.desc()).all()
            
            # Build CSV content
            csv_lines = ['ID,Title,Status,Priority,Category,Created,Assigned']
            for row in tickets_query:
                created_date = row.created_at.strftime('%Y-%m-%d') if row.created_at else ''
                assigned_name = row.assigned_name or ''
                csv_lines.append(f'{row.ticket_id},{row.title},{row.status},{row.priority},{row.category},{created_date},{assigned_name}')
            
            csv_data = '\n'.join(csv_lines)
            
            # Return CSV file as download
            return Response(
                csv_data,
                mimetype='text/csv',
                headers={'Content-Disposition': 'attachment; filename=tickets.csv'}
            )
        except Exception as e:
            print(f"Error exporting tickets: {e}")
            # Return empty CSV on error
            return Response(
                'ID,Title,Status,Priority,Category,Created,Assigned\n',
                mimetype='text/csv',
                headers={'Content-Disposition': 'attachment; filename=tickets.csv'}
            )
    
    # Development storage (production uses database)
    tickets_store = []  # Temporary ticket storage
    ticket_counter = 5000  # Counter for generating ticket IDs
    
    @app.route('/api/alerts/<user_id>', methods=['GET', 'OPTIONS'])
    def user_alerts(user_id):
        """Get all alerts for a specific user with ticket information"""
        # Handle CORS preflight request
        if request.method == 'OPTIONS':
            return '', 200
        
        try:
            from app.models import Alert, Ticket
            
            # Query user alerts with related ticket info
            alerts_query = db.session.query(
                Alert.id,
                Alert.title,
                Alert.message,
                Alert.alert_type,
                Alert.is_read,
                Alert.created_at,
                Ticket.ticket_id
            ).outerjoin(
                Ticket, Alert.ticket_id == Ticket.id
            ).filter(
                Alert.user_id == user_id
            ).order_by(
                Alert.created_at.desc()
            ).limit(20).all()  # Limit to most recent 20 alerts
            
            # Format alerts for frontend
            alerts = []
            for row in alerts_query:
                alerts.append({
                    'id': row.id,
                    'title': row.title,
                    'message': row.message,
                    'alert_type': row.alert_type,
                    'is_read': row.is_read,
                    'created_at': row.created_at.isoformat() + 'Z' if row.created_at else None,
                    'ticket_id': row.ticket_id
                })
            
            return alerts
        except Exception as e:
            print(f"Error fetching alerts for user {user_id}: {e}")
            return []
    

    
    @app.route('/api/sla/realtime-adherence')
    def realtime_sla_adherence():
        """Comprehensive SLA adherence analysis with priority breakdown"""
        try:
            from app.models import Ticket
            from sqlalchemy import func, case, extract
            
            # Debug: Check total tickets
            total_count = Ticket.query.count()
            print(f"Debug realtime SLA: Total tickets: {total_count}")
            
            if total_count == 0:
                return {
                    'overall': {'total_tickets': 0, 'closed_met_sla': 0, 'closed_violated_sla': 0, 'closed_adherence_percentage': 0, 'open_violated': 0, 'open_at_risk': 0},
                    'priority_breakdown': {},
                    'average_resolution_times': {},
                    'sla_targets': {'Critical': 4, 'High': 8, 'Medium': 24, 'Low': 72}
                }
            
            # Calculate overall SLA statistics with null handling
            overall_result = db.session.query(
                func.count(Ticket.id).label('total_tickets'),
                func.count(case([
                    ((Ticket.status.in_(['Resolved', 'Closed'])) & (Ticket.sla_violated == False), 1)
                ])).label('closed_met_sla'),
                func.count(case([
                    ((Ticket.status.in_(['Resolved', 'Closed'])) & (Ticket.sla_violated == True), 1)
                ])).label('closed_violated_sla'),
                func.count(case([
                    ((~Ticket.status.in_(['Resolved', 'Closed'])) & (Ticket.sla_violated == True), 1)
                ])).label('open_violated'),
                func.count(case([(Ticket.sla_violated.is_(None), 1)])).label('null_sla')
            ).first()
            
            # Extract overall metrics
            total = overall_result.total_tickets or 0
            closed_met = overall_result.closed_met_sla or 0
            closed_violated = overall_result.closed_violated_sla or 0
            open_violated = overall_result.open_violated or 0
            null_sla = overall_result.null_sla or 0
            
            print(f"Debug SLA breakdown: Total={total}, Met={closed_met}, Violated={closed_violated}, Open_violated={open_violated}, Null={null_sla}")
            
            # Calculate overall adherence percentage
            closed_total = closed_met + closed_violated
            adherence_pct = (closed_met / closed_total * 100) if closed_total > 0 else 0
            
            # Get SLA breakdown by priority level
            priority_result = db.session.query(
                Ticket.priority,
                func.count(case([
                    ((Ticket.status.in_(['Resolved', 'Closed'])) & (Ticket.sla_violated == False), 1)
                ])).label('met_sla'),
                func.count(case([
                    ((Ticket.status.in_(['Resolved', 'Closed'])) & (Ticket.sla_violated == True), 1)
                ])).label('violated_sla'),
                func.avg(
                    case([
                        ((Ticket.status.in_(['Resolved', 'Closed'])) & (Ticket.resolved_at.isnot(None)),
                         extract('epoch', Ticket.resolved_at - Ticket.created_at) / 3600)
                    ])
                ).label('avg_resolution_hours')
            ).filter(
                Ticket.priority.in_(['Critical', 'High', 'Medium', 'Low'])
            ).group_by(Ticket.priority).all()
            
            # SLA target hours by priority
            sla_targets = {'Critical': 4, 'High': 8, 'Medium': 24, 'Low': 72}
            priority_breakdown = {}
            average_resolution_times = {}
            
            # Process priority-specific metrics
            for row in priority_result:
                priority = row.priority
                met = row.met_sla or 0
                violated = row.violated_sla or 0
                avg_hours = row.avg_resolution_hours or 0
                total_priority = met + violated
                
                # Priority-specific adherence
                priority_breakdown[priority] = {
                    'met_sla': met,
                    'violated_sla': violated,
                    'adherence_percentage': round((met / total_priority * 100) if total_priority > 0 else 0, 1),
                    'target_hours': sla_targets.get(priority, 24)
                }
                
                # Average resolution time analysis
                average_resolution_times[priority] = {
                    'average_hours': round(avg_hours, 1),
                    'target_hours': sla_targets.get(priority, 24),
                    'within_target': avg_hours <= sla_targets.get(priority, 24)
                }
            
            return {
                'overall': {
                    'total_tickets': total,
                    'closed_met_sla': closed_met,
                    'closed_violated_sla': closed_violated,
                    'closed_adherence_percentage': round(adherence_pct, 1),
                    'open_violated': open_violated,
                    'open_at_risk': 0  # Placeholder for future enhancement
                },
                'priority_breakdown': priority_breakdown,
                'average_resolution_times': average_resolution_times,
                'sla_targets': sla_targets
            }
        except Exception as e:
            print(f"Error fetching SLA adherence: {e}")
            import traceback
            traceback.print_exc()
            # Return empty structure on error
            return {
                'overall': {'total_tickets': 0, 'closed_met_sla': 0, 'closed_violated_sla': 0, 'closed_adherence_percentage': 0, 'open_violated': 0, 'open_at_risk': 0},
                'priority_breakdown': {},
                'average_resolution_times': {},
                'sla_targets': {'Critical': 4, 'High': 8, 'Medium': 24, 'Low': 72},
                'error': str(e)
            }
    
    # Return configured Flask application
    return app