"""
Authentication utilities for Sophia AI platform.
Provides JWT token handling and user session management.
"""

import os
from datetime import datetime, timedelta
from typing import Any

# Try to import jose, fallback to basic implementation if not available
try:
    from jose import JWTError, jwt

    JOSE_AVAILABLE = True
except ImportError:
    JOSE_AVAILABLE = False
    JWTError = Exception

# Try to import passlib, fallback to basic implementation if not available
try:
    from passlib.context import CryptContext

    PASSLIB_AVAILABLE = True
except ImportError:
    PASSLIB_AVAILABLE = False
    import hashlib

from shared.utils.custom_logger import setup_logger

logger = setup_logger(__name__)


class AuthManager:
    """Authentication and authorization manager."""

    def __init__(self, secret_key: str | None = None, algorithm: str = "HS256"):
        self.secret_key = secret_key or os.getenv(
            "JWT_SECRET_KEY", "default-secret-key-change-in-production"
        )
        self.algorithm = algorithm

        if PASSLIB_AVAILABLE:
            self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        else:
            logger.warning("passlib not available, using basic hashing")

    def create_access_token(
        self, data: dict[str, Any], expires_delta: timedelta | None = None
    ) -> str:
        """Create JWT access token."""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=24)

        to_encode.update({"exp": expire})

        try:
            if JOSE_AVAILABLE:
                encoded_jwt = jwt.encode(
                    to_encode, self.secret_key, algorithm=self.algorithm
                )
            else:
                # Basic implementation - not secure for production
                import base64
                import json

                encoded_jwt = base64.b64encode(json.dumps(to_encode).encode()).decode()

            logger.info(
                "Access token created", user=data.get("sub"), expires=expire.isoformat()
            )
            return encoded_jwt
        except Exception as e:
            logger.exception("Failed to create access token", error=str(e))
            raise

    def verify_token(self, token: str) -> dict[str, Any] | None:
        """Verify and decode JWT token."""
        try:
            if JOSE_AVAILABLE:
                payload = jwt.decode(
                    token, self.secret_key, algorithms=[self.algorithm]
                )
            else:
                # Basic implementation - not secure for production
                import base64
                import json

                payload = json.loads(base64.b64decode(token))
                # Check expiration
                if "exp" in payload:
                    exp = (
                        datetime.fromisoformat(payload["exp"])
                        if isinstance(payload["exp"], str)
                        else datetime.fromtimestamp(payload["exp"])
                    )
                    if exp < datetime.utcnow():
                        return None
            return payload
        except (JWTError, Exception) as e:
            logger.warning("Invalid token", error=str(e))
            return None

    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt or fallback."""
        if PASSLIB_AVAILABLE:
            return self.pwd_context.hash(password)
        else:
            # Basic SHA256 hashing - not secure for production
            return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        if PASSLIB_AVAILABLE:
            return self.pwd_context.verify(plain_password, hashed_password)
        else:
            # Basic comparison for SHA256
            return (
                hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password
            )


# Default auth manager (will be configured with actual secret)
auth_manager = AuthManager()


def get_current_user(token: str) -> dict[str, Any] | None:
    """Get current user from token - used by API routes."""
    return auth_manager.verify_token(token)


def create_user_token(user_id: str, role: str = "user", expires_hours: int = 24) -> str:
    """Create a user access token."""
    data = {"sub": user_id, "role": role, "iat": datetime.utcnow()}
    expires_delta = timedelta(hours=expires_hours)
    return auth_manager.create_access_token(data, expires_delta)
