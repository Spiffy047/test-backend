#!/bin/bash

echo "=========================================="
echo "IT ServiceDesk Backend Startup"
echo "=========================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Check if database needs initialization
if [ ! -f "servicedesk_dev.db" ]; then
    echo "Database not found. Initializing..."
    export INIT_DB=true
fi

# Start the server
echo "Starting Flask server on http://localhost:5002"
echo "Press Ctrl+C to stop"
echo "=========================================="
python app.py
