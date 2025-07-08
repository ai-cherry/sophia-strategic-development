"""
Ephemeral Credentials Service for Sophia AI Platform.

This module provides the core service for managing ephemeral credentials,
which are short-lived access tokens for API and service authentication.
"""

from __future__ import annotations

import base64
import json
import logging
import os
import secrets
import uuid
from datetime import UTC, datetime, timedelta

import jwt

from infrastructure.security.audit_logger import AuditEventType, error, info
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
from infrastructure.security.secret_management import SecretManager

logger = logging.getLogger(__name__)


class EphemeralCredentialsService:
    """
    Service for managing ephemeral credentials.

    This service provides functionality for creating, validating, and revoking
    short-lived access tokens for API and service authentication.
    """

    def __init__(
        self,
        secret_manager: SecretManager | None = None,
        storage_path: str | None = None,
        auto_save: bool = True,
        token_signing_key: str | None = None,
    ):
        """
        Initialize the ephemeral credentials service.

        Args:
            secret_manager: Secret manager for accessing secure credentials
            storage_path: Path to the storage file for credentials
            auto_save: Whether to automatically save changes to storage
            token_signing_key: Key for signing tokens (generated if not provided)
        """
        self.secret_manager = secret_manager or SecretManager()
        self.storage_path = storage_path or os.path.join(
            os.getcwd(), "data", "ephemeral_credentials.json"
        )
        self.auto_save = auto_save

        # Ensure storage directory exists
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)

        # Initialize credential storage
        self.credentials: dict[str, EphemeralCredential] = {}

        # Initialize token signing key
        self.token_signing_key = token_signing_key or self._get_or_create_signing_key()

        # Load existing credentials
        self._load_from_storage()

        # Set up logger
        self.logger = logger.bind(component="ephemeral_credentials_service")
        self.logger.info("Ephemeral credentials service initialized")

    def _get_or_create_signing_key(self) -> str:
        """
        Get or create a token signing key.

        Returns:
            Token signing key as a string
        """
        # Try to get from secret manager
        signing_key = self.secret_manager.config.get("token_signing_key")

        if not signing_key:
            # Generate a new key
            signing_key = secrets.token_hex(32)
            self.logger.warning(
                "Generated new token signing key - should be stored in ESC"
            )

        return signing_key

    def _load_from_storage(self) -> None:
        """Load credentials from storage file."""
        if not os.path.exists(self.storage_path):
            self.logger.info(
                "No credentials storage file found, starting with empty state"
            )
            return

        try:
            with open(self.storage_path) as f:
                data = json.load(f)

            # Convert JSON data to EphemeralCredential objects
            for cred_data in data.get("credentials", []):
                # Convert string dates to datetime objects
                if "created_at" in cred_data:
                    cred_data["created_at"] = datetime.fromisoformat(
                        cred_data["created_at"]
                    )
                if "expires_at" in cred_data:
                    cred_data["expires_at"] = datetime.fromisoformat(
                        cred_data["expires_at"]
                    )
                if cred_data.get("last_used_at"):
                    cred_data["last_used_at"] = datetime.fromisoformat(
                        cred_data["last_used_at"]
                    )
                if cred_data.get("revoked_at"):
                    cred_data["revoked_at"] = datetime.fromisoformat(
                        cred_data["revoked_at"]
                    )

                # Convert string scopes to enum values
                if "scopes" in cred_data:
                    cred_data["scopes"] = [
                        CredentialScope(s) for s in cred_data["scopes"]
                    ]

                # Convert string credential type to enum value
                if "credential_type" in cred_data:
                    cred_data["credential_type"] = CredentialType(
                        cred_data["credential_type"]
                    )

                # Convert string status to enum value
                if "status" in cred_data:
                    cred_data["status"] = CredentialStatus(cred_data["status"])

                # Create credential object
                credential = EphemeralCredential(**cred_data)
                self.credentials[credential.id] = credential

            self.logger.info(f"Loaded {len(self.credentials)} credentials from storage")

        except Exception as e:
            self.logger.exception(f"Failed to load credentials from storage: {e}")
            # Start with empty state
            self.credentials = {}

    def _save_to_storage(self) -> None:
        """Save credentials to storage file."""
        try:
            # Convert EphemeralCredential objects to dictionaries
            creds_data = []
            for cred in self.credentials.values():
                cred_dict = cred.dict()

                # Convert datetime objects to ISO format strings
                if "created_at" in cred_dict:
                    cred_dict["created_at"] = cred_dict["created_at"].isoformat()
                if "expires_at" in cred_dict:
                    cred_dict["expires_at"] = cred_dict["expires_at"].isoformat()
                if cred_dict.get("last_used_at"):
                    cred_dict["last_used_at"] = cred_dict["last_used_at"].isoformat()
                if cred_dict.get("revoked_at"):
                    cred_dict["revoked_at"] = cred_dict["revoked_at"].isoformat()

                # Convert enum values to strings
                if "scopes" in cred_dict:
                    cred_dict["scopes"] = [s.value for s in cred_dict["scopes"]]
                if "credential_type" in cred_dict:
                    cred_dict["credential_type"] = cred_dict["credential_type"].value
                if "status" in cred_dict:
                    cred_dict["status"] = cred_dict["status"].value

                creds_data.append(cred_dict)

            # Write to file
            with open(self.storage_path, "w") as f:
                json.dump({"credentials": creds_data}, f, indent=2)

            self.logger.info(f"Saved {len(self.credentials)} credentials to storage")

        except Exception as e:
            self.logger.exception(f"Failed to save credentials to storage: {e}")

    def _generate_token(
        self,
        credential_type: CredentialType,
        scopes: list[CredentialScope],
        expires_at: datetime,
        metadata: TokenMetadata,
    ) -> str:
        """
        Generate a secure token for the credential.

        Args:
            credential_type: Type of credential
            scopes: List of scopes for the credential
            expires_at: Expiration time
            metadata: Token metadata

        Returns:
            Secure token string
        """
        if credential_type == CredentialType.API_KEY:
            # Generate a random API key with prefix
            prefix = "sk-sophia"
            random_part = secrets.token_hex(16)
            return f"{prefix}-{random_part}"

        elif credential_type in (
            CredentialType.ACCESS_TOKEN,
            CredentialType.SERVICE_TOKEN,
        ):
            # Generate a JWT token
            payload = {
                "jti": str(uuid.uuid4()),
                "iat": datetime.now(UTC).timestamp(),
                "exp": expires_at.timestamp(),
                "scopes": [scope.value for scope in scopes],
                "type": credential_type.value,
            }

            # Add metadata to payload
            if metadata.user_id:
                payload["sub"] = metadata.user_id
            if metadata.service_id:
                payload["service_id"] = metadata.service_id
            if metadata.client_id:
                payload["client_id"] = metadata.client_id

            # Sign the token
            return jwt.encode(payload, self.token_signing_key, algorithm="HS256")

        elif credential_type == CredentialType.SESSION_TOKEN:
            # Generate a session token with high entropy
            token_bytes = secrets.token_bytes(32)
            return base64.urlsafe_b64encode(token_bytes).decode("utf-8")

        else:
            # Default to a secure random token
            return secrets.token_urlsafe(32)

    async def create_credential(
        self,
        request: CredentialRequest,
        created_by: str | None = None,
    ) -> CredentialResponse:
        """
        Create a new ephemeral credential.

        Args:
            request: Credential request
            created_by: ID of the user or service creating the credential

        Returns:
            Credential response with token value
        """
        try:
            # Calculate expiration time
            expires_at = datetime.now(UTC) + timedelta(seconds=request.ttl_seconds)

            # Generate token
            token_value = self._generate_token(
                request.credential_type,
                request.scopes,
                expires_at,
                request.metadata or TokenMetadata(),
            )

            # Create credential
            credential = EphemeralCredential(
                name=request.name,
                credential_type=request.credential_type,
                token_value=token_value,
                scopes=request.scopes,
                expires_at=expires_at,
                created_by=created_by,
                metadata=request.metadata or TokenMetadata(),
            )

            # Store credential
            self.credentials[credential.id] = credential

            # Save to storage if auto-save is enabled
            if self.auto_save:
                self._save_to_storage()

            # Log credential creation
            info(
                AuditEventType.ADMIN_ACTION,
                f"Created ephemeral credential: {credential.name}",
                {
                    "credential_id": credential.id,
                    "credential_type": credential.credential_type.value,
                    "scopes": [scope.value for scope in credential.scopes],
                    "expires_at": credential.expires_at.isoformat(),
                    "created_by": created_by,
                },
            )

            # Return credential response
            return CredentialResponse(
                id=credential.id,
                name=credential.name,
                credential_type=credential.credential_type,
                token_value=credential.token_value,
                scopes=[scope.value for scope in credential.scopes],
                expires_at=credential.expires_at.isoformat(),
                created_at=credential.created_at.isoformat(),
            )

        except Exception as e:
            error(
                AuditEventType.ERROR,
                f"Failed to create ephemeral credential: {e}",
                {"error": str(e)},
            )
            raise

    async def validate_credential(
        self,
        request: CredentialValidationRequest,
    ) -> CredentialValidationResponse:
        """
        Validate an ephemeral credential.

        Args:
            request: Validation request

        Returns:
            Validation response
        """
        try:
            # Find credential by token value
            credential = None
            for cred in self.credentials.values():
                if cred.token_value == request.token_value:
                    credential = cred
                    break

            # If credential not found
            if not credential:
                return CredentialValidationResponse(
                    valid=False,
                    error="Invalid credential",
                )

            # Check if credential is valid
            if not credential.is_valid():
                return CredentialValidationResponse(
                    valid=False,
                    error="Credential is expired or revoked",
                )

            # Check if required scopes are present
            if request.required_scopes:
                required_scope_set = set(request.required_scopes)
                credential_scope_set = set(credential.scopes)

                if not required_scope_set.issubset(credential_scope_set):
                    return CredentialValidationResponse(
                        valid=False,
                        error="Insufficient scopes",
                    )

            # Update last used timestamp
            credential.last_used_at = datetime.now(UTC)

            # Save to storage if auto-save is enabled
            if self.auto_save:
                self._save_to_storage()

            # Return validation response
            return CredentialValidationResponse(
                valid=True,
                credential_id=credential.id,
                scopes=[scope.value for scope in credential.scopes],
                expires_at=credential.expires_at.isoformat(),
            )

        except Exception as e:
            error(
                AuditEventType.ERROR,
                f"Failed to validate ephemeral credential: {e}",
                {"error": str(e)},
            )

            return CredentialValidationResponse(
                valid=False,
                error=f"Validation error: {e!s}",
            )

    async def revoke_credential(
        self,
        request: CredentialRevocationRequest,
        revoked_by: str | None = None,
    ) -> bool:
        """
        Revoke an ephemeral credential.

        Args:
            request: Revocation request
            revoked_by: ID of the user or service revoking the credential

        Returns:
            True if credential was revoked, False otherwise
        """
        try:
            # Find credential by ID
            credential = self.credentials.get(request.credential_id)

            # If credential not found
            if not credential:
                return False

            # Revoke credential
            credential.status = CredentialStatus.REVOKED
            credential.revoked_at = datetime.now(UTC)
            credential.revoked_by = revoked_by

            # Save to storage if auto-save is enabled
            if self.auto_save:
                self._save_to_storage()

            # Log credential revocation
            info(
                AuditEventType.ADMIN_ACTION,
                f"Revoked ephemeral credential: {credential.name}",
                {
                    "credential_id": credential.id,
                    "revoked_by": revoked_by,
                    "reason": request.reason,
                },
            )

            return True

        except Exception as e:
            error(
                AuditEventType.ERROR,
                f"Failed to revoke ephemeral credential: {e}",
                {"error": str(e)},
            )
            return False

    async def get_credential(self, credential_id: str) -> EphemeralCredential | None:
        """
        Get an ephemeral credential by ID.

        Args:
            credential_id: ID of the credential

        Returns:
            Credential if found, None otherwise
        """
        return self.credentials.get(credential_id)

    async def list_credentials(
        self,
        include_expired: bool = False,
        include_revoked: bool = False,
    ) -> list[EphemeralCredential]:
        """
        List all ephemeral credentials.

        Args:
            include_expired: Whether to include expired credentials
            include_revoked: Whether to include revoked credentials

        Returns:
            List of credentials
        """
        result = []

        for credential in self.credentials.values():
            # Skip expired credentials if not included
            if not include_expired and credential.is_expired():
                continue

            # Skip revoked credentials if not included
            if not include_revoked and credential.status == CredentialStatus.REVOKED:
                continue

            result.append(credential)

        return result

    async def cleanup_expired_credentials(self) -> int:
        """
        Clean up expired credentials.

        Returns:
            Number of credentials removed
        """
        now = datetime.now(UTC)
        expired_ids = []

        # Find expired credentials
        for cred_id, credential in self.credentials.items():
            if credential.expires_at <= now:
                expired_ids.append(cred_id)

        # Remove expired credentials
        for cred_id in expired_ids:
            del self.credentials[cred_id]

        # Save to storage if auto-save is enabled
        if self.auto_save and expired_ids:
            self._save_to_storage()

        # Log cleanup
        if expired_ids:
            info(
                AuditEventType.ADMIN_ACTION,
                f"Cleaned up {len(expired_ids)} expired credentials",
                {"expired_count": len(expired_ids)},
            )

        return len(expired_ids)

    async def initialize(self) -> None:
        """Initialize the ephemeral credentials service."""
        # Clean up expired credentials
        await self.cleanup_expired_credentials()

        # Log initialization
        self.logger.info("Ephemeral credentials service initialized")

    async def shutdown(self) -> None:
        """Shut down the ephemeral credentials service."""
        # Save credentials to storage
        self._save_to_storage()

        # Log shutdown
        self.logger.info("Ephemeral credentials service shut down")
