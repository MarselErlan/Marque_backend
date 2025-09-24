"""
Main FastAPI Application
Multi-market phone authentication system
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import uvicorn

from .routers.auth_router import router as auth_router
from .routers.product_router import router as product_router
from .routers.category_router import router as category_router
from .routers.cart_router import router as cart_router
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
