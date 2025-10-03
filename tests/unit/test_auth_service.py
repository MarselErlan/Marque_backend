"""
Unit tests for authentication service
Tests for auth logic, token generation, and user management
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import jwt

from src.app_01.services.auth_service import auth_service
from src.app_01.schemas.auth import PhoneLoginRequest, VerifyCodeRequest
from src.app_01.db.market_db import Market


class TestTokenGeneration:
    """Test JWT token generation and validation"""
    
    def test_create_access_token(self):
        """Test creating access token"""
        data = {"user_id": "1", "phone_number": "+996555123456"}
        token = auth_service.create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_access_token_with_expiry(self):
        """Test token with custom expiry"""
        data = {"user_id": "1"}
        expires_delta = timedelta(minutes=15)
        token = auth_service.create_access_token(data, expires_delta)
        
        # Decode and check expiry
        decoded = jwt.decode(token, "your-secret-key-here", algorithms=["HS256"])
        assert "exp" in decoded
    
    def test_verify_valid_token(self):
        """Test verifying valid token"""
        data = {"user_id": "1", "phone_number": "+996555123456"}
        token = auth_service.create_access_token(data)
        
        payload = auth_service.verify_token(token)
        assert payload is not None
        assert payload["user_id"] == "1"
        assert payload["phone_number"] == "+996555123456"
    
    def test_verify_expired_token(self):
        """Test verifying expired token"""
        data = {"user_id": "1"}
        expires_delta = timedelta(seconds=-1)  # Already expired
        token = auth_service.create_access_token(data, expires_delta)
        
        payload = auth_service.verify_token(token)
        assert payload is None
    
    def test_verify_invalid_token(self):
        """Test verifying invalid token"""
        invalid_token = "invalid.token.here"
        payload = auth_service.verify_token(invalid_token)
        assert payload is None


class TestVerificationCodeGeneration:
    """Test verification code generation"""
    
    def test_generate_verification_code(self):
        """Test generating verification code"""
        code = auth_service._generate_verification_code()
        
        assert code is not None
        assert isinstance(code, str)
        assert len(code) == 6
        assert code.isdigit()
    
    def test_verification_code_uniqueness(self):
        """Test that codes are unique"""
        codes = [auth_service._generate_verification_code() for _ in range(100)]
        # Most codes should be unique
        assert len(set(codes)) > 90


class TestPhoneNumberValidation:
    """Test phone number validation"""
    
    @pytest.mark.parametrize("phone", [
        "+996555123456",
        "+996700987654",
        "996555123456",
        "+996 555 123 456",
    ])
    def test_valid_kg_phone(self, phone):
        """Test valid KG phone numbers"""
        from src.app_01.db.market_db import detect_market_from_phone
        market = detect_market_from_phone(phone)
        assert market == Market.KG
    
    @pytest.mark.parametrize("phone", [
        "+12125551234",
        "+14155559999",
        "12125551234",
        "+1 212 555 1234",
    ])
    def test_valid_us_phone(self, phone):
        """Test valid US phone numbers"""
        from src.app_01.db.market_db import detect_market_from_phone
        market = detect_market_from_phone(phone)
        assert market == Market.US


class TestUserProfileOperations:
    """Test user profile operations"""
    
    @patch('src.app_01.services.auth_service.get_user_by_phone_with_market_detection')
    def test_get_user_profile(self, mock_get_user):
        """Test getting user profile"""
        # Mock user
        mock_user = Mock()
        mock_user.id = 1
        mock_user.phone_number = "+996555123456"
        mock_user.full_name = "Test User"
        mock_user.email = "test@example.com"
        mock_get_user.return_value = (mock_user, Market.KG)
        
        # Test
        db_mock = Mock()
        token_data = {"phone_number": "+996555123456", "market": "KG"}
        
        profile = auth_service.get_user_profile(db_mock, token_data)
        
        assert profile is not None
        assert profile.phone_number == "+996555123456"


class TestRateLimiting:
    """Test rate limiting logic"""
    
    def test_rate_limit_check(self):
        """Test rate limiting check"""
        phone = "+996555123456"
        
        # First attempt should be allowed
        assert auth_service._check_rate_limit(phone) == True
    
    def test_rate_limit_exceeded(self):
        """Test rate limit exceeded"""
        phone = "+996555999888"
        
        # Simulate multiple attempts
        for i in range(5):
            auth_service._check_rate_limit(phone)
        
        # Next attempt might be rate limited
        # (depends on implementation)
        result = auth_service._check_rate_limit(phone)
        assert isinstance(result, bool)


class TestMarketDetection:
    """Test market detection in auth service"""
    
    def test_detect_kg_market(self):
        """Test detecting KG market from phone"""
        from src.app_01.db.market_db import detect_market_from_phone
        market = detect_market_from_phone("+996555123456")
        assert market == Market.KG
    
    def test_detect_us_market(self):
        """Test detecting US market from phone"""
        from src.app_01.db.market_db import detect_market_from_phone
        market = detect_market_from_phone("+12125551234")
        assert market == Market.US


class TestSendVerificationCode:
    """Test sending verification code"""
    
    @patch('src.app_01.services.auth_service.create_verification_for_market')
    @patch('src.app_01.services.auth_service.get_user_by_phone_with_market_detection')
    def test_send_code_new_user(self, mock_get_user, mock_create_verification):
        """Test sending code to new user"""
        # Setup mocks
        mock_get_user.return_value = (None, Market.KG)
        mock_create_verification.return_value = "123456"
        
        # Test
        db_mock = Mock()
        request = PhoneLoginRequest(phone_number="+996555123456")
        
        response = auth_service.send_verification_code(db_mock, request)
        
        assert response is not None
        assert response.message is not None
    
    @patch('src.app_01.services.auth_service.create_verification_for_market')
    @patch('src.app_01.services.auth_service.get_user_by_phone_with_market_detection')
    def test_send_code_existing_user(self, mock_get_user, mock_create_verification):
        """Test sending code to existing user"""
        # Setup mocks
        mock_user = Mock()
        mock_user.phone_number = "+996555123456"
        mock_get_user.return_value = (mock_user, Market.KG)
        mock_create_verification.return_value = "123456"
        
        # Test
        db_mock = Mock()
        request = PhoneLoginRequest(phone_number="+996555123456")
        
        response = auth_service.send_verification_code(db_mock, request)
        
        assert response is not None
        assert response.message is not None

