#!/bin/bash

# Configuration
PORT=8888
LOG_FILE="app.log"
NO_BROWSER=false
CONDA_ENV="invoice_generator"

# Process simple arguments
if [ "$1" = "--help" ]; then
    echo "Usage: ./run.sh [port] [--no-browser]"
    echo "  port         Specify the port (default: 8888)"
    echo "  --no-browser Don't open the browser automatically"
    exit 0
fi

# If a number is provided as the first argument, use it as the port
if [[ $1 =~ ^[0-9]+$ ]]; then
    PORT=$1
    shift
fi

# Option to not open the browser
if [ "$1" = "--no-browser" ]; then
    NO_BROWSER=true
fi

# Simple function to display errors
show_error() {
    echo "ERROR: $1"
    echo "Check the log file: $LOG_FILE"
    exit 1
}

# Function to clean up on exit
cleanup() {
    echo "Shutting down the application..."
    # Find and terminate the Flask process
    PID=$(lsof -i:$PORT -t)
    if [ ! -z "$PID" ]; then
        kill $PID 2>/dev/null
    fi
    exit 0
}

# Set up trap to handle Ctrl+C and other termination signals
trap cleanup SIGINT SIGTERM EXIT

# Activate conda environment if it exists
if conda info --envs | grep -q "$CONDA_ENV"; then
    echo "Activating conda environment $CONDA_ENV..."
    eval "$(conda shell.bash hook)"
    conda activate "$CONDA_ENV"
else
    echo "Warning: Conda environment $CONDA_ENV not found"
    echo "Creating conda environment from environment.yml..."
    if [ -f "environment.yml" ]; then
        mamba env create -f environment.yml
        eval "$(conda shell.bash hook)"
        conda activate "$CONDA_ENV"
    else
        echo "Error: environment.yml not found"
        exit 1
    fi
fi

# Check if Flask is installed
if ! python -c "import flask" &>/dev/null; then
    echo "Flask is not installed in the conda environment."
    echo "Please check the environment.yml file and recreate the environment:"
    echo "mamba env create -f environment.yml --force"
    exit 1
fi

# Start the Flask application in the background
echo "Starting Flask application on port $PORT..."
python app.py > "$LOG_FILE" 2>&1 &

# Check if the application started correctly
echo "Waiting for the application to start..."
for i in {1..10}; do
    if lsof -i:$PORT > /dev/null; then
        echo "Application started successfully!"
        break
    fi

    if [ $i -eq 10 ]; then
        show_error "The application failed to start"
    fi

    sleep 1
done

# Open the browser with the application
if [ "$NO_BROWSER" = false ]; then
    echo "Opening browser..."
    open "http://localhost:$PORT"
fi

echo ""
echo "==============================================="
echo "  Invoice Generator is running"
echo "  URL: http://localhost:$PORT"
echo "  Logs: $LOG_FILE"
if [ -f "app.py" ]; then
    echo "  Last modified: $(date -r app.py '+%Y-%m-%d %H:%M')"
fi
echo "  Press Ctrl+C to stop the application"
echo "==============================================="
echo ""

# Keep the script running
while true; do
    sleep 5
    # Check if Flask is still running
    if ! lsof -i:$PORT > /dev/null 2>&1; then
        show_error "The application has unexpectedly terminated"
    fi
done
