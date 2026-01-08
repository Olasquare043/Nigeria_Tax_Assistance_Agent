from functools import wraps
from datetime import datetime, timedelta
from typing import Optional, Callable
import time

from fastapi import Request, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from errors import RateLimitError

class RateLimiter:
    def __init__(self):
        self.rate_limit_config = {
            "default": {"limit": 100, "window": 60},  
            "login": {"limit": 10, "window": 60},    
            "register": {"limit": 5, "window": 60},   
            "chat": {"limit": 50, "window": 3600},    
            "password_reset": {"limit": 3, "window": 3600},  
        }
    
    def check_rate_limit(
        self, 
        ip_address: str, 
        endpoint: str, 
        db: Session
    ) -> bool:
        """Check if request is within rate limit"""
        config = self.rate_limit_config.get(endpoint, self.rate_limit_config["default"])
        limit = config["limit"]
        window = config["window"]
        
        window_start = datetime.utcnow() - timedelta(seconds=window)
        
        # Get current request count for this IP and endpoint
        result = db.execute(
            text("""
                SELECT SUM(request_count) 
                FROM rate_limit_logs 
                WHERE ip_address = :ip 
                AND endpoint = :endpoint
                AND window_start >= :window_start
            """),
            {
                "ip": ip_address,
                "endpoint": endpoint,
                "window_start": window_start
            }
        ).fetchone()
        
        current_count = result[0] or 0
        
        if current_count >= limit:
            return False
        
        
        db.execute(
            text("""
                INSERT INTO rate_limit_logs 
                (ip_address, endpoint, request_count, window_start, window_end)
                VALUES (:ip, :endpoint, 1, :window_start, :window_end)
            """),
            {
                "ip": ip_address,
                "endpoint": endpoint,
                "window_start": window_start,
                "window_end": datetime.utcnow()
            }
        )
        db.commit()
        
        return True
    
    def cleanup_old_logs(self, db: Session):
        """Clean up old rate limit logs"""
        # Keep logs for 24 hours only
        cutoff = datetime.utcnow() - timedelta(hours=24)
        
        db.execute(
            text("DELETE FROM rate_limit_logs WHERE window_end < :cutoff"),
            {"cutoff": cutoff}
        )
        db.commit()

rate_limiter = RateLimiter()

def get_client_ip(request: Request) -> str:
    """Get client IP address from request"""
    if request.client:
        return request.client.host
    return "unknown"

def rate_limit(endpoint: str = "default"):
    """Rate limiting decorator"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Find request object
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                for key, value in kwargs.items():
                    if isinstance(value, Request):
                        request = value
                        break
            
            if not request:
                raise HTTPException(500, "Request object not found")
            
            # Get database session
            db = None
            for arg in args:
                if isinstance(arg, Session):
                    db = arg
                    break
            
            if not db:
                for key, value in kwargs.items():
                    if isinstance(value, Session):
                        db = value
                        break
            
            if not db:
                # Try to get from dependencies
                for key, value in kwargs.items():
                    if key == "db":
                        db = value
                        break
            
            if not db:
                raise HTTPException(500, "Database session not found")
            
            # Get client IP
            ip_address = get_client_ip(request)
            
            # Check rate limit
            if not rate_limiter.check_rate_limit(ip_address, endpoint, db):
                # Clean up old logs
                rate_limiter.cleanup_old_logs(db)
                
                raise RateLimitError(
                    retry_after=60,
                    detail=f"Rate limit exceeded for {endpoint}"
                )
            
            # Clean up old logs periodically (every 100 requests)
            if int(time.time()) % 100 == 0:
                rate_limiter.cleanup_old_logs(db)
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator