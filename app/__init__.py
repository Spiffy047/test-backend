from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flasgger import Swagger
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
ma = Marshmallow()
swagger = Swagger()

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
    
    # Initialize Swagger
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs/"
    }
    
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "IT ServiceDesk API",
            "description": "RESTful API for IT ServiceDesk Platform",
            "version": "2.0.0"
        },
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme. Example: 'Bearer {token}'"
            }
        },
        "security": [
            {"Bearer": []}
        ]
    }
    
    swagger.init_app(app, config=swagger_config, template=swagger_template)
    
    # CORS configuration - Allow Netlify frontend
    cors_origins = os.environ.get('CORS_ORIGINS', 'https://hotfixsdm.netlify.app,http://localhost:5173').split(',')
    CORS(app, 
         resources={r"/api/*": {"origins": cors_origins}},
         supports_credentials=True,
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
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'version': '2.0.0'}
    
    return app