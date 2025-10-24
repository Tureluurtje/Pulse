#!/bin/bash
echo "Setting up Pulse Chat Application..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed. Please install Python 3.8+"
    exit 1
fi

# Create virtual environment in project root
python3 -m venv ../venv
source ../venv/bin/activate

# Install dependencies
pip install -r ../requirements.txt

# Install frontend dependencies if package.json exists
if [ -f "../frontend/package.json" ]; then
    echo "Installing frontend dependencies..."
    cd ../frontend
    npm install
    cd ../scripts
fi

echo "Setup complete! Run the application with: ./scripts/run.sh"