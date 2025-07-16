"""
Basic Authentication Module
Provides user authentication for API endpoints
"""

from typing import Dict, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Simple bearer token authentication
security = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Dict[str, str]:
    """
    Get current user from authentication token

    For now, this is a simplified implementation.
    In production, this would validate JWT tokens and return real user data.
    """

    # For development, allow unauthenticated access
    if not credentials:
        return {"id": "default_user", "name": "Default User", "role": "admin"}

    # In production, validate the token here
    # For now, just return a mock user
    return {
        "id": "authenticated_user",
        "name": "Authenticated User",
        "role": "admin",
        "token": credentials.credentials,
    }

def require_role(required_role: str):
    """Dependency to require a specific role"""

    async def role_checker(user: Dict = Depends(get_current_user)):
        if user.get("role") != required_role and user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )
        return user

    return role_checker
