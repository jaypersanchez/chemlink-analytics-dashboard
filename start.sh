#!/bin/bash

# Start Flask app in background with auto-reload
# Flask debug mode already includes auto-reload functionality

PID_FILE="flask_app.pid"
LOG_FILE="flask_app.log"

# Check if app is already running
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "Flask app is already running with PID $OLD_PID"
        echo "Use ./stop.sh to stop it first"
        exit 1
    else
        echo "Removing stale PID file"
        rm "$PID_FILE"
    fi
fi

# Start Flask app in background
echo "Starting Flask app in background..."
nohup python3 app.py > "$LOG_FILE" 2>&1 &
APP_PID=$!

# Save PID to file
echo $APP_PID > "$PID_FILE"

# Wait a moment and check if it started successfully
sleep 2

if ps -p $APP_PID > /dev/null; then
    echo "✅ Flask app started successfully!"
    echo "   PID: $APP_PID"
    echo "   URL: http://127.0.0.1:5000"
    echo "   Logs: tail -f $LOG_FILE"
    echo ""
    echo "To stop: ./stop.sh"
else
    echo "❌ Failed to start Flask app"
    echo "Check $LOG_FILE for errors"
    rm "$PID_FILE"
    exit 1
fi
