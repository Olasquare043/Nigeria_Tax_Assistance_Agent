import bcrypt
import jwt
import secrets
import hashlib
import os
from datetime import datetime, timedelta
from typing import Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "tax-reform-secret-key-change-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_EXPIRE_DAYS", "7"))
PASSWORD_RESET_EXPIRE_MINUTES = int(os.getenv("PASSWORD_RESET_EXPIRE_MINUTES", "30"))

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
   
    password_bytes = password.encode('utf-8')
    
    
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    try:
        plain_bytes = plain_password.encode('utf-8')
        
        # Truncate if too long
        if len(plain_bytes) > 72:
            plain_bytes = plain_bytes[:72]
        
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(plain_bytes, hashed_bytes)
    except Exception as e:
        print(f"Password verification error: {e}")
        return False

def create_access_token(user_id: int) -> str:
    """Create JWT access token"""
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def generate_reset_token() -> Tuple[str, str]:
    """Generate password reset token and its hash"""
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    return token, token_hash

def verify_reset_token(provided_token: str, stored_hash: str) -> bool:
    """Verify password reset token"""
    return hashlib.sha256(provided_token.encode()).hexdigest() == stored_hash

def get_password_reset_expiry() -> datetime:
    """Get password reset token expiry time"""
    return datetime.utcnow() + timedelta(minutes=PASSWORD_RESET_EXPIRE_MINUTES)

def validate_password_strength(password: str) -> Tuple[bool, Optional[str]]:
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    if len(password) > 128:
        return False, "Password is too long (max 128 characters)"
    
   
    
    return True, None

def validate_email(email: str) -> bool:
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

