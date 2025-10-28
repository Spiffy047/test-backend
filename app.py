from app import create_app, db
from app.models import User, Ticket, Message
import os

# Set database URL if not set
if not os.environ.get('DATABASE_URL'):
    os.environ['DATABASE_URL'] = 'postgresql://hotfix_user:UlNqxVgaEpb5aDMUKRQ97fZkwPn7LsSB@dpg-d3vie4ndiees73f0rtc0-a.oregon-postgres.render.com/hotfix'

config_name = os.getenv('FLASK_ENV', 'production')
try:
    app = create_app(config_name)
except Exception as e:
    print(f"App creation error: {e}")
    # Create minimal app for health checks
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def health():
        return {'status': 'ok', 'message': 'ServiceDesk API'}

# Routes moved to __init__.py

def init_db():
    """Initialize database tables"""
    try:
        with app.app_context():
            db.create_all()
            print("Database tables created successfully")
    except Exception as e:
        print(f"Database initialization error: {e}")
        # Continue without database for basic health checks

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)