#!/usr/bin/env python3
"""
Test script for the NEW wishlist API design
Uses user_id and product_id directly in request body
"""

import requests
import json
import sys
from typing import Dict, Any

# Configuration
API_BASE_URL = "https://marquebackend-production.up.railway.app/api/v1"

def make_request(method: str, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Make HTTP request and return response"""
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, timeout=30)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, timeout=30)
        elif method.upper() == "DELETE":
            response = requests.delete(url, json=data, timeout=30)
        else:
            return {"error": f"Unsupported method: {method}"}
        
        return {
            "status": response.status_code,
            "data": response.json() if response.content else {}
        }
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

def test_new_wishlist_api():
    """Test the new wishlist API design"""
    print("🧪 TESTING NEW WISHLIST API DESIGN")
    print("=" * 60)
    
    # Test user and product IDs
    TEST_USER_ID = 19  # User from KG database
    TEST_PRODUCT_ID = 297  # First product
    
    print(f"Testing with User ID: {TEST_USER_ID}")
    print(f"Testing with Product ID: {TEST_PRODUCT_ID}")
    print()
    
    # Step 1: Get wishlist (should create empty wishlist if doesn't exist)
    print("STEP 1: Get wishlist")
    print("-" * 30)
    result = make_request("POST", "/wishlist/get", {"user_id": TEST_USER_ID})
    print(f"Status: {result.get('status', 'ERROR')}")
    print(f"Response: {json.dumps(result.get('data', {}), indent=2)}")
    
    if result.get('status') == 200:
        print("✅ Successfully got wishlist")
        wishlist_data = result.get('data', {})
        print(f"Wishlist ID: {wishlist_data.get('id')}")
        print(f"User ID: {wishlist_data.get('user_id')}")
        print(f"Items count: {len(wishlist_data.get('items', []))}")
    else:
        print("❌ Failed to get wishlist")
        return
    
    print()
    
    # Step 2: Add product to wishlist
    print("STEP 2: Add product to wishlist")
    print("-" * 30)
    result = make_request("POST", "/wishlist/add", {
        "user_id": TEST_USER_ID,
        "product_id": TEST_PRODUCT_ID
    })
    print(f"Status: {result.get('status', 'ERROR')}")
    print(f"Response: {json.dumps(result.get('data', {}), indent=2)}")
    
    if result.get('status') == 200:
        print("✅ Successfully added product to wishlist")
        wishlist_data = result.get('data', {})
        items = wishlist_data.get('items', [])
        print(f"Items count: {len(items)}")
        if items:
            first_item = items[0]
            product = first_item.get('product', {})
            print(f"Product name: {product.get('name', 'N/A')}")
            print(f"Product price: {product.get('price', 'N/A')}")
    else:
        print("❌ Failed to add product to wishlist")
        return
    
    print()
    
    # Step 3: Get wishlist again (should show the added product)
    print("STEP 3: Get wishlist again")
    print("-" * 30)
    result = make_request("POST", "/wishlist/get", {"user_id": TEST_USER_ID})
    print(f"Status: {result.get('status', 'ERROR')}")
    print(f"Response: {json.dumps(result.get('data', {}), indent=2)}")
    
    if result.get('status') == 200:
        print("✅ Successfully got updated wishlist")
        wishlist_data = result.get('data', {})
        items = wishlist_data.get('items', [])
        print(f"Items count: {len(items)}")
        if items:
            print("Products in wishlist:")
            for i, item in enumerate(items, 1):
                product = item.get('product', {})
                print(f"  {i}. {product.get('name', 'N/A')} - ${product.get('price', 'N/A')}")
    else:
        print("❌ Failed to get updated wishlist")
        return
    
    print()
    
    # Step 4: Remove product from wishlist
    print("STEP 4: Remove product from wishlist")
    print("-" * 30)
    result = make_request("POST", "/wishlist/remove", {
        "user_id": TEST_USER_ID,
        "product_id": TEST_PRODUCT_ID
    })
    print(f"Status: {result.get('status', 'ERROR')}")
    print(f"Response: {json.dumps(result.get('data', {}), indent=2)}")
    
    if result.get('status') == 200:
        print("✅ Successfully removed product from wishlist")
        wishlist_data = result.get('data', {})
        items = wishlist_data.get('items', [])
        print(f"Items count: {len(items)}")
    else:
        print("❌ Failed to remove product from wishlist")
        return
    
    print()
    
    # Step 5: Test error handling
    print("STEP 5: Test error handling")
    print("-" * 30)
    
    # Test with non-existent user
    print("Testing with non-existent user (ID: 99999):")
    result = make_request("POST", "/wishlist/get", {"user_id": 99999})
    print(f"Status: {result.get('status', 'ERROR')}")
    print(f"Response: {json.dumps(result.get('data', {}), indent=2)}")
    
    # Test with non-existent product
    print("\nTesting with non-existent product (ID: 99999):")
    result = make_request("POST", "/wishlist/add", {
        "user_id": TEST_USER_ID,
        "product_id": 99999
    })
    print(f"Status: {result.get('status', 'ERROR')}")
    print(f"Response: {json.dumps(result.get('data', {}), indent=2)}")
    
    print()
    print("🎉 NEW WISHLIST API TEST COMPLETED!")
    print("=" * 60)

if __name__ == "__main__":
    test_new_wishlist_api()
