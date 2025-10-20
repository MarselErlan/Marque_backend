#!/bin/bash
# Run Alembic migration on Railway production database

echo "🚀 Running migration on Railway production database..."

# Run migration
railway run alembic upgrade head

echo "✅ Migration complete!"

