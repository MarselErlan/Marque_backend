"""
Test Suite: Catalog Navigation API
Tests for category and subcategory navigation endpoints
"""

import pytest
from sqlalchemy.orm import Session

from src.app_01.models import Category, Subcategory, Product, Brand, SKU


class TestCategoryNavigation:
    """Test category listing and navigation"""

    def test_get_all_main_categories(self, api_client, sample_categories):
        """
        GIVEN: Database with categories
        WHEN: GET /api/v1/categories
        THEN: Returns all active categories with product counts
        """
        response = api_client.get("/api/v1/categories")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "categories" in data
        assert len(data["categories"]) > 0
        
        # Check first category structure
        category = data["categories"][0]
        assert "id" in category
        assert "name" in category
        assert "slug" in category
        assert "product_count" in category
        assert "icon" in category
        assert "sort_order" in category
        assert category["is_active"] is True

    def test_get_category_with_subcategories(self, api_client, sample_categories_with_subcategories):
        """
        GIVEN: Category with subcategories
        WHEN: GET /api/categories/{slug}
        THEN: Returns category detail with subcategories
        """
        response = api_client.get("/api/v1/categories/men")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["slug"] == "men"
        assert "name" in data
        assert "description" in data
        assert "product_count" in data
        assert "subcategories" in data
        assert len(data["subcategories"]) > 0
        
        # Check subcategory structure
        subcategory = data["subcategories"][0]
        assert "id" in subcategory
        assert "name" in subcategory
        assert "slug" in subcategory
        assert "product_count" in subcategory
        assert "sort_order" in subcategory

    def test_get_subcategories_by_category_slug(self, api_client, sample_categories_with_subcategories):
        """
        GIVEN: Category with subcategories
        WHEN: GET /api/categories/{slug}/subcategories
        THEN: Returns list of subcategories
        """
        response = api_client.get("/api/v1/categories/men/subcategories")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "subcategories" in data
        assert len(data["subcategories"]) > 0
        
        # Verify all subcategories belong to men category
        for subcategory in data["subcategories"]:
            assert "name" in subcategory
            assert "slug" in subcategory
            assert "product_count" in subcategory

    def test_category_includes_product_count(self, api_client, sample_products_in_category):
        """
        GIVEN: Category with products
        WHEN: GET /api/categories/{slug}
        THEN: Product count is accurate
        """
        response = api_client.get("/api/v1/categories/men")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["product_count"] > 0
        # The fixture creates products, so count should match

    def test_subcategory_includes_product_count(self, api_client, sample_products_in_subcategory):
        """
        GIVEN: Subcategory with products
        WHEN: GET /api/categories/{category_slug}/subcategories
        THEN: Each subcategory shows correct product count
        """
        response = api_client.get("/api/v1/categories/men/subcategories")
        
        assert response.status_code == 200
        data = response.json()
        
        # Find the t-shirts subcategory
        tshirt_sub = next((s for s in data["subcategories"] if s["slug"] == "t-shirts-polos"), None)
        assert tshirt_sub is not None
        assert tshirt_sub["product_count"] > 0

    def test_inactive_categories_not_returned(self, api_client, inactive_category):
        """
        GIVEN: Mix of active and inactive categories
        WHEN: GET /api/categories
        THEN: Only active categories returned
        """
        response = api_client.get("/api/v1/categories")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify inactive category not in results
        slugs = [cat["slug"] for cat in data["categories"]]
        assert "inactive-category" not in slugs

    def test_categories_sorted_by_order(self, api_client, sample_categories):
        """
        GIVEN: Categories with different sort_order values
        WHEN: GET /api/categories
        THEN: Categories returned in sort_order
        """
        response = api_client.get("/api/v1/categories")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify sorting
        sort_orders = [cat["sort_order"] for cat in data["categories"]]
        assert sort_orders == sorted(sort_orders)

    def test_get_nonexistent_category_returns_404(self, api_client):
        """
        GIVEN: No category with given slug
        WHEN: GET /api/categories/{invalid_slug}
        THEN: Returns 404
        """
        response = api_client.get("/api/v1/categories/nonexistent")
        
        assert response.status_code == 404

    def test_subcategories_sorted_by_order(self, api_client, sample_categories_with_subcategories):
        """
        GIVEN: Subcategories with different sort_order
        WHEN: GET /api/categories/{slug}/subcategories
        THEN: Subcategories returned in correct order
        """
        response = api_client.get("/api/v1/categories/men/subcategories")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify sorting
        sort_orders = [sub["sort_order"] for sub in data["subcategories"]]
        assert sort_orders == sorted(sort_orders)
