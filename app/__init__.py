# IT ServiceDesk Flask Application Factory
# This module creates and configures the main Flask application with all necessary extensions,
# routes, and middleware for the IT ServiceDesk system.

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
    """Flask application factory pattern
    
    Creates and configures a Flask application instance with all necessary
    extensions, blueprints, and middleware.
    
    Args:
        config_name (str): Configuration environment ('default', 'development', 'production')
    
    Returns:
        Flask: Configured Flask application instance
    """
    # Create Flask application instance
    app = Flask(__name__)
    
    # === CONFIGURATION LOADING ===
    # Load configuration based on environment
    from config import config
    app.config.from_object(config[config_name])
    
    # === DATABASE INITIALIZATION ===
    # Initialize database with error handling and fallback
    try:
        # Bind SQLAlchemy and Flask-Migrate to app
        db.init_app(app)
        migrate.init_app(app, db)
        print("✅ Database initialized successfully")
        
        # Create database tables if they don't exist
        with app.app_context():
            try:
                db.create_all()
                print("✅ Database tables initialized successfully")
                print("💡 To seed database with sample data, run: python init_postgres_db.py")
            except Exception as e:
                print(f"⚠️ Database table creation error: {e}")
                
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        # Fallback to in-memory SQLite for basic functionality
        print("🔄 Falling back to in-memory SQLite database")
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        db.init_app(app)
    
    # === EXTENSION INITIALIZATION ===
    # Initialize remaining Flask extensions
    jwt.init_app(app)  # JWT authentication (currently disabled for deployment)
    ma.init_app(app)   # Marshmallow serialization
    
    # Note: Swagger/OpenAPI documentation disabled for deployment stability
    
    # === CORS CONFIGURATION ===
    # Configure Cross-Origin Resource Sharing for frontend integration
    # WARNING: Allowing all origins (*) is not recommended for production
    # TODO: Restrict origins to specific frontend domains in production
    CORS(app, 
         resources={r"/*": {"origins": "*"}},  # Allow all origins (dev only)
         allow_headers=["Content-Type", "Authorization", "X-Requested-With", "X-CSRF-Token"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         supports_credentials=False  # Disabled for deployment compatibility
    )
    
    # === BLUEPRINT REGISTRATION ===
    # Register all route blueprints with appropriate URL prefixes
    
    # Register Swagger documentation
    from app.swagger import swagger_bp
    app.register_blueprint(swagger_bp, url_prefix='/api')
    print("✅ Swagger documentation registered at /api/docs/")
    
    # Main RESTful API endpoints (tickets, users, etc.)
    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    print("✅ RESTful API routes registered")
    
    # Administrative endpoints (system management)
    from app.routes.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    print(" Admin routes registered")
    
    # File upload/download endpoints (with fallback to built-in)
    try:
        from app.routes.files import files_bp
        app.register_blueprint(files_bp, url_prefix='/api/files')
        print(" Files routes registered successfully")
    except ImportError:
        print(" Files routes not found, using built-in file endpoints")
    
    # Note: Legacy routes removed - using Flask-RESTful API architecture
    # Note: WebSocket events disabled for deployment stability
    
    # === BASIC API ENDPOINTS ===
    # Core system endpoints for health checks and API information
    
    @app.route('/')
    def index():
        """API root endpoint - returns basic system information"""
        return {
            'message': 'IT ServiceDesk API', 
            'version': '2.0.0', 
            'status': 'healthy',
            'documentation': 'Contact system administrator for API documentation'
        }
    
    @app.route('/health')
    def health_check():
        """Health check endpoint for monitoring and load balancers"""
        return {
            'status': 'healthy', 
            'database': 'connected',
            'timestamp': datetime.utcnow().isoformat()
        }
    
    @app.route('/api/test')
    def test_api():
        """Simple API test endpoint for connectivity verification"""
        return {
            'message': 'API is working', 
            'status': 'ok',
            'timestamp': datetime.utcnow().isoformat()
        }
    

    
    # Note: Authentication endpoints moved to Flask-RESTful resources
    
    # === ANALYTICS ENDPOINTS ===
    # These endpoints provide real-time analytics data for dashboards
    # Note: Analytics endpoints provide real-time data for dashboards
    
    @app.route('/api/tickets/analytics/sla-adherence')
    def sla_adherence():
        """Calculate SLA adherence metrics from database
        
        Returns:
            JSON object with SLA statistics:
            - sla_adherence: Percentage of tickets meeting SLA
            - total_tickets: Total number of tickets
            - violations: Number of SLA violations
            - on_time: Number of tickets resolved within SLA
            - trend: SLA trend indicator
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
        """Get basic agent performance metrics from database"""
        try:
            from sqlalchemy import text
            
            result = db.session.execute(text("""
                SELECT 
                    u.id, u.name, u.email,
                    COUNT(CASE WHEN t.status IN ('Resolved', 'Closed') THEN 1 END) as tickets_closed,
                    AVG(CASE WHEN t.status IN ('Resolved', 'Closed') AND t.resolved_at IS NOT NULL THEN 
                        EXTRACT(EPOCH FROM (t.resolved_at - t.created_at))/3600 END) as avg_handle_time,
                    COUNT(CASE WHEN t.sla_violated = true THEN 1 END) as sla_violations
                FROM users u
                LEFT JOIN tickets t ON u.id = t.assigned_to
                WHERE u.role IN ('Technical User', 'Technical Supervisor')
                GROUP BY u.id, u.name, u.email
            """))
            
            agents = []
            for row in result:
                closed = row[3] or 0
                violations = row[5] or 0
                score = max(0, (closed * 10) - (violations * 5))
                rating = 'Excellent' if score >= 50 else 'Good' if score >= 30 else 'Average' if score >= 15 else 'Needs Improvement'
                
                agents.append({
                    'id': row[0],
                    'name': row[1],
                    'tickets_closed': closed,
                    'avg_handle_time': round(row[4] or 0, 1),
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
                    t.assigned_to,
                    u.name,
                    u.email,
                    COUNT(*) as total_tickets,
                    COUNT(CASE WHEN t.status NOT IN ('Resolved', 'Closed') THEN 1 END) as active_tickets,
                    COUNT(CASE WHEN t.status = 'Pending' THEN 1 END) as pending_tickets,
                    COUNT(CASE WHEN t.status IN ('Resolved', 'Closed') THEN 1 END) as closed_tickets
                FROM tickets t
                LEFT JOIN users u ON t.assigned_to = u.id
                WHERE t.assigned_to IS NOT NULL
                GROUP BY t.assigned_to, u.name, u.email
            """))
            
            agents = []
            for row in result:
                agents.append({
                    'agent_id': row[0],
                    'name': row[1] or f'Agent {row[0]}',
                    'email': row[2] or f'agent{row[0]}@company.com',
                    'ticket_count': row[3],
                    'active_tickets': row[4],
                    'pending_tickets': row[5],
                    'closed_tickets': row[6]
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
                    t.assigned_to,
                    u.name,
                    u.email,
                    COUNT(CASE WHEN t.status NOT IN ('Resolved', 'Closed') THEN 1 END) as active_tickets,
                    COUNT(CASE WHEN t.status IN ('Resolved', 'Closed') THEN 1 END) as closed_tickets,
                    COUNT(CASE WHEN t.sla_violated = true THEN 1 END) as sla_violations,
                    AVG(CASE WHEN t.status IN ('Resolved', 'Closed') THEN 
                        EXTRACT(EPOCH FROM (t.updated_at - t.created_at))/3600 END) as avg_handle_time
                FROM tickets t
                LEFT JOIN users u ON t.assigned_to = u.id
                WHERE t.assigned_to IS NOT NULL
                GROUP BY t.assigned_to, u.name, u.email
            """))
            
            agents = []
            for row in result:
                closed_tickets = row[4] or 0
                sla_violations = row[5] or 0
                score = max(0, (closed_tickets * 10) - (sla_violations * 5))
                rating = 'Excellent' if score >= 50 else 'Good' if score >= 30 else 'Average' if score >= 15 else 'Needs Improvement'
                
                agents.append({
                    'agent_id': row[0],
                    'id': row[0],
                    'name': row[1] or f'Agent {row[0]}',
                    'email': row[2] or f'agent{row[0]}@company.com',
                    'active_tickets': row[3] or 0,
                    'closed_tickets': closed_tickets,
                    'avg_handle_time': round(row[6] or 0, 1),
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
                SELECT m.id, m.message, m.created_at, m.sender_id, u.name, u.role
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
            
            # Get ticket creation activity
            ticket_result = db.session.execute(text("""
                SELECT t.created_at, u.name as creator_name
                FROM tickets t
                LEFT JOIN users u ON t.created_by = u.id
                WHERE t.ticket_id = :ticket_id OR t.id = :ticket_id
            """), {'ticket_id': ticket_id})
            
            activities = []
            ticket_row = ticket_result.fetchone()
            if ticket_row:
                activities.append({
                    'id': f'create_{ticket_id}',
                    'ticket_id': ticket_id,
                    'description': f'Ticket created by {ticket_row[1] or "Unknown User"}',
                    'performed_by': 'system',
                    'performed_by_name': 'System',
                    'created_at': ticket_row[0].isoformat() + 'Z' if ticket_row[0] else None
                })
            
            return activities
        except Exception as e:
            print(f"Error fetching activities for {ticket_id}: {e}")
            return []
    
    @app.route('/api/files/ticket/<ticket_id>')
    def ticket_files(ticket_id):
        files = []
        
        # Add any uploaded files for this ticket from memory store
        if ticket_id in uploaded_files:
            files.extend(uploaded_files[ticket_id])
        
        return files
    
    # File storage for uploaded files
    uploaded_files = {}
    
    @app.route('/api/files/upload', methods=['POST', 'OPTIONS'])
    def upload_file():
        if request.method == 'OPTIONS':
            return '', 200
            
        try:
            if 'file' not in request.files:
                return {'error': 'No image provided'}, 400
            
            file = request.files['file']
            ticket_id = request.form.get('ticket_id')
            uploaded_by = request.form.get('uploaded_by')
            
            if not ticket_id or not uploaded_by:
                return {'error': 'Missing ticket_id or uploaded_by'}, 400
            
            if file.filename == '':
                return {'error': 'No file selected'}, 400
            
            # Validate file type
            allowed_extensions = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'zip', 'log'}
            if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
                return {'error': 'File type not allowed'}, 400
            
            # Read file content for size calculation
            file_content = file.read()
            file_size = len(file_content)
            
            # Check file size (10MB limit)
            if file_size > 10 * 1024 * 1024:
                return {'error': 'File too large (max 10MB)'}, 400
            
            # Reset file pointer
            file.seek(0)
            
            # Store file info in memory (in production, save to cloud storage)
            import uuid
            file_id = str(uuid.uuid4())
            file_info = {
                'id': file_id,
                'filename': file.filename,
                'file_size_mb': round(file_size / (1024 * 1024), 2),
                'ticket_id': ticket_id,
                'uploaded_by': uploaded_by,
                'download_url': f'/api/files/download/{file_id}',
                'uploaded_at': datetime.utcnow().isoformat() + 'Z',
                'content': file_content  # Store content in memory for demo
            }
            
            if ticket_id not in uploaded_files:
                uploaded_files[ticket_id] = []
            uploaded_files[ticket_id].append(file_info)
            
            # Add file upload to timeline
            if ticket_id not in messages_store:
                messages_store[ticket_id] = []
            
            upload_message = {
                'id': f'file_msg_{len(messages_store[ticket_id]) + 100}',
                'ticket_id': ticket_id,
                'sender_id': uploaded_by,
                'sender_name': 'User',
                'sender_role': 'Normal User',
                'message': f'Uploaded file: {file.filename} ({file_info["file_size_mb"]} MB)',
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'type': 'file_upload'
            }
            messages_store[ticket_id].append(upload_message)
            
            return {
                'id': file_info['id'],
                'filename': file_info['filename'],
                'file_size_mb': file_info['file_size_mb'],
                'uploaded_at': file_info['uploaded_at']
            }, 200
            
        except Exception as e:
            print(f"File upload error: {e}")
            return {'error': str(e)}, 500
    
    # Global message storage per ticket (in production, use database)
    messages_store = {}
    
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
    
    @app.route('/api/files/download/<file_id>')
    def download_file(file_id):
        # Find file in uploaded_files
        for ticket_id, files in uploaded_files.items():
            for file_info in files:
                if file_info['id'] == file_id:
                    # Return file content (in production, stream from cloud storage)
                    return Response(
                        file_info.get('content', b'File content not available'),
                        mimetype='application/octet-stream',
                        headers={
                            'Content-Disposition': f'attachment; filename="{file_info["filename"]}"'
                        }
                    )
        return {'error': 'File not found'}, 404
    
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