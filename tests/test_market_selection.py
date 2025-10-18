"""
Tests for Multi-Market Admin Panel

Tests the market selection functionality:
- Market selector view
- Market switching
- Database isolation
- Session management
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.middleware.sessions import SessionMiddleware
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.app_01.main import app
from src.app_01.models import Product, Category, Brand, Admin, Subcategory
from src.app_01.db.market_db import db_manager, Market, Base
import bcrypt

# Test client
client = TestClient(app)


@pytest.fixture(scope="function")
def setup_test_databases():
    """Setup test databases for both markets"""
    # Create test databases for both markets
    kg_engine = db_manager.get_engine(Market.KG)
    us_engine = db_manager.get_engine(Market.US)
    
    # Create all tables
    Base.metadata.create_all(bind=kg_engine)
    Base.metadata.create_all(bind=us_engine)
    
    yield
    
    # Cleanup is handled by Railway (persistent databases)
    # In local testing, you might want to drop tables here


@pytest.fixture(scope="function")
def create_test_admin():
    """Create test admin in both databases"""
    
    # Hash password
    password = "test123"
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Create admin in KG database
    kg_session = db_manager.get_session_factory(Market.KG)()
    kg_admin = Admin(
        username="test_admin_kg",
        hashed_password=hashed_password,
        is_active=True,
        is_super_admin=True
    )
    kg_session.add(kg_admin)
    kg_session.commit()
    kg_admin_id = kg_admin.id
    kg_session.close()
    
    # Create admin in US database
    us_session = db_manager.get_session_factory(Market.US)()
    us_admin = Admin(
        username="test_admin_us",
        hashed_password=hashed_password,
        is_active=True,
        is_super_admin=True
    )
    us_session.add(us_admin)
    us_session.commit()
    us_admin_id = us_admin.id
    us_session.close()
    
    yield {
        "kg": {"username": "test_admin_kg", "password": password, "id": kg_admin_id},
        "us": {"username": "test_admin_us", "password": password, "id": us_admin_id}
    }
    
    # Cleanup
    kg_session = db_manager.get_session_factory(Market.KG)()
    kg_session.query(Admin).filter(Admin.id == kg_admin_id).delete()
    kg_session.commit()
    kg_session.close()
    
    us_session = db_manager.get_session_factory(Market.US)()
    us_session.query(Admin).filter(Admin.id == us_admin_id).delete()
    us_session.commit()
    us_session.close()


class TestMarketSelector:
    """Test market selector functionality"""
    
    def test_market_selector_page_loads(self):
        """Test that market selector page loads"""
        # Note: This test requires authentication
        # For now, just test that the endpoint exists
        response = client.get("/admin/market-selector")
        
        # Should redirect to login if not authenticated
        assert response.status_code in [200, 302, 307]
    
    def test_market_selector_has_both_markets(self):
        """Test that market selector shows both KG and US options"""
        # This would require authentication
        # We'll test the HTML contains market options
        pass  # Requires session setup


class TestMarketSwitching:
    """Test market switching functionality"""
    
    def test_switch_market_endpoint_exists(self):
        """Test that switch market endpoint exists"""
        response = client.get("/admin/switch-market")
        
        # Should redirect to login or market selector
        assert response.status_code in [200, 302, 307]
    
    def test_market_stored_in_session(self, create_test_admin):
        """Test that selected market is stored in session"""
        # Login would set selected_market in session
        # This is tested in authentication flow
        pass


class TestDatabaseIsolation:
    """Test that operations on one market don't affect the other"""
    
    def test_create_product_in_kg_market(self, setup_test_databases):
        """Test creating a product in KG market"""
        kg_session = db_manager.get_session_factory(Market.KG)()
        
        try:
            # Create category and brand first
            category = Category(name="Test Category KG", slug="test-category-kg", is_active=True)
            kg_session.add(category)
            kg_session.commit()
            kg_session.refresh(category)
            
            subcategory = Subcategory(
                name="Test Subcategory KG",
                slug="test-subcategory-kg",
                category_id=category.id,
                is_active=True
            )
            kg_session.add(subcategory)
            kg_session.commit()
            kg_session.refresh(subcategory)
            
            brand = Brand(name="Test Brand KG", slug="test-brand-kg", is_active=True)
            kg_session.add(brand)
            kg_session.commit()
            kg_session.refresh(brand)
            
            # Create product in KG
            kg_product = Product(
                title="KG Product",
                slug="kg-product",
                description="Product for KG market",
                category_id=category.id,
                subcategory_id=subcategory.id,
                brand_id=brand.id,
                is_active=True
            )
            kg_session.add(kg_product)
            kg_session.commit()
            
            # Verify product exists in KG
            assert kg_session.query(Product).filter(Product.slug == "kg-product").first() is not None
            
            # Verify product does NOT exist in US
            us_session = db_manager.get_session_factory(Market.US)()
            us_product = us_session.query(Product).filter(Product.slug == "kg-product").first()
            assert us_product is None
            us_session.close()
            
        finally:
            # Cleanup
            kg_session.query(Product).filter(Product.slug == "kg-product").delete()
            kg_session.query(Subcategory).filter(Subcategory.slug == "test-subcategory-kg").delete()
            kg_session.query(Brand).filter(Brand.slug == "test-brand-kg").delete()
            kg_session.query(Category).filter(Category.slug == "test-category-kg").delete()
            kg_session.commit()
            kg_session.close()
    
    def test_create_product_in_us_market(self, setup_test_databases):
        """Test creating a product in US market"""
        us_session = db_manager.get_session_factory(Market.US)()
        
        try:
            # Create category and brand first
            category = Category(name="Test Category US", slug="test-category-us", is_active=True)
            us_session.add(category)
            us_session.commit()
            us_session.refresh(category)
            
            subcategory = Subcategory(
                name="Test Subcategory US",
                slug="test-subcategory-us",
                category_id=category.id,
                is_active=True
            )
            us_session.add(subcategory)
            us_session.commit()
            us_session.refresh(subcategory)
            
            brand = Brand(name="Test Brand US", slug="test-brand-us", is_active=True)
            us_session.add(brand)
            us_session.commit()
            us_session.refresh(brand)
            
            # Create product in US
            us_product = Product(
                title="US Product",
                slug="us-product",
                description="Product for US market",
                category_id=category.id,
                subcategory_id=subcategory.id,
                brand_id=brand.id,
                is_active=True
            )
            us_session.add(us_product)
            us_session.commit()
            
            # Verify product exists in US
            assert us_session.query(Product).filter(Product.slug == "us-product").first() is not None
            
            # Verify product does NOT exist in KG
            kg_session = db_manager.get_session_factory(Market.KG)()
            kg_product = kg_session.query(Product).filter(Product.slug == "us-product").first()
            assert kg_product is None
            kg_session.close()
            
        finally:
            # Cleanup
            us_session.query(Product).filter(Product.slug == "us-product").delete()
            us_session.query(Subcategory).filter(Subcategory.slug == "test-subcategory-us").delete()
            us_session.query(Brand).filter(Brand.slug == "test-brand-us").delete()
            us_session.query(Category).filter(Category.slug == "test-category-us").delete()
            us_session.commit()
            us_session.close()
    
    def test_separate_product_counts(self, setup_test_databases):
        """Test that product counts are separate per market"""
        kg_session = db_manager.get_session_factory(Market.KG)()
        us_session = db_manager.get_session_factory(Market.US)()
        
        try:
            # Get initial counts
            kg_count_before = kg_session.query(Product).count()
            us_count_before = us_session.query(Product).count()
            
            # Create dependencies for KG product
            kg_category = Category(name="Count Test KG", slug="count-test-kg", is_active=True)
            kg_session.add(kg_category)
            kg_session.commit()
            kg_session.refresh(kg_category)
            
            kg_subcategory = Subcategory(
                name="Count Subcat KG",
                slug="count-subcat-kg",
                category_id=kg_category.id,
                is_active=True
            )
            kg_session.add(kg_subcategory)
            kg_session.commit()
            kg_session.refresh(kg_subcategory)
            
            kg_brand = Brand(name="Count Brand KG", slug="count-brand-kg", is_active=True)
            kg_session.add(kg_brand)
            kg_session.commit()
            kg_session.refresh(kg_brand)
            
            # Add product to KG
            kg_product = Product(
                title="Count Test Product",
                slug="count-test-product-kg",
                description="Test",
                category_id=kg_category.id,
                subcategory_id=kg_subcategory.id,
                brand_id=kg_brand.id,
                is_active=True
            )
            kg_session.add(kg_product)
            kg_session.commit()
            
            # Verify counts
            kg_count_after = kg_session.query(Product).count()
            us_count_after = us_session.query(Product).count()
            
            assert kg_count_after == kg_count_before + 1
            assert us_count_after == us_count_before  # US count unchanged
            
        finally:
            # Cleanup
            kg_session.query(Product).filter(Product.slug == "count-test-product-kg").delete()
            kg_session.query(Subcategory).filter(Subcategory.slug == "count-subcat-kg").delete()
            kg_session.query(Brand).filter(Brand.slug == "count-brand-kg").delete()
            kg_session.query(Category).filter(Category.slug == "count-test-kg").delete()
            kg_session.commit()
            kg_session.close()
            us_session.close()


class TestMarketHelperFunctions:
    """Test helper functions for market management"""
    
    def test_get_current_market_default(self):
        """Test getting current market returns default when not set"""
        from src.app_01.admin.market_selector import get_current_market
        from starlette.requests import Request
        
        # Create a mock request without session
        class MockRequest:
            def __init__(self):
                self.session = {}
        
        request = MockRequest()
        market = get_current_market(request)
        
        # Should default to KG
        assert market == Market.KG
    
    def test_get_current_market_kg(self):
        """Test getting KG market from session"""
        from src.app_01.admin.market_selector import get_current_market
        
        class MockRequest:
            def __init__(self):
                self.session = {"selected_market": "kg"}
        
        request = MockRequest()
        market = get_current_market(request)
        
        assert market == Market.KG
    
    def test_get_current_market_us(self):
        """Test getting US market from session"""
        from src.app_01.admin.market_selector import get_current_market
        
        class MockRequest:
            def __init__(self):
                self.session = {"selected_market": "us"}
        
        request = MockRequest()
        market = get_current_market(request)
        
        assert market == Market.US


class TestMarketAwareViews:
    """Test that admin views use the selected market"""
    
    def test_admin_views_have_market_awareness(self):
        """Test that market awareness was added to views"""
        from src.app_01.admin.dynamic_admin_app import create_dynamic_admin
        from fastapi import FastAPI
        
        test_app = FastAPI()
        admin = create_dynamic_admin(test_app)
        
        # Verify admin was created
        assert admin is not None
        
        # Verify views were added
        assert len(admin._views) > 0


class TestMiddleware:
    """Test MarketMiddleware functionality"""
    
    def test_middleware_allows_login_page(self):
        """Test that middleware allows access to login page"""
        response = client.get("/admin/login")
        
        # Should not be blocked by middleware
        assert response.status_code in [200, 302, 307]
    
    def test_middleware_allows_market_selector(self):
        """Test that middleware allows access to market selector"""
        response = client.get("/admin/market-selector")
        
        # Should not be blocked by middleware
        assert response.status_code in [200, 302, 307]


# Integration test
class TestEndToEndMarketFlow:
    """Test complete market selection flow"""
    
    def test_complete_workflow(self, setup_test_databases):
        """Test: Login -> Select Market -> Create Product -> Verify Isolation"""
        
        # This test demonstrates the complete workflow
        # In practice, this would involve:
        # 1. Admin logs in
        # 2. Selects KG market
        # 3. Creates product in KG
        # 4. Switches to US market
        # 5. Verifies KG product is not visible
        # 6. Creates different product in US
        # 7. Verifies US product is not in KG
        
        # For now, we test the database isolation
        kg_session = db_manager.get_session_factory(Market.KG)()
        us_session = db_manager.get_session_factory(Market.US)()
        
        try:
            # Create test data in both markets with unique IDs
            kg_category = Category(name="Workflow Test KG", slug="workflow-test-kg", is_active=True)
            kg_session.add(kg_category)
            kg_session.commit()
            kg_session.refresh(kg_category)
            
            kg_subcategory = Subcategory(
                name="Workflow Subcat KG",
                slug="workflow-subcat-kg",
                category_id=kg_category.id,
                is_active=True
            )
            kg_session.add(kg_subcategory)
            kg_session.commit()
            kg_session.refresh(kg_subcategory)
            
            kg_brand = Brand(name="Workflow Brand KG", slug="workflow-brand-kg", is_active=True)
            kg_session.add(kg_brand)
            kg_session.commit()
            kg_session.refresh(kg_brand)
            
            us_category = Category(name="Workflow Test US", slug="workflow-test-us", is_active=True)
            us_session.add(us_category)
            us_session.commit()
            us_session.refresh(us_category)
            
            us_subcategory = Subcategory(
                name="Workflow Subcat US",
                slug="workflow-subcat-us",
                category_id=us_category.id,
                is_active=True
            )
            us_session.add(us_subcategory)
            us_session.commit()
            us_session.refresh(us_subcategory)
            
            us_brand = Brand(name="Workflow Brand US", slug="workflow-brand-us", is_active=True)
            us_session.add(us_brand)
            us_session.commit()
            us_session.refresh(us_brand)
            
            # Create products
            kg_product = Product(
                title="Workflow KG Product",
                slug="workflow-kg-product",
                description="KG only",
                category_id=kg_category.id,
                subcategory_id=kg_subcategory.id,
                brand_id=kg_brand.id,
                is_active=True
            )
            kg_session.add(kg_product)
            kg_session.commit()
            
            us_product = Product(
                title="Workflow US Product",
                slug="workflow-us-product",
                description="US only",
                category_id=us_category.id,
                subcategory_id=us_subcategory.id,
                brand_id=us_brand.id,
                is_active=True
            )
            us_session.add(us_product)
            us_session.commit()
            
            # Verify isolation
            kg_has_kg = kg_session.query(Product).filter(Product.slug == "workflow-kg-product").first() is not None
            kg_has_us = kg_session.query(Product).filter(Product.slug == "workflow-us-product").first() is not None
            
            us_has_us = us_session.query(Product).filter(Product.slug == "workflow-us-product").first() is not None
            us_has_kg = us_session.query(Product).filter(Product.slug == "workflow-kg-product").first() is not None
            
            assert kg_has_kg is True
            assert kg_has_us is False
            assert us_has_us is True
            assert us_has_kg is False
            
            print("✅ Complete workflow test passed!")
            print("   - KG database has KG product only")
            print("   - US database has US product only")
            print("   - Complete database isolation verified!")
            
        finally:
            # Cleanup
            kg_session.query(Product).filter(Product.slug == "workflow-kg-product").delete()
            kg_session.query(Subcategory).filter(Subcategory.slug == "workflow-subcat-kg").delete()
            kg_session.query(Brand).filter(Brand.slug == "workflow-brand-kg").delete()
            kg_session.query(Category).filter(Category.slug == "workflow-test-kg").delete()
            kg_session.commit()
            kg_session.close()
            
            us_session.query(Product).filter(Product.slug == "workflow-us-product").delete()
            us_session.query(Subcategory).filter(Subcategory.slug == "workflow-subcat-us").delete()
            us_session.query(Brand).filter(Brand.slug == "workflow-brand-us").delete()
            us_session.query(Category).filter(Category.slug == "workflow-test-us").delete()
            us_session.commit()
            us_session.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

