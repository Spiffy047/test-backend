#!/bin/bash
# Production startup script for Render
export FLASK_ENV=production
export PYTHONPATH=/opt/render/project/src:$PYTHONPATH

# Try to run database migrations if possible
python -c "from app import create_app, db; app = create_app('production'); app.app_context().push(); db.create_all()" 2>/dev/null || echo "Database setup skipped"

# Start the application with gunicorn
gunicorn --config gunicorn_config.py app:app