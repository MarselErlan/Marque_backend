"""
Main FastAPI Application
Multi-market phone authentication system
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import uvicorn

from .routers.auth_router import router as auth_router
from .routers.product_router import router as product_router
from .routers.category_router import router as category_router
from .routers.cart_router import router as cart_router
from .routers.wishlist_router import router as wishlist_router
from .routers.banner_router import router as banner_router
from .routers.upload_router import router as upload_router
# NEW: Enhanced model APIs
from .routers.product_asset_router import router as product_asset_router
from .routers.product_catalog_router import router as product_catalog_router
from .routers.product_search_router import router as product_search_router
from .routers.product_discount_router import router as product_discount_router
from .routers.admin_analytics_router import router as admin_analytics_router
from .services.auth_service import auth_service

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Marque Multi-Market Authentication API",
    description="Phone number authentication system for KG and US markets",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ProxyHeadersMiddleware (CRITICAL for SQLAdmin HTTPS URLs)
class ProxyHeadersMiddleware(BaseHTTPMiddleware):
    """
    Force HTTPS scheme for Railway deployment.
    This fixes SQLAdmin generating http:// URLs instead of https://
    which causes Mixed Content errors in the browser.
    """
    async def dispatch(self, request: Request, call_next):
        # Railway sets x-forwarded-proto to 'https'
        forwarded_proto = request.headers.get("x-forwarded-proto")
        if forwarded_proto == "https":
            # Force the request to use HTTPS scheme for URL generation
            request.scope["scheme"] = "https"
        response = await call_next(request)
        return response

# HTTPS Redirect Middleware (for Railway and production)
class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    """Redirect HTTP to HTTPS in production (Railway)"""
    
    async def dispatch(self, request: Request, call_next):
        # Check if request came through HTTPS proxy (Railway sets this header)
        forwarded_proto = request.headers.get("x-forwarded-proto")
        
        # If we're behind a proxy and it's HTTP, redirect to HTTPS
        if forwarded_proto == "http":
            # Get the HTTPS URL
            url = str(request.url).replace("http://", "https://", 1)
            return RedirectResponse(url=url, status_code=301)
        
        response = await call_next(request)
        return response

# Add proxy headers middleware FIRST (critical for HTTPS URL generation)
app.add_middleware(ProxyHeadersMiddleware)

# Add HTTPS redirect middleware (before other middlewares)
app.add_middleware(HTTPSRedirectMiddleware)

# Session middleware (required for admin authentication - MUST be added BEFORE SQLAdmin)
from starlette.middleware.sessions import SessionMiddleware
import os

# Session configuration for production (Railway HTTPS)
session_secret = os.getenv("SESSION_SECRET_KEY", "marque-session-secret-key-change-in-production")
is_production = os.getenv("RAILWAY_ENVIRONMENT") is not None

app.add_middleware(
    SessionMiddleware,
    secret_key=session_secret,
    session_cookie="marque_admin_session",
    max_age=14 * 24 * 60 * 60,  # 14 days
    same_site="lax",  # Required for Railway redirects
    https_only=is_production  # Only require HTTPS in production
)

# Mount static files for SQLAdmin FIRST (before initializing SQLAdmin)
try:
    from fastapi.staticfiles import StaticFiles
    import sqladmin
    import pathlib
    
    # Get SQLAdmin's static files directory
    sqladmin_static_path = pathlib.Path(sqladmin.__file__).parent / "statics"
    
    # Mount static files BEFORE creating SQLAdmin instance
    app.mount("/admin/statics", StaticFiles(directory=str(sqladmin_static_path)), name="admin-statics")
    logger.info(f"✅ SQLAdmin static files mounted from: {sqladmin_static_path}")
    
    # Mount uploads directory for user-uploaded images
    uploads_dir = pathlib.Path(__file__).parent.parent.parent / "static" / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")
    logger.info(f"✅ Uploads directory mounted from: {uploads_dir}")
    
    # Mount demo images directory (for testing/fallback)
    demo_images_dir = pathlib.Path(__file__).parent.parent.parent / "static" / "demo-images"
    demo_images_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/demo-images", StaticFiles(directory=str(demo_images_dir)), name="demo-images")
    logger.info(f"✅ Demo images directory mounted from: {demo_images_dir}")
    
except Exception as static_error:
    logger.error(f"❌ Failed to mount static files: {static_error}")
    import traceback
    traceback.print_exc()

# Initialize SQLAdmin AFTER static files are mounted
try:
    from .admin.admin_app import create_sqladmin_app
    
    admin = create_sqladmin_app(app)
    logger.info("✅ SQLAdmin initialized at /admin")
except Exception as e:
    logger.error(f"❌ SQLAdmin initialization failed: {e}")
    import traceback
    traceback.print_exc()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(product_router, prefix="/api/v1")
app.include_router(category_router, prefix="/api/v1")
app.include_router(cart_router, prefix="/api/v1")
app.include_router(wishlist_router, prefix="/api/v1")
app.include_router(banner_router, prefix="/api/v1")
app.include_router(upload_router, prefix="/api/v1")  # Image upload endpoints

# NEW: Enhanced APIs for improved models
app.include_router(product_asset_router)  # Product images/videos management
app.include_router(product_catalog_router)  # Attributes, filters, seasons, materials, styles
app.include_router(product_search_router)  # Search analytics
app.include_router(product_discount_router)  # Discounts & promotions
app.include_router(admin_analytics_router)  # Admin dashboard statistics

# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    logger.error(f"HTTP exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": "http_error",
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "internal_error",
            "message": "Internal server error",
            "status_code": 500
        }
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Application health check"""
    return {
        "status": "healthy",
        "service": "marque-auth-api",
        "version": "1.0.0",
        "markets": ["kg", "us"]
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Marque Multi-Market Authentication API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "markets": {
            "kg": "Kyrgyzstan (+996)",
            "us": "United States (+1)"
        }
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("Starting Marque Multi-Market Authentication API")
    logger.info("Supported markets: KG (Kyrgyzstan), US (United States)")
    
    # Verify database connections
    try:
        markets = auth_service.get_supported_markets()
        logger.info(f"Loaded {len(markets)} supported markets")
        for market in markets:
            logger.info(f"  - {market.market}: {market.country} ({market.currency})")
    except Exception as e:
        logger.error(f"Failed to load market configurations: {e}")
        raise

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("Shutting down Marque Multi-Market Authentication API")

if __name__ == "__main__":
    uvicorn.run(
        "src.app_01.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
