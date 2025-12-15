#!/bin/bash

# Change to project root directory
cd "$(dirname "$0")/.."

# Activate virtual environment
source venv/bin/activate

echo "Starting Pulse Chat Application..."
echo "Backend will run on: http://localhost:8000"
echo "API Docs will be at: http://localhost:8000/docs"
echo "Press Ctrl+C to stop the server"
echo ""

# Start backend
uvicorn asgi_app:app --host 0.0.0.0 --port 8000