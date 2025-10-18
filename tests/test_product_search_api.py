"""
Unit tests for Product Search API

Tests all 9 endpoints for search analytics:
- Track searches
- Popular searches
- Trending searches
- Zero-result searches
- Search suggestions
- Search insights
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from src.app_01.main import app
from src.app_01.db import Base, get_db
# Import all models to ensure they're registered with Base
from src.app_01.models import (
    Product, ProductAsset, Category, Subcategory, Brand, SKU, Review,
    ProductAttribute, ProductFilter, ProductSeason, ProductMaterial,
    ProductStyle, ProductDiscount, ProductSearch
)

# Test database - SQLite for local testing (production uses PostgreSQL)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_product_search.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Create tables before each test, drop after"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_searches():
    """Create sample search records"""
    db = TestingSessionLocal()
    
    searches = [
        ProductSearch(search_term="winter jacket", search_count=50, result_count=15),
        ProductSearch(search_term="summer dress", search_count=30, result_count=20),
        ProductSearch(search_term="running shoes", search_count=40, result_count=25),
        ProductSearch(search_term="winter boots", search_count=25, result_count=0),  # Zero results
        ProductSearch(search_term="swim shorts", search_count=15, result_count=0),   # Zero results
    ]
    
    for search in searches:
        db.add(search)
    
    db.commit()
    db.close()
    
    return len(searches)


class TestSearchTracking:
    """Test search tracking endpoints"""
    
    def test_track_new_search(self):
        """Test tracking a new search term"""
        response = client.post(
            "/api/v1/search/track",
            json={"search_term": "blue jeans", "result_count": 10}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["search_term"] == "blue jeans"
        assert data["result_count"] == 10
        
        # Verify in database
        db = TestingSessionLocal()
        search = db.query(ProductSearch).filter(
            ProductSearch.search_term == "blue jeans"
        ).first()
        assert search is not None
        assert search.search_count == 1
        assert search.result_count == 10
        db.close()
    
    def test_track_existing_search(self):
        """Test tracking an existing search term increments count"""
        # Track first time
        client.post(
            "/api/v1/search/track",
            json={"search_term": "red shoes", "result_count": 5}
        )
        
        # Track second time
        response = client.post(
            "/api/v1/search/track",
            json={"search_term": "red shoes", "result_count": 6}
        )
        
        assert response.status_code == 200
        
        # Verify count incremented
        db = TestingSessionLocal()
        search = db.query(ProductSearch).filter(
            ProductSearch.search_term == "red shoes"
        ).first()
        assert search.search_count == 2
        assert search.result_count == 6  # Updated to latest
        db.close()
    
    def test_track_zero_result_search(self):
        """Test tracking a search with zero results"""
        response = client.post(
            "/api/v1/search/track",
            json={"search_term": "purple unicorn", "result_count": 0}
        )
        
        assert response.status_code == 200
        
        # Verify in database
        db = TestingSessionLocal()
        search = db.query(ProductSearch).filter(
            ProductSearch.search_term == "purple unicorn"
        ).first()
        assert search.result_count == 0
        db.close()


class TestPopularSearches:
    """Test popular searches endpoints"""
    
    def test_get_popular_searches(self, sample_searches):
        """Test getting most popular search terms"""
        response = client.get("/api/v1/search/popular?limit=3")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 3
        
        # Should be sorted by search_count descending
        if len(data) >= 2:
            assert data[0]["search_count"] >= data[1]["search_count"]
    
    def test_popular_searches_custom_limit(self, sample_searches):
        """Test popular searches with custom limit"""
        response = client.get("/api/v1/search/popular?limit=2")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2
    
    def test_popular_searches_empty_database(self):
        """Test popular searches with no data"""
        response = client.get("/api/v1/search/popular")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0


class TestRecentSearches:
    """Test recent searches endpoints"""
    
    def test_get_recent_searches(self, sample_searches):
        """Test getting most recent search terms"""
        response = client.get("/api/v1/search/recent?limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5
        
        # Should be sorted by last_searched descending
        if len(data) >= 2:
            date1 = datetime.fromisoformat(data[0]["last_searched"])
            date2 = datetime.fromisoformat(data[1]["last_searched"])
            assert date1 >= date2


class TestTrendingSearches:
    """Test trending searches endpoints"""
    
    def test_get_trending_searches(self, sample_searches):
        """Test getting trending searches"""
        response = client.get("/api/v1/search/trending?days=7&limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5
    
    def test_trending_searches_custom_period(self, sample_searches):
        """Test trending searches with custom time period"""
        response = client.get("/api/v1/search/trending?days=30&limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 10
    
    def test_trending_searches_filters_old_searches(self):
        """Test that trending only returns recent searches"""
        db = TestingSessionLocal()
        
        # Create an old search
        old_date = datetime.now() - timedelta(days=100)
        old_search = ProductSearch(
            search_term="very old search",
            search_count=100,
            last_searched=old_date
        )
        db.add(old_search)
        db.commit()
        db.close()
        
        # Get trending for last 7 days
        response = client.get("/api/v1/search/trending?days=7")
        
        assert response.status_code == 200
        data = response.json()
        
        # Old search should not be in results
        search_terms = [s["search_term"] for s in data]
        assert "very old search" not in search_terms


class TestZeroResultSearches:
    """Test zero-result searches endpoints"""
    
    def test_get_zero_result_searches(self, sample_searches):
        """Test getting searches that returned no results"""
        response = client.get("/api/v1/search/zero-results?limit=10")
        
        assert response.status_code == 200
        data = response.json()
        
        # All should have result_count = 0
        assert all(s["result_count"] == 0 for s in data)
        
        # Should contain our test zero-result searches
        search_terms = [s["search_term"] for s in data]
        assert "winter boots" in search_terms
        assert "swim shorts" in search_terms
    
    def test_zero_result_searches_sorted_by_popularity(self, sample_searches):
        """Test zero-result searches are sorted by search count"""
        response = client.get("/api/v1/search/zero-results")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should be sorted by search_count descending
        if len(data) >= 2:
            assert data[0]["search_count"] >= data[1]["search_count"]


class TestSearchStatistics:
    """Test search statistics endpoints"""
    
    def test_get_search_stats(self, sample_searches):
        """Test getting comprehensive search statistics"""
        response = client.get("/api/v1/search/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "total_searches" in data
        assert "unique_terms" in data
        assert "avg_results_per_search" in data
        assert "zero_result_searches" in data
        assert "most_popular_term" in data
        
        # Verify values
        assert data["unique_terms"] == sample_searches
        assert data["zero_result_searches"] == 2  # winter boots, swim shorts
        assert data["most_popular_term"] is not None
    
    def test_search_stats_empty_database(self):
        """Test search stats with no data"""
        response = client.get("/api/v1/search/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_searches"] == 0
        assert data["unique_terms"] == 0
        assert data["most_popular_term"] is None


class TestSearchSuggestions:
    """Test search suggestions endpoints"""
    
    def test_get_search_suggestions(self, sample_searches):
        """Test getting search suggestions"""
        response = client.get("/api/v1/search/suggestions?q=winter&limit=5")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "query" in data
        assert "suggestions" in data
        assert data["query"] == "winter"
        
        # Suggestions should contain "winter jacket" and "winter boots"
        suggested_terms = [s["term"] for s in data["suggestions"]]
        matching = [term for term in suggested_terms if "winter" in term.lower()]
        assert len(matching) > 0
    
    def test_suggestions_exclude_zero_results(self, sample_searches):
        """Test that suggestions only include successful searches"""
        response = client.get("/api/v1/search/suggestions?q=winter")
        
        assert response.status_code == 200
        data = response.json()
        
        # All suggestions should have result_count > 0
        assert all(s["result_count"] > 0 for s in data["suggestions"])
    
    def test_suggestions_case_insensitive(self, sample_searches):
        """Test that suggestions are case insensitive"""
        response = client.get("/api/v1/search/suggestions?q=WINTER")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should still find "winter" searches
        if data["suggestions"]:
            found = any("winter" in s["term"].lower() for s in data["suggestions"])
            assert found
    
    def test_suggestions_minimum_query_length(self):
        """Test that suggestions require minimum query length"""
        response = client.get("/api/v1/search/suggestions?q=w")
        
        # Should fail validation (min_length=2)
        assert response.status_code == 422


class TestSearchInsights:
    """Test search insights endpoints"""
    
    def test_get_search_insights(self, sample_searches):
        """Test getting actionable search insights"""
        response = client.get("/api/v1/search/insights")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required sections
        assert "popular_searches" in data
        assert "zero_result_searches" in data
        assert "trending_searches" in data
        assert "recommendations" in data
        
        # Verify recommendations are generated
        assert isinstance(data["recommendations"], list)
    
    def test_insights_recommendations_for_zero_results(self):
        """Test that insights recommend adding missing products"""
        db = TestingSessionLocal()
        
        # Add a popular zero-result search
        search = ProductSearch(
            search_term="popular missing item",
            search_count=100,
            result_count=0
        )
        db.add(search)
        db.commit()
        db.close()
        
        response = client.get("/api/v1/search/insights")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should recommend adding this product
        recommendations_text = " ".join(data["recommendations"])
        assert "popular missing item" in recommendations_text.lower()


class TestSearchAdminOperations:
    """Test admin search operations"""
    
    def test_clear_old_searches(self, sample_searches):
        """Test clearing old search records"""
        db = TestingSessionLocal()
        
        # Create an old search
        old_date = datetime.now() - timedelta(days=100)
        old_search = ProductSearch(
            search_term="very old search",
            search_count=5,
            last_searched=old_date
        )
        db.add(old_search)
        db.commit()
        initial_count = db.query(ProductSearch).count()
        db.close()
        
        # Clear searches older than 90 days
        response = client.delete("/api/v1/search/admin/clear-old-searches?days=90")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["deleted_count"] > 0
        
        # Verify old search was deleted
        db = TestingSessionLocal()
        remaining_count = db.query(ProductSearch).count()
        assert remaining_count < initial_count
        
        old_search_check = db.query(ProductSearch).filter(
            ProductSearch.search_term == "very old search"
        ).first()
        assert old_search_check is None
        db.close()
    
    def test_clear_old_searches_minimum_days(self):
        """Test that minimum days constraint is enforced"""
        response = client.delete("/api/v1/search/admin/clear-old-searches?days=20")
        
        # Should fail validation (ge=30)
        assert response.status_code == 422


class TestSearchRecordMethod:
    """Test ProductSearch.record_search method"""
    
    def test_record_search_creates_new(self):
        """Test that record_search creates new search record"""
        db = TestingSessionLocal()
        
        ProductSearch.record_search(db, "new search term", 10)
        
        search = db.query(ProductSearch).filter(
            ProductSearch.search_term == "new search term"
        ).first()
        
        assert search is not None
        assert search.search_count == 1
        assert search.result_count == 10
        db.close()
    
    def test_record_search_increments_existing(self):
        """Test that record_search increments existing search"""
        db = TestingSessionLocal()
        
        # Record first time
        ProductSearch.record_search(db, "repeat search", 5)
        
        # Record second time
        ProductSearch.record_search(db, "repeat search", 7)
        
        search = db.query(ProductSearch).filter(
            ProductSearch.search_term == "repeat search"
        ).first()
        
        assert search.search_count == 2
        assert search.result_count == 7  # Updated to latest
        db.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

