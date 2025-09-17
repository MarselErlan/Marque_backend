"""
Pydantic Schemas for API Requests and Responses
Type-safe data validation and serialization
"""

from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from ...core.config import Market

# Enums
class NotificationType(str, Enum):
    ORDER = "order"
    PROMOTION = "promotion"
    SYSTEM = "system"

class AddressType(str, Enum):
    HOME = "home"
    WORK = "work"
    OTHER = "other"

class PaymentType(str, Enum):
    CARD = "card"
    PAYPAL = "paypal"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"
    CASH_ON_DELIVERY = "cash_on_delivery"
    BANK_TRANSFER = "bank_transfer"

# Request Schemas
class PhoneLoginRequest(BaseModel):
    """Phone login request"""
    phone: str = Field(..., description="Phone number with country code")
    
    @validator('phone')
    def validate_phone(cls, v):
        if not v.startswith('+'):
            raise ValueError('Phone number must start with +')
        if len(v) < 10:
            raise ValueError('Phone number too short')
        return v

class PhoneVerificationRequest(BaseModel):
    """Phone verification request"""
    phone: str = Field(..., description="Phone number with country code")
    code: str = Field(..., min_length=4, max_length=8, description="Verification code")
    
    @validator('phone')
    def validate_phone(cls, v):
        if not v.startswith('+'):
            raise ValueError('Phone number must start with +')
        return v

class UserProfileUpdateRequest(BaseModel):
    """User profile update request"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[EmailStr] = None
    language: Optional[str] = Field(None, regex="^(ru|en)$")
    
    @validator('full_name')
    def validate_full_name(cls, v):
        if v and len(v.strip()) < 2:
            raise ValueError('Full name must be at least 2 characters')
        return v.strip() if v else v

class UserAddressCreateRequest(BaseModel):
    """User address creation request"""
    address_type: AddressType = Field(..., description="Type of address")
    title: str = Field(..., min_length=2, max_length=100, description="Address title")
    full_address: str = Field(..., min_length=10, max_length=500, description="Full address")
    
    # KG-specific fields
    street: Optional[str] = Field(None, max_length=200)
    building: Optional[str] = Field(None, max_length=50)
    apartment: Optional[str] = Field(None, max_length=20)
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    region: Optional[str] = Field(None, max_length=100)
    district: Optional[str] = Field(None, max_length=100)
    
    # US-specific fields
    street_address: Optional[str] = Field(None, max_length=200)
    street_number: Optional[str] = Field(None, max_length=20)
    street_name: Optional[str] = Field(None, max_length=200)
    apartment_unit: Optional[str] = Field(None, max_length=20)
    city_us: Optional[str] = Field(None, max_length=100, alias="city")
    state: Optional[str] = Field(None, max_length=50)
    postal_code: Optional[str] = Field(None, max_length=20)
    country_us: Optional[str] = Field(None, max_length=100, alias="country")
    
    is_default: bool = Field(False, description="Set as default address")

class UserPaymentMethodCreateRequest(BaseModel):
    """User payment method creation request"""
    payment_type: PaymentType = Field(..., description="Payment method type")
    
    # Card-specific fields
    card_type: Optional[str] = Field(None, max_length=20)
    card_number_masked: Optional[str] = Field(None, max_length=20)
    card_holder_name: Optional[str] = Field(None, max_length=100)
    expiry_month: Optional[str] = Field(None, regex="^(0[1-9]|1[0-2])$")
    expiry_year: Optional[str] = Field(None, regex="^(20[2-9][0-9]|2[1-9][0-9][0-9])$")
    bank_name: Optional[str] = Field(None, max_length=100)
    
    # PayPal-specific fields
    paypal_email: Optional[EmailStr] = None
    
    is_default: bool = Field(False, description="Set as default payment method")

class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str = Field(..., description="Refresh token")

# Response Schemas
class UserProfileResponse(BaseModel):
    """User profile response"""
    id: int
    phone_number: str
    full_name: Optional[str]
    email: Optional[str]
    market: str
    language: str
    country: str
    is_active: bool
    is_verified: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    last_login: Optional[datetime]

class UserAddressResponse(BaseModel):
    """User address response"""
    id: int
    address_type: str
    title: str
    full_address: str
    street: Optional[str]
    building: Optional[str]
    apartment: Optional[str]
    city: Optional[str]
    country: Optional[str]
    region: Optional[str]
    district: Optional[str]
    street_address: Optional[str]
    street_number: Optional[str]
    street_name: Optional[str]
    apartment_unit: Optional[str]
    state: Optional[str]
    postal_code: Optional[str]
    is_default: bool
    is_active: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

class UserPaymentMethodResponse(BaseModel):
    """User payment method response"""
    id: int
    payment_type: str
    card_type: Optional[str]
    card_number_masked: Optional[str]
    card_holder_name: Optional[str]
    expiry_month: Optional[str]
    expiry_year: Optional[str]
    bank_name: Optional[str]
    paypal_email: Optional[str]
    is_default: bool
    is_active: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

class UserNotificationResponse(BaseModel):
    """User notification response"""
    id: int
    notification_type: str
    title: str
    message: Optional[str]
    order_id: Optional[int]
    is_read: bool
    is_active: bool
    created_at: datetime
    read_at: Optional[datetime]

class MarketInfoResponse(BaseModel):
    """Market information response"""
    code: str
    name: str
    phone_prefix: str
    language: str
    currency: str
    currency_code: str
    country: str

class AuthResponse(BaseModel):
    """Authentication response"""
    success: bool
    message: str
    user: Optional[UserProfileResponse] = None
    tokens: Optional[Dict[str, Any]] = None
    phone: Optional[str] = None
    market: Optional[str] = None
    user_exists: Optional[bool] = None

class PhoneVerificationResponse(BaseModel):
    """Phone verification response"""
    success: bool
    message: str
    phone: str
    market: str
    expires_in_minutes: Optional[int] = None
    verified_at: Optional[datetime] = None

class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    status_code: int

class SuccessResponse(BaseModel):
    """Success response"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

# Pagination Schemas
class PaginationParams(BaseModel):
    """Pagination parameters"""
    skip: int = Field(0, ge=0, description="Number of items to skip")
    limit: int = Field(100, ge=1, le=1000, description="Number of items to return")

class PaginatedResponse(BaseModel):
    """Paginated response"""
    items: List[Any]
    total: int
    skip: int
    limit: int
    has_next: bool
    has_prev: bool

# Health Check Schemas
class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str
    environment: str
    timestamp: datetime
    markets: List[str]

class ComponentHealthResponse(BaseModel):
    """Component health response"""
    status: str
    market: Optional[str] = None
    error: Optional[str] = None
    url: Optional[str] = None

class DetailedHealthResponse(BaseModel):
    """Detailed health check response"""
    status: str
    service: str
    version: str
    environment: str
    timestamp: datetime
    components: Dict[str, ComponentHealthResponse]

# Configuration Schemas
class AppConfigResponse(BaseModel):
    """Application configuration response"""
    application: Dict[str, Any]
    server: Dict[str, Any]
    markets: Dict[str, Dict[str, str]]
    features: Dict[str, Any]
