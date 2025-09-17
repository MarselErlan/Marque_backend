"""
FastAPI Dependencies
Dependency injection for authentication, market detection, and other cross-cutting concerns
"""

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, Optional
import jwt
from datetime import datetime

from ...core.config import get_settings, Market
from ...core.exceptions import create_token_error, create_market_error, ErrorCode
from ...core.container import get_container

# Security scheme
security = HTTPBearer()

async def get_market_from_request(request: Request) -> Market:
    """Extract market from request"""
    settings = get_settings()
    
    # 1. Check X-Market header
    market_header = request.headers.get("X-Market")
    if market_header:
        try:
            return Market(market_header.lower())
        except ValueError:
            pass
    
    # 2. Check phone number in request body (for auth endpoints)
    if request.url.path.startswith("/api/v1/auth") or request.url.path.startswith("/api/v1/phone"):
        try:
            # This would need proper body parsing
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
    return settings.default_market

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    market: Market = Depends(get_market_from_request)
) -> Dict[str, Any]:
    """Get current authenticated user"""
    settings = get_settings()
    
    try:
        # Verify JWT token
        payload = jwt.decode(
            credentials.credentials,
            settings.security.secret_key,
            algorithms=[settings.security.jwt_algorithm]
        )
        
        # Check token expiration
        exp = payload.get("exp")
        if exp and datetime.utcnow().timestamp() > exp:
            raise create_token_error(
                "Token has expired",
                ErrorCode.TOKEN_EXPIRED
            )
        
        # Extract user information
        user_id = payload.get("user_id")
        token_market = payload.get("market")
        
        if not user_id:
            raise create_token_error(
                "Invalid token: missing user_id",
                ErrorCode.TOKEN_INVALID
            )
        
        # Verify market matches
        if token_market != market.value:
            raise create_market_error(
                "Token market mismatch",
                ErrorCode.UNSUPPORTED_MARKET,
                {"token_market": token_market, "request_market": market.value}
            )
        
        # Get user from database
        container = get_container()
        from ...domain.repositories import RepositoryManager
        repo_manager = container.get(RepositoryManager)
        
        user_repo = await repo_manager.get_user_repository(market)
        user = await user_repo.get_by_id(user_id)
        
        if not user:
            raise create_token_error(
                "User not found",
                ErrorCode.TOKEN_INVALID
            )
        
        if not user.is_active:
            raise create_token_error(
                "User account is inactive",
                ErrorCode.ACCESS_DENIED
            )
        
        return {
            "id": user.id,
            "phone_number": user.phone_number,
            "full_name": user.full_name,
            "market": user.market,
            "language": user.language,
            "country": user.country,
            "is_verified": user.is_verified,
            "is_active": user.is_active
        }
        
    except jwt.ExpiredSignatureError:
        raise create_token_error(
            "Token has expired",
            ErrorCode.TOKEN_EXPIRED
        )
    except jwt.InvalidTokenError:
        raise create_token_error(
            "Invalid token",
            ErrorCode.TOKEN_INVALID
        )
    except Exception as e:
        raise create_token_error(
            f"Token verification failed: {str(e)}",
            ErrorCode.TOKEN_INVALID
        )

async def get_current_verified_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get current authenticated and verified user"""
    if not current_user.get("is_verified"):
        raise HTTPException(
            status_code=403,
            detail="Phone number verification required"
        )
    
    return current_user

async def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get current authenticated and active user"""
    if not current_user.get("is_active"):
        raise HTTPException(
            status_code=403,
            detail="User account is inactive"
        )
    
    return current_user

async def get_optional_user(
    request: Request,
    market: Market = Depends(get_market_from_request)
) -> Optional[Dict[str, Any]]:
    """Get user if authenticated, otherwise return None"""
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        token = auth_header.split(" ")[1]
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        
        return await get_current_user(credentials, market)
    except Exception:
        return None

def get_database_session(market: Market = Depends(get_market_from_request)):
    """Get database session for market"""
    container = get_container()
    from ...infrastructure.database.manager import DatabaseManager
    db_manager = container.get(DatabaseManager)
    
    return db_manager.get_session(market)

def get_user_repository(market: Market = Depends(get_market_from_request)):
    """Get user repository for market"""
    container = get_container()
    from ...domain.repositories import RepositoryManager
    repo_manager = container.get(RepositoryManager)
    
    return repo_manager.get_user_repository(market)

def get_phone_verification_repository(market: Market = Depends(get_market_from_request)):
    """Get phone verification repository for market"""
    container = get_container()
    from ...domain.repositories import RepositoryManager
    repo_manager = container.get(RepositoryManager)
    
    return repo_manager.get_phone_verification_repository(market)

def get_user_address_repository(market: Market = Depends(get_market_from_request)):
    """Get user address repository for market"""
    container = get_container()
    from ...domain.repositories import RepositoryManager
    repo_manager = container.get(RepositoryManager)
    
    return repo_manager.get_user_address_repository(market)

def get_user_payment_method_repository(market: Market = Depends(get_market_from_request)):
    """Get user payment method repository for market"""
    container = get_container()
    from ...domain.repositories import RepositoryManager
    repo_manager = container.get(RepositoryManager)
    
    return repo_manager.get_user_payment_method_repository(market)

def get_user_notification_repository(market: Market = Depends(get_market_from_request)):
    """Get user notification repository for market"""
    container = get_container()
    from ...domain.repositories import RepositoryManager
    repo_manager = container.get(RepositoryManager)
    
    return repo_manager.get_user_notification_repository(market)

# Service dependencies
def get_auth_service():
    """Get authentication service"""
    container = get_container()
    from ...application.services import AuthService
    return container.get(AuthService)

def get_user_service():
    """Get user service"""
    container = get_container()
    from ...application.services import UserService
    return container.get(UserService)

def get_phone_verification_service():
    """Get phone verification service"""
    container = get_container()
    from ...application.services import PhoneVerificationService
    return container.get(PhoneVerificationService)

def get_market_service():
    """Get market service"""
    container = get_container()
    from ...application.services import MarketService
    return container.get(MarketService)
