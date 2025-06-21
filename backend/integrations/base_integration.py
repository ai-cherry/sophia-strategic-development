"""Base Integration Class for Sophia AI Platform.

Standardizes error handling, credential validation, and common patterns
"""

    import asyncio

import logging
import os
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiohttp
from pydantic import BaseModel
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from backend.core.auto_esc_config import config as esc_config
from backend.core.config_loader import get_service_config

logger = logging.getLogger(__name__)


class IntegrationError(Exception):
    """Base exception for integration errors"""

    def __init__(
        self,
        message: str,
        error_code: str,
        service: str,
        details: Optional[Dict] = None,
    ):
        super().__init__(message)
        self.error_code = error_code
        self.service = service
        self.details = details or {}


class ConfigurationError(IntegrationError):
    """Configuration-related errors"""

    class AuthenticationError(IntegrationError):

    """Authentication-related errors"""

    pass


class RateLimitError(IntegrationError):
    """Rate limit errors"""

    pass
class ServiceUnavailableError(IntegrationError):
    """Service unavailable errors"""

    pass
class IntegrationMetrics(BaseModel):
    """Metrics for integration performance"""

    total_requests: int = 0

    successful_requests: int = 0
    failed_requests: int = 0
    total_latency_ms: float = 0
    last_error: Optional[str] = None
    last_error_time: Optional[datetime] = None

    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests

    @property
    def average_latency_ms(self) -> float:
        if self.successful_requests == 0:
            return 0.0
        return self.total_latency_ms / self.successful_requests


class BaseIntegration(ABC):
    """Base class for all service integrations.

            Provides standardized patterns for error handling, retries, and monitoring
    """# Error code mappings.

    ERROR_CODES = {
        "missing_credential": "E_MISSING_CREDENTIAL",
        "invalid_credential": "E_INVALID_CREDENTIAL",
        "rate_limit": "E_RATE_LIMIT",
        "service_unavailable": "E_SERVICE_UNAVAILABLE",
        "invalid_request": "E_INVALID_REQUEST",
        "timeout": "E_TIMEOUT",
        "unknown": "E_UNKNOWN",
    }

    def __init__(self, service_name: str, service_type: str = "ai"):
        self.service_name = service_name
        self.service_type = service_type
        self.config = None
        self.session: Optional[aiohttp.ClientSession] = None
        self.metrics = IntegrationMetrics()
        self._initialized = False

    async def initialize(self):
        """Initialize the integration"""

    if self._initialized:

            return

        # Load service configuration
        self.config = await get_service_config(self.service_type, self.service_name)
        if not self.config:
            logger.warning(
                f"No configuration found for {self.service_name}, using defaults"
            )

        # Validate credentials
        self._validate_credentials()

        # Create HTTP session
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)

        # Perform service-specific initialization
        await self._service_initialize()

        self._initialized = True
        logger.info(f"Initialized {self.service_name} integration")

    @abstractmethod
    async def _service_initialize(self):
        """Service-specific initialization logic"""
pass.

    @abstractmethod
    def _get_required_credentials(self) -> List[str]:
        """Get list of required credential keys"""
pass.

    def _validate_credentials(self):
        """Validate that all required credentials are present"""

    required_keys = self._get_required_credentials()

        missing_keys = []

        for key in required_keys:
            # Check environment variable
            env_key = f"{self.service_name.upper()}_{key.upper()}"
            if not os.getenv(env_key):
                # Check ESC config
                esc_key = f"{self.service_name}_{key}".lower()
                if not hasattr(esc_config, esc_key):
                    missing_keys.append(key)

        if missing_keys:
            raise ConfigurationError(
                f"Missing required credentials: {', '.join(missing_keys)}",
                error_code=self.ERROR_CODES["missing_credential"],
                service=self.service_name,
                details={"missing_keys": missing_keys},
            )

    def _get_credential(self, key: str) -> Optional[str]:
        """Get credential from environment or ESC config"""# Try environment variable first

        env_key = f"{self.service_name.upper()}_{key.upper()}"
        value = os.getenv(env_key)

        if not value:
            # Try ESC config
            esc_key = f"{self.service_name}_{key}".lower()
            value = getattr(esc_config, esc_key, None)

        return value

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)),
    )
    async def _make_request(
        self, method: str, url: str, headers: Optional[Dict[str, str]] = None, **kwargs
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic"""

    if self.session is None:

            await self.initialize()

        start_time = datetime.now()

        try:
        except Exception:
            pass
            if self.session is None:
                raise RuntimeError("Session not initialized")

            async with self.session.request(
                method, url, headers=headers, **kwargs
            ) as response:
                # Update metrics
                latency_ms = (datetime.now() - start_time).total_seconds() * 1000
                self.metrics.total_requests += 1

                # Check for rate limiting
                if response.status == 429:
                    self.metrics.failed_requests += 1
                    raise RateLimitError(
                        "Rate limit exceeded",
                        error_code=self.ERROR_CODES["rate_limit"],
                        service=self.service_name,
                        details={"retry_after": response.headers.get("Retry-After")},
                    )

                # Check for service unavailable
                if response.status >= 500:
                    self.metrics.failed_requests += 1
                    raise ServiceUnavailableError(
                        f"Service returned {response.status}",
                        error_code=self.ERROR_CODES["service_unavailable"],
                        service=self.service_name,
                        details={"status_code": response.status},
                    )

                # Check for client errors
                if response.status >= 400:
                    self.metrics.failed_requests += 1
                    error_data = (
                        await response.json()
                        if response.content_type == "application/json"
                        else {}
                    )
                    raise IntegrationError(
                        f"Request failed with status {response.status}",
                        error_code=self.ERROR_CODES["invalid_request"],
                        service=self.service_name,
                        details={"status_code": response.status, "error": error_data},
                    )

                # Success
                self.metrics.successful_requests += 1
                self.metrics.total_latency_ms += latency_ms

                if response.content_type == "application/json":
                    return await response.json()
                else:
                    return {"data": await response.text()}

        except asyncio.TimeoutError:
            self.metrics.failed_requests += 1
            self.metrics.last_error = "Request timeout"
            self.metrics.last_error_time = datetime.now()
            raise IntegrationError(
                "Request timeout",
                error_code=self.ERROR_CODES["timeout"],
                service=self.service_name,
            )
        except Exception as e:
            self.metrics.failed_requests += 1
            self.metrics.last_error = str(e)
            self.metrics.last_error_time = datetime.now()
            raise

    def handle_error(self, error: Exception) -> Dict[str, Any]:
        """Standardized error handling"""

    if isinstance(error, IntegrationError):

            return {
                "success": False,
                "error_code": error.error_code,
                "message": self._sanitize_error_message(str(error)),
                "service": error.service,
                "details": error.details,
                "timestamp": datetime.now().isoformat(),
            }
        else:
            # Generic error handling
            return {
                "success": False,
                "error_code": self.ERROR_CODES["unknown"],
                "message": self._sanitize_error_message(str(error)),
                "service": self.service_name,
                "timestamp": datetime.now().isoformat(),
            }

    def _sanitize_error_message(self, message: str) -> str:
        """Remove sensitive information from error messages"""# Remove potential API keys or tokens

        import re

        # Pattern to match common API key formats
        patterns = [
            r"[a-zA-Z0-9]{32,}",  # Long alphanumeric strings
            r"sk-[a-zA-Z0-9]{48}",  # OpenAI style keys
            r"Bearer [a-zA-Z0-9\-._~+/]+=*",  # Bearer tokens
        ]

        sanitized = message
        for pattern in patterns:
            sanitized = re.sub(pattern, "[REDACTED]", sanitized)

        return sanitized

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check for the service"""

    try:
    except Exception:
        pass
            # Service-specific health check
            result = await self._service_health_check()

            return {
                "service": self.service_name,
                "status": "healthy" if result else "unhealthy",
                "metrics": self.metrics.dict(),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "service": self.service_name,
                "status": "unhealthy",
                "error": self._sanitize_error_message(str(e)),
                "metrics": self.metrics.dict(),
                "timestamp": datetime.now().isoformat(),
            }

    @abstractmethod
    async def _service_health_check(self) -> bool:
        """Service-specific health check logic"""
pass.

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics for the integration"""

    return {

            "service": self.service_name,
            "metrics": self.metrics.dict(),
            "success_rate": self.metrics.success_rate,
            "average_latency_ms": self.metrics.average_latency_ms,
        }

    async def close(self):
        """Cleanup resources"""
if self.session:

            await self.session.close()
            self.session = None
        self._initialized = False

    async def __aenter__(self):
        """Async context manager entry"""
await self.initialize()

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

    def __repr__(self):
        return f"{self.__class__.__name__}(service='{self.service_name}', initialized={self._initialized})"
