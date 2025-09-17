"""
Integration tests for authentication system
End-to-end tests for phone number authentication with multi-market support
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock
import json

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from routers.auth_router import router
from services.auth_service import auth_service
from db.market_db import Market, db_manager
from models.users.market_user import UserKG, UserUS
from models.users.market_phone_verification import PhoneVerificationKG, PhoneVerificationUS

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth_integration.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Mock the database manager for testing
@pytest.fixture
def mock_db_manager():
    """Mock database manager for testing"""
    with patch('src.app_01.services.auth_service.db_manager') as mock:
        # Mock session factories
        mock.get_session_factory.return_value = TestingSessionLocal
        yield mock

@pytest.fixture
def client():
    """Create test client"""
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    
    # Create test database tables
    from db.market_db import get_base
    kg_base = get_base(Market.KG)
    us_base = get_base(Market.US)
    
    kg_base.metadata.create_all(bind=engine)
    us_base.metadata.create_all(bind=engine)
    
    return TestClient(app)

@pytest.fixture
def kg_user_data():
    """KG user test data"""
    return {
        "phone_number": "+996505325311",
        "full_name": "Анна Ахматова",
        "market": "kg",
        "language": "ru",
        "country": "Kyrgyzstan"
    }

@pytest.fixture
def us_user_data():
    """US user test data"""
    return {
        "phone_number": "+15551234567",
        "full_name": "John Smith",
        "market": "us",
        "language": "en",
        "country": "United States"
    }

class TestPhoneAuthenticationFlow:
    """Test complete phone authentication flow"""
    
    def test_kg_market_send_verification_code(self, client, kg_user_data):
        """Test sending verification code for KG market"""
        # Given
        request_data = {
            "phone_number": kg_user_data["phone_number"]
        }
        
        # When
        with patch.object(auth_service, 'send_verification_code') as mock_send:
            mock_send.return_value = {
                "success": True,
                "message": "Verification code sent successfully",
                "phone_number": "+996 505 325 311",
                "market": "kg",
                "language": "ru",
                "expires_in_minutes": 10
            }
            
            response = client.post("/auth/send-code", json=request_data)
        
        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["market"] == "kg"
        assert data["language"] == "ru"
        assert data["phone_number"] == "+996 505 325 311"
        assert data["expires_in_minutes"] == 10
    
    def test_us_market_send_verification_code(self, client, us_user_data):
        """Test sending verification code for US market"""
        # Given
        request_data = {
            "phone_number": us_user_data["phone_number"]
        }
        
        # When
        with patch.object(auth_service, 'send_verification_code') as mock_send:
            mock_send.return_value = {
                "success": True,
                "message": "Verification code sent successfully",
                "phone_number": "+1 (555) 123-4567",
                "market": "us",
                "language": "en",
                "expires_in_minutes": 15
            }
            
            response = client.post("/auth/send-code", json=request_data)
        
        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["market"] == "us"
        assert data["language"] == "en"
        assert data["phone_number"] == "+1 (555) 123-4567"
        assert data["expires_in_minutes"] == 15
    
    def test_send_code_with_market_override(self, client, kg_user_data):
        """Test sending verification code with market override header"""
        # Given
        request_data = {
            "phone_number": kg_user_data["phone_number"]
        }
        headers = {"X-Market": "us"}
        
        # When
        with patch.object(auth_service, 'send_verification_code') as mock_send:
            mock_send.return_value = {
                "success": True,
                "message": "Verification code sent successfully",
                "phone_number": "+996 505 325 311",
                "market": "us",
                "language": "en",
                "expires_in_minutes": 15
            }
            
            response = client.post("/auth/send-code", json=request_data, headers=headers)
        
        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["market"] == "us"
        assert data["language"] == "en"
    
    def test_send_code_invalid_phone_format(self, client):
        """Test sending verification code with invalid phone format"""
        # Given
        request_data = {
            "phone_number": "+44123456789"  # UK number, not supported
        }
        
        # When
        response = client.post("/auth/send-code", json=request_data)
        
        # Then
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data
    
    def test_verify_code_success_new_user(self, client, kg_user_data):
        """Test successful code verification for new user"""
        # Given
        request_data = {
            "phone_number": kg_user_data["phone_number"],
            "verification_code": "123456"
        }
        
        # When
        with patch.object(auth_service, 'verify_phone_code') as mock_verify:
            mock_verify.return_value = {
                "success": True,
                "message": "Phone number verified successfully",
                "access_token": "mock_jwt_token",
                "token_type": "bearer",
                "expires_in": 1800,
                "user_id": 1,
                "market": "kg",
                "is_new_user": True
            }
            
            response = client.post("/auth/verify-code", json=request_data)
        
        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["access_token"] == "mock_jwt_token"
        assert data["user_id"] == 1
        assert data["market"] == "kg"
        assert data["is_new_user"] == True
    
    def test_verify_code_success_existing_user(self, client, us_user_data):
        """Test successful code verification for existing user"""
        # Given
        request_data = {
            "phone_number": us_user_data["phone_number"],
            "verification_code": "789012"
        }
        
        # When
        with patch.object(auth_service, 'verify_phone_code') as mock_verify:
            mock_verify.return_value = {
                "success": True,
                "message": "Phone number verified successfully",
                "access_token": "mock_jwt_token",
                "token_type": "bearer",
                "expires_in": 1800,
                "user_id": 2,
                "market": "us",
                "is_new_user": False
            }
            
            response = client.post("/auth/verify-code", json=request_data)
        
        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["access_token"] == "mock_jwt_token"
        assert data["user_id"] == 2
        assert data["market"] == "us"
        assert data["is_new_user"] == False
    
    def test_verify_code_invalid_code(self, client, kg_user_data):
        """Test verification with invalid code"""
        # Given
        request_data = {
            "phone_number": kg_user_data["phone_number"],
            "verification_code": "999999"
        }
        
        # When
        with patch.object(auth_service, 'verify_phone_code') as mock_verify:
            mock_verify.side_effect = ValueError("Invalid or expired verification code")
            
            response = client.post("/auth/verify-code", json=request_data)
        
        # Then
        assert response.status_code == 400
        data = response.json()
        assert "Invalid or expired verification code" in data["detail"]

class TestUserProfile:
    """Test user profile endpoints"""
    
    def test_get_user_profile_success(self, client, kg_user_data):
        """Test getting user profile successfully"""
        # Given
        mock_token_response = MagicMock()
        mock_token_response.user_id = 1
        mock_token_response.market = "kg"
        
        # When
        with patch('routers.auth_router.get_current_user_from_token') as mock_auth:
            mock_auth.return_value = mock_token_response
            
            with patch.object(auth_service, 'get_user_profile') as mock_get_profile:
                mock_get_profile.return_value = {
                    "id": 1,
                    "phone_number": kg_user_data["phone_number"],
                    "formatted_phone": "+996 505 325 311",
                    "full_name": kg_user_data["full_name"],
                    "profile_image_url": None,
                    "is_verified": True,
                    "market": "kg",
                    "language": "ru",
                    "country": "Kyrgyzstan",
                    "currency": "сом",
                    "currency_code": "KGS",
                    "last_login": "2024-01-15T10:00:00Z",
                    "created_at": "2024-01-15T09:00:00Z"
                }
                
                response = client.get(
                    "/auth/profile",
                    headers={"Authorization": "Bearer mock_token"}
                )
        
        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["phone_number"] == kg_user_data["phone_number"]
        assert data["formatted_phone"] == "+996 505 325 311"
        assert data["full_name"] == kg_user_data["full_name"]
        assert data["market"] == "kg"
        assert data["currency"] == "сом"
    
    def test_update_user_profile_success(self, client, kg_user_data):
        """Test updating user profile successfully"""
        # Given
        mock_token_response = MagicMock()
        mock_token_response.user_id = 1
        mock_token_response.market = "kg"
        
        request_data = {
            "full_name": "Анна Петровна Ахматова",
            "profile_image_url": "https://example.com/profile.jpg"
        }
        
        # When
        with patch('routers.auth_router.get_current_user_from_token') as mock_auth:
            mock_auth.return_value = mock_token_response
            
            with patch.object(auth_service, 'update_user_profile') as mock_update:
                mock_update.return_value = {
                    "id": 1,
                    "phone_number": kg_user_data["phone_number"],
                    "formatted_phone": "+996 505 325 311",
                    "full_name": "Анна Петровна Ахматова",
                    "profile_image_url": "https://example.com/profile.jpg",
                    "is_verified": True,
                    "market": "kg",
                    "language": "ru",
                    "country": "Kyrgyzstan",
                    "currency": "сом",
                    "currency_code": "KGS",
                    "last_login": "2024-01-15T10:00:00Z",
                    "created_at": "2024-01-15T09:00:00Z"
                }
                
                response = client.put(
                    "/auth/profile",
                    json=request_data,
                    headers={"Authorization": "Bearer mock_token"}
                )
        
        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["user"]["full_name"] == "Анна Петровна Ахматова"
        assert data["user"]["profile_image_url"] == "https://example.com/profile.jpg"
    
    def test_get_profile_unauthorized(self, client):
        """Test getting profile without authorization"""
        # When
        response = client.get("/auth/profile")
        
        # Then
        assert response.status_code == 403  # No authorization header
    
    def test_update_profile_unauthorized(self, client):
        """Test updating profile without authorization"""
        # Given
        request_data = {
            "full_name": "Test User"
        }
        
        # When
        response = client.put("/auth/profile", json=request_data)
        
        # Then
        assert response.status_code == 403  # No authorization header

class TestTokenVerification:
    """Test token verification endpoints"""
    
    def test_verify_token_success(self, client, kg_user_data):
        """Test successful token verification"""
        # Given
        mock_token_response = MagicMock()
        mock_token_response.user_id = 1
        mock_token_response.market = "kg"
        mock_token_response.phone_number = kg_user_data["phone_number"]
        mock_token_response.formatted_phone = "+996 505 325 311"
        mock_token_response.currency = "сом"
        
        # When
        with patch('routers.auth_router.get_current_user_from_token') as mock_auth:
            mock_auth.return_value = mock_token_response
            
            response = client.get(
                "/auth/verify-token",
                headers={"Authorization": "Bearer mock_token"}
            )
        
        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] == True
        assert data["user_id"] == 1
        assert data["market"] == "kg"
        assert data["phone_number"] == kg_user_data["phone_number"]
    
    def test_logout_success(self, client):
        """Test successful logout"""
        # When
        response = client.post("/auth/logout")
        
        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "Logged out successfully" in data["message"]

class TestMarketSupport:
    """Test market support endpoints"""
    
    def test_get_supported_markets(self, client):
        """Test getting supported markets"""
        # When
        with patch.object(auth_service, 'get_supported_markets') as mock_markets:
            mock_markets.return_value = [
                {
                    "market": "kg",
                    "country": "Kyrgyzstan",
                    "currency": "сом",
                    "currency_code": "KGS",
                    "language": "ru",
                    "phone_prefix": "+996",
                    "phone_format": "+996 XXX XXX XXX"
                },
                {
                    "market": "us",
                    "country": "United States",
                    "currency": "$",
                    "currency_code": "USD",
                    "language": "en",
                    "phone_prefix": "+1",
                    "phone_format": "+1 (XXX) XXX-XXXX"
                }
            ]
            
            response = client.get("/auth/markets")
        
        # Then
        assert response.status_code == 200
        data = response.json()
        assert len(data["supported_markets"]) == 2
        assert data["default_market"] == "kg"
        
        kg_market = data["supported_markets"][0]
        assert kg_market["market"] == "kg"
        assert kg_market["currency"] == "сом"
        assert kg_market["language"] == "ru"
        
        us_market = data["supported_markets"][1]
        assert us_market["market"] == "us"
        assert us_market["currency"] == "$"
        assert us_market["language"] == "en"
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        # When
        response = client.get("/auth/health")
        
        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "authentication"
        assert "kg" in data["markets"]
        assert "us" in data["markets"]

class TestErrorHandling:
    """Test error handling scenarios"""
    
    def test_invalid_json_request(self, client):
        """Test request with invalid JSON"""
        # When
        response = client.post(
            "/auth/send-code",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        # Then
        assert response.status_code == 422
    
    def test_missing_required_fields(self, client):
        """Test request with missing required fields"""
        # Given
        request_data = {}  # Missing phone_number
        
        # When
        response = client.post("/auth/send-code", json=request_data)
        
        # Then
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_invalid_verification_code_format(self, client, kg_user_data):
        """Test verification with invalid code format"""
        # Given
        request_data = {
            "phone_number": kg_user_data["phone_number"],
            "verification_code": "abc123"  # Non-numeric
        }
        
        # When
        response = client.post("/auth/verify-code", json=request_data)
        
        # Then
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

if __name__ == "__main__":
    pytest.main([__file__])
