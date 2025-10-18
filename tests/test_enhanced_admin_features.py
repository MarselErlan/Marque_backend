"""
Tests for Enhanced Admin Features

This module tests the new admin features implemented:
1. Role-based permissions in MarketAwareModelView
2. Enhanced audit logging with market context
3. Market comparison analytics in dashboard
4. Market switching functionality
5. Market-specific theming and branding
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
import bcrypt
from datetime import datetime

# Import the classes we're testing
from src.app_01.admin.multi_market_admin_views import (
    MultiMarketAuthenticationBackend,
    MarketAwareModelView,
    ProductAdmin
)
from src.app_01.admin.dashboard_admin_views import DashboardView
from src.app_01.db.market_db import Market, db_manager
from src.app_01.models import Admin, Product, AdminLog, Order, User


class TestMarketAwarePermissions:
    """Test role-based permissions in MarketAwareModelView"""
    
    @pytest.fixture
    def market_aware_view(self):
        """Create MarketAwareModelView instance"""
        # Create a test class that inherits from MarketAwareModelView
        class TestMarketAwareView(MarketAwareModelView, model=Product):
            pass
        return TestMarketAwareView()
    
    @pytest.fixture
    def mock_request_with_session(self):
        """Create mock request with session data"""
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
    
    @pytest.fixture
    def mock_admin_super(self):
        """Create mock super admin"""
        admin = Mock(spec=Admin)
        admin.id = 1
        admin.username = "superadmin"
        admin.is_active = True
        admin.is_super_admin = True
        admin.admin_role = "super_admin"
        admin.has_permission = Mock(return_value=True)
        return admin
    
    @pytest.fixture
    def mock_admin_limited(self):
        """Create mock limited admin"""
        admin = Mock(spec=Admin)
        admin.id = 2
        admin.username = "limitedadmin"
        admin.is_active = True
        admin.is_super_admin = False
        admin.admin_role = "order_management"
        admin.has_permission = Mock(return_value=False)
        return admin
    
    @pytest.mark.asyncio
    async def test_check_permissions_super_admin_access(self, market_aware_view, mock_request_with_session, mock_admin_super):
        """Test that super admin has access to all operations"""
        with patch.object(db_manager, 'get_db_session') as mock_db_session:
            mock_db = Mock()
            # Create a function that returns a new iterator each time
            mock_db_session.side_effect = lambda market: iter([mock_db])
            mock_db.query.return_value.filter.return_value.first.return_value = mock_admin_super
            mock_db.close = Mock()
            
            # Super admin should have access to all operations
            assert market_aware_view.check_permissions(mock_request_with_session, "list") == True
            assert market_aware_view.check_permissions(mock_request_with_session, "create") == True
            assert market_aware_view.check_permissions(mock_request_with_session, "edit") == True
            assert market_aware_view.check_permissions(mock_request_with_session, "delete") == True
    
    @pytest.mark.asyncio
    async def test_check_permissions_role_mismatch(self, mock_request_with_session, mock_admin_limited):
        """Test that admin with wrong role is denied access"""
        # Create ProductAdmin which requires website_content role
        product_admin = ProductAdmin()
        
        with patch.object(db_manager, 'get_db_session') as mock_db_session:
            mock_db = Mock()
            mock_db_session.return_value = iter([mock_db])  # Make it an iterator
            mock_db.query.return_value.filter.return_value.first.return_value = mock_admin_limited
            mock_db.close = Mock()
            
            # Admin with order_management role should not access product admin
            assert product_admin.check_permissions(mock_request_with_session, "list") == False
    
    @pytest.mark.asyncio
    async def test_check_permissions_missing_permission(self, market_aware_view, mock_request_with_session, mock_admin_limited):
        """Test that admin without specific permission is denied"""
        # Set up view to require specific permission for delete
        market_aware_view.required_permissions = {"delete": "delete_products"}
        
        with patch.object(db_manager, 'get_db_session') as mock_db_session:
            mock_db = Mock()
            mock_db_session.return_value = iter([mock_db])  # Make it an iterator
            mock_db.query.return_value.filter.return_value.first.return_value = mock_admin_limited
            mock_db.close = Mock()
            
            # Admin without delete_products permission should be denied
            assert market_aware_view.check_permissions(mock_request_with_session, "delete") == False
    
    @pytest.mark.asyncio
    async def test_create_with_permission_denied(self, market_aware_view, mock_request_with_session):
        """Test create operation with permission denied"""
        with patch.object(market_aware_view, 'check_permissions', return_value=False):
            result = await market_aware_view.create(mock_request_with_session)
            
            assert isinstance(result, HTMLResponse)
            assert result.status_code == 403
            assert "Access Denied" in result.body.decode()
    
    @pytest.mark.asyncio
    async def test_delete_with_permission_denied(self, market_aware_view, mock_request_with_session):
        """Test delete operation with permission denied"""
        with patch.object(market_aware_view, 'check_permissions', return_value=False):
            result = await market_aware_view.delete(mock_request_with_session)
            
            assert isinstance(result, JSONResponse)
            assert result.status_code == 403


class TestAuditLogging:
    """Test enhanced audit logging functionality"""
    
    @pytest.fixture
    def market_aware_view(self):
        """Create MarketAwareModelView instance"""
        # Create a test class that inherits from MarketAwareModelView
        class TestMarketAwareView(MarketAwareModelView, model=Product):
            pass
        return TestMarketAwareView()
    
    @pytest.fixture
    def mock_request_with_session(self):
        """Create mock request with session data"""
        request = Mock(spec=Request)
        request.session = {
            "admin_id": 1,
            "admin_market": "kg",
            "token": "test-token"
        }
        request.client = Mock()
        request.client.host = "192.168.1.100"
        request.headers = {"user-agent": "Mozilla/5.0 Test Browser"}
        return request
    
    def test_log_admin_action_creates_log_entry(self, market_aware_view, mock_request_with_session):
        """Test that admin actions are properly logged"""
        with patch.object(db_manager, 'get_db_session') as mock_db_session:
            mock_db = Mock()
            mock_db_session.return_value = iter([mock_db])  # Make it an iterator
            mock_db.add = Mock()
            mock_db.commit = Mock()
            mock_db.close = Mock()
            
            # Call log_admin_action
            market_aware_view.log_admin_action(
                mock_request_with_session, 
                "create", 
                entity_id=123, 
                description="Created new product"
            )
            
            # Verify log entry was created
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
            
            # Get the AdminLog instance that was added
            log_entry = mock_db.add.call_args[0][0]
            assert log_entry.admin_id == 1
            assert log_entry.action == "create"
            assert log_entry.entity_type == "product"
            assert log_entry.entity_id == 123
            assert "[KG]" in log_entry.description
            assert log_entry.ip_address == "192.168.1.100"
            assert "Mozilla/5.0 Test Browser" in log_entry.user_agent
    
    @pytest.mark.asyncio
    async def test_create_logs_action(self, market_aware_view, mock_request_with_session):
        """Test that create operation logs the action"""
        with patch.object(market_aware_view, 'check_permissions', return_value=True), \
             patch.object(market_aware_view, 'log_admin_action') as mock_log, \
             patch('src.app_01.admin.multi_market_admin_views.ModelView.create', new_callable=AsyncMock) as mock_super_create:
            
            mock_super_create.return_value = Mock()
            
            await market_aware_view.create(mock_request_with_session)
            
            # Verify action was logged
            mock_log.assert_called_once()
            args = mock_log.call_args[0]
            assert args[1] == "create"  # action
            assert "Created new Product" in args[3]  # description
    
    @pytest.mark.asyncio
    async def test_edit_logs_action_with_entity_id(self, market_aware_view, mock_request_with_session):
        """Test that edit operation logs the action with entity ID"""
        mock_request_with_session.url.path = "/admin/product/edit/456"
        
        with patch.object(market_aware_view, 'check_permissions', return_value=True), \
             patch.object(market_aware_view, 'log_admin_action') as mock_log, \
             patch('src.app_01.admin.multi_market_admin_views.ModelView.edit', new_callable=AsyncMock) as mock_super_edit:
            
            mock_super_edit.return_value = Mock()
            
            await market_aware_view.edit(mock_request_with_session)
            
            # Verify action was logged with entity ID
            mock_log.assert_called_once()
            args = mock_log.call_args
            assert args[0][1] == "update"  # action
            assert args[0][2] == 456  # entity_id
            assert "Updated Product" in args[0][3]  # description


class TestDashboardAnalytics:
    """Test market comparison analytics in dashboard"""
    
    @pytest.fixture
    def dashboard_view(self):
        """Create DashboardView instance"""
        return DashboardView()
    
    @pytest.fixture
    def mock_request_kg_market(self):
        """Create mock request for KG market"""
        request = Mock(spec=Request)
        request.session = {"admin_market": "kg"}
        return request
    
    @pytest.fixture
    def mock_request_us_market(self):
        """Create mock request for US market"""
        request = Mock(spec=Request)
        request.session = {"admin_market": "us"}
        return request
    
    @pytest.mark.asyncio
    async def test_dashboard_loads_market_comparison_data(self, dashboard_view, mock_request_kg_market):
        """Test that dashboard loads comparison data from both markets"""
        with patch.object(db_manager, 'get_db_session') as mock_db_session:
            # Mock KG database
            mock_kg_db = Mock()
            mock_kg_db.query.return_value.filter.return_value.scalar.return_value = 5  # orders today
            mock_kg_db.close = Mock()
            
            # Mock US database  
            mock_us_db = Mock()
            mock_us_db.query.return_value.filter.return_value.scalar.return_value = 3  # orders today
            mock_us_db.close = Mock()
            
            # Return KG db first, then US db for comparison (as iterators)
            mock_db_session.side_effect = [iter([mock_kg_db]), iter([mock_us_db])]
            
            result = await dashboard_view.index(mock_request_kg_market)
            
            # Verify both databases were accessed
            assert mock_db_session.call_count == 2
            assert isinstance(result, HTMLResponse)
            
            # Check that comparison data is in the response
            content = result.body.decode()
            assert "Сравнение Рынков" in content
            assert "vs" in content  # Should show comparison
    
    @pytest.mark.asyncio
    async def test_dashboard_handles_comparison_error_gracefully(self, dashboard_view, mock_request_kg_market):
        """Test that dashboard handles errors when fetching comparison data"""
        with patch.object(db_manager, 'get_db_session') as mock_db_session:
            # Mock KG database (main market)
            mock_kg_db = Mock()
            mock_kg_db.query.return_value.filter.return_value.scalar.return_value = 5
            mock_kg_db.close = Mock()
            
            # Mock US database to raise exception
            mock_us_db = Mock()
            mock_us_db.query.side_effect = Exception("Database connection error")
            mock_us_db.close = Mock()
            
            mock_db_session.side_effect = [iter([mock_kg_db]), iter([mock_us_db])]
            
            result = await dashboard_view.index(mock_request_kg_market)
            
            # Should still return successful response despite comparison error
            assert isinstance(result, HTMLResponse)
            assert result.status_code == 200
    
    @pytest.mark.asyncio
    async def test_dashboard_market_specific_theming(self, dashboard_view, mock_request_kg_market, mock_request_us_market):
        """Test that dashboard applies market-specific theming"""
        with patch.object(db_manager, 'get_db_session') as mock_db_session:
            mock_db = Mock()
            mock_db.query.return_value.filter.return_value.scalar.return_value = 0
            mock_db.query.return_value.order_by.return_value.limit.return_value.all.return_value = []
            mock_db.close = Mock()
            mock_db_session.return_value = iter([mock_db])
            
            # Test KG market theming
            kg_result = await dashboard_view.index(mock_request_kg_market)
            kg_content = kg_result.body.decode()
            
            # Should contain KG flag and colors
            assert "🇰🇬" in kg_content
            assert "#c41e3a" in kg_content  # KG red color
            assert "сом" in kg_content  # KG currency
            
            # Test US market theming
            us_result = await dashboard_view.index(mock_request_us_market)
            us_content = us_result.body.decode()
            
            # Should contain US flag and colors
            assert "🇺🇸" in us_content
            assert "#002868" in us_content  # US blue color
            assert "$" in us_content  # US currency


class TestMarketSwitching:
    """Test market switching functionality"""
    
    @pytest.mark.asyncio
    async def test_market_switching_endpoint_success(self):
        """Test successful market switching"""
        from src.app_01.main import switch_market
        
        # Create mock request with form data
        request = Mock(spec=Request)
        request.session = {"admin_id": 1, "token": "test-token"}
        
        # Mock form data
        mock_form = Mock()
        mock_form.get.return_value = "us"
        request.form = AsyncMock(return_value=mock_form)
        
        result = await switch_market(request)
        
        # Verify session was updated
        assert request.session["admin_market"] == "us"
        
        # Verify JSON response
        assert hasattr(result, 'body')
    
    @pytest.mark.asyncio
    async def test_market_switching_invalid_market(self):
        """Test market switching with invalid market"""
        from src.app_01.main import switch_market
        
        request = Mock(spec=Request)
        request.session = {"admin_id": 1, "token": "test-token"}
        
        # Mock form data with invalid market
        mock_form = Mock()
        mock_form.get.return_value = "invalid"
        request.form = AsyncMock(return_value=mock_form)
        
        result = await switch_market(request)
        
        # Should return error response
        assert result.status_code == 400
    
    @pytest.mark.asyncio
    async def test_market_switching_unauthenticated(self):
        """Test market switching without authentication"""
        from src.app_01.main import switch_market
        
        request = Mock(spec=Request)
        request.session = {}  # No admin_id or token
        
        mock_form = Mock()
        mock_form.get.return_value = "us"
        request.form = AsyncMock(return_value=mock_form)
        
        result = await switch_market(request)
        
        # Should return 401 unauthorized
        assert result.status_code == 401


class TestMarketAwareDatabase:
    """Test that MarketAwareModelView correctly routes to market databases"""
    
    @pytest.fixture
    def market_aware_view(self):
        # Create a test class that inherits from MarketAwareModelView
        class TestMarketAwareView(MarketAwareModelView, model=Product):
            pass
        return TestMarketAwareView()
    
    def test_get_db_session_kg_market(self, market_aware_view):
        """Test database session routing for KG market"""
        request = Mock(spec=Request)
        request.session = {"admin_market": "kg"}
        
        with patch.object(db_manager, 'get_db_session') as mock_get_session:
            mock_get_session.return_value = iter([Mock()])
            
            result = market_aware_view.get_db_session(request)
            
            # Verify KG market was requested
            mock_get_session.assert_called_once_with(Market.KG)
    
    def test_get_db_session_us_market(self, market_aware_view):
        """Test database session routing for US market"""
        request = Mock(spec=Request)
        request.session = {"admin_market": "us"}
        
        with patch.object(db_manager, 'get_db_session') as mock_get_session:
            mock_get_session.return_value = iter([Mock()])
            
            result = market_aware_view.get_db_session(request)
            
            # Verify US market was requested
            mock_get_session.assert_called_once_with(Market.US)
    
    def test_get_db_session_default_kg(self, market_aware_view):
        """Test database session defaults to KG when no market in session"""
        request = Mock(spec=Request)
        request.session = {}  # No admin_market
        
        with patch.object(db_manager, 'get_db_session') as mock_get_session:
            mock_get_session.return_value = iter([Mock()])
            
            result = market_aware_view.get_db_session(request)
            
            # Should default to KG market
            mock_get_session.assert_called_once_with(Market.KG)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
