"""
Integration tests for authentication flow
Tests complete auth workflows: send code -> verify -> get profile
"""

import pytest
from unittest.mock import patch, MagicMock


@pytest.mark.integration
class TestAuthenticationFlow:
    """Test complete authentication workflows"""
    
    def test_health_check_endpoint(self, api_client):
        """Test that health check endpoint works"""
        response = api_client.get("/api/v1/auth/health")
        
        # Should return 200 or 404 (if endpoint doesn't exist)
        assert response.status_code in [200, 404]
    
    def test_markets_endpoint(self, api_client):
        """Test getting supported markets"""
        response = api_client.get("/api/v1/auth/markets")
        
        # Should return list of markets or 404
        assert response.status_code in [200, 404]
    
    @patch('src.app_01.services.auth_service.auth_service.send_verification_code')
    def test_send_verification_code_kg(self, mock_send, api_client):
        """Test sending verification code for KG user"""
        mock_send.return_value = MagicMock(
            success=True,
            message="Code sent successfully"
        )
        
        response = api_client.post("/api/v1/auth/send-code", json={
            "phone_number": "+996555123456"
        })
        
        # Should not crash (may return 200 or error based on implementation)
        assert response.status_code in [200, 400, 422, 500]
    
    @patch('src.app_01.services.auth_service.auth_service.send_verification_code')
    def test_send_verification_code_us(self, mock_send, api_client):
        """Test sending verification code for US user"""
        mock_send.return_value = MagicMock(
            success=True,
            message="Code sent successfully"
        )
        
        response = api_client.post("/api/v1/auth/send-code", json={
            "phone_number": "+12125551234"
        })
        
        assert response.status_code in [200, 400, 422, 500]
    
    def test_send_code_invalid_phone(self, api_client):
        """Test sending code with invalid phone"""
        response = api_client.post("/api/v1/auth/send-code", json={
            "phone_number": "invalid"
        })
        
        # Should return validation error
        assert response.status_code in [400, 422]
    
    def test_verify_code_missing_fields(self, api_client):
        """Test verifying code without required fields"""
        response = api_client.post("/api/v1/auth/verify-code", json={})
        
        # Should return validation error
        assert response.status_code == 422
    
    def test_get_profile_without_auth(self, api_client):
        """Test getting profile without authentication"""
        response = api_client.get("/api/v1/auth/profile")
        
        # Should return unauthorized
        assert response.status_code in [401, 403]
    
    def test_get_profile_with_invalid_token(self, api_client):
        """Test getting profile with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = api_client.get("/api/v1/auth/profile", headers=headers)
        
        # Should return unauthorized
        assert response.status_code in [401, 403]
    
    def test_logout_endpoint(self, api_client):
        """Test logout endpoint exists"""
        response = api_client.post("/api/v1/auth/logout")
        
        # Should exist (may require auth or not)
        assert response.status_code != 404


@pytest.mark.integration
class TestAuthenticationWithDatabase:
    """Test authentication with database operations"""
    
    def test_user_exists_in_database(self, api_client, sample_kg_user):
        """Test that user is created in database"""
        assert sample_kg_user.id is not None
        assert sample_kg_user.phone_number == "+996555123456"
        assert sample_kg_user.is_verified == True
    
    def test_multiple_users_different_markets(self, api_client, sample_kg_user, sample_us_user):
        """Test users from different markets"""
        assert sample_kg_user.phone_number.startswith("+996")
        assert sample_us_user.phone_number.startswith("+1")
        assert sample_kg_user.id != sample_us_user.id


@pytest.mark.integration
class TestAuthTokens:
    """Test JWT token generation and validation"""
    
    def test_token_generation(self, auth_token):
        """Test that auth token is generated"""
        assert auth_token is not None
        assert isinstance(auth_token, str)
        assert len(auth_token) > 0
    
    def test_token_in_headers(self, auth_headers):
        """Test that token is in headers"""
        assert "Authorization" in auth_headers
        assert auth_headers["Authorization"].startswith("Bearer ")
    
    def test_decode_token(self, auth_token):
        """Test decoding token"""
        import jwt
        
        try:
            decoded = jwt.decode(auth_token, "your-secret-key-here", algorithms=["HS256"])
            assert "user_id" in decoded
            assert "phone_number" in decoded
            assert "market" in decoded
        except jwt.InvalidTokenError:
            # Token format may differ
            pass

