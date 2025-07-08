# V2+ Template Architecture

## Overview

This document defines the golden template for all V2+ MCP servers. Every new server must follow this architecture to ensure consistency, maintainability, and operational excellence.

## Golden Template Structure

```
infrastructure/mcp_servers/{server_name}_v2/
├── __init__.py
├── server.py
├── models.py
├── services/
│   ├── __init__.py
│   └── core_service.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_server.py
├── Dockerfile
├── requirements.txt
└── README.md
```

## 1. Base Server Implementation

### `server.py` - Main Server File

```python
"""
{Server Name} V2+ MCP Server
Implements {brief description of functionality}
"""

from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager
import logging

from fastapi import HTTPException, Depends
from pydantic import BaseModel, Field

from backend.core.auto_esc_config import get_config_value
from backend.core.cache_manager import get_cache, CacheTTL, cache_or_run
from infrastructure.mcp_servers.base.standardized_mcp_server import (
    StandardizedMCPServer,
    HealthResponse,
    InfoResponse
)
from backend.core.ports.port_manager import PortManager

# Import service layer
from .services.core_service import CoreService
from .models import (
    RequestModel,
    ResponseModel,
    ConfigModel
)

# Configure logging
logger = logging.getLogger(__name__)


class {ServerName}V2Server(StandardizedMCPServer):
    """
    {Server Name} V2+ Implementation

    Features:
    - {Feature 1}
    - {Feature 2}
    - {Feature 3}
    """

    def __init__(self):
        # Get port from central registry
        port_manager = PortManager()
        port = port_manager.get_port("{server_name}_v2") or {default_port}

        super().__init__(
            service_name="{server_name}_v2",
            default_port=port
        )

        # Service instances
        self.core_service: Optional[CoreService] = None
        self.config: Optional[ConfigModel] = None

    @asynccontextmanager
    async def lifespan(self, app):
        """FastAPI lifespan manager"""
        # Startup
        logger.info(f"Starting {self.service_name} on port {self.port}")
        await self.on_startup()

        yield

        # Shutdown
        logger.info(f"Shutting down {self.service_name}")
        await self.on_shutdown()

    async def on_startup(self):
        """Initialize server resources"""
        try:
            # Load configuration from ESC
            self.config = ConfigModel(
                api_key=get_config_value("{service}_api_key"),
                endpoint=get_config_value("{service}_endpoint"),
                timeout=get_config_value("{service}_timeout", default=30),
                max_retries=get_config_value("{service}_max_retries", default=3)
            )

            # Initialize cache
            self.cache = get_cache(namespace=self.service_name)

            # Initialize service layer
            self.core_service = CoreService(self.config)
            await self.core_service.initialize()

            # Register MCP tools
            self._register_tools()

            logger.info(f"{self.service_name} initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize {self.service_name}: {e}")
            raise

    async def on_shutdown(self):
        """Cleanup server resources"""
        if self.core_service:
            await self.core_service.cleanup()

    def _register_tools(self):
        """Register MCP tools for Cursor"""

        @self.tool()
        async def process_request(
            self,
            data: str,
            options: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            """
            Process a request through {service_name}

            Args:
                data: Input data to process
                options: Optional processing options

            Returns:
                Processed result
            """
            # Create request model
            request = RequestModel(data=data, options=options or {})

            # Check cache
            cache_key = f"{self.service_name}:request:{request.cache_key()}"

            async def process():
                result = await self.core_service.process(request)
                return result.model_dump()

            # Use cache with TTL
            result = await cache_or_run(
                cache_key,
                CacheTTL.MEDIUM,
                process()
            )

            return result

        @self.tool()
        async def get_status(self) -> Dict[str, Any]:
            """Get current service status"""
            return await self.core_service.get_status()

        @self.tool()
        async def list_capabilities(self) -> List[str]:
            """List available capabilities"""
            return self.core_service.list_capabilities()


# Create server instance
server = {ServerName}V2Server()
app = server.create_app()


# Additional API endpoints (beyond MCP tools)
@app.get("/api/v1/status", response_model=ResponseModel)
async def get_detailed_status():
    """Get detailed service status"""
    if not server.core_service:
        raise HTTPException(status_code=503, detail="Service not initialized")

    status = await server.core_service.get_detailed_status()
    return ResponseModel(
        status="ok",
        data=status,
        message="Service operational"
    )


@app.post("/api/v1/process", response_model=ResponseModel)
async def process_api_request(request: RequestModel):
    """Process request via REST API"""
    if not server.core_service:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        result = await server.core_service.process(request)
        return ResponseModel(
            status="ok",
            data=result.model_dump(),
            message="Request processed successfully"
        )
    except Exception as e:
        logger.error(f"Processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=server.port)
```

### `models.py` - Pydantic Models

```python
"""
Data models for {Server Name} V2
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
import hashlib
import json


class ConfigModel(BaseModel):
    """Service configuration"""
    model_config = ConfigDict(frozen=True)

    api_key: str = Field(..., description="API key for service")
    endpoint: str = Field(..., description="Service endpoint URL")
    timeout: int = Field(30, description="Request timeout in seconds")
    max_retries: int = Field(3, description="Maximum retry attempts")


class RequestModel(BaseModel):
    """Request data model"""
    data: str = Field(..., description="Input data")
    options: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    def cache_key(self) -> str:
        """Generate cache key for request"""
        data = {
            "data": self.data,
            "options": self.options
        }
        return hashlib.md5(
            json.dumps(data, sort_keys=True).encode()
        ).hexdigest()


class ResponseModel(BaseModel):
    """Standard response model"""
    status: str = Field(..., description="Response status")
    data: Optional[Dict[str, Any]] = Field(None)
    message: Optional[str] = Field(None)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ServiceStatus(BaseModel):
    """Service status model"""
    healthy: bool
    version: str
    uptime_seconds: float
    processed_requests: int
    error_rate: float
    last_error: Optional[str] = None
    capabilities: List[str]
```

### `services/core_service.py` - Business Logic

```python
"""
Core service implementation for {Server Name}
"""

import asyncio
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from ..models import (
    ConfigModel,
    RequestModel,
    ResponseModel,
    ServiceStatus
)

logger = logging.getLogger(__name__)


class CoreService:
    """
    Core business logic for {service_name}
    """

    def __init__(self, config: ConfigModel):
        self.config = config
        self.client: Optional[httpx.AsyncClient] = None
        self.start_time = datetime.utcnow()
        self.request_count = 0
        self.error_count = 0
        self.last_error: Optional[str] = None

    async def initialize(self):
        """Initialize service resources"""
        self.client = httpx.AsyncClient(
            timeout=self.config.timeout,
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "User-Agent": "{service_name}_v2/1.0"
            }
        )

    async def cleanup(self):
        """Cleanup service resources"""
        if self.client:
            await self.client.aclose()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(httpx.HTTPError)
    )
    async def process(self, request: RequestModel) -> ResponseModel:
        """
        Process request with retry logic
        """
        self.request_count += 1

        try:
            # Implement actual processing logic here
            response = await self.client.post(
                f"{self.config.endpoint}/process",
                json=request.model_dump()
            )
            response.raise_for_status()

            result = response.json()

            return ResponseModel(
                status="success",
                data=result,
                message="Processed successfully"
            )

        except Exception as e:
            self.error_count += 1
            self.last_error = str(e)
            logger.error(f"Processing error: {e}")
            raise

    async def get_status(self) -> Dict[str, Any]:
        """Get service status"""
        uptime = (datetime.utcnow() - self.start_time).total_seconds()
        error_rate = self.error_count / max(self.request_count, 1)

        return ServiceStatus(
            healthy=error_rate < 0.1,  # Less than 10% error rate
            version="2.0.0",
            uptime_seconds=uptime,
            processed_requests=self.request_count,
            error_rate=error_rate,
            last_error=self.last_error,
            capabilities=self.list_capabilities()
        ).model_dump()

    async def get_detailed_status(self) -> Dict[str, Any]:
        """Get detailed service status"""
        basic_status = await self.get_status()

        # Add detailed metrics
        basic_status.update({
            "config": {
                "endpoint": self.config.endpoint,
                "timeout": self.config.timeout,
                "max_retries": self.config.max_retries
            },
            "performance": {
                "avg_response_time": 0.0,  # Implement tracking
                "p99_response_time": 0.0,
                "throughput": 0.0
            }
        })

        return basic_status

    def list_capabilities(self) -> List[str]:
        """List service capabilities"""
        return [
            "process_request",
            "batch_process",
            "async_process",
            "status_check",
            "health_monitoring"
        ]
```

### `tests/conftest.py` - Test Configuration

```python
"""
Test configuration for {Server Name} V2
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import Mock, AsyncMock, patch

from httpx import AsyncClient
import fakeredis.aioredis

from ..server import {ServerName}V2Server, app
from ..models import ConfigModel


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def mock_config():
    """Mock configuration"""
    return ConfigModel(
        api_key="test-api-key",
        endpoint="https://api.test.com",
        timeout=30,
        max_retries=3
    )


@pytest.fixture
async def mock_redis():
    """Mock Redis for testing"""
    redis = fakeredis.aioredis.FakeRedis()
    with patch("backend.core.cache_manager.redis", redis):
        yield redis


@pytest.fixture
async def mock_esc(monkeypatch):
    """Mock ESC configuration"""
    mock_values = {
        "{service}_api_key": "test-api-key",
        "{service}_endpoint": "https://api.test.com",
        "{service}_timeout": "30",
        "{service}_max_retries": "3"
    }

    def mock_get_config_value(key, default=None):
        return mock_values.get(key, default)

    monkeypatch.setattr(
        "backend.core.auto_esc_config.get_config_value",
        mock_get_config_value
    )


@pytest.fixture
async def test_server(mock_esc, mock_redis):
    """Create test server instance"""
    server = {ServerName}V2Server()
    await server.on_startup()
    yield server
    await server.on_shutdown()


@pytest.fixture
async def test_client(test_server) -> AsyncGenerator[AsyncClient, None]:
    """Create test client"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_httpx_client():
    """Mock httpx client for external API calls"""
    with patch("httpx.AsyncClient") as mock:
        client = AsyncMock()
        mock.return_value = client

        # Mock successful response
        response = AsyncMock()
        response.json.return_value = {"result": "success"}
        response.raise_for_status = Mock()
        client.post.return_value = response

        yield client
```

### `tests/test_server.py` - Unit Tests

```python
"""
Unit tests for {Server Name} V2
"""

import pytest
from httpx import AsyncClient

from ..models import RequestModel, ResponseModel


class Test{ServerName}V2Server:
    """Test {Server Name} V2 server"""

    async def test_health_endpoint(self, test_client: AsyncClient):
        """Test health endpoint"""
        response = await test_client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    async def test_info_endpoint(self, test_client: AsyncClient):
        """Test info endpoint"""
        response = await test_client.get("/info")
        assert response.status_code == 200

        data = response.json()
        assert data["service_name"] == "{server_name}_v2"
        assert "version" in data
        assert "uptime" in data

    async def test_metrics_endpoint(self, test_client: AsyncClient):
        """Test Prometheus metrics endpoint"""
        response = await test_client.get("/metrics")
        assert response.status_code == 200
        assert "request_seconds" in response.text

    async def test_process_request(self, test_client: AsyncClient, mock_httpx_client):
        """Test process request endpoint"""
        request_data = {
            "data": "test input",
            "options": {"key": "value"}
        }

        response = await test_client.post("/api/v1/process", json=request_data)
        assert response.status_code == 200

        result = response.json()
        assert result["status"] == "ok"
        assert result["data"] is not None

    async def test_process_request_error(self, test_client: AsyncClient):
        """Test process request with error"""
        # Send invalid request
        response = await test_client.post("/api/v1/process", json={})
        assert response.status_code == 422  # Validation error

    async def test_mcp_tool_registration(self, test_server):
        """Test MCP tool registration"""
        tools = test_server.list_tools()

        expected_tools = [
            "process_request",
            "get_status",
            "list_capabilities"
        ]

        for tool in expected_tools:
            assert tool in [t["name"] for t in tools]

    async def test_caching(self, test_server, mock_redis):
        """Test request caching"""
        request = RequestModel(data="test", options={})

        # First call
        result1 = await test_server.process_request("test", {})

        # Second call (should use cache)
        result2 = await test_server.process_request("test", {})

        assert result1 == result2

        # Verify cache was used
        cache_key = f"{test_server.service_name}:request:{request.cache_key()}"
        cached = await mock_redis.get(cache_key)
        assert cached is not None

    @pytest.mark.parametrize("error_rate,expected_health", [
        (0.05, True),   # 5% error rate - healthy
        (0.15, False),  # 15% error rate - unhealthy
    ])
    async def test_health_status(self, test_server, error_rate, expected_health):
        """Test health status based on error rate"""
        # Simulate requests with errors
        test_server.core_service.request_count = 100
        test_server.core_service.error_count = int(100 * error_rate)

        status = await test_server.core_service.get_status()
        assert status["healthy"] == expected_health
```

### `Dockerfile` - Container Definition

```dockerfile
# Multi-stage build for V2+ MCP Server
FROM python:3.12-slim AS builder

# Install UV for fast dependency resolution
RUN pip install uv

# Copy dependency files
WORKDIR /app
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Runtime stage
FROM python:3.12-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
WORKDIR /app
COPY . .

# Set Python path
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-9000}/health || exit 1

# Expose port (will be overridden by docker-compose)
EXPOSE 9000

# Run server
CMD ["python", "-m", "infrastructure.mcp_servers.{server_name}_v2.server"]
```

### `README.md` - Documentation

```markdown
# {Server Name} V2+ MCP Server

## Overview

{Brief description of what this server does}

## Features

- ✅ {Feature 1}
- ✅ {Feature 2}
- ✅ {Feature 3}
- ✅ Prometheus metrics
- ✅ Health monitoring
- ✅ Caching support
- ✅ Retry logic
- ✅ Type-safe API

## Configuration

All configuration is managed through Pulumi ESC:

| Variable | Description | Required |
|----------|-------------|----------|
| `{service}_api_key` | API key for service | Yes |
| `{service}_endpoint` | Service endpoint URL | Yes |
| `{service}_timeout` | Request timeout (seconds) | No (default: 30) |
| `{service}_max_retries` | Max retry attempts | No (default: 3) |

## API Endpoints

### Health Check
```
GET /health
```

### Service Info
```
GET /info
```

### Process Request
```
POST /api/v1/process
{
  "data": "input data",
  "options": {}
}
```

## MCP Tools

### process_request
Process a request through the service.

```python
result = await server.process_request(
    data="input data",
    options={"key": "value"}
)
```

### get_status
Get current service status.

```python
status = await server.get_status()
```

### list_capabilities
List available capabilities.

```python
capabilities = await server.list_capabilities()
```

## Development

### Running Locally
```bash
# Install dependencies
uv sync

# Run server
uv run python -m infrastructure.mcp_servers.{server_name}_v2.server
```

### Testing
```bash
# Run tests
uv run pytest infrastructure/mcp_servers/{server_name}_v2/tests -v

# Run with coverage
uv run pytest infrastructure/mcp_servers/{server_name}_v2/tests --cov
```

### Building Docker Image
```bash
docker build -t {server_name}_v2 -f infrastructure/mcp_servers/{server_name}_v2/Dockerfile .
```

## Deployment

This server is deployed as part of the Sophia AI platform using Docker Swarm.

## Monitoring

- Prometheus metrics available at `/metrics`
- Grafana dashboard: `{dashboard_url}`
- Alerts configured for:
  - High error rate (>10%)
  - High response time (>1s)
  - Service unavailable

## Troubleshooting

### Common Issues

1. **Connection refused**
   - Check if service is running: `docker ps | grep {server_name}_v2`
   - Check logs: `docker logs {container_id}`

2. **Authentication errors**
   - Verify API key in Pulumi ESC
   - Check secret sync: `gh workflow run sync_secrets.yml`

3. **High error rate**
   - Check external service status
   - Review error logs
   - Verify configuration

## Support

- Slack: #sophia-ai-support
- Documentation: [Internal Wiki]
- On-call: [PagerDuty]
```

## 2. Standardized Components

### Error Handling Middleware

```python
# infrastructure/mcp_servers/base/middleware.py
"""
Standard middleware for V2+ servers
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import time
import logging
from typing import Callable

logger = logging.getLogger(__name__)


async def error_handler_middleware(request: Request, call_next: Callable):
    """Global error handler"""
    try:
        response = await call_next(request)
        return response
    except HTTPException:
        raise  # Let FastAPI handle HTTP exceptions
    except Exception as e:
        logger.exception(f"Unhandled error: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Internal server error",
                "detail": str(e) if request.app.debug else None
            }
        )


async def timing_middleware(request: Request, call_next: Callable):
    """Request timing middleware"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

### Validation Utilities

```python
# infrastructure/mcp_servers/base/validation.py
"""
Standard validation utilities
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, validator


class PaginationParams(BaseModel):
    """Standard pagination parameters"""
    page: int = 1
    page_size: int = 100

    @validator("page")
    def validate_page(cls, v):
        if v < 1:
            raise ValueError("Page must be >= 1")
        return v

    @validator("page_size")
    def validate_page_size(cls, v):
        if v < 1 or v > 1000:
            raise ValueError("Page size must be between 1 and 1000")
        return v


def validate_config(config: Dict[str, Any], required_keys: list) -> None:
    """Validate configuration has required keys"""
    missing = [key for key in required_keys if key not in config]
    if missing:
        raise ValueError(f"Missing required config keys: {missing}")
```

## 3. Migration Checklist

For each server migration:

- [ ] Create new directory under `infrastructure/mcp_servers/{server_name}_v2/`
- [ ] Copy template files and customize
- [ ] Update server name and configuration
- [ ] Implement core business logic
- [ ] Write comprehensive tests (>80% coverage)
- [ ] Create Dockerfile
- [ ] Update port allocation in `consolidated_mcp_ports.json`
- [ ] Add to CI matrix
- [ ] Document in README
- [ ] Test locally
- [ ] Deploy to staging
- [ ] Validate health and metrics
- [ ] Deploy to production
- [ ] Archive old V1 server

## Summary

This V2+ template provides:

1. **Standardized structure** for consistency
2. **Comprehensive error handling** and retry logic
3. **Built-in monitoring** with Prometheus metrics
4. **Type safety** with Pydantic models
5. **Testability** with fixtures and mocks
6. **Production readiness** with Docker and health checks

Next: [Phase 1: Core Infrastructure](./04_PHASE1_CORE_INFRASTRUCTURE.md)
