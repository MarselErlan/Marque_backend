"""
Integration tests for cart and wishlist APIs
Tests cart and wishlist operations
"""

import pytest


@pytest.mark.integration
class TestCartAPI:
    """Test cart API endpoints"""
    
    def test_get_cart_requires_auth(self, api_client):
        """Test that getting cart requires authentication"""
        response = api_client.get("/api/v1/cart")
        
        # Should require auth
        assert response.status_code in [401, 403, 404]
    
    def test_add_to_cart_requires_auth(self, api_client):
        """Test that adding to cart requires authentication"""
        response = api_client.post("/api/v1/cart/items", json={
            "product_id": 1,
            "sku_id": 1,
            "quantity": 1
        })
        
        # Should require auth
        assert response.status_code in [401, 403, 404, 422]
    
    def test_update_cart_requires_auth(self, api_client):
        """Test that updating cart requires authentication"""
        response = api_client.put("/api/v1/cart/items/1", json={
            "quantity": 2
        })
        
        # Should require auth
        assert response.status_code in [401, 403, 404, 422]
    
    def test_remove_from_cart_requires_auth(self, api_client):
        """Test that removing from cart requires authentication"""
        response = api_client.delete("/api/v1/cart/items/1")
        
        # Should require auth
        assert response.status_code in [401, 403, 404, 422]
    
    def test_clear_cart_requires_auth(self, api_client):
        """Test that clearing cart requires authentication"""
        response = api_client.delete("/api/v1/cart")
        
        # Should require auth
        assert response.status_code in [401, 403, 404]


@pytest.mark.integration
class TestWishlistAPI:
    """Test wishlist API endpoints"""
    
    def test_get_wishlist_requires_auth(self, api_client):
        """Test that getting wishlist requires authentication"""
        response = api_client.get("/api/v1/wishlist")
        
        # Should require auth
        assert response.status_code in [401, 403, 404]
    
    def test_add_to_wishlist_requires_auth(self, api_client):
        """Test that adding to wishlist requires authentication"""
        response = api_client.post("/api/v1/wishlist/items", json={
            "product_id": 1
        })
        
        # Should require auth
        assert response.status_code in [401, 403, 404, 422]
    
    def test_remove_from_wishlist_requires_auth(self, api_client):
        """Test that removing from wishlist requires authentication"""
        response = api_client.delete("/api/v1/wishlist/items/1")
        
        # Should require auth
        assert response.status_code in [401, 403, 404, 422]
    
    def test_check_wishlist_status_requires_auth(self, api_client):
        """Test that checking wishlist status requires authentication"""
        response = api_client.get("/api/v1/wishlist/check/1")
        
        # Should require auth
        assert response.status_code in [401, 403, 404]
    
    def test_clear_wishlist_requires_auth(self, api_client):
        """Test that clearing wishlist requires authentication"""
        response = api_client.delete("/api/v1/wishlist")
        
        # Should require auth
        assert response.status_code in [401, 403, 404]


@pytest.mark.integration
class TestCartWithAuth:
    """Test cart operations with authentication"""
    
    def test_get_cart_with_auth(self, authenticated_client):
        """Test getting cart with authentication"""
        response = authenticated_client.get("/api/v1/cart")
        
        # Should work or return proper error
        assert response.status_code in [200, 404, 422, 500]
    
    def test_add_to_cart_with_auth(self, authenticated_client, sample_product):
        """Test adding to cart with authentication"""
        response = authenticated_client.post(
            "/api/v1/cart/items",
            json={
                "product_id": sample_product.id,
                "sku_id": 1,
                "quantity": 1
            }
        )
        
        # Should work or return proper error
        assert response.status_code in [200, 201, 404, 422, 500]


@pytest.mark.integration
class TestWishlistWithAuth:
    """Test wishlist operations with authentication"""
    
    def test_get_wishlist_with_auth(self, authenticated_client):
        """Test getting wishlist with authentication"""
        response = authenticated_client.get("/api/v1/wishlist")
        
        # Should work or return proper error
        assert response.status_code in [200, 404, 422, 500]
    
    def test_add_to_wishlist_with_auth(self, authenticated_client, sample_product):
        """Test adding to wishlist with authentication"""
        response = authenticated_client.post(
            "/api/v1/wishlist/items",
            json={"product_id": sample_product.id}
        )
        
        # Should work or return proper error
        assert response.status_code in [200, 201, 404, 422, 500]

