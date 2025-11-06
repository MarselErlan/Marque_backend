#!/bin/bash
# Test API Endpoints After Migration Reset
# This script tests that data saves correctly to the database

echo "=================================="
echo "  Testing Marque API Endpoints"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test server is running
echo -e "${BLUE}1. Testing server health...${NC}"
curl -s http://localhost:8000/health | python3 -m json.tool
echo ""
echo ""

# Step 1: Send verification code
echo -e "${BLUE}2. Sending verification code to +996500123456...${NC}"
SEND_CODE_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/send-code \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+996500123456"
  }')

echo "$SEND_CODE_RESPONSE" | python3 -m json.tool
echo ""

# Extract verification code if in dev mode (it's returned in response)
VERIFY_CODE=$(echo "$SEND_CODE_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('verification_code', 'N/A'))" 2>/dev/null || echo "N/A")

if [ "$VERIFY_CODE" != "N/A" ]; then
    echo -e "${GREEN}✓ Got verification code: $VERIFY_CODE${NC}"
    echo ""
    
    # Step 2: Verify code (this creates the user)
    echo -e "${BLUE}3. Verifying code and creating user...${NC}"
    VERIFY_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/verify-code \
      -H "Content-Type: application/json" \
      -d "{
        \"phone\": \"+996500123456\",
        \"verification_code\": \"$VERIFY_CODE\"
      }")
    
    echo "$VERIFY_RESPONSE" | python3 -m json.tool
    echo ""
    
    # Check if user was created
    USER_ID=$(echo "$VERIFY_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('user', {}).get('id', 'N/A'))" 2>/dev/null || echo "N/A")
    
    if [ "$USER_ID" != "N/A" ]; then
        echo -e "${GREEN}✓ User created with ID: $USER_ID${NC}"
        echo ""
        
        # Step 3: Check database
        echo -e "${BLUE}4. Checking if user was saved to database...${NC}"
        python3 -c "
from src.app_01.core.config import settings
from sqlalchemy import create_engine, text

engine = create_engine(settings.database.url_kg)
with engine.connect() as conn:
    result = conn.execute(text('SELECT id, phone_number, created_at, market FROM users WHERE phone_number = \'+996500123456\' LIMIT 1'))
    row = result.fetchone()
    if row:
        print(f'✅ SUCCESS! User found in database:')
        print(f'   ID: {row[0]}')
        print(f'   Phone: {row[1]}')
        print(f'   Created: {row[2]}')
        print(f'   Market: {row[3] or \"N/A\"}')
    else:
        print('❌ FAILED: User not found in database!')
"
        echo ""
        echo -e "${GREEN}=================================="
        echo -e "  ✅ TEST PASSED!"
        echo -e "  Data is saving correctly!"
        echo -e "==================================${NC}"
    else
        echo -e "${RED}❌ Failed to create user${NC}"
    fi
else
    echo -e "${RED}⚠ Verification code not in response (production mode?)${NC}"
    echo -e "In production, you need to check SMS for the code."
    echo ""
    echo -e "${BLUE}Manual test:${NC}"
    echo "1. Call: curl -X POST http://localhost:8000/api/v1/auth/send-code -H 'Content-Type: application/json' -d '{\"phone\": \"+996500123456\"}'"
    echo "2. Check SMS for code"
    echo "3. Call: curl -X POST http://localhost:8000/api/v1/auth/verify-code -H 'Content-Type: application/json' -d '{\"phone\": \"+996500123456\", \"verification_code\": \"YOUR_CODE\"}'"
fi

echo ""
echo ""
echo -e "${BLUE}Other available endpoints:${NC}"
echo "  • GET  /health - Health check"
echo "  • GET  /docs - API documentation"
echo "  • POST /api/v1/auth/send-code - Send verification code"
echo "  • POST /api/v1/auth/verify-code - Verify code and login"
echo "  • GET  /api/v1/products - List products"
echo "  • GET  /api/v1/categories - List categories"
echo "  • GET  /api/v1/cart - Get cart"
echo "  • GET  /api/v1/wishlist - Get wishlist"
echo ""

