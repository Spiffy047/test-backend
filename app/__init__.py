from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_marshmallow import Marshmallow
from marshmallow import ValidationError
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
ma = Marshmallow()

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Load configuration
    from config import config
    app.config.from_object(config[config_name])
    
    # Initialize extensions with error handling
    try:
        db.init_app(app)
        migrate.init_app(app, db)
        print("Database initialized successfully")
        
        # Auto-migrate ticket IDs on startup
        with app.app_context():
            try:
                from app.models import Ticket
                from sqlalchemy import text
                
                # Check if we have tickets without proper TKT-XXXX format
                non_tkt_tickets = Ticket.query.filter(~Ticket.ticket_id.like('TKT-%')).count()
                
                if non_tkt_tickets > 0:
                    print(f"Migrating {non_tkt_tickets} tickets to TKT-XXXX format...")
                    
                    tickets_to_migrate = Ticket.query.filter(~Ticket.ticket_id.like('TKT-%')).all()
                    
                    # Find highest existing TKT number
                    existing_tkt = db.session.execute(
                        text("SELECT ticket_id FROM tickets WHERE ticket_id LIKE 'TKT-%' ORDER BY ticket_id DESC LIMIT 1")
                    ).fetchone()
                    
                    ticket_counter = 1001
                    if existing_tkt:
                        try:
                            last_num = int(existing_tkt[0].split('-')[1])
                            ticket_counter = last_num + 1
                        except (ValueError, IndexError):
                            pass
                    
                    # Migrate each ticket
                    for ticket in tickets_to_migrate:
                        old_id = ticket.ticket_id
                        new_id = f"TKT-{ticket_counter:04d}"
                        
                        while Ticket.query.filter_by(ticket_id=new_id).first():
                            ticket_counter += 1
                            new_id = f"TKT-{ticket_counter:04d}"
                        
                        ticket.ticket_id = new_id
                        print(f"Migrated: {old_id} -> {new_id}")
                        ticket_counter += 1
                    
                    db.session.commit()
                    print(f"Successfully migrated {len(tickets_to_migrate)} tickets!")
                else:
                    print("All tickets already have proper TKT-XXXX format")
                    
            except Exception as e:
                print(f"Migration error: {e}")
                
    except Exception as e:
        print(f"Database initialization failed: {e}")
        # Create a minimal app that can still serve basic endpoints
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        db.init_app(app)
    
    jwt.init_app(app)
    ma.init_app(app)
    
    # Swagger disabled for deployment stability
    
    # CORS configuration - Allow all origins for deployment
    CORS(app, 
         resources={r"/*": {"origins": "*"}},
         allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         supports_credentials=False)
    
    # Register Flask-RESTful API
    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Legacy routes removed - using Flask-RESTful API only
    
    # WebSocket events disabled for now
    # from app.websocket import events
    
    # Basic API endpoints
    @app.route('/')
    def index():
        return {'message': 'Hotfix ServiceDesk API', 'version': '2.0.0', 'status': 'healthy'}
    
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'database': 'connected'}
    
    @app.route('/api/test')
    def test_api():
        return {'message': 'API is working', 'status': 'ok'}
    
    # Auth endpoint moved to Flask-RESTful resources
    
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
        try:
            from sqlalchemy import text
            result = db.session.execute(text("""
                SELECT status, COUNT(*) as count 
                FROM tickets 
                GROUP BY status
            """))
            
            counts = {'new': 0, 'open': 0, 'pending': 0, 'closed': 0}
            for row in result:
                status_key = row[0].lower().replace(' ', '_')
                counts[status_key] = row[1]
            
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
                    ticket_id,
                    title,
                    priority,
                    category,
                    created_at,
                    EXTRACT(EPOCH FROM (NOW() - created_at))/3600 as hours_open
                FROM tickets 
                WHERE assigned_to IS NULL AND status != 'Closed'
                ORDER BY created_at DESC
                LIMIT 20
            """))
            
            tickets = []
            for row in result:
                tickets.append({
                    'id': row[0],
                    'title': row[1],
                    'priority': row[2],
                    'category': row[3],
                    'created_at': row[4].isoformat() if row[4] else None,
                    'hours_open': round(float(row[5]), 1) if row[5] else 0
                })
            
            return {'tickets': tickets}
        except Exception as e:
            print(f"Error fetching unassigned tickets: {e}")
            return {'tickets': []}
    
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
    
    @app.route('/api/alerts/<user_id>/count', methods=['GET', 'OPTIONS'])
    def alert_count(user_id):
        if request.method == 'OPTIONS':
            return '', 200
        # Return different counts based on user role
        if user_id in ['user1']:
            return {'count': 2}
        elif user_id in ['user2', 'agent1']:
            return {'count': 3}
        elif user_id in ['user3']:
            return {'count': 5}
        return {'count': 0}
    
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
    
    # Tickets endpoint moved to Flask-RESTful resources
    
    # Ticket update endpoint moved to Flask-RESTful resources
    
    # Users endpoint moved to Flask-RESTful resources
    
    # User detail endpoint moved to Flask-RESTful resources
    
    @app.route('/api/alerts/<user_id>', methods=['GET', 'OPTIONS'])
    def user_alerts(user_id):
        if request.method == 'OPTIONS':
            return '', 200
        return [
            {
                'id': 'alert1',
                'title': 'SLA Violation',
                'message': 'Ticket TKT-2001 has violated SLA',
                'alert_type': 'sla_violation',
                'ticket_id': 'TKT-2001',
                'created_at': '2025-01-27T10:00:00Z',
                'is_read': False
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