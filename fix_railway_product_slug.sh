#!/bin/bash

# Fix product slug in Railway database
# Connect to Railway's PostgreSQL and update product #42

echo "🔧 Fixing product slug in Railway database..."
echo ""

# Use Railway CLI to connect and run SQL
railway run --service Postgres -- psql -c "UPDATE products SET slug = 'test-product1' WHERE id = 42 AND slug IS NULL;"

echo ""
echo "✅ Done! Verifying..."
echo ""

# Verify the change
curl -s "https://marquebackend-production.up.railway.app/api/v1/products?limit=1" | jq '.[0] | {id, name, slug}'

