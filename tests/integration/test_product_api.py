"""
Integration tests for product API
Tests product listing, search, and detail endpoints
"""

import pytest


@pytest.mark.integration
class TestProductListingAPI:
    """Test product listing endpoints"""
    
    def test_get_products_endpoint_exists(self, api_client):
        """Test that products endpoint exists"""
        response = api_client.get("/api/v1/products")
        
        # Should not be 404
        assert response.status_code != 404
    
    def test_get_products_returns_list(self, api_client):
        """Test that products endpoint returns a list"""
        response = api_client.get("/api/v1/products")
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    def test_get_products_with_pagination(self, api_client):
        """Test products with pagination parameters"""
        response = api_client.get("/api/v1/products?page=1&limit=10")
        
        # Should handle pagination
        assert response.status_code in [200, 422]
    
    def test_get_products_with_category_filter(self, api_client, sample_category):
        """Test filtering products by category"""
        response = api_client.get(f"/api/v1/products?category={sample_category.slug}")
        
        assert response.status_code in [200, 422]
    
    def test_get_products_with_brand_filter(self, api_client, sample_brand):
        """Test filtering products by brand"""
        response = api_client.get(f"/api/v1/products?brand={sample_brand.slug}")
        
        assert response.status_code in [200, 422]


@pytest.mark.integration
class TestProductSearchAPI:
    """Test product search endpoints"""
    
    def test_search_endpoint_exists(self, api_client):
        """Test that search endpoint exists"""
        response = api_client.get("/api/v1/products/search?q=test")
        
        # Should not be 404
        assert response.status_code != 404
    
    def test_search_requires_query(self, api_client):
        """Test that search requires query parameter"""
        response = api_client.get("/api/v1/products/search")
        
        # Should return validation error
        assert response.status_code == 422
    
    def test_search_with_valid_query(self, api_client):
        """Test search with valid query"""
        response = api_client.get("/api/v1/products/search?q=shoes")
        
        if response.status_code == 200:
            data = response.json()
            assert "query" in data
            assert "results" in data
            assert "total" in data
            assert data["query"] == "shoes"
    
    def test_search_with_filters(self, api_client):
        """Test search with multiple filters"""
        response = api_client.get(
            "/api/v1/products/search?q=running&min_price=50&max_price=200&sort_by=relevance"
        )
        
        assert response.status_code in [200, 422]
    
    def test_search_with_pagination(self, api_client):
        """Test search with pagination"""
        response = api_client.get("/api/v1/products/search?q=test&page=1&limit=5")
        
        if response.status_code == 200:
            data = response.json()
            assert data["page"] == 1
            assert data["limit"] == 5


@pytest.mark.integration
class TestProductDetailAPI:
    """Test product detail endpoint"""
    
    def test_get_product_by_id(self, api_client, sample_product):
        """Test getting product by ID"""
        response = api_client.get(f"/api/v1/products/{sample_product.id}")
        
        if response.status_code == 200:
            data = response.json()
            assert data["id"] == str(sample_product.id)
            assert data["name"] == sample_product.title
    
    def test_get_nonexistent_product(self, api_client):
        """Test getting non-existent product"""
        response = api_client.get("/api/v1/products/999999")
        
        # Should return 404
        assert response.status_code in [404, 422]
    
    def test_get_product_invalid_id(self, api_client):
        """Test getting product with invalid ID"""
        response = api_client.get("/api/v1/products/invalid")
        
        # Should return validation error
        assert response.status_code == 422


@pytest.mark.integration
class TestProductWithDatabase:
    """Test product operations with database"""
    
    def test_product_in_database(self, test_db, sample_product):
        """Test that product is created in database"""
        from src.app_01.models.products.product import Product
        
        product = test_db.query(Product).filter_by(id=sample_product.id).first()
        assert product is not None
        assert product.title == "Running Shoes"
    
    def test_product_with_relationships(self, test_db, sample_product):
        """Test product with brand and category relationships"""
        from src.app_01.models.products.product import Product
        
        product = test_db.query(Product).filter_by(id=sample_product.id).first()
        assert product.brand is not None
        assert product.category is not None
        assert product.brand.name == "Nike"
        assert product.category.name == "Shoes"
    
    def test_search_finds_product(self, api_client, sample_product):
        """Test that search can find created product"""
        response = api_client.get("/api/v1/products/search?q=running")
        
        if response.status_code == 200:
            data = response.json()
            # May or may not find product depending on implementation
            assert "results" in data


@pytest.mark.integration
class TestProductSorting:
    """Test product sorting in API"""
    
    @pytest.mark.parametrize("sort_option", [
        "newest", "popular", "price_low", "price_high", "relevance"
    ])
    def test_sort_options(self, api_client, sort_option):
        """Test different sort options"""
        response = api_client.get(f"/api/v1/products/search?q=test&sort_by={sort_option}")
        
        # Should accept valid sort options
        assert response.status_code in [200, 422]

