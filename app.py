import os
from app import create_app, db

config_name = os.getenv('FLASK_ENV', 'production')
app = create_app(config_name)

# Routes moved to __init__.py

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)