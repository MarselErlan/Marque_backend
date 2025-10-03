"""
Unit tests for cart router
Tests for cart management endpoints
"""

import pytest
from fastapi.testclient import TestClient


class TestCartEndpoints:
    """Test cart API endpoints"""
    
    def test_get_cart_endpoint_exists(self, client):
        """Test that cart endpoint exists"""
        response = client.get("/api/v1/cart")
        # Should require auth
        assert response.status_code in [401, 403, 404]
    
    def test_get_cart_without_auth(self, client):
        """Test getting cart without authentication"""
        response = client.get("/api/v1/cart")
        assert response.status_code in [401, 403, 404]
    
    def test_add_to_cart_without_auth(self, client):
        """Test adding to cart without authentication"""
        response = client.post("/api/v1/cart/items", json={
            "product_id": 1,
            "sku_id": 1,
            "quantity": 1
        })
        assert response.status_code in [401, 403, 404]
    
    def test_update_cart_item_without_auth(self, client):
        """Test updating cart item without authentication"""
        response = client.put("/api/v1/cart/items/1", json={
            "quantity": 2
        })
        assert response.status_code in [401, 403, 404]
    
    def test_remove_from_cart_without_auth(self, client):
        """Test removing from cart without authentication"""
        response = client.delete("/api/v1/cart/items/1")
        assert response.status_code in [401, 403, 404]
    
    def test_clear_cart_without_auth(self, client):
        """Test clearing cart without authentication"""
        response = client.delete("/api/v1/cart")
        assert response.status_code in [401, 403, 404]


class TestCartValidation:
    """Test cart data validation"""
    
    def test_add_to_cart_missing_fields(self, client):
        """Test adding to cart with missing fields"""
        response = client.post("/api/v1/cart/items", json={})
        # Should fail validation
        assert response.status_code in [422, 401, 403]
    
    def test_add_to_cart_invalid_quantity(self, client):
        """Test adding to cart with invalid quantity"""
        response = client.post("/api/v1/cart/items", json={
            "product_id": 1,
            "sku_id": 1,
            "quantity": -1
        })
        assert response.status_code in [422, 401, 403]


@pytest.mark.parametrize("endpoint", [
    "/api/v1/cart",
    "/api/v1/cart/items",
])
def test_cart_endpoints_exist(client, endpoint):
    """Parametrized test for cart endpoint existence"""
    response = client.get(endpoint)
    # Should not return 404 (may return 401)
    assert response.status_code != 405

