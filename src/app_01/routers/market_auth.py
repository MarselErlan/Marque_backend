"""
Market-Aware Phone Number Authentication API Endpoints
FastAPI routes for phone number-based authentication with multi-market support
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator
from typing import Optional
import jwt
from datetime import datetime, timedelta

from ..db.market_db import (
    db_manager, Market, MarketConfig, detect_market_from_phone, 
    format_phone_for_market, get_market_config
)
from ..models.users.market_user import get_user_model, get_user_by_phone_with_market_detection
from ..models.users.market_phone_verification import create_verification_for_market, verify_code_for_market
from ..config import settings

router = APIRouter(prefix="/auth", tags=["market-authentication"])

# JWT Configuration
SECRET_KEY = "your-secret-key-here"  # Should be in environment variables
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class PhoneLoginRequest(BaseModel):
    """Phone number login request"""
    phone_number: str
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        """Validate phone number format"""
        # Remove spaces and validate format
        clean_phone = v.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        
        # Check if it's a valid KG or US phone number
        if clean_phone.startswith("+996") and len(clean_phone) == 13:
            return clean_phone
        elif clean_phone.startswith("+1") and len(clean_phone) == 12:
            return clean_phone
        else:
            raise ValueError("Phone number must be in format +996XXXXXXXXX (KG) or +1XXXXXXXXXX (US)")

class VerifyCodeRequest(BaseModel):
    """Phone verification code request"""
    phone_number: str
    verification_code: str
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        clean_phone = v.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        
        if clean_phone.startswith("+996") and len(clean_phone) == 13:
            return clean_phone
        elif clean_phone.startswith("+1") and len(clean_phone) == 12:
            return clean_phone
        else:
            raise ValueError("Phone number must be in format +996XXXXXXXXX (KG) or +1XXXXXXXXXX (US)")

class VerifyCodeResponse(BaseModel):
    """Phone verification response"""
    success: bool
    message: str
    access_token: Optional[str] = None
    user_id: Optional[int] = None
    market: Optional[str] = None
    is_new_user: Optional[bool] = None

class UserProfile(BaseModel):
    """User profile response"""
    id: int
    phone_number: str
    formatted_phone: str
    full_name: Optional[str]
    profile_image_url: Optional[str]
    is_verified: bool
    market: str
    language: str
    country: str
    currency: str
    currency_code: str
    last_login: Optional[datetime]
    created_at: datetime

class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    token_type: str
    expires_in: int
    market: str

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: str = Header(None)):
    """Verify JWT token"""
    try:
        if not credentials or not credentials.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization header",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token = credentials.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        market: str = payload.get("market")
        
        if user_id is None or market is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user_id, market
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(user_id: int, market: str = Depends(verify_token)):
    """Get current authenticated user"""
    try:
        market_enum = Market(market)
        user_model = get_user_model(market_enum)
        session_factory = db_manager.get_session_factory(market_enum)
        
        db = session_factory()
        try:
            user = db.query(user_model).filter(user_model.id == user_id).first()
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
            return user
        finally:
            db.close()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid market"
        )

@router.post("/send-code", response_model=dict)
async def send_verification_code(
    request: PhoneLoginRequest,
    x_market: Optional[str] = Header(None)
):
    """Send SMS verification code to phone number"""
    try:
        # Detect market from phone number
        market = detect_market_from_phone(request.phone_number)
        
        # Override with header if provided
        if x_market:
            try:
                market = Market(x_market.lower())
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid market header: {x_market}"
                )
        
        # Get market configuration
        config = get_market_config(market)
        
        # Get user model and session for this market
        user_model = get_user_model(market)
        session_factory = db_manager.get_session_factory(market)
        
        db = session_factory()
        try:
            # Check if user exists
            user = user_model.get_by_phone(db, request.phone_number)
            
            # Create verification code
            verification = create_verification_for_market(db, request.phone_number, user.id if user else None)
            
            # In a real application, you would send SMS here
            # For demo purposes, we'll just return the code
            formatted_phone = format_phone_for_market(request.phone_number, market)
            print(f"SMS sent to {formatted_phone}: Your verification code is {verification.verification_code}")
            
            return {
                "success": True,
                "message": "Verification code sent successfully",
                "phone_number": formatted_phone,
                "market": market.value,
                "language": config["default_language"],
                "demo_code": verification.verification_code  # Remove in production
            }
        finally:
            db.close()
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send verification code: {str(e)}"
        )

@router.post("/verify-code", response_model=VerifyCodeResponse)
async def verify_phone_code(
    request: VerifyCodeRequest,
    x_market: Optional[str] = Header(None)
):
    """Verify phone number with SMS code"""
    try:
        # Detect market from phone number
        market = detect_market_from_phone(request.phone_number)
        
        # Override with header if provided
        if x_market:
            try:
                market = Market(x_market.lower())
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid market header: {x_market}"
                )
        
        # Get user model and session for this market
        user_model = get_user_model(market)
        session_factory = db_manager.get_session_factory(market)
        
        db = session_factory()
        try:
            # Verify the code
            verification = verify_code_for_market(db, request.phone_number, request.verification_code)
            
            if not verification:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid or expired verification code"
                )
            
            # Check if user exists
            user = user_model.get_by_phone(db, request.phone_number)
            is_new_user = False
            
            if not user:
                # Create new user
                user = user_model.create_user(db, request.phone_number)
                is_new_user = True
            
            # Mark user as verified and update last login
            user.is_verified = True
            user.update_last_login()
            db.commit()
            
            # Create access token
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": str(user.id), "market": market.value}, 
                expires_delta=access_token_expires
            )
            
            return VerifyCodeResponse(
                success=True,
                message="Phone number verified successfully",
                access_token=access_token,
                user_id=user.id,
                market=market.value,
                is_new_user=is_new_user
            )
        finally:
            db.close()
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify code: {str(e)}"
        )

@router.get("/profile", response_model=UserProfile)
async def get_user_profile(
    current_user = Depends(get_current_user)
):
    """Get current user profile"""
    return UserProfile(
        id=current_user.id,
        phone_number=current_user.phone_number,
        formatted_phone=current_user.formatted_phone,
        full_name=current_user.full_name,
        profile_image_url=current_user.profile_image_url,
        is_verified=current_user.is_verified,
        market=current_user.market,
        language=current_user.language,
        country=current_user.country,
        currency=current_user.currency,
        currency_code=current_user.currency_code,
        last_login=current_user.last_login,
        created_at=current_user.created_at
    )

@router.put("/profile", response_model=UserProfile)
async def update_user_profile(
    full_name: Optional[str] = None,
    profile_image_url: Optional[str] = None,
    current_user = Depends(get_current_user)
):
    """Update user profile"""
    try:
        # Get database session for the user's market
        market = Market(current_user.market)
        session_factory = db_manager.get_session_factory(market)
        
        db = session_factory()
        try:
            # Get user from database
            user_model = get_user_model(market)
            user = db.query(user_model).filter(user_model.id == current_user.id).first()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Update fields
            if full_name is not None:
                user.full_name = full_name
            if profile_image_url is not None:
                user.profile_image_url = profile_image_url
            
            db.commit()
            db.refresh(user)
            
            return UserProfile(
                id=user.id,
                phone_number=user.phone_number,
                formatted_phone=user.formatted_phone,
                full_name=user.full_name,
                profile_image_url=user.profile_image_url,
                is_verified=user.is_verified,
                market=user.market,
                language=user.language,
                country=user.country,
                currency=user.currency,
                currency_code=user.currency_code,
                last_login=user.last_login,
                created_at=user.created_at
            )
        finally:
            db.close()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )

@router.post("/logout", response_model=dict)
async def logout():
    """Logout user (client should discard token)"""
    return {
        "success": True,
        "message": "Logged out successfully"
    }

@router.get("/verify-token")
async def verify_access_token(
    current_user = Depends(get_current_user)
):
    """Verify if access token is valid"""
    return {
        "valid": True,
        "user_id": current_user.id,
        "phone_number": current_user.phone_number,
        "formatted_phone": current_user.formatted_phone,
        "market": current_user.market,
        "currency": current_user.currency
    }

@router.get("/markets")
async def get_supported_markets():
    """Get supported markets and their configurations"""
    markets = []
    for market in Market:
        config = get_market_config(market)
        markets.append({
            "market": market.value,
            "country": config["country"],
            "currency": config["currency"],
            "currency_code": config["currency_code"],
            "language": config["default_language"],
            "phone_prefix": config["phone_prefix"],
            "phone_format": config["phone_format"]
        })
    
    return {
        "supported_markets": markets,
        "default_market": Market.KG.value
    }
