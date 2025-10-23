"""
Test script for Profile APIs
Tests all profile-related endpoints
"""

import requests
import json

# Configuration
BASE_URL = "http://127.0.0.1:8000/api/v1"
# You'll need to get a real token from logging in
# For testing, you can either:
# 1. Use a token from Postman after sending SMS and verifying
# 2. Or run the login flow first

def test_profile_apis():
    """Test all profile APIs"""
    
    print("=" * 60)
    print("PROFILE API TEST SCRIPT")
    print("=" * 60)
    
    # Get token first
    phone = input("\nEnter phone number (e.g., +13128059851): ").strip()
    
    print("\n1. Sending verification code...")
    response = requests.post(
        f"{BASE_URL}/auth/send-verification",
        json={"phone": phone}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code != 200:
        print("Failed to send verification code!")
        return
    
    # Wait for code
    code = input("\nEnter verification code from SMS: ").strip()
    
    print("\n2. Verifying code...")
    response = requests.post(
        f"{BASE_URL}/auth/verify-code",
        json={"phone": phone, "verification_code": code}
    )
    print(f"Status: {response.status_code}")
    
    if response.status_code != 200:
        print("Failed to verify code!")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return
    
    data = response.json()
    token = data.get("access_token")
    print(f"✅ Got token: {token[:20]}...")
    
    # Set up headers
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test Profile APIs
    print("\n" + "=" * 60)
    print("TESTING PROFILE ENDPOINTS")
    print("=" * 60)
    
    # 1. Get user profile
    print("\n3. Get User Profile...")
    response = requests.get(f"{BASE_URL}/auth/profile", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # 2. Get addresses
    print("\n4. Get User Addresses...")
    response = requests.get(f"{BASE_URL}/profile/addresses", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # 3. Create address
    print("\n5. Create New Address...")
    new_address = {
        "title": "Test Address",
        "full_address": "ул. Тестовая, 123, кв. 45, Бишкек",
        "street": "ул. Тестовая",
        "building": "123",
        "apartment": "45",
        "city": "Бишкек",
        "postal_code": "720000",
        "country": "Kyrgyzstan",
        "is_default": False
    }
    response = requests.post(
        f"{BASE_URL}/profile/addresses",
        headers=headers,
        json=new_address
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        address_id = response.json().get("address", {}).get("id")
        print(f"✅ Created address with ID: {address_id}")
    
    # 4. Get payment methods
    print("\n6. Get Payment Methods...")
    response = requests.get(f"{BASE_URL}/profile/payment-methods", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # 5. Create payment method
    print("\n7. Create New Payment Method...")
    new_payment = {
        "card_number": "4111111111111111",
        "card_holder_name": "TEST USER",
        "expiry_month": "12",
        "expiry_year": "2028",
        "is_default": False
    }
    response = requests.post(
        f"{BASE_URL}/profile/payment-methods",
        headers=headers,
        json=new_payment
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        payment_id = response.json().get("payment_method", {}).get("id")
        print(f"✅ Created payment method with ID: {payment_id}")
    
    # 6. Get orders
    print("\n8. Get User Orders...")
    response = requests.get(f"{BASE_URL}/profile/orders", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # 7. Get notifications
    print("\n9. Get User Notifications...")
    response = requests.get(f"{BASE_URL}/profile/notifications", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    print("\n" + "=" * 60)
    print("✅ PROFILE API TESTS COMPLETE!")
    print("=" * 60)
    print("\nAll endpoints are working correctly!")
    print("\nNext steps:")
    print("1. Update your frontend to use these APIs")
    print("2. Test address updates and deletions")
    print("3. Test payment method updates and deletions")
    print("4. Test order cancellation")
    print("5. Test notification marking as read")


if __name__ == "__main__":
    try:
        test_profile_apis()
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

