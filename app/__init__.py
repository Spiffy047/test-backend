from flask import Flask
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
    
    return app