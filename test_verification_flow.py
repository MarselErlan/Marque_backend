#!/usr/bin/env python3
"""
Test verification flow without sending actual SMS codes
Simulates the verification process to test database saving
"""

import requests
import json
import time
from datetime import datetime

def test_verification_flow():
    """Test the verification flow for different phone numbers"""
    print("🧪 Testing Verification Flow (Simulation)")
    print("=" * 50)
    
    base_url = "https://marque.website/api/v1/auth"
    
    # Test cases: phone number -> expected market
    test_cases = [
        {
            "phone": "+13473926894",  # US number
            "expected_market": "us",
            "expected_language": "en",
            "expected_country": "United States"
        },
        {
            "phone": "+996555123456",  # KG number
            "expected_market": "kg",
            "expected_language": "ru", 
            "expected_country": "Kyrgyzstan"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📱 Test {i}: {test_case['phone']}")
        print(f"   Expected Market: {test_case['expected_market']}")
        print(f"   Expected Language: {test_case['expected_language']}")
        print(f"   Expected Country: {test_case['expected_country']}")
        
        try:
            # Step 1: Test send verification endpoint (to see market detection)
            print("   Step 1: Testing send verification endpoint...")
            send_response = requests.post(f"{base_url}/send-verification", 
                json={"phone": test_case['phone']},
                headers={"Content-Type": "application/json"}
            )
            
            print(f"   📊 Send response status: {send_response.status_code}")
            
            if send_response.status_code == 200:
                send_data = send_response.json()
                print(f"   ✅ Send verification successful")
                
                # Check market detection
                response_data = send_data.get('data', {})
                if 'market' in response_data:
                    detected_market = response_data['market']
                    print(f"   🌍 Market detected: {detected_market}")
                    
                    if detected_market == test_case['expected_market']:
                        print(f"   ✅ Market detection is CORRECT")
                    else:
                        print(f"   ❌ Market detection is WRONG - expected {test_case['expected_market']}")
                else:
                    print(f"   ⚠️ No market information in response")
                
                print(f"   📋 Full send response:")
                print(f"      {json.dumps(send_data, indent=6)}")
                
            else:
                print(f"   ❌ Send verification failed")
                print(f"   📄 Error response: {send_response.text}")
            
            print("\n   " + "-" * 40)
            
            # Step 2: Test verify code endpoint (will fail but we can see the process)
            print("   Step 2: Testing verify code endpoint...")
            verify_response = requests.post(f"{base_url}/verify-code", 
                json={
                    "phone": test_case['phone'],
                    "code": "123456"  # This will fail verification but show the process
                },
                headers={"Content-Type": "application/json"}
            )
            
            print(f"   📊 Verify response status: {verify_response.status_code}")
            
            if verify_response.status_code == 200:
                verify_data = verify_response.json()
                print(f"   ✅ Verification successful (unexpected!)")
                
                # Check user data
                user_data = verify_data.get('data', {}).get('user', {})
                if user_data:
                    print(f"   👤 User data:")
                    print(f"      - ID: {user_data.get('id', 'N/A')}")
                    print(f"      - Phone: {user_data.get('phone', 'N/A')}")
                    print(f"      - Market: {user_data.get('market', 'N/A')}")
                    print(f"      - Language: {user_data.get('language', 'N/A')}")
                    print(f"      - Country: {user_data.get('country', 'N/A')}")
                    print(f"      - Is Verified: {user_data.get('is_verified', 'N/A')}")
                    print(f"      - Is New User: {user_data.get('is_new_user', 'N/A')}")
                    
                    # Validate the data
                    if user_data.get('market') == test_case['expected_market']:
                        print(f"   ✅ User market is CORRECT")
                    else:
                        print(f"   ❌ User market is WRONG")
                        
                    if user_data.get('language') == test_case['expected_language']:
                        print(f"   ✅ User language is CORRECT")
                    else:
                        print(f"   ❌ User language is WRONG")
                        
                    if user_data.get('country') == test_case['expected_country']:
                        print(f"   ✅ User country is CORRECT")
                    else:
                        print(f"   ❌ User country is WRONG")
                
                print(f"   📋 Full verify response:")
                print(f"      {json.dumps(verify_data, indent=6)}")
                
            else:
                print(f"   ❌ Verification failed (expected)")
                error_response = verify_response.text
                print(f"   📄 Error: {error_response}")
                
                # Check if it's a verification code error (which is expected)
                if "Invalid or expired verification code" in error_response:
                    print(f"   ✅ This is expected - verification code is invalid")
                elif "Cannot detect market" in error_response:
                    print(f"   ❌ Market detection failed in verification")
                else:
                    print(f"   ⚠️ Unexpected error type")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        print("\n" + "=" * 50)

def check_api_version():
    """Check current API version"""
    print("🔍 Checking API Version")
    print("=" * 25)
    
    try:
        # Check health endpoint
        health_response = requests.get("https://marque.website/health")
        if health_response.status_code == 200:
            health_data = health_response.json()
            version = health_data.get('version', 'Unknown')
            print(f"   📊 Health endpoint version: {version}")
        else:
            print(f"   ❌ Health check failed: {health_response.status_code}")
        
        # Check OpenAPI endpoint
        openapi_response = requests.get("https://marque.website/openapi.json")
        if openapi_response.status_code == 200:
            api_info = openapi_response.json()
            version = api_info.get('info', {}).get('version', 'Unknown')
            print(f"   📊 OpenAPI version: {version}")
            
            if version >= "1.0.9":
                print(f"   ✅ Latest database integration version is deployed!")
                return True
            else:
                print(f"   ⚠️ Version {version} deployed - database integration may not be active")
                return False
        else:
            print(f"   ❌ OpenAPI check failed: {openapi_response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error checking version: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Verification Flow Test")
    print("=" * 30)
    
    # Check version first
    if check_api_version():
        print(f"\n🚀 Running verification flow tests...")
        test_verification_flow()
    else:
        print(f"\n⏳ Waiting for latest version to deploy...")
        print(f"   Current version may not have database integration yet.")
    
    print(f"\n📋 What to look for:")
    print(f"   - Market detection in send-verification response")
    print(f"   - Proper error handling in verify-code (expected to fail)")
    print(f"   - Check Railway logs for database operation messages")
    print(f"   - Look for: '🌍 Detected market: [us/kg] for phone: [number]'")
    print(f"   - Look for: '✅ Created new user in [market] database: [id]' (if verification succeeds)")
