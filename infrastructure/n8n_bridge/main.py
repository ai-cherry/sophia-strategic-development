from datetime import UTC, datetime

"""
N8N Bridge Service for Sophia AI MCP Integration
Provides seamless integration between N8N workflows and MCP orchestration service
"""

import asyncio
import logging
import os
from typing import Any

import redis.asyncio as redis
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Import existing MCP orchestration service
from infrastructure.services.mcp_orchestration_service import MCPOrchestrationService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Sophia AI N8N Bridge",
    description="Bridge service connecting N8N workflows with MCP orchestration",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class N8NWorkflowRequest(BaseModel):
    workflow_id: str
    execution_id: str
    node_name: str
    mcp_server: str = Field(
        ..., description="Target MCP server (ai_memory, gong_intelligence, etc.)"
    )
    enhancement_type: str = Field(
        default="business_intelligence", description="Type of AI enhancement"
    )
    data: dict[str, Any] = Field(..., description="Data to process")
    priority: str = Field(
        default="standard",
        description="Processing priority: low, standard, high, executive",
    )


class N8NResponse(BaseModel):
    success: bool
    data: dict[str, Any] | None = None
    error: str | None = None
    execution_time_ms: int
    mcp_servers_used: list[str]
    enhancement_applied: str


class N8NHealthResponse(BaseModel):
    status: str
    timestamp: str
    mcp_service_status: str
    redis_status: str
    active_workflows: int


# Global services
mcp_service: MCPOrchestrationService | None = None
redis_client: redis.Redis | None = None


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global mcp_service, redis_client

    try:
        # Initialize MCP orchestration service
        mcp_service = MCPOrchestrationService()
        await mcp_service.initialize_mcp_servers()
        logger.info("MCP orchestration service initialized")

        # Initialize Redis for caching and state management
        redis_url = os.getenv("REDIS_URL", "redis://redis-cache:6379")
        redis_client = redis.from_url(redis_url, decode_responses=True)
        await redis_client.ping()
        logger.info("Redis connection established")

        logger.info("N8N Bridge service started successfully")

    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global mcp_service, redis_client

    if redis_client:
        await redis_client.close()

    if mcp_service:
        await mcp_service.shutdown()

    logger.info("N8N Bridge service shut down")


@app.get("/health", response_model=N8NHealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Check MCP service health
        if mcp_service:
            mcp_health_data = await mcp_service.get_mcp_health_status()
            mcp_health = mcp_health_data.get("overall_health", "unavailable")
        else:
            mcp_health = "unavailable"

        # Check Redis health
        redis_health = "healthy"
        if redis_client:
            try:
                await redis_client.ping()
            except Exception:
                redis_health = "unavailable"
        else:
            redis_health = "unavailable"

        # Get active workflow count from Redis
        if redis_client:
            active_workflows = await redis_client.scard("active_workflows")
        else:
            active_workflows = 0

        return N8NHealthResponse(
            status=(
                "healthy"
                if mcp_health == "healthy" and redis_health == "healthy"
                else "degraded"
            ),
            timestamp=datetime.now(UTC).isoformat(),
            mcp_service_status=str(mcp_health),
            redis_status=redis_health,
            active_workflows=active_workflows,
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@app.post("/api/v1/n8n/process", response_model=N8NResponse)
async def process_n8n_request(
    request: N8NWorkflowRequest, background_tasks: BackgroundTasks
):
    """
    Process N8N workflow request through MCP orchestration
    This is the main integration endpoint
    """
    start_time = datetime.now(UTC)

    try:
        # Track active workflow
        if redis_client:
            await redis_client.sadd(
                "active_workflows", f"{request.workflow_id}:{request.execution_id}"
            )

        # Route request through MCP orchestration service
        mcp_response = await mcp_service.route_request(
            server_type=request.mcp_server,
            request_data={
                "action": "n8n_integration",
                "enhancement_type": request.enhancement_type,
                "data": request.data,
                "priority": request.priority,
                "workflow_context": {
                    "workflow_id": request.workflow_id,
                    "execution_id": request.execution_id,
                    "node_name": request.node_name,
                },
            },
            priority=request.priority,
        )

        # Calculate execution time
        execution_time = int((datetime.now(UTC) - start_time).total_seconds() * 1000)

        # Schedule cleanup in background
        background_tasks.add_task(
            cleanup_workflow_tracking, f"{request.workflow_id}:{request.execution_id}"
        )

        return N8NResponse(
            success=True,
            data=mcp_response.get("data"),
            execution_time_ms=execution_time,
            mcp_servers_used=mcp_response.get("servers_used", [request.mcp_server]),
            enhancement_applied=request.enhancement_type,
        )

    except Exception as e:
        execution_time = int((datetime.now(UTC) - start_time).total_seconds() * 1000)
        logger.error(f"N8N request processing failed: {e}")

        return N8NResponse(
            success=False,
            error=str(e),
            execution_time_ms=execution_time,
            mcp_servers_used=[],
            enhancement_applied="none",
        )


@app.post("/api/v1/n8n/batch-process")
async def batch_process_n8n_requests(
    requests: list[N8NWorkflowRequest], background_tasks: BackgroundTasks
):
    """
    Process multiple N8N requests in parallel for performance
    """
    start_time = datetime.now(UTC)

    try:
        # Process requests in parallel
        tasks = [process_single_request(request) for request in requests]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Clean up tracking
        for request in requests:
            background_tasks.add_task(
                cleanup_workflow_tracking,
                f"{request.workflow_id}:{request.execution_id}",
            )

        execution_time = int((datetime.now(UTC) - start_time).total_seconds() * 1000)

        return {
            "success": True,
            "results": results,
            "total_requests": len(requests),
            "execution_time_ms": execution_time,
        }

    except Exception as e:
        logger.error(f"Batch processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def process_single_request(request: N8NWorkflowRequest) -> dict[str, Any]:
    """Process a single N8N request"""
    try:
        mcp_response = await mcp_service.route_request(
            server_type=request.mcp_server,
            request_data={
                "action": "n8n_integration",
                "enhancement_type": request.enhancement_type,
                "data": request.data,
                "priority": request.priority,
            },
            priority=request.priority,
        )

        return {
            "success": True,
            "workflow_id": request.workflow_id,
            "data": mcp_response.get("data"),
            "servers_used": mcp_response.get("servers_used", []),
        }

    except Exception as e:
        return {"success": False, "workflow_id": request.workflow_id, "error": str(e)}


async def cleanup_workflow_tracking(workflow_key: str):
    """Remove workflow from active tracking"""
    if redis_client:
        try:
            await redis_client.srem("active_workflows", workflow_key)
        except Exception as e:
            logger.warning(f"Failed to cleanup workflow tracking: {e}")


@app.get("/api/v1/n8n/servers")
async def get_available_mcp_servers():
    """Get list of available MCP servers for N8N workflows"""
    try:
        if not mcp_service:
            raise HTTPException(status_code=503, detail="MCP service not available")

        servers = await mcp_service.get_available_servers()

        return {"success": True, "servers": servers, "total_count": len(servers)}

    except Exception as e:
        logger.error(f"Failed to get MCP servers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/n8n/metrics")
async def get_integration_metrics():
    """Get N8N integration performance metrics"""
    try:
        if not redis_client:
            return {"error": "Redis not available for metrics"}

        # Get metrics from Redis
        metrics = {}

        # Active workflows
        metrics["active_workflows"] = await redis_client.scard("active_workflows")

        # Recent execution times (if tracked)
        recent_times = await redis_client.lrange("execution_times", 0, 99)
        if recent_times:
            times = [float(t) for t in recent_times]
            metrics["avg_execution_time_ms"] = sum(times) / len(times)
            metrics["max_execution_time_ms"] = max(times)
            metrics["min_execution_time_ms"] = min(times)

        # MCP service metrics
        if mcp_service:
            mcp_metrics = await mcp_service.get_performance_metrics()
            metrics["mcp_metrics"] = mcp_metrics

        return metrics

    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/n8n/webhook/{workflow_id}")
async def n8n_webhook_handler(workflow_id: str, data: dict[str, Any]):
    """
    Handle webhooks from N8N workflows
    Useful for workflow completion notifications and data callbacks
    """
    try:
        logger.info(f"Received webhook for workflow {workflow_id}")

        # Store webhook data in Redis for processing
        if redis_client:
            await redis_client.setex(
                f"webhook:{workflow_id}", 3600, str(data)  # 1 hour TTL
            )

        # Route through MCP if needed
        if data.get("route_to_mcp"):
            await mcp_service.route_request(
                server_type=data.get("mcp_server", "ai_memory"),
                request_data={
                    "action": "webhook_processing",
                    "workflow_id": workflow_id,
                    "data": data,
                },
            )

        return {"success": True, "message": f"Webhook processed for {workflow_id}"}

    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9099)
