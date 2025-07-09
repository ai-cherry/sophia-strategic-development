"""
MCP V2+ Server Template
Golden template for all V2+ MCP servers
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest
from pydantic import BaseModel, Field

from infrastructure.mcp_servers.base import StandardizedMCPServer

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Prometheus metrics
request_count = Counter(
    "mcp_requests_total", "Total MCP requests", ["method", "status"]
)
request_duration = Histogram(
    "mcp_request_duration_seconds", "Request duration", ["method"]
)


class ServerConfig:
    """Server configuration"""

    NAME = "template_server"
    VERSION = "2.0.0"
    PORT = 9000
    DESCRIPTION = "Template MCP V2+ Server"


# Request/Response models
class ExampleRequest(BaseModel):
    """Example request model"""

    query: str = Field(..., description="Query string")
    options: dict[str, Any] | None = Field(default_factory=dict)


class ExampleResponse(BaseModel):
    """Example response model"""

    result: Any
    metadata: dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    version: str
    uptime: float
    checks: dict[str, bool]


# Server implementation
class TemplateServer(StandardizedMCPServer):
    """Template MCP V2+ Server"""

    def __init__(self):
        super().__init__(
            name=ServerConfig.NAME, version=ServerConfig.VERSION, port=ServerConfig.PORT
        )
        self.start_time = time.time()

    async def initialize(self):
        """Initialize server resources"""
        logger.info(f"Initializing {self.name} v{self.version}")
        # Initialize connections, caches, etc.

    async def shutdown(self):
        """Clean up server resources"""
        logger.info(f"Shutting down {self.name}")
        # Close connections, save state, etc.

    def get_health_status(self) -> dict[str, Any]:
        """Get detailed health status"""
        return {
            "database": self._check_database(),
            "cache": self._check_cache(),
            "external_api": self._check_external_api(),
        }

    def _check_database(self) -> bool:
        """Check database connectivity"""
        # Implement database health check
        return True

    def _check_cache(self) -> bool:
        """Check cache connectivity"""
        # Implement cache health check
        return True

    def _check_external_api(self) -> bool:
        """Check external API connectivity"""
        # Implement API health check
        return True


# Create server instance
server = TemplateServer()


# FastAPI lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage server lifecycle"""
    await server.initialize()
    yield
    await server.shutdown()


# Create FastAPI app
app = FastAPI(
    title=ServerConfig.NAME,
    description=ServerConfig.DESCRIPTION,
    version=ServerConfig.VERSION,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routes
@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    with request_duration.labels(method="health").time():
        checks = server.get_health_status()
        status = "healthy" if all(checks.values()) else "degraded"

        request_count.labels(method="health", status=status).inc()

        return HealthResponse(
            status=status,
            version=server.version,
            uptime=time.time() - server.start_time,
            checks=checks,
        )


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()


@app.post("/example", response_model=ExampleResponse)
async def example_endpoint(request: ExampleRequest):
    """Example endpoint"""
    with request_duration.labels(method="example").time():
        try:
            # Implement business logic
            result = f"Processed: {request.query}"

            request_count.labels(method="example", status="success").inc()

            return ExampleResponse(result=result, metadata={"options": request.options})

        except Exception as e:
            request_count.labels(method="example", status="error").inc()
            logger.error(f"Error processing request: {e}")
            raise HTTPException(status_code=500, detail=str(e))


# MCP tool registration (if using MCP protocol)
@server.tool("example_tool")
async def example_tool(query: str, **kwargs) -> dict[str, Any]:
    """Example MCP tool"""
    # Implement tool logic
    return {"result": f"Tool processed: {query}"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=ServerConfig.PORT, log_level="info")
