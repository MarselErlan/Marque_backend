#!/usr/bin/env python3
"""
Simple SMS Configuration Test
Tests the SMS configuration without complex dependencies
"""

import requests
import json


def test_sms_configuration():
    """Test SMS configuration on Railway deployment"""
    base_url = "https://marque.website"
    
    print("🔍 Testing SMS Configuration on Railway")
    print("=" * 50)
    
    try:
        # Test health endpoint
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health endpoint accessible")
            print(f"   Status: {data.get('status')}")
            print(f"   SMS Provider: {data.get('sms_provider')}")
            print(f"   SMS Configured: {data.get('sms_configured')}")
            
            if data.get('sms_configured'):
                print("🎉 SMS is properly configured!")
                return True
            else:
                print("⚠️  SMS is not configured - running in demo mode")
                
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test debug endpoint
    try:
        response = requests.get(f"{base_url}/debug/env", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"\n🔍 Environment Variables:")
            for key, value in data.items():
                print(f"   {key}: {value}")
                
            # Check what's missing
            if data.get('TWILIO_AVAILABLE') == "❌ Missing":
                print("\n❌ Issue: TWILIO_AVAILABLE is missing from debug output")
                print("💡 This suggests the Railway deployment is running old code")
                return False
                
            if data.get('TWILIO_READY') == "❌ Missing":
                print("\n❌ Issue: TWILIO_READY is missing from debug output")
                print("💡 This suggests the Railway deployment is running old code")
                return False
                
        else:
            print(f"❌ Debug endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Debug endpoint error: {e}")
        return False
    
    return False


def test_sms_functionality():
    """Test SMS functionality"""
    base_url = "https://marque.website"
    test_phone = "+13473926894"
    
    print(f"\n🧪 Testing SMS Functionality")
    print("=" * 50)
    
    try:
        # Test phone validation
        payload = {"phone": test_phone}
        response = requests.post(
            f"{base_url}/api/v1/validate-phone",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Phone validation: PASSED")
            print(f"   Phone: {data.get('phone')}")
            print(f"   Market: {data.get('market')}")
        else:
            print(f"❌ Phone validation failed: {response.status_code}")
            return False
        
        # Test send verification
        payload = {"phone": test_phone}
        response = requests.post(
            f"{base_url}/api/v1/auth/send-verification",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Send verification: PASSED")
            print(f"   Message: {data.get('message')}")
        else:
            print(f"❌ Send verification failed: {response.status_code}")
            return False
        
        # Test verify code
        payload = {
            "phone": test_phone,
            "code": "123456"  # Demo code
        }
        response = requests.post(
            f"{base_url}/api/v1/auth/verify-code",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Verify code: PASSED")
            print(f"   Success: {data.get('success')}")
            if data.get('access_token'):
                print(f"   Token generated: YES")
            return True
        else:
            print(f"❌ Verify code failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ SMS functionality error: {e}")
        return False


if __name__ == "__main__":
    print("🧪 SMS Configuration Test")
    print("=" * 60)
    
    config_ok = test_sms_configuration()
    functionality_ok = test_sms_functionality()
    
    print(f"\n📋 RESULTS")
    print("=" * 60)
    print(f"Configuration Test: {'✅ PASSED' if config_ok else '❌ FAILED'}")
    print(f"Functionality Test: {'✅ PASSED' if functionality_ok else '❌ FAILED'}")
    
    if config_ok and functionality_ok:
        print("\n🎉 All tests passed! SMS is working correctly.")
    else:
        print("\n⚠️  Issues detected. Railway deployment may need updating.")
