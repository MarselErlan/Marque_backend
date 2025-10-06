"""
Test Suite: Product Detail API
Tests for product detail page functionality
"""

import pytest
from sqlalchemy.orm import Session

from src.app_01.models import Product, SKU, ProductAsset, Review


class TestProductDetail:
    """Test product detail endpoint"""

    def test_get_product_by_slug(self, api_client, sample_product_with_details):
        """
        GIVEN: Product with slug exists
        WHEN: GET /api/v1/products/{slug}
        THEN: Returns complete product details
        """
        product = sample_product_with_details
        response = api_client.get(f"/api/v1/products/{product.slug}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Basic product info
        assert data["id"] == product.id
        assert data["title"] == product.title
        assert data["slug"] == product.slug
        assert data["description"] == product.description
        assert "brand" in data
        assert "category" in data
        assert "subcategory" in data

    def test_product_includes_images(self, api_client, sample_product_with_images):
        """
        GIVEN: Product with multiple images
        WHEN: GET /api/v1/products/{slug}
        THEN: Returns all product images in order
        """
        product = sample_product_with_images
        response = api_client.get(f"/api/v1/products/{product.slug}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "images" in data
        assert len(data["images"]) > 0
        # Images should be sorted by order
        assert data["images"][0]["order"] == 1

    def test_product_includes_skus(self, api_client, sample_product_with_skus):
        """
        GIVEN: Product with multiple SKUs
        WHEN: GET /api/v1/products/{slug}
        THEN: Returns all SKUs with sizes, colors, prices, stock
        """
        product = sample_product_with_skus
        response = api_client.get(f"/api/v1/products/{product.slug}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "skus" in data
        assert len(data["skus"]) > 0
        
        # Check SKU structure
        sku = data["skus"][0]
        assert "id" in sku
        assert "size" in sku
        assert "color" in sku
        assert "price" in sku
        assert "original_price" in sku
        assert "stock" in sku
        assert "sku_code" in sku

    def test_product_includes_available_sizes(self, api_client, sample_product_with_skus):
        """
        GIVEN: Product with multiple sizes
        WHEN: GET /api/v1/products/{slug}
        THEN: Returns unique list of available sizes
        """
        product = sample_product_with_skus
        response = api_client.get(f"/api/v1/products/{product.slug}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "available_sizes" in data
        assert len(data["available_sizes"]) > 0
        # Should be unique sizes
        assert len(data["available_sizes"]) == len(set(data["available_sizes"]))

    def test_product_includes_available_colors(self, api_client, sample_product_with_skus):
        """
        GIVEN: Product with multiple colors
        WHEN: GET /api/v1/products/{slug}
        THEN: Returns unique list of available colors
        """
        product = sample_product_with_skus
        response = api_client.get(f"/api/v1/products/{product.slug}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "available_colors" in data
        assert len(data["available_colors"]) > 0

    def test_product_includes_price_range(self, api_client, sample_product_with_skus):
        """
        GIVEN: Product with SKUs at different prices
        WHEN: GET /api/v1/products/{slug}
        THEN: Returns min and max price
        """
        product = sample_product_with_skus
        response = api_client.get(f"/api/v1/products/{product.slug}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "price_min" in data
        assert "price_max" in data
        assert data["price_min"] <= data["price_max"]

    def test_product_includes_stock_status(self, api_client, sample_product_with_skus):
        """
        GIVEN: Product with SKUs
        WHEN: GET /api/v1/products/{slug}
        THEN: Returns overall stock availability
        """
        product = sample_product_with_skus
        response = api_client.get(f"/api/v1/products/{product.slug}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "in_stock" in data
        assert isinstance(data["in_stock"], bool)

    def test_product_includes_reviews(self, api_client, sample_product_with_reviews):
        """
        GIVEN: Product with reviews
        WHEN: GET /api/v1/products/{slug}
        THEN: Returns reviews with ratings
        """
        product = sample_product_with_reviews
        response = api_client.get(f"/api/v1/products/{product.slug}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "reviews" in data
        assert "rating_avg" in data
        assert "rating_count" in data
        
        if len(data["reviews"]) > 0:
            review = data["reviews"][0]
            assert "id" in review
            assert "rating" in review
            assert "text" in review
            assert "created_at" in review

    def test_product_includes_breadcrumbs(self, api_client, sample_product_with_details):
        """
        GIVEN: Product with category and subcategory
        WHEN: GET /api/v1/products/{slug}
        THEN: Returns breadcrumb navigation data
        """
        product = sample_product_with_details
        response = api_client.get(f"/api/v1/products/{product.slug}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "breadcrumbs" in data
        breadcrumbs = data["breadcrumbs"]
        assert len(breadcrumbs) >= 3  # Category > Subcategory > Product
        
        # Check breadcrumb structure
        assert "name" in breadcrumbs[0]
        assert "slug" in breadcrumbs[0]

    def test_product_includes_similar_products(self, api_client, sample_product_with_similar):
        """
        GIVEN: Product with similar products in same category
        WHEN: GET /api/v1/products/{slug}
        THEN: Returns list of similar products
        """
        product = sample_product_with_similar
        response = api_client.get(f"/api/v1/products/{product.slug}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "similar_products" in data
        # Similar products should not include the current product
        similar_ids = [p["id"] for p in data["similar_products"]]
        assert product.id not in similar_ids

    def test_get_nonexistent_product_returns_404(self, api_client):
        """
        GIVEN: No product with given slug
        WHEN: GET /api/v1/products/{invalid_slug}
        THEN: Returns 404
        """
        response = api_client.get("/api/v1/products/nonexistent-product")
        
        assert response.status_code == 404

    def test_inactive_product_returns_404(self, api_client, inactive_product):
        """
        GIVEN: Product exists but is inactive
        WHEN: GET /api/v1/products/{slug}
        THEN: Returns 404
        """
        response = api_client.get(f"/api/v1/products/{inactive_product.slug}")
        
        assert response.status_code == 404

    def test_product_with_discount(self, api_client, sample_product_with_discount):
        """
        GIVEN: Product with discount
        WHEN: GET /api/v1/products/{slug}
        THEN: Returns discount information
        """
        product = sample_product_with_discount
        response = api_client.get(f"/api/v1/products/{product.slug}")
        
        assert response.status_code == 200
        data = response.json()
        
        # At least one SKU should have discount
        skus_with_discount = [sku for sku in data["skus"] if sku.get("original_price", 0) > sku["price"]]
        assert len(skus_with_discount) > 0

    def test_product_attributes(self, api_client, sample_product_with_details):
        """
        GIVEN: Product with attributes (gender, season, composition)
        WHEN: GET /api/v1/products/{slug}
        THEN: Returns all product attributes
        """
        product = sample_product_with_details
        response = api_client.get(f"/api/v1/products/{product.slug}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "attributes" in data
        # Attributes should be a dict with composition, gender, season, etc.
        assert isinstance(data["attributes"], dict)

