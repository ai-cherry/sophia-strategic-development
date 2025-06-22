from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

# This is a placeholder for a secure way to store and retrieve API keys.
# In a real production environment, this would be integrated with a secrets manager
# like Pulumi ESC, AWS Secrets Manager, or HashiCorp Vault.
# For this example, we will use a static dictionary.
VALID_API_KEYS = {"sophia-dashboard-prod-key"}  # This is an example key.


async def get_api_key(api_key: str = Security(api_key_header)):
    """Validate the API key from the X-API-KEY header."""
        if api_key in VALID_API_KEYS:
        return api_key
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
