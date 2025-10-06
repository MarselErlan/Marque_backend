from sqladmin import Admin
from fastapi import FastAPI
from ..db.market_db import db_manager, Market
from .sqladmin_views import (
    WebsiteContentAuthenticationBackend,
    ProductAdmin, SKUAdmin, ProductAssetAdmin, ProductAttributeAdmin,
    ReviewAdmin, UserAdmin, AdminLogAdmin, WebsiteContentDashboard
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


def create_sqladmin_app(app: FastAPI) -> Admin:
    """Create and configure SQLAdmin for website content management"""
    
    # Use KG market engine as default for admin (can be switched later)
    engine = db_manager.get_engine(Market.KG)
    
    # Initialize SQLAdmin with authentication
    admin = Admin(
        app=app,
        engine=engine,
        authentication_backend=WebsiteContentAuthenticationBackend(secret_key="your-secret-key-here"),
        title="Marque - Admin Panel",
        base_url="/admin"
    )
    
    # Add all admin views
    # User Management
    admin.add_view(UserAdmin)
    admin.add_view(PhoneVerificationAdmin)
    admin.add_view(UserAddressAdmin)
    admin.add_view(UserPaymentMethodAdmin)
    admin.add_view(UserNotificationAdmin)
    
    # Catalog Management
    admin.add_view(CategoryAdmin)
    admin.add_view(SubcategoryAdmin)
    admin.add_view(BrandAdmin)
    admin.add_view(ProductFilterAdmin)
    admin.add_view(ProductSeasonAdmin)
    admin.add_view(ProductMaterialAdmin)
    admin.add_view(ProductStyleAdmin)
    admin.add_view(ProductDiscountAdmin)
    admin.add_view(ProductSearchAdmin)
    
    # Product Management
    admin.add_view(ProductAdmin)
    admin.add_view(SKUAdmin)
    admin.add_view(ProductAssetAdmin)
    admin.add_view(ProductAttributeAdmin)
    admin.add_view(ReviewAdmin)
    
    # Admin Management
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
