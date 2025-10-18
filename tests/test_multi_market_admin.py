"""
Tests for Multi-Market Admin System

This module tests the multi-market authentication, market selection,
and market-aware admin operations.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from starlette.requests import Request
from starlette.responses import HTMLResponse
from sqlalchemy.orm import Session
import bcrypt
from datetime import datetime

# Import the classes we're testing
from src.app_01.admin.multi_market_admin_views import (
    MultiMarketAuthenticationBackend,
    MarketSelectionView,
    MarketAwareModelView,
    ProductAdmin,
    SKUAdmin,
    ReviewAdmin
)
from src.app_01.db.market_db import Market, MarketConfig, db_manager
from src.app_01.models import Admin, Product, SKU, Review


class TestMultiMarketAuthenticationBackend:
    """Test the multi-market authentication system"""
    
    @pytest.fixture
    def auth_backend(self):
        """Create authentication backend instance"""
        return MultiMarketAuthenticationBackend(secret_key="test-secret-key")
    
    @pytest.fixture
    def mock_request(self):
        """Create mock request with form data"""
        request = Mock(spec=Request)
        request.session = {}
        return request
    
    @pytest.fixture
    def mock_admin(self):
        """Create mock admin user"""
        admin = Mock(spec=Admin)
        admin.id = 1
        admin.username = "testadmin"
        admin.is_active = True
        admin.is_super_admin = False
        admin.hashed_password = bcrypt.hashpw("testpass".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        admin.last_login = None
        return admin
    
    @pytest.mark.asyncio
    async def test_login_success_kg_market(self, auth_backend, mock_request, mock_admin):
        """Test successful login with KG market selection"""
        # Mock form data
        form_data = {
            "username": "testadmin",
            "password": "testpass",
            "market": "kg"
        }
        mock_request.form = AsyncMock(return_value=form_data)
        
        # Mock database session and query
        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_admin
        mock_db.commit = Mock()
        mock_db.close = Mock()
        
        # Mock db_manager
        with patch('src.app_01.admin.multi_market_admin_views.db_manager') as mock_db_manager:
            mock_db_manager.get_db_session.return_value = iter([mock_db])
            
            # Test login
            result = await auth_backend.login(mock_request)
            
            # Assertions
            assert result is True
            assert mock_request.session["admin_id"] == 1
            assert mock_request.session["admin_username"] == "testadmin"
            assert mock_request.session["admin_market"] == "kg"
            assert mock_request.session["market_currency"] == "сом"
            assert mock_request.session["market_country"] == "Kyrgyzstan"
            
            # Verify database calls
            mock_db_manager.get_db_session.assert_called_once_with(Market.KG)
            mock_db.query.assert_called_once_with(Admin)
            mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_login_success_us_market(self, auth_backend, mock_request, mock_admin):
        """Test successful login with US market selection"""
        # Mock form data
        form_data = {
            "username": "testadmin",
            "password": "testpass",
            "market": "us"
        }
        mock_request.form = AsyncMock(return_value=form_data)
        
        # Mock database session and query
        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_admin
        mock_db.commit = Mock()
        mock_db.close = Mock()
        
        # Mock db_manager
        with patch('src.app_01.admin.multi_market_admin_views.db_manager') as mock_db_manager:
            mock_db_manager.get_db_session.return_value = iter([mock_db])
            
            # Test login
            result = await auth_backend.login(mock_request)
            
            # Assertions
            assert result is True
            assert mock_request.session["admin_market"] == "us"
            assert mock_request.session["market_currency"] == "$"
            assert mock_request.session["market_country"] == "United States"
            
            # Verify database calls
            mock_db_manager.get_db_session.assert_called_once_with(Market.US)
    
    @pytest.mark.asyncio
    async def test_login_missing_credentials(self, auth_backend, mock_request):
        """Test login failure with missing credentials"""
        # Mock form data with missing fields
        form_data = {
            "username": "",
            "password": "testpass",
            "market": "kg"
        }
        mock_request.form = AsyncMock(return_value=form_data)
        
        # Test login
        result = await auth_backend.login(mock_request)
        
        # Assertions
        assert result is False
        assert len(mock_request.session) == 0
    
    @pytest.mark.asyncio
    async def test_login_missing_market_selection(self, auth_backend, mock_request):
        """Test login failure with missing market selection"""
        # Mock form data with missing market
        form_data = {
            "username": "testadmin",
            "password": "testpass",
            "market": ""
        }
        mock_request.form = AsyncMock(return_value=form_data)
        
        # Test login
        result = await auth_backend.login(mock_request)
        
        # Assertions
        assert result is False
        assert len(mock_request.session) == 0
    
    @pytest.mark.asyncio
    async def test_login_invalid_market(self, auth_backend, mock_request):
        """Test login failure with invalid market selection"""
        # Mock form data with invalid market
        form_data = {
            "username": "testadmin",
            "password": "testpass",
            "market": "invalid"
        }
        mock_request.form = AsyncMock(return_value=form_data)
        
        # Test login
        result = await auth_backend.login(mock_request)
        
        # Assertions
        assert result is False
        assert len(mock_request.session) == 0
    
    @pytest.mark.asyncio
    async def test_login_admin_not_found(self, auth_backend, mock_request):
        """Test login failure when admin not found in selected market"""
        # Mock form data
        form_data = {
            "username": "nonexistent",
            "password": "testpass",
            "market": "kg"
        }
        mock_request.form = AsyncMock(return_value=form_data)
        
        # Mock database session with no admin found
        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_db.close = Mock()
        
        # Mock db_manager
        with patch('src.app_01.admin.multi_market_admin_views.db_manager') as mock_db_manager:
            mock_db_manager.get_db_session.return_value = iter([mock_db])
            
            # Test login
            result = await auth_backend.login(mock_request)
            
            # Assertions
            assert result is False
            assert len(mock_request.session) == 0
    
    @pytest.mark.asyncio
    async def test_login_inactive_admin(self, auth_backend, mock_request, mock_admin):
        """Test login failure with inactive admin"""
        # Make admin inactive
        mock_admin.is_active = False
        
        # Mock form data
        form_data = {
            "username": "testadmin",
            "password": "testpass",
            "market": "kg"
        }
        mock_request.form = AsyncMock(return_value=form_data)
        
        # Mock database session
        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_admin
        mock_db.close = Mock()
        
        # Mock db_manager
        with patch('src.app_01.admin.multi_market_admin_views.db_manager') as mock_db_manager:
            mock_db_manager.get_db_session.return_value = iter([mock_db])
            
            # Test login
            result = await auth_backend.login(mock_request)
            
            # Assertions
            assert result is False
            assert len(mock_request.session) == 0
    
    @pytest.mark.asyncio
    async def test_login_wrong_password(self, auth_backend, mock_request, mock_admin):
        """Test login failure with wrong password"""
        # Mock form data with wrong password
        form_data = {
            "username": "testadmin",
            "password": "wrongpass",
            "market": "kg"
        }
        mock_request.form = AsyncMock(return_value=form_data)
        
        # Mock database session
        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_admin
        mock_db.close = Mock()
        
        # Mock db_manager
        with patch('src.app_01.admin.multi_market_admin_views.db_manager') as mock_db_manager:
            mock_db_manager.get_db_session.return_value = iter([mock_db])
            
            # Test login
            result = await auth_backend.login(mock_request)
            
            # Assertions
            assert result is False
            assert len(mock_request.session) == 0
    
    @pytest.mark.asyncio
    async def test_logout(self, auth_backend, mock_request):
        """Test logout functionality"""
        # Set up session data
        mock_request.session = {
            "token": "test-token",
            "admin_id": 1,
            "admin_market": "kg"
        }
        
        # Test logout
        result = await auth_backend.logout(mock_request)
        
        # Assertions
        assert result is True
        assert len(mock_request.session) == 0
    
    @pytest.mark.asyncio
    async def test_authenticate_valid_session_kg(self, auth_backend, mock_request, mock_admin):
        """Test authentication with valid KG session"""
        # Set up session data
        mock_request.session = {
            "token": "test-token",
            "admin_id": 1,
            "admin_market": "kg"
        }
        
        # Mock database session
        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_admin
        mock_db.close = Mock()
        
        # Mock db_manager
        with patch('src.app_01.admin.multi_market_admin_views.db_manager') as mock_db_manager:
            mock_db_manager.get_db_session.return_value = iter([mock_db])
            
            # Test authentication
            result = await auth_backend.authenticate(mock_request)
            
            # Assertions
            assert result is True
            mock_db_manager.get_db_session.assert_called_once_with(Market.KG)
    
    @pytest.mark.asyncio
    async def test_authenticate_valid_session_us(self, auth_backend, mock_request, mock_admin):
        """Test authentication with valid US session"""
        # Set up session data
        mock_request.session = {
            "token": "test-token",
            "admin_id": 1,
            "admin_market": "us"
        }
        
        # Mock database session
        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_admin
        mock_db.close = Mock()
        
        # Mock db_manager
        with patch('src.app_01.admin.multi_market_admin_views.db_manager') as mock_db_manager:
            mock_db_manager.get_db_session.return_value = iter([mock_db])
            
            # Test authentication
            result = await auth_backend.authenticate(mock_request)
            
            # Assertions
            assert result is True
            mock_db_manager.get_db_session.assert_called_once_with(Market.US)
    
    @pytest.mark.asyncio
    async def test_authenticate_no_session(self, auth_backend, mock_request):
        """Test authentication with no session data"""
        # Empty session
        mock_request.session = {}
        
        # Test authentication
        result = await auth_backend.authenticate(mock_request)
        
        # Assertions
        assert result is False
    
    @pytest.mark.asyncio
    async def test_authenticate_admin_not_found(self, auth_backend, mock_request):
        """Test authentication when admin not found in database"""
        # Set up session data
        mock_request.session = {
            "token": "test-token",
            "admin_id": 999,
            "admin_market": "kg"
        }
        
        # Mock database session with no admin found
        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_db.close = Mock()
        
        # Mock db_manager
        with patch('src.app_01.admin.multi_market_admin_views.db_manager') as mock_db_manager:
            mock_db_manager.get_db_session.return_value = iter([mock_db])
            
            # Test authentication
            result = await auth_backend.authenticate(mock_request)
            
            # Assertions
            assert result is False


class TestMarketSelectionView:
    """Test the market selection view"""
    
    @pytest.fixture
    def market_view(self):
        """Create market selection view instance"""
        return MarketSelectionView()
    
    @pytest.fixture
    def mock_request(self):
        """Create mock request"""
        return Mock(spec=Request)
    
    @pytest.mark.asyncio
    async def test_index_returns_html_response(self, market_view, mock_request):
        """Test that index method returns HTML response"""
        # Test index method
        response = await market_view.index(mock_request)
        
        # Assertions
        assert isinstance(response, HTMLResponse)
        assert "Marque - Multi-Market Admin" in response.body.decode()
        assert "Select Market Database" in response.body.decode()
        assert "Kyrgyzstan (KG)" in response.body.decode()
        assert "United States (US)" in response.body.decode()
    
    @pytest.mark.asyncio
    async def test_login_form_elements(self, market_view, mock_request):
        """Test that login form contains all required elements"""
        # Test index method
        response = await market_view.index(mock_request)
        html_content = response.body.decode()
        
        # Check form elements
        assert 'name="username"' in html_content
        assert 'name="password"' in html_content
        assert 'name="market"' in html_content
        assert 'value="kg"' in html_content
        assert 'value="us"' in html_content
        assert 'action="/admin/login"' in html_content
        assert 'method="post"' in html_content
    
    @pytest.mark.asyncio
    async def test_market_flags_present(self, market_view, mock_request):
        """Test that market flags are present in the UI"""
        # Test index method
        response = await market_view.index(mock_request)
        html_content = response.body.decode()
        
        # Check for flag elements
        assert "🇰🇬" in html_content
        assert "🇺🇸" in html_content
        assert "flag-kg" in html_content
        assert "flag-us" in html_content


class TestMarketAwareModelView:
    """Test the market-aware model view base class"""
    
    @pytest.fixture
    def mock_request_kg(self):
        """Create mock request with KG market session data"""
        request = Mock(spec=Request)
        request.session = {"admin_market": "kg"}
        return request
    
    @pytest.fixture
    def mock_request_us(self):
        """Create mock request with US market session data"""
        request = Mock(spec=Request)
        request.session = {"admin_market": "us"}
        return request
    
    @pytest.fixture
    def mock_request_empty(self):
        """Create mock request with empty session"""
        request = Mock(spec=Request)
        request.session = {}
        return request
    
    def test_get_db_session_kg_market(self, mock_request_kg):
        """Test getting database session for KG market"""
        # Mock db_manager
        with patch('src.app_01.admin.multi_market_admin_views.db_manager') as mock_db_manager:
            mock_db = Mock(spec=Session)
            mock_db_manager.get_db_session.return_value = iter([mock_db])
            
            # Just test the method directly without full initialization
            result = MarketAwareModelView.get_db_session(None, mock_request_kg)
            
            # Assertions
            assert result == mock_db
            mock_db_manager.get_db_session.assert_called_once_with(Market.KG)
    
    def test_get_db_session_us_market(self, mock_request_us):
        """Test getting database session for US market"""
        # Mock db_manager
        with patch('src.app_01.admin.multi_market_admin_views.db_manager') as mock_db_manager:
            mock_db = Mock(spec=Session)
            mock_db_manager.get_db_session.return_value = iter([mock_db])
            
            # Test get_db_session using the method directly
            from src.app_01.admin.multi_market_admin_views import MarketAwareModelView
            result = MarketAwareModelView.get_db_session(None, mock_request_us)
            
            # Assertions
            assert result == mock_db
            mock_db_manager.get_db_session.assert_called_once_with(Market.US)
    
    def test_get_db_session_default_market(self, mock_request_empty):
        """Test getting database session with default market when not set"""
        # Mock db_manager
        with patch('src.app_01.admin.multi_market_admin_views.db_manager') as mock_db_manager:
            mock_db = Mock(spec=Session)
            mock_db_manager.get_db_session.return_value = iter([mock_db])
            
            # Test get_db_session using the method directly
            from src.app_01.admin.multi_market_admin_views import MarketAwareModelView
            result = MarketAwareModelView.get_db_session(None, mock_request_empty)
            
            # Assertions
            assert result == mock_db
            mock_db_manager.get_db_session.assert_called_once_with(Market.KG)


class TestMarketConfig:
    """Test market configuration functionality"""
    
    def test_kg_market_config(self):
        """Test KG market configuration"""
        config = MarketConfig.get_config(Market.KG)
        
        # Assertions
        assert config["currency"] == "сом"
        assert config["currency_code"] == "KGS"
        assert config["phone_prefix"] == "+996"
        assert config["language"] == "ru"
        assert config["country"] == "Kyrgyzstan"
        assert config["tax_rate"] == 0.12
    
    def test_us_market_config(self):
        """Test US market configuration"""
        config = MarketConfig.get_config(Market.US)
        
        # Assertions
        assert config["currency"] == "$"
        assert config["currency_code"] == "USD"
        assert config["phone_prefix"] == "+1"
        assert config["language"] == "en"
        assert config["country"] == "United States"
        assert config["tax_rate"] == 0.08


class TestIntegrationScenarios:
    """Integration tests for complete multi-market workflows"""
    
    @pytest.fixture
    def auth_backend(self):
        """Create authentication backend instance"""
        return MultiMarketAuthenticationBackend(secret_key="test-secret-key")
    
    @pytest.fixture
    def mock_request(self):
        """Create mock request"""
        request = Mock(spec=Request)
        request.session = {}
        return request
    
    @pytest.fixture
    def mock_admin_kg(self):
        """Create mock KG admin"""
        admin = Mock(spec=Admin)
        admin.id = 1
        admin.username = "kg_admin"
        admin.is_active = True
        admin.is_super_admin = False
        admin.hashed_password = bcrypt.hashpw("kgpass".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        return admin
    
    @pytest.fixture
    def mock_admin_us(self):
        """Create mock US admin"""
        admin = Mock(spec=Admin)
        admin.id = 2
        admin.username = "us_admin"
        admin.is_active = True
        admin.is_super_admin = False
        admin.hashed_password = bcrypt.hashpw("uspass".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        return admin
    
    @pytest.mark.asyncio
    async def test_complete_kg_workflow(self, auth_backend, mock_request, mock_admin_kg):
        """Test complete workflow for KG market"""
        # Step 1: Login to KG market
        form_data = {
            "username": "kg_admin",
            "password": "kgpass",
            "market": "kg"
        }
        mock_request.form = AsyncMock(return_value=form_data)
        
        # Mock database
        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_admin_kg
        mock_db.commit = Mock()
        mock_db.close = Mock()
        
        with patch('src.app_01.admin.multi_market_admin_views.db_manager') as mock_db_manager:
            # Use side_effect with a function to avoid StopIteration in async context
            def get_db_gen(market):
                yield mock_db
            mock_db_manager.get_db_session.side_effect = get_db_gen
            
            # Test login
            login_result = await auth_backend.login(mock_request)
            assert login_result is True
            assert mock_request.session["admin_market"] == "kg"
            assert mock_request.session["market_currency"] == "сом"
            
            # Step 2: Test authentication
            auth_result = await auth_backend.authenticate(mock_request)
            assert auth_result is True
            
            # Step 3: Test market-aware model view
            # Test the get_db_session method directly without initialization
            with patch('src.app_01.admin.multi_market_admin_views.db_manager') as mock_db_manager2:
                mock_db_manager2.get_db_session.return_value = iter([mock_db])
                db_session = MarketAwareModelView.get_db_session(None, mock_request)
                assert db_session == mock_db
    
    @pytest.mark.asyncio
    async def test_complete_us_workflow(self, auth_backend, mock_request, mock_admin_us):
        """Test complete workflow for US market"""
        # Step 1: Login to US market
        form_data = {
            "username": "us_admin",
            "password": "uspass",
            "market": "us"
        }
        mock_request.form = AsyncMock(return_value=form_data)
        
        # Mock database
        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_admin_us
        mock_db.commit = Mock()
        mock_db.close = Mock()
        
        with patch('src.app_01.admin.multi_market_admin_views.db_manager') as mock_db_manager:
            # Use side_effect with a function to avoid StopIteration in async context
            def get_db_gen(market):
                yield mock_db
            mock_db_manager.get_db_session.side_effect = get_db_gen
            
            # Test login
            login_result = await auth_backend.login(mock_request)
            assert login_result is True
            assert mock_request.session["admin_market"] == "us"
            assert mock_request.session["market_currency"] == "$"
            
            # Step 2: Test authentication
            auth_result = await auth_backend.authenticate(mock_request)
            assert auth_result is True
            
            # Step 3: Test market-aware model view
            # Test the get_db_session method directly without initialization
            with patch('src.app_01.admin.multi_market_admin_views.db_manager') as mock_db_manager2:
                mock_db_manager2.get_db_session.return_value = iter([mock_db])
                db_session = MarketAwareModelView.get_db_session(None, mock_request)
                assert db_session == mock_db
    
    @pytest.mark.asyncio
    async def test_market_switching_workflow(self, auth_backend, mock_request, mock_admin_kg, mock_admin_us):
        """Test switching between markets"""
        # Step 1: Login to KG market
        form_data_kg = {
            "username": "kg_admin",
            "password": "kgpass",
            "market": "kg"
        }
        mock_request.form = AsyncMock(return_value=form_data_kg)
        
        mock_db_kg = Mock(spec=Session)
        mock_db_kg.query.return_value.filter.return_value.first.return_value = mock_admin_kg
        mock_db_kg.commit = Mock()
        mock_db_kg.close = Mock()
        
        with patch('src.app_01.admin.multi_market_admin_views.db_manager') as mock_db_manager:
            mock_db_manager.get_db_session.return_value = iter([mock_db_kg])
            
            # Login to KG
            kg_login = await auth_backend.login(mock_request)
            assert kg_login is True
            assert mock_request.session["admin_market"] == "kg"
            
            # Step 2: Logout
            logout_result = await auth_backend.logout(mock_request)
            assert logout_result is True
            assert len(mock_request.session) == 0
            
            # Step 3: Login to US market
            form_data_us = {
                "username": "us_admin",
                "password": "uspass",
                "market": "us"
            }
            mock_request.form = AsyncMock(return_value=form_data_us)
            
            mock_db_us = Mock(spec=Session)
            mock_db_us.query.return_value.filter.return_value.first.return_value = mock_admin_us
            mock_db_us.commit = Mock()
            mock_db_us.close = Mock()
            
            mock_db_manager.get_db_session.return_value = iter([mock_db_us])
            
            # Login to US
            us_login = await auth_backend.login(mock_request)
            assert us_login is True
            assert mock_request.session["admin_market"] == "us"
            assert mock_request.session["market_currency"] == "$"


class TestErrorHandling:
    """Test error handling scenarios"""
    
    @pytest.fixture
    def auth_backend(self):
        """Create authentication backend instance"""
        return MultiMarketAuthenticationBackend(secret_key="test-secret-key")
    
    @pytest.fixture
    def mock_request(self):
        """Create mock request"""
        request = Mock(spec=Request)
        request.session = {}
        return request
    
    @pytest.mark.asyncio
    async def test_database_connection_error(self, auth_backend, mock_request):
        """Test handling of database connection errors"""
        # Mock form data
        form_data = {
            "username": "testadmin",
            "password": "testpass",
            "market": "kg"
        }
        mock_request.form = AsyncMock(return_value=form_data)
        
        # Mock db_manager to raise exception
        with patch('src.app_01.admin.multi_market_admin_views.db_manager') as mock_db_manager:
            mock_db_manager.get_db_session.side_effect = Exception("Database connection failed")
            
            # Test login
            result = await auth_backend.login(mock_request)
            
            # Assertions
            assert result is False
            assert len(mock_request.session) == 0
    
    @pytest.mark.asyncio
    async def test_bcrypt_error_handling(self, auth_backend, mock_request):
        """Test handling of bcrypt errors"""
        # Mock form data
        form_data = {
            "username": "testadmin",
            "password": "testpass",
            "market": "kg"
        }
        mock_request.form = AsyncMock(return_value=form_data)
        
        # Mock admin with invalid hash
        mock_admin = Mock(spec=Admin)
        mock_admin.id = 1
        mock_admin.username = "testadmin"
        mock_admin.is_active = True
        mock_admin.hashed_password = "invalid_hash"
        
        # Mock database
        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_admin
        mock_db.close = Mock()
        
        with patch('src.app_01.admin.multi_market_admin_views.db_manager') as mock_db_manager:
            mock_db_manager.get_db_session.return_value = iter([mock_db])
            
            # Test login (should handle bcrypt error gracefully)
            result = await auth_backend.login(mock_request)
            
            # Assertions
            assert result is False
            assert len(mock_request.session) == 0


class TestEnhancedMarketAwareFeatures:
    """Test the new enhanced features in MarketAwareModelView"""
    
    @pytest.fixture
    def enhanced_product_admin(self):
        """Create ProductAdmin with enhanced features"""
        return ProductAdmin()
    
    @pytest.fixture
    def mock_request_with_admin_session(self):
        """Create mock request with admin session"""
        request = Mock(spec=Request)
        request.session = {
            "admin_id": 1,
            "admin_market": "kg",
            "token": "test-token"
        }
        request.url = Mock()
        request.url.path = "/admin/product/edit/123"
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.headers = {"user-agent": "test-browser"}
        return request
    
    def test_product_admin_has_role_requirements(self, enhanced_product_admin):
        """Test that ProductAdmin has proper role requirements"""
        assert enhanced_product_admin.required_roles == ["website_content", "super_admin"]
        assert "manage_products" in enhanced_product_admin.required_permissions.values()
        assert "delete_products" in enhanced_product_admin.required_permissions.values()
    
    @pytest.mark.asyncio
    async def test_permission_check_with_super_admin(self, enhanced_product_admin, mock_request_with_admin_session):
        """Test permission check with super admin"""
        mock_admin = Mock()
        mock_admin.id = 1
        mock_admin.is_active = True
        mock_admin.is_super_admin = True
        
        with patch.object(db_manager, 'get_db_session') as mock_db_session:
            mock_db = Mock()
            mock_db_session.return_value = mock_db
            mock_db.query.return_value.filter.return_value.first.return_value = mock_admin
            mock_db.close = Mock()
            
            # Super admin should have all permissions
            assert enhanced_product_admin.check_permissions(mock_request_with_admin_session, "create") == True
            assert enhanced_product_admin.check_permissions(mock_request_with_admin_session, "delete") == True
    
    @pytest.mark.asyncio
    async def test_permission_check_with_wrong_role(self, enhanced_product_admin, mock_request_with_admin_session):
        """Test permission check with admin having wrong role"""
        mock_admin = Mock()
        mock_admin.id = 1
        mock_admin.is_active = True
        mock_admin.is_super_admin = False
        mock_admin.admin_role = "order_management"  # Wrong role for product admin
        
        with patch.object(db_manager, 'get_db_session') as mock_db_session:
            mock_db = Mock()
            mock_db_session.return_value = mock_db
            mock_db.query.return_value.filter.return_value.first.return_value = mock_admin
            mock_db.close = Mock()
            
            # Should be denied due to wrong role
            assert enhanced_product_admin.check_permissions(mock_request_with_admin_session, "create") == False
    
    def test_audit_logging_functionality(self, enhanced_product_admin, mock_request_with_admin_session):
        """Test that admin actions are logged with market context"""
        with patch.object(db_manager, 'get_db_session') as mock_db_session:
            mock_db = Mock()
            mock_db_session.return_value = mock_db
            mock_db.add = Mock()
            mock_db.commit = Mock()
            mock_db.close = Mock()
            
            # Call log_admin_action
            enhanced_product_admin.log_admin_action(
                mock_request_with_admin_session,
                "create",
                entity_id=123,
                description="Created new product"
            )
            
            # Verify log entry was created
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
            
            # Check the log entry details
            log_entry = mock_db.add.call_args[0][0]
            assert log_entry.admin_id == 1
            assert log_entry.action == "create"
            assert log_entry.entity_id == 123
            assert "[KG]" in log_entry.description
            assert log_entry.ip_address == "127.0.0.1"


class TestDashboardEnhancements:
    """Test enhanced dashboard features"""
    
    @pytest.fixture
    def dashboard_view(self):
        """Create DashboardView instance"""
        from src.app_01.admin.dashboard_admin_views import DashboardView
        return DashboardView()
    
    @pytest.fixture
    def mock_request_kg(self):
        """Mock request for KG market"""
        request = Mock(spec=Request)
        request.session = {"admin_market": "kg"}
        return request
    
    @pytest.fixture
    def mock_request_us(self):
        """Mock request for US market"""
        request = Mock(spec=Request)
        request.session = {"admin_market": "us"}
        return request
    
    @pytest.mark.asyncio
    async def test_dashboard_market_context_kg(self, dashboard_view, mock_request_kg):
        """Test dashboard shows correct market context for KG"""
        with patch.object(db_manager, 'get_db_session') as mock_db_session:
            mock_db = Mock()
            # Mock all database queries to return 0
            mock_db.query.return_value.filter.return_value.scalar.return_value = 0
            mock_db.query.return_value.order_by.return_value.limit.return_value.all.return_value = []
            mock_db.close = Mock()
            mock_db_session.return_value = mock_db
            
            result = await dashboard_view.index(mock_request_kg)
            
            assert isinstance(result, HTMLResponse)
            content = result.body.decode()
            
            # Should show KG market context
            assert "🇰🇬" in content
            assert "Kyrgyzstan" in content
            assert "сом" in content
    
    @pytest.mark.asyncio
    async def test_dashboard_market_context_us(self, dashboard_view, mock_request_us):
        """Test dashboard shows correct market context for US"""
        with patch.object(db_manager, 'get_db_session') as mock_db_session:
            mock_db = Mock()
            # Mock all database queries to return 0
            mock_db.query.return_value.filter.return_value.scalar.return_value = 0
            mock_db.query.return_value.order_by.return_value.limit.return_value.all.return_value = []
            mock_db.close = Mock()
            mock_db_session.return_value = mock_db
            
            result = await dashboard_view.index(mock_request_us)
            
            assert isinstance(result, HTMLResponse)
            content = result.body.decode()
            
            # Should show US market context
            assert "🇺🇸" in content
            assert "United States" in content
            assert "$" in content
    
    @pytest.mark.asyncio
    async def test_dashboard_market_comparison(self, dashboard_view, mock_request_kg):
        """Test dashboard includes market comparison analytics"""
        with patch.object(db_manager, 'get_db_session') as mock_db_session:
            # Mock KG database (current market)
            mock_kg_db = Mock()
            mock_kg_db.query.return_value.filter.return_value.scalar.return_value = 5
            mock_kg_db.query.return_value.order_by.return_value.limit.return_value.all.return_value = []
            mock_kg_db.close = Mock()
            
            # Mock US database (comparison market)
            mock_us_db = Mock()
            mock_us_db.query.return_value.filter.return_value.scalar.return_value = 3
            mock_us_db.close = Mock()
            
            # Return KG first, then US for comparison
            mock_db_session.side_effect = [mock_kg_db, mock_us_db]
            
            result = await dashboard_view.index(mock_request_kg)
            
            assert isinstance(result, HTMLResponse)
            content = result.body.decode()
            
            # Should include comparison section
            assert "Сравнение Рынков" in content
            assert "vs" in content


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
