from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import secrets
import uuid

from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from security import (
    hash_password, verify_password, create_access_token, decode_access_token,
    generate_reset_token, verify_reset_token, get_password_reset_expiry,
    validate_password_strength, validate_email
)
from errors import (
    AppException, AuthenticationError, ValidationException,
    NotFoundError, RateLimitError, create_error_response
)
from rate_limiter import rate_limit, get_client_ip

router = APIRouter()
security = HTTPBearer(auto_error=False)

# Pydantic Models
class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None
    
    @validator('username')
    def validate_username(cls, v):
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        is_valid, error = validate_password_strength(v)
        if not is_valid:
            raise ValueError(error)
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None

class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        is_valid, error = validate_password_strength(v)
        if not is_valid:
            raise ValueError(error)
        return v

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        is_valid, error = validate_password_strength(v)
        if not is_valid:
            raise ValueError(error)
        return v

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    is_verified: bool
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

# Helper Functions
async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[Dict[str, Any]]:
    """Get current authenticated user"""
    if not credentials:
        return None
    
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if not payload:
        return None
    
    user_id = int(payload.get("sub"))
    
    # Get user from database
    result = db.execute(
        text("""
            SELECT id, email, username, full_name, is_verified, created_at
            FROM users 
            WHERE id = :user_id AND is_active = TRUE
        """),
        {"user_id": user_id}
    ).fetchone()
    
    if result:
        return {
            "id": result[0],
            "email": result[1],
            "username": result[2],
            "full_name": result[3],
            "is_verified": result[4],
            "created_at": result[5]
        }
    
    return None

def check_account_lockout(user: Dict[str, Any], db: Session) -> bool:
    """Check if account is locked"""
    if user.get("locked_until"):
        locked_until = user["locked_until"]
        if locked_until and locked_until > datetime.utcnow():
            return True
    return False

# API Endpoints
@router.post("/register", response_model=Token)
@rate_limit("5/minute")  
async def register(
    request: Request,
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    # Validate email
    if not validate_email(user.email):
        raise ValidationException(
            message="Invalid email format",
            detail="Please enter a valid email address"
        )
    
    # Check if email exists
    existing_email = db.execute(
        text("SELECT id FROM users WHERE email = :email"),
        {"email": user.email}
    ).fetchone()
    
    if existing_email:
        raise ValidationException(
            message="Email already registered",
            detail="This email is already associated with an account"
        )
    
    # Check if username exists
    existing_username = db.execute(
        text("SELECT id FROM users WHERE username = :username"),
        {"username": user.username}
    ).fetchone()
    
    if existing_username:
        raise ValidationException(
            message="Username already taken",
            detail="Please choose a different username"
        )
    
    # Hash password
    hashed_password = hash_password(user.password)
    
    # Create user
    result = db.execute(
        text("""
            INSERT INTO users (email, username, password_hash, full_name)
            VALUES (:email, :username, :password_hash, :full_name)
        """),
        {
            "email": user.email,
            "username": user.username,
            "password_hash": hashed_password,
            "full_name": user.full_name
        }
    )
    db.commit()
    
    user_id = result.lastrowid
    
    # Create access token
    access_token = create_access_token(user_id)
    
    # Get user data for response
    user_data = db.execute(
        text("""
            SELECT id, email, username, full_name, is_verified, created_at
            FROM users WHERE id = :user_id
        """),
        {"user_id": user_id}
    ).fetchone()
    
    # Log registration
    db.execute(
        text("""
            INSERT INTO system_logs (level, service, message, ip_address, user_id)
            VALUES ('INFO', 'auth', 'User registered', :ip, :user_id)
        """),
        {"ip": get_client_ip(request), "user_id": user_id}
    )
    db.commit()
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=7 * 24 * 3600,  # 7 days in seconds
        user=UserResponse(
            id=user_data[0],
            email=user_data[1],
            username=user_data[2],
            full_name=user_data[3],
            is_verified=user_data[4],
            created_at=user_data[5]
        )
    )

@router.post("/login", response_model=Token)
@rate_limit("10/minute")  # 10 login attempts per minute per IP
async def login(
    request: Request,
    user: UserLogin,
    db: Session = Depends(get_db)
):
    """Login user"""
    # Get user
    result = db.execute(
        text("""
            SELECT id, email, username, password_hash, full_name, 
                   is_verified, created_at, failed_login_attempts, locked_until
            FROM users 
            WHERE email = :email AND is_active = TRUE
        """),
        {"email": user.email}
    ).fetchone()
    
    if not result:
        # Log failed attempt
        db.execute(
            text("""
                INSERT INTO system_logs (level, service, message, ip_address)
                VALUES ('WARN', 'auth', 'Failed login attempt - user not found', :ip)
            """),
            {"ip": get_client_ip(request)}
        )
        db.commit()
        
        raise AuthenticationError(
            message="Invalid email or password",
            detail="Please check your credentials and try again"
        )
    
    (user_id, email, username, password_hash, full_name, 
     is_verified, created_at, failed_attempts, locked_until) = result
    
    # Check if account is locked
    if locked_until and locked_until > datetime.utcnow():
        raise AuthenticationError(
            message="Account temporarily locked",
            detail="Too many failed login attempts. Try again later."
        )
    
    # Verify password
    if not verify_password(user.password, password_hash):
        # Increment failed attempts
        failed_attempts = failed_attempts + 1 if failed_attempts else 1
        
        # Lock account after 5 failed attempts
        if failed_attempts >= 5:
            locked_until = datetime.utcnow() + timedelta(minutes=15)
            db.execute(
                text("""
                    UPDATE users 
                    SET failed_login_attempts = :attempts, locked_until = :locked_until
                    WHERE id = :user_id
                """),
                {
                    "attempts": failed_attempts,
                    "locked_until": locked_until,
                    "user_id": user_id
                }
            )
            
            # Log account lock
            db.execute(
                text("""
                    INSERT INTO system_logs (level, service, message, ip_address, user_id)
                    VALUES ('WARN', 'auth', 'Account locked due to failed attempts', :ip, :user_id)
                """),
                {"ip": get_client_ip(request), "user_id": user_id}
            )
            
            raise AuthenticationError(
                message="Account temporarily locked",
                detail="Too many failed login attempts. Try again in 15 minutes."
            )
        else:
            # Update failed attempts
            db.execute(
                text("UPDATE users SET failed_login_attempts = :attempts WHERE id = :user_id"),
                {"attempts": failed_attempts, "user_id": user_id}
            )
        
        db.commit()
        
        # Log failed attempt
        db.execute(
            text("""
                INSERT INTO system_logs (level, service, message, ip_address, user_id)
                VALUES ('WARN', 'auth', 'Failed login attempt - wrong password', :ip, :user_id)
            """),
            {"ip": get_client_ip(request), "user_id": user_id}
        )
        db.commit()
        
        raise AuthenticationError(
            message="Invalid email or password",
            detail=f"{5 - failed_attempts} attempts remaining"
        )
    
    # Reset failed attempts on successful login
    db.execute(
        text("""
            UPDATE users 
            SET failed_login_attempts = 0, locked_until = NULL
            WHERE id = :user_id
        """),
        {"user_id": user_id}
    )
    
    # Create access token
    access_token = create_access_token(user_id)
    
    # Log successful login
    db.execute(
        text("""
            INSERT INTO system_logs (level, service, message, ip_address, user_id)
            VALUES ('INFO', 'auth', 'User logged in', :ip, :user_id)
        """),
        {"ip": get_client_ip(request), "user_id": user_id}
    )
    db.commit()
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=7 * 24 * 3600,
        user=UserResponse(
            id=user_id,
            email=email,
            username=username,
            full_name=full_name,
            is_verified=is_verified,
            created_at=created_at
        )
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user information"""
    if not current_user:
        raise AuthenticationError(
            message="Not authenticated",
            detail="Please login to access this resource"
        )
    
    return UserResponse(**current_user)

@router.put("/profile")
async def update_profile(
    update_data: UserUpdate,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    if not current_user:
        raise AuthenticationError(
            message="Not authenticated",
            detail="Please login to update your profile"
        )
    
    # Update user profile
    db.execute(
        text("UPDATE users SET full_name = :full_name WHERE id = :user_id"),
        {"full_name": update_data.full_name, "user_id": current_user["id"]}
    )
    db.commit()
    
    # Get updated user
    user_data = db.execute(
        text("""
            SELECT id, email, username, full_name, is_verified, created_at
            FROM users WHERE id = :user_id
        """),
        {"user_id": current_user["id"]}
    ).fetchone()
    
    return {
        "message": "Profile updated successfully",
        "user": UserResponse(
            id=user_data[0],
            email=user_data[1],
            username=user_data[2],
            full_name=user_data[3],
            is_verified=user_data[4],
            created_at=user_data[5]
        )
    }

@router.put("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    if not current_user:
        raise AuthenticationError(
            message="Not authenticated",
            detail="Please login to change your password"
        )
    
    # Get current password hash
    result = db.execute(
        text("SELECT password_hash FROM users WHERE id = :user_id"),
        {"user_id": current_user["id"]}
    ).fetchone()
    
    if not result:
        raise NotFoundError(resource="User")
    
    current_password_hash = result[0]
    
    # Verify current password
    if not verify_password(password_data.current_password, current_password_hash):
        raise AuthenticationError(
            message="Current password is incorrect",
            detail="Please enter your current password correctly"
        )
    
    # Hash new password
    new_password_hash = hash_password(password_data.new_password)
    
    # Update password
    db.execute(
        text("UPDATE users SET password_hash = :password_hash WHERE id = :user_id"),
        {"password_hash": new_password_hash, "user_id": current_user["id"]}
    )
    db.commit()
    
    # Log password change
    db.execute(
        text("""
            INSERT INTO system_logs (level, service, message, user_id)
            VALUES ('INFO', 'auth', 'Password changed', :user_id)
        """),
        {"user_id": current_user["id"]}
    )
    db.commit()
    
    return {"message": "Password changed successfully"}

@router.post("/forgot-password")
@rate_limit("3/hour")  # 3 password reset requests per hour per IP
async def forgot_password(
    request: Request,
    reset_request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """Request password reset"""
    # Find user by email
    result = db.execute(
        text("SELECT id, email, full_name FROM users WHERE email = :email AND is_active = TRUE"),
        {"email": reset_request.email}
    ).fetchone()
    
    if not result:
        # Don't reveal if user exists (security best practice)
        return {
            "message": "If an account exists with this email, you will receive reset instructions"
        }
    
    user_id, email, full_name = result
    
    # Generate reset token
    token, token_hash = generate_reset_token()
    expires_at = get_password_reset_expiry()
    
    # Invalidate any existing reset tokens for this user
    db.execute(
        text("UPDATE password_reset_tokens SET used = TRUE WHERE user_id = :user_id AND used = FALSE"),
        {"user_id": user_id}
    )
    
    # Store new token
    db.execute(
        text("""
            INSERT INTO password_reset_tokens (user_id, token, expires_at)
            VALUES (:user_id, :token, :expires_at)
        """),
        {
            "user_id": user_id,
            "token": token_hash,
            "expires_at": expires_at
        }
    )
    db.commit()
    
    # In a real app, you would send an email here
    # For demo purposes, we'll return the token
    # In production: send_email(user.email, "Password Reset", f"Token: {token}")
    
    # Log reset request
    db.execute(
        text("""
            INSERT INTO system_logs (level, service, message, ip_address, user_id)
            VALUES ('INFO', 'auth', 'Password reset requested', :ip, :user_id)
        """),
        {"ip": get_client_ip(request), "user_id": user_id}
    )
    db.commit()
    
    return {
        "message": "Password reset instructions sent",
        "demo_token": token,  # Remove in production - only for demo!
        "expires_at": expires_at.isoformat()
    }

@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """Reset password using token"""
    # Find valid reset token
    result = db.execute(
        text("""
            SELECT prt.id, prt.user_id, prt.token, prt.expires_at, prt.used
            FROM password_reset_tokens prt
            JOIN users u ON prt.user_id = u.id
            WHERE prt.expires_at > UTC_TIMESTAMP() 
            AND prt.used = FALSE
            AND u.is_active = TRUE
        """)
    ).fetchall()
    
    token_found = None
    for token_record in result:
        if verify_reset_token(reset_data.token, token_record[2]):
            token_found = token_record
            break
    
    if not token_found:
        raise ValidationException(
            message="Invalid or expired reset token",
            detail="Please request a new password reset"
        )
    
    token_id, user_id, _, expires_at, used = token_found
    
    # Mark token as used
    db.execute(
        text("UPDATE password_reset_tokens SET used = TRUE WHERE id = :token_id"),
        {"token_id": token_id}
    )
    
    # Hash new password
    new_password_hash = hash_password(reset_data.new_password)
    
    # Update user password and reset failed attempts
    db.execute(
        text("""
            UPDATE users 
            SET password_hash = :password_hash, 
                failed_login_attempts = 0,
                locked_until = NULL
            WHERE id = :user_id
        """),
        {"password_hash": new_password_hash, "user_id": user_id}
    )
    
    db.commit()
    
    # Log password reset
    db.execute(
        text("""
            INSERT INTO system_logs (level, service, message, user_id)
            VALUES ('INFO', 'auth', 'Password reset completed', :user_id)
        """),
        {"user_id": user_id}
    )
    db.commit()
    
    return {"message": "Password reset successfully. You can now login with your new password."}

@router.post("/logout")
async def logout(
    current_user: Dict = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Logout user (in JWT, we can't invalidate token, but we can log it)"""
    if not current_user or not credentials:
        raise AuthenticationError(
            message="Not authenticated",
            detail="You are not logged in"
        )
    
    # Log logout action
    db.execute(
        text("""
            INSERT INTO system_logs (level, service, message, user_id)
            VALUES ('INFO', 'auth', 'User logged out', :user_id)
        """),
        {"user_id": current_user["id"]}
    )
    db.commit()
    
    return {"message": "Logged out successfully"}

# Export dependencies
get_current_user_dependency = get_current_user