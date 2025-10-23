#!/bin/bash

# This script sets up the .env file to use TWO separate Railway PostgreSQL databases
# - KG Market: One Railway PostgreSQL
# - US Market: Another Railway PostgreSQL

# --- Configuration ---
KG_DB="postgresql://postgres:YgyDmMbYyzPKvSsNyDRShLJqehXtTdJx@metro.proxy.rlwy.net:45504/railway"
US_DB="postgresql://postgres:HnxnpmuFbMiTFmOFJQkfhTDjaublaith@interchange.proxy.rlwy.net:54878/railway"

# --- Create/Update .env file ---
ENV_FILE=".env"

echo "🚂 Configuring TWO Railway Databases (KG + US)"
echo "=========================================="

# Check if .env exists, if not, create it
if [ ! -f "$ENV_FILE" ]; then
    touch "$ENV_FILE"
    echo "✅ Created new .env file."
else
    echo "🔄 Updating existing .env file."
fi

# Remove old database URLs if they exist
sed -i '' '/^DATABASE_URL_MARQUE_KG=/d' "$ENV_FILE"
sed -i '' '/^DATABASE_URL_MARQUE_US=/d' "$ENV_FILE"
sed -i '' '/^TWILIO_ACCOUNT_SID=/d' "$ENV_FILE"
sed -i '' '/^TWILIO_AUTH_TOKEN=/d' "$ENV_FILE"
sed -i '' '/^TWILIO_VERIFY_SERVICE_SID=/d' "$ENV_FILE"
sed -i '' '/^SECRET_KEY=/d' "$ENV_FILE"
sed -i '' '/^JWT_ALGORITHM=/d' "$ENV_FILE"
sed -i '' '/^ACCESS_TOKEN_EXPIRE_MINUTES=/d' "$ENV_FILE"

# Add new database URLs
echo "" >> "$ENV_FILE"
echo "# Database Configuration - Two Separate Railway PostgreSQL Databases" >> "$ENV_FILE"
echo "DATABASE_URL_MARQUE_KG=$KG_DB" >> "$ENV_FILE"
echo "DATABASE_URL_MARQUE_US=$US_DB" >> "$ENV_FILE"
echo "" >> "$ENV_FILE"

# Twilio Configuration
echo "# Twilio Configuration" >> "$ENV_FILE"
echo "TWILIO_ACCOUNT_SID=your_twilio_account_sid_here" >> "$ENV_FILE"
echo "TWILIO_AUTH_TOKEN=your_twilio_auth_token_here" >> "$ENV_FILE"
echo "TWILIO_VERIFY_SERVICE_SID=your_twilio_verify_service_sid_here" >> "$ENV_FILE"
echo "" >> "$ENV_FILE"

# Security
echo "# Security" >> "$ENV_FILE"
echo "SECRET_KEY=your-super-secure-production-secret-key-change-this" >> "$ENV_FILE"
echo "JWT_ALGORITHM=HS256" >> "$ENV_FILE"
echo "ACCESS_TOKEN_EXPIRE_MINUTES=30" >> "$ENV_FILE"
echo "" >> "$ENV_FILE"

echo "✅ Created .env file with TWO Railway databases"
echo ""
echo "📊 Configuration:"
echo "  KG Market DB: metro.proxy.rlwy.net:45504"
echo "  US Market DB: interchange.proxy.rlwy.net:54878"
echo ""
echo "🎯 What this means:"
echo "  - KG users (+996) → KG Railway PostgreSQL"
echo "  - US users (+1) → US Railway PostgreSQL"
echo "  - User 19 will be in US database!"
echo ""
echo "✅ Setup complete!"

