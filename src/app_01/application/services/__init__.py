"""
Application Service Layer
Business logic and use case implementations
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import secrets
import hashlib

from ..core.config import Market, get_settings
from ..core.exceptions import (
    create_user_error, create_phone_verification_error, create_market_error,
    create_validation_error, ErrorCode
)
from ..domain.repositories import (
    UserRepository, PhoneVerificationRepository, UserAddressRepository,
    UserPaymentMethodRepository, UserNotificationRepository
)

class BaseService(ABC):
    """Base service class"""
    
    def __init__(self):
        self.settings = get_settings()

class UserService(BaseService):
    """User management service"""
    
    def __init__(
        self,
        user_repository: UserRepository,
        phone_verification_repository: PhoneVerificationRepository,
        notification_repository: UserNotificationRepository
    ):
        super().__init__()
        self.user_repository = user_repository
        self.phone_verification_repository = phone_verification_repository
        self.notification_repository = notification_repository
    
    async def register_user(self, phone: str, market: Market, full_name: Optional[str] = None) -> Dict[str, Any]:
        """Register new user with phone verification"""
        # Check if user already exists
        existing_user = await self.user_repository.get_by_phone(phone, market)
        if existing_user:
            raise create_user_error(
                "User already exists with this phone number",
                ErrorCode.USER_ALREADY_EXISTS,
                {"phone": phone, "market": market.value}
            )
        
        # Create user
        user_data = {
            "phone_number": phone,
            "market": market.value,
            "language": self.settings.get_market_config(market)["language"],
            "country": self.settings.get_market_config(market)["country"],
            "is_active": True,
            "is_verified": False,
            "created_at": datetime.utcnow()
        }
        
        if full_name:
            user_data["full_name"] = full_name
        
        # This would need to be implemented based on your user model
        # user = await self.user_repository.create(user_data)
        
        return {
            "success": True,
            "message": "User registered successfully",
            "user_id": 1,  # Placeholder
            "phone": phone,
            "market": market.value,
            "verification_required": True
        }
    
    async def get_user_profile(self, user_id: int, market: Market) -> Dict[str, Any]:
        """Get user profile"""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise create_user_error(
                "User not found",
                ErrorCode.USER_NOT_FOUND,
                {"user_id": user_id}
            )
        
        return {
            "success": True,
            "user": {
                "id": user.id,
                "phone_number": user.phone_number,
                "full_name": user.full_name,
                "market": user.market,
                "language": user.language,
                "country": user.country,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_login": user.last_login.isoformat() if user.last_login else None
            }
        }
    
    async def update_user_profile(self, user_id: int, market: Market, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile"""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise create_user_error(
                "User not found",
                ErrorCode.USER_NOT_FOUND,
                {"user_id": user_id}
            )
        
        # Update user fields
        for field, value in updates.items():
            if hasattr(user, field) and field not in ["id", "created_at", "market"]:
                setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        updated_user = await self.user_repository.update(user)
        
        return {
            "success": True,
            "message": "Profile updated successfully",
            "user": {
                "id": updated_user.id,
                "phone_number": updated_user.phone_number,
                "full_name": updated_user.full_name,
                "market": updated_user.market,
                "language": updated_user.language,
                "country": updated_user.country,
                "is_active": updated_user.is_active,
                "is_verified": updated_user.is_verified,
                "updated_at": updated_user.updated_at.isoformat() if updated_user.updated_at else None
            }
        }
    
    async def deactivate_user(self, user_id: int, market: Market) -> Dict[str, Any]:
        """Deactivate user account"""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise create_user_error(
                "User not found",
                ErrorCode.USER_NOT_FOUND,
                {"user_id": user_id}
            )
        
        user.is_active = False
        user.updated_at = datetime.utcnow()
        await self.user_repository.update(user)
        
        return {
            "success": True,
            "message": "User account deactivated successfully"
        }

class PhoneVerificationService(BaseService):
    """Phone verification service"""
    
    def __init__(
        self,
        phone_verification_repository: PhoneVerificationRepository,
        user_repository: UserRepository,
        sms_service: 'SMSService'
    ):
        super().__init__()
        self.phone_verification_repository = phone_verification_repository
        self.user_repository = user_repository
        self.sms_service = sms_service
    
    async def send_verification_code(self, phone: str, market: Market, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Send SMS verification code"""
        # Check for existing active verification
        existing_verification = await self.phone_verification_repository.get_active_verification(phone, market)
        if existing_verification:
            # Check if we can resend (rate limiting)
            time_since_creation = datetime.utcnow() - existing_verification.created_at
            if time_since_creation < timedelta(minutes=1):
                raise create_phone_verification_error(
                    "Please wait before requesting another code",
                    ErrorCode.VERIFICATION_LIMIT_EXCEEDED,
                    {"retry_after": 60 - time_since_creation.seconds}
                )
        
        # Generate verification code
        code_length = self.settings.get_market_config(market)["verification_code_length"]
        verification_code = self._generate_verification_code(code_length)
        
        # Create verification record
        expiry_minutes = self.settings.get_market_config(market)["sms_expiry_minutes"]
        expires_at = datetime.utcnow() + timedelta(minutes=expiry_minutes)
        
        verification_data = {
            "phone_number": phone,
            "verification_code": verification_code,
            "market": market.value,
            "expires_at": expires_at,
            "is_used": False,
            "created_at": datetime.utcnow()
        }
        
        if user_id:
            verification_data["user_id"] = user_id
        
        # This would need to be implemented based on your verification model
        # verification = await self.phone_verification_repository.create_verification(
        #     phone, verification_code, market, user_id
        # )
        
        # Send SMS
        try:
            await self.sms_service.send_verification_code(phone, verification_code, market)
        except Exception as e:
            raise create_phone_verification_error(
                "Failed to send verification code",
                ErrorCode.SMS_SERVICE_ERROR,
                {"error": str(e)}
            )
        
        return {
            "success": True,
            "message": "Verification code sent successfully",
            "phone": phone,
            "market": market.value,
            "expires_in_minutes": expiry_minutes
        }
    
    async def verify_code(self, phone: str, code: str, market: Market) -> Dict[str, Any]:
        """Verify SMS code"""
        # Get active verification
        verification = await self.phone_verification_repository.get_active_verification(phone, market)
        if not verification:
            raise create_phone_verification_error(
                "No active verification found for this phone number",
                ErrorCode.VERIFICATION_CODE_INVALID,
                {"phone": phone}
            )
        
        # Check if code matches
        if verification.verification_code != code:
            raise create_phone_verification_error(
                "Invalid verification code",
                ErrorCode.VERIFICATION_CODE_INVALID,
                {"phone": phone}
            )
        
        # Check if code is expired
        if datetime.utcnow() > verification.expires_at:
            raise create_phone_verification_error(
                "Verification code has expired",
                ErrorCode.VERIFICATION_CODE_EXPIRED,
                {"phone": phone}
            )
        
        # Check if code is already used
        if verification.is_used:
            raise create_phone_verification_error(
                "Verification code has already been used",
                ErrorCode.VERIFICATION_CODE_INVALID,
                {"phone": phone}
            )
        
        # Mark verification as used
        await self.phone_verification_repository.mark_as_used(verification.id)
        
        # Update user verification status if user exists
        if verification.user_id:
            user = await self.user_repository.get_by_id(verification.user_id)
            if user:
                user.is_verified = True
                user.updated_at = datetime.utcnow()
                await self.user_repository.update(user)
        
        return {
            "success": True,
            "message": "Phone number verified successfully",
            "phone": phone,
            "market": market.value,
            "verified_at": datetime.utcnow().isoformat()
        }
    
    def _generate_verification_code(self, length: int) -> str:
        """Generate random verification code"""
        return ''.join([str(secrets.randbelow(10)) for _ in range(length)])

class AuthService(BaseService):
    """Authentication service"""
    
    def __init__(
        self,
        user_repository: UserRepository,
        phone_verification_service: PhoneVerificationService,
        jwt_service: 'JWTService'
    ):
        super().__init__()
        self.user_repository = user_repository
        self.phone_verification_service = phone_verification_service
        self.jwt_service = jwt_service
    
    async def login_with_phone(self, phone: str, market: Market) -> Dict[str, Any]:
        """Login with phone number (send verification code)"""
        # Check if user exists
        user = await self.user_repository.get_by_phone(phone, market)
        if not user:
            # Create new user
            user_service = UserService(
                self.user_repository,
                None,  # Would need phone verification repository
                None   # Would need notification repository
            )
            await user_service.register_user(phone, market)
        
        # Send verification code
        await self.phone_verification_service.send_verification_code(phone, market, user.id if user else None)
        
        return {
            "success": True,
            "message": "Verification code sent to your phone",
            "phone": phone,
            "market": market.value,
            "user_exists": user is not None
        }
    
    async def verify_and_login(self, phone: str, code: str, market: Market) -> Dict[str, Any]:
        """Verify code and complete login"""
        # Verify code
        verification_result = await self.phone_verification_service.verify_code(phone, code, market)
        
        # Get user
        user = await self.user_repository.get_by_phone(phone, market)
        if not user:
            raise create_user_error(
                "User not found",
                ErrorCode.USER_NOT_FOUND,
                {"phone": phone}
            )
        
        # Update last login
        await self.user_repository.update_last_login(user.id, datetime.utcnow())
        
        # Generate tokens
        access_token = self.jwt_service.create_access_token(user.id, market)
        refresh_token = self.jwt_service.create_refresh_token(user.id, market)
        
        return {
            "success": True,
            "message": "Login successful",
            "user": {
                "id": user.id,
                "phone_number": user.phone_number,
                "full_name": user.full_name,
                "market": user.market,
                "language": user.language,
                "country": user.country,
                "is_verified": user.is_verified
            },
            "tokens": {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": self.settings.security.access_token_expire_minutes * 60
            }
        }
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token"""
        try:
            payload = self.jwt_service.verify_refresh_token(refresh_token)
            user_id = payload.get("user_id")
            market = Market(payload.get("market"))
            
            # Get user
            user = await self.user_repository.get_by_id(user_id)
            if not user:
                raise create_user_error(
                    "User not found",
                    ErrorCode.USER_NOT_FOUND,
                    {"user_id": user_id}
                )
            
            # Generate new access token
            new_access_token = self.jwt_service.create_access_token(user.id, market)
            
            return {
                "success": True,
                "message": "Token refreshed successfully",
                "access_token": new_access_token,
                "token_type": "bearer",
                "expires_in": self.settings.security.access_token_expire_minutes * 60
            }
            
        except Exception as e:
            raise create_phone_verification_error(
                "Invalid refresh token",
                ErrorCode.TOKEN_INVALID,
                {"error": str(e)}
            )

class MarketService(BaseService):
    """Market management service"""
    
    async def get_supported_markets(self) -> Dict[str, Any]:
        """Get list of supported markets"""
        markets = []
        for market in Market:
            config = self.settings.get_market_config(market)
            markets.append({
                "code": market.value,
                "name": config["country"],
                "phone_prefix": config["phone_prefix"],
                "language": config["language"],
                "currency": config["currency"],
                "currency_code": config["currency_code"]
            })
        
        return {
            "success": True,
            "markets": markets
        }
    
    async def detect_market_from_phone(self, phone: str) -> Dict[str, Any]:
        """Detect market from phone number"""
        if phone.startswith("+996"):
            market = Market.KG
        elif phone.startswith("+1"):
            market = Market.US
        else:
            raise create_market_error(
                "Cannot detect market from phone number",
                ErrorCode.MARKET_NOT_DETECTED,
                {"phone": phone}
            )
        
        config = self.settings.get_market_config(market)
        
        return {
            "success": True,
            "market": market.value,
            "country": config["country"],
            "language": config["language"],
            "currency": config["currency"],
            "currency_code": config["currency_code"],
            "phone_prefix": config["phone_prefix"]
        }
