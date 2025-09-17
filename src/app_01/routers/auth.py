"""
Phone Number Authentication API Endpoints
FastAPI routes for phone number-based authentication
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator
from typing import Optional
import secrets
import jwt
from datetime import datetime, timedelta

from ..db import get_db
from ..models import User, PhoneVerification
from ..config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

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
        # Remove spaces and validate Kyrgyzstan format
        clean_phone = v.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        if not clean_phone.startswith("+996") or len(clean_phone) != 13:
            raise ValueError("Phone number must be in format +996XXXXXXXXX")
        return clean_phone

class VerifyCodeRequest(BaseModel):
    """Phone verification code request"""
    phone_number: str
    verification_code: str
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        clean_phone = v.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        if not clean_phone.startswith("+996") or len(clean_phone) != 13:
            raise ValueError("Phone number must be in format +996XXXXXXXXX")
        return clean_phone

class VerifyCodeResponse(BaseModel):
    """Phone verification response"""
    success: bool
    message: str
    access_token: Optional[str] = None
    user_id: Optional[int] = None
    is_new_user: Optional[bool] = None

class UserProfile(BaseModel):
    """User profile response"""
    id: int
    phone_number: str
    full_name: Optional[str]
    profile_image_url: Optional[str]
    is_verified: bool
    last_login: Optional[datetime]
    created_at: datetime

class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    token_type: str
    expires_in: int

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

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(user_id: int = Depends(verify_token), db: Session = Depends(get_db)):
    """Get current authenticated user"""
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user

@router.post("/send-code", response_model=dict)
async def send_verification_code(
    request: PhoneLoginRequest,
    db: Session = Depends(get_db)
):
    """Send SMS verification code to phone number"""
    try:
        # Check if user exists
        user = User.get_by_phone(db, request.phone_number)
        
        # Create verification code
        verification = PhoneVerification.create_verification(
            db, request.phone_number, user.id if user else None
        )
        
        # In a real application, you would send SMS here
        # For demo purposes, we'll just return the code
        print(f"SMS sent to {request.phone_number}: Your verification code is {verification.verification_code}")
        
        return {
            "success": True,
            "message": "Verification code sent successfully",
            "phone_number": request.phone_number,
            "demo_code": verification.verification_code  # Remove in production
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send verification code: {str(e)}"
        )

@router.post("/verify-code", response_model=VerifyCodeResponse)
async def verify_phone_code(
    request: VerifyCodeRequest,
    db: Session = Depends(get_db)
):
    """Verify phone number with SMS code"""
    try:
        # Verify the code
        verification = PhoneVerification.verify_code(
            db, request.phone_number, request.verification_code
        )
        
        if not verification:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification code"
            )
        
        # Check if user exists
        user = User.get_by_phone(db, request.phone_number)
        is_new_user = False
        
        if not user:
            # Create new user
            user = User.create_user(db, request.phone_number)
            is_new_user = True
        
        # Mark user as verified and update last login
        user.is_verified = True
        user.update_last_login()
        db.commit()
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        
        return VerifyCodeResponse(
            success=True,
            message="Phone number verified successfully",
            access_token=access_token,
            user_id=user.id,
            is_new_user=is_new_user
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify code: {str(e)}"
        )

@router.get("/profile", response_model=UserProfile)
async def get_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user profile"""
    return UserProfile(
        id=current_user.id,
        phone_number=current_user.phone_number,
        full_name=current_user.full_name,
        profile_image_url=current_user.profile_image_url,
        is_verified=current_user.is_verified,
        last_login=current_user.last_login,
        created_at=current_user.created_at
    )

@router.put("/profile", response_model=UserProfile)
async def update_user_profile(
    full_name: Optional[str] = None,
    profile_image_url: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    try:
        if full_name is not None:
            current_user.full_name = full_name
        if profile_image_url is not None:
            current_user.profile_image_url = profile_image_url
        
        db.commit()
        db.refresh(current_user)
        
        return UserProfile(
            id=current_user.id,
            phone_number=current_user.phone_number,
            full_name=current_user.full_name,
            profile_image_url=current_user.profile_image_url,
            is_verified=current_user.is_verified,
            last_login=current_user.last_login,
            created_at=current_user.created_at
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )

@router.post("/logout", response_model=dict)
async def logout(
    current_user: User = Depends(get_current_user)
):
    """Logout user (client should discard token)"""
    return {
        "success": True,
        "message": "Logged out successfully"
    }

@router.get("/verify-token")
async def verify_access_token(
    current_user: User = Depends(get_current_user)
):
    """Verify if access token is valid"""
    return {
        "valid": True,
        "user_id": current_user.id,
        "phone_number": current_user.phone_number
    }
