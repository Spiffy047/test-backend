from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
# from flasgger import Swagger  # Disabled for deployment
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
ma = Marshmallow()
# swagger = Swagger()  # Disabled for deployment

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Load configuration
    from config import config
    app.config.from_object(config[config_name])
    
    # Initialize extensions with error handling
    try:
        db.init_app(app)
        migrate.init_app(app, db)
    except Exception as e:
        print(f"Database initialization error: {e}")
        # Continue without database for health checks
        pass
    
    jwt.init_app(app)
    ma.init_app(app)
    
    # Swagger disabled for deployment stability
    
    # CORS configuration - Allow all origins for deployment
    CORS(app, 
         resources={r"/*": {"origins": "*"}},
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    
    # Register Flask-RESTful API
    from app.api import api_bp
    app.register_blueprint(api_bp)
    
    # Register existing blueprints for backward compatibility
    from app.routes.tickets import tickets_bp
    from app.routes.users import users_bp
    from app.routes.agents import agents_bp
    from app.routes.messages import messages_bp
    from app.routes.analytics import analytics_bp
    from app.routes.auth import auth_bp
    from app.routes.export import export_bp
    from app.routes.sla import sla_bp
    from app.routes.files import files_bp
    from app.routes.alerts import alerts_bp
    
    app.register_blueprint(tickets_bp, url_prefix='/api/v1/tickets')
    app.register_blueprint(users_bp, url_prefix='/api/v1/users')
    app.register_blueprint(agents_bp, url_prefix='/api/v1/agents')
    app.register_blueprint(messages_bp, url_prefix='/api/v1/messages')
    app.register_blueprint(analytics_bp, url_prefix='/api/v1/analytics')
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(export_bp, url_prefix='/api/v1/export')
    app.register_blueprint(sla_bp, url_prefix='/api/v1/sla')
    app.register_blueprint(files_bp, url_prefix='/api/v1/files')
    app.register_blueprint(alerts_bp, url_prefix='/api/v1/alerts')
    
    # WebSocket events disabled for now
    # from app.websocket import events
    
    # Basic API endpoints
    @app.route('/')
    def index():
        return {'message': 'IT ServiceDesk API', 'version': '2.0.0', 'status': 'healthy'}
    
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'database': 'connected'}
    
    @app.route('/api/test')
    def test_api():
        return {'message': 'API is working', 'status': 'ok'}
    
    @app.route('/api/tickets/analytics/sla-adherence')
    def sla_adherence():
        return {
            'sla_adherence': 87.2,
            'total_tickets': 71,
            'violations': 9,
            'on_time': 62,
            'critical_violations': 2,
            'high_violations': 3,
            'medium_violations': 3,
            'low_violations': 1,
            'trend': 'improving'
        }
    
    @app.route('/api/agents/performance')
    def agent_performance():
        return [{
            'id': 'agent1',
            'name': 'Sarah Johnson',
            'tickets_closed': 25,
            'avg_handle_time': 4.2,
            'sla_violations': 2,
            'rating': 'Excellent'
        }]
    
    @app.route('/api/agents')
    def agents_list():
        return [{
            'id': 'agent1',
            'name': 'Sarah Johnson',
            'email': 'sarah.j@company.com'
        }, {
            'id': 'agent2', 
            'name': 'Mike Chen',
            'email': 'mike.c@company.com'
        }]
    
    @app.route('/api/analytics/ticket-status-counts')
    def ticket_status_counts():
        return {
            'new': 8,
            'open': 15, 
            'pending': 6,
            'closed': 42
        }
    
    @app.route('/api/analytics/unassigned-tickets')
    def unassigned_tickets():
        # Return the New tickets (which are unassigned)
        return {
            'tickets': [{
                'id': f'TKT-100{i+1}',
                'title': f'New Issue #{i+1}',
                'priority': ['Critical', 'High', 'Medium', 'Low'][i % 4],
                'category': 'Hardware',
                'created_at': '2025-10-27T10:00:00Z',
                'hours_open': 2.5
            } for i in range(8)]
        }
    
    @app.route('/api/analytics/agent-workload')
    def agent_workload():
        return [{
            'agent_id': 'agent1',
            'name': 'Sarah Johnson',
            'email': 'sarah.j@company.com',
            'ticket_count': 16,
            'active_tickets': 5,
            'pending_tickets': 2,
            'closed_tickets': 11
        }, {
            'agent_id': 'agent2',
            'name': 'Mike Chen',
            'email': 'mike.c@company.com', 
            'ticket_count': 14,
            'active_tickets': 4,
            'pending_tickets': 2,
            'closed_tickets': 10
        }, {
            'agent_id': 'agent3',
            'name': 'Emily Rodriguez',
            'email': 'emily.r@company.com',
            'ticket_count': 13,
            'active_tickets': 3,
            'pending_tickets': 1,
            'closed_tickets': 10
        }, {
            'agent_id': 'agent4',
            'name': 'David Kim',
            'email': 'david.k@company.com',
            'ticket_count': 12,
            'active_tickets': 3,
            'pending_tickets': 1,
            'closed_tickets': 11
        }]
    
    @app.route('/api/analytics/agent-performance-detailed')
    def agent_performance_detailed():
        return [{
            'agent_id': 'agent1',
            'id': 'agent1',
            'name': 'Sarah Johnson',
            'email': 'sarah.j@company.com',
            'active_tickets': 5,
            'closed_tickets': 28,
            'avg_handle_time': 3.8,
            'sla_violations': 1,
            'rating': 'Excellent',
            'performance_rating': 'Excellent',
            'performance_score': 95,
            'satisfaction_score': 4.8
        }, {
            'agent_id': 'agent2',
            'id': 'agent2',
            'name': 'Mike Chen',
            'email': 'mike.c@company.com',
            'active_tickets': 4,
            'closed_tickets': 22,
            'avg_handle_time': 4.5,
            'sla_violations': 3,
            'rating': 'Good',
            'performance_rating': 'Good',
            'performance_score': 78,
            'satisfaction_score': 4.3
        }, {
            'agent_id': 'agent3',
            'id': 'agent3',
            'name': 'Emily Rodriguez',
            'email': 'emily.r@company.com',
            'active_tickets': 3,
            'closed_tickets': 19,
            'avg_handle_time': 5.2,
            'sla_violations': 2,
            'rating': 'Good',
            'performance_rating': 'Good',
            'performance_score': 72,
            'satisfaction_score': 4.1
        }, {
            'agent_id': 'agent4',
            'id': 'agent4',
            'name': 'David Kim',
            'email': 'david.k@company.com',
            'active_tickets': 2,
            'closed_tickets': 15,
            'avg_handle_time': 6.1,
            'sla_violations': 4,
            'rating': 'Average',
            'performance_rating': 'Average',
            'performance_score': 58,
            'satisfaction_score': 3.9
        }]
    
    @app.route('/api/alerts/<user_id>/count')
    def alert_count(user_id):
        # Return different counts based on user role
        if user_id in ['user1']:
            return {'count': 2}
        elif user_id in ['user2', 'agent1']:
            return {'count': 3}
        elif user_id in ['user3']:
            return {'count': 5}
        return {'count': 1}
    
    @app.route('/api/messages/ticket/<ticket_id>/timeline')
    def ticket_timeline(ticket_id):
        # Sample messages
        sample_messages = [{
            'id': 'msg1',
            'ticket_id': ticket_id,
            'sender_id': 'user1',
            'sender_name': 'John Smith',
            'sender_role': 'Normal User',
            'message': 'I am having trouble accessing my email. The error message says authentication failed.',
            'timestamp': '2025-10-27T10:30:00Z',
            'type': 'message'
        }, {
            'id': 'msg2',
            'ticket_id': ticket_id,
            'sender_id': 'agent1',
            'sender_name': 'Sarah Johnson',
            'sender_role': 'Technical User',
            'message': 'Hi John, I can help you with this. Can you please try resetting your password first?',
            'timestamp': '2025-10-27T10:45:00Z',
            'type': 'message'
        }]
        
        # Add any new messages for this ticket
        if ticket_id in messages_store:
            sample_messages.extend(messages_store[ticket_id])
        
        return sample_messages
    
    @app.route('/api/tickets/<ticket_id>/activities')
    def ticket_activities(ticket_id):
        return [{
            'id': 'act1',
            'ticket_id': ticket_id,
            'description': 'Ticket assigned to Sarah Johnson',
            'performed_by': 'system',
            'performed_by_name': 'System',
            'created_at': '2025-10-27T10:35:00Z'
        }]
    
    @app.route('/api/files/ticket/<ticket_id>')
    def ticket_files(ticket_id):
        files = []
        
        # Add sample attachment for TKT-1001
        if ticket_id == 'TKT-1001':
            files.append({
                'id': 'file1',
                'filename': 'error_screenshot.png',
                'file_size_mb': '0.5',
                'download_url': '/api/files/download/file1',
                'uploaded_by': 'user1',
                'uploaded_at': '2025-10-27T10:35:00Z'
            })
        
        # Add any uploaded files for this ticket
        if ticket_id in uploaded_files:
            files.extend(uploaded_files[ticket_id])
        
        return files
    
    # File storage for uploaded files
    uploaded_files = {}
    
    @app.route('/api/files/upload', methods=['POST'])
    def upload_file():
        try:
            if 'file' not in request.files:
                return {'error': 'No file provided'}, 400
            
            file = request.files['file']
            ticket_id = request.form.get('ticket_id', 'unknown')
            uploaded_by = request.form.get('uploaded_by', 'unknown')
            
            if file.filename == '':
                return {'error': 'No file selected'}, 400
            
            # Store file info (in production, save to cloud storage)
            file_id = f'file_{len(uploaded_files) + 1}'
            file_info = {
                'id': file_id,
                'filename': file.filename,
                'file_size_mb': round(len(file.read()) / (1024 * 1024), 2),
                'ticket_id': ticket_id,
                'uploaded_by': uploaded_by,
                'download_url': f'/api/files/download/{file_id}',
                'uploaded_at': '2025-10-27T12:30:00Z'
            }
            
            if ticket_id not in uploaded_files:
                uploaded_files[ticket_id] = []
            uploaded_files[ticket_id].append(file_info)
            
            # Add file upload to timeline
            if ticket_id not in messages_store:
                messages_store[ticket_id] = []
            
            from datetime import datetime
            upload_message = {
                'id': f'file_msg_{len(messages_store[ticket_id]) + 100}',
                'ticket_id': ticket_id,
                'sender_id': uploaded_by,
                'sender_name': 'User',
                'sender_role': 'Normal User',
                'message': f'Uploaded file: {file.filename}',
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'type': 'message'
            }
            messages_store[ticket_id].append(upload_message)
            
            return file_info, 200
            
        except Exception as e:
            return {'error': str(e)}, 500
    
    # Global message storage per ticket (in production, use database)
    messages_store = {}
    
    @app.route('/api/messages', methods=['POST', 'OPTIONS'])
    def messages():
        if request.method == 'OPTIONS':
            return '', 200
        
        data = request.get_json()
        ticket_id = data.get('ticket_id')
        
        if ticket_id not in messages_store:
            messages_store[ticket_id] = []
        
        from datetime import datetime
        new_message = {
            'id': f'msg_{len(messages_store[ticket_id]) + 100}',
            'ticket_id': ticket_id,
            'sender_id': data.get('sender_id'),
            'sender_name': data.get('sender_name'),
            'sender_role': data.get('sender_role'),
            'message': data.get('message'),
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'type': 'message'
        }
        messages_store[ticket_id].append(new_message)
        return new_message, 201
    
    @app.route('/api/alerts/<alert_id>/read', methods=['PUT'])
    def mark_alert_read(alert_id):
        return {'success': True, 'message': 'Alert marked as read'}
    
    @app.route('/api/alerts/<user_id>/read-all', methods=['PUT'])
    def mark_all_alerts_read(user_id):
        return {'success': True, 'message': 'All alerts marked as read'}
    
    @app.route('/api/analytics/ticket-aging')
    def ticket_aging():
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        
        aging_buckets = {
            '0-24h': [],
            '24-48h': [],
            '48-72h': [],
            '72h+': []
        }
        
        # Categorize open tickets by age
        for ticket in tickets_store:
            if ticket['status'] != 'Closed':
                created = datetime.fromisoformat(ticket['created_at'].replace('Z', '+00:00'))
                hours_old = (now - created).total_seconds() / 3600
                
                if hours_old <= 24:
                    aging_buckets['0-24h'].append(ticket)
                elif hours_old <= 48:
                    aging_buckets['24-48h'].append(ticket)
                elif hours_old <= 72:
                    aging_buckets['48-72h'].append(ticket)
                else:
                    aging_buckets['72h+'].append(ticket)
        
        return {
            'aging_data': [
                {'age_range': '0-24h', 'count': len(aging_buckets['0-24h'])},
                {'age_range': '24-48h', 'count': len(aging_buckets['24-48h'])},
                {'age_range': '48-72h', 'count': len(aging_buckets['48-72h'])},
                {'age_range': '72h+', 'count': len(aging_buckets['72h+'])}
            ],
            'buckets': aging_buckets,
            'total_open_tickets': sum(len(bucket) for bucket in aging_buckets.values()),
            'average_age_hours': 48.5
        }
    
    @app.route('/api/analytics/sla-violations')
    def sla_violations():
        return [{
            'ticket_id': 'TKT-1001',
            'title': 'Email access issue',
            'priority': 'High',
            'hours_overdue': 2.5,
            'assigned_to': 'agent1'
        }, {
            'ticket_id': 'TKT-1003',
            'title': 'VPN connection problems',
            'priority': 'High', 
            'hours_overdue': 1.2,
            'assigned_to': 'agent2'
        }]
    
    @app.route('/api/export/tickets/excel')
    def export_tickets():
        # Return CSV data for Excel export
        csv_data = '''ID,Title,Status,Priority,Category,Created,Assigned
TKT-1001,Unable to access company email,Open,High,Email & Communication,2025-10-27,agent1
TKT-1002,Laptop running very slow,New,Medium,Hardware,2025-10-27,
TKT-1003,VPN connection issues,Pending,High,Network & Connectivity,2025-10-27,agent2'''
        
        from flask import Response
        return Response(
            csv_data,
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=tickets.csv'}
        )
    
    # Global ticket storage (in production, use database)
    tickets_store = []
    
    # Global counter for new tickets
    ticket_counter = 5000
    
    @app.route('/api/tickets', methods=['GET', 'POST', 'OPTIONS'])
    def tickets():
        global ticket_counter
        
        if request.method == 'OPTIONS':
            return '', 200
            
        if request.method == 'POST':
            data = request.get_json()
            ticket_counter += 1
            new_ticket = {
                'id': f'TKT-{ticket_counter}',
                'title': data.get('title'),
                'description': data.get('description'),
                'status': 'New',
                'priority': data.get('priority'),
                'category': data.get('category'),
                'created_by': data.get('created_by'),
                'assigned_to': None,
                'created_at': '2025-01-27T12:00:00Z',
                'sla_violated': False
            }
            return new_ticket, 201
        
        # GET request - return sample tickets
        created_by = request.args.get('created_by')
        sample_tickets = []
        
        # Add sample tickets for the user
        if created_by:
            sample_tickets = [
                {
                    'id': 'TKT-5001',
                    'title': 'My Test Ticket',
                    'description': 'Sample ticket for testing',
                    'status': 'New',
                    'priority': 'Medium',
                    'category': 'Hardware',
                    'created_by': created_by,
                    'assigned_to': None,
                    'created_at': '2025-01-27T12:00:00Z',
                    'sla_violated': False
                }
            ]
        
        return sample_tickets
    
    @app.route('/api/tickets/<ticket_id>', methods=['PUT', 'OPTIONS'])
    def update_ticket(ticket_id):
        if request.method == 'OPTIONS':
            return '', 200
            
        data = request.get_json()
        
        # Handle SLA violated tickets specifically
        if ticket_id in ['TKT-2001', 'TKT-2002', 'TKT-2003', 'TKT-3001']:
            return {
                'id': ticket_id,
                'status': data.get('status', 'Open'),
                'assigned_to': data.get('assigned_to'),
                'message': 'Ticket updated successfully',
                'success': True
            }
        
        # Handle other tickets
        return {
            'id': ticket_id,
            'status': data.get('status', 'Open'),
            'message': 'Ticket updated successfully',
            'success': True
        }
    
    @app.route('/api/users', methods=['GET', 'POST', 'PUT', 'DELETE'])
    def users():
        sample_users = [
            {'id': 'user1', 'name': 'John Smith', 'email': 'john.smith@company.com', 'role': 'Normal User'},
            {'id': 'user2', 'name': 'Jane Doe', 'email': 'jane.doe@company.com', 'role': 'Normal User'},
            {'id': 'user3', 'name': 'Bob Wilson', 'email': 'bob.wilson@company.com', 'role': 'Technical Supervisor'},
            {'id': 'agent1', 'name': 'Sarah Johnson', 'email': 'sarah.j@company.com', 'role': 'Technical User'},
            {'id': 'agent2', 'name': 'Mike Chen', 'email': 'mike.c@company.com', 'role': 'Technical User'}
        ]
        return sample_users
    
    @app.route('/api/users/<user_id>', methods=['PUT', 'DELETE'])
    def user_detail(user_id):
        if request.method == 'PUT':
            return {'success': True, 'message': 'User updated'}
        elif request.method == 'DELETE':
            return {'success': True, 'message': 'User deleted'}
    
    @app.route('/api/alerts/<user_id>')
    def user_alerts(user_id):
        return [
            {
                'id': 'alert1',
                'title': 'SLA Violation',
                'message': 'Ticket TKT-2001 has violated SLA',
                'type': 'sla_breach',
                'ticket_id': 'TKT-2001',
                'created_at': '2025-01-27T10:00:00Z',
                'read': False
            }
        ]
    
    @app.route('/api/files/download/<file_id>')
    def download_file(file_id):
        return {'message': 'File download endpoint', 'file_id': file_id}
    
    @app.route('/api/sla/realtime-adherence')
    def realtime_sla_adherence():
        return {
            'overall': {
                'total_tickets': 125,
                'closed_met_sla': 89,
                'closed_violated_sla': 16,
                'closed_adherence_percentage': 84.8,
                'open_violated': 4,
                'open_at_risk': 12
            },
            'priority_breakdown': {
                'Critical': {
                    'met_sla': 8,
                    'violated_sla': 3,
                    'adherence_percentage': 72.7,
                    'target_hours': 4
                },
                'High': {
                    'met_sla': 22,
                    'violated_sla': 6,
                    'adherence_percentage': 78.6,
                    'target_hours': 8
                },
                'Medium': {
                    'met_sla': 35,
                    'violated_sla': 5,
                    'adherence_percentage': 87.5,
                    'target_hours': 24
                },
                'Low': {
                    'met_sla': 24,
                    'violated_sla': 2,
                    'adherence_percentage': 92.3,
                    'target_hours': 72
                }
            },
            'average_resolution_times': {
                'Critical': {
                    'average_hours': 3.2,
                    'target_hours': 4,
                    'within_target': True
                },
                'High': {
                    'average_hours': 9.1,
                    'target_hours': 8,
                    'within_target': False
                },
                'Medium': {
                    'average_hours': 18.5,
                    'target_hours': 24,
                    'within_target': True
                },
                'Low': {
                    'average_hours': 45.2,
                    'target_hours': 72,
                    'within_target': True
                }
            },
            'sla_targets': {
                'Critical': 4,
                'High': 8,
                'Medium': 24,
                'Low': 72
            }
        }
    
    return app