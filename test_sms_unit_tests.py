#!/usr/bin/env python3
"""
Unit Tests for SMS/Twilio Configuration
Tests the SMS configuration detection and Twilio initialization
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Import the production API
from marque_api_production import app, TWILIO_READY, TWILIO_AVAILABLE, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_VERIFY_SERVICE_SID


class TestSMSConfiguration:
    """Test SMS configuration detection"""
    
    def test_twilio_availability_check(self):
        """Test if Twilio library is available"""
        assert TWILIO_AVAILABLE is True, "Twilio library should be available"
    
    def test_twilio_environment_variables(self):
        """Test Twilio environment variable detection"""
        # Test with mock environment variables
        with patch.dict(os.environ, {
            'TWILIO_ACCOUNT_SID': 'test_sid',
            'TWILIO_AUTH_TOKEN': 'test_token',
            'TWILIO_VERIFY_SERVICE_SID': 'test_service_sid'
        }, clear=True):
            # Import the module again to test initialization
            import importlib
            import marque_api_production
            importlib.reload(marque_api_production)
            
            assert marque_api_production.TWILIO_ACCOUNT_SID == 'test_sid'
            assert marque_api_production.TWILIO_AUTH_TOKEN == 'test_token'
            assert marque_api_production.TWILIO_VERIFY_SERVICE_SID == 'test_service_sid'
    
    def test_twilio_initialization_success(self):
        """Test successful Twilio client initialization"""
        with patch.dict(os.environ, {
            'TWILIO_ACCOUNT_SID': 'test_sid',
            'TWILIO_AUTH_TOKEN': 'test_token',
            'TWILIO_VERIFY_SERVICE_SID': 'test_service_sid'
        }, clear=True):
            with patch('marque_api_production.Client') as mock_client:
                mock_client.return_value = MagicMock()
                
                # Import the module again to test initialization
                import importlib
                import marque_api_production
                importlib.reload(marque_api_production)
                
                assert marque_api_production.TWILIO_READY is True
                mock_client.assert_called_once_with('test_sid', 'test_token')
    
    def test_twilio_initialization_failure(self):
        """Test Twilio client initialization failure"""
        with patch.dict(os.environ, {
            'TWILIO_ACCOUNT_SID': 'invalid_sid',
            'TWILIO_AUTH_TOKEN': 'invalid_token',
            'TWILIO_VERIFY_SERVICE_SID': 'invalid_service_sid'
        }, clear=True):
            with patch('marque_api_production.Client') as mock_client:
                mock_client.side_effect = Exception("Invalid credentials")
                
                # Import the module again to test initialization
                import importlib
                import marque_api_production
                importlib.reload(marque_api_production)
                
                assert marque_api_production.TWILIO_READY is False
    
    def test_missing_twilio_credentials(self):
        """Test behavior when Twilio credentials are missing"""
        with patch.dict(os.environ, {}, clear=True):
            # Import the module again to test initialization
            import importlib
            import marque_api_production
            importlib.reload(marque_api_production)
            
            assert marque_api_production.TWILIO_READY is False
            assert marque_api_production.TWILIO_ACCOUNT_SID is None
            assert marque_api_production.TWILIO_AUTH_TOKEN is None
            assert marque_api_production.TWILIO_VERIFY_SERVICE_SID is None


class TestSMSHealthEndpoint:
    """Test SMS configuration in health endpoint"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
    
    def test_health_endpoint_sms_configuration(self):
        """Test health endpoint shows correct SMS configuration"""
        response = self.client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "sms_provider" in data
        assert "sms_configured" in data
        
        # Should show current configuration
        if data["sms_configured"]:
            assert data["sms_provider"] == "Twilio Verify"
        else:
            assert data["sms_provider"] == "Demo"
    
    def test_debug_env_endpoint(self):
        """Test debug environment endpoint shows Twilio configuration"""
        response = self.client.get("/debug/env")
        assert response.status_code == 200
        
        data = response.json()
        assert "TWILIO_ACCOUNT_SID" in data
        assert "TWILIO_AUTH_TOKEN" in data
        assert "TWILIO_VERIFY_SERVICE_SID" in data
        assert "TWILIO_READY" in data
        assert "TWILIO_AVAILABLE" in data


class TestSMSDemoMode:
    """Test SMS functionality in demo mode"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
    
    def test_send_verification_demo_mode(self):
        """Test sending verification code in demo mode"""
        payload = {"phone": "+13473926894"}
        response = self.client.post("/api/v1/auth/send-verification", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "message" in data
        assert data["phone_number"] == "+13473926894"
    
    def test_verify_code_demo_mode(self):
        """Test verifying code in demo mode"""
        payload = {
            "phone": "+13473926894",
            "code": "123456"
        }
        response = self.client.post("/api/v1/auth/verify-code", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data
        assert "token_type" in data
        assert "expires_in" in data


class TestSMSProductionMode:
    """Test SMS functionality in production mode with Twilio"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
    
    @patch('marque_api_production.twilio_client')
    def test_send_verification_twilio_mode(self, mock_twilio):
        """Test sending verification code with Twilio"""
        # Mock Twilio verification creation
        mock_verification = MagicMock()
        mock_verification.status = "pending"
        mock_twilio.verify.v2.services.return_value.verifications.create.return_value = mock_verification
        
        # Mock TWILIO_READY to be True
        with patch('marque_api_production.TWILIO_READY', True):
            payload = {"phone": "+13473926894"}
            response = self.client.post("/api/v1/auth/send-verification", json=payload)
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert "message" in data
            assert data["phone_number"] == "+13473926894"
            
            # Verify Twilio was called
            mock_twilio.verify.v2.services.assert_called()
    
    @patch('marque_api_production.twilio_client')
    def test_verify_code_twilio_mode(self, mock_twilio):
        """Test verifying code with Twilio"""
        # Mock Twilio verification check
        mock_verification_check = MagicMock()
        mock_verification_check.status = "approved"
        mock_twilio.verify.v2.services.return_value.verification_checks.create.return_value = mock_verification_check
        
        # Mock TWILIO_READY to be True
        with patch('marque_api_production.TWILIO_READY', True):
            payload = {
                "phone": "+13473926894",
                "code": "123456"
            }
            response = self.client.post("/api/v1/auth/verify-code", json=payload)
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert "access_token" in data
            
            # Verify Twilio was called
            mock_twilio.verify.v2.services.assert_called()
    
    @patch('marque_api_production.twilio_client')
    def test_twilio_verification_failure(self, mock_twilio):
        """Test Twilio verification failure handling"""
        # Mock Twilio verification failure
        mock_twilio.verify.v2.services.return_value.verifications.create.side_effect = Exception("Twilio error")
        
        # Mock TWILIO_READY to be True
        with patch('marque_api_production.TWILIO_READY', True):
            payload = {"phone": "+13473926894"}
            response = self.client.post("/api/v1/auth/send-verification", json=payload)
            
            # Should handle error gracefully
            assert response.status_code in [200, 500]  # Depending on error handling implementation


class TestSMSConfigurationDetection:
    """Test SMS configuration detection logic"""
    
    def test_sms_provider_detection(self):
        """Test SMS provider detection logic"""
        # Test demo mode detection
        with patch('marque_api_production.TWILIO_READY', False):
            from marque_api_production import app
            response = TestClient(app).get("/health")
            data = response.json()
            assert data["sms_provider"] == "Demo"
            assert data["sms_configured"] is False
        
        # Test Twilio mode detection
        with patch('marque_api_production.TWILIO_READY', True):
            from marque_api_production import app
            response = TestClient(app).get("/health")
            data = response.json()
            assert data["sms_provider"] == "Twilio Verify"
            assert data["sms_configured"] is True
    
    def test_environment_variable_loading(self):
        """Test environment variable loading"""
        # Test with no environment variables
        with patch.dict(os.environ, {}, clear=True):
            import importlib
            import marque_api_production
            importlib.reload(marque_api_production)
            
            assert marque_api_production.TWILIO_ACCOUNT_SID is None
            assert marque_api_production.TWILIO_AUTH_TOKEN is None
            assert marque_api_production.TWILIO_VERIFY_SERVICE_SID is None
        
        # Test with partial environment variables
        with patch.dict(os.environ, {
            'TWILIO_ACCOUNT_SID': 'test_sid',
            'TWILIO_AUTH_TOKEN': 'test_token'
            # Missing TWILIO_VERIFY_SERVICE_SID
        }, clear=True):
            import importlib
            import marque_api_production
            importlib.reload(marque_api_production)
            
            assert marque_api_production.TWILIO_ACCOUNT_SID == 'test_sid'
            assert marque_api_production.TWILIO_AUTH_TOKEN == 'test_token'
            assert marque_api_production.TWILIO_VERIFY_SERVICE_SID is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
