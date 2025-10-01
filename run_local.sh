#!/bin/bash

# Marque API - Local Development Server
# This script runs the Marque API locally with auto-reload

echo "🚀 Starting Marque API..."
echo "📍 Location: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""

# Activate virtual environment
source venv/bin/activate

# Run the application with uvicorn (auto-reload enabled)
uvicorn src.app_01.main:app --reload --host 0.0.0.0 --port 8000

# Alternative: Run using Python module
# python -m src.app_01.main

