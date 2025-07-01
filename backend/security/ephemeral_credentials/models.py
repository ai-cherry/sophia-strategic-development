"""
Ephemeral Credentials Models for Sophia AI Platform.

This module defines the data models for the ephemeral credentials system,
which provides short-lived access tokens for API and service authentication.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, validator


class CredentialScope(str, Enum):
    """Scope of the ephemeral credential."""

    # API access scopes
    API_READ = "api:read"
    API_WRITE = "api:write"
    API_ADMIN = "api:admin"

    # Service scopes
    SERVICE_READ = "service:read"
    SERVICE_WRITE = "service:write"
    SERVICE_ADMIN = "service:admin"

    # Resource-specific scopes
    LLM_ACCESS = "llm:access"
    AGENT_ACCESS = "agent:access"
    DOCUMENT_READ = "document:read"
    DOCUMENT_WRITE = "document:write"
    KB_READ = "kb:read"
    KB_WRITE = "kb:write"

    # Integration scopes
    INTEGRATION_READ = "integration:read"
    INTEGRATION_WRITE = "integration:write"

    # System scopes
    SYSTEM_READ = "system:read"
    SYSTEM_WRITE = "system:write"
    SYSTEM_ADMIN = "system:admin"


class CredentialType(str, Enum):
    """Type of ephemeral credential."""

    API_KEY = "api_key"
    ACCESS_TOKEN = "access_token"
    REFRESH_TOKEN = "refresh_token"
    SESSION_TOKEN = "session_token"
    SERVICE_TOKEN = "service_token"


class CredentialStatus(str, Enum):
    """Status of ephemeral credential."""

    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    PENDING = "pending"


class TokenMetadata(BaseModel):
    """Metadata for an ephemeral token."""

    user_id: str | None = None
    service_id: str | None = None
    client_id: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    device_id: str | None = None
    session_id: str | None = None
    request_id: str | None = None
    additional_data: dict[str, Any] = Field(default_factory=dict)


class EphemeralCredential(BaseModel):
    """Ephemeral credential model."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    credential_type: CredentialType
    token_value: str
    scopes: list[CredentialScope]
    status: CredentialStatus = CredentialStatus.ACTIVE
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime
    last_used_at: datetime | None = None
    created_by: str | None = None
    revoked_at: datetime | None = None
    revoked_by: str | None = None
    metadata: TokenMetadata = Field(default_factory=TokenMetadata)

    @validator("expires_at")
    def validate_expiration(cls, v, values):
        """Validate that expiration is in the future."""
        if "created_at" in values and v <= values["created_at"]:
            raise ValueError("Expiration time must be in the future")
        return v

    def is_expired(self) -> bool:
        """Check if the credential is expired."""
        return self.expires_at <= datetime.now(UTC)

    def is_valid(self) -> bool:
        """Check if the credential is valid."""
        return self.status == CredentialStatus.ACTIVE and not self.is_expired()

    def to_response_dict(self) -> dict[str, Any]:
        """Convert to a dictionary suitable for API responses."""
        return {
            "id": self.id,
            "name": self.name,
            "credential_type": self.credential_type,
            "scopes": [scope.value for scope in self.scopes],
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "last_used_at": (
                self.last_used_at.isoformat() if self.last_used_at else None
            ),
            "metadata": {
                "user_id": self.metadata.user_id,
                "service_id": self.metadata.service_id,
                "client_id": self.metadata.client_id,
            },
        }


class CredentialRequest(BaseModel):
    """Request for creating an ephemeral credential."""

    name: str
    credential_type: CredentialType
    scopes: list[CredentialScope]
    ttl_seconds: int = 3600  # Default to 1 hour
    metadata: TokenMetadata | None = None

    @validator("ttl_seconds")
    def validate_ttl(cls, v):
        """Validate TTL is within allowed range."""
        min_ttl = 60  # 1 minute
        max_ttl = 86400 * 7  # 7 days

        if v < min_ttl:
            raise ValueError(f"TTL must be at least {min_ttl} seconds")

        if v > max_ttl:
            raise ValueError(f"TTL cannot exceed {max_ttl} seconds")

        return v


class CredentialResponse(BaseModel):
    """Response for credential creation or retrieval."""

    id: str
    name: str
    credential_type: CredentialType
    token_value: str
    scopes: list[str]
    expires_at: str
    created_at: str


class CredentialRevocationRequest(BaseModel):
    """Request for revoking an ephemeral credential."""

    credential_id: str
    reason: str | None = None


class CredentialValidationRequest(BaseModel):
    """Request for validating an ephemeral credential."""

    token_value: str
    required_scopes: list[CredentialScope] | None = None


class CredentialValidationResponse(BaseModel):
    """Response for credential validation."""

    valid: bool
    credential_id: str | None = None
    scopes: list[str] | None = None
    expires_at: str | None = None
    error: str | None = None
