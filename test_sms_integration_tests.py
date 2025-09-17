#!/usr/bin/env python3
"""
Integration Tests for SMS/Twilio Functionality
End-to-end tests for SMS verification with real API calls
"""

import pytest
import requests
import json
import time
from unittest.mock import patch
import os


class TestSMSIntegration:
    """Integration tests for SMS functionality"""
    
    def setup_method(self):
        """Setup for integration tests"""
        self.base_url = "https://marque.website"
        self.test_phone = "+13473926894"
        self.session = requests.Session()
    
    def test_api_health_check(self):
        """Test API health and SMS configuration"""
        response = self.session.get(f"{self.base_url}/health")
        assert response.status_code == 200
        
        data = response.json()
        print(f"📊 Health Check Response:")
        print(f"   Status: {data['status']}")
        print(f"   SMS Provider: {data['sms_provider']}")
        print(f"   SMS Configured: {data['sms_configured']}")
        
        assert "sms_provider" in data
        assert "sms_configured" in data
    
    def test_debug_environment_endpoint(self):
        """Test debug environment endpoint"""
        response = self.session.get(f"{self.base_url}/debug/env")
        assert response.status_code == 200
        
        data = response.json()
        print(f"🔍 Debug Environment Response:")
        for key, value in data.items():
            print(f"   {key}: {value}")
        
        assert "TWILIO_ACCOUNT_SID" in data
        assert "TWILIO_AUTH_TOKEN" in data
        assert "TWILIO_VERIFY_SERVICE_SID" in data
        assert "TWILIO_READY" in data
        assert "TWILIO_AVAILABLE" in data
    
    def test_phone_validation(self):
        """Test phone number validation"""
        payload = {"phone": self.test_phone}
        response = self.session.post(
            f"{self.base_url}/api/v1/validate-phone",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        print(f"📱 Phone Validation Response:")
        print(f"   Phone: {data['phone']}")
        print(f"   Market: {data['market']}")
        print(f"   Message: {data['message']}")
        
        assert data["phone"] == self.test_phone
        assert data["market"] == "us"
    
    def test_send_verification_integration(self):
        """Test sending verification code end-to-end"""
        payload = {"phone": self.test_phone}
        response = self.session.post(
            f"{self.base_url}/api/v1/auth/send-verification",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        print(f"📤 Send Verification Response:")
        print(f"   Success: {data['success']}")
        print(f"   Phone: {data['phone_number']}")
        print(f"   Message: {data['message']}")
        
        assert data["success"] is True
        assert data["phone_number"] == self.test_phone
    
    def test_verify_code_integration(self):
        """Test verifying code end-to-end"""
        # First send verification code
        send_payload = {"phone": self.test_phone}
        send_response = self.session.post(
            f"{self.base_url}/api/v1/auth/send-verification",
            json=send_payload,
            headers={"Content-Type": "application/json"}
        )
        assert send_response.status_code == 200
        
        # Then verify with demo code
        verify_payload = {
            "phone": self.test_phone,
            "code": "123456"  # Demo code
        }
        verify_response = self.session.post(
            f"{self.base_url}/api/v1/auth/verify-code",
            json=verify_payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert verify_response.status_code == 200
        data = verify_response.json()
        print(f"✅ Verify Code Response:")
        print(f"   Success: {data['success']}")
        print(f"   Token Type: {data['token_type']}")
        print(f"   Expires In: {data['expires_in']}")
        
        assert data["success"] is True
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        
        return data["access_token"]
    
    def test_profile_access_with_token(self):
        """Test accessing profile with JWT token"""
        # Get token from verification
        token = self.test_verify_code_integration()
        
        # Access profile with token
        headers = {"Authorization": f"Bearer {token}"}
        response = self.session.get(
            f"{self.base_url}/api/v1/auth/profile",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        print(f"👤 Profile Response:")
        print(f"   Phone: {data['phone_number']}")
        print(f"   Market: {data['market']}")
        
        assert data["phone_number"] == self.test_phone
    
    def test_invalid_phone_number(self):
        """Test with invalid phone number"""
        payload = {"phone": "invalid_phone"}
        response = self.session.post(
            f"{self.base_url}/api/v1/validate-phone",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_invalid_verification_code(self):
        """Test with invalid verification code"""
        payload = {
            "phone": self.test_phone,
            "code": "invalid_code"
        }
        response = self.session.post(
            f"{self.base_url}/api/v1/auth/verify-code",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422  # Validation error


class TestSMSConfigurationDiagnosis:
    """Diagnostic tests for SMS configuration issues"""
    
    def setup_method(self):
        """Setup for diagnostic tests"""
        self.base_url = "https://marque.website"
        self.session = requests.Session()
    
    def test_sms_configuration_diagnosis(self):
        """Comprehensive SMS configuration diagnosis"""
        print("🔍 SMS Configuration Diagnosis")
        print("=" * 50)
        
        # Test health endpoint
        health_response = self.session.get(f"{self.base_url}/health")
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ Health Check: {health_data['status']}")
            print(f"📱 SMS Provider: {health_data['sms_provider']}")
            print(f"🔧 SMS Configured: {health_data['sms_configured']}")
            
            if not health_data['sms_configured']:
                print("⚠️  SMS is not configured - running in demo mode")
            else:
                print("✅ SMS is properly configured")
        else:
            print(f"❌ Health check failed: {health_response.status_code}")
        
        # Test debug endpoint
        debug_response = self.session.get(f"{self.base_url}/debug/env")
        if debug_response.status_code == 200:
            debug_data = debug_response.json()
            print(f"\n🔍 Environment Variables Status:")
            print(f"   TWILIO_AVAILABLE: {debug_data['TWILIO_AVAILABLE']}")
            print(f"   TWILIO_READY: {debug_data['TWILIO_READY']}")
            print(f"   TWILIO_ACCOUNT_SID: {debug_data['TWILIO_ACCOUNT_SID']}")
            print(f"   TWILIO_AUTH_TOKEN: {debug_data['TWILIO_AUTH_TOKEN']}")
            print(f"   TWILIO_VERIFY_SERVICE_SID: {debug_data['TWILIO_VERIFY_SERVICE_SID']}")
            
            # Analyze configuration
            missing_vars = []
            if debug_data['TWILIO_ACCOUNT_SID'] == "❌ Missing":
                missing_vars.append("TWILIO_ACCOUNT_SID")
            if debug_data['TWILIO_AUTH_TOKEN'] == "❌ Missing":
                missing_vars.append("TWILIO_AUTH_TOKEN")
            if debug_data['TWILIO_VERIFY_SERVICE_SID'] == "❌ Missing":
                missing_vars.append("TWILIO_VERIFY_SERVICE_SID")
            
            if missing_vars:
                print(f"\n❌ Missing Environment Variables: {', '.join(missing_vars)}")
                print("💡 Solution: Add these variables to Railway dashboard")
            else:
                print(f"\n✅ All required environment variables are present")
                
        else:
            print(f"❌ Debug endpoint failed: {debug_response.status_code}")
    
    def test_twilio_service_status(self):
        """Test Twilio service connectivity"""
        print(f"\n🌐 Testing Twilio Service Connectivity")
        print("=" * 50)
        
        # Test if we can reach Twilio API
        try:
            # This is a simple connectivity test
            twilio_response = self.session.get("https://api.twilio.com", timeout=10)
            print(f"✅ Twilio API reachable: {twilio_response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Twilio API not reachable: {e}")
    
    def test_sms_functionality_end_to_end(self):
        """Test complete SMS functionality"""
        print(f"\n🧪 Testing SMS Functionality End-to-End")
        print("=" * 50)
        
        test_phone = "+13473926894"
        
        # Step 1: Validate phone
        validate_payload = {"phone": test_phone}
        validate_response = self.session.post(
            f"{self.base_url}/api/v1/validate-phone",
            json=validate_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if validate_response.status_code == 200:
            print("✅ Phone validation: PASSED")
        else:
            print(f"❌ Phone validation: FAILED ({validate_response.status_code})")
            return
        
        # Step 2: Send verification
        send_payload = {"phone": test_phone}
        send_response = self.session.post(
            f"{self.base_url}/api/v1/auth/send-verification",
            json=send_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if send_response.status_code == 200:
            send_data = send_response.json()
            print(f"✅ Send verification: PASSED ({send_data['message']})")
        else:
            print(f"❌ Send verification: FAILED ({send_response.status_code})")
            return
        
        # Step 3: Verify code
        verify_payload = {
            "phone": test_phone,
            "code": "123456"  # Demo code
        }
        verify_response = self.session.post(
            f"{self.base_url}/api/v1/auth/verify-code",
            json=verify_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if verify_response.status_code == 200:
            verify_data = verify_response.json()
            print(f"✅ Verify code: PASSED (Token generated)")
            
            # Step 4: Test profile access
            token = verify_data.get("access_token")
            if token:
                headers = {"Authorization": f"Bearer {token}"}
                profile_response = self.session.get(
                    f"{self.base_url}/api/v1/auth/profile",
                    headers=headers
                )
                
                if profile_response.status_code == 200:
                    print("✅ Profile access: PASSED")
                    print("🎉 Complete SMS flow: WORKING")
                else:
                    print(f"❌ Profile access: FAILED ({profile_response.status_code})")
            else:
                print("❌ No access token received")
        else:
            print(f"❌ Verify code: FAILED ({verify_response.status_code})")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
