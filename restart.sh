#!/bin/bash

# restart.sh - Stop server, reload env vars, and restart server in foreground

ENV_FILE=".env"
PORT=8030

echo "Restarting server with fresh environment variables..."

# Step 1: Kill the server
echo "Stopping server on port $PORT..."

# Find and kill process using port 8030
PID=$(lsof -ti:$PORT 2>/dev/null)
if [ -n "$PID" ]; then
    echo "Found process $PID using port $PORT"
    kill $PID 2>/dev/null && echo "Killed process $PID"

    # Give process time to stop gracefully
    sleep 2

    # Force kill if still running
    if kill -0 $PID 2>/dev/null; then
        kill -9 $PID 2>/dev/null && echo "Force killed process $PID"
    fi
else
    echo "No process found using port $PORT"
fi

echo "Server stopped"

# Step 2: Load environment variables
echo "Loading environment variables from $ENV_FILE..."
if [ ! -f "$ENV_FILE" ]; then
    echo "Error: $ENV_FILE file not found!"
    exit 1
fi

# Export variables from .env file
set -a  # automatically export all variables
source "$ENV_FILE"
set +a  # stop auto-exporting

echo "Environment variables loaded"

# Step 3: Start the server in foreground
echo "Starting FastAPI server..."
echo "Server running at: http://localhost:8030"
echo "Auto-reload enabled for development"
echo "Press Ctrl+C to stop the server"

uvicorn app.main:app --host 0.0.0.0 --port 8030 --reload