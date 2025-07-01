"""
Ephemeral Credentials API Routes for Sophia AI Platform.

This module provides the FastAPI routes for managing ephemeral credentials,
which are short-lived access tokens for API and service authentication.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer

from backend.security.audit_logger import AuditEventType, info
from backend.security.ephemeral_credentials.models import (
    CredentialRequest,
    CredentialResponse,
    CredentialRevocationRequest,
    CredentialValidationRequest,
    CredentialValidationResponse,
    TokenMetadata,
)
from backend.security.ephemeral_credentials.service import EphemeralCredentialsService
from backend.security.rbac.dependencies import (
    get_current_user,
    require_permission,
)
from backend.security.rbac.models import ActionType, ResourceType

# Create router
router = APIRouter(prefix="/api/v1/credentials", tags=["credentials"])

# Set up logger
logger = logging.getLogger(__name__)

# API key security scheme
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# OAuth2 security scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


async def get_credentials_service() -> EphemeralCredentialsService:
    """
    Get the ephemeral credentials service.

    Returns:
        EphemeralCredentialsService instance
    """
    # In a real application, this would be a singleton or dependency injection
    service = EphemeralCredentialsService()
    await service.initialize()
    return service


@router.post(
    "/",
    response_model=CredentialResponse,
    summary="Create a new ephemeral credential",
    description="Create a new ephemeral credential with specified scopes and TTL.",
)
async def create_credential(
    request: CredentialRequest,
    credentials_service: EphemeralCredentialsService = Depends(get_credentials_service),
    current_user: dict = Depends(get_current_user),
    _: bool = Depends(require_permission(ResourceType.SYSTEM, ActionType.MANAGE)),
) -> CredentialResponse:
    """
    Create a new ephemeral credential.

    Args:
        request: Credential request
        credentials_service: Ephemeral credentials service
        current_user: Current authenticated user

    Returns:
        Credential response with token value
    """
    # Add user ID to metadata if not provided
    if request.metadata is None:
        request.metadata = TokenMetadata(user_id=current_user.get("id"))
    elif request.metadata.user_id is None:
        request.metadata.user_id = current_user.get("id")

    # Create credential
    response = await credentials_service.create_credential(
        request=request,
        created_by=current_user.get("id"),
    )

    # Log credential creation
    info(
        AuditEventType.ADMIN_ACTION,
        f"Created ephemeral credential: {request.name}",
        {
            "credential_id": response.id,
            "credential_type": request.credential_type.value,
            "scopes": [scope.value for scope in request.scopes],
            "ttl_seconds": request.ttl_seconds,
        },
    )

    return response


@router.post(
    "/validate",
    response_model=CredentialValidationResponse,
    summary="Validate an ephemeral credential",
    description="Validate an ephemeral credential and check if it has the required scopes.",
)
async def validate_credential(
    request: CredentialValidationRequest,
    credentials_service: EphemeralCredentialsService = Depends(get_credentials_service),
    current_user: dict = Depends(get_current_user),
    _: bool = Depends(require_permission(ResourceType.SYSTEM, ActionType.READ)),
) -> CredentialValidationResponse:
    """
    Validate an ephemeral credential.

    Args:
        request: Validation request
        credentials_service: Ephemeral credentials service
        current_user: Current authenticated user

    Returns:
        Validation response
    """
    # Validate credential
    response = await credentials_service.validate_credential(request=request)

    # Log validation
    info(
        (
            AuditEventType.ACCESS_GRANTED
            if response.valid
            else AuditEventType.ACCESS_DENIED
        ),
        f"Validated ephemeral credential: {'valid' if response.valid else 'invalid'}",
        {
            "credential_id": response.credential_id,
            "valid": response.valid,
            "error": response.error,
        },
    )

    return response


@router.post(
    "/revoke",
    summary="Revoke an ephemeral credential",
    description="Revoke an ephemeral credential to prevent further use.",
)
async def revoke_credential(
    request: CredentialRevocationRequest,
    credentials_service: EphemeralCredentialsService = Depends(get_credentials_service),
    current_user: dict = Depends(get_current_user),
    _: bool = Depends(require_permission(ResourceType.SYSTEM, ActionType.MANAGE)),
) -> dict[str, bool]:
    """
    Revoke an ephemeral credential.

    Args:
        request: Revocation request
        credentials_service: Ephemeral credentials service
        current_user: Current authenticated user

    Returns:
        Success status
    """
    # Revoke credential
    success = await credentials_service.revoke_credential(
        request=request,
        revoked_by=current_user.get("id"),
    )

    # If credential not found
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Credential with ID {request.credential_id} not found",
        )

    # Log revocation
    info(
        AuditEventType.ADMIN_ACTION,
        f"Revoked ephemeral credential: {request.credential_id}",
        {
            "credential_id": request.credential_id,
            "reason": request.reason,
        },
    )

    return {"success": success}


@router.get(
    "/",
    response_model=list[dict],
    summary="List ephemeral credentials",
    description="List all ephemeral credentials with optional filters.",
)
async def list_credentials(
    include_expired: bool = Query(False, description="Include expired credentials"),
    include_revoked: bool = Query(False, description="Include revoked credentials"),
    credentials_service: EphemeralCredentialsService = Depends(get_credentials_service),
    current_user: dict = Depends(get_current_user),
    _: bool = Depends(require_permission(ResourceType.SYSTEM, ActionType.READ)),
) -> list[dict]:
    """
    List all ephemeral credentials.

    Args:
        include_expired: Whether to include expired credentials
        include_revoked: Whether to include revoked credentials
        credentials_service: Ephemeral credentials service
        current_user: Current authenticated user

    Returns:
        List of credentials
    """
    # List credentials
    credentials = await credentials_service.list_credentials(
        include_expired=include_expired,
        include_revoked=include_revoked,
    )

    # Convert to response format
    return [cred.to_response_dict() for cred in credentials]


@router.get(
    "/{credential_id}",
    response_model=dict,
    summary="Get ephemeral credential",
    description="Get an ephemeral credential by ID.",
)
async def get_credential(
    credential_id: str = Path(..., description="ID of the credential"),
    credentials_service: EphemeralCredentialsService = Depends(get_credentials_service),
    current_user: dict = Depends(get_current_user),
    _: bool = Depends(require_permission(ResourceType.SYSTEM, ActionType.READ)),
) -> dict:
    """
    Get an ephemeral credential by ID.

    Args:
        credential_id: ID of the credential
        credentials_service: Ephemeral credentials service
        current_user: Current authenticated user

    Returns:
        Credential details
    """
    # Get credential
    credential = await credentials_service.get_credential(credential_id=credential_id)

    # If credential not found
    if not credential:
        raise HTTPException(
            status_code=404,
            detail=f"Credential with ID {credential_id} not found",
        )

    # Convert to response format
    return credential.to_response_dict()


@router.post(
    "/cleanup",
    summary="Clean up expired credentials",
    description="Remove expired credentials from the system.",
)
async def cleanup_credentials(
    credentials_service: EphemeralCredentialsService = Depends(get_credentials_service),
    current_user: dict = Depends(get_current_user),
    _: bool = Depends(require_permission(ResourceType.SYSTEM, ActionType.MANAGE)),
) -> dict[str, int]:
    """
    Clean up expired credentials.

    Args:
        credentials_service: Ephemeral credentials service
        current_user: Current authenticated user

    Returns:
        Number of credentials removed
    """
    # Clean up expired credentials
    removed_count = await credentials_service.cleanup_expired_credentials()

    # Log cleanup
    info(
        AuditEventType.ADMIN_ACTION,
        f"Cleaned up {removed_count} expired credentials",
        {"removed_count": removed_count},
    )

    return {"removed_count": removed_count}


# Authentication middleware for API routes
@router.middleware("http")
async def authenticate_request(request: Request, call_next):
    """
    Authenticate requests using ephemeral credentials.

    Args:
        request: FastAPI request
        call_next: Next middleware or route handler

    Returns:
        Response from next middleware or route handler
    """
    # Get credentials service
    credentials_service = await get_credentials_service()

    # Try to get token from header
    token = request.headers.get("Authorization")
    if token and token.startswith("Bearer "):
        token = token[7:]  # Remove "Bearer " prefix
    else:
        token = request.headers.get("X-API-Key")

    # If token found, validate it
    if token:
        validation_result = await credentials_service.validate_credential(
            request=CredentialValidationRequest(token_value=token)
        )

        if validation_result.valid:
            # Add credential info to request state
            request.state.credential_id = validation_result.credential_id
            request.state.credential_scopes = validation_result.scopes

    # Continue with request
    return await call_next(request)
