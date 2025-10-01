"""
API v1 Routes
Main API endpoints organized by feature
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, Any

from ..dependencies import get_current_user, get_market_from_request
from ..schemas.auth import (
    PhoneLoginRequest, PhoneVerificationRequest, 
    UserProfileResponse, UserProfileUpdateRequest
)
from ...core.config import Market
from ...core.container import get_container
from ...application.services import (
    AuthService, UserService, PhoneVerificationService, MarketService
)

from ....routers.auth_router import router as auth_router
from ....routers.product_router import router as product_router
from ....routers.category_router import router as category_router
from ....routers.cart_router import router as cart_router
from ....routers.wishlist_router import router as wishlist_router

router = APIRouter()

# Authentication routes
@router.post("/auth/login")
async def login_with_phone(request: PhoneLoginRequest, market: Market = Depends(get_market_from_request)):
    """Login with phone number (sends verification code)"""
    container = get_container()
    auth_service = container.get(AuthService)
    
    return await auth_service.login_with_phone(request.phone, market)

@router.post("/auth/verify")
async def verify_phone_code(request: PhoneVerificationRequest, market: Market = Depends(get_market_from_request)):
    """Verify phone code and complete login"""
    container = get_container()
    auth_service = container.get(AuthService)
    
    return await auth_service.verify_and_login(request.phone, request.code, market)

@router.post("/auth/refresh")
async def refresh_token(request: Request):
    """Refresh access token"""
    container = get_container()
    auth_service = container.get(AuthService)
    
    # Extract refresh token from request
    body = await request.json()
    refresh_token = body.get("refresh_token")
    
    if not refresh_token:
        raise HTTPException(status_code=400, detail="Refresh token required")
    
    return await auth_service.refresh_token(refresh_token)

# User routes
@router.get("/users/profile", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: Dict[str, Any] = Depends(get_current_user),
    market: Market = Depends(get_market_from_request)
):
    """Get current user profile"""
    container = get_container()
    user_service = container.get(UserService)
    
    return await user_service.get_user_profile(current_user["id"], market)

@router.put("/users/profile")
async def update_user_profile(
    request: UserProfileUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    market: Market = Depends(get_market_from_request)
):
    """Update user profile"""
    container = get_container()
    user_service = container.get(UserService)
    
    updates = request.dict(exclude_unset=True)
    return await user_service.update_user_profile(current_user["id"], market, updates)

@router.delete("/users/profile")
async def deactivate_user(
    current_user: Dict[str, Any] = Depends(get_current_user),
    market: Market = Depends(get_market_from_request)
):
    """Deactivate user account"""
    container = get_container()
    user_service = container.get(UserService)
    
    return await user_service.deactivate_user(current_user["id"], market)

# Phone verification routes
@router.post("/phone/send-code")
async def send_verification_code(request: PhoneLoginRequest, market: Market = Depends(get_market_from_request)):
    """Send phone verification code"""
    container = get_container()
    phone_service = container.get(PhoneVerificationService)
    
    return await phone_service.send_verification_code(request.phone, market)

@router.post("/phone/verify")
async def verify_phone_code(request: PhoneVerificationRequest, market: Market = Depends(get_market_from_request)):
    """Verify phone code"""
    container = get_container()
    phone_service = container.get(PhoneVerificationService)
    
    return await phone_service.verify_code(request.phone, request.code, market)

# Market routes
@router.get("/markets")
async def get_supported_markets():
    """Get supported markets"""
    container = get_container()
    market_service = container.get(MarketService)
    
    return await market_service.get_supported_markets()

@router.post("/markets/detect")
async def detect_market(request: Request):
    """Detect market from phone number"""
    container = get_container()
    market_service = container.get(MarketService)
    
    body = await request.json()
    phone = body.get("phone")
    
    if not phone:
        raise HTTPException(status_code=400, detail="Phone number required")
    
    return await market_service.detect_market_from_phone(phone)

# User addresses routes
@router.get("/users/addresses")
async def get_user_addresses(
    current_user: Dict[str, Any] = Depends(get_current_user),
    market: Market = Depends(get_market_from_request)
):
    """Get user addresses"""
    container = get_container()
    from ...domain.repositories import RepositoryManager
    repo_manager = container.get(RepositoryManager)
    
    address_repo = await repo_manager.get_user_address_repository(market)
    addresses = await address_repo.get_user_addresses(current_user["id"], market)
    
    return {
        "success": True,
        "addresses": [
            {
                "id": addr.id,
                "title": addr.title,
                "full_address": addr.full_address,
                "is_default": addr.is_default,
                "created_at": addr.created_at.isoformat() if addr.created_at else None
            }
            for addr in addresses
        ]
    }

@router.post("/users/addresses")
async def create_user_address(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user),
    market: Market = Depends(get_market_from_request)
):
    """Create user address"""
    container = get_container()
    from ...domain.repositories import RepositoryManager
    repo_manager = container.get(RepositoryManager)
    
    body = await request.json()
    
    # This would need proper address model creation
    # address_data = {
    #     "user_id": current_user["id"],
    #     "market": market.value,
    #     **body
    # }
    # address = await address_repo.create(address_data)
    
    return {
        "success": True,
        "message": "Address created successfully",
        "address_id": 1  # Placeholder
    }

# User payment methods routes
@router.get("/users/payment-methods")
async def get_user_payment_methods(
    current_user: Dict[str, Any] = Depends(get_current_user),
    market: Market = Depends(get_market_from_request)
):
    """Get user payment methods"""
    container = get_container()
    from ...domain.repositories import RepositoryManager
    repo_manager = container.get(RepositoryManager)
    
    payment_repo = await repo_manager.get_user_payment_method_repository(market)
    payment_methods = await payment_repo.get_user_payment_methods(current_user["id"], market)
    
    return {
        "success": True,
        "payment_methods": [
            {
                "id": pm.id,
                "payment_type": pm.payment_type,
                "card_type": pm.card_type,
                "card_number_masked": pm.card_number_masked,
                "is_default": pm.is_default,
                "created_at": pm.created_at.isoformat() if pm.created_at else None
            }
            for pm in payment_methods
        ]
    }

# User notifications routes
@router.get("/users/notifications")
async def get_user_notifications(
    unread_only: bool = False,
    current_user: Dict[str, Any] = Depends(get_current_user),
    market: Market = Depends(get_market_from_request)
):
    """Get user notifications"""
    container = get_container()
    from ...domain.repositories import RepositoryManager
    repo_manager = container.get(RepositoryManager)
    
    notification_repo = await repo_manager.get_user_notification_repository(market)
    notifications = await notification_repo.get_user_notifications(current_user["id"], unread_only)
    
    return {
        "success": True,
        "notifications": [
            {
                "id": notif.id,
                "type": notif.notification_type,
                "title": notif.title,
                "message": notif.message,
                "is_read": notif.is_read,
                "created_at": notif.created_at.isoformat() if notif.created_at else None
            }
            for notif in notifications
        ]
    }

@router.put("/users/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    market: Market = Depends(get_market_from_request)
):
    """Mark notification as read"""
    container = get_container()
    from ...domain.repositories import RepositoryManager
    repo_manager = container.get(RepositoryManager)
    
    notification_repo = await repo_manager.get_user_notification_repository(market)
    success = await notification_repo.mark_as_read(notification_id, current_user["id"])
    
    return {
        "success": success,
        "message": "Notification marked as read" if success else "Failed to mark notification as read"
    }

router.include_router(auth_router, prefix="/auth", tags=["authentication"])
router.include_router(product_router, prefix="/products", tags=["products"])
router.include_router(category_router, prefix="/categories", tags=["categories"])
router.include_router(cart_router, prefix="/cart", tags=["cart"])
router.include_router(wishlist_router, prefix="/wishlist", tags=["wishlist"])