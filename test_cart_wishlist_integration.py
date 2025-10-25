"""
Integration Tests for Cart and Wishlist Stateless APIs
Tests both new stateless endpoints and legacy JWT endpoints
"""

import requests
import json
from typing import Dict, Any

# ==================== Configuration ====================

BASE_URL = "https://marquebackend-production.up.railway.app/api/v1"
# BASE_URL = "http://localhost:8000/api/v1"  # Use this for local testing

# Test data
TEST_PHONE_KG = "+996700123456"  # KG market
TEST_PHONE_US = "+996555123456"  # Will be treated as KG (for testing)
TEST_USER_ID = 19  # Replace with your test user ID
TEST_PRODUCT_ID = 1  # Replace with a valid product ID
TEST_SKU_ID = 1  # Replace with a valid SKU ID

# ==================== Helper Functions ====================

def print_section(title: str):
    """Print a section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def print_test(test_name: str):
    """Print a test name"""
    print(f"\n🧪 TEST: {test_name}")
    print("-" * 70)

def print_success(message: str):
    """Print success message"""
    print(f"✅ SUCCESS: {message}")

def print_error(message: str):
    """Print error message"""
    print(f"❌ ERROR: {message}")

def print_response(response: requests.Response):
    """Pretty print response"""
    print(f"\n📤 Request: {response.request.method} {response.request.url}")
    if response.request.body:
        try:
            body = json.loads(response.request.body)
            print(f"📦 Body: {json.dumps(body, indent=2)}")
        except:
            print(f"📦 Body: {response.request.body}")
    
    print(f"\n📥 Response: {response.status_code}")
    try:
        print(f"📄 Data: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"📄 Data: {response.text}")

def get_auth_token(phone: str) -> str:
    """Get JWT token for testing legacy endpoints"""
    # Step 1: Send verification code
    print(f"\n🔐 Getting auth token for {phone}...")
    send_response = requests.post(
        f"{BASE_URL}/auth/send-verification",
        json={"phone": phone}  # ✅ Fixed: use 'phone' not 'phone_number'
    )
    
    if send_response.status_code != 200:
        print_error(f"Failed to send verification: {send_response.text}")
        return None
    
    print("✅ Verification code sent (check SMS)")
    
    # Step 2: Get code from user
    code = input("Enter verification code: ").strip()
    
    # Step 3: Verify code and get token
    verify_response = requests.post(
        f"{BASE_URL}/auth/verify-code",
        json={"phone": phone, "verification_code": code}  # ✅ Fixed: use 'phone' and 'verification_code'
    )
    
    if verify_response.status_code != 200:
        print_error(f"Failed to verify: {verify_response.text}")
        return None
    
    data = verify_response.json()
    token = data.get("access_token")
    user_id = data.get("user", {}).get("id")
    
    print(f"✅ Token received for user_id: {user_id}")
    return token

# ==================== Wishlist Tests ====================

def test_wishlist_api():
    """Test all wishlist endpoints (stateless)"""
    print_section("WISHLIST API TESTS (Stateless)")
    
    # Test 1: Get Wishlist (Empty)
    print_test("1. Get Wishlist (should be empty or existing)")
    response = requests.post(
        f"{BASE_URL}/wishlist/get",
        json={"user_id": TEST_USER_ID}
    )
    print_response(response)
    
    if response.status_code == 200:
        print_success("Get wishlist works!")
        wishlist_data = response.json()
        initial_items = len(wishlist_data.get("items", []))
        print(f"📊 Initial wishlist has {initial_items} items")
    else:
        print_error(f"Failed to get wishlist: {response.text}")
        return False
    
    # Test 2: Add to Wishlist
    print_test("2. Add Product to Wishlist")
    response = requests.post(
        f"{BASE_URL}/wishlist/add",
        json={
            "user_id": TEST_USER_ID,
            "product_id": TEST_PRODUCT_ID
        }
    )
    print_response(response)
    
    if response.status_code == 200:
        print_success("Add to wishlist works!")
        wishlist_data = response.json()
        new_items = len(wishlist_data.get("items", []))
        print(f"📊 Wishlist now has {new_items} items")
    else:
        print_error(f"Failed to add to wishlist: {response.text}")
        return False
    
    # Test 3: Get Wishlist (with item)
    print_test("3. Get Wishlist (should have item)")
    response = requests.post(
        f"{BASE_URL}/wishlist/get",
        json={"user_id": TEST_USER_ID}
    )
    print_response(response)
    
    if response.status_code == 200:
        wishlist_data = response.json()
        items = wishlist_data.get("items", [])
        if len(items) >= 1:
            print_success(f"Wishlist has {len(items)} item(s) ✅")
        else:
            print_error("Wishlist should have at least 1 item")
    else:
        print_error(f"Failed to get wishlist: {response.text}")
    
    # Test 4: Remove from Wishlist
    print_test("4. Remove Product from Wishlist")
    response = requests.post(
        f"{BASE_URL}/wishlist/remove",
        json={
            "user_id": TEST_USER_ID,
            "product_id": TEST_PRODUCT_ID
        }
    )
    print_response(response)
    
    if response.status_code == 200:
        print_success("Remove from wishlist works!")
        wishlist_data = response.json()
        final_items = len(wishlist_data.get("items", []))
        print(f"📊 Wishlist now has {final_items} items")
    else:
        print_error(f"Failed to remove from wishlist: {response.text}")
        return False
    
    # Test 5: Clear Wishlist
    print_test("5. Clear Wishlist")
    response = requests.post(
        f"{BASE_URL}/wishlist/clear",
        json={"user_id": TEST_USER_ID}
    )
    print_response(response)
    
    if response.status_code == 200:
        print_success("Clear wishlist works!")
        wishlist_data = response.json()
        items = wishlist_data.get("items", [])
        if len(items) == 0:
            print_success("Wishlist is now empty ✅")
        else:
            print_error(f"Wishlist should be empty but has {len(items)} items")
    else:
        print_error(f"Failed to clear wishlist: {response.text}")
        return False
    
    return True

# ==================== Cart Tests (Stateless) ====================

def test_cart_stateless_api():
    """Test all new cart stateless endpoints"""
    print_section("CART API TESTS (Stateless - NEW)")
    
    # Test 1: Get Cart (Empty)
    print_test("1. Get Cart (should be empty or existing)")
    response = requests.post(
        f"{BASE_URL}/cart/get",
        json={"user_id": TEST_USER_ID}
    )
    print_response(response)
    
    if response.status_code == 200:
        print_success("Get cart works!")
        cart_data = response.json()
        initial_items = len(cart_data.get("items", []))
        print(f"📊 Initial cart has {initial_items} items")
    else:
        print_error(f"Failed to get cart: {response.text}")
        return False
    
    # Test 2: Add to Cart
    print_test("2. Add SKU to Cart")
    response = requests.post(
        f"{BASE_URL}/cart/add",
        json={
            "user_id": TEST_USER_ID,
            "sku_id": TEST_SKU_ID,
            "quantity": 2
        }
    )
    print_response(response)
    
    if response.status_code == 200:
        print_success("Add to cart works!")
        cart_data = response.json()
        items = cart_data.get("items", [])
        print(f"📊 Cart now has {len(items)} item(s)")
        print(f"💰 Total price: {cart_data.get('total_price')}")
        
        # Save cart_item_id for later tests
        if items:
            global CART_ITEM_ID
            CART_ITEM_ID = items[0]["id"]
            print(f"📝 Saved cart_item_id: {CART_ITEM_ID}")
    else:
        print_error(f"Failed to add to cart: {response.text}")
        return False
    
    # Test 3: Get Cart (with item)
    print_test("3. Get Cart (should have item)")
    response = requests.post(
        f"{BASE_URL}/cart/get",
        json={"user_id": TEST_USER_ID}
    )
    print_response(response)
    
    if response.status_code == 200:
        cart_data = response.json()
        items = cart_data.get("items", [])
        if len(items) >= 1:
            print_success(f"Cart has {len(items)} item(s) ✅")
            item = items[0]
            print(f"📦 Item: {item['name']} x{item['quantity']} @ ${item['price']}")
        else:
            print_error("Cart should have at least 1 item")
    else:
        print_error(f"Failed to get cart: {response.text}")
    
    # Test 4: Update Cart Item Quantity
    print_test("4. Update Cart Item Quantity")
    if 'CART_ITEM_ID' not in globals():
        print_error("No cart_item_id available, skipping update test")
    else:
        response = requests.post(
            f"{BASE_URL}/cart/update",
            json={
                "user_id": TEST_USER_ID,
                "cart_item_id": CART_ITEM_ID,
                "quantity": 5
            }
        )
        print_response(response)
        
        if response.status_code == 200:
            print_success("Update cart item works!")
            cart_data = response.json()
            items = cart_data.get("items", [])
            if items:
                updated_item = items[0]
                if updated_item["quantity"] == 5:
                    print_success(f"Quantity updated to {updated_item['quantity']} ✅")
                else:
                    print_error(f"Quantity should be 5 but is {updated_item['quantity']}")
        else:
            print_error(f"Failed to update cart: {response.text}")
    
    # Test 5: Remove from Cart
    print_test("5. Remove Item from Cart")
    if 'CART_ITEM_ID' not in globals():
        print_error("No cart_item_id available, skipping remove test")
    else:
        response = requests.post(
            f"{BASE_URL}/cart/remove",
            json={
                "user_id": TEST_USER_ID,
                "cart_item_id": CART_ITEM_ID
            }
        )
        print_response(response)
        
        if response.status_code == 200:
            print_success("Remove from cart works!")
            cart_data = response.json()
            items = cart_data.get("items", [])
            print(f"📊 Cart now has {len(items)} items")
        else:
            print_error(f"Failed to remove from cart: {response.text}")
    
    # Test 6: Clear Cart
    print_test("6. Clear Cart")
    response = requests.post(
        f"{BASE_URL}/cart/clear",
        json={"user_id": TEST_USER_ID}
    )
    print_response(response)
    
    if response.status_code == 200:
        print_success("Clear cart works!")
        cart_data = response.json()
        items = cart_data.get("items", [])
        if len(items) == 0:
            print_success("Cart is now empty ✅")
        else:
            print_error(f"Cart should be empty but has {len(items)} items")
    else:
        print_error(f"Failed to clear cart: {response.text}")
        return False
    
    return True

# ==================== Cart Tests (Legacy JWT) ====================

def test_cart_jwt_api(token: str):
    """Test legacy JWT-based cart endpoints"""
    print_section("CART API TESTS (Legacy JWT)")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Get Cart (JWT)
    print_test("1. Get Cart (JWT)")
    response = requests.get(
        f"{BASE_URL}/cart/",
        headers=headers
    )
    print_response(response)
    
    if response.status_code == 200:
        print_success("JWT Get cart works!")
        cart_data = response.json()
        print(f"📊 Cart has {len(cart_data.get('items', []))} items")
    else:
        print_error(f"Failed to get cart with JWT: {response.text}")
        return False
    
    # Test 2: Add to Cart (JWT)
    print_test("2. Add to Cart (JWT)")
    response = requests.post(
        f"{BASE_URL}/cart/items",
        headers=headers,
        json={
            "sku_id": TEST_SKU_ID,
            "quantity": 1
        }
    )
    print_response(response)
    
    if response.status_code == 200:
        print_success("JWT Add to cart works!")
        cart_data = response.json()
        items = cart_data.get("items", [])
        print(f"📊 Cart now has {len(items)} item(s)")
        
        # Save item_id for deletion
        if items:
            global JWT_CART_ITEM_ID
            JWT_CART_ITEM_ID = items[0]["id"]
    else:
        print_error(f"Failed to add to cart with JWT: {response.text}")
        return False
    
    # Test 3: Get Cart Items (JWT)
    print_test("3. Get Cart Items (JWT)")
    response = requests.get(
        f"{BASE_URL}/cart/items",
        headers=headers
    )
    print_response(response)
    
    if response.status_code == 200:
        print_success("JWT Get cart items works!")
    else:
        print_error(f"Failed to get cart items with JWT: {response.text}")
    
    # Test 4: Update Cart Item (JWT)
    print_test("4. Update Cart Item (JWT)")
    if 'JWT_CART_ITEM_ID' not in globals():
        print_error("No cart_item_id available")
    else:
        response = requests.put(
            f"{BASE_URL}/cart/items/{JWT_CART_ITEM_ID}?quantity=3",
            headers=headers
        )
        print_response(response)
        
        if response.status_code == 200:
            print_success("JWT Update cart item works!")
        else:
            print_error(f"Failed to update cart with JWT: {response.text}")
    
    # Test 5: Delete Cart Item (JWT)
    print_test("5. Delete Cart Item (JWT)")
    if 'JWT_CART_ITEM_ID' not in globals():
        print_error("No cart_item_id available")
    else:
        response = requests.delete(
            f"{BASE_URL}/cart/items/{JWT_CART_ITEM_ID}",
            headers=headers
        )
        print_response(response)
        
        if response.status_code == 200:
            print_success("JWT Delete cart item works!")
        else:
            print_error(f"Failed to delete cart item with JWT: {response.text}")
    
    # Test 6: Clear Cart (JWT)
    print_test("6. Clear Cart (JWT)")
    response = requests.delete(
        f"{BASE_URL}/cart/",
        headers=headers
    )
    print_response(response)
    
    if response.status_code == 200:
        print_success("JWT Clear cart works!")
    else:
        print_error(f"Failed to clear cart with JWT: {response.text}")
    
    return True

# ==================== Error Handling Tests ====================

def test_error_handling():
    """Test error scenarios"""
    print_section("ERROR HANDLING TESTS")
    
    # Test 1: Invalid user_id
    print_test("1. Invalid user_id (should return 404)")
    response = requests.post(
        f"{BASE_URL}/wishlist/get",
        json={"user_id": 999999}
    )
    print_response(response)
    
    if response.status_code == 404:
        print_success("Correctly returns 404 for invalid user_id ✅")
    else:
        print_error(f"Expected 404, got {response.status_code}")
    
    # Test 2: Invalid product_id
    print_test("2. Invalid product_id (should return 404)")
    response = requests.post(
        f"{BASE_URL}/wishlist/add",
        json={
            "user_id": TEST_USER_ID,
            "product_id": 999999
        }
    )
    print_response(response)
    
    if response.status_code == 404:
        print_success("Correctly returns 404 for invalid product_id ✅")
    else:
        print_error(f"Expected 404, got {response.status_code}")
    
    # Test 3: Missing required field
    print_test("3. Missing user_id (should return 422)")
    response = requests.post(
        f"{BASE_URL}/cart/add",
        json={
            "sku_id": TEST_SKU_ID,
            "quantity": 1
        }
    )
    print_response(response)
    
    if response.status_code == 422:
        print_success("Correctly returns 422 for missing field ✅")
    else:
        print_error(f"Expected 422, got {response.status_code}")

# ==================== Main Test Runner ====================

def main():
    """Run all integration tests"""
    print("\n" + "="*70)
    print("  🧪 CART & WISHLIST INTEGRATION TESTS")
    print("="*70)
    print(f"\n📍 Testing against: {BASE_URL}")
    print(f"👤 Test User ID: {TEST_USER_ID}")
    print(f"📦 Test Product ID: {TEST_PRODUCT_ID}")
    print(f"🏷️  Test SKU ID: {TEST_SKU_ID}")
    
    input("\n⚠️  Press Enter to start tests (Ctrl+C to cancel)...")
    
    results = {
        "wishlist": False,
        "cart_stateless": False,
        "cart_jwt": False,
        "error_handling": False
    }
    
    try:
        # Test 1: Wishlist API (Stateless)
        results["wishlist"] = test_wishlist_api()
        
        # Test 2: Cart API (Stateless)
        results["cart_stateless"] = test_cart_stateless_api()
        
        # Test 3: Cart API (Legacy JWT) - Optional
        print("\n" + "="*70)
        test_jwt = input("🔐 Test legacy JWT endpoints? (requires SMS verification) [y/N]: ").lower()
        if test_jwt == 'y':
            token = get_auth_token(TEST_PHONE_KG)
            if token:
                results["cart_jwt"] = test_cart_jwt_api(token)
        
        # Test 4: Error Handling
        results["error_handling"] = test_error_handling()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    
    # Print summary
    print_section("TEST SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status:12} - {test_name}")
    
    print(f"\n{'='*70}")
    print(f"  TOTAL: {passed_tests}/{total_tests} test suites passed")
    print(f"{'='*70}\n")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! APIs are working correctly!")
    else:
        print(f"⚠️  {total_tests - passed_tests} test suite(s) failed")

if __name__ == "__main__":
    # Configuration prompts
    print("\n🔧 CONFIGURATION")
    print("="*70)
    
    use_local = input("Use local server? [y/N]: ").lower()
    if use_local == 'y':
        BASE_URL = "http://localhost:8000/api/v1"
    
    print(f"\n📍 Using: {BASE_URL}")
    
    custom_user = input(f"Enter test user_id (default: {TEST_USER_ID}): ").strip()
    if custom_user:
        TEST_USER_ID = int(custom_user)
    
    custom_product = input(f"Enter test product_id (default: {TEST_PRODUCT_ID}): ").strip()
    if custom_product:
        TEST_PRODUCT_ID = int(custom_product)
    
    custom_sku = input(f"Enter test sku_id (default: {TEST_SKU_ID}): ").strip()
    if custom_sku:
        TEST_SKU_ID = int(custom_sku)
    
    main()

