import os
from enum import Enum

from fastapi import Depends, Header, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from backend.config.settings import settings


class UserRole(str, Enum):
    CEO = "ceo"
    TEAM_LEAD = "team_lead"
    INDIVIDUAL_CONTRIBUTOR = "individual"
    ADMIN = "admin"


reusable_oauth2 = HTTPBearer()

SOPHIA_ADMIN_KEY = os.getenv("SOPHIA_ADMIN_KEY", "sophia_admin_2024")


async def get_current_user_role(
    credentials: HTTPAuthorizationCredentials = Depends(reusable_oauth2),
) -> UserRole:
    """Dependency to get the current user's role from a JWT."""
        try:
        token = credentials.credentials
        SECRET_KEY = settings.security.jwt_secret_key  # Use the centralized secret
        ALGORITHM = "HS256"

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        role = payload.get("role")
        if role is None:
            raise HTTPException(status_code=403, detail="Role not found in token.")

        return UserRole(role)
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def verify_admin_key(x_admin_key: str = Header(...)):
    """A simple dependency to verify the admin API key."""
        if x_admin_key != SOPHIA_ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Invalid Admin Key")


# The old UserRole and JWT dependencies can be removed or kept for other purposes,
# but will not be used for the simplified Retool interface.
