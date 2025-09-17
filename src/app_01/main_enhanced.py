"""
Enhanced FastAPI Application with Clean Architecture
Multi-market e-commerce backend with proper separation of concerns
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Core imports
from .core.config import get_settings, Market
from .core.middleware import setup_middleware
from .core.container import get_container, configure_services
from .core.exceptions import BaseAppException, create_internal_error

# API imports
from .presentation.api.v1.routes import router as api_v1_router
from .presentation.api.health import router as health_router

# Setup logging
logging.basicConfig(
    level=get_settings().logging.level,
    format=get_settings().logging.format
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting Marque E-commerce API")
    logger.info(f"Environment: {get_settings().environment.value}")
    logger.info(f"Supported markets: {get_settings().supported_markets}")
    
    # Configure services
    container = get_container()
    configure_services(container)
    logger.info("✅ Services configured successfully")
    
    # Verify database connections
    try:
        from .infrastructure.database.manager import DatabaseManager
        db_manager = container.get(DatabaseManager)
        
        for market in Market:
            # Test database connection
            session = await db_manager.get_session(market)
            await session.execute("SELECT 1")
            await session.close()
            logger.info(f"✅ {market.value.upper()} database connected")
        
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Marque E-commerce API")
    
    # Cleanup services
    try:
        from .domain.repositories import RepositoryManager
        repo_manager = container.get(RepositoryManager)
        await repo_manager.cleanup()
        logger.info("✅ Services cleaned up successfully")
    except Exception as e:
        logger.error(f"⚠️ Service cleanup failed: {e}")

# Create FastAPI application
app = FastAPI(
    title=get_settings().app_name,
    description="Multi-market e-commerce backend for Marque fashion platform",
    version=get_settings().app_version,
    docs_url="/docs" if get_settings().is_development() else None,
    redoc_url="/redoc" if get_settings().is_development() else None,
    lifespan=lifespan
)

# Setup middleware
app = setup_middleware(app)

# Include routers
app.include_router(health_router, tags=["Health"])
app.include_router(api_v1_router, prefix="/api/v1", tags=["API v1"])

# Global exception handlers
@app.exception_handler(BaseAppException)
async def app_exception_handler(request: Request, exc: BaseAppException):
    """Handle application exceptions"""
    logger.error(f"Application error: {exc.message}", exc_info=True)
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(),
        headers={"X-Request-ID": getattr(request.state, "request_id", None)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    error = create_internal_error("Internal server error")
    return JSONResponse(
        status_code=error.status_code,
        content=error.to_dict(),
        headers={"X-Request-ID": getattr(request.state, "request_id", None)}
    )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    settings = get_settings()
    return {
        "message": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment.value,
        "docs": "/docs" if settings.is_development() else "Documentation not available in production",
        "health": "/health",
        "markets": {
            market.value: {
                "name": settings.get_market_config(market)["country"],
                "currency": settings.get_market_config(market)["currency_code"],
                "language": settings.get_market_config(market)["language"]
            }
            for market in Market
        }
    }

# Market detection endpoint
@app.get("/markets")
async def get_markets():
    """Get supported markets information"""
    from .application.services import MarketService
    container = get_container()
    market_service = MarketService()
    return await market_service.get_supported_markets()

# Phone validation endpoint
@app.post("/validate-phone")
async def validate_phone(request: Request):
    """Validate phone number and detect market"""
    from .application.services import MarketService
    from pydantic import BaseModel
    
    class PhoneRequest(BaseModel):
        phone: str
    
    try:
        body = await request.json()
        phone_request = PhoneRequest(**body)
        
        market_service = MarketService()
        return await market_service.detect_market_from_phone(phone_request.phone)
        
    except Exception as e:
        logger.error(f"Phone validation error: {e}")
        error = create_internal_error("Phone validation failed")
        return JSONResponse(
            status_code=error.status_code,
            content=error.to_dict()
        )

if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    uvicorn.run(
        "src.app_01.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development(),
        log_level=settings.logging.level.lower(),
        workers=settings.workers if settings.is_production() else 1
    )
