"""
Debug wishlist error - get detailed error message
"""

import requests
import json

API_BASE_URL = "https://marquebackend-production.up.railway.app/api/v1"
MARKET = "us"
TEST_PHONE = "+13128059851"

print("\n🔍 DEBUGGING WISHLIST ERROR\n")

# Step 1: Send verification
print("Step 1: Sending verification code...")
response = requests.post(
    f"{API_BASE_URL}/auth/send-verification",
    json={"phone": TEST_PHONE},
    headers={"X-Market": MARKET}
)
print(f"✅ Code sent (Status: {response.status_code})")

# Step 2: Login
code = input("\nEnter SMS code: ").strip()
print("\nStep 2: Logging in...")
response = requests.post(
    f"{API_BASE_URL}/auth/verify-code",
    json={"phone": TEST_PHONE, "verification_code": code},
    headers={"X-Market": MARKET}
)

if response.status_code != 200:
    print(f"❌ Login failed: {response.json()}")
    exit(1)

token = response.json().get("access_token")
print(f"✅ Logged in (Token: {token[:20]}...)")

# Step 3: Try to get wishlist with detailed error
print("\nStep 3: Getting wishlist (with full error details)...")
headers = {
    "Authorization": f"Bearer {token}",
    "X-Market": MARKET
}

response = requests.get(f"{API_BASE_URL}/wishlist", headers=headers)

print(f"\nStatus Code: {response.status_code}")
print(f"\nResponse Headers:")
for key, value in response.headers.items():
    if key.lower() in ['content-type', 'content-length', 'date']:
        print(f"  {key}: {value}")

print(f"\nResponse Body:")
try:
    print(json.dumps(response.json(), indent=2))
except:
    print(response.text)

if response.status_code == 500:
    print("\n" + "="*60)
    print("❌ 500 ERROR DETECTED")
    print("="*60)
    print("\nPossible causes:")
    print("1. Railway hasn't redeployed yet (check Railway dashboard)")
    print("2. Database migration needed")
    print("3. Missing Product model attribute")
    print("4. Database connection issue")
    print("\nCheck Railway logs for detailed error:")
    print("https://railway.app → Your Project → Logs")
    print("\nOr wait 1-2 minutes for Railway to finish deploying")

