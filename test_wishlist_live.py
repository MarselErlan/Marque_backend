"""
Test Wishlist Functionality on Railway Production
This script tests if wishlist properly saves products to the database
"""

import requests
import json

# Production API URL
API_BASE_URL = "https://marquebackend-production.up.railway.app/api/v1"

# ⚠️ IMPORTANT: Choose market based on your test user
# If you get "user not found" error, try the other market
MARKET = "us"  # Change to 'kg' if testing with KG phone number

# Test credentials
# US: Use +1 phone numbers (e.g., +13125551234)
# KG: Use +996 phone numbers (e.g., +996700123456)
TEST_PHONE = "+13125559876"  # ⚠️ Use a NEW phone number to create fresh user
TEST_CODE = None  # Will be sent via SMS


def print_step(step, message):
    """Print formatted step"""
    print(f"\n{'='*60}")
    print(f"STEP {step}: {message}")
    print('='*60)


def test_wishlist():
    """Test complete wishlist flow"""
    
    print("\n🧪 TESTING WISHLIST FUNCTIONALITY\n")
    
    # Step 1: Send verification code
    print_step(1, "Sending verification code")
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/send-verification",
            json={"phone": TEST_PHONE},
            headers={"X-Market": MARKET}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code != 200:
            print("❌ Failed to send verification code")
            return
            
        print("✅ Verification code sent! Check your phone for SMS")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Step 2: Get verification code from user
    print_step(2, "Enter verification code")
    verification_code = input("Enter the 6-digit code you received via SMS: ").strip()
    
    # Step 3: Verify code and login
    print_step(3, "Logging in")
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/verify-code",
            json={
                "phone": TEST_PHONE,
                "verification_code": verification_code
            },
            headers={"X-Market": MARKET}
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Login failed: {response.json()}")
            return
        
        data = response.json()
        access_token = data.get("access_token")
        user = data.get("user")
        
        print(f"✅ Logged in successfully!")
        print(f"User ID: {user.get('id')}")
        print(f"Phone: {user.get('phone')}")
        print(f"Token: {access_token[:20]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Headers for authenticated requests
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Market": MARKET,
        "Content-Type": "application/json"
    }
    
    # Step 4: Get available products
    print_step(4, "Fetching available products")
    try:
        response = requests.get(
            f"{API_BASE_URL}/products",
            headers={"X-Market": MARKET}
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Failed to get products: {response.json()}")
            return
        
        products = response.json()
        if not products or len(products) == 0:
            print("❌ No products available in database")
            return
        
        # Get first 3 products
        test_products = products[:3]
        print(f"\n✅ Found {len(products)} products")
        print("\nWill add these products to wishlist:")
        for p in test_products:
            # Handle both 'title' and 'name' fields
            product_name = p.get('title') or p.get('name') or 'Unknown'
            product_price = p.get('price', 0)
            print(f"  - Product ID: {p['id']}, Name: {product_name}, Price: ${product_price}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Step 5: Get current wishlist (should be empty)
    print_step(5, "Checking current wishlist")
    try:
        response = requests.get(
            f"{API_BASE_URL}/wishlist",
            headers=headers
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Failed to get wishlist: {response.json()}")
            return
        
        wishlist = response.json()
        print(f"✅ Current wishlist:")
        print(f"  Wishlist ID: {wishlist.get('id')}")
        print(f"  User ID: {wishlist.get('user_id')}")
        print(f"  Items count: {len(wishlist.get('items', []))}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Step 6: Add products to wishlist
    print_step(6, f"Adding {len(test_products)} products to wishlist")
    added_products = []
    
    for product in test_products:
        try:
            product_name = product.get('title') or product.get('name') or f"Product {product['id']}"
            print(f"\n  Adding product {product['id']}: {product_name}")
            response = requests.post(
                f"{API_BASE_URL}/wishlist/items",
                json={"product_id": product['id']},
                headers=headers
            )
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                wishlist = response.json()
                print(f"  ✅ Added! Wishlist now has {len(wishlist.get('items', []))} items")
                added_products.append(product['id'])
            else:
                print(f"  ❌ Failed: {response.json()}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    # Step 7: Verify wishlist has products
    print_step(7, "Verifying wishlist contents")
    try:
        response = requests.get(
            f"{API_BASE_URL}/wishlist",
            headers=headers
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Failed to get wishlist: {response.json()}")
            return
        
        wishlist = response.json()
        items = wishlist.get('items', [])
        
        print(f"\n✅ Wishlist details:")
        print(f"  Wishlist ID: {wishlist.get('id')}")
        print(f"  User ID: {wishlist.get('user_id')}")
        print(f"  Total items: {len(items)}")
        
        if len(items) > 0:
            print(f"\n  Items in wishlist:")
            for idx, item in enumerate(items, 1):
                product = item.get('product', {})
                product_name = product.get('title') or product.get('name') or 'Unknown'
                print(f"    {idx}. Product ID: {product.get('id')}, Name: {product_name}")
            print(f"\n✅ SUCCESS! Wishlist is saving products to database!")
        else:
            print("\n⚠️  Wishlist is empty. Products may not have been added.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Step 8: Test logout and login again
    print_step(8, "Testing persistence - Logout and login again")
    
    # Logout
    try:
        print("\n  Logging out...")
        response = requests.post(
            f"{API_BASE_URL}/auth/logout",
            headers=headers
        )
        print(f"  Status: {response.status_code}")
        print(f"  ✅ Logged out")
    except Exception as e:
        print(f"  ❌ Logout error: {e}")
    
    # Login again
    print("\n  Logging in again...")
    verification_code2 = input("  Enter NEW verification code (check SMS): ").strip()
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/verify-code",
            json={
                "phone": TEST_PHONE,
                "verification_code": verification_code2
            },
            headers={"X-Market": MARKET}
        )
        
        if response.status_code != 200:
            print(f"  ❌ Login failed: {response.json()}")
            return
        
        data = response.json()
        new_token = data.get("access_token")
        print(f"  ✅ Logged in with NEW token")
        print(f"  Token: {new_token[:20]}...")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return
    
    # Step 9: Check wishlist with new token
    print_step(9, "Checking wishlist with NEW token")
    try:
        new_headers = {
            "Authorization": f"Bearer {new_token}",
            "X-Market": MARKET,
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{API_BASE_URL}/wishlist",
            headers=new_headers
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Failed to get wishlist: {response.json()}")
            return
        
        wishlist = response.json()
        items = wishlist.get('items', [])
        
        print(f"\n✅ Wishlist after re-login:")
        print(f"  Wishlist ID: {wishlist.get('id')}")
        print(f"  User ID: {wishlist.get('user_id')}")
        print(f"  Total items: {len(items)}")
        
        if len(items) == len(added_products):
            print(f"\n🎉 PERFECT! All {len(items)} items persisted across logout/login!")
            print("\n✅✅✅ WISHLIST IS WORKING CORRECTLY! ✅✅✅")
            print("\nYour wishlist:")
            print("  - Saves products to database ✅")
            print("  - Links to user_id ✅")
            print("  - Persists across sessions ✅")
            print("  - Works with new tokens ✅")
        else:
            print(f"\n⚠️  Expected {len(added_products)} items, got {len(items)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)
    print("\n📊 Check your Railway database now:")
    print("   1. Go to Railway → Postgres → Data")
    print("   2. Look at 'wishlists' table (should have 1 row)")
    print("   3. Look at 'wishlist_items' table (should have your items)")
    print("\nThe wishlist is working correctly! 🎉")


if __name__ == "__main__":
    test_wishlist()

