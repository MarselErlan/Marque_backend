#!/bin/bash
# Railway Migration Script
# Run this to manually apply migrations to Railway databases

set -e

echo "🚂 Railway Database Migration Script"
echo "======================================"
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found!"
    echo "Install it with: npm i -g @railway/cli"
    echo "Then run: railway login && railway link"
    exit 1
fi

# Check target database parameter
TARGET_DB=${1:-BOTH}

echo "Target: $TARGET_DB market(s)"
echo ""

# Function to run migration
run_migration() {
    local market=$1
    echo "📊 Migrating $market database..."
    ALEMBIC_TARGET_DB=$market railway run alembic upgrade head
    
    if [ $? -eq 0 ]; then
        echo "✅ $market migration completed successfully"
    else
        echo "❌ $market migration failed!"
        return 1
    fi
    echo ""
}

# Run migrations based on parameter
case $TARGET_DB in
    KG|kg)
        run_migration "KG"
        ;;
    US|us)
        run_migration "US"
        ;;
    BOTH|both)
        run_migration "KG"
        run_migration "US"
        ;;
    *)
        echo "❌ Invalid target: $TARGET_DB"
        echo "Usage: ./railway_migrate.sh [KG|US|BOTH]"
        echo "Example: ./railway_migrate.sh US"
        exit 1
        ;;
esac

echo "======================================"
echo "✅ All migrations completed!"
echo ""
echo "🔍 Verify with:"
echo "  railway run alembic current"
echo ""
echo "📝 Check database schema:"
echo "  railway run psql \$DATABASE_URL_MARQUE_US -c '\d users'"
echo ""
echo "🚀 Ready to deploy!"

