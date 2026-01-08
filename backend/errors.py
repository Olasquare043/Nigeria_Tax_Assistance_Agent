# errors.py - CUSTOM ERROR HANDLING
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

class ErrorResponse(BaseModel):
    """Standard error response format"""
    error: str                    # Error code: "INVALID_TOKEN"
    message: str                  # User-friendly message
    detail: Optional[str] = None  # Technical details
    code: Optional[str] = None    # Error code: "AUTH-1001"
    timestamp: str = datetime.now().isoformat()
    request_id: Optional[str] = None  # For support tracking
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "VALIDATION_ERROR",
                "message": "Invalid input provided",
                "detail": "Email must be valid",
                "code": "VAL-1001",
                "timestamp": "2024-01-06T10:30:00Z",
                "request_id": "req_123456"
            }
        }

class ValidationErrorDetail(BaseModel):
    """Validation error detail"""
    field: str
    error: str
    value: Optional[Any] = None

class ValidationErrorResponse(ErrorResponse):
    """Validation error response"""
    errors: Optional[Dict[str, ValidationErrorDetail]] = None

# Custom Exceptions
class AppException(Exception):
    """Base application exception"""
    def __init__(
        self,
        error_code: str,
        message: str,
        status_code: int = 400,
        detail: Optional[str] = None,
        code: Optional[str] = None
    ):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        self.detail = detail
        self.code = code
        super().__init__(message)

class AuthenticationError(AppException):
    """Authentication related errors"""
    def __init__(
        self,
        message: str = "Authentication failed",
        detail: Optional[str] = None,
        code: Optional[str] = None
    ):
        super().__init__(
            error_code="AUTHENTICATION_ERROR",
            message=message,
            status_code=401,
            detail=detail,
            code=code or "AUTH-1001"
        )

class AuthorizationError(AppException):
    """Authorization related errors"""
    def __init__(
        self,
        message: str = "Access denied",
        detail: Optional[str] = None,
        code: Optional[str] = None
    ):
        super().__init__(
            error_code="AUTHORIZATION_ERROR",
            message=message,
            status_code=403,
            detail=detail,
            code=code or "AUTH-1002"
        )

class ValidationException(AppException):
    """Validation errors"""
    def __init__(
        self,
        message: str = "Validation failed",
        errors: Optional[Dict[str, ValidationErrorDetail]] = None,
        detail: Optional[str] = None,
        code: Optional[str] = None
    ):
        super().__init__(
            error_code="VALIDATION_ERROR",
            message=message,
            status_code=400,
            detail=detail,
            code=code or "VAL-1001"
        )
        self.errors = errors

class NotFoundError(AppException):
    """Resource not found"""
    def __init__(
        self,
        resource: str = "Resource",
        detail: Optional[str] = None,
        code: Optional[str] = None
    ):
        message = f"{resource} not found"
        super().__init__(
            error_code="NOT_FOUND",
            message=message,
            status_code=404,
            detail=detail,
            code=code or "RES-1001"
        )

class RateLimitError(AppException):
    """Rate limit exceeded"""
    def __init__(
        self,
        retry_after: int = 60,
        detail: Optional[str] = None,
        code: Optional[str] = None
    ):
        message = f"Too many requests. Please try again in {retry_after} seconds"
        super().__init__(
            error_code="RATE_LIMIT_EXCEEDED",
            message=message,
            status_code=429,
            detail=detail,
            code=code or "RATE-1001"
        )
        self.retry_after = retry_after

class ServiceError(AppException):
    """External service errors"""
    def __init__(
        self,
        service: str = "Service",
        detail: Optional[str] = None,
        code: Optional[str] = None
    ):
        message = f"{service} is temporarily unavailable"
        super().__init__(
            error_code="SERVICE_ERROR",
            message=message,
            status_code=503,
            detail=detail,
            code=code or "SVC-1001"
        )

# Common error codes
ERROR_CODES = {
    # Authentication
    "INVALID_CREDENTIALS": ("Invalid email or password", "AUTH-1002"),
    "ACCOUNT_LOCKED": ("Account is temporarily locked", "AUTH-1003"),
    "INVALID_TOKEN": ("Invalid or expired token", "AUTH-1004"),
    "TOKEN_EXPIRED": ("Session expired", "AUTH-1005"),
    
    # Validation
    "INVALID_EMAIL": ("Invalid email format", "VAL-1002"),
    "WEAK_PASSWORD": ("Password must be at least 6 characters", "VAL-1003"),
    "EMAIL_EXISTS": ("Email already registered", "VAL-1004"),
    "USERNAME_EXISTS": ("Username already taken", "VAL-1005"),
    "EMPTY_MESSAGE": ("Message cannot be empty", "VAL-1006"),
    
    # Business Logic
    "CONVERSATION_NOT_FOUND": ("Conversation not found", "BIZ-1001"),
    "ACCESS_DENIED": ("You don't have access to this resource", "BIZ-1002"),
    "INVALID_RESET_TOKEN": ("Invalid or expired reset token", "BIZ-1003"),
    
    # Rate Limiting
    "TOO_MANY_REQUESTS": ("Too many requests", "RATE-1002"),
    "TOO_MANY_LOGIN_ATTEMPTS": ("Too many login attempts", "RATE-1003"),
}

def create_error_response(
    error_key: str,
    detail: Optional[str] = None,
    request_id: Optional[str] = None
) -> ErrorResponse:
    """Create a standardized error response"""
    message, code = ERROR_CODES.get(error_key, ("An error occurred", "GEN-1001"))
    
    return ErrorResponse(
        error=error_key,
        message=message,
        detail=detail,
        code=code,
        request_id=request_id or str(uuid.uuid4())
    )