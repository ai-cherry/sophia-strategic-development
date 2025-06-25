"""
Gong API Client - Handles all interactions with the Gong API.

Provides rate-limited, retry-enabled access to Gong API endpoints for
data enhancement and retrieval.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import aiohttp
import structlog
from pydantic import BaseModel, Field

from backend.integrations.gong_webhook_server import (
    AsyncRateLimiter,
    RateLimitError,
    RetryManager,
    api_calls_total,
    api_rate_limit_hits,
)

logger = structlog.get_logger()


class GongCallData(BaseModel):
    """Enhanced call data from Gong API."""

    call_id: str
    title: str
    scheduled_start: datetime
    started: datetime
    duration: int
    primary_user_id: str
    direction: str
    is_video: bool
    language: str
    purpose: Optional[str] = None
    meeting_url: Optional[str] = None
    participants: List[Dict[str, Any]] = Field(default_factory=list)
    transcript: Optional[Dict[str, Any]] = None
    topics: List[Dict[str, Any]] = Field(default_factory=list)
    trackers: List[Dict[str, Any]] = Field(default_factory=list)
    summary: Optional[Dict[str, Any]] = None
    action_items: List[Dict[str, Any]] = Field(default_factory=list)


class GongCallTranscript(BaseModel):
    """Call transcript data."""

    call_id: str
    transcript_url: Optional[str] = None
    sentences: List[Dict[str, Any]] = Field(default_factory=list)
    topics: List[Dict[str, Any]] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)


class GongCallAnalytics(BaseModel):
    """Call analytics data."""

    call_id: str
    talk_ratio: Optional[float] = None
    longest_monologue: Optional[int] = None
    interactivity: Optional[float] = None
    patience: Optional[float] = None
    questions_asked: Optional[int] = None
    sentiment_score: Optional[float] = None
    engagement_score: Optional[float] = None


class GongAPIError(Exception):
    """Exception raised for Gong API errors."""

    def __init__(
        self, status_code: int, message: str, details: Optional[Dict[str, Any]] = None
    ):
        self.status_code = status_code
        self.message = message
        self.details = details or {}
        super().__init__(f"Gong API Error ({status_code}): {message}")


class GongAPIClient:
    """Client for interacting with the Gong API."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.gong.io",
        rate_limit: float = 2.5,
        burst_limit: int = 10,
        timeout: int = 30,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.rate_limiter = AsyncRateLimiter(rate_limit, burst_limit=burst_limit)
        self.retry_manager = RetryManager()
        self.logger = logger.bind(component="gong_api_client")
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def _ensure_session(self):
        """Ensure aiohttp session is created."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )

    async def close(self):
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        retry: bool = True,
    ) -> Dict[str, Any]:
        """Make a rate-limited API request."""
        await self._ensure_session()

        url = urljoin(self.base_url, endpoint)

        async def _request():
            async with self.rate_limiter:
                self.logger.info(f"Making {method} request", url=url, params=params)

                async with self._session.request(
                    method, url, params=params, json=json_data
                ) as response:
                    response_data = await response.json()

                    if response.status == 200:
                        api_calls_total.labels(
                            endpoint=endpoint, status="success"
                        ).inc()
                        return response_data

                    # Handle rate limiting
                    if response.status == 429:
                        api_rate_limit_hits.inc()
                        retry_after = int(response.headers.get("Retry-After", 60))
                        raise RateLimitError(retry_after)

                    # Handle other errors
                    api_calls_total.labels(endpoint=endpoint, status="error").inc()
                    error_message = response_data.get("message", "Unknown error")
                    raise GongAPIError(response.status, error_message, response_data)

        # Use retry manager if enabled
        if retry:
            return await self.retry_manager.exponential_backoff(_request)
        else:
            return await _request()

    async def get_call(self, call_id: str) -> GongCallData:
        """Get detailed call information."""
        self.logger.info("Fetching call data", call_id=call_id)

        response = await self._make_request("GET", f"/v2/calls/{call_id}")

        call_data = response.get("call", {})

        # Parse and structure the call data
        return GongCallData(
            call_id=call_data.get("id", call_id),
            title=call_data.get("title", ""),
            scheduled_start=datetime.fromisoformat(call_data.get("scheduledStart", "")),
            started=datetime.fromisoformat(call_data.get("started", "")),
            duration=call_data.get("duration", 0),
            primary_user_id=call_data.get("primaryUserId", ""),
            direction=call_data.get("direction", ""),
            is_video=call_data.get("isVideo", False),
            language=call_data.get("language", ""),
            purpose=call_data.get("purpose"),
            meeting_url=call_data.get("meetingUrl"),
            participants=call_data.get("participants", []),
            transcript=call_data.get("transcript"),
            topics=call_data.get("topics", []),
            trackers=call_data.get("trackers", []),
            summary=call_data.get("summary"),
            action_items=call_data.get("actionItems", []),
        )

    async def get_call_transcript(self, call_id: str) -> GongCallTranscript:
        """Get call transcript."""
        self.logger.info("Fetching call transcript", call_id=call_id)

        response = await self._make_request("GET", f"/v2/calls/{call_id}/transcript")

        transcript_data = response.get("callTranscript", {})

        return GongCallTranscript(
            call_id=call_id,
            transcript_url=transcript_data.get("url"),
            sentences=transcript_data.get("sentences", []),
            topics=transcript_data.get("topics", []),
            keywords=transcript_data.get("keywords", []),
        )

    async def get_call_analytics(self, call_id: str) -> GongCallAnalytics:
        """Get call analytics and insights."""
        self.logger.info("Fetching call analytics", call_id=call_id)

        response = await self._make_request("GET", f"/v2/calls/{call_id}/analytics")

        analytics = response.get("analytics", {})

        return GongCallAnalytics(
            call_id=call_id,
            talk_ratio=analytics.get("talkRatio"),
            longest_monologue=analytics.get("longestMonologue"),
            interactivity=analytics.get("interactivity"),
            patience=analytics.get("patience"),
            questions_asked=analytics.get("questionsAsked"),
            sentiment_score=analytics.get("sentimentScore"),
            engagement_score=analytics.get("engagementScore"),
        )

    async def get_call_participants(self, call_id: str) -> List[Dict[str, Any]]:
        """Get detailed participant information."""
        self.logger.info("Fetching call participants", call_id=call_id)

        response = await self._make_request("GET", f"/v2/calls/{call_id}/participants")

        return response.get("participants", [])

    async def list_calls(
        self,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        cursor: Optional[str] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """List calls with optional filters."""
        params = {"limit": min(limit, 100)}  # API max is 100

        if from_date:
            params["fromDateTime"] = from_date.isoformat()

        if to_date:
            params["toDateTime"] = to_date.isoformat()

        if cursor:
            params["cursor"] = cursor

        response = await self._make_request("GET", "/v2/calls", params=params)

        return {
            "calls": response.get("calls", []),
            "cursor": response.get("cursor"),
            "has_more": response.get("hasMore", False),
        }

    async def enhance_call_data(self, call_id: str) -> Dict[str, Any]:
        """Enhance call data with all available information."""
        self.logger.info("Enhancing call data", call_id=call_id)

        # Fetch all data in parallel where possible
        tasks = {
            "call": self.get_call(call_id),
            "transcript": self.get_call_transcript(call_id),
            "analytics": self.get_call_analytics(call_id),
            "participants": self.get_call_participants(call_id),
        }

        results = {}
        for name, task in tasks.items():
            try:
                results[name] = await task
            except GongAPIError as e:
                self.logger.warning(
                    f"Failed to fetch {name} data", call_id=call_id, error=str(e)
                )
                results[name] = None
            except Exception as e:
                self.logger.error(
                    f"Unexpected error fetching {name} data",
                    call_id=call_id,
                    error=str(e),
                )
                results[name] = None

        # Combine all data
        enhanced_data = {
            "call_id": call_id,
            "enhanced_at": datetime.now(timezone.utc).isoformat(),
            "call_data": results["call"].dict() if results["call"] else None,
            "transcript": (
                results["transcript"].dict() if results["transcript"] else None
            ),
            "analytics": results["analytics"].dict() if results["analytics"] else None,
            "participants": results["participants"] if results["participants"] else [],
        }

        return enhanced_data

    async def get_user(self, user_id: str) -> Dict[str, Any]:
        """Get user information."""
        response = await self._make_request("GET", f"/v2/users/{user_id}")

        return response.get("user", {})

    async def get_email_content(self, email_id: str) -> Dict[str, Any]:
        """Get email content and metadata."""
        response = await self._make_request("GET", f"/v2/emails/{email_id}")

        return response.get("email", {})

    async def get_meeting_details(self, meeting_id: str) -> Dict[str, Any]:
        """Get meeting details and attendees."""
        response = await self._make_request("GET", f"/v2/meetings/{meeting_id}")

        return response.get("meeting", {})
