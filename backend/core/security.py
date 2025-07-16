"""
Security module for Sophia AI
Handles user authentication, JWT tokens, and authorization
"""

import logging
from datetime import datetime, timedelta, UTC
from typing import Optional, Dict, Any
import jwt
import hashlib
import secrets
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.auto_esc_config import get_config_value

logger = logging.getLogger(__name__)

# Security configuration
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = get_config_value("jwt_secret_key", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

class SecurityConfig:
    """Security configuration and utilities"""
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def generate_salt() -> str:
        """Generate a random salt"""
        return secrets.token_hex(16)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Failed to create access token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create access token"
        )

def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Failed to create refresh token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create refresh token"
        )

def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode a JWT token
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check if token has expired
        exp = payload.get("exp")
        if exp is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing expiration"
            )
        
        if datetime.now(UTC) > datetime.fromtimestamp(exp, UTC):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not verify token"
        )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user from JWT token
    """
    try:
        # Extract token from credentials
        token = credentials.credentials
        
        # Verify token and extract payload
        payload = verify_token(token)
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing user ID"
            )
        
        # Import here to avoid circular imports
        from backend.models.user import User
        
        # Get user from database
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Check if user is active
        if not user.is_active():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive"
            )
        
        # Check if user account is locked
        if user.is_locked():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is locked"
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get current user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not authenticate user"
        )

def require_role(*required_roles):
    """
    Decorator to require specific roles for accessing endpoints
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Get current user from kwargs
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Check if user has required role
            if current_user.role not in required_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Required role: {', '.join(required_roles)}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_permission(permission: str):
    """
    Decorator to require specific permissions for accessing endpoints
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            user_permissions = current_user.get_permissions()
            if permission not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Required permission: {permission}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def generate_api_key() -> str:
    """Generate a secure API key"""
    return f"ska_{secrets.token_urlsafe(32)}"

def hash_api_key(api_key: str) -> str:
    """Hash an API key for storage"""
    return hashlib.sha256(api_key.encode()).hexdigest()

def verify_api_key(api_key: str, hashed_key: str) -> bool:
    """Verify an API key against its hash"""
    return hashlib.sha256(api_key.encode()).hexdigest() == hashed_key

async def authenticate_api_key(api_key: str, db: Session) -> Optional[dict]:
    """Authenticate using API key"""
    try:
        hash_api_key(api_key)
        
        # Here you would check against your API key storage
        # This is a simplified implementation
        logger.info(f"API key authentication attempted: {api_key[:10]}...")
        
        return {
            "user_id": "api_user",
            "permissions": ["api_access"],
            "api_key": True
        }
        
    except Exception as e:
        logger.error(f"API key authentication error: {e}")
        return None

def check_security_health() -> dict:
    """Check security system health"""
    try:
        # Test token creation and verification
        test_data = {"sub": "test_user", "role": "user"}
        test_token = create_access_token(test_data, timedelta(seconds=1))
        verify_token(test_token)
        
        return {
            "status": "healthy",
            "jwt_algorithm": ALGORITHM,
            "token_expiry": f"{ACCESS_TOKEN_EXPIRE_MINUTES} minutes",
            "password_hashing": "bcrypt"
        }
        
    except Exception as e:
        logger.error(f"Security health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        } 