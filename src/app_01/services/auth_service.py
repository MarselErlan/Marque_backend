"""
Authentication Service
Business logic for phone number authentication with multi-market support
"""

from typing import Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import secrets
import jwt
import logging
import os

from ..db import (
    db_manager, Market, MarketConfig, detect_market_from_phone, 
    format_phone_for_market, get_market_config
)
from ..models.users.market_user import get_user_model, get_user_by_phone_with_market_detection
from ..models.users.market_phone_verification import create_verification_for_market, verify_code_for_market
from ..schemas.auth import (
    PhoneLoginRequest, VerifyCodeRequest, SendCodeResponse, VerifyCodeResponse,
    UserProfile, UpdateProfileRequest, VerifyTokenResponse, MarketInfo,
    UserSchema, MarketEnum
)
from ..models.admins.admin import Admin
import bcrypt



# Twilio imports
try:
    from twilio.rest import Client
    from twilio.base.exceptions import TwilioException
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    TwilioException = Exception

# JWT Configuration
SECRET_KEY = "your-secret-key-here"  # Should be in environment variables
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Rate limiting configuration
MAX_VERIFICATION_ATTEMPTS = 3
VERIFICATION_ATTEMPTS_WINDOW = 15  # minutes

# Twilio Configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_VERIFY_SERVICE_SID = os.getenv("TWILIO_VERIFY_SERVICE_SID")

# Initialize Twilio client
TWILIO_READY = False
twilio_client = None

if TWILIO_AVAILABLE and TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_VERIFY_SERVICE_SID:
    try:
        twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        TWILIO_READY = True
    except Exception as e:
        logging.warning(f"Twilio client initialization failed: {e}")

logger = logging.getLogger(__name__)

def create_admin(db: Session, username: str, password: str, full_name: str, is_super_admin: bool = False, admin_role: str = "order_management") -> Admin:
    """
    Creates a new admin user.
    """
    # Check if admin already exists
    existing_admin = db.query(Admin).filter(Admin.username == username).first()
    if existing_admin:
        raise ValueError("Admin with this username already exists")

    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Create new admin
    new_admin = Admin(
        username=username,
        hashed_password=hashed_password.decode('utf-8'),
        full_name=full_name,
        is_super_admin=is_super_admin,
        admin_role=admin_role
    )

    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    
    logger.info(f"✅ New admin created: {username}")
    
    return new_admin


class AuthService:
    """Authentication service for phone number authentication"""
    
    def __init__(self):
        self.rate_limit_store = {}  # In production, use Redis
    
    def send_verification_code(self, request: PhoneLoginRequest, x_market: Optional[str] = None) -> SendCodeResponse:
        """
        Send SMS verification code to phone number
        
        Args:
            request: Phone login request
            x_market: Optional market override header
            
        Returns:
            SendCodeResponse with verification details
            
        Raises:
            ValueError: If phone number format is invalid
            RateLimitError: If too many attempts in time window
        """
        try:
            # Detect market from phone number
            market = detect_market_from_phone(request.phone)
            
            # Override with header if provided
            if x_market:
                try:
                    market = Market(x_market.lower())
                except ValueError:
                    raise ValueError(f"Invalid market header: {x_market}")
            
            # Check rate limiting
            self._check_rate_limit(request.phone)
            
            # Get market configuration
            config = get_market_config(market)
            
            # Get user model and session for this market
            user_model = get_user_model(market)
            session_factory = db_manager.get_session_factory(market)
            
            with session_factory() as db:
                # Check if user exists
                user = user_model.get_by_phone(db, request.phone)
                
                # Send SMS via Twilio Verify (Twilio generates and stores the code)
                formatted_phone = format_phone_for_market(request.phone, market)
                sms_sent = self._send_sms_via_twilio_verify(request.phone)
                
                if not sms_sent:
                    # If Twilio fails, create local verification for demo
                    verification = create_verification_for_market(db, request.phone, user.id if user else None)
                    logger.warning(f"Twilio Verify failed. Demo code for {formatted_phone}: {verification.verification_code}")
                else:
                    logger.info(f"✅ SMS sent to {formatted_phone} via Twilio Verify")
                
                # Update rate limiting
                self._update_rate_limit(request.phone)
                
                return SendCodeResponse(
                    success=True,
                    message="Verification code sent successfully",
                    phone_number=formatted_phone,
                    market=market.value,
                    language=config["default_language"],
                    expires_in_minutes=10 if market == Market.KG else 15
                )
        
        except ValueError as e:
            logger.error(f"Phone validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to send verification code: {e}")
            raise RuntimeError(f"Failed to send verification code: {str(e)}")
    
    def verify_phone_code(self, request: VerifyCodeRequest, x_market: Optional[str] = None) -> VerifyCodeResponse:
        """
        Verify phone number with SMS code
        
        Args:
            request: Verify code request
            x_market: Optional market override header
            
        Returns:
            VerifyCodeResponse with authentication token
            
        Raises:
            ValueError: If phone number or code is invalid
            AuthenticationError: If verification fails
        """
        try:
            # Detect market from phone number
            market = detect_market_from_phone(request.phone)
            
            # Override with header if provided
            if x_market:
                try:
                    market = Market(x_market.lower())
                except ValueError:
                    raise ValueError(f"Invalid market header: {x_market}")
            
            # Get user model and session for this market
            user_model = get_user_model(market)
            session_factory = db_manager.get_session_factory(market)
            
            with session_factory() as db:
                # Verify the code via Twilio Verify
                if TWILIO_READY:
                    # Using Twilio Verify - codes are checked by Twilio
                    code_valid = self._verify_code_via_twilio_verify(request.phone, request.verification_code)
                    if not code_valid:
                        raise ValueError("Invalid or expired verification code")
                else:
                    # Demo mode - check local database
                    verification = verify_code_for_market(db, request.phone, request.verification_code)
                    if not verification:
                        raise ValueError("Invalid or expired verification code")
                
                # Check if user exists
                user = user_model.get_by_phone(db, request.phone)
                is_new_user = False
                
                if not user:
                    # Create new user
                    user = user_model.create_user(db, request.phone)
                    is_new_user = True
                    logger.info(f"✅ New user created: ID={user.id}, Phone={request.phone}")
                else:
                    # Existing user - check if previously verified
                    if user.is_verified:
                        logger.info(f"🔄 Existing verified user logging back in: ID={user.id}, Phone={request.phone}")
                    else:
                        logger.info(f"📱 First-time verification for user: ID={user.id}, Phone={request.phone}")
                
                # Mark user as verified and active, update last login
                user.is_verified = True
                user.is_active = True  # Set active when user logs in
                user.update_last_login()
                db.commit()
                
                # Create access token
                access_token = self._create_access_token(user.id, market.value)
                
                logger.info(f"✅ User authenticated successfully: ID={user.id}, Active={user.is_active}, Verified={user.is_verified}")
                
                user_data = UserSchema(
                    id=str(user.id),
                    name=user.display_name,
                    full_name=user.full_name,
                    phone=user.phone_number,
                    email=user.email,
                    is_active=user.is_active,
                    is_verified=user.is_verified,
                    market=MarketEnum(market.value)  # Add market to user schema
                )

                return VerifyCodeResponse(
                    success=True,
                    message="Phone number verified successfully",
                    access_token=access_token,
                    token_type="bearer",
                    expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                    user=user_data,
                    market=market.value,
                    is_new_user=is_new_user
                )
        
        except ValueError as e:
            logger.error(f"Verification error: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to verify code: {e}")
            raise RuntimeError(f"Failed to verify code: {str(e)}")
    
    def logout_user(self, user_id: int, market: str) -> bool:
        """
        Logout user by setting is_active to False
        
        Args:
            user_id: User ID
            market: User market
            
        Returns:
            True if successful
            
        Raises:
            ValueError: If market is invalid or user not found
        """
        try:
            market_enum = Market(market)
            user_model = get_user_model(market_enum)
            session_factory = db_manager.get_session_factory(market_enum)
            
            with session_factory() as db:
                user = db.query(user_model).filter(user_model.id == user_id).first()
                if not user:
                    raise ValueError(f"User not found with ID: {user_id}")
                
                # Set user as inactive
                user.is_active = False
                db.commit()
                
                logger.info(f"✅ User logged out: ID={user_id}, Market={market}, is_active=False")
                return True
        
        except ValueError as e:
            logger.error(f"Logout error: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to logout user: {e}")
            raise RuntimeError(f"Failed to logout user: {str(e)}")
    
    def get_user_profile(self, user_id: int, market: str) -> UserProfile:
        """
        Get user profile by ID and market
        
        Args:
            user_id: User ID
            market: User market
            
        Returns:
            UserProfile with user details
            
        Raises:
            ValueError: If market is invalid
            UserNotFoundError: If user doesn't exist
        """
        try:
            market_enum = Market(market)
            user_model = get_user_model(market_enum)
            session_factory = db_manager.get_session_factory(market_enum)
            
            with session_factory() as db:
                user = db.query(user_model).filter(user_model.id == user_id).first()
                if not user:
                    raise ValueError(f"User not found with ID: {user_id}")
                
                return UserProfile(
                    id=str(user.id),
                    phone_number=user.phone_number,
                    formatted_phone=user.formatted_phone,
                    name=user.display_name,
                    full_name=user.full_name,
                    profile_image_url=user.profile_image_url,
                    is_active=user.is_active,
                    is_verified=user.is_verified,
                    market=user.market,
                    language=user.language,
                    country=user.country,
                    currency=user.currency,
                    currency_code=user.currency_code,
                    last_login=user.last_login,
                    created_at=user.created_at
                )
        
        except ValueError as e:
            logger.error(f"Profile retrieval error: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to get user profile: {e}")
            raise RuntimeError(f"Failed to get user profile: {str(e)}")
    
    def update_user_profile(self, user_id: int, market: str, request: UpdateProfileRequest) -> UserProfile:
        """
        Update user profile
        
        Args:
            user_id: User ID
            market: User market
            request: Update profile request
            
        Returns:
            Updated UserProfile
            
        Raises:
            ValueError: If market is invalid or user not found
        """
        try:
            market_enum = Market(market)
            user_model = get_user_model(market_enum)
            session_factory = db_manager.get_session_factory(market_enum)
            
            with session_factory() as db:
                user = db.query(user_model).filter(user_model.id == user_id).first()
                if not user:
                    raise ValueError(f"User not found with ID: {user_id}")
                
                # Update fields
                if request.full_name is not None:
                    user.full_name = request.full_name
                if request.profile_image_url is not None:
                    user.profile_image_url = request.profile_image_url
                
                db.commit()
                db.refresh(user)
                
                return UserProfile(
                    id=str(user.id),
                    phone_number=user.phone_number,
                    formatted_phone=user.formatted_phone,
                    name=user.display_name,
                    full_name=user.full_name,
                    profile_image_url=user.profile_image_url,
                    is_active=user.is_active,
                    is_verified=user.is_verified,
                    market=user.market,
                    language=user.language,
                    country=user.country,
                    currency=user.currency,
                    currency_code=user.currency_code,
                    last_login=user.last_login,
                    created_at=user.created_at
                )
        
        except ValueError as e:
            logger.error(f"Profile update error: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to update user profile: {e}")
            raise RuntimeError(f"Failed to update user profile: {str(e)}")
    
    def verify_access_token(self, token: str) -> VerifyTokenResponse:
        """
        Verify JWT access token
        
        Args:
            token: JWT access token
            
        Returns:
            VerifyTokenResponse with token validation result
            
        Raises:
            ValueError: If token is invalid
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: int = payload.get("sub")
            market: str = payload.get("market")
            
            if user_id is None or market is None:
                raise ValueError("Invalid token payload")
            
            # Get user to verify they still exist
            market_enum = Market(market)
            user_model = get_user_model(market_enum)
            session_factory = db_manager.get_session_factory(market_enum)
            
            with session_factory() as db:
                user = db.query(user_model).filter(user_model.id == user_id).first()
                if not user:
                    raise ValueError("User not found")
                
                return VerifyTokenResponse(
                    valid=True,
                    user_id=user.id,
                    phone_number=user.phone_number,
                    formatted_phone=user.formatted_phone,
                    market=user.market,
                    currency=user.currency
                )
        
        except jwt.PyJWTError as e:
            logger.error(f"JWT validation error: {e}")
            raise ValueError("Invalid token")
        except ValueError as e:
            logger.error(f"Token verification error: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to verify token: {e}")
            raise RuntimeError(f"Failed to verify token: {str(e)}")
    
    def get_supported_markets(self) -> list[MarketInfo]:
        """
        Get list of supported markets
        
        Returns:
            List of MarketInfo objects
        """
        markets = []
        for market in Market:
            config = get_market_config(market)
            markets.append(MarketInfo(
                market=market.value,
                country=config["country"],
                currency=config["currency"],
                currency_code=config["currency_code"],
                language=config["default_language"],
                phone_prefix=config["phone_prefix"],
                phone_format=config["phone_format"]
            ))
        
        return markets
    
    def _create_access_token(self, user_id: int, market: str) -> str:
        """Create JWT access token"""
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {
            "sub": str(user_id),
            "market": market,
            "exp": expire
        }
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    def _generate_verification_code(self) -> str:
        """Generate a random 6-digit verification code"""
        import random
        return ''.join([str(random.randint(0, 9)) for _ in range(6)])
    
    def _check_rate_limit(self, phone_number: str) -> bool:
        """
        Check if phone number has exceeded rate limit
        
        Returns:
            True if within rate limit, raises ValueError if exceeded
        """
        current_time = datetime.utcnow()
        window_start = current_time - timedelta(minutes=VERIFICATION_ATTEMPTS_WINDOW)
        
        # Clean old attempts
        if phone_number in self.rate_limit_store:
            self.rate_limit_store[phone_number] = [
                attempt_time for attempt_time in self.rate_limit_store[phone_number]
                if attempt_time > window_start
            ]
        else:
            self.rate_limit_store[phone_number] = []
        
        # Check if limit exceeded
        if len(self.rate_limit_store[phone_number]) >= MAX_VERIFICATION_ATTEMPTS:
            raise ValueError(f"Too many verification attempts. Please wait {VERIFICATION_ATTEMPTS_WINDOW} minutes.")
        
        return True
    
    def _update_rate_limit(self, phone_number: str) -> None:
        """Update rate limit for phone number"""
        current_time = datetime.utcnow()
        
        if phone_number not in self.rate_limit_store:
            self.rate_limit_store[phone_number] = []
        
        self.rate_limit_store[phone_number].append(current_time)
    
    def _send_sms_via_twilio_verify(self, phone: str) -> bool:
        """
        Send SMS verification code via Twilio Verify
        
        Args:
            phone: Phone number to send to
            
        Returns:
            True if SMS sent successfully, False otherwise
        """
        if not TWILIO_READY:
            logger.info(f"📱 Twilio not configured - running in demo mode for {phone}")
            return False
        
        try:
            # Send SMS using Twilio Verify API
            verification = twilio_client.verify.v2.services(
                TWILIO_VERIFY_SERVICE_SID
            ).verifications.create(
                to=phone,
                channel='sms'
            )
            logger.info(f"✅ Twilio Verify SMS sent to {phone} - SID: {verification.sid}")
            return True
        except TwilioException as e:
            logger.error(f"❌ Twilio Verify failed: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error sending SMS: {e}")
            return False
    
    def _verify_code_via_twilio_verify(self, phone: str, code: str) -> bool:
        """
        Verify code via Twilio Verify
        
        Args:
            phone: Phone number
            code: Verification code to check
            
        Returns:
            True if code is valid, False otherwise
        """
        if not TWILIO_READY:
            logger.info(f"📱 Twilio not configured - skipping Twilio verification for {phone}")
            return False
        
        try:
            # Verify code using Twilio Verify API
            logger.info(f"🔍 Checking code for {phone} with Twilio Verify...")
            verification_check = twilio_client.verify.v2.services(
                TWILIO_VERIFY_SERVICE_SID
            ).verification_checks.create(
                to=phone,
                code=code
            )
            is_approved = verification_check.status == 'approved'
            if is_approved:
                logger.info(f"✅ Twilio Verify code APPROVED for {phone}")
            else:
                logger.warning(f"❌ Twilio Verify code REJECTED for {phone}: Status={verification_check.status}")
            return is_approved
        except TwilioException as e:
            logger.error(f"❌ Twilio Verify check FAILED for {phone}: {type(e).__name__}: {e}")
            # Important: return False, don't raise - let the caller handle it
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error verifying code for {phone}: {type(e).__name__}: {e}")
            return False

# Global service instance
auth_service = AuthService()
