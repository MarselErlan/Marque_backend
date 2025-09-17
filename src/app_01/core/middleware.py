"""
Custom Middleware Components
Handles request/response processing, logging, and cross-cutting concerns
"""

import time
import logging
import uuid
from typing import Callable, Optional
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .config import get_settings, Market
from .exceptions import BaseAppException, create_internal_error

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.settings = get_settings()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Log request
        start_time = time.time()
        logger.info(
            f"Request started - ID: {request_id}, "
            f"Method: {request.method}, "
            f"URL: {request.url}, "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"Request completed - ID: {request_id}, "
                f"Status: {response.status_code}, "
                f"Time: {process_time:.3f}s"
            )
            
            # Add headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            # Log error
            process_time = time.time() - start_time
            logger.error(
                f"Request failed - ID: {request_id}, "
                f"Error: {str(e)}, "
                f"Time: {process_time:.3f}s"
            )
            
            # Return error response
            if isinstance(e, BaseAppException):
                return JSONResponse(
                    status_code=e.status_code,
                    content=e.to_dict(),
                    headers={"X-Request-ID": request_id}
                )
            else:
                error = create_internal_error("Internal server error")
                return JSONResponse(
                    status_code=error.status_code,
                    content=error.to_dict(),
                    headers={"X-Request-ID": request_id}
                )

class MarketDetectionMiddleware(BaseHTTPMiddleware):
    """Middleware for detecting market from request"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.settings = get_settings()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Detect market from various sources
        market = self._detect_market(request)
        request.state.market = market
        
        # Add market info to request
        request.state.market_config = self.settings.get_market_config(market)
        
        response = await call_next(request)
        
        # Add market info to response headers
        response.headers["X-Market"] = market.value
        response.headers["X-Currency"] = self.settings.get_market_config(market)["currency_code"]
        response.headers["X-Language"] = self.settings.get_market_config(market)["language"]
        
        return response
    
    def _detect_market(self, request: Request) -> Market:
        """Detect market from request"""
        # 1. Check X-Market header
        market_header = request.headers.get("X-Market")
        if market_header:
            try:
                return Market(market_header.lower())
            except ValueError:
                pass
        
        # 2. Check phone number in request body (for auth endpoints)
        if request.url.path.startswith("/api/v1/auth"):
            try:
                # This would need to be implemented based on request body parsing
                # For now, we'll use a simple approach
                pass
            except Exception:
                pass
        
        # 3. Check domain or subdomain
        host = request.headers.get("host", "")
        if "kg" in host.lower() or "kyrgyzstan" in host.lower():
            return Market.KG
        elif "us" in host.lower() or "usa" in host.lower() or "america" in host.lower():
            return Market.US
        
        # 4. Default to configured default market
        return self.settings.default_market

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.settings = get_settings()
        self._rate_limit_store = {}  # In production, use Redis
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not self.settings.rate_limit.enabled:
            return await call_next(request)
        
        # Get client identifier
        client_id = self._get_client_id(request)
        
        # Check rate limit
        if not self._check_rate_limit(client_id, request):
            from .exceptions import create_rate_limit_error
            error = create_rate_limit_error("Rate limit exceeded")
            return JSONResponse(
                status_code=error.status_code,
                content=error.to_dict()
            )
        
        return await call_next(request)
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting"""
        # Use IP address as client identifier
        client_ip = request.client.host if request.client else "unknown"
        return f"rate_limit:{client_ip}"
    
    def _check_rate_limit(self, client_id: str, request: Request) -> bool:
        """Check if client is within rate limit"""
        import time
        
        current_time = int(time.time())
        
        # Get rate limit configuration based on endpoint
        if request.url.path.startswith("/api/v1/auth"):
            limit = self.settings.rate_limit.auth_limit
            window = self.settings.rate_limit.auth_window
        elif request.url.path.startswith("/api/v1/sms"):
            limit = self.settings.rate_limit.sms_limit
            window = self.settings.rate_limit.sms_window
        else:
            limit = self.settings.rate_limit.default_limit
            window = self.settings.rate_limit.default_window
        
        # Get or create rate limit entry
        if client_id not in self._rate_limit_store:
            self._rate_limit_store[client_id] = {
                "requests": [],
                "limit": limit,
                "window": window
            }
        
        entry = self._rate_limit_store[client_id]
        
        # Clean old requests
        entry["requests"] = [
            req_time for req_time in entry["requests"]
            if current_time - req_time < window
        ]
        
        # Check if limit exceeded
        if len(entry["requests"]) >= limit:
            return False
        
        # Add current request
        entry["requests"].append(current_time)
        return True

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.settings = get_settings()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Add CSP header in production (allow Swagger UI)
        if self.settings.is_production():
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "img-src 'self' data: https:; "
                "font-src 'self' data: https://cdn.jsdelivr.net; "
                "connect-src 'self' https://api.twilio.com https://verify.twilio.com;"
            )
        
        return response

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for handling exceptions"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.settings = get_settings()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except BaseAppException as e:
            # Handle application exceptions
            logger.error(f"Application error: {e.message}", exc_info=True)
            return JSONResponse(
                status_code=e.status_code,
                content=e.to_dict()
            )
        except HTTPException as e:
            # Handle FastAPI HTTP exceptions
            logger.error(f"HTTP error: {e.detail}")
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "error": "HTTP_ERROR",
                    "message": e.detail,
                    "status_code": e.status_code
                }
            )
        except Exception as e:
            # Handle unexpected exceptions
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            error = create_internal_error("Internal server error")
            return JSONResponse(
                status_code=error.status_code,
                content=error.to_dict()
            )

class CORSHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for CORS headers"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.settings = get_settings()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add CORS headers
        origin = request.headers.get("origin")
        if origin and self._is_allowed_origin(origin):
            response.headers["Access-Control-Allow-Origin"] = origin
        else:
            response.headers["Access-Control-Allow-Origin"] = "*"
        
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Market, X-Request-ID"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Max-Age"] = "86400"
        
        return response
    
    def _is_allowed_origin(self, origin: str) -> bool:
        """Check if origin is allowed"""
        # In production, implement proper origin checking
        return True

def setup_middleware(app: ASGIApp) -> ASGIApp:
    """Setup all middleware components"""
    # Add middleware in reverse order (last added is first executed)
    app.add_middleware(CORSHeadersMiddleware)
    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(MarketDetectionMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    
    return app
