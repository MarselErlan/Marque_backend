from sqladmin import Admin
from fastapi import FastAPI
from ..db.market_db import db_manager, Market
from .sqladmin_views import (
    WebsiteContentAuthenticationBackend,
    ProductAdmin, SKUAdmin, ProductAssetAdmin, ProductAttributeAdmin,
    ReviewAdmin, AdminLogAdmin, WebsiteContentDashboard
)
from .catalog_admin_views import CategoryAdmin, SubcategoryAdmin, BrandAdmin
from .filter_admin_views import (
    ProductFilterAdmin, ProductSeasonAdmin, ProductMaterialAdmin, 
    ProductStyleAdmin, ProductDiscountAdmin, ProductSearchAdmin
)
from .user_admin_views import (
    UserAdmin, PhoneVerificationAdmin, UserAddressAdmin, 
    UserPaymentMethodAdmin, UserNotificationAdmin
)
# Import order management views
from .order_admin_views import OrderAdmin, OrderItemAdmin, OrderStatusHistoryAdmin
from .banner_admin_views import BannerAdmin
from .cart_admin_views import CartAdmin, CartItemAdmin
from .wishlist_admin_views import WishlistAdmin, WishlistItemAdmin
from .admin_user_admin_views import AdminUserAdmin
# Import dashboard
from .dashboard_admin_views import DashboardView


def create_sqladmin_app(app: FastAPI) -> Admin:
    """Create and configure SQLAdmin for website content management"""
    
    # Use KG market engine as default for admin (can be switched later)
    engine = db_manager.get_engine(Market.KG)
    
    # Initialize SQLAdmin with authentication
    # Note: templates_dir is required for custom templates, but we use default
    admin = Admin(
        app=app,
        engine=engine,
        authentication_backend=WebsiteContentAuthenticationBackend(secret_key="your-secret-key-here"),
        title="Marque - Admin Panel",
        base_url="/admin",
        # Explicitly set middlewares list to empty to avoid conflicts
        middlewares=[]
    )
    
    # Add all admin views
    
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
    
    return admin


def create_website_content_admin_app() -> FastAPI:
    """Create FastAPI app specifically for website content admin"""
    
    app = FastAPI(
        title="Marque Website Content Admin",
        description="Admin interface for managing website content, products, and attributes",
        version="1.0.0"
    )
    
    # Create SQLAdmin instance
    admin = create_sqladmin_app(app)
    
    return app
