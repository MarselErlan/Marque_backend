"""
Integration Tests for Multi-Market Admin System

This module tests the complete integration of the multi-market admin system
including database operations, session management, and admin panel functionality.
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import tempfile
import os
from unittest.mock import patch, Mock
import bcrypt

# Import the FastAPI app and dependencies
from src.app_01.main import app
from src.app_01.admin.admin_app import create_sqladmin_app
from src.app_01.db.market_db import Base, Market, db_manager
from src.app_01.models import Admin, Product, SKU, Category, Brand, Subcategory


class TestMultiMarketAdminIntegration:
    """Integration tests for the complete multi-market admin system"""
    
    @pytest.fixture(scope="class")
    def test_databases(self):
        """Create temporary test databases for both markets"""
        # Create temporary SQLite databases for testing
        kg_db_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        us_db_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        
        kg_engine = create_engine(
            f"sqlite:///{kg_db_file.name}",
            poolclass=StaticPool,
            connect_args={"check_same_thread": False}
        )
        
        us_engine = create_engine(
            f"sqlite:///{us_db_file.name}",
            poolclass=StaticPool,
            connect_args={"check_same_thread": False}
        )
        
        # Create tables
        Base.metadata.create_all(bind=kg_engine)
        Base.metadata.create_all(bind=us_engine)
        
        # Create session factories
        KGSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=kg_engine)
        USSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=us_engine)
        
        yield {
            "kg": {"engine": kg_engine, "session": KGSessionLocal},
            "us": {"engine": us_engine, "session": USSessionLocal}
        }
        
        # Cleanup
        kg_db_file.close()
        us_db_file.close()
        os.unlink(kg_db_file.name)
        os.unlink(us_db_file.name)
    
    @pytest.fixture
    def setup_test_data(self, test_databases):
        """Set up test data in both databases"""
        # Create test admins
        kg_session = test_databases["kg"]["session"]()
        us_session = test_databases["us"]["session"]()
        
        try:
            # KG Admin - check if exists first
            kg_admin = kg_session.query(Admin).filter_by(username="kg_admin").first()
            if not kg_admin:
                kg_admin = Admin(
                    username="kg_admin",
                    email="kg@test.com",
                    hashed_password=bcrypt.hashpw("kgpass123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                    is_active=True,
                    is_super_admin=True
                )
                kg_session.add(kg_admin)
            
            # US Admin - check if exists first
            us_admin = us_session.query(Admin).filter_by(username="us_admin").first()
            if not us_admin:
                us_admin = Admin(
                    username="us_admin",
                    email="us@test.com",
                    hashed_password=bcrypt.hashpw("uspass123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                    is_active=True,
                    is_super_admin=True
                )
                us_session.add(us_admin)
            
            # Create test categories and brands for both markets
            for session, market in [(kg_session, "KG"), (us_session, "US")]:
                # Category - check if exists first
                category = session.query(Category).filter_by(slug=f"{market.lower()}-category").first()
                if not category:
                    category = Category(
                        name=f"{market} Category",
                        slug=f"{market.lower()}-category",
                        is_active=True,
                        is_featured=False
                    )
                    session.add(category)
                    session.flush()  # Get the ID
                
                # Subcategory - check if exists first
                subcategory = session.query(Subcategory).filter_by(slug=f"{market.lower()}-subcategory").first()
                if not subcategory:
                    subcategory = Subcategory(
                        name=f"{market} Subcategory",
                        slug=f"{market.lower()}-subcategory",
                        category_id=category.id,
                        is_active=True,
                        is_featured=False
                    )
                    session.add(subcategory)
                    session.flush()
                
                # Brand - check if exists first
                brand = session.query(Brand).filter_by(slug=f"{market.lower()}-brand").first()
                if not brand:
                    brand = Brand(
                        name=f"{market} Brand",
                        slug=f"{market.lower()}-brand",
                        is_active=True,
                        is_featured=False
                    )
                    session.add(brand)
                    session.flush()
                
                # Product - check if exists first
                product = session.query(Product).filter_by(slug=f"{market.lower()}-test-product").first()
                if not product:
                    product = Product(
                        title=f"{market} Test Product",
                        slug=f"{market.lower()}-test-product",
                        description=f"Test product for {market} market",
                        category_id=category.id,
                        subcategory_id=subcategory.id,
                        brand_id=brand.id,
                        is_active=True,
                        is_featured=False,
                        is_new=True,
                        is_trending=False
                    )
                    session.add(product)
                    session.flush()
                
                # SKU - check if exists first
                sku = session.query(SKU).filter_by(sku_code=f"{market}-SKU-001").first()
                if not sku:
                    sku = SKU(
                        product_id=product.id,
                        sku_code=f"{market}-SKU-001",
                        size="M",
                        color="Blue",
                        price=100.0 if market == "US" else 7000.0,  # $100 or 7000 сом
                        stock=50,
                        is_active=True
                    )
                    session.add(sku)
            
            kg_session.commit()
            us_session.commit()
            
            yield {
                "kg_admin": kg_admin,
                "us_admin": us_admin
            }
            
        finally:
            kg_session.close()
            us_session.close()
    
    @pytest.fixture
    def mock_db_manager(self, test_databases):
        """Mock the db_manager to use test databases"""
        original_get_db_session = db_manager.get_db_session
        original_get_session_factory = db_manager.get_session_factory
        
        def mock_get_db_session(market):
            session_factory = test_databases[market.value]["session"]
            session = session_factory()
            try:
                yield session
            finally:
                session.close()
        
        def mock_get_session_factory(market):
            return test_databases[market.value]["session"]
        
        # Patch the methods
        with patch.object(db_manager, 'get_db_session', side_effect=mock_get_db_session), \
             patch.object(db_manager, 'get_session_factory', side_effect=mock_get_session_factory):
            yield db_manager
    
    def test_admin_login_kg_market(self, setup_test_data, mock_db_manager):
        """Test admin login with KG market selection"""
        # Create test client
        client = TestClient(app)
        
        # Test login form submission
        login_data = {
            "username": "kg_admin",
            "password": "kgpass123",
            "market": "kg"
        }
        
        # This would normally test the actual login endpoint
        # For now, we'll test the authentication backend directly
        from src.app_01.admin.multi_market_admin_views import MultiMarketAuthenticationBackend
        
        auth_backend = MultiMarketAuthenticationBackend(secret_key="test-key")
        
        # Create mock request
        from unittest.mock import Mock, AsyncMock
        mock_request = Mock()
        mock_request.session = {}
        mock_request.form = AsyncMock(return_value=login_data)
        
        # Test login
        import asyncio
        result = asyncio.run(auth_backend.login(mock_request))
        
        # Assertions
        assert result is True
        assert mock_request.session["admin_username"] == "kg_admin"
        assert mock_request.session["admin_market"] == "kg"
        assert mock_request.session["market_currency"] == "сом"
    
    def test_admin_login_us_market(self, setup_test_data, mock_db_manager):
        """Test admin login with US market selection"""
        from src.app_01.admin.multi_market_admin_views import MultiMarketAuthenticationBackend
        from unittest.mock import Mock, AsyncMock
        
        auth_backend = MultiMarketAuthenticationBackend(secret_key="test-key")
        
        # Test login form submission
        login_data = {
            "username": "us_admin",
            "password": "uspass123",
            "market": "us"
        }
        
        # Create mock request
        mock_request = Mock()
        mock_request.session = {}
        mock_request.form = AsyncMock(return_value=login_data)
        
        # Test login
        import asyncio
        result = asyncio.run(auth_backend.login(mock_request))
        
        # Assertions
        assert result is True
        assert mock_request.session["admin_username"] == "us_admin"
        assert mock_request.session["admin_market"] == "us"
        assert mock_request.session["market_currency"] == "$"
    
    def test_market_aware_product_operations(self, setup_test_data, mock_db_manager):
        """Test that product operations use the correct market database"""
        from src.app_01.admin.multi_market_admin_views import MarketAwareModelView
        from unittest.mock import Mock
        
        # Test KG market operations
        kg_request = Mock()
        kg_request.session = {"admin_market": "kg"}
        
        # Test get_db_session method directly
        kg_db = MarketAwareModelView.get_db_session(None, kg_request)
        
        # Query products from KG database
        kg_products = kg_db.query(Product).all()
        assert len(kg_products) == 1
        assert kg_products[0].title == "KG Test Product"
        
        # Test US market operations
        us_request = Mock()
        us_request.session = {"admin_market": "us"}
        
        us_db = MarketAwareModelView.get_db_session(None, us_request)
        
        # Query products from US database
        us_products = us_db.query(Product).all()
        assert len(us_products) == 1
        assert us_products[0].title == "US Test Product"
        
        # Verify data isolation
        assert kg_products[0].title != us_products[0].title
    
    def test_market_specific_pricing(self, setup_test_data, mock_db_manager):
        """Test that pricing is market-specific"""
        from src.app_01.admin.multi_market_admin_views import MarketAwareModelView
        from unittest.mock import Mock
        
        # Test get_db_session method directly
        
        # Get KG market SKU
        kg_request = Mock()
        kg_request.session = {"admin_market": "kg"}
        kg_db = MarketAwareModelView.get_db_session(None, kg_request)
        kg_sku = kg_db.query(SKU).first()
        
        # Get US market SKU
        us_request = Mock()
        us_request.session = {"admin_market": "us"}
        us_db = MarketAwareModelView.get_db_session(None, us_request)
        us_sku = us_db.query(SKU).first()
        
        # Verify different pricing
        assert kg_sku.price == 7000.0  # сом
        assert us_sku.price == 100.0   # $
        
        # Verify stock levels
        assert kg_sku.stock == 50
        assert us_sku.stock == 50
        
        # Verify different SKU codes
        assert kg_sku.sku_code == "KG-SKU-001"
        assert us_sku.sku_code == "US-SKU-001"
    
    def test_cross_market_data_isolation(self, setup_test_data, mock_db_manager):
        """Test that data is completely isolated between markets"""
        from src.app_01.admin.multi_market_admin_views import MarketAwareModelView
        from unittest.mock import Mock
        
        # Test get_db_session method directly
        
        # Get all data from KG market
        kg_request = Mock()
        kg_request.session = {"admin_market": "kg"}
        kg_db = MarketAwareModelView.get_db_session(None, kg_request)
        
        kg_admins = kg_db.query(Admin).all()
        kg_products = kg_db.query(Product).all()
        kg_categories = kg_db.query(Category).all()
        kg_brands = kg_db.query(Brand).all()
        
        # Get all data from US market
        us_request = Mock()
        us_request.session = {"admin_market": "us"}
        us_db = MarketAwareModelView.get_db_session(None, us_request)
        
        us_admins = us_db.query(Admin).all()
        us_products = us_db.query(Product).all()
        us_categories = us_db.query(Category).all()
        us_brands = us_db.query(Brand).all()
        
        # Verify data counts are the same (1 each)
        assert len(kg_admins) == len(us_admins) == 1
        assert len(kg_products) == len(us_products) == 1
        assert len(kg_categories) == len(us_categories) == 1
        assert len(kg_brands) == len(us_brands) == 1
        
        # Verify data is different
        assert kg_admins[0].username != us_admins[0].username
        assert kg_products[0].title != us_products[0].title
        assert kg_categories[0].name != us_categories[0].name
        assert kg_brands[0].name != us_brands[0].name
    
    def test_session_market_context(self, setup_test_data, mock_db_manager):
        """Test that session correctly maintains market context"""
        from src.app_01.admin.multi_market_admin_views import MultiMarketAuthenticationBackend
        from unittest.mock import Mock, AsyncMock
        
        auth_backend = MultiMarketAuthenticationBackend(secret_key="test-key")
        
        # Test KG session
        kg_request = Mock()
        kg_request.session = {}
        kg_request.form = AsyncMock(return_value={
            "username": "kg_admin",
            "password": "kgpass123",
            "market": "kg"
        })
        
        # Login to KG
        import asyncio
        kg_result = asyncio.run(auth_backend.login(kg_request))
        assert kg_result is True
        
        # Verify KG session data
        assert kg_request.session["admin_market"] == "kg"
        assert kg_request.session["market_currency"] == "сом"
        assert kg_request.session["market_country"] == "Kyrgyzstan"
        assert kg_request.session["market_language"] == "ru"
        
        # Test US session
        us_request = Mock()
        us_request.session = {}
        us_request.form = AsyncMock(return_value={
            "username": "us_admin",
            "password": "uspass123",
            "market": "us"
        })
        
        # Login to US
        us_result = asyncio.run(auth_backend.login(us_request))
        assert us_result is True
        
        # Verify US session data
        assert us_request.session["admin_market"] == "us"
        assert us_request.session["market_currency"] == "$"
        assert us_request.session["market_country"] == "United States"
        assert us_request.session["market_language"] == "en"
    
    def test_market_switching_workflow(self, setup_test_data, mock_db_manager):
        """Test complete market switching workflow"""
        from src.app_01.admin.multi_market_admin_views import MultiMarketAuthenticationBackend, MarketAwareModelView
        from unittest.mock import Mock, AsyncMock
        
        auth_backend = MultiMarketAuthenticationBackend(secret_key="test-key")
        # Test get_db_session method directly
        
        # Step 1: Login to KG market
        request = Mock()
        request.session = {}
        request.form = AsyncMock(return_value={
            "username": "kg_admin",
            "password": "kgpass123",
            "market": "kg"
        })
        
        import asyncio
        kg_login = asyncio.run(auth_backend.login(request))
        assert kg_login is True
        assert request.session["admin_market"] == "kg"
        
        # Verify KG data access
        kg_db = MarketAwareModelView.get_db_session(None, request)
        kg_product = kg_db.query(Product).first()
        assert kg_product.title == "KG Test Product"
        
        # Step 2: Logout
        logout_result = asyncio.run(auth_backend.logout(request))
        assert logout_result is True
        assert len(request.session) == 0
        
        # Step 3: Login to US market
        request.form = AsyncMock(return_value={
            "username": "us_admin",
            "password": "uspass123",
            "market": "us"
        })
        
        us_login = asyncio.run(auth_backend.login(request))
        assert us_login is True
        assert request.session["admin_market"] == "us"
        
        # Verify US data access
        us_db = MarketAwareModelView.get_db_session(None, request)
        us_product = us_db.query(Product).first()
        assert us_product.title == "US Test Product"
        
        # Verify complete isolation
        assert kg_product.title != us_product.title


class TestMarketSelectionUI:
    """Test the market selection user interface"""
    
    def test_market_selection_page_content(self):
        """Test that market selection page contains required elements"""
        from src.app_01.admin.multi_market_admin_views import MarketSelectionView
        from unittest.mock import Mock
        
        view = MarketSelectionView()
        request = Mock()
        
        import asyncio
        response = asyncio.run(view.index(request))
        
        html_content = response.body.decode()
        
        # Check for required form elements
        assert 'name="username"' in html_content
        assert 'name="password"' in html_content
        assert 'name="market"' in html_content
        
        # Check for market options
        assert 'value="kg"' in html_content
        assert 'value="us"' in html_content
        assert 'Kyrgyzstan (KG)' in html_content
        assert 'United States (US)' in html_content
        
        # Check for visual elements
        assert '🇰🇬' in html_content
        assert '🇺🇸' in html_content
        
        # Check for market information
        assert 'сом' in html_content
        assert '$' in html_content
        assert 'Russian' in html_content
        assert 'English' in html_content


class TestErrorScenarios:
    """Test error handling in multi-market scenarios"""
    
    def test_invalid_market_selection(self):
        """Test handling of invalid market selection"""
        from src.app_01.admin.multi_market_admin_views import MultiMarketAuthenticationBackend
        from unittest.mock import Mock, AsyncMock
        
        auth_backend = MultiMarketAuthenticationBackend(secret_key="test-key")
        
        request = Mock()
        request.session = {}
        request.form = AsyncMock(return_value={
            "username": "admin",
            "password": "pass",
            "market": "invalid"
        })
        
        import asyncio
        result = asyncio.run(auth_backend.login(request))
        
        assert result is False
        assert len(request.session) == 0
    
    def test_missing_market_selection(self):
        """Test handling of missing market selection"""
        from src.app_01.admin.multi_market_admin_views import MultiMarketAuthenticationBackend
        from unittest.mock import Mock, AsyncMock
        
        auth_backend = MultiMarketAuthenticationBackend(secret_key="test-key")
        
        request = Mock()
        request.session = {}
        request.form = AsyncMock(return_value={
            "username": "admin",
            "password": "pass",
            "market": ""
        })
        
        import asyncio
        result = asyncio.run(auth_backend.login(request))
        
        assert result is False
        assert len(request.session) == 0
    
    def test_authentication_with_invalid_session_market(self):
        """Test authentication with invalid session market"""
        from src.app_01.admin.multi_market_admin_views import MultiMarketAuthenticationBackend
        from unittest.mock import Mock
        
        auth_backend = MultiMarketAuthenticationBackend(secret_key="test-key")
        
        request = Mock()
        request.session = {
            "token": "test-token",
            "admin_id": 1,
            "admin_market": "invalid"
        }
        
        import asyncio
        result = asyncio.run(auth_backend.authenticate(request))
        
        # Should default to KG market and still work if admin exists
        # In this test case, it will fail because no database is set up
        assert result is False


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
