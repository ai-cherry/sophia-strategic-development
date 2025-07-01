"""
Audit Middleware for FastAPI

Provides automatic audit logging for all API requests and responses.
Integrates with the audit_logger module to provide comprehensive security logging.

Key Features:
- Request and response logging
- Performance metrics
- Error tracking
- User and session context tracking
- PII protection
"""

import time
import uuid
from collections.abc import Callable

from fastapi import FastAPI, Request, Response
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from backend.security.audit_logger import (
    AuditEventType,
    clear_request_context,
    error,
    info,
    set_request_context,
)


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware for auditing FastAPI requests and responses.

    Automatically logs all API requests and responses with appropriate context.
    """

    def __init__(
        self,
        app: ASGIApp,
        exclude_paths: list[str] | None = None,
        exclude_methods: list[str] | None = None,
        log_request_body: bool = False,
        log_response_body: bool = False,
        log_headers: bool = True,
        exclude_headers: list[str] | None = None,
    ):
        super().__init__(app)
        self.exclude_paths = exclude_paths or ["/health", "/metrics", "/favicon.ico"]
        self.exclude_methods = exclude_methods or ["OPTIONS"]
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.log_headers = log_headers
        self.exclude_headers = [h.lower() for h in (exclude_headers or [
            "authorization", "cookie", "set-cookie", "x-api-key"
        ])]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip excluded paths and methods
        if request.url.path in self.exclude_paths or request.method in self.exclude_methods:
            return await call_next(request)

        # Generate request ID
        request_id = str(uuid.uuid4())

        # Extract user information from request
        user_id = self._extract_user_id(request)
        session_id = self._extract_session_id(request)

        # Set request context for audit logging
        set_request_context(
            user_id=user_id,
            session_id=session_id,
            request_id=request_id,
            ip_address=self._get_client_ip(request),
            user_agent=request.headers.get("user-agent"),
        )

        # Prepare request details
        request_details = {
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
        }

        # Add headers if enabled
        if self.log_headers:
            request_details["headers"] = self._filter_headers(request.headers)

        # Add request body if enabled
        if self.log_request_body:
            try:
                # Clone the request body for logging
                body = await request.body()
                request_details["body"] = body.decode("utf-8")
                # Reset the request body for further processing
                await request._receive()
            except Exception:
                request_details["body"] = "<error reading body>"

        # Log request
        info(
            AuditEventType.DATA_READ,
            f"API Request: {request.method} {request.url.path}",
            request_details,
        )

        # Track timing
        start_time = time.time()

        try:
            # Process the request
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Prepare response details
            response_details = {
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
            }

            # Add headers if enabled
            if self.log_headers:
                response_details["headers"] = self._filter_headers(response.headers)

            # Add response body if enabled
            if self.log_response_body:
                try:
                    # This is tricky as we can't easily access the response body
                    # We would need to modify the response to capture its body
                    pass
                except Exception:
                    response_details["body"] = "<error reading body>"

            # Log response
            info(
                AuditEventType.DATA_READ,
                f"API Response: {response.status_code} for {request.method} {request.url.path}",
                response_details,
            )

            return response

        except Exception as e:
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log error
            error(
                AuditEventType.ERROR,
                f"API Error: {str(e)} for {request.method} {request.url.path}",
                {
                    "error": str(e),
                    "duration_ms": round(duration_ms, 2),
                },
            )

            # Re-raise the exception
            raise

        finally:
            # Clear request context
            clear_request_context()

    def _extract_user_id(self, request: Request) -> str:
        """Extract user ID from request"""
        # Try to get from authorization header
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            # This is a simplified example - in a real system, you would
            # decode and validate the JWT token to get the user ID
            return "user_from_token"

        # Try to get from session cookie
        session = request.cookies.get("session")
        if session:
            # In a real system, you would decode and validate the session
            return "user_from_session"

        # Default to anonymous
        return "anonymous"

    def _extract_session_id(self, request: Request) -> str | None:
        """Extract session ID from request"""
        # Try to get from session cookie
        return request.cookies.get("session")

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request"""
        # Check for X-Forwarded-For header
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # The client IP is the first address in the list
            return forwarded_for.split(",")[0].strip()

        # Fall back to direct client address
        return request.client.host if request.client else "unknown"

    def _filter_headers(self, headers: dict[str, str]) -> dict[str, str]:
        """Filter sensitive headers"""
        return {
            k: v if k.lower() not in self.exclude_headers else "[REDACTED]"
            for k, v in headers.items()
        }


def setup_audit_middleware(app: FastAPI):
    """
    Set up audit middleware for a FastAPI application.

    Args:
        app: FastAPI application instance
    """
    # Add audit middleware
    app.add_middleware(
        AuditMiddleware,
        exclude_paths=["/health", "/metrics", "/favicon.ico"],
        exclude_methods=["OPTIONS"],
        log_request_body=False,
        log_response_body=False,
        log_headers=True,
    )

    # Log application startup
    @app.on_event("startup")
    async def startup_event():
        info(
            AuditEventType.SYSTEM_START,
            "API server started",
            {"app_name": app.title},
        )

    # Log application shutdown
    @app.on_event("shutdown")
    async def shutdown_event():
        info(
            AuditEventType.SYSTEM_STOP,
            "API server stopped",
            {"app_name": app.title},
        )


class AuditRoute(APIRoute):
    """
    Custom API route that adds audit logging.

    This is an alternative to the middleware approach, which logs at the
    individual route level instead of for all requests.
    """

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def audit_route_handler(request: Request) -> Response:
            # Generate request ID
            request_id = str(uuid.uuid4())

            # Extract user information from request
            user_id = self._extract_user_id(request)
            session_id = request.cookies.get("session")

            # Set request context for audit logging
            set_request_context(
                user_id=user_id,
                session_id=session_id,
                request_id=request_id,
                ip_address=self._get_client_ip(request),
                user_agent=request.headers.get("user-agent"),
            )

            # Log request
            info(
                AuditEventType.DATA_READ,
                f"API Request: {request.method} {request.url.path}",
                {
                    "method": request.method,
                    "path": request.url.path,
                    "query_params": dict(request.query_params),
                },
            )

            # Track timing
            start_time = time.time()

            try:
                # Process the request
                response = await original_route_handler(request)

                # Calculate duration
                duration_ms = (time.time() - start_time) * 1000

                # Log response
                info(
                    AuditEventType.DATA_READ,
                    f"API Response: {getattr(response, 'status_code', 200)} for {request.method} {request.url.path}",
                    {
                        "status_code": getattr(response, "status_code", 200),
                        "duration_ms": round(duration_ms, 2),
                    },
                )

                return response

            except Exception as e:
                # Calculate duration
                duration_ms = (time.time() - start_time) * 1000

                # Log error
                error(
                    AuditEventType.ERROR,
                    f"API Error: {str(e)} for {request.method} {request.url.path}",
                    {
                        "error": str(e),
                        "duration_ms": round(duration_ms, 2),
                    },
                )

                # Re-raise the exception
                raise

            finally:
                # Clear request context
                clear_request_context()

        return audit_route_handler

    def _extract_user_id(self, request: Request) -> str:
        """Extract user ID from request"""
        # Try to get from authorization header
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            # This is a simplified example - in a real system, you would
            # decode and validate the JWT token to get the user ID
            return "user_from_token"

        # Try to get from session cookie
        session = request.cookies.get("session")
        if session:
            # In a real system, you would decode and validate the session
            return "user_from_session"

        # Default to anonymous
        return "anonymous"

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request"""
        # Check for X-Forwarded-For header
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # The client IP is the first address in the list
            return forwarded_for.split(",")[0].strip()

        # Fall back to direct client address
        return request.client.host if request.client else "unknown"

