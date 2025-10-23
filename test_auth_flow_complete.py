"""
Test Complete Authentication Flow
Tests login, logout, and user state management (is_active, is_verified)
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
    print(f"\n{CYAN}{'=' * 70}{RESET}")
    print(f"{CYAN}{msg:^70}{RESET}")
    print(f"{CYAN}{'=' * 70}{RESET}")

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


def test_send_verification():
    """Test Step 1: Send verification code"""
    print_header("STEP 1: SEND VERIFICATION CODE")
    
    phone = input("\n📱 Enter phone number (e.g., +13128059851 or +996555123456): ").strip()
    
    print_info(f"Sending verification code to {phone}...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/send-verification",
            json={"phone": phone},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Verification code sent!")
            print_info(f"Message: {data.get('message')}")
            print_info(f"Status: {data.get('status')}")
            print_json(data)
            record_test("Send verification code", True)
            return phone
        else:
            print_error(f"Failed: Status {response.status_code}")
            print_error(response.text)
            record_test("Send verification code", False, f"Status {response.status_code}")
            return None
            
    except Exception as e:
        print_error(f"Error: {e}")
        record_test("Send verification code", False, str(e))
        return None


def test_verify_code(phone):
    """Test Step 2: Verify code and login"""
    print_header("STEP 2: VERIFY CODE AND LOGIN")
    
    if not phone:
        print_error("No phone number from previous step")
        return None
    
    code = input("\n🔑 Enter verification code from SMS: ").strip()
    
    print_info("Verifying code...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/verify-code",
            json={"phone": phone, "verification_code": code},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("✨ Login successful!")
            
            user = data.get("user", {})
            token = data.get("access_token")
            is_new_user = data.get("is_new_user", False)
            
            print()
            print_info(f"User ID: {user.get('id')}")
            print_info(f"Phone: {user.get('phone_number')}")
            print_info(f"Market: {data.get('market')}")
            print_info(f"Is New User: {is_new_user}")
            print_info(f"Is Active: {user.get('is_active')}")
            print_info(f"Is Verified: {user.get('is_verified')}")
            print_info(f"Token: {token[:30]}...")
            
            print()
            print_header("✅ USER STATE AFTER LOGIN")
            print(f"  is_active:   {GREEN}{user.get('is_active')}{RESET}   ← Should be TRUE")
            print(f"  is_verified: {GREEN}{user.get('is_verified')}{RESET}   ← Should be TRUE")
            
            # Verify expected state
            if user.get('is_active') == True and user.get('is_verified') == True:
                record_test("Verify code & login", True, f"User ID: {user.get('id')}")
                print_success("User state is correct! ✅")
            else:
                record_test("Verify code & login", False, "User state incorrect")
                print_error("User state is incorrect! ❌")
            
            return {
                "token": token,
                "user_id": user.get("id"),
                "phone": phone,
                "market": data.get("market")
            }
        else:
            print_error(f"Failed: Status {response.status_code}")
            print_error(response.text)
            record_test("Verify code & login", False, f"Status {response.status_code}")
            return None
            
    except Exception as e:
        print_error(f"Error: {e}")
        record_test("Verify code & login", False, str(e))
        return None


def test_get_profile(auth):
    """Test Step 3: Get user profile while logged in"""
    print_header("STEP 3: GET USER PROFILE (LOGGED IN)")
    
    if not auth:
        print_error("No authentication from previous step")
        return
    
    print_info("Fetching profile...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/auth/profile",
            headers={"Authorization": f"Bearer {auth['token']}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Profile retrieved!")
            
            print()
            print_info(f"User ID: {data.get('id')}")
            print_info(f"Phone: {data.get('phone_number')}")
            print_info(f"Name: {data.get('full_name') or 'Not set'}")
            print_info(f"Is Active: {data.get('is_active')}")
            print_info(f"Is Verified: {data.get('is_verified')}")
            print_info(f"Last Login: {data.get('last_login')}")
            
            print()
            print_header("✅ USER STATE WHILE LOGGED IN")
            print(f"  is_active:   {GREEN}{data.get('is_active')}{RESET}   ← Should be TRUE")
            print(f"  is_verified: {GREEN}{data.get('is_verified')}{RESET}   ← Should be TRUE")
            
            if data.get('is_active') == True:
                record_test("Get profile (logged in)", True)
                print_success("User is active! ✅")
            else:
                record_test("Get profile (logged in)", False, "User not active")
                print_error("User not active! ❌")
        else:
            print_error(f"Failed: Status {response.status_code}")
            print_error(response.text)
            record_test("Get profile (logged in)", False, f"Status {response.status_code}")
            
    except Exception as e:
        print_error(f"Error: {e}")
        record_test("Get profile (logged in)", False, str(e))


def test_logout(auth):
    """Test Step 4: Logout"""
    print_header("STEP 4: LOGOUT")
    
    if not auth:
        print_error("No authentication from previous step")
        return None
    
    print_info("Logging out...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/logout",
            headers={"Authorization": f"Bearer {auth['token']}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Logged out successfully!")
            print_info(f"Message: {data.get('message')}")
            
            print()
            print_header("✅ LOGOUT RESULT")
            print(f"  User should now be: {YELLOW}is_active = FALSE{RESET}")
            print(f"  Token discarded by server")
            
            record_test("Logout", True)
            return True
        else:
            print_error(f"Failed: Status {response.status_code}")
            print_error(response.text)
            record_test("Logout", False, f"Status {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error: {e}")
        record_test("Logout", False, str(e))
        return False


def test_profile_after_logout(auth):
    """Test Step 5: Try to access profile after logout (should fail or show inactive)"""
    print_header("STEP 5: TRY PROFILE AFTER LOGOUT")
    
    if not auth:
        print_error("No authentication from previous step")
        return
    
    print_info("Trying to access profile with old token...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/auth/profile",
            headers={"Authorization": f"Bearer {auth['token']}"},
            timeout=10
        )
        
        if response.status_code == 401 or response.status_code == 403:
            print_success("✅ Token properly rejected! (Unauthorized)")
            record_test("Profile after logout (should fail)", True, "Token rejected as expected")
        elif response.status_code == 200:
            data = response.json()
            print_warning("⚠️  Token still works, but checking user state...")
            
            print()
            print_info(f"Is Active: {data.get('is_active')}")
            print_info(f"Is Verified: {data.get('is_verified')}")
            
            if data.get('is_active') == False:
                print_success("✅ User is inactive! Logout worked correctly!")
                print_header("✅ USER STATE AFTER LOGOUT")
                print(f"  is_active:   {RED}{data.get('is_active')}{RESET}   ← Should be FALSE ✅")
                print(f"  is_verified: {GREEN}{data.get('is_verified')}{RESET}   ← Still TRUE (OK)")
                record_test("Profile after logout (user inactive)", True, "is_active = False")
            else:
                print_error("❌ User still active after logout!")
                record_test("Profile after logout (user inactive)", False, "is_active still True")
        else:
            print_warning(f"Unexpected status: {response.status_code}")
            print_info(response.text)
            record_test("Profile after logout", False, f"Unexpected status {response.status_code}")
            
    except Exception as e:
        print_error(f"Error: {e}")
        record_test("Profile after logout", False, str(e))


def test_login_again(phone):
    """Test Step 6: Login again to verify no duplicate user created"""
    print_header("STEP 6: LOGIN AGAIN (RE-LOGIN)")
    
    if not phone:
        print_error("No phone number from previous step")
        return None
    
    print_info(f"Sending new verification code to {phone}...")
    
    try:
        # Send verification code
        response = requests.post(
            f"{BASE_URL}/auth/send-verification",
            json={"phone": phone},
            timeout=10
        )
        
        if response.status_code != 200:
            print_error("Failed to send verification code")
            record_test("Re-login (send code)", False)
            return None
        
        print_success("Verification code sent!")
        
        code = input("\n🔑 Enter NEW verification code from SMS: ").strip()
        
        # Verify code
        response = requests.post(
            f"{BASE_URL}/auth/verify-code",
            json={"phone": phone, "verification_code": code},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("✨ Re-login successful!")
            
            user = data.get("user", {})
            is_new_user = data.get("is_new_user", False)
            
            print()
            print_info(f"User ID: {user.get('id')}")
            print_info(f"Phone: {user.get('phone_number')}")
            print_info(f"Is New User: {is_new_user}")
            print_info(f"Is Active: {user.get('is_active')}")
            print_info(f"Is Verified: {user.get('is_verified')}")
            
            print()
            print_header("✅ RE-LOGIN VERIFICATION")
            
            if is_new_user == False:
                print_success("✅ No duplicate user created! (is_new_user = False)")
            else:
                print_error("❌ New user created! Should have used existing user!")
            
            if user.get('is_active') == True:
                print_success("✅ User reactivated! (is_active = True)")
            else:
                print_error("❌ User not reactivated!")
            
            print()
            print_header("✅ USER STATE AFTER RE-LOGIN")
            print(f"  is_new_user: {YELLOW}{is_new_user}{RESET}   ← Should be FALSE ✅")
            print(f"  is_active:   {GREEN}{user.get('is_active')}{RESET}   ← Should be TRUE ✅")
            print(f"  is_verified: {GREEN}{user.get('is_verified')}{RESET}   ← Should be TRUE ✅")
            
            if not is_new_user and user.get('is_active') and user.get('is_verified'):
                record_test("Re-login (no duplicate)", True, "Existing user reactivated")
            else:
                record_test("Re-login (no duplicate)", False, "State incorrect")
            
            return data
        else:
            print_error(f"Failed: Status {response.status_code}")
            record_test("Re-login", False, f"Status {response.status_code}")
            return None
            
    except Exception as e:
        print_error(f"Error: {e}")
        record_test("Re-login", False, str(e))
        return None


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
    
    print(f"\n{CYAN}{'=' * 70}{RESET}")


def main():
    """Main test flow"""
    print_header("🔐 COMPLETE AUTHENTICATION FLOW TEST")
    
    print("\nThis script will test:")
    print("  1. ✅ Send verification code")
    print("  2. ✅ Verify code and login (sets is_active=True, is_verified=True)")
    print("  3. ✅ Get profile while logged in")
    print("  4. ✅ Logout (sets is_active=False)")
    print("  5. ✅ Try profile after logout (should fail or show inactive)")
    print("  6. ✅ Login again (no duplicate user, reactivates existing)")
    
    print(f"\n🌐 Testing API: {BASE_URL}")
    
    # Step 1: Send verification
    phone = test_send_verification()
    if not phone:
        print_error("Cannot proceed without phone number")
        return
    
    # Step 2: Verify and login
    auth = test_verify_code(phone)
    if not auth:
        print_error("Cannot proceed without authentication")
        return
    
    # Step 3: Get profile while logged in
    test_get_profile(auth)
    
    # Step 4: Logout
    logout_success = test_logout(auth)
    
    # Step 5: Try profile after logout
    if logout_success:
        test_profile_after_logout(auth)
    
    # Step 6: Login again
    print_info("\nNow let's test re-login to ensure no duplicate users...")
    input("Press Enter when ready to continue...")
    test_login_again(phone)
    
    # Print summary
    print_test_summary()
    
    print(f"\n{GREEN}🎉 Authentication flow test complete!{RESET}")


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

