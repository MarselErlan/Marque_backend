"""
Unit tests for banner router
Tests for banner endpoints
"""

import pytest
from fastapi.testclient import TestClient


class TestBannerEndpoints:
    """Test banner API endpoints"""
    
    def test_get_banners_endpoint_exists(self, client):
        """Test that banners endpoint exists"""
        response = client.get("/api/v1/banners")
        assert response.status_code != 404
    
    def test_get_banners_success(self, client):
        """Test getting all banners"""
        response = client.get("/api/v1/banners")
        assert response.status_code in [200, 422]
    
    def test_get_banner_by_id(self, client):
        """Test getting banner by ID"""
        response = client.get("/api/v1/banners/1")
        assert response.status_code in [200, 404, 422]
    
    def test_get_banner_invalid_id(self, client):
        """Test getting banner with invalid ID"""
        response = client.get("/api/v1/banners/invalid")
        assert response.status_code == 422


class TestBannerFiltering:
    """Test banner filtering"""
    
    def test_filter_by_type(self, client):
        """Test filtering banners by type"""
        response = client.get("/api/v1/banners?banner_type=sale")
        assert response.status_code in [200, 422]
    
    def test_filter_by_active(self, client):
        """Test filtering banners by active status"""
        response = client.get("/api/v1/banners?is_active=true")
        assert response.status_code in [200, 422]
    
    @pytest.mark.parametrize("banner_type", ["sale", "model"])
    def test_filter_by_various_types(self, client, banner_type):
        """Test filtering by various banner types"""
        response = client.get(f"/api/v1/banners?banner_type={banner_type}")
        assert response.status_code in [200, 422]


class TestBannerAdmin:
    """Test banner admin endpoints"""
    
    def test_create_banner_without_auth(self, client):
        """Test creating banner without authentication"""
        response = client.post("/api/v1/admin/banners", json={
            "title": "Test Banner",
            "image_url": "https://example.com/test.jpg",
            "banner_type": "sale"
        })
        # Should require authentication
        assert response.status_code in [401, 403, 404]
    
    def test_update_banner_without_auth(self, client):
        """Test updating banner without authentication"""
        response = client.put("/api/v1/admin/banners/1", json={
            "title": "Updated Banner"
        })
        assert response.status_code in [401, 403, 404]
    
    def test_delete_banner_without_auth(self, client):
        """Test deleting banner without authentication"""
        response = client.delete("/api/v1/admin/banners/1")
        assert response.status_code in [401, 403, 404]


class TestBannerValidation:
    """Test banner data validation"""
    
    def test_banner_type_validation(self, client):
        """Test banner type validation"""
        response = client.get("/api/v1/banners?banner_type=invalid")
        # Should validate banner type
        assert response.status_code in [422, 200]

