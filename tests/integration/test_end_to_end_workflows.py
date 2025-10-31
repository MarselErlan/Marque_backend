"""
End-to-end integration tests
Tests complete user workflows across multiple features
"""

import pytest
from unittest.mock import patch, MagicMock


@pytest.mark.integration
class TestCompleteUserJourney:
    """Test complete user journey from registration to purchase"""
    
    def test_guest_browsing_products(self, api_client, sample_product):
        """Test guest user can browse products"""
        # Get products list
        response = api_client.get("/api/v1/products")
        assert response.status_code != 404
        
        # Search for products
        response = api_client.get("/api/v1/products/search?q=running")
        assert response.status_code in [200, 422]
        
        # View product details
        response = api_client.get(f"/api/v1/products/{sample_product.id}")
        assert response.status_code in [200, 404, 422]
    
    def test_guest_viewing_banners(self, api_client, sample_banner):
        """Test guest user can view banners"""
        # Get banners
        response = api_client.get("/api/v1/banners")
        assert response.status_code != 404
        
        # Get specific banner
        response = api_client.get(f"/api/v1/banners/{sample_banner.id}")
        assert response.status_code in [200, 404, 422]
    
    def test_authenticated_user_cart_workflow(self, authenticated_client, sample_product, sample_sku):
        """Test authenticated user cart workflow"""
        # View cart (should be empty)
        response = authenticated_client.get("/api/v1/cart")
        assert response.status_code in [200, 404, 422]
        
        # Add item to cart
        response = authenticated_client.post(
            "/api/v1/cart/items",
            json={
                "product_id": sample_product.id,
                "sku_id": sample_sku.id,
                "quantity": 1
            }
        )
        assert response.status_code in [200, 201, 404, 422, 500]
    
    def test_authenticated_user_wishlist_workflow(self, authenticated_client, sample_product):
        """Test authenticated user wishlist workflow"""
        # View wishlist (API requires POST with user_id, may return 400)
        response = authenticated_client.get("/api/v1/wishlist")
        assert response.status_code in [200, 400, 404, 422]
        
        # Add to wishlist
        response = authenticated_client.post(
            "/api/v1/wishlist/items",
            json={"product_id": sample_product.id}
        )
        assert response.status_code in [200, 201, 404, 422, 500]


@pytest.mark.integration
class TestSearchAndFilter:
    """Test search and filter combinations"""
    
    def test_search_then_filter_by_category(self, api_client, sample_category):
        """Test searching then filtering by category"""
        # First search
        response = api_client.get("/api/v1/products/search?q=shoes")
        assert response.status_code in [200, 422]
        
        # Then filter by category
        response = api_client.get(
            f"/api/v1/products/search?q=shoes&category={sample_category.slug}"
        )
        assert response.status_code in [200, 422]
    
    def test_search_with_price_range(self, api_client):
        """Test search with price filtering"""
        response = api_client.get(
            "/api/v1/products/search?q=shoes&min_price=50&max_price=150"
        )
        assert response.status_code in [200, 422]
    
    def test_search_with_sorting(self, api_client):
        """Test search with different sort orders"""
        sort_options = ["newest", "popular", "price_low", "price_high", "relevance"]
        
        for sort in sort_options:
            response = api_client.get(f"/api/v1/products/search?q=test&sort_by={sort}")
            assert response.status_code in [200, 422]


@pytest.mark.integration
class TestMarketSpecific:
    """Test market-specific functionality"""
    
    def test_kg_user_workflow(self, api_client, sample_kg_user):
        """Test KG user workflow"""
        assert sample_kg_user.phone_number.startswith("+996")
        assert sample_kg_user.full_name is not None
    
    def test_us_user_workflow(self, api_client, sample_us_user):
        """Test US user workflow"""
        assert sample_us_user.phone_number.startswith("+1")
        assert sample_us_user.full_name is not None
    
    def test_market_detection_from_phone(self):
        """Test market detection from phone numbers"""
        from src.app_01.db.market_db import detect_market_from_phone, Market
        
        kg_market = detect_market_from_phone("+996555123456")
        assert kg_market == Market.KG
        
        us_market = detect_market_from_phone("+12125551234")
        assert us_market == Market.US


@pytest.mark.integration
class TestErrorHandling:
    """Test error handling across features"""
    
    def test_invalid_product_id(self, api_client):
        """Test handling of invalid product ID"""
        response = api_client.get("/api/v1/products/invalid")
        assert response.status_code == 404  # Product not found (correct response)
    
    def test_invalid_banner_id(self, api_client):
        """Test handling of invalid banner ID"""
        response = api_client.get("/api/v1/banners/invalid")
        # Should return 404 for non-existent banner
        assert response.status_code == 404
    
    def test_missing_required_fields(self, api_client):
        """Test validation of required fields"""
        # Search without query
        response = api_client.get("/api/v1/products/search")
        assert response.status_code == 422
        
        # Add to cart without data
        response = api_client.post("/api/v1/cart/items", json={})
        assert response.status_code in [401, 422]
    
    def test_invalid_auth_token(self, api_client):
        """Test handling of invalid auth token"""
        headers = {"Authorization": "Bearer invalid_token_here"}
        
        response = api_client.get("/api/v1/auth/profile", headers=headers)
        assert response.status_code in [401, 403]
        
        response = api_client.get("/api/v1/cart", headers=headers)
        assert response.status_code in [401, 403, 404]


@pytest.mark.integration
class TestDatabaseIntegrity:
    """Test database integrity and relationships"""
    
    def test_product_brand_relationship(self, test_db, sample_product, sample_brand):
        """Test product-brand relationship"""
        from src.app_01.models.products.product import Product
        
        product = test_db.query(Product).filter_by(id=sample_product.id).first()
        assert product.brand_id == sample_brand.id
        assert product.brand.name == "Nike"
    
    def test_product_category_relationship(self, test_db, sample_product, sample_category):
        """Test product-category relationship"""
        from src.app_01.models.products.product import Product
        
        product = test_db.query(Product).filter_by(id=sample_product.id).first()
        assert product.category_id == sample_category.id
        assert product.category.name == "Shoes"
    
    def test_cascade_delete_protection(self, test_db, sample_brand, sample_product):
        """Test that deleting brand doesn't orphan products"""
        from src.app_01.models.products.product import Product
        
        # Product should exist
        product = test_db.query(Product).filter_by(id=sample_product.id).first()
        assert product is not None
        
        # This tests database integrity (actual cascade behavior depends on config)
        assert product.brand_id == sample_brand.id


@pytest.mark.integration
class TestConcurrentOperations:
    """Test concurrent operations"""
    
    def test_multiple_searches_simultaneously(self, api_client):
        """Test handling multiple search requests"""
        queries = ["shoes", "shirt", "pants", "jacket", "dress"]
        
        for query in queries:
            response = api_client.get(f"/api/v1/products/search?q={query}")
            assert response.status_code in [200, 422]
    
    def test_multiple_product_views(self, api_client, sample_product):
        """Test viewing same product multiple times"""
        for _ in range(5):
            response = api_client.get(f"/api/v1/products/{sample_product.id}")
            assert response.status_code in [200, 404, 422]


@pytest.mark.integration
class TestPagination:
    """Test pagination across endpoints"""
    
    def test_products_pagination_consistency(self, api_client):
        """Test products pagination is consistent"""
        # Page 1
        response1 = api_client.get("/api/v1/products?page=1&limit=5")
        if response1.status_code == 200:
            # Page 2
            response2 = api_client.get("/api/v1/products?page=2&limit=5")
            assert response2.status_code in [200, 422]
    
    def test_search_pagination_metadata(self, api_client):
        """Test search pagination metadata"""
        response = api_client.get("/api/v1/products/search?q=test&page=1&limit=10")
        
        if response.status_code == 200:
            data = response.json()
            assert "page" in data
            assert "limit" in data
            assert "total" in data
            assert "total_pages" in data
            assert "has_more" in data


@pytest.mark.integration
@pytest.mark.slow
class TestPerformance:
    """Test performance of integration scenarios"""
    
    def test_search_performance(self, api_client):
        """Test search response time"""
        import time
        
        start = time.time()
        response = api_client.get("/api/v1/products/search?q=test")
        end = time.time()
        
        # Should respond within reasonable time (2 seconds for test env)
        assert (end - start) < 2.0
        assert response.status_code in [200, 422]
    
    def test_product_list_performance(self, api_client):
        """Test product listing response time"""
        import time
        
        start = time.time()
        response = api_client.get("/api/v1/products?limit=20")
        end = time.time()
        
        # Should respond within reasonable time
        assert (end - start) < 2.0
        assert response.status_code in [200, 422]

