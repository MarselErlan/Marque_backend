#!/usr/bin/env python3
"""
Marque Production API - Phone Authentication v2
Production-ready phone authentication API with enhanced endpoints and Twilio integration
"""

from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, validator, Field
import logging
import uvicorn
from datetime import datetime, timedelta
import secrets
import jwt
import re
import os
from typing import Optional, List
from enum import Enum

# Setup logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Twilio Verify integration
try:
    from twilio.rest import Client
    from twilio.base.exceptions import TwilioException
    TWILIO_AVAILABLE = True
    logger.info("✅ Twilio library imported successfully")
except ImportError as e:
    TWILIO_AVAILABLE = False
    logger.error(f"❌ Failed to import Twilio library: {e}")
except Exception as e:
    TWILIO_AVAILABLE = False
    logger.error(f"❌ Unexpected error importing Twilio: {e}")

# Import new architecture components
from src.app_01.core.config import get_settings, Market, MarketConfig
from src.app_01.core.exceptions import create_market_error, ErrorCode
from src.app_01.core.middleware import setup_middleware

# Get settings
settings = get_settings()

# Twilio Configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_VERIFY_SERVICE_SID = os.getenv("TWILIO_VERIFY_SERVICE_SID")

# Initialize Twilio client
if TWILIO_AVAILABLE and TWILIO_ACCOUNT_SID:
    try:
        twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        # Test the client by getting account info
        account = twilio_client.api.accounts(TWILIO_ACCOUNT_SID).fetch()
        TWILIO_READY = True
        logger.info(f"✅ Twilio Verify service initialized for account: {account.friendly_name}")
    except Exception as e:
        TWILIO_READY = False
        logger.error(f"❌ Failed to initialize Twilio: {e}")
        logger.error(f"❌ TWILIO_ACCOUNT_SID: {TWILIO_ACCOUNT_SID[:10]}...")
        logger.error(f"❌ TWILIO_AUTH_TOKEN: {TWILIO_AUTH_TOKEN[:10] if TWILIO_AUTH_TOKEN else 'None'}...")
else:
    TWILIO_READY = False
    if not TWILIO_AVAILABLE:
        logger.warning("⚠️ Twilio library not available")
    if not TWILIO_ACCOUNT_SID:
        logger.warning("⚠️ TWILIO_ACCOUNT_SID not set")

# Debug logging
    logger.info(f"🔍 Twilio Config Debug (v1.1.0):")
logger.info(f"  - TWILIO_ACCOUNT_SID: {'✅ Set' if TWILIO_ACCOUNT_SID else '❌ Missing'}")
logger.info(f"  - TWILIO_AUTH_TOKEN: {'✅ Set' if TWILIO_AUTH_TOKEN else '❌ Missing'}")
logger.info(f"  - TWILIO_VERIFY_SERVICE_SID: {'✅ Set' if TWILIO_VERIFY_SERVICE_SID else '❌ Missing'}")
logger.info(f"  - TWILIO_AVAILABLE: {TWILIO_AVAILABLE}")
logger.info(f"  - TWILIO_READY: {TWILIO_READY}")

# Create FastAPI app
app = FastAPI(
    title="Marque API",
    description="Marque E-commerce Platform - Phone Authentication & User Management",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Setup middleware
app = setup_middleware(app)

# Security
security = HTTPBearer()
SECRET_KEY = settings.security.secret_key
ALGORITHM = settings.security.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.security.access_token_expire_minutes

# Market detection function
def detect_market_from_phone(phone_number: str) -> str:
    """Detect market from phone number"""
    if phone_number.startswith("+996"):
        return "kg"
    elif phone_number.startswith("+1"):
        return "us"
    else:
        raise ValueError(f"Cannot detect market for phone number: {phone_number}")

# Import database components (avoid table conflicts)
from src.app_01.db.market_db import Market, MarketDatabaseManager, detect_market_from_phone as db_detect_market

# Initialize database manager
db_manager = MarketDatabaseManager()

# Import database models directly to avoid table conflicts
def get_user_model_for_market(market: Market):
    """Get user model for specific market without importing the module"""
    if market == Market.KG:
        # Import KG model directly
        from src.app_01.models.users.market_user import UserKG
        return UserKG
    elif market == Market.US:
        # Import US model directly
        from src.app_01.models.users.market_user import UserUS
        return UserUS
    else:
        raise ValueError(f"Unsupported market: {market}")

# In-memory storage (fallback for demo)
users = {}
sessions = {}

# Enums
class AuthStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"

class UserRole(str, Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"
    VENDOR = "vendor"

# Pydantic Models
class PhoneRequest(BaseModel):
    """Phone number request model"""
    phone: str = Field(..., description="Phone number (+1 for US or +996 for KG)", example="+13473926894")
    
    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number format for US or KG"""
        clean_phone = re.sub(r'\D', '', v)
        
        # US number validation
        if v.startswith('+1') or (len(clean_phone) == 10) or (len(clean_phone) == 11 and clean_phone.startswith('1')):
            if len(clean_phone) == 10:
                return f"+1{clean_phone}"
            elif len(clean_phone) == 11 and clean_phone.startswith('1'):
                return f"+{clean_phone}"
            elif v.startswith('+1') and len(clean_phone) == 11:
                return v
            else:
                raise ValueError("Phone number must be a valid US number (10 digits or +1XXXXXXXXXX)")
        
        # KG number validation
        elif v.startswith('+996') or (len(clean_phone) == 12 and clean_phone.startswith('996')):
            if v.startswith('+996') and len(clean_phone) == 12:
                return v
            elif len(clean_phone) == 12 and clean_phone.startswith('996'):
                return f"+{clean_phone}"
            else:
                raise ValueError("Phone number must be a valid KG number (+996XXXXXXXXX)")
        
        else:
            raise ValueError("Phone number must be a valid US number (+1XXXXXXXXXX) or KG number (+996XXXXXXXXX)")

class VerificationRequest(BaseModel):
    """SMS verification request model"""
    phone: str = Field(..., description="Phone number (+1 for US or +996 for KG)", example="+13473926894")
    code: str = Field(..., description="6-digit verification code", example="123456", min_length=6, max_length=6)
    
    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number format for US or KG"""
        clean_phone = re.sub(r'\D', '', v)
        
        # US number validation
        if v.startswith('+1') or (len(clean_phone) == 10) or (len(clean_phone) == 11 and clean_phone.startswith('1')):
            if len(clean_phone) == 10:
                return f"+1{clean_phone}"
            elif len(clean_phone) == 11 and clean_phone.startswith('1'):
                return f"+{clean_phone}"
            elif v.startswith('+1') and len(clean_phone) == 11:
                return v
            else:
                raise ValueError("Phone number must be a valid US number (10 digits or +1XXXXXXXXXX)")
        
        # KG number validation
        elif v.startswith('+996') or (len(clean_phone) == 12 and clean_phone.startswith('996')):
            if v.startswith('+996') and len(clean_phone) == 12:
                return v
            elif len(clean_phone) == 12 and clean_phone.startswith('996'):
                return f"+{clean_phone}"
            else:
                raise ValueError("Phone number must be a valid KG number (+996XXXXXXXXX)")
        
        else:
            raise ValueError("Phone number must be a valid US number (+1XXXXXXXXXX) or KG number (+996XXXXXXXXX)")

class AuthResponse(BaseModel):
    """Authentication response model"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    data: Optional[dict] = Field(None, description="Response data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

class UserProfile(BaseModel):
    """User profile model"""
    id: str = Field(..., description="Unique user ID")
    phone: str = Field(..., description="User's phone number")
    is_verified: bool = Field(..., description="Whether user is verified")
    role: UserRole = Field(default=UserRole.CUSTOMER, description="User role")
    created_at: datetime = Field(..., description="Account creation timestamp")
    last_login: datetime = Field(..., description="Last login timestamp")
    metadata: Optional[dict] = Field(None, description="Additional user data")

class SessionInfo(BaseModel):
    """Session information model"""
    session_id: str = Field(..., description="Session ID")
    user_id: str = Field(..., description="User ID")
    created_at: datetime = Field(..., description="Session creation time")
    expires_at: datetime = Field(..., description="Session expiration time")
    is_active: bool = Field(..., description="Whether session is active")

# Utility Functions
def create_access_token(user_id: str, role: str = "customer", market: str = None) -> str:
    """Create JWT access token"""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": user_id,
        "role": role,
        "market": market,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

def send_verification_via_twilio_verify(phone: str) -> bool:
    """Send verification code via Twilio Verify"""
    if not TWILIO_READY:
        logger.info(f"📱 DEMO Verify SMS to {phone}")
        return True
    
    try:
        verification = twilio_client.verify.v2.services(TWILIO_VERIFY_SERVICE_SID).verifications.create(
            to=phone,
            channel='sms'
        )
        logger.info(f"✅ Twilio Verify SMS sent to {phone} - SID: {verification.sid}")
        return True
    except TwilioException as e:
        logger.error(f"❌ Twilio Verify failed: {e}")
        return False

def verify_code_via_twilio_verify(phone: str, code: str) -> bool:
    """Verify code via Twilio Verify"""
    if not TWILIO_READY:
        return code.isdigit() and len(code) == 6
    
    try:
        verification_check = twilio_client.verify.v2.services(TWILIO_VERIFY_SERVICE_SID).verification_checks.create(
            to=phone,
            code=code
        )
        return verification_check.status == 'approved'
    except TwilioException as e:
        logger.error(f"❌ Twilio Verify check failed: {e}")
        return False

def format_us_phone(phone: str) -> str:
    """Format US phone number for display"""
    clean_phone = re.sub(r'\D', '', phone)
    if len(clean_phone) == 11 and clean_phone.startswith('1'):
        clean_phone = clean_phone[1:]
    
    if len(clean_phone) == 10:
        return f"+1 ({clean_phone[:3]}) {clean_phone[3:6]}-{clean_phone[6:]}"
    return phone

# API Endpoints

@app.get("/", tags=["Root"])
async def root():
    """API root endpoint with information"""
    return {
        "name": "Marque API",
        "version": "1.0.1",
        "description": "Marque E-commerce Platform - Phone Authentication & User Management",
        "documentation": "/docs",
        "health": "/health",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "marque-api",
        "version": "1.0.1",
        "environment": settings.environment.value,
        "sms_provider": "Twilio Verify" if TWILIO_READY else "Demo",
        "sms_configured": TWILIO_READY,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/debug/env")
async def debug_env():
    """Debug endpoint to check environment variables"""
    return {
        "TWILIO_ACCOUNT_SID": "✅ Set" if os.getenv("TWILIO_ACCOUNT_SID") else "❌ Missing",
        "TWILIO_AUTH_TOKEN": "✅ Set" if os.getenv("TWILIO_AUTH_TOKEN") else "❌ Missing", 
        "TWILIO_VERIFY_SERVICE_SID": "✅ Set" if os.getenv("TWILIO_VERIFY_SERVICE_SID") else "❌ Missing",
        "TWILIO_READY": TWILIO_READY,
        "TWILIO_AVAILABLE": TWILIO_AVAILABLE
    }

# Authentication Endpoints
@app.post("/api/v1/auth/send-verification", 
          response_model=AuthResponse,
          tags=["Authentication"],
          summary="Send SMS Verification Code",
          description="Send a 6-digit verification code to the provided phone number (+1 US or +996 KG)")
async def send_verification_code(request: PhoneRequest):
    """Send SMS verification code to phone number"""
    try:
        phone = request.phone
        
        # Detect market from phone number
        try:
            market = db_detect_market(phone)
            logger.info(f"🌍 Detected market: {market.value} for phone: {phone}")
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid phone number format: {str(e)}"
            )
        
        # Send verification via Twilio Verify
        sms_sent = send_verification_via_twilio_verify(phone)
        
        if not sms_sent:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send verification code"
            )
        
        return AuthResponse(
            success=True,
            message="Verification code sent successfully",
            data={
                "phone": phone,
                "market": market.value,
                "expires_in_minutes": 10,
                "sms_provider": "Twilio Verify" if TWILIO_READY else "Demo"
            }
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to send verification code: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification code"
        )

@app.post("/api/v1/auth/verify-code",
          response_model=AuthResponse,
          tags=["Authentication"],
          summary="Verify SMS Code",
          description="Verify the 6-digit SMS code and authenticate user")
async def verify_phone_code(request: VerificationRequest):
    """Verify phone number with SMS code"""
    try:
        phone = request.phone
        code = request.code
        
        # Detect market from phone number
        try:
            market = db_detect_market(phone)
            logger.info(f"🌍 Detected market: {market.value} for phone: {phone}")
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid phone number format: {str(e)}"
            )
        
        # Verify code via Twilio Verify
        is_valid = verify_code_via_twilio_verify(phone, code)
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification code"
            )
        
        # Get database session for the detected market
        session_factory = db_manager.get_session_factory(market)
        
        with session_factory() as db:
            try:
                # Import models dynamically to avoid table conflicts
                if market == Market.KG:
                    from src.app_01.models.users.market_user import UserKG as UserModel
                elif market == Market.US:
                    from src.app_01.models.users.market_user import UserUS as UserModel
                else:
                    raise ValueError(f"Unsupported market: {market}")
                
                # Check if user exists in database
                user = UserModel.get_by_phone(db, phone)
                is_new_user = False
                
                if not user:
                    # Create new user in the correct market database
                    user = UserModel.create_user(db, phone)
                    is_new_user = True
                    logger.info(f"✅ Created new user in {market.value} database: {user.id}")
                else:
                    # Update existing user
                    user.is_verified = True
                    user.update_last_login()
                    db.commit()
                    logger.info(f"✅ Updated existing user in {market.value} database: {user.id}")
                
                # Create access token with market info
                user_id = str(user.id)
                access_token = create_access_token(user_id, "customer", market.value)
                
            except Exception as db_error:
                logger.error(f"Database error: {db_error}")
                # Fallback to in-memory storage if database fails
                user_id = f"user_{phone}"
                is_new_user = user_id not in users
                
                if is_new_user:
                    users[user_id] = {
                        "id": user_id,
                        "phone": phone,
                        "market": market.value,
                        "is_verified": True,
                        "role": "customer",
                        "created_at": datetime.utcnow().isoformat(),
                        "last_login": datetime.utcnow().isoformat(),
                        "metadata": {}
                    }
                    logger.info(f"✅ Created new user in memory for {market.value} market: {user_id}")
                else:
                    users[user_id]["last_login"] = datetime.utcnow().isoformat()
                    users[user_id]["is_verified"] = True
                    users[user_id]["market"] = market.value
                    logger.info(f"✅ Updated existing user in memory for {market.value} market: {user_id}")
                
                # Create access token with market info
                access_token = create_access_token(user_id, "customer", market.value)
        
        # Create session (still in-memory for now, can be moved to database later)
        session_id = secrets.token_urlsafe(32)
        sessions[session_id] = {
            "session_id": session_id,
            "user_id": user_id,
            "market": market.value,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            "is_active": True
        }
        
        # Prepare user data for response
        if 'user' in locals() and hasattr(user, 'id'):
            # User was created/updated in database
            user_data = {
                "id": str(user.id),
                "phone": user.phone_number,
                "is_verified": user.is_verified,
                "role": "customer",
                "is_new_user": is_new_user,
                "market": market.value,
                "language": user.language,
                "country": user.country
            }
        else:
            # Fallback to in-memory user data
            user_data = {
                "id": user_id,
                "phone": phone,
                "is_verified": True,
                "role": "customer",
                "is_new_user": is_new_user,
                "market": market.value
            }
        
        return AuthResponse(
            success=True,
            message="Phone number verified successfully",
            data={
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in_minutes": ACCESS_TOKEN_EXPIRE_MINUTES,
                "user": user_data,
                "session_id": session_id,
                "market": market.value
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to verify code: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify code"
        )

# User Management Endpoints
@app.get("/api/v1/users/profile",
         response_model=AuthResponse,
         tags=["User Management"],
         summary="Get User Profile",
         description="Get current authenticated user's profile")
async def get_user_profile(token_data: dict = Depends(verify_token)):
    """Get current user profile"""
    try:
        user_id = token_data.get("sub")
        
        if user_id not in users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user_data = users[user_id]
        profile = UserProfile(
            id=user_data["id"],
            phone=format_us_phone(user_data["phone"]),
            is_verified=user_data["is_verified"],
            role=UserRole(user_data["role"]),
            created_at=datetime.fromisoformat(user_data["created_at"]),
            last_login=datetime.fromisoformat(user_data["last_login"]),
            metadata=user_data.get("metadata", {})
        )
        
        return AuthResponse(
            success=True,
            message="Profile retrieved successfully",
            data={"profile": profile.dict()}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get profile"
        )

class ProfileUpdateRequest(BaseModel):
    """Profile update request model"""
    metadata: dict = Field(..., description="User metadata to update")

@app.put("/api/v1/users/profile",
         response_model=AuthResponse,
         tags=["User Management"],
         summary="Update User Profile",
         description="Update current user's profile information")
async def update_user_profile(
    request: ProfileUpdateRequest,
    token_data: dict = Depends(verify_token)
):
    """Update user profile"""
    try:
        user_id = token_data.get("sub")
        
        if user_id not in users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update metadata
        users[user_id]["metadata"].update(request.metadata)
        
        return AuthResponse(
            success=True,
            message="Profile updated successfully",
            data={
                "user_id": user_id,
                "updated_metadata": users[user_id]["metadata"]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )

# Session Management
@app.post("/api/v1/auth/logout",
          response_model=AuthResponse,
          tags=["Authentication"],
          summary="Logout User",
          description="Logout current user and invalidate session")
async def logout(token_data: dict = Depends(verify_token)):
    """Logout user"""
    try:
        user_id = token_data.get("sub")
        
        # Deactivate all sessions for user
        for session_id, session in sessions.items():
            if session["user_id"] == user_id:
                session["is_active"] = False
        
        return AuthResponse(
            success=True,
            message="Logged out successfully",
            data={"user_id": user_id}
        )
        
    except Exception as e:
        logger.error(f"Failed to logout: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to logout"
        )

@app.get("/api/v1/auth/sessions",
         response_model=AuthResponse,
         tags=["Authentication"],
         summary="Get User Sessions",
         description="Get all active sessions for current user")
async def get_user_sessions(token_data: dict = Depends(verify_token)):
    """Get user sessions"""
    try:
        user_id = token_data.get("sub")
        
        user_sessions = []
        for session_id, session in sessions.items():
            if session["user_id"] == user_id and session["is_active"]:
                session_info = SessionInfo(
                    session_id=session["session_id"],
                    user_id=session["user_id"],
                    created_at=session["created_at"],
                    expires_at=session["expires_at"],
                    is_active=session["is_active"]
                )
                user_sessions.append(session_info.dict())
        
        return AuthResponse(
            success=True,
            message="Sessions retrieved successfully",
            data={"sessions": user_sessions, "count": len(user_sessions)}
        )
        
    except Exception as e:
        logger.error(f"Failed to get sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get sessions"
        )

# Admin Endpoints (for future use)
@app.get("/api/v1/admin/users",
         response_model=AuthResponse,
         tags=["Admin"],
         summary="Get All Users (Admin)",
         description="Get list of all users (admin only)")
async def get_all_users(token_data: dict = Depends(verify_token)):
    """Get all users (admin only)"""
    try:
        user_role = token_data.get("role")
        if user_role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        user_list = []
        for user_id, user_data in users.items():
            user_list.append({
                "id": user_data["id"],
                "phone": format_us_phone(user_data["phone"]),
                "is_verified": user_data["is_verified"],
                "role": user_data["role"],
                "created_at": user_data["created_at"],
                "last_login": user_data["last_login"]
            })
        
        return AuthResponse(
            success=True,
            message="Users retrieved successfully",
            data={"users": user_list, "count": len(user_list)}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get users"
        )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("🚀 Starting Marque Production API")
    logger.info("📱 Phone Authentication with Twilio Verify")
    logger.info(f"🌍 Environment: {settings.environment.value}")
    logger.info(f"📞 SMS Provider: {'Twilio Verify' if TWILIO_READY else 'Demo Mode'}")
    
    if TWILIO_READY:
        logger.info(f"🔗 Verify Service SID: {TWILIO_VERIFY_SERVICE_SID}")
    
    logger.info("✅ API ready for production use")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("🛑 Shutting down Marque Production API")

if __name__ == "__main__":
    # Railway provides PORT environment variable
    port = int(os.getenv("PORT", 8004))
    uvicorn.run(
        "marque_api_production:app",
        host="0.0.0.0",  # Railway requires 0.0.0.0
        port=port,
        reload=False,  # Disable reload in production
        log_level="info"
    )
