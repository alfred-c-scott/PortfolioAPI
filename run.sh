#!/bin/bash

# run.sh - Load environment variables and start the server

ENV_FILE=".env"

echo "Starting server with fresh environment variables..."

# Step 1: Load environment variables
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

# Step 2: Start the server in foreground
echo "Starting FastAPI server..."
echo "Server running at: http://localhost:8000"
echo "Auto-reload enabled for development"
echo "Press Ctrl+C to stop the server"

uvicorn app.main:app --host 0.0.0.0 --port 8030 --reload