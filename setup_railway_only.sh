#!/bin/bash

# Setup Script - Railway Database Only
# This configures your app to use ONLY Railway database

echo "🚂 Configuring Railway Database Only Setup"
echo "=========================================="
echo ""

# Railway Database URL (same for both markets)
RAILWAY_DB="postgresql://postgres:YgyDmMbYyzPKvSsNyDRShLJqehXtTdJx@metro.proxy.rlwy.net:45504/railway"

# Create or update .env file
cat > .env << EOF
# Marque API - Railway Production Only
# Both KG and US markets use the same Railway database

# Railway PostgreSQL (Same database for both markets)
DATABASE_URL_MARQUE_KG=$RAILWAY_DB
DATABASE_URL_MARQUE_US=$RAILWAY_DB

# Twilio Configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_VERIFY_SERVICE_SID=your_twilio_verify_service_sid_here

# Security
SECRET_KEY=your-super-secure-production-secret-key-change-this
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000
EOF

echo "✅ Created .env file with Railway database configuration"
echo ""
echo "📊 Configuration:"
echo "  KG Market DB: Railway PostgreSQL"
echo "  US Market DB: Railway PostgreSQL (SAME)"
echo "  Database: metro.proxy.rlwy.net:45504"
echo ""
echo "🎯 What this means:"
echo "  - All users (KG + US) in ONE Railway database"
echo "  - No local database needed"
echo "  - User 19 will now be created in Railway!"
echo ""
echo "🚀 Next steps:"
echo "  1. Test locally: python3 test_auth_flow_complete.py"
echo "  2. Check database: python3 check_railway_user_19.py"
echo "  3. User 19 should now appear in Railway database!"
echo ""
echo "✅ Setup complete!"

