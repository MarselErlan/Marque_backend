#!/bin/bash
# Simple Auth Test - After Bug Fix

echo "🧪 Testing Auth Flow..."
echo ""

# Your Railway URL (update if different)
API_URL="${1:-http://localhost:8000}"

echo "Testing: $API_URL"
echo ""

# Step 1: Send code
echo "1️⃣ Sending verification code to +996500123456..."
curl -s -X POST "$API_URL/api/v1/auth/send-code" \
  -H "Content-Type: application/json" \
  -d '{"phone": "+996500123456"}' | python3 -m json.tool

echo ""
echo ""
echo "2️⃣ Now check SMS for the code and run:"
echo ""
echo "curl -X POST $API_URL/api/v1/auth/verify-code \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"phone\": \"+996500123456\", \"verification_code\": \"YOUR_CODE\"}'"
echo ""

