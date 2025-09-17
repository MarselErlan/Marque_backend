#!/usr/bin/env python3
"""
Migration from simple_main.py to Enhanced Architecture
This script helps migrate from the simple FastAPI app to the new clean architecture
"""

import os
import sys
from pathlib import Path

def create_migration_guide():
    """Create a step-by-step migration guide"""
    
    migration_steps = """
# 🔄 Migration Guide: simple_main.py → Enhanced Architecture

## 📋 Current Status
- ✅ `simple_main.py` is running and working
- ✅ New architecture components are implemented
- ✅ Core systems tested and working

## 🎯 Migration Options

### Option 1: Gradual Migration (Recommended)
1. Keep `simple_main.py` running for development
2. Gradually migrate endpoints to new architecture
3. Test new architecture components
4. Switch to `main_enhanced.py` when ready

### Option 2: Direct Migration
1. Stop `simple_main.py`
2. Start `main_enhanced.py`
3. Test all functionality
4. Update any missing features

## 🚀 Quick Start with New Architecture

### Step 1: Test New Architecture
```bash
# Test core components
python -c "from src.app_01.core.config import get_settings; print('✅ Config working')"

# Test dependency injection
python -c "from src.app_01.core.container import get_container; print('✅ DI working')"

# Test exception handling
python -c "from src.app_01.core.exceptions import create_user_error; print('✅ Exceptions working')"
```

### Step 2: Start Enhanced Application
```bash
# Stop simple_main.py (Ctrl+C)
# Start enhanced application
python src/app_01/main_enhanced.py
```

### Step 3: Test Endpoints
```bash
# Health check
curl http://127.0.0.1:8000/health

# Market info
curl http://127.0.0.1:8000/markets

# Phone validation
curl -X POST http://127.0.0.1:8000/validate-phone \\
  -H "Content-Type: application/json" \\
  -d '{"phone": "+996700123456"}'
```

## 🔧 Missing Components to Implement

### 1. Database Manager
- Complete async database manager
- Market-specific session handling

### 2. Repository Implementations
- Concrete repository classes
- Database operations

### 3. External Services
- SMS service integration
- Email service integration
- File storage service

### 4. JWT Service
- Token creation and validation
- Refresh token handling

## 📊 Comparison: Simple vs Enhanced

| Feature | simple_main.py | main_enhanced.py |
|---------|----------------|------------------|
| **Architecture** | Monolithic | Clean Architecture |
| **Configuration** | Manual | Structured Config |
| **Error Handling** | Basic | Custom Exceptions |
| **Dependencies** | Tight Coupling | Dependency Injection |
| **Testing** | Difficult | Easy with DI |
| **Scalability** | Limited | Enterprise-Ready |
| **Maintainability** | Low | High |

## 🎯 Recommendation

**Keep both applications running:**

1. **Development**: Use `simple_main.py` for quick testing
2. **Production**: Use `main_enhanced.py` for full features
3. **Gradual Migration**: Move features one by one to new architecture

This approach allows you to:
- ✅ Keep current functionality working
- ✅ Test new architecture components
- ✅ Migrate gradually without breaking changes
- ✅ Have a fallback if issues arise

## 🚀 Next Steps

1. **Test Enhanced Architecture**: Verify all components work
2. **Implement Missing Services**: Add database manager, repositories
3. **Migrate Endpoints**: Move endpoints from simple to enhanced
4. **Add Advanced Features**: Rate limiting, caching, monitoring
5. **Production Deployment**: Use enhanced architecture for production
"""
    
    return migration_steps

def create_enhanced_simple_main():
    """Create an enhanced version of simple_main.py using new architecture"""
    
    enhanced_code = '''#!/usr/bin/env python3
"""
Enhanced Simple Main - Bridge between simple_main.py and new architecture
Uses new architecture components while maintaining simple_main.py interface
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
import uvicorn
from datetime import datetime

# Import new architecture components
from src.app_01.core.config import get_settings, Market, MarketConfig
from src.app_01.core.exceptions import create_market_error, ErrorCode
from src.app_01.core.middleware import setup_middleware

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get settings from new architecture
settings = get_settings()

# Create FastAPI app with new architecture
app = FastAPI(
    title=settings.app_name,
    description="Multi-market phone authentication system for KG and US markets",
    version=settings.app_version,
    docs_url="/docs" if settings.is_development() else None,
    redoc_url="/redoc" if settings.is_development() else None
)

# Setup middleware from new architecture
app = setup_middleware(app)

# Pydantic model for phone validation
class PhoneValidationRequest(BaseModel):
    phone: str

# Health check endpoint
@app.get("/health")
async def health_check():
    """Application health check"""
    return {
        "status": "healthy",
        "service": "marque-auth-api",
        "version": settings.app_version,
        "environment": settings.environment.value,
        "markets": [market.value for market in Market],
        "timestamp": datetime.now().isoformat()
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment.value,
        "docs": "/docs" if settings.is_development() else "Documentation not available in production",
        "health": "/health",
        "markets": {
            market.value: {
                "name": MarketConfig.get_config(market)["country"],
                "currency": MarketConfig.get_config(market)["currency_code"],
                "language": MarketConfig.get_config(market)["language"]
            }
            for market in Market
        },
        "timestamp": datetime.now().isoformat()
    }

# Market detection endpoint
@app.get("/api/v1/markets")
async def get_markets():
    """Get supported markets"""
    markets = []
    for market in Market:
        config = MarketConfig.get_config(market)
        markets.append({
            "code": market.value,
            "name": config["country"],
            "phone_prefix": config["phone_prefix"],
            "language": config["language"],
            "currency": config["currency"],
            "currency_code": config["currency_code"]
        })
    
    return {
        "success": True,
        "markets": markets
    }

# Phone validation endpoint
@app.post("/api/v1/validate-phone")
async def validate_phone(request: PhoneValidationRequest):
    """Validate phone number and detect market"""
    try:
        phone = request.phone
        
        # Use new architecture market detection
        if phone.startswith("+996"):
            market = Market.KG
        elif phone.startswith("+1"):
            market = Market.US
        else:
            raise create_market_error(
                "Unsupported phone number format",
                ErrorCode.MARKET_NOT_DETECTED,
                {"phone": phone}
            )
        
        config = MarketConfig.get_config(market)
        
        return {
            "success": True,
            "phone": phone,
            "market": market.value,
            "country": config["country"],
            "language": config["language"],
            "currency": config["currency"],
            "currency_code": config["currency_code"],
            "valid": True
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Database status endpoint
@app.get("/api/v1/database-status")
async def database_status():
    """Check database connection status"""
    return {
        "success": True,
        "databases": {
            "kg": {
                "configured": bool(settings.database.url_kg),
                "url": settings.database.url_kg[:50] + "..." if settings.database.url_kg else None
            },
            "us": {
                "configured": bool(settings.database.url_us),
                "url": settings.database.url_us[:50] + "..." if settings.database.url_us else None
            }
        }
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info(f"Starting {settings.app_name}")
    logger.info(f"Environment: {settings.environment.value}")
    logger.info(f"Supported markets: {settings.supported_markets}")
    
    # Check database configurations
    if settings.database.url_kg:
        logger.info("✅ KG database configured")
    else:
        logger.warning("⚠️ KG database not configured")
    
    if settings.database.url_us:
        logger.info("✅ US database configured")
    else:
        logger.warning("⚠️ US database not configured")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info(f"Shutting down {settings.app_name}")

if __name__ == "__main__":
    uvicorn.run(
        "enhanced_simple_main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development(),
        log_level=settings.logging.level.lower()
    )
'''
    
    return enhanced_code

if __name__ == "__main__":
    print("🔄 Migration Guide Created!")
    print(create_migration_guide())
    
    print("\n🚀 Creating enhanced_simple_main.py...")
    enhanced_code = create_enhanced_simple_main()
    
    with open("enhanced_simple_main.py", "w") as f:
        f.write(enhanced_code)
    
    print("✅ enhanced_simple_main.py created!")
    print("\n📋 Next Steps:")
    print("1. Test enhanced_simple_main.py")
    print("2. Compare with simple_main.py")
    print("3. Gradually migrate to full architecture")
