"""
Gong Webhook Server - Production-ready FastAPI webhook processor for Gong integrations.

This server processes Gong webhooks, enhances data via API calls, stores in Qdrant,
and notifies Sophia agents via Redis pub/sub.
"""

from backend.services.unified_memory_service_v3 import UnifiedMemoryServiceV3
from __future__ import annotations

import asyncio
import time
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import jwt
import structlog
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Gauge, Histogram, generate_latest
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

from infrastructure.integrations.gong_webhook_processor import WebhookProcessor

# Import shared error classes
from shared.utils.errors import RateLimitError

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Prometheus metrics
webhook_requests_total = Counter(
    "webhook_requests_total", "Total webhook requests", ["endpoint", "status"]
)
webhook_processing_duration = Histogram(
    "webhook_processing_duration_seconds", "Webhook processing duration"
)
api_calls_total = Counter(
    "gong_api_calls_total", "Total Gong API calls", ["endpoint", "status"]
)
api_rate_limit_hits = Counter("gong_api_rate_limit_hits_total", "Rate limit hits")
data_quality_score = Gauge("data_quality_score", "Current data quality score")
validation_failures = Counter(
    "validation_failures_total", "Data validation failures", ["type"]
)
active_background_tasks = Gauge(
    "active_background_tasks", "Number of active background tasks"
)


class WebhookServerConfig(BaseSettings):
    """Configuration for the Gong webhook server."""

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8080
    WORKERS: int = 4

    # Gong API settings
    GONG_API_BASE_URL: str = "https://api.gong.io"
    GONG_API_KEY: str = Field(..., env="GONG_API_KEY")
    GONG_WEBHOOK_SECRETS: list[str] = Field(..., env="GONG_WEBHOOK_SECRETS")

    # Rate limiting
    GONG_API_RATE_LIMIT: float = 2.5
    GONG_API_BURST_LIMIT: int = 10

    # Database settings
    
    
    
    
    
    

    # Redis settings
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")

    # Processing settings
    MAX_RETRY_ATTEMPTS: int = 5
    INITIAL_RETRY_DELAY: float = 1.0
    MAX_RETRY_DELAY: float = 300.0
    WEBHOOK_TIMEOUT_SECONDS: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global configuration instance for lazy initialization
_server_config: WebhookServerConfig | None = None


def get_server_config() -> WebhookServerConfig:
    """Get the global server configuration instance with lazy initialization"""
    global _server_config
    if _server_config is None:
        _server_config = WebhookServerConfig()
    return _server_config


# Pydantic models for webhook data
class GongWebhookBase(BaseModel):
    """Base model for Gong webhook data."""

    webhook_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: str
    event_timestamp: datetime
    object_id: str
    object_type: str


class GongCallWebhook(GongWebhookBase):
    """Model for Gong call webhooks."""

    call_id: str
    call_start_time: datetime
    duration: int
    participants: list[dict[str, Any]]
    recording_url: str | None = None


class GongEmailWebhook(GongWebhookBase):
    """Model for Gong email webhooks."""

    email_id: str
    subject: str
    sender: str
    recipients: list[str]
    sent_time: datetime


class GongMeetingWebhook(GongWebhookBase):
    """Model for Gong meeting webhooks."""

    meeting_id: str
    title: str
    start_time: datetime
    end_time: datetime
    attendees: list[dict[str, Any]]


class WebhookVerificationError(Exception):
    """Exception raised when webhook verification fails."""

    pass


class ValidationResult(BaseModel):
    """Result of data validation."""

    is_valid: bool
    quality_score: float
    issues: list[str]


class ProcessingResult(BaseModel):
    """Result of webhook processing."""

    webhook_id: str
    status: str
    processing_time: float
    error: str | None = None


# JWT Webhook Verification
class GongWebhookVerifier:
    """Verifies Gong webhook signatures using JWT."""

    def __init__(self, webhook_secrets: list[str]):
        self.secrets = webhook_secrets
        self.logger = logger.bind(component="webhook_verifier")

    async def verify_signature(self, request: Request) -> bool:
        """Verify the JWT signature of the webhook request."""
        try:
            # Extract JWT token from headers
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                raise WebhookVerificationError(
                    "Missing or invalid Authorization header"
                )

            token = auth_header.replace("Bearer ", "")

            # Try to verify with each secret (for rotation support)
            verified = False
            decoded_payload = None

            for secret in self.secrets:
                try:
                    decoded_payload = jwt.decode(
                        token,
                        secret,
                        algorithms=["HS256"],
                        options={"verify_exp": True},
                    )
                    verified = True
                    break
                except jwt.InvalidTokenError:
                    continue

            if not verified:
                raise WebhookVerificationError("Invalid webhook signature")

            # Validate timestamp to prevent replay attacks (5-minute window)
            if "iat" in decoded_payload:
                issued_at = datetime.fromtimestamp(decoded_payload["iat"], tz=UTC)
                now = datetime.now(tz=UTC)
                if abs((now - issued_at).total_seconds()) > 300:
                    raise WebhookVerificationError(
                        "Webhook timestamp outside acceptable window"
                    )

            # Validate required claims
            required_claims = ["sub", "iat", "exp"]
            for claim in required_claims:
                if claim not in decoded_payload:
                    raise WebhookVerificationError(f"Missing required claim: {claim}")

            self.logger.info(
                "Webhook signature verified successfully",
                subject=decoded_payload.get("sub"),
            )
            return True

        except WebhookVerificationError:
            raise
        except Exception as e:
            self.logger.exception("Webhook verification failed", error=str(e))
            raise WebhookVerificationError(f"Verification failed: {e!s}")


# Rate Limiter
class AsyncRateLimiter:
    """Async rate limiter with burst support."""

    def __init__(
        self, max_calls: float, time_window: float = 1.0, burst_limit: int = 10
    ):
        self.max_calls = max_calls
        self.time_window = time_window
        self.burst_limit = burst_limit
        self.calls = []
        self.lock = asyncio.Lock()

    async def __aenter__(self):
        async with self.lock:
            now = time.time()
            # Remove old calls outside the time window
            self.calls = [
                call_time
                for call_time in self.calls
                if now - call_time < self.time_window
            ]

            # Check if we're at the limit
            if len(self.calls) >= self.burst_limit:
                # Calculate wait time
                oldest_call = min(self.calls)
                wait_time = self.time_window - (now - oldest_call)
                if wait_time > 0:
                    api_rate_limit_hits.inc()
                    raise RateLimitError(
                        message="Rate limit exceeded for Gong API",
                        retry_after=int(wait_time),
                        service="gong_webhook",
                    )

            # Add current call
            self.calls.append(now)

        return self

    async def __aexit__(...):
    """TODO: Implement __aexit__"""
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"__aexit__ not yet implemented")


# Retry Manager
class RetryManager:
    """Manages retry logic with different policies."""

    def __init__(self):
        self.logger = logger.bind(component="retry_manager")

    async def exponential_backoff(
        self,
        operation: Callable,
        max_retries: int = 5,
        base_delay: float = 1.0,
        max_delay: float = 300.0,
    ) -> Any:
        """Retry with exponential backoff."""
        for attempt in range(max_retries):
            try:
                return await operation()
            except Exception as e:
                if attempt == max_retries - 1:
                    self.logger.exception(
                        "Max retries exceeded", error=str(e), attempts=max_retries
                    )
                    raise

                delay = min(base_delay * (2**attempt), max_delay)
                self.logger.warning(
                    f"Retry attempt {attempt + 1}/{max_retries}",
                    error=str(e),
                    next_retry_in=delay,
                )
                await asyncio.sleep(delay)


# Data Validator
class DataValidator:
    """Validates webhook data quality."""

    async def validate_call_data(self, data: dict[str, Any]) -> ValidationResult:
        """Validate call webhook data."""
        issues = []

        # Check required fields
        required_fields = ["call_id", "call_start_time", "participants"]
        for field in required_fields:
            if field not in data or data[field] is None:
                issues.append(f"Missing required field: {field}")

        # Validate data types
        if "duration" in data and not isinstance(data.get("duration"), int | float):
            issues.append("Duration must be a number")

        if "participants" in data and not isinstance(data.get("participants"), list):
            issues.append("Participants must be a list")

        # Calculate quality score
        quality_score = 1.0 - (len(issues) * 0.1)
        quality_score = max(0.0, quality_score)

        # Update metric
        data_quality_score.set(quality_score)

        if issues:
            validation_failures.labels(type="call_data").inc()

        return ValidationResult(
            is_valid=len(issues) == 0, quality_score=quality_score, issues=issues
        )


# Initialize FastAPI app
app = FastAPI(
    title="Gong Webhook Server",
    description="Production-ready webhook processor for Gong integrations",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware for request tracking
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add request ID for tracing."""
    request_id = request.headers.get("X-Request-ID", str(uuid4()))

    # Bind request ID to logger
    structlog.contextvars.bind_contextvars(request_id=request_id)

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    return response


# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests and responses."""
    start_time = time.time()

    # Log request
    logger.info(
        "Request received",
        method=request.method,
        path=request.url.path,
        client=request.client.host if request.client else None,
    )

    response = await call_next(request)

    # Log response
    duration = time.time() - start_time
    logger.info(
        "Request completed",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration=duration,
    )

    return response


# Initialize components
# webhook_verifier will be initialized lazily
# rate_limiter will be initialized lazily
# retry_manager will be initialized lazily
# data_validator will be initialized lazily

# Initialize webhook processor
# webhook_processor will be initialized lazily


# Lazy initialization for components
_webhook_verifier: GongWebhookVerifier | None = None
_rate_limiter: AsyncRateLimiter | None = None
_retry_manager: RetryManager | None = None
_data_validator: DataValidator | None = None
_webhook_processor: WebhookProcessor | None = None


def get_webhook_verifier() -> GongWebhookVerifier:
    global _webhook_verifier
    if _webhook_verifier is None:
        config = get_server_config()
        _webhook_verifier = GongWebhookVerifier(config.GONG_WEBHOOK_SECRETS)
    return _webhook_verifier


def get_rate_limiter() -> AsyncRateLimiter:
    global _rate_limiter
    if _rate_limiter is None:
        config = get_server_config()
        _rate_limiter = AsyncRateLimiter(
            config.GONG_API_RATE_LIMIT, burst_limit=config.GONG_API_BURST_LIMIT
        )
    return _rate_limiter


def get_retry_manager() -> RetryManager:
    global _retry_manager
    if _retry_manager is None:
        _retry_manager = RetryManager()
    return _retry_manager


def get_data_validator() -> DataValidator:
    global _data_validator
    if _data_validator is None:
        _data_validator = DataValidator()
    return _data_validator


def get_webhook_processor() -> WebhookProcessor:
    global _webhook_processor
    if _webhook_processor is None:
        config = get_server_config()
        _webhook_processor = WebhookProcessor(
            gong_api_key=config.GONG_API_KEY,
            
                "account": config.qdrant_ACCOUNT,
                "user": config.qdrant_USER,
                "password": config.qdrant_PASSWORD,
                "warehouse": config.qdrant_WAREHOUSE,
                "database": config.qdrant_DATABASE,
                "schema": config.qdrant_SCHEMA,
            },
            redis_url=config.REDIS_URL,
        )
    return _webhook_processor


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    checks = {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
        "version": "1.0.0",
        "checks": {
            "redis": {"status": "ok"},  # TODO: Implement actual health checks
            "qdrant": {"status": "ok"},
            "gong_api": {"status": "ok"},
        },
    }

    return checks


# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(content=generate_latest(), media_type="text/plain")


# Webhook endpoints
@app.post("/webhook/gong/calls")
async def handle_call_webhook(request: Request, background_tasks: BackgroundTasks):
    """Handle Gong call webhooks."""
    with webhook_processing_duration.time():
        try:
            # Verify webhook signature
            await get_webhook_verifier().verify_signature(request)

            # Parse webhook data
            webhook_data = await request.json()

            # Create webhook record
            webhook = GongCallWebhook(
                event_type="call",
                event_timestamp=datetime.now(UTC),
                object_id=webhook_data.get("call_id", ""),
                object_type="call",
                call_id=webhook_data.get("call_id", ""),
                call_start_time=webhook_data.get("call_start_time", datetime.now(UTC)),
                duration=webhook_data.get("duration", 0),
                participants=webhook_data.get("participants", []),
            )

            # Store raw webhook immediately (fast response)
            # TODO: Implement Qdrant storage

            # Queue background processing
            background_tasks.add_task(
                process_call_webhook_background, webhook.webhook_id, webhook_data
            )
            active_background_tasks.inc()

            # Update metrics
            webhook_requests_total.labels(endpoint="calls", status="success").inc()

            # Return success response
            return {
                "status": "accepted",
                "webhook_id": webhook.webhook_id,
                "message": "Webhook queued for processing",
            }

        except WebhookVerificationError as e:
            webhook_requests_total.labels(endpoint="calls", status="unauthorized").inc()
            logger.exception("Webhook verification failed", error=str(e))
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

        except Exception as e:
            webhook_requests_total.labels(endpoint="calls", status="error").inc()
            logger.exception("Error processing webhook", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )


async def process_call_webhook_background(
    webhook_id: str, webhook_data: dict[str, Any]
):
    """Process call webhook in the background."""
    async with webhook_processor:
        await webhook_processor.process_call_webhook_background(
            webhook_id, webhook_data
        )


async def process_call_webhook_background(
    webhook_id: str, webhook_data: dict[str, Any]
):
    """Process call webhook in the background."""
    processor = get_webhook_processor()
    async with processor:
        await processor.process_call_webhook(webhook_id, webhook_data)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.integrations.gong_webhook_server:app",
        host=get_server_config().HOST,
        port=get_server_config().PORT,
        workers=get_server_config().WORKERS,
        log_config={
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                },
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
            },
            "root": {
                "level": "INFO",
                "handlers": ["default"],
            },
        },
    )
