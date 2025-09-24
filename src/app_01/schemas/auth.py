"""
Pydantic schemas for authentication
Request and response models for phone number authentication
"""

from pydantic import BaseModel, validator, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class UserSchema(BaseModel):
    id: str
    name: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

class MarketEnum(str, Enum):
    """Supported markets"""
    KG = "kg"
    US = "us"

class PhoneLoginRequest(BaseModel):
    """Phone number login request"""
    phone: str = Field(..., description="Phone number in international format")
    
    @validator('phone')
    def validate_phone_number(cls, v):
        """Validate phone number format for supported markets"""
        # Remove spaces and special characters
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
    phone: str = Field(..., description="Phone number in international format")
    verification_code: str = Field(..., min_length=4, max_length=8, description="SMS verification code")
    
    @validator('phone')
    def validate_phone_number(cls, v):
        """Validate phone number format for supported markets"""
        clean_phone = v.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        
        if clean_phone.startswith("+996") and len(clean_phone) == 13:
            return clean_phone
        elif clean_phone.startswith("+1") and len(clean_phone) == 12:
            return clean_phone
        else:
            raise ValueError("Phone number must be in format +996XXXXXXXXX (KG) or +1XXXXXXXXXX (US)")
    
    @validator('verification_code')
    def validate_verification_code(cls, v):
        """Validate verification code format"""
        if not v.isdigit():
            raise ValueError("Verification code must contain only digits")
        return v

class SendCodeResponse(BaseModel):
    """Send verification code response"""
    success: bool = Field(..., description="Whether the code was sent successfully")
    message: str = Field(..., description="Response message")
    phone_number: str = Field(..., description="Formatted phone number")
    market: MarketEnum = Field(..., description="Detected market")
    language: str = Field(..., description="Market language")
    expires_in_minutes: int = Field(..., description="Code expiration time in minutes")

class VerifyCodeResponse(BaseModel):
    """Phone verification response"""
    success: bool = Field(..., description="Whether verification was successful")
    message: str = Field(..., description="Response message")
    access_token: Optional[str] = Field(None, description="JWT access token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: Optional[int] = Field(None, description="Token expiration in seconds")
    user: Optional[UserSchema] = Field(None, description="User information")
    market: Optional[MarketEnum] = Field(None, description="User market")
    is_new_user: Optional[bool] = Field(None, description="Whether this is a new user")

class UserProfile(BaseModel):
    """User profile response"""
    id: str = Field(..., description="User ID")
    phone_number: str = Field(..., description="User phone number")
    formatted_phone: str = Field(..., description="Formatted phone number")
    name: Optional[str] = Field(None, description="User display name")
    full_name: Optional[str] = Field(None, description="User full name")
    profile_image_url: Optional[str] = Field(None, description="Profile image URL")
    is_verified: bool = Field(..., description="Phone verification status")
    market: MarketEnum = Field(..., description="User market")
    language: str = Field(..., description="User language")
    country: str = Field(..., description="User country")
    currency: str = Field(..., description="User currency")
    currency_code: str = Field(..., description="User currency code")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    created_at: datetime = Field(..., description="Account creation timestamp")

class UpdateProfileRequest(BaseModel):
    """Update user profile request"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=255, description="User full name")
    profile_image_url: Optional[str] = Field(None, max_length=500, description="Profile image URL")

class UpdateProfileResponse(BaseModel):
    """Update user profile response"""
    success: bool = Field(..., description="Whether update was successful")
    message: str = Field(..., description="Response message")
    user: UserProfile = Field(..., description="Updated user profile")

class LogoutResponse(BaseModel):
    """Logout response"""
    success: bool = Field(..., description="Whether logout was successful")
    message: str = Field(..., description="Response message")

class VerifyTokenResponse(BaseModel):
    """Verify token response"""
    valid: bool = Field(..., description="Whether token is valid")
    user_id: Optional[int] = Field(None, description="User ID from token")
    phone_number: Optional[str] = Field(None, description="User phone number")
    formatted_phone: Optional[str] = Field(None, description="Formatted phone number")
    market: Optional[MarketEnum] = Field(None, description="User market")
    currency: Optional[str] = Field(None, description="User currency")

class MarketInfo(BaseModel):
    """Market information"""
    market: MarketEnum = Field(..., description="Market code")
    country: str = Field(..., description="Country name")
    currency: str = Field(..., description="Currency symbol")
    currency_code: str = Field(..., description="Currency code")
    language: str = Field(..., description="Default language")
    phone_prefix: str = Field(..., description="Phone country code")
    phone_format: str = Field(..., description="Phone number format example")

class SupportedMarketsResponse(BaseModel):
    """Supported markets response"""
    supported_markets: list[MarketInfo] = Field(..., description="List of supported markets")
    default_market: MarketEnum = Field(..., description="Default market")

class ErrorResponse(BaseModel):
    """Error response"""
    success: bool = Field(False, description="Always false for errors")
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[dict] = Field(None, description="Additional error details")

class AuthErrorDetail(BaseModel):
    """Authentication error details"""
    field: Optional[str] = Field(None, description="Field that caused the error")
    code: Optional[str] = Field(None, description="Error code")
    market: Optional[MarketEnum] = Field(None, description="Market context")

class ValidationErrorResponse(BaseModel):
    """Validation error response"""
    success: bool = Field(False, description="Always false for validation errors")
    error: str = Field("validation_error", description="Error type")
    message: str = Field(..., description="Error message")
    details: list[dict] = Field(..., description="Validation error details")

class RateLimitResponse(BaseModel):
    """Rate limit response"""
    success: bool = Field(False, description="Always false for rate limit")
    error: str = Field("rate_limit", description="Error type")
    message: str = Field(..., description="Rate limit message")
    retry_after: int = Field(..., description="Seconds to wait before retry")
    max_attempts: int = Field(..., description="Maximum attempts allowed")
    attempts_remaining: int = Field(..., description="Attempts remaining")
