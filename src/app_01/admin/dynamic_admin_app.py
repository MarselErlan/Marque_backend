"""
Dynamic Multi-Market Admin Panel

This admin system allows admins to select which market (KG or US) they want to manage,
and all operations will be performed on the selected market's database.
"""

from sqladmin import Admin
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse
import logging

from ..db.market_db import db_manager, Market

from .sqladmin_views import (
    WebsiteContentAuthenticationBackend,
    ProductAdmin, SKUAdmin, ProductAssetAdmin, ProductAttributeAdmin,
    ReviewAdmin, WebsiteContentDashboard
)
from .admin_log_admin_views import AdminLogAdmin
from .catalog_admin_views import CategoryAdmin, SubcategoryAdmin, BrandAdmin
from .filter_admin_views import (
    ProductFilterAdmin, ProductSeasonAdmin, ProductMaterialAdmin, 
    ProductStyleAdmin, ProductDiscountAdmin, ProductSearchAdmin
)
from .user_admin_views import (
    UserAdmin, PhoneVerificationAdmin, UserAddressAdmin, 
    UserPaymentMethodAdmin, UserNotificationAdmin
)
from .order_admin_views import OrderAdmin, OrderItemAdmin, OrderStatusHistoryAdmin
from .banner_admin_views import BannerAdmin
from .cart_admin_views import CartAdmin, CartItemAdmin
from .wishlist_admin_views import WishlistAdmin, WishlistItemAdmin
from .admin_user_admin_views import AdminUserAdmin
from .dashboard_admin_views import DashboardView
from .market_selector import MarketSelectorView, MarketSwitcherView, get_current_market

logger = logging.getLogger(__name__)


class MarketMiddleware(BaseHTTPMiddleware):
    """
    Middleware to ensure market is selected before accessing admin.
    Redirects to market selector if no market is selected.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Check if this is an admin route
        if request.url.path.startswith("/admin"):
            # Allow login page and market selector
            if request.url.path in ["/admin/login", "/admin/market-selector", "/admin/switch-market"]:
                return await call_next(request)
            
            # Check if session is available (SessionMiddleware must be installed)
            if "session" in request.scope:
                # Check if user is authenticated
                if request.session.get("token"):
                    # Check if market is selected
                    if not request.session.get("selected_market"):
                        # Set default market if not set
                        request.session["selected_market"] = "kg"
                        logger.info(f"✅ Set default market 'KG' for admin '{request.session.get('admin_username')}'")
        
        response = await call_next(request)
        return response


def create_dynamic_admin(app: FastAPI) -> Admin:
    """
    Create admin panel with dynamic market switching.
    
    The engine will be switched based on the selected market in the session.
    """
    
    # Start with KG market engine as default
    default_engine = db_manager.get_engine(Market.KG)
    
    # Initialize SQLAdmin with authentication
    admin = Admin(
        app=app,
        engine=default_engine,
        authentication_backend=WebsiteContentAuthenticationBackend(secret_key="your-secret-key-here"),
        title="Marque - Multi-Market Admin",
        base_url="/admin",
        middlewares=[]
    )
    
    # Add market selector and switcher
    admin.add_view(MarketSelectorView)
    admin.add_view(MarketSwitcherView)
    
    # Add all admin views with market-aware sessions
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🌍 MARKET MANAGEMENT
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Market selector is already added above
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 📊 DASHBOARD (MAIN VIEW - Business Intelligence)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # TODO: Fix DashboardView routing issue - temporarily disabled
    # admin.add_view(DashboardView)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🛒 ORDER MANAGEMENT (CRITICAL for e-commerce)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    admin.add_view(OrderAdmin)
    admin.add_view(OrderItemAdmin)
    admin.add_view(OrderStatusHistoryAdmin)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🛍️ CART & WISHLIST MANAGEMENT
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    admin.add_view(CartAdmin)
    admin.add_view(CartItemAdmin)
    admin.add_view(WishlistAdmin)
    admin.add_view(WishlistItemAdmin)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 👤 USER MANAGEMENT
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    admin.add_view(UserAdmin)
    admin.add_view(PhoneVerificationAdmin)
    admin.add_view(UserAddressAdmin)
    admin.add_view(UserPaymentMethodAdmin)
    admin.add_view(UserNotificationAdmin)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 📦 CATALOG MANAGEMENT
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    admin.add_view(CategoryAdmin)
    admin.add_view(SubcategoryAdmin)
    admin.add_view(BrandAdmin)
    admin.add_view(ProductFilterAdmin)
    admin.add_view(ProductSeasonAdmin)
    admin.add_view(ProductMaterialAdmin)
    admin.add_view(ProductStyleAdmin)
    admin.add_view(ProductDiscountAdmin)
    admin.add_view(ProductSearchAdmin)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🛍️ PRODUCT MANAGEMENT
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    admin.add_view(ProductAdmin)
    admin.add_view(SKUAdmin)
    admin.add_view(ProductAssetAdmin)
    admin.add_view(ProductAttributeAdmin)
    admin.add_view(ReviewAdmin)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🎨 MARKETING & CONTENT
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    admin.add_view(BannerAdmin)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔐 ADMIN MANAGEMENT
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    admin.add_view(AdminUserAdmin)
    admin.add_view(AdminLogAdmin)
    
    logger.info("✅ Dynamic multi-market admin panel created")
    
    return admin


class DynamicSessionMixin:
    """
    Mixin for ModelView to use market-aware database sessions.
    
    This should be added to all ModelView classes that need to work
    with the selected market's database.
    """
    
    def get_session_maker(self, request: Request = None):
        """
        Override to return session maker for the selected market.
        """
        if request and hasattr(request, "session"):
            market = get_current_market(request)
            logger.debug(f"🌍 Using {market.value.upper()} database for {self.__class__.__name__}")
            return db_manager.get_session_factory(market)
        
        # Fallback to KG market
        logger.warning(f"⚠️  No request/session found, using KG database as fallback")
        return db_manager.get_session_factory(Market.KG)
    
    async def get_model_objects(self, request: Request):
        """
        Override to use the correct market's database.
        """
        session_maker = self.get_session_maker(request)
        session = session_maker()
        
        try:
            query = session.query(self.model)
            
            # Apply any filters
            if hasattr(self, 'list_query'):
                query = await self.list_query(request, query)
            
            return query.all()
        finally:
            session.close()


def add_market_awareness_to_views(admin: Admin):
    """
    Patches all admin views to be market-aware.
    
    This function overrides the get_session method to use the selected market's database.
    """
    from sqlalchemy.orm import Session
    
    for view in admin._views:
        if hasattr(view, 'model'):  # Only ModelView instances
            # Store original session method
            original_get_session = getattr(view, '_get_session', None)
            
            # Create market-aware session getter
            def create_session_getter(view_instance):
                async def get_session_wrapper(request: Request):
                    """Get session for the selected market"""
                    try:
                        if hasattr(request, 'session') and 'selected_market' in request.session:
                            market = get_current_market(request)
                            logger.debug(f"🌍 {view_instance.__class__.__name__}: Creating session for {market.value.upper()} database")
                            session_factory = db_manager.get_session_factory(market)
                            session = session_factory()
                            return session
                        else:
                            logger.debug(f"⚠️  No selected_market in session, using KG")
                    except Exception as e:
                        logger.warning(f"   Error getting market from session: {e}")
                    
                    # Fallback to KG
                    logger.debug(f"   {view_instance.__class__.__name__}: Using KG database (fallback)")
                    session_factory = db_manager.get_session_factory(Market.KG)
                    return session_factory()
                
                return get_session_wrapper
            
            # Override the _get_session method
            view._get_session = create_session_getter(view)
    
    logger.info(f"✅ Added market awareness to {len(admin._views)} admin views")

