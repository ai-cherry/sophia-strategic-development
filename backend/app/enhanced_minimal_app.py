"""Enhanced Minimal FastAPI app with monitoring and caching"""
import asyncio
import os

# Import our new services
import sys
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

sys.path.append("/app")
from backend.monitoring.mcp_health_monitor import health_monitor
from backend.services.gptcache_service import CEO_COMMON_QUERIES, cache_service
from backend.services.mcp_capability_router import Capability, capability_router

app = FastAPI(
    title="Sophia AI Backend - Enhanced",
    version="2.0.0",
    description="Enhanced backend with health monitoring and intelligent caching",
)


class QueryRequest(BaseModel):
    query: str
    context: Optional[dict] = None
    use_cache: bool = True


class RoutingRequest(BaseModel):
    capability: str
    context: Optional[dict] = None
    prefer_servers: Optional[list[str]] = None
    avoid_servers: Optional[list[str]] = None


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    # Warm the cache with common CEO queries
    cache_service.warm_cache(CEO_COMMON_QUERIES)

    # Start health monitoring in background
    asyncio.create_task(health_monitor.start_monitoring())

    print("✅ Enhanced Sophia AI Backend started")
    print(f"🔍 Health monitoring active for {len(health_monitor.servers)} servers")
    print(f"💾 Cache warmed with {len(CEO_COMMON_QUERIES)} common queries")


@app.get("/")
async def root():
    """Root endpoint with system info"""
    return {
        "message": "Sophia AI Enhanced Backend is running",
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "pulumi_org": os.getenv("PULUMI_ORG", "unknown"),
        "timestamp": datetime.utcnow().isoformat(),
        "features": {
            "health_monitoring": True,
            "intelligent_caching": True,
            "capability_routing": True,
        },
    }


@app.get("/health")
async def health():
    """Basic health check"""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "sophia-backend-enhanced",
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@app.get("/api/health")
async def api_health():
    """API health with service status"""
    health_summary = health_monitor.get_health_summary()
    cache_stats = cache_service.get_stats()

    return {
        "status": "healthy",
        "service": "sophia-backend-api",
        "timestamp": datetime.utcnow().isoformat(),
        "mcp_servers": {
            "total": health_summary["total_servers"],
            "healthy": health_summary["healthy"],
            "degraded": health_summary["degraded"],
            "unhealthy": health_summary["unhealthy"],
            "health_percentage": health_summary["health_percentage"],
        },
        "cache": cache_stats,
    }


@app.get("/api/mcp/health")
async def get_mcp_health():
    """Get detailed MCP server health status"""
    return health_monitor.get_health_summary()


@app.get("/api/mcp/servers")
async def get_mcp_servers():
    """List all MCP servers and their capabilities"""
    servers = {}
    for server_name in health_monitor.servers.keys():
        servers[server_name] = {
            "port": health_monitor.servers[server_name]["port"],
            "capabilities": [
                cap.value
                for cap in capability_router.get_server_capabilities(server_name)
            ],
            "health": health_monitor.health_cache.get(server_name, {}),
        }
    return servers


@app.post("/api/query")
async def process_query(request: QueryRequest):
    """Process a query with optional caching"""
    # Check cache first if enabled
    if request.use_cache:
        cached_result = await cache_service.get(request.query, request.context)
        if cached_result:
            result, similarity = cached_result
            return {
                "result": result,
                "cached": True,
                "cache_similarity": similarity,
                "timestamp": datetime.utcnow().isoformat(),
            }

    # Simulate processing (in production, this would call Snowflake/AI services)
    result = {
        "response": f"Processed query: {request.query}",
        "data": {"placeholder": "This would be real data from Snowflake/AI"},
    }

    # Cache the result
    if request.use_cache:
        await cache_service.set(request.query, result, request.context)

    return {
        "result": result,
        "cached": False,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/api/cache/stats")
async def get_cache_stats():
    """Get cache statistics"""
    return cache_service.get_stats()


@app.delete("/api/cache/clear")
async def clear_cache():
    """Clear the cache"""
    cache_service.clear_cache()
    return {"message": "Cache cleared successfully"}


@app.post("/api/route")
async def route_capability(request: RoutingRequest):
    """Route a request to the best MCP server for a capability"""
    try:
        # Convert string to Capability enum
        capability = Capability(request.capability)

        # Update health data for routing
        health_data = {}
        for server, health in health_monitor.health_cache.items():
            health_data[server] = {"status": health.status.value}
        capability_router.update_server_health(health_data)

        # Get routing decision
        decision = await capability_router.route_request(
            capability, request.context, request.prefer_servers, request.avoid_servers
        )

        return {
            "primary_server": decision.primary_server,
            "fallback_servers": decision.fallback_servers,
            "confidence": decision.confidence_score,
            "reason": decision.reason,
        }
    except ValueError:
        raise HTTPException(
            status_code=400, detail=f"Invalid capability: {request.capability}"
        )


@app.get("/api/capabilities")
async def get_capabilities():
    """Get all available capabilities and their server coverage"""
    return capability_router.get_capability_coverage()


@app.get("/api/routing/stats")
async def get_routing_stats():
    """Get routing statistics"""
    return capability_router.get_routing_stats()


@app.get("/api/metrics")
async def get_metrics():
    """Get system metrics"""
    health_summary = health_monitor.get_health_summary()
    cache_stats = cache_service.get_stats()
    routing_stats = capability_router.get_routing_stats()

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "health": {
            "servers_total": health_summary["total_servers"],
            "servers_healthy": health_summary["healthy"],
            "health_percentage": health_summary["health_percentage"],
        },
        "cache": {
            "hit_rate": cache_stats["hit_rate"],
            "total_hits": cache_stats["hits"],
            "total_misses": cache_stats["misses"],
        },
        "routing": {
            "total_requests": routing_stats["total_requests"],
            "average_confidence": routing_stats.get("average_confidence", 0),
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
