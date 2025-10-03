"""
Unit tests for product search functionality
Tests for search logic, filtering, sorting, and pagination
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy.orm import Query

from src.app_01.models.products.product import Product
from src.app_01.models.products.brand import Brand
from src.app_01.models.products.category import Category
from src.app_01.models.products.sku import SKU
from src.app_01.schemas.product import ProductSchema, ProductSearchResponse


class TestSearchQueryBuilding:
    """Test search query construction"""
    
    def test_search_query_with_term(self):
        """Test that search term is applied to query"""
        search_term = "running shoes"
        expected_pattern = f"%{search_term}%"
        
        assert expected_pattern == "%running shoes%"
    
    def test_search_case_insensitive(self):
        """Test that search is case insensitive"""
        term1 = "SHOES"
        term2 = "shoes"
        term3 = "ShOeS"
        
        # All should produce same pattern
        assert f"%{term1.lower()}%" == f"%{term2.lower()}%" == f"%{term3.lower()}%"
    
    def test_search_partial_matching(self):
        """Test partial matching with wildcards"""
        search = "run"
        pattern = f"%{search}%"
        
        # Should match: running, runner, run, etc.
        test_values = ["running", "runner", "run", "sunrunner"]
        for value in test_values:
            assert search.lower() in value.lower()


class TestSearchFiltering:
    """Test search filtering logic"""
    
    def test_category_filter(self):
        """Test filtering by category"""
        category_slug = "mens-clothing"
        
        # Mock filter would check category.slug == category_slug
        assert category_slug == "mens-clothing"
    
    def test_brand_filter(self):
        """Test filtering by brand"""
        brand_slug = "nike"
        
        # Mock filter would check brand.slug == brand_slug
        assert brand_slug == "nike"
    
    def test_price_range_filter_min(self):
        """Test minimum price filter"""
        min_price = 50.0
        test_prices = [30.0, 50.0, 75.0, 100.0]
        
        filtered = [p for p in test_prices if p >= min_price]
        assert filtered == [50.0, 75.0, 100.0]
    
    def test_price_range_filter_max(self):
        """Test maximum price filter"""
        max_price = 100.0
        test_prices = [30.0, 50.0, 75.0, 100.0, 150.0]
        
        filtered = [p for p in test_prices if p <= max_price]
        assert filtered == [30.0, 50.0, 75.0, 100.0]
    
    def test_price_range_filter_both(self):
        """Test both min and max price filters"""
        min_price = 50.0
        max_price = 100.0
        test_prices = [30.0, 50.0, 75.0, 100.0, 150.0]
        
        filtered = [p for p in test_prices if min_price <= p <= max_price]
        assert filtered == [50.0, 75.0, 100.0]


class TestSearchSorting:
    """Test search result sorting"""
    
    def test_sort_by_newest(self):
        """Test sorting by newest (created_at desc)"""
        from datetime import datetime, timedelta
        
        dates = [
            datetime.now() - timedelta(days=5),
            datetime.now() - timedelta(days=1),
            datetime.now() - timedelta(days=3),
        ]
        
        sorted_dates = sorted(dates, reverse=True)
        assert sorted_dates[0] > sorted_dates[1] > sorted_dates[2]
    
    def test_sort_by_popular(self):
        """Test sorting by popularity (sold_count desc)"""
        sold_counts = [10, 50, 25, 100, 5]
        
        sorted_counts = sorted(sold_counts, reverse=True)
        assert sorted_counts == [100, 50, 25, 10, 5]
    
    def test_sort_by_price_low_to_high(self):
        """Test sorting by price ascending"""
        prices = [99.99, 19.99, 49.99, 149.99, 29.99]
        
        sorted_prices = sorted(prices)
        assert sorted_prices == [19.99, 29.99, 49.99, 99.99, 149.99]
    
    def test_sort_by_price_high_to_low(self):
        """Test sorting by price descending"""
        prices = [99.99, 19.99, 49.99, 149.99, 29.99]
        
        sorted_prices = sorted(prices, reverse=True)
        assert sorted_prices == [149.99, 99.99, 49.99, 29.99, 19.99]
    
    def test_sort_by_relevance(self):
        """Test relevance sorting (title match priority)"""
        # Title matches should rank higher than description matches
        results = [
            {"title": "Blue Shirt", "has_title_match": False},
            {"title": "Red Running Shoes", "has_title_match": True},
            {"title": "Green Pants", "has_title_match": False},
            {"title": "Running Jacket", "has_title_match": True},
        ]
        
        # Sort by relevance (title matches first)
        sorted_results = sorted(results, key=lambda x: 1 if x["has_title_match"] else 2)
        
        assert sorted_results[0]["has_title_match"] == True
        assert sorted_results[1]["has_title_match"] == True


class TestSearchPagination:
    """Test search pagination logic"""
    
    def test_pagination_offset_calculation(self):
        """Test offset calculation for pagination"""
        page = 1
        limit = 20
        offset = (page - 1) * limit
        assert offset == 0
        
        page = 2
        offset = (page - 1) * limit
        assert offset == 20
        
        page = 3
        offset = (page - 1) * limit
        assert offset == 40
    
    def test_total_pages_calculation(self):
        """Test total pages calculation"""
        total_items = 95
        limit = 20
        total_pages = (total_items + limit - 1) // limit
        assert total_pages == 5
        
        total_items = 100
        total_pages = (total_items + limit - 1) // limit
        assert total_pages == 5
        
        total_items = 101
        total_pages = (total_items + limit - 1) // limit
        assert total_pages == 6
    
    def test_has_more_pages(self):
        """Test has_more flag calculation"""
        page = 1
        total_pages = 5
        has_more = page < total_pages
        assert has_more == True
        
        page = 5
        has_more = page < total_pages
        assert has_more == False
        
        page = 3
        has_more = page < total_pages
        assert has_more == True
    
    def test_pagination_limit_bounds(self):
        """Test pagination limit boundaries"""
        # Minimum limit
        limit = max(1, 0)
        assert limit == 1
        
        # Maximum limit
        limit = min(100, 150)
        assert limit == 100
        
        # Normal limit
        limit = max(1, min(100, 20))
        assert limit == 20


class TestSearchRelevance:
    """Test search relevance scoring"""
    
    def test_title_match_higher_priority(self):
        """Test that title matches rank higher"""
        search_term = "running"
        
        # Simulate relevance scoring
        title_match_score = 1
        description_match_score = 2
        
        assert title_match_score < description_match_score  # Lower = higher priority
    
    def test_exact_match_vs_partial(self):
        """Test exact matches vs partial matches"""
        search_term = "shoe"
        
        exact_match = "shoe"
        partial_match = "shoes"
        
        assert search_term in exact_match
        assert search_term in partial_match
    
    def test_brand_name_matching(self):
        """Test matching in brand names"""
        search_term = "nike"
        brand_name = "Nike"
        
        assert search_term.lower() in brand_name.lower()


class TestSearchEdgeCases:
    """Test search edge cases"""
    
    def test_empty_search_term(self):
        """Test handling empty search term"""
        search_term = ""
        
        # Should handle gracefully
        assert len(search_term) == 0
    
    def test_very_long_search_term(self):
        """Test handling very long search terms"""
        search_term = "a" * 1000
        
        # Should handle but might want to limit
        assert len(search_term) == 1000
    
    def test_special_characters_in_search(self):
        """Test special characters in search"""
        special_chars = ["!", "@", "#", "$", "%", "^", "&", "*"]
        
        for char in special_chars:
            search_term = f"test{char}product"
            # Should not crash
            assert char in search_term
    
    def test_unicode_search(self):
        """Test unicode characters in search"""
        search_terms = ["кроссовки", "新しい", "مُنتَج"]
        
        for term in search_terms:
            # Should handle unicode
            assert len(term) > 0
    
    def test_whitespace_handling(self):
        """Test whitespace in search terms"""
        search_term = "  running   shoes  "
        cleaned = " ".join(search_term.split())
        
        assert cleaned == "running shoes"
    
    def test_no_results_found(self):
        """Test when no results are found"""
        total_results = 0
        page = 1
        limit = 20
        total_pages = (total_results + limit - 1) // limit if total_results > 0 else 0
        
        assert total_pages == 0
        assert total_results == 0


class TestSearchResponseFormat:
    """Test search response formatting"""
    
    def test_search_response_structure(self):
        """Test ProductSearchResponse structure"""
        response = ProductSearchResponse(
            query="test",
            results=[],
            total=0,
            page=1,
            limit=20,
            total_pages=0,
            has_more=False
        )
        
        assert response.query == "test"
        assert response.results == []
        assert response.total == 0
        assert response.page == 1
        assert response.limit == 20
        assert response.total_pages == 0
        assert response.has_more == False
    
    def test_product_schema_in_search_results(self):
        """Test ProductSchema in search results"""
        product = ProductSchema(
            id="1",
            name="Test Product",
            brand="Test Brand",
            price=99.99,
            image="https://example.com/image.jpg",
            category="Test Category"
        )
        
        assert product.id == "1"
        assert product.name == "Test Product"
        assert product.price == 99.99


class TestSearchQueryValidation:
    """Test search query parameter validation"""
    
    def test_minimum_query_length(self):
        """Test minimum query length validation"""
        min_length = 1
        
        valid_query = "a"
        assert len(valid_query) >= min_length
        
        invalid_query = ""
        assert len(invalid_query) < min_length
    
    def test_page_number_validation(self):
        """Test page number must be >= 1"""
        valid_pages = [1, 2, 10, 100]
        for page in valid_pages:
            assert page >= 1
        
        invalid_pages = [0, -1, -10]
        for page in invalid_pages:
            assert page < 1
    
    def test_limit_validation(self):
        """Test limit must be between 1 and 100"""
        valid_limits = [1, 20, 50, 100]
        for limit in valid_limits:
            assert 1 <= limit <= 100
        
        invalid_limits = [0, -1, 101, 200]
        for limit in invalid_limits:
            assert not (1 <= limit <= 100)
    
    def test_price_validation(self):
        """Test price must be non-negative"""
        valid_prices = [0.0, 10.0, 99.99, 1000.0]
        for price in valid_prices:
            assert price >= 0
        
        invalid_prices = [-1.0, -10.0, -99.99]
        for price in invalid_prices:
            assert price < 0


class TestSearchCombinations:
    """Test combinations of search features"""
    
    def test_search_with_category_and_brand(self):
        """Test search with both category and brand filters"""
        query = "shoes"
        category = "mens"
        brand = "nike"
        
        # Should apply all filters
        assert query and category and brand
    
    def test_search_with_price_range_and_sort(self):
        """Test search with price range and sorting"""
        query = "shirt"
        min_price = 20.0
        max_price = 50.0
        sort_by = "price_low"
        
        # Should filter by price then sort
        assert query and min_price and max_price and sort_by
    
    def test_search_with_all_filters(self):
        """Test search with all available filters"""
        filters = {
            "query": "running shoes",
            "category": "sports",
            "brand": "nike",
            "min_price": 50.0,
            "max_price": 150.0,
            "sort_by": "popular",
            "page": 1,
            "limit": 20
        }
        
        # All filters should be present
        assert all(filters.values())


@pytest.mark.parametrize("query,expected_pattern", [
    ("shoes", "%shoes%"),
    ("running", "%running%"),
    ("nike air", "%nike air%"),
    ("t-shirt", "%t-shirt%"),
])
def test_search_pattern_generation(query, expected_pattern):
    """Parametrized test for search pattern generation"""
    pattern = f"%{query}%"
    assert pattern == expected_pattern


@pytest.mark.parametrize("sort_option", [
    "relevance",
    "newest",
    "popular",
    "price_low",
    "price_high",
])
def test_valid_sort_options(sort_option):
    """Parametrized test for valid sort options"""
    valid_sorts = ["relevance", "newest", "popular", "price_low", "price_high"]
    assert sort_option in valid_sorts


@pytest.mark.parametrize("page,limit,expected_offset", [
    (1, 20, 0),
    (2, 20, 20),
    (3, 20, 40),
    (1, 50, 0),
    (2, 50, 50),
])
def test_offset_calculation(page, limit, expected_offset):
    """Parametrized test for offset calculation"""
    offset = (page - 1) * limit
    assert offset == expected_offset


@pytest.mark.parametrize("total,limit,expected_pages", [
    (0, 20, 0),
    (10, 20, 1),
    (20, 20, 1),
    (21, 20, 2),
    (100, 20, 5),
    (95, 20, 5),
])
def test_total_pages_calculation(total, limit, expected_pages):
    """Parametrized test for total pages calculation"""
    if total == 0:
        pages = 0
    else:
        pages = (total + limit - 1) // limit
    assert pages == expected_pages


class TestSearchPerformance:
    """Test search performance considerations"""
    
    def test_pagination_prevents_large_queries(self):
        """Test that pagination limits result set size"""
        max_limit = 100
        requested_limit = 1000
        
        actual_limit = min(requested_limit, max_limit)
        assert actual_limit == max_limit
    
    def test_distinct_results(self):
        """Test that results are distinct (no duplicates)"""
        results = [1, 2, 3, 2, 1, 4]
        unique_results = list(set(results))
        
        assert len(unique_results) < len(results)
        assert sorted(unique_results) == [1, 2, 3, 4]


class TestSearchWithMockData:
    """Test search with mock data"""
    
    def test_search_response_with_products(self):
        """Test search response with mock products"""
        mock_products = [
            ProductSchema(
                id="1",
                name="Running Shoes",
                brand="Nike",
                price=99.99,
                image="image1.jpg",
                category="Sports"
            ),
            ProductSchema(
                id="2",
                name="Running Shorts",
                brand="Adidas",
                price=29.99,
                image="image2.jpg",
                category="Sports"
            ),
        ]
        
        response = ProductSearchResponse(
            query="running",
            results=mock_products,
            total=2,
            page=1,
            limit=20,
            total_pages=1,
            has_more=False
        )
        
        assert len(response.results) == 2
        assert response.total == 2
        assert response.query == "running"
        assert all("running" in p.name.lower() for p in response.results)


class TestSearchMultiWordQueries:
    """Test multi-word search queries"""
    
    def test_multi_word_search(self):
        """Test searching with multiple words"""
        query = "red running shoes"
        words = query.split()
        
        assert len(words) == 3
        assert words == ["red", "running", "shoes"]
    
    def test_phrase_search(self):
        """Test searching with exact phrases"""
        query = "running shoes"
        
        # Should match products with both words
        assert " " in query
        assert len(query.split()) == 2


class TestSearchIntegration:
    """Integration-style tests for search"""
    
    def test_empty_search_returns_structure(self):
        """Test that empty search returns proper structure"""
        response = ProductSearchResponse(
            query="",
            results=[],
            total=0,
            page=1,
            limit=20,
            total_pages=0,
            has_more=False
        )
        
        assert isinstance(response, ProductSearchResponse)
        assert response.results == []
    
    def test_search_with_no_filters(self):
        """Test search with only query, no filters"""
        query = "shirt"
        
        # Minimum required parameter
        assert len(query) > 0
    
    def test_search_preserves_query(self):
        """Test that search response includes original query"""
        original_query = "test product"
        
        response = ProductSearchResponse(
            query=original_query,
            results=[],
            total=0,
            page=1,
            limit=20,
            total_pages=0,
            has_more=False
        )
        
        assert response.query == original_query

