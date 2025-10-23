#!/bin/bash

# Stop Flask app

PID_FILE="flask_app.pid"

# Check if PID file exists
if [ ! -f "$PID_FILE" ]; then
    echo "Flask app is not running (no PID file found)"
    exit 0
fi

# Read PID
APP_PID=$(cat "$PID_FILE")

# Check if process is running
if ! ps -p "$APP_PID" > /dev/null 2>&1; then
    echo "Flask app is not running (stale PID file)"
    rm "$PID_FILE"
    exit 0
fi

# Kill the process
echo "Stopping Flask app (PID: $APP_PID)..."
kill "$APP_PID"

# Wait for process to stop
sleep 2

# Check if it stopped
if ps -p "$APP_PID" > /dev/null 2>&1; then
    echo "Process didn't stop, forcing..."
    kill -9 "$APP_PID"
    sleep 1
fi

# Remove PID file
rm "$PID_FILE"

echo "✅ Flask app stopped successfully"
