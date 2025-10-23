"""
FastAPI Authentication Router
Endpoints for phone number authentication with multi-market support
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging

from ..services.auth_service import auth_service
from ..schemas.auth import (
    PhoneLoginRequest, VerifyCodeRequest, SendCodeResponse, VerifyCodeResponse,
    UserProfile, UpdateProfileRequest, UpdateProfileResponse, LogoutResponse,
    VerifyTokenResponse, SupportedMarketsResponse, ErrorResponse, ValidationErrorResponse
)

# Setup logging
logger = logging.getLogger(__name__)

# Router setup
router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer(auto_error=False)

# Custom exceptions
class AuthenticationError(HTTPException):
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )

class ValidationError(HTTPException):
    def __init__(self, detail: str = "Validation failed"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )

class RateLimitError(HTTPException):
    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail
        )

def get_current_user_from_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get current user from JWT token"""
    if not credentials:
        raise AuthenticationError("Missing authorization header")
    
    try:
        # Verify token and get user info
        token_response = auth_service.verify_access_token(credentials.credentials)
        return token_response
    except ValueError as e:
        logger.error(f"Token verification failed: {e}")
        raise AuthenticationError("Invalid token")

async def _send_verification_code_handler(
    request: PhoneLoginRequest,
    request_obj: Request,
    x_market: Optional[str] = None
):
    """Internal handler for sending verification code"""
    try:
        logger.info(f"Sending verification code to {request.phone}")
        
        # Get client IP for rate limiting
        client_ip = request_obj.client.host
        
        # Send verification code
        response = auth_service.send_verification_code(request, x_market)
        
        logger.info(f"Verification code sent successfully to {response.phone_number}")
        return response
        
    except ValueError as e:
        logger.warning(f"Validation error for {request.phone}: {e}")
        raise ValidationError(str(e))
    except RuntimeError as e:
        logger.error(f"Service error for {request.phone}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error for {request.phone}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/send-verification", response_model=SendCodeResponse, responses={
    422: {"model": ValidationErrorResponse},
    429: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def send_verification_code(
    request: PhoneLoginRequest,
    request_obj: Request,
    x_market: Optional[str] = Header(None, description="Market override (kg/us)")
):
    """
    Send SMS verification code to phone number
    
    - **phone**: Phone number in international format (+996XXXXXXXXX for KG, +1XXXXXXXXXX for US)
    - **x_market**: Optional market override header
    
    Returns verification code details and market information.
    """
    return await _send_verification_code_handler(request, request_obj, x_market)

@router.post("/send-code", response_model=SendCodeResponse, responses={
    422: {"model": ValidationErrorResponse},
    429: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def send_code(
    request: PhoneLoginRequest,
    request_obj: Request,
    x_market: Optional[str] = Header(None, description="Market override (kg/us)")
):
    """
    Send SMS verification code to phone number (alias for /send-verification)
    
    - **phone**: Phone number in international format (+996XXXXXXXXX for KG, +1XXXXXXXXXX for US)
    - **x_market**: Optional market override header
    
    Returns verification code details and market information.
    """
    return await _send_verification_code_handler(request, request_obj, x_market)

@router.post("/verify-code", response_model=VerifyCodeResponse, responses={
    400: {"model": ErrorResponse},
    422: {"model": ValidationErrorResponse},
    500: {"model": ErrorResponse}
})
async def verify_phone_code(
    request: VerifyCodeRequest,
    x_market: Optional[str] = Header(None, description="Market override (kg/us)")
):
    """
    Verify phone number with SMS code
    
    - **phone_number**: Phone number in international format
    - **verification_code**: SMS verification code (4-8 digits)
    - **x_market**: Optional market override header
    
    Returns authentication token and user information.
    """
    try:
        logger.info(f"Verifying code for {request.phone}")
        
        # Verify phone code
        response = auth_service.verify_phone_code(request, x_market)
        
        logger.info(f"Phone verification successful for {request.phone}, user_id: {response.user.id}")
        return response
        
    except ValueError as e:
        logger.warning(f"Verification error for {request.phone}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RuntimeError as e:
        logger.error(f"Service error for {request.phone}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error for {request.phone}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/profile", response_model=UserProfile, responses={
    401: {"model": ErrorResponse},
    404: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def get_user_profile(
    current_user: VerifyTokenResponse = Depends(get_current_user_from_token)
):
    """
    Get current user profile
    
    Requires valid JWT token in Authorization header.
    
    Returns user profile information including market-specific details.
    """
    try:
        logger.info(f"Getting profile for user_id: {current_user.user_id}")
        
        # Get user profile
        profile = auth_service.get_user_profile(current_user.user_id, current_user.market)
        
        logger.info(f"Profile retrieved successfully for user_id: {current_user.user_id}")
        return profile
        
    except ValueError as e:
        logger.warning(f"Profile retrieval error for user_id {current_user.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except RuntimeError as e:
        logger.error(f"Service error for user_id {current_user.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error for user_id {current_user.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/profile", response_model=UpdateProfileResponse, responses={
    400: {"model": ValidationErrorResponse},
    401: {"model": ErrorResponse},
    404: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def update_user_profile(
    request: UpdateProfileRequest,
    current_user: VerifyTokenResponse = Depends(get_current_user_from_token)
):
    """
    Update user profile
    
    - **full_name**: Optional full name update
    - **profile_image_url**: Optional profile image URL update
    
    Requires valid JWT token in Authorization header.
    """
    try:
        logger.info(f"Updating profile for user_id: {current_user.user_id}")
        
        # Update user profile
        updated_profile = auth_service.update_user_profile(
            current_user.user_id, 
            current_user.market, 
            request
        )
        
        logger.info(f"Profile updated successfully for user_id: {current_user.user_id}")
        return UpdateProfileResponse(
            success=True,
            message="Profile updated successfully",
            user=updated_profile
        )
        
    except ValueError as e:
        logger.warning(f"Profile update error for user_id {current_user.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RuntimeError as e:
        logger.error(f"Service error for user_id {current_user.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error for user_id {current_user.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/logout", response_model=LogoutResponse)
async def logout(
    current_user: VerifyTokenResponse = Depends(get_current_user_from_token)
):
    """
    Logout user
    
    Sets user's is_active status to False in the database.
    Client should also discard the token.
    """
    try:
        logger.info(f"User logout request: user_id={current_user.user_id}, market={current_user.market}")
        
        # Call auth service to handle logout
        auth_service.logout_user(current_user.user_id, current_user.market)
        
        logger.info(f"✅ User logged out successfully: user_id={current_user.user_id}")
        return LogoutResponse(
            success=True,
            message="Logged out successfully. User is now inactive."
        )
    except Exception as e:
        logger.error(f"Logout error for user {current_user.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

@router.get("/verify-token", response_model=VerifyTokenResponse, responses={
    401: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def verify_access_token(
    current_user: VerifyTokenResponse = Depends(get_current_user_from_token)
):
    """
    Verify if access token is valid
    
    Requires valid JWT token in Authorization header.
    
    Returns token validation result and user information.
    """
    try:
        logger.info(f"Token verification requested for user_id: {current_user.user_id}")
        
        # Token is already verified by the dependency
        return current_user
        
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/markets", response_model=SupportedMarketsResponse)
async def get_supported_markets():
    """
    Get supported markets and their configurations
    
    Returns list of supported markets with their specific configurations
    including currency, language, phone format, etc.
    """
    try:
        logger.info("Getting supported markets")
        
        # Get supported markets
        markets = auth_service.get_supported_markets()
        
        return SupportedMarketsResponse(
            supported_markets=markets,
            default_market="kg"
        )
        
    except Exception as e:
        logger.error(f"Error getting supported markets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/health")
async def health_check():
    """
    Health check endpoint for authentication service
    
    Returns service health status.
    """
    return {
        "status": "healthy",
        "service": "authentication",
        "version": "1.0.0",
        "markets": ["kg", "us"]
    }
