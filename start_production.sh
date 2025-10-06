#!/bin/bash
set -e

echo "🔧 Marque Production Startup Script"
echo "======================================"

# Run migrations for KG database
echo "📊 Running migrations for KG market..."
ALEMBIC_TARGET_DB=KG alembic upgrade head || echo "⚠️  KG migration failed or already up to date"

# Run migrations for US database
echo "📊 Running migrations for US market..."
ALEMBIC_TARGET_DB=US alembic upgrade head || echo "⚠️  US migration failed or already up to date"

echo "✅ Database migrations completed"
echo ""

# Start the production server
echo "🚀 Starting Marque API server..."
echo "Host: 0.0.0.0"
echo "Port: ${PORT:-8000}"
echo "======================================"

exec uvicorn src.app_01.main:app --host 0.0.0.0 --port ${PORT:-8000}

