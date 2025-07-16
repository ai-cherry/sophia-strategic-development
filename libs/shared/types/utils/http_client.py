"""
Centralized HTTP client for Sophia AI
Provides common patterns for API calls, retries, and error handling
"""

import asyncio
import logging
from typing import Any, Optional
from urllib.parse import urljoin

import aiohttp
from aiohttp import ClientSession, ClientTimeout

from shared.utils.errors import (
    APIError,
    AuthenticationError,
    ConnectionError,
    RateLimitError,
)

logger = logging.getLogger(__name__)

class HTTPClient:
    """Async HTTP client with retry logic and error handling"""

    def __init__(
        self,
        base_url: Optional[str] = None,
        headers: Optional[dict[str, str]] = None,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        max_retry_delay: float = 60.0,
    ):
        self.base_url = base_url
        self.headers = headers or {}
        self.timeout = ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.max_retry_delay = max_retry_delay
        self._session: Optional[ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

    async def _ensure_session(self):
        """Ensure we have an active session"""
        if not self._session or self._session.closed:
            self._session = ClientSession(headers=self.headers, timeout=self.timeout)

    async def close(self):
        """Close the HTTP session"""
        if self._session and not self._session.closed:
            await self._session.close()

    def _get_full_url(self, endpoint: str) -> str:
        """Get full URL for an endpoint"""
        if self.base_url:
            return urljoin(self.base_url, endpoint)
        return endpoint

    async def _handle_response(self, response: aiohttp.ClientResponse) -> Any:
        """Handle HTTP response and errors"""
        if response.status == 401:
            raise AuthenticationError(
                message="Authentication failed", service=self.base_url
            )

        if response.status == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                message="Rate limit exceeded",
                retry_after=int(retry_after) if retry_after else None,
                service=self.base_url,
            )

        if response.status >= 400:
            try:
                error_data = await response.json()
                message = error_data.get("message", str(error_data))
            except:
                message = await response.text()

            raise APIError(
                message=message, status_code=response.status, service=self.base_url
            )

        # Try to parse JSON response
        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type:
            return await response.json()
        else:
            return await response.text()

    async def _request_with_retry(self, method: str, url: str, **kwargs) -> Any:
        """Make HTTP request with retry logic"""
        await self._ensure_session()

        if not self._session:
            raise ConnectionError("Failed to create HTTP session")

        last_error: Optional[Exception] = None
        delay = self.retry_delay

        for attempt in range(self.max_retries + 1):
            try:
                async with self._session.request(method, url, **kwargs) as response:
                    return await self._handle_response(response)

            except RateLimitError as e:
                # If we have a retry_after, use it
                if e.retry_after:
                    delay = min(e.retry_after, self.max_retry_delay)
                last_error = e

            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                last_error = ConnectionError(
                    message=f"Request failed: {e!s}",
                    service=self.base_url,
                    retry_count=attempt,
                )

            except Exception:
                # Don't retry on other exceptions
                raise

            # Don't sleep on the last attempt
            if attempt < self.max_retries:
                logger.warning(
                    f"Request failed (attempt {attempt + 1}/{self.max_retries + 1}), "
                    f"retrying in {delay}s: {last_error}"
                )
                await asyncio.sleep(delay)
                # Exponential backoff
                delay = min(delay * 2, self.max_retry_delay)

        # All retries exhausted
        if last_error:
            raise last_error
        else:
            raise ConnectionError("Request failed after all retries")

    async def get(self, endpoint: str, **kwargs) -> Any:
        """Make GET request"""
        url = self._get_full_url(endpoint)
        return await self._request_with_retry("GET", url, **kwargs)

    async def post(
        self, endpoint: str, json: Any = None, data: Any = None, **kwargs
    ) -> Any:
        """Make POST request"""
        url = self._get_full_url(endpoint)
        return await self._request_with_retry(
            "POST", url, json=json, data=data, **kwargs
        )

    async def put(
        self, endpoint: str, json: Any = None, data: Any = None, **kwargs
    ) -> Any:
        """Make PUT request"""
        url = self._get_full_url(endpoint)
        return await self._request_with_retry(
            "PUT", url, json=json, data=data, **kwargs
        )

    async def delete(self, endpoint: str, **kwargs) -> Any:
        """Make DELETE request"""
        url = self._get_full_url(endpoint)
        return await self._request_with_retry("DELETE", url, **kwargs)

    async def patch(
        self, endpoint: str, json: Any = None, data: Any = None, **kwargs
    ) -> Any:
        """Make PATCH request"""
        url = self._get_full_url(endpoint)
        return await self._request_with_retry(
            "PATCH", url, json=json, data=data, **kwargs
        )

class APIClient(HTTPClient):
    """Enhanced API client with authentication and service-specific features"""

    def __init__(self, service_name: str, api_key: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.service_name = service_name

        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

    def with_api_key(self, api_key: str) -> "APIClient":
        """Set API key for authentication"""
        self.headers["Authorization"] = f"Bearer {api_key}"
        return self

    def with_header(self, key: str, value: str) -> "APIClient":
        """Add custom header"""
        self.headers[key] = value
        return self
