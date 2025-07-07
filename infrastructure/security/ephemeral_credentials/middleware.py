"""
Ephemeral Credentials Middleware for Sophia AI Platform.

This module provides middleware for authenticating requests using ephemeral credentials.
"""

from __future__ import annotations

import logging
from collections.abc import Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from infrastructure.security.audit_logger import AuditEventType, error, info
from infrastructure.security.ephemeral_credentials.models import (
    CredentialScope,
    CredentialValidationRequest,
)
from infrastructure.security.ephemeral_credentials.service import EphemeralCredentialsService

logger = logging.getLogger(__name__)


class EphemeralCredentialsMiddleware(BaseHTTPMiddleware):
    """
    Middleware for authenticating requests using ephemeral credentials.

    This middleware extracts credentials from request headers and validates them
    against the ephemeral credentials service. If valid, it adds the credential
    information to the request state for use by downstream handlers.
    """

    def __init__(
        self,
        app: FastAPI,
        credentials_service: EphemeralCredentialsService,
        exclude_paths: list[str] = None,
        required_scopes_by_path: dict[str, list[CredentialScope]] = None,
    ):
        """
        Initialize the middleware.

        Args:
            app: FastAPI application
            credentials_service: Ephemeral credentials service
            exclude_paths: List of paths to exclude from authentication
            required_scopes_by_path: Dictionary mapping paths to required scopes
        """
        super().__init__(app)
        self.credentials_service = credentials_service
        self.exclude_paths = exclude_paths or [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/auth",
        ]
        self.required_scopes_by_path = required_scopes_by_path or {}
        self.logger = logger.bind(component="ephemeral_credentials_middleware")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and authenticate using ephemeral credentials.

        Args:
            request: FastAPI request
            call_next: Next middleware or route handler

        Returns:
            Response from next middleware or route handler
        """
        # Skip authentication for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        # Extract token from headers
        token = self._extract_token(request)

        # If no token found, continue without authentication
        if not token:
            # For paths that require authentication, return 401
            if self._path_requires_auth(request.url.path):
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Authentication required"},
                )

            # Otherwise, continue without authentication
            return await call_next(request)

        # Validate token
        validation_result = await self.credentials_service.validate_credential(
            request=CredentialValidationRequest(
                token_value=token,
                required_scopes=self._get_required_scopes(request.url.path),
            )
        )

        # If token is invalid, return 401
        if not validation_result.valid:
            error(
                AuditEventType.ACCESS_DENIED,
                "Invalid credential",
                {
                    "path": request.url.path,
                    "method": request.method,
                    "error": validation_result.error,
                    "ip": request.client.host if request.client else None,
                },
            )

            return JSONResponse(
                status_code=401,
                content={"detail": validation_result.error or "Invalid credential"},
            )

        # Add credential info to request state
        request.state.credential_id = validation_result.credential_id
        request.state.credential_scopes = validation_result.scopes

        # Log successful authentication
        info(
            AuditEventType.ACCESS_GRANTED,
            "Authenticated with ephemeral credential",
            {
                "credential_id": validation_result.credential_id,
                "path": request.url.path,
                "method": request.method,
                "ip": request.client.host if request.client else None,
            },
        )

        # Continue with request
        return await call_next(request)

    def _extract_token(self, request: Request) -> str | None:
        """
        Extract token from request headers.

        Args:
            request: FastAPI request

        Returns:
            Token if found, None otherwise
        """
        # Try Authorization header (Bearer token)
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header[7:]  # Remove "Bearer " prefix

        # Try X-API-Key header
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return api_key

        # No token found
        return None

    def _path_requires_auth(self, path: str) -> bool:
        """
        Check if the path requires authentication.

        Args:
            path: Request path

        Returns:
            True if authentication is required, False otherwise
        """
        # Public paths don't require authentication
        if any(path.startswith(excluded) for excluded in self.exclude_paths):
            return False

        # API paths require authentication
        if path.startswith("/api/"):
            return True

        # Other paths don't require authentication
        return False

    def _get_required_scopes(self, path: str) -> list[CredentialScope] | None:
        """
        Get required scopes for the path.

        Args:
            path: Request path

        Returns:
            List of required scopes if any, None otherwise
        """
        # Check for exact path match
        if path in self.required_scopes_by_path:
            return self.required_scopes_by_path[path]

        # Check for prefix match
        for prefix, scopes in self.required_scopes_by_path.items():
            if path.startswith(prefix):
                return scopes

        # No specific scopes required
        return None


def setup_ephemeral_credentials_middleware(
    app: FastAPI,
    credentials_service: EphemeralCredentialsService | None = None,
    exclude_paths: list[str] | None = None,
    required_scopes_by_path: dict[str, list[CredentialScope]] | None = None,
) -> None:
    """
    Set up ephemeral credentials middleware for a FastAPI application.

    Args:
        app: FastAPI application
        credentials_service: Ephemeral credentials service (created if not provided)
        exclude_paths: List of paths to exclude from authentication
        required_scopes_by_path: Dictionary mapping paths to required scopes
    """
    # Create credentials service if not provided
    if credentials_service is None:
        credentials_service = EphemeralCredentialsService()

    # Default exclude paths
    if exclude_paths is None:
        exclude_paths = [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/auth",
            "/api/v1/health",
            "/api/v1/metrics",
        ]

    # Default required scopes by path
    if required_scopes_by_path is None:
        required_scopes_by_path = {
            "/api/v1/credentials": [CredentialScope.SYSTEM_ADMIN],
            "/api/v1/llm": [CredentialScope.LLM_ACCESS],
            "/api/v1/agent": [CredentialScope.AGENT_ACCESS],
            "/api/v1/document": [CredentialScope.DOCUMENT_READ],
            "/api/v1/kb": [CredentialScope.KB_READ],
        }

    # Add middleware
    app.add_middleware(
        EphemeralCredentialsMiddleware,
        credentials_service=credentials_service,
        exclude_paths=exclude_paths,
        required_scopes_by_path=required_scopes_by_path,
    )

    # Log middleware setup
    logger.info("✅ Ephemeral credentials middleware configured")
