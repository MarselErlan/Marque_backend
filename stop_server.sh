#!/bin/bash

# Stop Marque API Server
# This script stops any running instances of the Marque API

echo "🛑 Stopping Marque API..."

# Find and kill all Python processes running the app
pkill -f "src.app_01.main"
pkill -f "uvicorn.*src.app_01.main"

# Wait a moment
sleep 1

# Check if any processes are still running
if pgrep -f "src.app_01.main" > /dev/null; then
    echo "❌ Some processes may still be running. Force killing..."
    pkill -9 -f "src.app_01.main"
else
    echo "✅ Server stopped successfully!"
fi

