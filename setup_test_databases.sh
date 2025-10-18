#!/bin/bash
# Setup PostgreSQL test databases

echo "🔧 Setting up PostgreSQL test databases..."

# Database credentials
DB_USER="postgres"
DB_PASSWORD="postgres"
DB_HOST="localhost"
DB_PORT="5432"

# Create test databases
echo "Creating test databases..."
PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -h $DB_HOST -p $DB_PORT -c "DROP DATABASE IF EXISTS marque_test_assets;" 2>/dev/null
PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -h $DB_HOST -p $DB_PORT -c "CREATE DATABASE marque_test_assets;" 2>/dev/null

PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -h $DB_HOST -p $DB_PORT -c "DROP DATABASE IF EXISTS marque_test_catalog;" 2>/dev/null
PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -h $DB_HOST -p $DB_PORT -c "CREATE DATABASE marque_test_catalog;" 2>/dev/null

PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -h $DB_HOST -p $DB_PORT -c "DROP DATABASE IF EXISTS marque_test_search;" 2>/dev/null
PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -h $DB_HOST -p $DB_PORT -c "CREATE DATABASE marque_test_search;" 2>/dev/null

echo "✅ Test databases created successfully!"
echo ""
echo "Test databases:"
echo "  - marque_test_assets"
echo "  - marque_test_catalog"
echo "  - marque_test_search"
echo ""
echo "Run tests with: pytest tests/test_product_*.py -v"

