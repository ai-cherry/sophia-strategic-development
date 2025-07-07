#!/usr/bin/env bash
# scaffold_mcp_server_v3.sh - Enhanced MCP Server Scaffolder for Sophia AI
# Combines production-ready template with Sophia AI patterns
# USAGE: ./scaffold_mcp_server_v3.sh <server-name>
set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Validate input
if [ $# -ne 1 ]; then
    echo -e "${RED}❌ Usage: $0 <server-name>${NC}"
    echo -e "   Example: $0 github"
    exit 1
fi

SRV="$1"
BASE="infrastructure/mcp_servers/${SRV}"

# Check if already exists
if [[ -d "${BASE}" ]]; then 
    echo -e "${RED}❌ ${SRV} already exists at ${BASE}${NC}"
    exit 1
fi

echo -e "${BLUE}🚀 Creating enhanced MCP server: ${SRV}${NC}"

# Create directory structure
mkdir -p "${BASE}"/{handlers,models,utils,tests/{unit,integration},config}

# Helper function to create files
create_file() {
    local file_path="$1"
    local content="$2"
    echo "$content" > "$file_path"
    echo -e "${GREEN}✓${NC} Created: $file_path"
}

# Get the next available port
get_next_port() {
    # Read existing ports from mcp_config.json
    local base_port=9000
    local max_port=$(find infrastructure/mcp_servers -name "config.py" -exec grep -h "PORT.*=" {} \; 2>/dev/null | grep -oE '[0-9]+' | sort -n | tail -1 || echo $base_port)
    echo $((max_port + 1))
}

NEXT_PORT=$(get_next_port)

echo -e "${YELLOW}📍 Assigning port: ${NEXT_PORT}${NC}"

# --- Create __init__.py files ------------------------------------------------------
create_file "${BASE}/__init__.py" """${SRV} MCP server package."""

create_file "${BASE}/handlers/__init__.py" """Handler modules for ${SRV} MCP server."""

create_file "${BASE}/models/__init__.py" """Data models for ${SRV} MCP server."""

create_file "${BASE}/utils/__init__.py" """Utility modules for ${SRV} MCP server."""

create_file "${BASE}/tests/__init__.py" """Test modules for ${SRV} MCP server."""

create_file "${BASE}/tests/unit/__init__.py" """Unit tests for ${SRV} MCP server."""

create_file "${BASE}/tests/integration/__init__.py" """Integration tests for ${SRV} MCP server."""

# --- Create config.py ------------------------------------------------------
create_file "${BASE}/config.py" """\"\"\"Configuration for ${SRV} MCP server.

Enhanced with production-ready settings and Sophia AI integration.
\"\"\"
import os
from enum import Enum
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings

from infrastructure.mcp_servers.base.standardized_mcp_server import (
    MCPServerConfig,
    SyncPriority,
)


class Environment(Enum):
    \"\"\"Environment enumeration.\"\"\"
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class ${SRV^}Settings(BaseSettings):
    \"\"\"Settings for ${SRV} MCP server.\"\"\"
    
    # Basic settings
    APP_NAME: str = "${SRV}-mcp"
    VERSION: str = "1.0.0"
    ENVIRONMENT: Environment = Field(
        default=Environment.PRODUCTION,
        description="Deployment environment"
    )
    
    # Server settings
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=${NEXT_PORT}, description="Server port")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    # Database settings (if needed)
    DB_DSN: Optional[str] = Field(
        default=None,
        description="Database connection string",
        alias="${SRV^^}_DB_DSN"
    )
    DB_POOL_MIN: int = Field(default=1, description="Min DB pool size")
    DB_POOL_MAX: int = Field(default=5, description="Max DB pool size")
    
    # External API settings (customize as needed)
    API_KEY: Optional[str] = Field(
        default=None,
        description="${SRV} API key",
        alias="${SRV^^}_API_KEY"
    )
    API_BASE_URL: Optional[str] = Field(
        default=None,
        description="${SRV} API base URL",
        alias="${SRV^^}_API_BASE_URL"
    )
    
    # Sync settings
    SYNC_ENABLED: bool = Field(default=True, description="Enable data sync")
    SYNC_INTERVAL_MINUTES: int = Field(default=30, description="Sync interval")
    SYNC_BATCH_SIZE: int = Field(default=100, description="Sync batch size")
    
    # AI settings
    ENABLE_AI_PROCESSING: bool = Field(default=True, description="Enable AI processing")
    
    # Feature flags
    ENABLE_METRICS: bool = Field(default=True, description="Enable Prometheus metrics")
    ENABLE_HEALTH_CHECKS: bool = Field(default=True, description="Enable health checks")
    
    class Config:
        env_prefix = "${SRV^^}_"
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = ${SRV^}Settings()

# Create MCP server config
mcp_config = MCPServerConfig(
    server_name="${SRV}",
    port=settings.PORT,
    sync_priority=SyncPriority.MEDIUM,
    sync_interval_minutes=settings.SYNC_INTERVAL_MINUTES,
    batch_size=settings.SYNC_BATCH_SIZE,
    retry_attempts=3,
    timeout_seconds=300,
    enable_ai_processing=settings.ENABLE_AI_PROCESSING,
    enable_metrics=settings.ENABLE_METRICS,
)

# --- Create logging_config.py ------------------------------------------------------
create_file "${BASE}/utils/logging_config.py" """Logging configuration for ${SRV} MCP server.

Production-ready JSON logging with correlation IDs.
"""
import logging
import sys
from logging.config import dictConfig

from pythonjsonlogger import jsonlogger


def setup_logging(level: str = "INFO", service_name: str = "${SRV}"):
    \"\"\"Configure JSON logging for production.
    
    Args:
        level: Logging level
        service_name: Name of the service for log correlation
    \"\"\"
    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
                "rename_fields": {
                    "asctime": "timestamp",
                    "levelname": "level",
                    "name": "logger"
                },
                "static_fields": {
                    "service": service_name,
                    "environment": "production"
                }
            },
            "standard": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        },
        "handlers": {
            "json": {
                "class": "logging.StreamHandler",
                "formatter": "json",
                "stream": sys.stdout
            },
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "stream": sys.stderr
            }
        },
        "root": {
            "level": level,
            "handlers": ["json"]
        },
        "loggers": {
            "uvicorn": {
                "level": "INFO",
                "handlers": ["json"],
                "propagate": False
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["json"],
                "propagate": False
            }
        }
    }
    
    dictConfig(log_config)
    
    # Test logging
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured for {service_name} at level {level}")
"""

# --- Create db.py (optional database helper) ------------------------------------------------------
create_file "${BASE}/utils/db.py" """Database connection helper for ${SRV} MCP server.

Async connection pool management with health checks.
"""
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from ${SRV}.config import settings

logger = logging.getLogger(__name__)

# Global engine instance
_engine: Optional[AsyncEngine] = None
_session_factory: Optional[async_sessionmaker[AsyncSession]] = None


async def get_engine() -> AsyncEngine:
    \"\"\"Get or create the database engine.\"\"\"
    global _engine
    
    if _engine is None:
        if not settings.DB_DSN:
            raise ValueError("Database DSN not configured")
            
        _engine = create_async_engine(
            settings.DB_DSN,
            pool_size=settings.DB_POOL_MAX,
            max_overflow=0,
            pool_pre_ping=True,
            echo=settings.LOG_LEVEL == "DEBUG",
        )
        logger.info("Database engine created", extra={
            "pool_size": settings.DB_POOL_MAX,
            "dsn": settings.DB_DSN.split("@")[-1]  # Log only host part
        })
    
    return _engine


async def get_session_factory() -> async_sessionmaker[AsyncSession]:
    \"\"\"Get or create the session factory.\"\"\"
    global _session_factory
    
    if _session_factory is None:
        engine = await get_engine()
        _session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        logger.info("Session factory created")
    
    return _session_factory


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    \"\"\"Get a database session.
    
    Usage:
        async with get_session() as session:
            result = await session.execute(query)
    \"\"\"
    factory = await get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    \"\"\"Initialize database connection pool.\"\"\"
    if settings.DB_DSN:
        engine = await get_engine()
        # Test connection
        async with engine.begin() as conn:
            await conn.run_sync(lambda _: None)
        logger.info("Database initialized successfully")
    else:
        logger.warning("Database DSN not configured, skipping DB initialization")


async def close_db() -> None:
    \"\"\"Close database connection pool.\"\"\"
    global _engine, _session_factory
    
    if _engine:
        await _engine.dispose()
        _engine = None
        _session_factory = None
        logger.info("Database connection pool closed")


async def check_db_health() -> bool:
    \"\"\"Check database health.\"\"\"
    if not settings.DB_DSN:
        return True  # No DB configured, consider healthy
        
    try:
        engine = await get_engine()
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False

# --- Create server.py ------------------------------------------------------
create_file "${BASE}/server.py" """${SRV^} MCP Server implementation.

Production-ready server with Sophia AI integration.
"""
import asyncio
import logging
from typing import Any, Optional

from infrastructure.mcp_servers.base.standardized_mcp_server import (
    HealthCheckResult,
    HealthStatus,
    ServerCapability,
    StandardizedMCPServer,
)

from ${SRV}.config import mcp_config, settings
from ${SRV}.handlers.main_handler import ${SRV^}Handler
from ${SRV}.utils.db import check_db_health, close_db, init_db
from ${SRV}.utils.logging_config import setup_logging

# Setup logging
setup_logging(settings.LOG_LEVEL, settings.APP_NAME)
logger = logging.getLogger(__name__)


class ${SRV^}MCPServer(StandardizedMCPServer):
    \"\"\"${SRV^} MCP Server implementation.
    
    Provides integration with ${SRV} platform including:
    - Data synchronization
    - AI-powered processing
    - Health monitoring
    - Metrics collection
    \"\"\"
    
    def __init__(self):
        \"\"\"Initialize ${SRV} MCP server.\"\"\"
        super().__init__(mcp_config)
        self.handler: Optional[${SRV^}Handler] = None
        
    async def server_specific_init(self) -> None:
        \"\"\"Initialize ${SRV}-specific components.\"\"\"
        logger.info("Initializing ${SRV} MCP server components...")
        
        # Initialize database if configured
        await init_db()
        
        # Initialize handler
        self.handler = ${SRV^}Handler(
            api_key=settings.API_KEY,
            base_url=settings.API_BASE_URL,
        )
        await self.handler.initialize()
        
        # Add custom routes
        self._add_custom_routes()
        
        logger.info("${SRV^} MCP server initialization complete")
        
    def _add_custom_routes(self) -> None:
        \"\"\"Add ${SRV}-specific API routes.\"\"\"
        # Add sync endpoint
        self.app.add_api_route(
            "/sync",
            self.sync_endpoint,
            methods=["POST"],
            summary="Trigger data synchronization",
            tags=["${SRV}"]
        )
        
        # Add data endpoints
        self.app.add_api_route(
            "/data",
            self.get_data_endpoint,
            methods=["GET"],
            summary="Get ${SRV} data",
            tags=["${SRV}"]
        )
        
    async def sync_endpoint(self) -> dict[str, Any]:
        \"\"\"Endpoint to trigger data sync.\"\"\"
        if not settings.SYNC_ENABLED:
            return {"status": "disabled", "message": "Sync is disabled"}
            
        result = await self.sync_data()
        return result
        
    async def get_data_endpoint(self, limit: int = 10, offset: int = 0) -> dict[str, Any]:
        \"\"\"Get ${SRV} data with pagination.\"\"\"
        if not self.handler:
            return {"error": "Handler not initialized"}
            
        data = await self.handler.get_data(limit=limit, offset=offset)
        return {
            "data": data,
            "limit": limit,
            "offset": offset,
            "total": len(data)
        }
        
    async def server_specific_cleanup(self) -> None:
        \"\"\"Cleanup ${SRV}-specific resources.\"\"\"
        logger.info("Cleaning up ${SRV} MCP server resources...")
        
        # Cleanup handler
        if self.handler:
            await self.handler.cleanup()
            
        # Close database
        await close_db()
        
        logger.info("${SRV^} MCP server cleanup complete")
        
    async def server_specific_health_check(self) -> HealthCheckResult:
        \"\"\"Check ${SRV}-specific health.\"\"\"
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Check handler health
            if not self.handler:
                return HealthCheckResult(
                    component="${SRV}_handler",
                    status=HealthStatus.UNHEALTHY,
                    response_time_ms=0,
                    error_message="Handler not initialized"
                )
                
            handler_healthy = await self.handler.check_health()
            
            # Check database health
            db_healthy = await check_db_health()
            
            # Overall health
            all_healthy = handler_healthy and db_healthy
            
            response_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return HealthCheckResult(
                component="${SRV}_server",
                status=HealthStatus.HEALTHY if all_healthy else HealthStatus.DEGRADED,
                response_time_ms=response_time,
                metadata={
                    "handler_healthy": handler_healthy,
                    "db_healthy": db_healthy,
                }
            )
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            response_time = (asyncio.get_event_loop().time() - start_time) * 1000
            return HealthCheckResult(
                component="${SRV}_server",
                status=HealthStatus.UNHEALTHY,
                response_time_ms=response_time,
                error_message=str(e)
            )
            
    async def check_external_api(self) -> bool:
        \"\"\"Check if ${SRV} API is accessible.\"\"\"
        if not self.handler:
            return False
        return await self.handler.check_api_health()
        
    async def get_server_capabilities(self) -> list[ServerCapability]:
        \"\"\"Get ${SRV}-specific capabilities.\"\"\"
        return [
            ServerCapability(
                name="${SRV}_sync",
                description="Synchronize data with ${SRV} platform",
                category="data_sync",
                available=settings.SYNC_ENABLED,
            ),
            ServerCapability(
                name="${SRV}_data_access",
                description="Access ${SRV} data via API",
                category="data_access",
                available=bool(settings.API_KEY),
            ),
            # Add more capabilities as needed
        ]
        
    async def sync_data(self) -> dict[str, Any]:
        \"\"\"Synchronize data with ${SRV}.\"\"\"
        if not self.handler:
            return {"status": "error", "message": "Handler not initialized"}
            
        try:
            logger.info("Starting ${SRV} data sync...")
            
            # Perform sync
            result = await self.handler.sync_data(
                batch_size=settings.SYNC_BATCH_SIZE
            )
            
            # Update metrics
            if self.config.enable_metrics:
                self.sync_success_rate.set(1.0)
                self.records_processed.labels(
                    operation="sync",
                    status="success"
                ).inc(result.get("records_synced", 0))
                
            logger.info(f"${SRV^} sync completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"${SRV^} sync failed: {e}")
            
            if self.config.enable_metrics:
                self.sync_success_rate.set(0.0)
                self.records_processed.labels(
                    operation="sync",
                    status="error"
                ).inc()
                
            return {"status": "error", "message": str(e)}
            
    async def process_with_ai(self, data: Any, model=None) -> Any:
        \"\"\"Process data with AI.\"\"\"
        if not self.config.enable_ai_processing:
            return data
            
        # Use Snowflake Cortex if available
        if self.cortex_service:
            try:
                # Example: Summarize or extract insights
                prompt = f"Analyze this ${SRV} data and provide insights: {data}"
                result = await self.cortex_service.complete(prompt)
                return {
                    "original": data,
                    "insights": result,
                    "processed_at": asyncio.get_event_loop().time()
                }
            except Exception as e:
                logger.error(f"AI processing failed: {e}")
                
        return data


async def main():
    \"\"\"Main entry point.\"\"\"
    server = ${SRV^}MCPServer()
    
    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("Shutting down ${SRV} MCP server...")
        await server.shutdown()
    except Exception as e:
        logger.error(f"Server error: {e}")
        await server.shutdown()
        raise


if __name__ == "__main__":
    asyncio.run(main())
"""

# --- Create main_handler.py ------------------------------------------------------
create_file "${BASE}/handlers/main_handler.py" """Main handler for ${SRV} MCP server.

Implements business logic for ${SRV} integration.
"""
import logging
from typing import Any, Optional

import aiohttp

logger = logging.getLogger(__name__)


class ${SRV^}Handler:
    \"\"\"Handler for ${SRV} operations.
    
    Manages:
    - API communication
    - Data transformation
    - Business logic
    - Error handling
    \"\"\"
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        \"\"\"Initialize handler.
        
        Args:
            api_key: API key for ${SRV}
            base_url: Base URL for ${SRV} API
        \"\"\"
        self.api_key = api_key
        self.base_url = base_url or "https://api.${SRV}.com/v1"
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def initialize(self) -> None:
        \"\"\"Initialize handler resources.\"\"\"
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            
        self.session = aiohttp.ClientSession(
            base_url=self.base_url,
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=30)
        )
        logger.info(f"${SRV^} handler initialized with base URL: {self.base_url}")
        
    async def cleanup(self) -> None:
        \"\"\"Cleanup handler resources.\"\"\"
        if self.session:
            await self.session.close()
            self.session = None
        logger.info("${SRV^} handler cleaned up")
        
    async def check_health(self) -> bool:
        \"\"\"Check handler health.\"\"\"
        try:
            # Check session is active
            if not self.session:
                return False
                
            # TODO: Add specific health check logic
            return True
            
        except Exception as e:
            logger.error(f"Handler health check failed: {e}")
            return False
            
    async def check_api_health(self) -> bool:
        \"\"\"Check if ${SRV} API is accessible.\"\"\"
        if not self.session:
            return False
            
        try:
            # TODO: Replace with actual health endpoint
            async with self.session.get("/health") as response:
                return response.status == 200
                
        except Exception as e:
            logger.error(f"API health check failed: {e}")
            return False
            
    async def get_data(self, limit: int = 10, offset: int = 0) -> list[dict[str, Any]]:
        \"\"\"Get data from ${SRV}.
        
        Args:
            limit: Number of records to fetch
            offset: Offset for pagination
            
        Returns:
            List of data records
        \"\"\"
        if not self.session:
            raise RuntimeError("Handler not initialized")
            
        try:
            # TODO: Replace with actual endpoint
            params = {"limit": limit, "offset": offset}
            async with self.session.get("/data", params=params) as response:
                response.raise_for_status()
                data = await response.json()
                
                logger.info(f"Fetched {len(data)} records from ${SRV}")
                return data
                
        except Exception as e:
            logger.error(f"Failed to fetch data: {e}")
            raise
            
    async def sync_data(self, batch_size: int = 100) -> dict[str, Any]:
        \"\"\"Synchronize data with ${SRV}.
        
        Args:
            batch_size: Number of records per batch
            
        Returns:
            Sync result summary
        \"\"\"
        if not self.session:
            raise RuntimeError("Handler not initialized")
            
        try:
            # TODO: Implement actual sync logic
            # This is a placeholder implementation
            
            records_synced = 0
            errors = 0
            
            # Example: Fetch and process data in batches
            offset = 0
            while True:
                data = await self.get_data(limit=batch_size, offset=offset)
                if not data:
                    break
                    
                # Process each record
                for record in data:
                    try:
                        await self._process_record(record)
                        records_synced += 1
                    except Exception as e:
                        logger.error(f"Failed to process record: {e}")
                        errors += 1
                        
                offset += batch_size
                
            result = {
                "status": "success" if errors == 0 else "partial",
                "records_synced": records_synced,
                "errors": errors,
            }
            
            logger.info(f"Sync completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "records_synced": 0,
            }
            
    async def _process_record(self, record: dict[str, Any]) -> None:
        \"\"\"Process a single record.
        
        Args:
            record: Record to process
        \"\"\"
        # TODO: Implement record processing logic
        # This could involve:
        # - Data validation
        # - Transformation
        # - Storage to database
        # - Sending to other services
        pass
"""

# --- Create models/data_models.py ------------------------------------------------------
create_file "${BASE}/models/data_models.py" """Data models for ${SRV} MCP server.

Pydantic models for data validation and serialization.
"""
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class ${SRV^}Record(BaseModel):
    \"\"\"Base model for ${SRV} records.\"\"\"
    
    id: str = Field(..., description="Unique identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    # TODO: Add ${SRV}-specific fields
    # Example fields:
    # name: str = Field(..., description="Record name")
    # status: str = Field(..., description="Record status")
    # data: dict[str, Any] = Field(default_factory=dict, description="Additional data")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SyncRequest(BaseModel):
    \"\"\"Request model for sync operations.\"\"\"
    
    batch_size: int = Field(default=100, ge=1, le=1000, description="Batch size")
    start_date: Optional[datetime] = Field(None, description="Start date for sync")
    end_date: Optional[datetime] = Field(None, description="End date for sync")
    force: bool = Field(default=False, description="Force full sync")


class SyncResponse(BaseModel):
    \"\"\"Response model for sync operations.\"\"\"
    
    status: str = Field(..., description="Sync status")
    records_synced: int = Field(..., description="Number of records synced")
    errors: int = Field(default=0, description="Number of errors")
    duration_seconds: float = Field(..., description="Sync duration")
    message: Optional[str] = Field(None, description="Status message")


class HealthResponse(BaseModel):
    \"\"\"Response model for health checks.\"\"\"
    
    status: str = Field(..., description="Health status")
    component: str = Field(..., description="Component name")
    response_time_ms: float = Field(..., description="Response time in milliseconds")
    error_message: Optional[str] = Field(None, description="Error message if unhealthy")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
"""

# --- Create requirements.txt ------------------------------------------------------
create_file "${BASE}/requirements.txt" "# ${SRV^} MCP Server Requirements

# Core dependencies
fastapi==0.111.0
uvicorn[standard]==0.29.0
pydantic==2.7.1
pydantic-settings==2.3.0
python-dotenv==1.0.1

# Async HTTP
aiohttp==3.9.5
httpx==0.27.0

# Database (optional - remove if not needed)
sqlalchemy[asyncio]==2.0.30
asyncpg==0.29.0

# Logging and monitoring
python-json-logger==2.0.7
prometheus-client==0.20.0

# Sophia AI dependencies
# Note: These are internal packages
# infrastructure.mcp_servers.base

# Testing
pytest==8.2.0
pytest-asyncio==0.23.6
pytest-cov==5.0.0
httpx==0.27.0  # For test client

# Development
black==24.4.2
ruff==0.4.4
mypy==1.10.0
"

# --- Create Dockerfile ------------------------------------------------------
create_file "${BASE}/Dockerfile" "FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONUNBUFFERED=1 \\
    PYTHONDONTWRITEBYTECODE=1 \\
    PIP_NO_CACHE_DIR=1 \\
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \\
    pip install -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && \\
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE ${NEXT_PORT}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:${NEXT_PORT}/health || exit 1

# Run the server
CMD [\"python\", \"-m\", \"${SRV}.server\"]
"

# --- Create docker-compose.yml ------------------------------------------------------
create_file "${BASE}/docker-compose.yml" "version: '3.9'

services:
  # Optional database (remove if not needed)
  db:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${SRV}
      POSTGRES_PASSWORD: ${SRV}_password
      POSTGRES_DB: ${SRV}_db
    ports:
      - \"5432:5432\"
    volumes:
      - ${SRV}_db_data:/var/lib/postgresql/data
    healthcheck:
      test: [\"CMD-SHELL\", \"pg_isready -U ${SRV}\"]
      interval: 10s
      timeout: 5s
      retries: 5

  # MCP Server
  ${SRV}:
    build:
      context: .
      dockerfile: Dockerfile
    restart: unless-stopped
    environment:
      # Basic settings
      ${SRV^^}_LOG_LEVEL: INFO
      ${SRV^^}_PORT: ${NEXT_PORT}
      
      # Database (if using)
      ${SRV^^}_DB_DSN: postgresql+asyncpg://${SRV}:${SRV}_password@db:5432/${SRV}_db
      
      # API settings (customize as needed)
      ${SRV^^}_API_KEY: \${${SRV^^}_API_KEY}
      ${SRV^^}_API_BASE_URL: \${${SRV^^}_API_BASE_URL}
      
      # Sophia AI settings
      PULUMI_ORG: scoobyjava-org
      ENVIRONMENT: production
      
    depends_on:
      db:
        condition: service_healthy
    ports:
      - \"${NEXT_PORT}:${NEXT_PORT}\"
    volumes:
      - ./logs:/app/logs
    healthcheck:
      test: [\"CMD\", \"curl\", \"-f\", \"http://localhost:${NEXT_PORT}/health\"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Optional: Prometheus for metrics
  prometheus:
    image: prom/prometheus:latest
    restart: unless-stopped
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    ports:
      - \"9090:9090\"
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus

volumes:
  ${SRV}_db_data:
  prometheus_data:

networks:
  default:
    name: sophia-ai-network
    external: true
"

# --- Create README.md ------------------------------------------------------
create_file "${BASE}/README.md" "# ${SRV^} MCP Server

Production-ready MCP server for ${SRV} integration with Sophia AI platform.

## Features

- ✅ Async/await architecture with FastAPI
- ✅ Production-ready logging (JSON format)
- ✅ Prometheus metrics
- ✅ Health checks and monitoring
- ✅ Docker support
- ✅ Comprehensive error handling
- ✅ AI-powered data processing (Snowflake Cortex)
- ✅ Automated testing

## Quick Start

### Local Development

\`\`\`bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ${SRV^^}_API_KEY=your_api_key
export ${SRV^^}_LOG_LEVEL=DEBUG

# Run the server
python -m ${SRV}.server
\`\`\`

### Docker

\`\`\`bash
# Build and run with docker-compose
docker-compose up --build

# Server will be available at http://localhost:${NEXT_PORT}
\`\`\`

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Health check endpoint |
| GET | /capabilities | Server capabilities (self-knowledge) |
| GET | /features | Available features |
| POST | /sync | Trigger data synchronization |
| GET | /data | Get ${SRV} data with pagination |
| GET | /docs | OpenAPI documentation |
| GET | /metrics | Prometheus metrics |

## Configuration

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| ${SRV^^}_PORT | ${NEXT_PORT} | Server port |
| ${SRV^^}_LOG_LEVEL | INFO | Logging level |
| ${SRV^^}_API_KEY | - | ${SRV} API key |
| ${SRV^^}_API_BASE_URL | https://api.${SRV}.com/v1 | API base URL |
| ${SRV^^}_DB_DSN | - | Database connection string |
| ${SRV^^}_SYNC_ENABLED | true | Enable data sync |
| ${SRV^^}_SYNC_INTERVAL_MINUTES | 30 | Sync interval |

## Testing

\`\`\`bash
# Run unit tests
pytest tests/unit -v

# Run integration tests
pytest tests/integration -v

# Run with coverage
pytest --cov=${SRV} --cov-report=html
\`\`\`

## Development

### Project Structure

\`\`\`
${SRV}/
├── config.py           # Configuration management
├── server.py           # Main server implementation
├── handlers/           # Request handlers
│   └── main_handler.py # Business logic
├── models/             # Data models
│   └── data_models.py  # Pydantic models
├── utils/              # Utilities
│   ├── db.py          # Database helpers
│   └── logging_config.py # Logging setup
└── tests/              # Test suite
    ├── unit/          # Unit tests
    └── integration/   # Integration tests
\`\`\`

### Adding New Endpoints

1. Add route in \`server.py\`:
   \`\`\`python
   self.app.add_api_route(\"/new-endpoint\", self.new_endpoint, methods=[\"GET\"])
   \`\`\`

2. Implement handler method:
   \`\`\`python
   async def new_endpoint(self) -> dict[str, Any]:
       return await self.handler.process_new_endpoint()
   \`\`\`

3. Add business logic in \`handlers/main_handler.py\`

### Database Migrations

If using database:

\`\`\`bash
# Create migration
alembic revision --autogenerate -m \"Add new table\"

# Run migrations
alembic upgrade head
\`\`\`

## Monitoring

### Prometheus Metrics

Available at \`/metrics\`:

- Request count by endpoint
- Request duration histogram
- Health status gauge
- Sync success rate
- Records processed counter
- AI processing metrics

### Health Checks

The \`/health\` endpoint provides:
- Overall server health
- Component status (handler, database, API)
- Response times
- Error messages if unhealthy

## Deployment

### Lambda Labs

\`\`\`bash
# Deploy to Lambda Labs
docker build -t scoobyjava15/${SRV}-mcp:latest .
docker push scoobyjava15/${SRV}-mcp:latest
docker stack deploy -c docker-compose.yml ${SRV}-mcp
\`\`\`

### Environment-specific Configuration

- Production: Uses Pulumi ESC for secrets
- Staging: Uses GitHub secrets
- Development: Uses local .env files

## Troubleshooting

### Common Issues

1. **Connection refused**
   - Check if server is running: \`curl http://localhost:${NEXT_PORT}/health\`
   - Verify port is not in use: \`lsof -i :${NEXT_PORT}\`

2. **API authentication errors**
   - Verify ${SRV^^}_API_KEY is set correctly
   - Check API key permissions

3. **Database connection errors**
   - Verify ${SRV^^}_DB_DSN is correct
   - Check database is running and accessible

### Debug Mode

Enable debug logging:
\`\`\`bash
export ${SRV^^}_LOG_LEVEL=DEBUG
\`\`\`

## License

Proprietary - Sophia AI Platform
" 

# --- Create unit test file ------------------------------------------------------
create_file "${BASE}/tests/unit/test_handler.py" """Unit tests for ${SRV} handler."""
import pytest
from unittest.mock import AsyncMock, MagicMock

from ${SRV}.handlers.main_handler import ${SRV^}Handler


@pytest.fixture
def handler():
    \"\"\"Create handler instance for testing.\"\"\"
    return ${SRV^}Handler(api_key="test_key", base_url="http://test.com")


@pytest.mark.asyncio
async def test_handler_initialization(handler):
    \"\"\"Test handler initialization.\"\"\"
    # Mock session
    handler.session = AsyncMock()
    
    # Initialize
    await handler.initialize()
    
    # Verify session created
    assert handler.session is not None


@pytest.mark.asyncio
async def test_handler_health_check(handler):
    \"\"\"Test handler health check.\"\"\"
    # Setup
    handler.session = AsyncMock()
    
    # Test
    result = await handler.check_health()
    
    # Verify
    assert result is True


@pytest.mark.asyncio
async def test_sync_data(handler):
    \"\"\"Test data synchronization.\"\"\"
    # Setup
    handler.session = AsyncMock()
    handler.get_data = AsyncMock(return_value=[])
    
    # Test
    result = await handler.sync_data(batch_size=10)
    
    # Verify
    assert result["status"] == "success"
    assert result["records_synced"] == 0
    assert result["errors"] == 0
"""

# --- Create integration test file ------------------------------------------------------
create_file "${BASE}/tests/integration/test_server.py" """Integration tests for ${SRV} server."""
import pytest
from httpx import AsyncClient

from ${SRV}.server import ${SRV^}MCPServer


@pytest.fixture
async def server():
    \"\"\"Create server instance for testing.\"\"\"
    server = ${SRV^}MCPServer()
    await server.initialize()
    yield server
    await server.shutdown()


@pytest.fixture
async def client(server):
    \"\"\"Create test client.\"\"\"
    async with AsyncClient(app=server.app, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_endpoint(client):
    \"\"\"Test health endpoint.\"\"\"
    response = await client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "components" in data


@pytest.mark.asyncio
async def test_capabilities_endpoint(client):
    \"\"\"Test capabilities endpoint.\"\"\"
    response = await client.get("/capabilities")
    assert response.status_code == 200
    
    data = response.json()
    assert "server_name" in data
    assert "capabilities" in data
    assert isinstance(data["capabilities"], list)


@pytest.mark.asyncio
async def test_sync_endpoint(client):
    \"\"\"Test sync endpoint.\"\"\"
    response = await client.post("/sync")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
"""

# --- Create pytest configuration ------------------------------------------------------
create_file "${BASE}/tests/conftest.py" """Pytest configuration for ${SRV} MCP server."""
import asyncio
import pytest


@pytest.fixture(scope="session")
def event_loop():
    \"\"\"Create event loop for async tests.\"\"\"
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
"""

# --- Create .env.example ------------------------------------------------------
create_file "${BASE}/.env.example" "# ${SRV^} MCP Server Environment Variables

# Server Configuration
${SRV^^}_PORT=${NEXT_PORT}
${SRV^^}_LOG_LEVEL=INFO
${SRV^^}_ENVIRONMENT=development

# API Configuration
${SRV^^}_API_KEY=your_api_key_here
${SRV^^}_API_BASE_URL=https://api.${SRV}.com/v1

# Database Configuration (optional)
${SRV^^}_DB_DSN=postgresql+asyncpg://user:pass@localhost:5432/${SRV}_db

# Sync Configuration
${SRV^^}_SYNC_ENABLED=true
${SRV^^}_SYNC_INTERVAL_MINUTES=30
${SRV^^}_SYNC_BATCH_SIZE=100

# Feature Flags
${SRV^^}_ENABLE_AI_PROCESSING=true
${SRV^^}_ENABLE_METRICS=true
"

# --- Create .gitignore ------------------------------------------------------
create_file "${BASE}/.gitignore" "# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Environment
.env
.env.local
.env.*.local

# Logs
logs/
*.log

# Database
*.db
*.sqlite

# Docker
docker-compose.override.yml
"

# --- Update mcp_config.json ------------------------------------------------------
echo -e "${BLUE}📝 Updating mcp_config.json...${NC}"

# Check if mcp_config.json exists
MCP_CONFIG="mcp_config.json"
if [[ -f "$MCP_CONFIG" ]]; then
    # Add new server to config
    python3 -c "
import json

with open('$MCP_CONFIG', 'r') as f:
    config = json.load(f)

# Add new server
config['mcpServers']['${SRV}'] = {
    'command': 'python',
    'args': ['-m', 'infrastructure.mcp_servers.${SRV}.server'],
    'env': {
        '${SRV^^}_PORT': '${NEXT_PORT}',
        '${SRV^^}_LOG_LEVEL': 'INFO'
    }
}

with open('$MCP_CONFIG', 'w') as f:
    json.dump(config, f, indent=2)

print('✓ Updated mcp_config.json')
"
fi

# --- Final summary ------------------------------------------------------
echo -e "\n${GREEN}✅ Successfully created ${SRV} MCP server!${NC}"
echo -e "\n${YELLOW}📋 Next steps:${NC}"
echo -e "  1. Review and customize the generated files"
echo -e "  2. Update API endpoints in handlers/main_handler.py"
echo -e "  3. Add ${SRV}-specific fields to models/data_models.py"
echo -e "  4. Configure environment variables (see .env.example)"
echo -e "  5. Run tests: pytest ${BASE}/tests"
echo -e "  6. Start server: python -m ${BASE}.server"
echo -e "\n${BLUE}📍 Server will run on port: ${NEXT_PORT}${NC}"
echo -e "\n${GREEN}🚀 Happy coding!${NC}" 