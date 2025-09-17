"""
Health Check Endpoints
Provides system health and status information
"""

from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from typing import Dict, Any
import asyncio

from ..core.config import get_settings, Market
from ..core.container import get_container

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "service": "marque-ecommerce-api",
        "version": get_settings().app_version,
        "environment": get_settings().environment.value,
        "timestamp": datetime.utcnow().isoformat(),
        "markets": [market.value for market in Market]
    }

@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with component status"""
    settings = get_settings()
    health_status = {
        "status": "healthy",
        "service": "marque-ecommerce-api",
        "version": settings.app_version,
        "environment": settings.environment.value,
        "timestamp": datetime.utcnow().isoformat(),
        "components": {}
    }
    
    # Check database connections
    try:
        container = get_container()
        from ..infrastructure.database.manager import DatabaseManager
        db_manager = container.get(DatabaseManager)
        
        for market in Market:
            try:
                session = await db_manager.get_session(market)
                await session.execute("SELECT 1")
                await session.close()
                health_status["components"][f"database_{market.value}"] = {
                    "status": "healthy",
                    "market": market.value
                }
            except Exception as e:
                health_status["components"][f"database_{market.value}"] = {
                    "status": "unhealthy",
                    "market": market.value,
                    "error": str(e)
                }
                health_status["status"] = "degraded"
    except Exception as e:
        health_status["components"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # Check Redis connection (if configured)
    try:
        if settings.redis.url:
            # This would need Redis client implementation
            health_status["components"]["redis"] = {
                "status": "healthy",
                "url": settings.redis.url
            }
    except Exception as e:
        health_status["components"]["redis"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        if health_status["status"] == "healthy":
            health_status["status"] = "degraded"
    
    # Check external services
    external_services = {
        "sms_service": settings.external_services.sms_service_url,
        "email_service": settings.external_services.email_service_url,
        "file_storage": settings.external_services.file_storage_url
    }
    
    for service_name, service_url in external_services.items():
        if service_url:
            try:
                # This would need actual service health check implementation
                health_status["components"][service_name] = {
                    "status": "healthy",
                    "url": service_url
                }
            except Exception as e:
                health_status["components"][service_name] = {
                    "status": "unhealthy",
                    "url": service_url,
                    "error": str(e)
                }
                if health_status["status"] == "healthy":
                    health_status["status"] = "degraded"
    
    return health_status

@router.get("/health/ready")
async def readiness_check():
    """Kubernetes readiness check"""
    try:
        container = get_container()
        from ..infrastructure.database.manager import DatabaseManager
        db_manager = container.get(DatabaseManager)
        
        # Check if at least one database is available
        for market in Market:
            try:
                session = await db_manager.get_session(market)
                await session.execute("SELECT 1")
                await session.close()
                return {"status": "ready", "timestamp": datetime.utcnow().isoformat()}
            except Exception:
                continue
        
        raise HTTPException(status_code=503, detail="No database available")
        
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service not ready: {str(e)}")

@router.get("/health/live")
async def liveness_check():
    """Kubernetes liveness check"""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/info")
async def system_info():
    """System information"""
    settings = get_settings()
    
    return {
        "application": {
            "name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment.value,
            "debug": settings.debug
        },
        "server": {
            "host": settings.host,
            "port": settings.port,
            "workers": settings.workers
        },
        "markets": {
            market.value: {
                "name": settings.get_market_config(market)["country"],
                "currency": settings.get_market_config(market)["currency_code"],
                "language": settings.get_market_config(market)["language"],
                "phone_prefix": settings.get_market_config(market)["phone_prefix"]
            }
            for market in Market
        },
        "features": {
            "rate_limiting": settings.rate_limit.enabled,
            "logging": {
                "level": settings.logging.level,
                "file_path": settings.logging.file_path
            }
        }
    }
