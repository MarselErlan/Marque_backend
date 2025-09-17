#!/usr/bin/env python3
"""
Test script to verify database saving functionality
Tests if users are saved to correct market databases based on phone numbers
"""

import requests
import json
import time
from datetime import datetime

def test_database_saving():
    """Test if users are saved to correct databases"""
    print("🧪 Testing Database Saving Functionality")
    print("=" * 60)
    
    base_url = "https://marque.website/api/v1/auth"
    
    # Test cases: phone number -> expected market -> expected database
    test_cases = [
        {
            "phone": "+13473926894",  # US number
            "expected_market": "us",
            "expected_db": "marque_db_us",
            "expected_language": "en",
            "expected_country": "United States"
        },
        {
            "phone": "+996555123456",  # KG number
            "expected_market": "kg", 
            "expected_db": "marque_db_kg",
            "expected_language": "ru",
            "expected_country": "Kyrgyzstan"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📱 Test {i}: {test_case['phone']}")
        print(f"   Expected Market: {test_case['expected_market']}")
        print(f"   Expected Database: {test_case['expected_db']}")
        print(f"   Expected Language: {test_case['expected_language']}")
        print(f"   Expected Country: {test_case['expected_country']}")
        
        try:
            # Step 1: Send verification code
            print("   Step 1: Sending verification code...")
            send_response = requests.post(f"{base_url}/send-verification", 
                json={"phone": test_case['phone']},
                headers={"Content-Type": "application/json"}
            )
            
            if send_response.status_code == 200:
                send_data = send_response.json()
                print(f"   ✅ Code sent successfully")
                
                # Check market detection in send response
                if 'market' in send_data.get('data', {}):
                    detected_market = send_data['data']['market']
                    if detected_market == test_case['expected_market']:
                        print(f"   ✅ Market detection correct: {detected_market}")
                    else:
                        print(f"   ❌ Market detection failed: expected {test_case['expected_market']}, got {detected_market}")
                else:
                    print(f"   ⚠️ Market not detected in send response")
                
                # Step 2: Simulate verification (we'll use a demo code)
                print("   Step 2: Simulating verification...")
                print("   ⚠️ Note: This will fail verification but we can check the logs")
                
                verify_response = requests.post(f"{base_url}/verify-code", 
                    json={
                        "phone": test_case['phone'], 
                        "code": "123456"  # This will fail, but we can check the process
                    },
                    headers={"Content-Type": "application/json"}
                )
                
                print(f"   📊 Verify response status: {verify_response.status_code}")
                
                if verify_response.status_code == 200:
                    verify_data = verify_response.json()
                    print(f"   ✅ Verification successful!")
                    
                    # Check user data in response
                    user_data = verify_data.get('data', {}).get('user', {})
                    if user_data:
                        print(f"   📋 User data received:")
                        print(f"      - ID: {user_data.get('id', 'N/A')}")
                        print(f"      - Phone: {user_data.get('phone', 'N/A')}")
                        print(f"      - Market: {user_data.get('market', 'N/A')}")
                        print(f"      - Language: {user_data.get('language', 'N/A')}")
                        print(f"      - Country: {user_data.get('country', 'N/A')}")
                        print(f"      - Is New User: {user_data.get('is_new_user', 'N/A')}")
                        
                        # Validate response data
                        if user_data.get('market') == test_case['expected_market']:
                            print(f"   ✅ Market in response is correct")
                        else:
                            print(f"   ❌ Market in response is wrong")
                            
                        if user_data.get('language') == test_case['expected_language']:
                            print(f"   ✅ Language is correct")
                        else:
                            print(f"   ❌ Language is wrong: expected {test_case['expected_language']}, got {user_data.get('language')}")
                            
                        if user_data.get('country') == test_case['expected_country']:
                            print(f"   ✅ Country is correct")
                        else:
                            print(f"   ❌ Country is wrong: expected {test_case['expected_country']}, got {user_data.get('country')}")
                    else:
                        print(f"   ❌ No user data in response")
                else:
                    print(f"   ❌ Verification failed: {verify_response.status_code}")
                    print(f"   📄 Error: {verify_response.text}")
                
            else:
                print(f"   ❌ Failed to send code: {send_response.status_code}")
                print(f"   📄 Error: {send_response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print(f"\n🎯 Summary:")
    print(f"   - Check Railway logs for database operation messages")
    print(f"   - Look for: '✅ Created new user in [market] database: [id]'")
    print(f"   - Verify users are in correct database tables")
    print(f"   - Check that market, language, and country are set correctly")

def test_api_health():
    """Test API health and version"""
    print(f"\n🏥 API Health Check")
    print("=" * 30)
    
    try:
        response = requests.get("https://marque.website/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"   ✅ API is healthy")
            print(f"   📊 Version: {health_data.get('version', 'Unknown')}")
            print(f"   📊 SMS Provider: {health_data.get('sms_provider', 'Unknown')}")
            print(f"   📊 SMS Configured: {health_data.get('sms_configured', 'Unknown')}")
        else:
            print(f"   ❌ API health check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error checking API health: {e}")

def check_deployment_status():
    """Check if the latest version is deployed"""
    print(f"\n🚀 Deployment Status Check")
    print("=" * 35)
    
    try:
        response = requests.get("https://marque.website/openapi.json")
        if response.status_code == 200:
            api_info = response.json()
            version = api_info.get('info', {}).get('version', 'Unknown')
            print(f"   📊 Current API Version: {version}")
            
            if version >= "1.0.9":
                print(f"   ✅ Latest database integration version is deployed!")
                return True
            else:
                print(f"   ⚠️ Older version deployed, waiting for 1.0.9...")
                return False
        else:
            print(f"   ❌ Failed to get API info: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error checking deployment: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Database Saving Test Suite")
    print("=" * 50)
    
    # Check deployment status first
    if check_deployment_status():
        test_api_health()
        test_database_saving()
    else:
        print(f"\n⏳ Waiting for version 1.0.9 to deploy...")
        print(f"   The database integration fix is not yet live.")
        print(f"   Please wait for Railway to deploy the latest version.")
l