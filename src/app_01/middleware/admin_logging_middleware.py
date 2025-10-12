"""
Admin Logging Middleware
Automatically logs all admin actions and errors
"""

import time
import traceback
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from sqlalchemy.orm import Session
from ..utils.admin_logger import AdminLogger
from ..db import get_db
import logging

logger = logging.getLogger(__name__)


class AdminLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically log admin actions"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        # Only log admin routes
        if not request.url.path.startswith("/admin"):
            return await call_next(request)
        
        start_time = time.time()
        
        # Get request details
        method = request.method
        path = request.url.path
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        # Try to get admin ID from session (if authenticated)
        admin_id = getattr(request.state, "admin_id", None)
        
        try:
            # Process request
            response = await call_next(request)
            
            # Log successful operations
            duration = time.time() - start_time
            
            # Log to file (database logging happens in individual endpoints)
            logger.info(
                f"Admin Request: {method} {path} - "
                f"Status: {response.status_code} - "
                f"Duration: {duration:.2f}s - "
                f"IP: {ip_address} - "
                f"Admin: {admin_id or 'Not authenticated'}"
            )
            
            return response
            
        except Exception as error:
            # Log error
            duration = time.time() - start_time
            
            logger.error(
                f"Admin Error: {method} {path} - "
                f"Duration: {duration:.2f}s - "
                f"IP: {ip_address} - "
                f"Admin: {admin_id or 'Not authenticated'} - "
                f"Error: {str(error)}\n"
                f"Traceback: {traceback.format_exc()}"
            )
            
            # Re-raise the exception
            raise

