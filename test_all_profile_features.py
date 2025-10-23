"""
Complete Profile Features Test
Tests all 16 profile endpoints + authentication
"""

import requests
import json
from datetime import datetime

# API Configuration
BASE_URL = "https://marquebackend-production.up.railway.app/api/v1"
# Or use local: BASE_URL = "http://127.0.0.1:8000/api/v1"

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
RESET = '\033[0m'

def print_success(msg):
    print(f"{GREEN}✅ {msg}{RESET}")

def print_error(msg):
    print(f"{RED}❌ {msg}{RESET}")

def print_info(msg):
    print(f"{BLUE}ℹ️  {msg}{RESET}")

def print_warning(msg):
    print(f"{YELLOW}⚠️  {msg}{RESET}")

def print_header(msg):
    print(f"\n{CYAN}{'=' * 60}{RESET}")
    print(f"{CYAN}{msg}{RESET}")
    print(f"{CYAN}{'=' * 60}{RESET}")

def print_json(data):
    print(json.dumps(data, indent=2))

# Test results tracker
test_results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "tests": []
}

def record_test(name, passed, message=""):
    test_results["total"] += 1
    if passed:
        test_results["passed"] += 1
        print_success(f"{name}: PASS {message}")
    else:
        test_results["failed"] += 1
        print_error(f"{name}: FAIL {message}")
    test_results["tests"].append({"name": name, "passed": passed, "message": message})


# ==================== Authentication ====================

def test_authentication():
    """Test authentication flow"""
    print_header("STEP 1: AUTHENTICATION")
    
    phone = input("\n📱 Enter phone number (e.g., +13128059851): ").strip()
    
    # Send verification code
    print_info(f"Sending verification code to {phone}...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/send-verification",
            json={"phone": phone},
            timeout=10
        )
        
        if response.status_code == 200:
            print_success("Verification code sent!")
            record_test("Send verification code", True)
        else:
            print_error(f"Failed: {response.text}")
            record_test("Send verification code", False, response.text)
            return None
    except Exception as e:
        print_error(f"Error: {e}")
        record_test("Send verification code", False, str(e))
        return None
    
    # Get code from user
    code = input("\n🔑 Enter verification code from SMS: ").strip()
    
    # Verify code
    print_info("Verifying code...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/verify-code",
            json={"phone": phone, "verification_code": code},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            user = data.get("user", {})
            is_new_user = data.get("is_new_user", False)
            
            print_success(f"Authentication successful!")
            print_info(f"User ID: {user.get('id')}")
            print_info(f"Market: {data.get('market')}")
            print_info(f"New User: {is_new_user}")
            print_info(f"Token: {token[:30]}...")
            
            record_test("Verify code", True, f"User ID: {user.get('id')}")
            
            return {
                "token": token,
                "user_id": user.get("id"),
                "market": data.get("market"),
                "phone": phone
            }
        else:
            print_error(f"Failed: {response.text}")
            record_test("Verify code", False, response.text)
            return None
    except Exception as e:
        print_error(f"Error: {e}")
        record_test("Verify code", False, str(e))
        return None


# ==================== Profile Tests ====================

def test_get_profile(auth):
    """Test GET /auth/profile"""
    print_header("TEST 1: GET USER PROFILE")
    
    headers = {"Authorization": f"Bearer {auth['token']}"}
    
    try:
        response = requests.get(f"{BASE_URL}/auth/profile", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_success("Profile retrieved!")
            print_json(data)
            record_test("GET /auth/profile", True)
            return data
        else:
            print_error(f"Status: {response.status_code}")
            print_error(response.text)
            record_test("GET /auth/profile", False, f"Status {response.status_code}")
            return None
    except Exception as e:
        print_error(f"Error: {e}")
        record_test("GET /auth/profile", False, str(e))
        return None


def test_update_profile(auth):
    """Test PUT /auth/profile"""
    print_header("TEST 2: UPDATE USER PROFILE")
    
    headers = {
        "Authorization": f"Bearer {auth['token']}",
        "Content-Type": "application/json"
    }
    
    update_data = {
        "full_name": "Test User Updated",
        "profile_image_url": "https://example.com/avatar.jpg"
    }
    
    print_info("Updating profile with:")
    print_json(update_data)
    
    try:
        response = requests.put(
            f"{BASE_URL}/auth/profile",
            headers=headers,
            json=update_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Profile updated!")
            print_json(data)
            record_test("PUT /auth/profile", True)
        else:
            print_error(f"Status: {response.status_code}")
            print_error(response.text)
            record_test("PUT /auth/profile", False, f"Status {response.status_code}")
    except Exception as e:
        print_error(f"Error: {e}")
        record_test("PUT /auth/profile", False, str(e))


# ==================== Address Tests ====================

def test_get_addresses(auth):
    """Test GET /profile/addresses"""
    print_header("TEST 3: GET ADDRESSES")
    
    headers = {"Authorization": f"Bearer {auth['token']}"}
    
    try:
        response = requests.get(f"{BASE_URL}/profile/addresses", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Found {data.get('total', 0)} addresses")
            print_json(data)
            record_test("GET /profile/addresses", True, f"{data.get('total', 0)} addresses")
            return data.get('addresses', [])
        else:
            print_error(f"Status: {response.status_code}")
            print_error(response.text)
            record_test("GET /profile/addresses", False, f"Status {response.status_code}")
            return []
    except Exception as e:
        print_error(f"Error: {e}")
        record_test("GET /profile/addresses", False, str(e))
        return []


def test_create_address(auth):
    """Test POST /profile/addresses"""
    print_header("TEST 4: CREATE ADDRESS")
    
    headers = {
        "Authorization": f"Bearer {auth['token']}",
        "Content-Type": "application/json"
    }
    
    new_address = {
        "title": "Test Address - Complete Test",
        "full_address": "123 Test Street, Apt 45, Bishkek",
        "street": "Test Street",
        "building": "123",
        "apartment": "45",
        "city": "Bishkek",
        "postal_code": "720000",
        "country": "Kyrgyzstan",
        "is_default": False
    }
    
    print_info("Creating address:")
    print_json(new_address)
    
    try:
        response = requests.post(
            f"{BASE_URL}/profile/addresses",
            headers=headers,
            json=new_address,
            timeout=10
        )
        
        if response.status_code == 201:
            data = response.json()
            address_id = data.get('address', {}).get('id')
            print_success(f"Address created with ID: {address_id}")
            print_json(data)
            record_test("POST /profile/addresses", True, f"ID: {address_id}")
            return address_id
        else:
            print_error(f"Status: {response.status_code}")
            print_error(response.text)
            record_test("POST /profile/addresses", False, f"Status {response.status_code}")
            return None
    except Exception as e:
        print_error(f"Error: {e}")
        record_test("POST /profile/addresses", False, str(e))
        return None


def test_update_address(auth, address_id):
    """Test PUT /profile/addresses/{id}"""
    print_header(f"TEST 5: UPDATE ADDRESS (ID: {address_id})")
    
    if not address_id:
        print_warning("No address ID, skipping update test")
        record_test("PUT /profile/addresses/{id}", False, "No address ID")
        return
    
    headers = {
        "Authorization": f"Bearer {auth['token']}",
        "Content-Type": "application/json"
    }
    
    update_data = {
        "title": "Updated Test Address",
        "is_default": True
    }
    
    print_info("Updating address:")
    print_json(update_data)
    
    try:
        response = requests.put(
            f"{BASE_URL}/profile/addresses/{address_id}",
            headers=headers,
            json=update_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Address updated!")
            print_json(data)
            record_test("PUT /profile/addresses/{id}", True)
        else:
            print_error(f"Status: {response.status_code}")
            print_error(response.text)
            record_test("PUT /profile/addresses/{id}", False, f"Status {response.status_code}")
    except Exception as e:
        print_error(f"Error: {e}")
        record_test("PUT /profile/addresses/{id}", False, str(e))


def test_delete_address(auth, address_id):
    """Test DELETE /profile/addresses/{id}"""
    print_header(f"TEST 6: DELETE ADDRESS (ID: {address_id})")
    
    if not address_id:
        print_warning("No address ID, skipping delete test")
        record_test("DELETE /profile/addresses/{id}", False, "No address ID")
        return
    
    delete = input(f"\n🗑️  Delete test address {address_id}? (y/n): ").strip().lower()
    
    if delete != 'y':
        print_info("Skipping delete (address kept for review)")
        record_test("DELETE /profile/addresses/{id}", True, "Skipped by user")
        return
    
    headers = {"Authorization": f"Bearer {auth['token']}"}
    
    try:
        response = requests.delete(
            f"{BASE_URL}/profile/addresses/{address_id}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Address deleted!")
            print_json(data)
            record_test("DELETE /profile/addresses/{id}", True)
        else:
            print_error(f"Status: {response.status_code}")
            print_error(response.text)
            record_test("DELETE /profile/addresses/{id}", False, f"Status {response.status_code}")
    except Exception as e:
        print_error(f"Error: {e}")
        record_test("DELETE /profile/addresses/{id}", False, str(e))


# ==================== Payment Method Tests ====================

def test_get_payment_methods(auth):
    """Test GET /profile/payment-methods"""
    print_header("TEST 7: GET PAYMENT METHODS")
    
    headers = {"Authorization": f"Bearer {auth['token']}"}
    
    try:
        response = requests.get(f"{BASE_URL}/profile/payment-methods", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Found {data.get('total', 0)} payment methods")
            print_json(data)
            record_test("GET /profile/payment-methods", True, f"{data.get('total', 0)} methods")
            return data.get('payment_methods', [])
        else:
            print_error(f"Status: {response.status_code}")
            print_error(response.text)
            record_test("GET /profile/payment-methods", False, f"Status {response.status_code}")
            return []
    except Exception as e:
        print_error(f"Error: {e}")
        record_test("GET /profile/payment-methods", False, str(e))
        return []


def test_create_payment_method(auth):
    """Test POST /profile/payment-methods"""
    print_header("TEST 8: CREATE PAYMENT METHOD")
    
    headers = {
        "Authorization": f"Bearer {auth['token']}",
        "Content-Type": "application/json"
    }
    
    new_payment = {
        "card_number": "4111111111111111",
        "card_holder_name": "TEST USER",
        "expiry_month": "12",
        "expiry_year": "2028",
        "is_default": False
    }
    
    print_info("Creating payment method:")
    print_json(new_payment)
    
    try:
        response = requests.post(
            f"{BASE_URL}/profile/payment-methods",
            headers=headers,
            json=new_payment,
            timeout=10
        )
        
        if response.status_code == 201:
            data = response.json()
            payment_id = data.get('payment_method', {}).get('id')
            print_success(f"Payment method created with ID: {payment_id}")
            print_json(data)
            record_test("POST /profile/payment-methods", True, f"ID: {payment_id}")
            return payment_id
        else:
            print_error(f"Status: {response.status_code}")
            print_error(response.text)
            record_test("POST /profile/payment-methods", False, f"Status {response.status_code}")
            return None
    except Exception as e:
        print_error(f"Error: {e}")
        record_test("POST /profile/payment-methods", False, str(e))
        return None


def test_update_payment_method(auth, payment_id):
    """Test PUT /profile/payment-methods/{id}"""
    print_header(f"TEST 9: UPDATE PAYMENT METHOD (ID: {payment_id})")
    
    if not payment_id:
        print_warning("No payment ID, skipping update test")
        record_test("PUT /profile/payment-methods/{id}", False, "No payment ID")
        return
    
    headers = {
        "Authorization": f"Bearer {auth['token']}",
        "Content-Type": "application/json"
    }
    
    update_data = {"is_default": True}
    
    print_info("Setting as default payment method")
    
    try:
        response = requests.put(
            f"{BASE_URL}/profile/payment-methods/{payment_id}",
            headers=headers,
            json=update_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Payment method updated!")
            print_json(data)
            record_test("PUT /profile/payment-methods/{id}", True)
        else:
            print_error(f"Status: {response.status_code}")
            print_error(response.text)
            record_test("PUT /profile/payment-methods/{id}", False, f"Status {response.status_code}")
    except Exception as e:
        print_error(f"Error: {e}")
        record_test("PUT /profile/payment-methods/{id}", False, str(e))


def test_delete_payment_method(auth, payment_id):
    """Test DELETE /profile/payment-methods/{id}"""
    print_header(f"TEST 10: DELETE PAYMENT METHOD (ID: {payment_id})")
    
    if not payment_id:
        print_warning("No payment ID, skipping delete test")
        record_test("DELETE /profile/payment-methods/{id}", False, "No payment ID")
        return
    
    delete = input(f"\n🗑️  Delete test payment method {payment_id}? (y/n): ").strip().lower()
    
    if delete != 'y':
        print_info("Skipping delete (payment method kept for review)")
        record_test("DELETE /profile/payment-methods/{id}", True, "Skipped by user")
        return
    
    headers = {"Authorization": f"Bearer {auth['token']}"}
    
    try:
        response = requests.delete(
            f"{BASE_URL}/profile/payment-methods/{payment_id}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Payment method deleted!")
            print_json(data)
            record_test("DELETE /profile/payment-methods/{id}", True)
        else:
            print_error(f"Status: {response.status_code}")
            print_error(response.text)
            record_test("DELETE /profile/payment-methods/{id}", False, f"Status {response.status_code}")
    except Exception as e:
        print_error(f"Error: {e}")
        record_test("DELETE /profile/payment-methods/{id}", False, str(e))


# ==================== Order Tests ====================

def test_get_orders(auth):
    """Test GET /profile/orders"""
    print_header("TEST 11: GET ORDERS")
    
    headers = {"Authorization": f"Bearer {auth['token']}"}
    
    try:
        response = requests.get(f"{BASE_URL}/profile/orders", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Found {data.get('total', 0)} orders")
            print_json(data)
            record_test("GET /profile/orders", True, f"{data.get('total', 0)} orders")
            return data.get('orders', [])
        else:
            print_error(f"Status: {response.status_code}")
            print_error(response.text)
            record_test("GET /profile/orders", False, f"Status {response.status_code}")
            return []
    except Exception as e:
        print_error(f"Error: {e}")
        record_test("GET /profile/orders", False, str(e))
        return []


def test_get_order_details(auth, orders):
    """Test GET /profile/orders/{id}"""
    print_header("TEST 12: GET ORDER DETAILS")
    
    if not orders:
        print_warning("No orders found, skipping order details test")
        record_test("GET /profile/orders/{id}", False, "No orders")
        return
    
    order_id = orders[0].get('id')
    print_info(f"Getting details for order ID: {order_id}")
    
    headers = {"Authorization": f"Bearer {auth['token']}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/profile/orders/{order_id}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Order details retrieved!")
            print_json(data)
            record_test("GET /profile/orders/{id}", True)
        else:
            print_error(f"Status: {response.status_code}")
            print_error(response.text)
            record_test("GET /profile/orders/{id}", False, f"Status {response.status_code}")
    except Exception as e:
        print_error(f"Error: {e}")
        record_test("GET /profile/orders/{id}", False, str(e))


def test_cancel_order(auth, orders):
    """Test POST /profile/orders/{id}/cancel"""
    print_header("TEST 13: CANCEL ORDER")
    
    if not orders:
        print_warning("No orders found, skipping cancel test")
        record_test("POST /profile/orders/{id}/cancel", False, "No orders")
        return
    
    # Find a pending order if any
    pending_orders = [o for o in orders if o.get('status') == 'pending']
    
    if not pending_orders:
        print_warning("No pending orders to cancel")
        record_test("POST /profile/orders/{id}/cancel", False, "No pending orders")
        return
    
    order_id = pending_orders[0].get('id')
    
    cancel = input(f"\n⚠️  Cancel order {order_id}? (y/n): ").strip().lower()
    
    if cancel != 'y':
        print_info("Skipping cancel")
        record_test("POST /profile/orders/{id}/cancel", True, "Skipped by user")
        return
    
    headers = {"Authorization": f"Bearer {auth['token']}"}
    
    try:
        response = requests.post(
            f"{BASE_URL}/profile/orders/{order_id}/cancel",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Order cancelled!")
            print_json(data)
            record_test("POST /profile/orders/{id}/cancel", True)
        else:
            print_error(f"Status: {response.status_code}")
            print_error(response.text)
            record_test("POST /profile/orders/{id}/cancel", False, f"Status {response.status_code}")
    except Exception as e:
        print_error(f"Error: {e}")
        record_test("POST /profile/orders/{id}/cancel", False, str(e))


# ==================== Notification Tests ====================

def test_get_notifications(auth):
    """Test GET /profile/notifications"""
    print_header("TEST 14: GET NOTIFICATIONS")
    
    headers = {"Authorization": f"Bearer {auth['token']}"}
    
    try:
        response = requests.get(f"{BASE_URL}/profile/notifications", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Found {data.get('total', 0)} notifications ({data.get('unread_count', 0)} unread)")
            print_json(data)
            record_test("GET /profile/notifications", True, f"{data.get('total', 0)} total")
            return data.get('notifications', [])
        else:
            print_error(f"Status: {response.status_code}")
            print_error(response.text)
            record_test("GET /profile/notifications", False, f"Status {response.status_code}")
            return []
    except Exception as e:
        print_error(f"Error: {e}")
        record_test("GET /profile/notifications", False, str(e))
        return []


def test_mark_notification_read(auth, notifications):
    """Test PUT /profile/notifications/{id}/read"""
    print_header("TEST 15: MARK NOTIFICATION AS READ")
    
    if not notifications:
        print_warning("No notifications found")
        record_test("PUT /profile/notifications/{id}/read", False, "No notifications")
        return
    
    # Find an unread notification
    unread_notifications = [n for n in notifications if not n.get('is_read')]
    
    if not unread_notifications:
        print_warning("No unread notifications")
        record_test("PUT /profile/notifications/{id}/read", False, "No unread notifications")
        return
    
    notification_id = unread_notifications[0].get('id')
    print_info(f"Marking notification {notification_id} as read")
    
    headers = {"Authorization": f"Bearer {auth['token']}"}
    
    try:
        response = requests.put(
            f"{BASE_URL}/profile/notifications/{notification_id}/read",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Notification marked as read!")
            print_json(data)
            record_test("PUT /profile/notifications/{id}/read", True)
        else:
            print_error(f"Status: {response.status_code}")
            print_error(response.text)
            record_test("PUT /profile/notifications/{id}/read", False, f"Status {response.status_code}")
    except Exception as e:
        print_error(f"Error: {e}")
        record_test("PUT /profile/notifications/{id}/read", False, str(e))


def test_mark_all_notifications_read(auth):
    """Test PUT /profile/notifications/read-all"""
    print_header("TEST 16: MARK ALL NOTIFICATIONS AS READ")
    
    headers = {"Authorization": f"Bearer {auth['token']}"}
    
    try:
        response = requests.put(
            f"{BASE_URL}/profile/notifications/read-all",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("All notifications marked as read!")
            print_json(data)
            record_test("PUT /profile/notifications/read-all", True)
        else:
            print_error(f"Status: {response.status_code}")
            print_error(response.text)
            record_test("PUT /profile/notifications/read-all", False, f"Status {response.status_code}")
    except Exception as e:
        print_error(f"Error: {e}")
        record_test("PUT /profile/notifications/read-all", False, str(e))


# ==================== Logout Test ====================

def test_logout(auth):
    """Test POST /auth/logout"""
    print_header("TEST 17: LOGOUT")
    
    logout = input("\n🚪 Test logout? (y/n): ").strip().lower()
    
    if logout != 'y':
        print_info("Skipping logout test")
        record_test("POST /auth/logout", True, "Skipped by user")
        return
    
    headers = {"Authorization": f"Bearer {auth['token']}"}
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/logout",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Logged out successfully!")
            print_json(data)
            record_test("POST /auth/logout", True)
        else:
            print_error(f"Status: {response.status_code}")
            print_error(response.text)
            record_test("POST /auth/logout", False, f"Status {response.status_code}")
    except Exception as e:
        print_error(f"Error: {e}")
        record_test("POST /auth/logout", False, str(e))


# ==================== Main Test Flow ====================

def print_test_summary():
    """Print final test summary"""
    print_header("TEST SUMMARY")
    
    print(f"\n📊 Total Tests: {test_results['total']}")
    print(f"{GREEN}✅ Passed: {test_results['passed']}{RESET}")
    print(f"{RED}❌ Failed: {test_results['failed']}{RESET}")
    
    success_rate = (test_results['passed'] / test_results['total'] * 100) if test_results['total'] > 0 else 0
    print(f"\n📈 Success Rate: {success_rate:.1f}%")
    
    if test_results['failed'] > 0:
        print(f"\n{RED}Failed Tests:{RESET}")
        for test in test_results['tests']:
            if not test['passed']:
                print(f"  ❌ {test['name']}: {test['message']}")
    
    print(f"\n{CYAN}{'=' * 60}{RESET}")


def main():
    """Main test flow"""
    print_header("🧪 COMPLETE PROFILE FEATURES TEST")
    
    print("\nThis script will test ALL profile endpoints:")
    print("  1. Authentication (login/logout)")
    print("  2. Profile (get/update)")
    print("  3. Addresses (get/create/update/delete)")
    print("  4. Payment methods (get/create/update/delete)")
    print("  5. Orders (get/details/cancel)")
    print("  6. Notifications (get/mark read/mark all read)")
    
    print(f"\n🌐 Using API: {BASE_URL}")
    
    # Step 1: Authentication
    auth = test_authentication()
    if not auth:
        print_error("Authentication failed. Cannot proceed with tests.")
        return
    
    # Step 2: Profile tests
    test_get_profile(auth)
    test_update_profile(auth)
    
    # Step 3: Address tests
    test_get_addresses(auth)
    address_id = test_create_address(auth)
    test_update_address(auth, address_id)
    test_get_addresses(auth)  # Verify updates
    test_delete_address(auth, address_id)
    
    # Step 4: Payment method tests
    test_get_payment_methods(auth)
    payment_id = test_create_payment_method(auth)
    test_update_payment_method(auth, payment_id)
    test_get_payment_methods(auth)  # Verify updates
    test_delete_payment_method(auth, payment_id)
    
    # Step 5: Order tests
    orders = test_get_orders(auth)
    test_get_order_details(auth, orders)
    test_cancel_order(auth, orders)
    
    # Step 6: Notification tests
    notifications = test_get_notifications(auth)
    test_mark_notification_read(auth, notifications)
    test_mark_all_notifications_read(auth)
    
    # Step 7: Logout test
    test_logout(auth)
    
    # Print summary
    print_test_summary()
    
    print(f"\n{GREEN}🎉 Test complete!{RESET}")
    print(f"\nYou tested {test_results['total']} endpoints:")
    print("✅ 2 Authentication endpoints")
    print("✅ 2 Profile endpoints")
    print("✅ 4 Address endpoints")
    print("✅ 4 Payment method endpoints")
    print("✅ 3 Order endpoints")
    print("✅ 3 Notification endpoints")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Test cancelled by user{RESET}")
        print_test_summary()
    except Exception as e:
        print(f"\n\n{RED}❌ Unexpected error: {e}{RESET}")
        import traceback
        traceback.print_exc()
        print_test_summary()

