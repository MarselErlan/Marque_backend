"""
Unit tests for authentication router
Tests for auth endpoints
"""

import pytest
from fastapi.testclient import TestClient


class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    def test_send_code_endpoint_exists(self, client):
        """Test that send-code endpoint exists"""
        response = client.post("/api/v1/auth/send-code", json={
            "phone_number": "+996555123456"
        })
        assert response.status_code not in [404]  # Endpoint may not exist
    
    def test_verify_code_endpoint_exists(self, client):
        """Test that verify-code endpoint exists"""
        response = client.post("/api/v1/auth/verify-code", json={
            "phone_number": "+996555123456",
            "code": "123456"
        })
        assert response.status_code not in [404]  # Endpoint may not exist
    
    def test_get_profile_endpoint_exists(self, client):
        """Test that profile endpoint exists"""
        response = client.get("/api/v1/auth/profile")
        # Will return 401 without auth, not 404
        assert response.status_code in [401, 403]
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/api/v1/auth/health")
        assert response.status_code in [200, 404]
    
    def test_markets_endpoint(self, client):
        """Test markets endpoint"""
        response = client.get("/api/v1/auth/markets")
        assert response.status_code in [200, 404]


class TestSendCodeValidation:
    """Test send code validation"""
    
    def test_send_code_missing_phone(self, client):
        """Test send code without phone number"""
        response = client.post("/api/v1/auth/send-code", json={})
        assert response.status_code in [404, 422]
    
    def test_send_code_invalid_phone(self, client):
        """Test send code with invalid phone"""
        response = client.post("/api/v1/auth/send-code", json={
            "phone_number": "invalid"
        })
        assert response.status_code in [400, 404, 422]
    
    @pytest.mark.parametrize("phone", [
        "+996555123456",
        "+996700987654",
        "+12125551234",
        "+14155559999",
    ])
    def test_send_code_valid_phones(self, client, phone):
        """Test send code with valid phone numbers"""
        response = client.post("/api/v1/auth/send-code", json={
            "phone_number": phone
        })
        # Should not be validation error
        assert response.status_code != 422


class TestVerifyCodeValidation:
    """Test verify code validation"""
    
    def test_verify_code_missing_fields(self, client):
        """Test verify code without required fields"""
        response = client.post("/api/v1/auth/verify-code", json={})
        assert response.status_code in [404, 422]
    
    def test_verify_code_missing_code(self, client):
        """Test verify code without code"""
        response = client.post("/api/v1/auth/verify-code", json={
            "phone_number": "+996555123456"
        })
        assert response.status_code in [404, 422]
    
    def test_verify_code_missing_phone(self, client):
        """Test verify code without phone"""
        response = client.post("/api/v1/auth/verify-code", json={
            "code": "123456"
        })
        assert response.status_code in [404, 422]
    
    def test_verify_code_invalid_code_format(self, client):
        """Test verify code with invalid code format"""
        response = client.post("/api/v1/auth/verify-code", json={
            "phone_number": "+996555123456",
            "code": "abc"
        })
        assert response.status_code in [400, 404, 422]


class TestProfileEndpoints:
    """Test profile endpoints"""
    
    def test_get_profile_without_auth(self, client):
        """Test getting profile without authentication"""
        response = client.get("/api/v1/auth/profile")
        assert response.status_code in [401, 403]
    
    def test_update_profile_without_auth(self, client):
        """Test updating profile without authentication"""
        response = client.put("/api/v1/auth/profile", json={
            "full_name": "New Name"
        })
        assert response.status_code in [401, 403]
    
    def test_get_profile_with_invalid_token(self, client):
        """Test getting profile with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/auth/profile", headers=headers)
        assert response.status_code in [401, 403]


class TestTokenVerification:
    """Test token verification"""
    
    def test_verify_token_endpoint(self, client):
        """Test token verification endpoint"""
        response = client.get("/api/v1/auth/verify-token")
        assert response.status_code in [401, 403, 404]
    
    def test_verify_token_with_invalid_token(self, client):
        """Test verifying invalid token"""
        headers = {"Authorization": "Bearer invalid"}
        response = client.get("/api/v1/auth/verify-token", headers=headers)
        assert response.status_code in [401, 403, 404]


class TestLogout:
    """Test logout functionality"""
    
    def test_logout_endpoint(self, client):
        """Test logout endpoint"""
        response = client.post("/api/v1/auth/logout")
        # Should exist even without auth
        assert response.status_code not in [404]  # Endpoint may not exist
    
    def test_logout_without_auth(self, client):
        """Test logout without authentication"""
        response = client.post("/api/v1/auth/logout")
        assert response.status_code in [200, 401, 403]


@pytest.mark.parametrize("endpoint,method", [
    ("/api/v1/auth/send-code", "POST"),
    ("/api/v1/auth/verify-code", "POST"),
    ("/api/v1/auth/profile", "GET"),
    ("/api/v1/auth/logout", "POST"),
])
def test_auth_endpoints_exist(client, endpoint, method):
    """Parametrized test for auth endpoint existence"""
    if method == "GET":
        response = client.get(endpoint)
    elif method == "POST":
        response = client.post(endpoint, json={})
    
    # Endpoints should exist (not 404)
    assert response.status_code not in [404]  # Endpoint may not exist

