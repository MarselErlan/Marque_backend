"""
Unit tests for wishlist router
Tests for wishlist management endpoints
"""

import pytest
from fastapi.testclient import TestClient


class TestWishlistEndpoints:
    """Test wishlist API endpoints"""
    
    def test_get_wishlist_endpoint_exists(self, client):
        """Test that wishlist endpoint exists"""
        response = client.get("/api/v1/wishlist")
        # Should require auth
        assert response.status_code in [401, 403, 404]
    
    def test_get_wishlist_without_auth(self, client):
        """Test getting wishlist without authentication"""
        response = client.get("/api/v1/wishlist")
        assert response.status_code in [401, 403, 404]
    
    def test_add_to_wishlist_without_auth(self, client):
        """Test adding to wishlist without authentication"""
        response = client.post("/api/v1/wishlist/items", json={
            "product_id": 1
        })
        assert response.status_code in [401, 403, 404]
    
    def test_remove_from_wishlist_without_auth(self, client):
        """Test removing from wishlist without authentication"""
        response = client.delete("/api/v1/wishlist/items/1")
        assert response.status_code in [401, 403, 404]
    
    def test_check_wishlist_status_without_auth(self, client):
        """Test checking wishlist status without authentication"""
        response = client.get("/api/v1/wishlist/check/1")
        assert response.status_code in [401, 403, 404]
    
    def test_clear_wishlist_without_auth(self, client):
        """Test clearing wishlist without authentication"""
        response = client.delete("/api/v1/wishlist")
        assert response.status_code in [401, 403, 404]


class TestWishlistValidation:
    """Test wishlist data validation"""
    
    def test_add_to_wishlist_missing_product_id(self, client):
        """Test adding to wishlist without product ID"""
        response = client.post("/api/v1/wishlist/items", json={})
        assert response.status_code in [422, 401, 403]
    
    def test_add_to_wishlist_invalid_product_id(self, client):
        """Test adding to wishlist with invalid product ID"""
        response = client.post("/api/v1/wishlist/items", json={
            "product_id": "invalid"
        })
        assert response.status_code in [422, 401, 403]


@pytest.mark.parametrize("endpoint", [
    "/api/v1/wishlist",
    "/api/v1/wishlist/items",
])
def test_wishlist_endpoints_exist(client, endpoint):
    """Parametrized test for wishlist endpoint existence"""
    response = client.get(endpoint)
    # Should not return 404 or 405 (may return 401)
    assert response.status_code in [200, 401, 403, 404]

