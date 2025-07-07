"""
Ephemeral Credentials Package for Sophia AI Platform.

This package provides functionality for managing ephemeral credentials,
which are short-lived access tokens for API and service authentication.
"""

from infrastructure.security.ephemeral_credentials.middleware import (
    EphemeralCredentialsMiddleware,
    setup_ephemeral_credentials_middleware,
)
from infrastructure.security.ephemeral_credentials.models import (
    CredentialRequest,
    CredentialResponse,
    CredentialRevocationRequest,
    CredentialScope,
    CredentialStatus,
    CredentialType,
    CredentialValidationRequest,
    CredentialValidationResponse,
    EphemeralCredential,
    TokenMetadata,
)
from infrastructure.security.ephemeral_credentials.service import (
    EphemeralCredentialsService,
)

__all__ = [
    "CredentialRequest",
    "CredentialResponse",
    "CredentialRevocationRequest",
    "CredentialScope",
    "CredentialStatus",
    "CredentialType",
    "CredentialValidationRequest",
    "CredentialValidationResponse",
    "EphemeralCredential",
    "TokenMetadata",
    "EphemeralCredentialsService",
    "EphemeralCredentialsMiddleware",
    "setup_ephemeral_credentials_middleware",
]
