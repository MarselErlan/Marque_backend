"""
Custom Exception Classes
Defines application-specific exceptions with proper error handling
"""

from typing import Optional, Dict, Any
from enum import Enum

class ErrorCode(Enum):
    """Application error codes"""
    # Authentication errors
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOKEN_INVALID = "TOKEN_INVALID"
    ACCESS_DENIED = "ACCESS_DENIED"
    
    # User errors
    USER_NOT_FOUND = "USER_NOT_FOUND"
    USER_ALREADY_EXISTS = "USER_ALREADY_EXISTS"
    USER_INACTIVE = "USER_INACTIVE"
    USER_NOT_VERIFIED = "USER_NOT_VERIFIED"
    
    # Phone verification errors
    INVALID_PHONE_NUMBER = "INVALID_PHONE_NUMBER"
    PHONE_ALREADY_VERIFIED = "PHONE_ALREADY_VERIFIED"
    VERIFICATION_CODE_INVALID = "VERIFICATION_CODE_INVALID"
    VERIFICATION_CODE_EXPIRED = "VERIFICATION_CODE_EXPIRED"
    VERIFICATION_LIMIT_EXCEEDED = "VERIFICATION_LIMIT_EXCEEDED"
    
    # Market errors
    UNSUPPORTED_MARKET = "UNSUPPORTED_MARKET"
    MARKET_NOT_DETECTED = "MARKET_NOT_DETECTED"
    
    # Validation errors
    VALIDATION_ERROR = "VALIDATION_ERROR"
    REQUIRED_FIELD_MISSING = "REQUIRED_FIELD_MISSING"
    INVALID_FORMAT = "INVALID_FORMAT"
    
    # Database errors
    DATABASE_ERROR = "DATABASE_ERROR"
    CONNECTION_ERROR = "CONNECTION_ERROR"
    TRANSACTION_ERROR = "TRANSACTION_ERROR"
    
    # External service errors
    SMS_SERVICE_ERROR = "SMS_SERVICE_ERROR"
    EMAIL_SERVICE_ERROR = "EMAIL_SERVICE_ERROR"
    PAYMENT_SERVICE_ERROR = "PAYMENT_SERVICE_ERROR"
    
    # Rate limiting errors
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    
    # General errors
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"

class BaseAppException(Exception):
    """Base application exception"""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary"""
        return {
            "error": self.error_code.value,
            "message": self.message,
            "details": self.details,
            "status_code": self.status_code
        }

class AuthenticationError(BaseAppException):
    """Authentication related errors"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.INVALID_CREDENTIALS,
            details=details,
            status_code=401
        )

class TokenError(BaseAppException):
    """Token related errors"""
    
    def __init__(self, message: str, error_code: ErrorCode, details: Optional[Dict[str, Any]] = None):
        status_code = 401 if error_code in [ErrorCode.TOKEN_EXPIRED, ErrorCode.TOKEN_INVALID] else 403
        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            status_code=status_code
        )

class UserError(BaseAppException):
    """User related errors"""
    
    def __init__(self, message: str, error_code: ErrorCode, details: Optional[Dict[str, Any]] = None):
        status_code = 404 if error_code == ErrorCode.USER_NOT_FOUND else 400
        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            status_code=status_code
        )

class PhoneVerificationError(BaseAppException):
    """Phone verification related errors"""
    
    def __init__(self, message: str, error_code: ErrorCode, details: Optional[Dict[str, Any]] = None):
        status_code = 429 if error_code == ErrorCode.VERIFICATION_LIMIT_EXCEEDED else 400
        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            status_code=status_code
        )

class MarketError(BaseAppException):
    """Market related errors"""
    
    def __init__(self, message: str, error_code: ErrorCode, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            status_code=400
        )

class ValidationError(BaseAppException):
    """Validation related errors"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            details=details,
            status_code=422
        )

class DatabaseError(BaseAppException):
    """Database related errors"""
    
    def __init__(self, message: str, error_code: ErrorCode, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            status_code=500
        )

class ExternalServiceError(BaseAppException):
    """External service related errors"""
    
    def __init__(self, message: str, error_code: ErrorCode, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            status_code=502
        )

class RateLimitError(BaseAppException):
    """Rate limiting errors"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
            details=details,
            status_code=429
        )

class NotFoundError(BaseAppException):
    """Resource not found errors"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.NOT_FOUND,
            details=details,
            status_code=404
        )

class ConflictError(BaseAppException):
    """Resource conflict errors"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.CONFLICT,
            details=details,
            status_code=409
        )

class InternalError(BaseAppException):
    """Internal server errors"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.INTERNAL_ERROR,
            details=details,
            status_code=500
        )

# Exception factory functions
def create_authentication_error(message: str, details: Optional[Dict[str, Any]] = None) -> AuthenticationError:
    """Create authentication error"""
    return AuthenticationError(message, details)

def create_token_error(message: str, error_code: ErrorCode, details: Optional[Dict[str, Any]] = None) -> TokenError:
    """Create token error"""
    return TokenError(message, error_code, details)

def create_user_error(message: str, error_code: ErrorCode, details: Optional[Dict[str, Any]] = None) -> UserError:
    """Create user error"""
    return UserError(message, error_code, details)

def create_phone_verification_error(message: str, error_code: ErrorCode, details: Optional[Dict[str, Any]] = None) -> PhoneVerificationError:
    """Create phone verification error"""
    return PhoneVerificationError(message, error_code, details)

def create_market_error(message: str, error_code: ErrorCode, details: Optional[Dict[str, Any]] = None) -> MarketError:
    """Create market error"""
    return MarketError(message, error_code, details)

def create_validation_error(message: str, details: Optional[Dict[str, Any]] = None) -> ValidationError:
    """Create validation error"""
    return ValidationError(message, details)

def create_database_error(message: str, error_code: ErrorCode, details: Optional[Dict[str, Any]] = None) -> DatabaseError:
    """Create database error"""
    return DatabaseError(message, error_code, details)

def create_external_service_error(message: str, error_code: ErrorCode, details: Optional[Dict[str, Any]] = None) -> ExternalServiceError:
    """Create external service error"""
    return ExternalServiceError(message, error_code, details)

def create_rate_limit_error(message: str, details: Optional[Dict[str, Any]] = None) -> RateLimitError:
    """Create rate limit error"""
    return RateLimitError(message, details)

def create_not_found_error(message: str, details: Optional[Dict[str, Any]] = None) -> NotFoundError:
    """Create not found error"""
    return NotFoundError(message, details)

def create_conflict_error(message: str, details: Optional[Dict[str, Any]] = None) -> ConflictError:
    """Create conflict error"""
    return ConflictError(message, details)

def create_internal_error(message: str, details: Optional[Dict[str, Any]] = None) -> InternalError:
    """Create internal error"""
    return InternalError(message, details)
