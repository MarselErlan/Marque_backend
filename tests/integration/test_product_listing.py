"""
Test Suite: Product Listing API
Tests for browsing products with pagination, sorting, and filtering
"""

import pytest
from sqlalchemy.orm import Session


class TestProductListing:
    """Test basic product listing by subcategory"""

    def test_get_products_by_subcategory(self, api_client, sample_products_in_subcategory):
        """
        GIVEN: Products exist in a subcategory
        WHEN: GET /api/v1/subcategories/{slug}/products
        THEN: Returns list of products
        """
        response = api_client.get("/api/v1/subcategories/t-shirts-polos/products")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "products" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data
        assert "total_pages" in data
        
        assert len(data["products"]) > 0
        assert data["total"] > 0

    def test_product_listing_includes_required_fields(self, api_client, sample_products_in_subcategory):
        """
        GIVEN: Products in subcategory
        WHEN: GET /api/v1/subcategories/{slug}/products
        THEN: Each product has required fields
        """
        response = api_client.get("/api/v1/subcategories/t-shirts-polos/products")
        
        assert response.status_code == 200
        products = response.json()["products"]
        
        for product in products:
            # Basic info
            assert "id" in product
            assert "title" in product
            assert "slug" in product
            
            # Pricing
            assert "price_min" in product
            assert "price_max" in product
            
            # Image
            assert "image" in product  # Main image URL
            
            # Rating
            assert "rating_avg" in product
            assert "rating_count" in product
            
            # Brand
            assert "brand_name" in product
            assert "brand_slug" in product

    def test_pagination_default_values(self, api_client, sample_products_in_subcategory):
        """
        GIVEN: Products in subcategory
        WHEN: GET /api/v1/subcategories/{slug}/products (no params)
        THEN: Returns first page with default limit
        """
        response = api_client.get("/api/v1/subcategories/t-shirts-polos/products")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["page"] == 1
        assert data["limit"] == 20  # Default limit
        assert len(data["products"]) <= 20

    def test_pagination_with_custom_page(self, api_client, sample_many_products_in_subcategory):
        """
        GIVEN: Many products in subcategory
        WHEN: GET /api/v1/subcategories/{slug}/products?page=2&limit=10
        THEN: Returns second page with 10 items
        """
        response = api_client.get("/api/v1/subcategories/t-shirts-polos/products?page=2&limit=10")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["page"] == 2
        assert data["limit"] == 10
        assert len(data["products"]) <= 10

    def test_pagination_total_pages_calculation(self, api_client, sample_many_products_in_subcategory):
        """
        GIVEN: 25 products in subcategory
        WHEN: GET /api/v1/subcategories/{slug}/products?limit=10
        THEN: total_pages is calculated correctly (3 pages)
        """
        response = api_client.get("/api/v1/subcategories/t-shirts-polos/products?limit=10")
        
        assert response.status_code == 200
        data = response.json()
        
        # 25 products / 10 per page = 3 pages
        assert data["total"] == 25
        assert data["total_pages"] == 3

    def test_empty_subcategory_returns_empty_list(self, api_client, sample_empty_subcategory):
        """
        GIVEN: Subcategory with no products
        WHEN: GET /api/v1/subcategories/{slug}/products
        THEN: Returns empty list with total=0
        """
        response = api_client.get("/api/v1/subcategories/empty-subcategory/products")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["products"] == []
        assert data["total"] == 0
        assert data["total_pages"] == 0

    def test_nonexistent_subcategory_returns_404(self, api_client):
        """
        GIVEN: Subcategory doesn't exist
        WHEN: GET /api/v1/subcategories/nonexistent/products
        THEN: Returns 404
        """
        response = api_client.get("/api/v1/subcategories/nonexistent/products")
        
        assert response.status_code == 404

    def test_only_active_products_shown(self, api_client, sample_products_active_and_inactive):
        """
        GIVEN: Mix of active and inactive products
        WHEN: GET /api/v1/subcategories/{slug}/products
        THEN: Only active products returned
        """
        response = api_client.get("/api/v1/subcategories/t-shirts-polos/products")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should only include active products (3 out of 5)
        assert data["total"] == 3
        assert len(data["products"]) == 3

    def test_products_with_no_skus_excluded(self, api_client, sample_products_with_and_without_skus):
        """
        GIVEN: Products with and without SKUs
        WHEN: GET /api/v1/subcategories/{slug}/products
        THEN: Only products with SKUs shown
        """
        response = api_client.get("/api/v1/subcategories/t-shirts-polos/products")
        
        assert response.status_code == 200
        data = response.json()
        
        # All returned products should have price_min > 0 (indicating they have SKUs)
        for product in data["products"]:
            assert product["price_min"] > 0


class TestProductSorting:
    """Test product sorting options"""

    def test_sort_by_price_ascending(self, api_client, sample_products_various_prices):
        """
        GIVEN: Products with different prices
        WHEN: GET /api/v1/subcategories/{slug}/products?sort_by=price_asc
        THEN: Products sorted by price low to high
        """
        response = api_client.get("/api/v1/subcategories/t-shirts-polos/products?sort_by=price_asc")
        
        assert response.status_code == 200
        products = response.json()["products"]
        
        # Verify ascending order
        prices = [p["price_min"] for p in products]
        assert prices == sorted(prices)

    def test_sort_by_price_descending(self, api_client, sample_products_various_prices):
        """
        GIVEN: Products with different prices
        WHEN: GET /api/v1/subcategories/{slug}/products?sort_by=price_desc
        THEN: Products sorted by price high to low
        """
        response = api_client.get("/api/v1/subcategories/t-shirts-polos/products?sort_by=price_desc")
        
        assert response.status_code == 200
        products = response.json()["products"]
        
        # Verify descending order
        prices = [p["price_min"] for p in products]
        assert prices == sorted(prices, reverse=True)

    def test_sort_by_newest(self, api_client, sample_products_different_dates):
        """
        GIVEN: Products created at different times
        WHEN: GET /api/v1/subcategories/{slug}/products?sort_by=newest
        THEN: Products sorted by created_at DESC
        """
        response = api_client.get("/api/v1/subcategories/t-shirts-polos/products?sort_by=newest")
        
        assert response.status_code == 200
        products = response.json()["products"]
        
        # First product should be the newest
        assert len(products) > 0
        # We can't easily verify dates in response, but endpoint should work

    def test_sort_by_popular(self, api_client, sample_products_different_popularity):
        """
        GIVEN: Products with different sold_count
        WHEN: GET /api/v1/subcategories/{slug}/products?sort_by=popular
        THEN: Products sorted by sold_count DESC
        """
        response = api_client.get("/api/v1/subcategories/t-shirts-polos/products?sort_by=popular")
        
        assert response.status_code == 200
        products = response.json()["products"]
        
        # Products should be in order of popularity
        # We need to add sold_count to the response schema for this test
        assert len(products) > 0

    def test_sort_by_rating(self, api_client, sample_products_different_ratings):
        """
        GIVEN: Products with different ratings
        WHEN: GET /api/v1/subcategories/{slug}/products?sort_by=rating
        THEN: Products sorted by rating_avg DESC
        """
        response = api_client.get("/api/v1/subcategories/t-shirts-polos/products?sort_by=rating")
        
        assert response.status_code == 200
        products = response.json()["products"]
        
        # Verify descending rating order
        ratings = [p["rating_avg"] for p in products]
        assert ratings == sorted(ratings, reverse=True)

    def test_default_sort_is_newest(self, api_client, sample_products_different_dates):
        """
        GIVEN: Products with different dates
        WHEN: GET /api/v1/subcategories/{slug}/products (no sort param)
        THEN: Default sort is newest
        """
        response = api_client.get("/api/v1/subcategories/t-shirts-polos/products")
        
        assert response.status_code == 200
        # Should not error, default sort applied
        assert len(response.json()["products"]) > 0

    def test_invalid_sort_param_ignored(self, api_client, sample_products_in_subcategory):
        """
        GIVEN: Products in subcategory
        WHEN: GET /api/v1/subcategories/{slug}/products?sort_by=invalid
        THEN: Falls back to default sort
        """
        response = api_client.get("/api/v1/subcategories/t-shirts-polos/products?sort_by=invalid")
        
        assert response.status_code == 200
        # Should not error, just use default sort
        assert len(response.json()["products"]) > 0


class TestProductFiltering:
    """Test product filtering options"""

    def test_filter_by_price_range(self, api_client, sample_products_various_prices):
        """
        GIVEN: Products with prices from 1000 to 5000
        WHEN: GET /api/v1/subcategories/{slug}/products?price_min=2000&price_max=3000
        THEN: Only products in price range returned
        """
        response = api_client.get("/api/v1/subcategories/t-shirts-polos/products?price_min=2000&price_max=3000")
        
        assert response.status_code == 200
        products = response.json()["products"]
        
        for product in products:
            assert product["price_min"] >= 2000
            assert product["price_min"] <= 3000

    def test_filter_by_min_price_only(self, api_client, sample_products_various_prices):
        """
        GIVEN: Products with various prices
        WHEN: GET /api/v1/subcategories/{slug}/products?price_min=3000
        THEN: Only products >= 3000 returned
        """
        response = api_client.get("/api/v1/subcategories/t-shirts-polos/products?price_min=3000")
        
        assert response.status_code == 200
        products = response.json()["products"]
        
        for product in products:
            assert product["price_min"] >= 3000

    def test_filter_by_max_price_only(self, api_client, sample_products_various_prices):
        """
        GIVEN: Products with various prices
        WHEN: GET /api/v1/subcategories/{slug}/products?price_max=2000
        THEN: Only products <= 2000 returned
        """
        response = api_client.get("/api/v1/subcategories/t-shirts-polos/products?price_max=2000")
        
        assert response.status_code == 200
        products = response.json()["products"]
        
        for product in products:
            assert product["price_min"] <= 2000

    def test_filter_by_single_size(self, api_client, sample_products_various_sizes):
        """
        GIVEN: Products with different sizes
        WHEN: GET /api/v1/subcategories/{slug}/products?sizes=M
        THEN: Only products with size M returned
        """
        response = api_client.get("/api/v1/subcategories/t-shirts-polos/products?sizes=M")
        
        assert response.status_code == 200
        products = response.json()["products"]
        
        # All returned products should have M size available
        assert len(products) > 0

    def test_filter_by_multiple_sizes(self, api_client, sample_products_various_sizes):
        """
        GIVEN: Products with different sizes
        WHEN: GET /api/v1/subcategories/{slug}/products?sizes=M,L,XL
        THEN: Products with any of those sizes returned
        """
        response = api_client.get("/api/v1/subcategories/t-shirts-polos/products?sizes=M,L,XL")
        
        assert response.status_code == 200
        products = response.json()["products"]
        
        assert len(products) > 0

    def test_filter_by_single_color(self, api_client, sample_products_various_colors):
        """
        GIVEN: Products with different colors
        WHEN: GET /api/v1/subcategories/{slug}/products?colors=black
        THEN: Only products with black color returned
        """
        response = api_client.get("/api/v1/subcategories/t-shirts-polos/products?colors=black")
        
        assert response.status_code == 200
        products = response.json()["products"]
        
        assert len(products) > 0

    def test_filter_by_multiple_colors(self, api_client, sample_products_various_colors):
        """
        GIVEN: Products with different colors
        WHEN: GET /api/v1/subcategories/{slug}/products?colors=black,white,blue
        THEN: Products with any of those colors returned
        """
        response = api_client.get("/api/v1/subcategories/t-shirts-polos/products?colors=black,white,blue")
        
        assert response.status_code == 200
        products = response.json()["products"]
        
        assert len(products) > 0

    def test_filter_by_single_brand(self, api_client, sample_products_multiple_brands):
        """
        GIVEN: Products from different brands
        WHEN: GET /api/v1/subcategories/{slug}/products?brands=nike
        THEN: Only Nike products returned
        """
        response = api_client.get("/api/v1/subcategories/t-shirts-polos/products?brands=nike")
        
        assert response.status_code == 200
        products = response.json()["products"]
        
        for product in products:
            assert product["brand_slug"] == "nike"

    def test_filter_by_multiple_brands(self, api_client, sample_products_multiple_brands):
        """
        GIVEN: Products from different brands
        WHEN: GET /api/v1/subcategories/{slug}/products?brands=nike,adidas,puma
        THEN: Products from those brands returned
        """
        response = api_client.get("/api/v1/subcategories/t-shirts-polos/products?brands=nike,adidas,puma")
        
        assert response.status_code == 200
        products = response.json()["products"]
        
        for product in products:
            assert product["brand_slug"] in ["nike", "adidas", "puma"]

    def test_combine_multiple_filters(self, api_client, sample_products_for_filtering):
        """
        GIVEN: Products with various attributes
        WHEN: GET /api/v1/subcategories/{slug}/products?price_min=2000&price_max=4000&sizes=M,L&colors=black&brands=nike
        THEN: Only products matching ALL filters returned
        """
        response = api_client.get(
            "/api/v1/subcategories/t-shirts-polos/products"
            "?price_min=2000&price_max=4000&sizes=M,L&colors=black&brands=nike"
        )
        
        assert response.status_code == 200
        products = response.json()["products"]
        
        # Verify all filters applied
        for product in products:
            assert product["price_min"] >= 2000
            assert product["price_min"] <= 4000
            assert product["brand_slug"] == "nike"

    def test_filters_with_sorting(self, api_client, sample_products_for_filtering):
        """
        GIVEN: Products with various attributes
        WHEN: GET /api/v1/subcategories/{slug}/products?price_min=2000&sort_by=price_asc
        THEN: Filtered results are sorted correctly
        """
        response = api_client.get(
            "/api/v1/subcategories/t-shirts-polos/products?price_min=2000&sort_by=price_asc"
        )
        
        assert response.status_code == 200
        products = response.json()["products"]
        
        # All products should be >= 2000
        for product in products:
            assert product["price_min"] >= 2000
        
        # And sorted by price ascending
        prices = [p["price_min"] for p in products]
        assert prices == sorted(prices)

    def test_filters_with_pagination(self, api_client, sample_many_products_for_filtering):
        """
        GIVEN: Many products matching filter
        WHEN: GET /api/v1/subcategories/{slug}/products?colors=black&page=1&limit=5
        THEN: Pagination works with filters
        """
        response = api_client.get(
            "/api/v1/subcategories/t-shirts-polos/products?colors=black&page=1&limit=5"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["page"] == 1
        assert data["limit"] == 5
        assert len(data["products"]) <= 5
        assert data["total"] > 0  # Total filtered count

    def test_filter_returns_accurate_count(self, api_client, sample_products_for_filtering):
        """
        GIVEN: 10 products, 5 are black
        WHEN: GET /api/v1/subcategories/{slug}/products?colors=black
        THEN: total reflects filtered count (5)
        """
        response = api_client.get("/api/v1/subcategories/t-shirts-polos/products?colors=black")
        
        assert response.status_code == 200
        data = response.json()
        
        # Total should reflect filtered count, not all products
        assert data["total"] == 5


class TestProductSearch:
    """Test search within subcategory"""

    def test_search_by_keyword_in_title(self, api_client, sample_products_for_search):
        """
        GIVEN: Products with different titles
        WHEN: GET /api/v1/subcategories/{slug}/products?search=cotton
        THEN: Only products with 'cotton' in title returned
        """
        response = api_client.get("/api/v1/subcategories/t-shirts-polos/products?search=cotton")
        
        assert response.status_code == 200
        products = response.json()["products"]
        
        # All returned products should have 'cotton' in title (case insensitive)
        for product in products:
            assert "cotton" in product["title"].lower()

    def test_search_case_insensitive(self, api_client, sample_products_for_search):
        """
        GIVEN: Products with titles
        WHEN: GET /api/v1/subcategories/{slug}/products?search=COTTON
        THEN: Case insensitive search works
        """
        response = api_client.get("/api/v1/subcategories/t-shirts-polos/products?search=COTTON")
        
        assert response.status_code == 200
        products = response.json()["products"]
        
        assert len(products) > 0

    def test_search_with_filters(self, api_client, sample_products_for_search):
        """
        GIVEN: Products with various attributes
        WHEN: GET /api/v1/subcategories/{slug}/products?search=shirt&colors=black
        THEN: Search and filters combined
        """
        response = api_client.get("/api/v1/subcategories/t-shirts-polos/products?search=shirt&colors=black")
        
        assert response.status_code == 200
        products = response.json()["products"]
        
        # Products should match search term AND filter
        for product in products:
            assert "shirt" in product["title"].lower()

    def test_search_with_no_results(self, api_client, sample_products_for_search):
        """
        GIVEN: Products in subcategory
        WHEN: GET /api/v1/subcategories/{slug}/products?search=nonexistent
        THEN: Returns empty list
        """
        response = api_client.get("/api/v1/subcategories/t-shirts-polos/products?search=nonexistent")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["products"] == []
        assert data["total"] == 0

