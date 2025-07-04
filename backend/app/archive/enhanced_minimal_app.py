"""
Enhanced minimal FastAPI app with production monitoring and LangChain features.
"""

import asyncio
import os
from datetime import datetime
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend.monitoring.mcp_health_monitor import health_monitor
from backend.services.fast_document_processor import FastDocumentProcessor
from backend.services.gptcache_service import cache_service
from backend.services.mcp_capability_router import capability_router
from backend.services.project_intelligence_service import ProjectIntelligenceService
from backend.services.structured_output_service import (
    StructuredOutputService,
)

app = FastAPI(
    title="Sophia AI Backend - Enhanced",
    version="2.0.0",
    description="Production monitoring, caching, and LangChain features",
)

# Initialize services
project_service = ProjectIntelligenceService()
structured_output_service = StructuredOutputService()
document_processor = FastDocumentProcessor()


# Request/Response models
class RouteRequest(BaseModel):
    """Request for capability routing."""

    capability: str
    priority: str = "normal"
    context: Optional[dict[str, Any]] = None


class DocumentRequest(BaseModel):
    """Request for document processing."""

    documents: list[dict[str, Any]]
    metadata: Optional[dict[str, Any]] = None


class StructuredOutputRequest(BaseModel):
    """Request for structured output generation."""

    prompt: str
    output_type: str  # executive_summary, deal_analysis, call_insights
    data: dict[str, Any]
    focus_area: Optional[str] = None


# Original endpoints
@app.get("/")
async def root():
    return {
        "message": "Sophia AI Enhanced Backend is running",
        "version": "2.0.0",
        "features": [
            "MCP Health Monitoring",
            "GPTCache Integration",
            "Capability Routing",
            "Project Intelligence",
            "Structured Outputs",
            "Fast Document Processing",
        ],
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/health")
async def health():
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "sophia-backend-enhanced",
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


# MCP Monitoring endpoints
@app.get("/api/mcp/health")
async def get_mcp_health():
    """Get health status of all MCP servers."""
    try:
        health_data = await health_monitor.get_all_health_status()
        return {
            "servers": health_data,
            "summary": {
                "total": len(health_data),
                "healthy": sum(
                    1 for s in health_data.values() if s["status"] == "healthy"
                ),
                "degraded": sum(
                    1 for s in health_data.values() if s["status"] == "degraded"
                ),
                "unhealthy": sum(
                    1 for s in health_data.values() if s["status"] == "unhealthy"
                ),
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/mcp/servers/{server_name}")
async def get_server_health(server_name: str):
    """Get detailed health for specific MCP server."""
    try:
        health_data = await health_monitor.check_server_health(server_name)
        if not health_data:
            raise HTTPException(
                status_code=404, detail=f"Server {server_name} not found"
            )
        return health_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Cache management endpoints
@app.get("/api/cache/stats")
async def get_cache_stats():
    """Get cache statistics."""
    try:
        stats = await cache_service.get_cache_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/cache/clear")
async def clear_cache(pattern: Optional[str] = None):
    """Clear cache entries."""
    try:
        cleared = await cache_service.clear_cache(pattern)
        return {"cleared": cleared, "pattern": pattern}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Capability routing endpoints
@app.post("/api/route")
async def route_capability(request: RouteRequest):
    """Route request to best MCP server based on capability."""
    try:
        result = await capability_router.route_request(
            capability=request.capability,
            priority=request.priority,
            context=request.context,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/capabilities")
async def list_capabilities():
    """List all available capabilities and their mappings."""
    try:
        return {
            "capabilities": capability_router.get_all_capabilities(),
            "servers": capability_router.get_server_capabilities(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# System metrics
@app.get("/api/metrics")
async def get_system_metrics():
    """Get comprehensive system metrics."""
    try:
        return {
            "mcp_health": await health_monitor.get_metrics(),
            "cache_performance": await cache_service.get_performance_metrics(),
            "routing_stats": capability_router.get_routing_stats(),
            "document_processing": document_processor.get_metrics().dict(),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Strategic Enhancement Endpoints


# 1. Project Intelligence endpoints
@app.get("/api/projects/summary")
async def get_project_summary():
    """Get comprehensive project summary for CEO dashboard."""
    try:
        summary = await project_service.get_project_summary()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects/team-performance")
async def get_team_performance():
    """Get team performance metrics."""
    try:
        performance = await project_service.get_team_performance()
        return performance
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects/milestones")
async def get_milestone_tracking():
    """Get upcoming milestones and risk assessment."""
    try:
        milestones = await project_service.get_milestone_tracking()
        return milestones
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 2. Structured Output endpoints
@app.post("/api/structured-output/generate")
async def generate_structured_output(request: StructuredOutputRequest):
    """Generate structured output with guaranteed parsing."""
    try:
        if request.output_type == "executive_summary":
            result = await structured_output_service.get_executive_summary(
                data=request.data, focus_area=request.focus_area or "business"
            )
        elif request.output_type == "deal_analysis":
            result = await structured_output_service.analyze_deal(
                deal_data=request.data
            )
        elif request.output_type == "call_insights":
            result = await structured_output_service.analyze_call(
                transcript=request.data.get("transcript", ""),
                metadata=request.data.get("metadata", {}),
            )
        else:
            raise HTTPException(
                status_code=400, detail=f"Unknown output type: {request.output_type}"
            )

        return result.dict()

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 3. Fast Document Processing endpoints
@app.post("/api/documents/process")
async def process_documents(request: DocumentRequest):
    """Process documents with 25x performance improvement."""
    try:
        results = await document_processor.process_documents_batch(
            documents=request.documents, metadata=request.metadata
        )

        return {
            "results": [r.dict() for r in results],
            "summary": {
                "total": len(results),
                "successful": sum(1 for r in results if r.status == "completed"),
                "failed": sum(1 for r in results if r.status == "failed"),
                "cached": sum(1 for r in results if r.cache_hit),
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/documents/metrics")
async def get_document_processing_metrics():
    """Get document processing performance metrics."""
    try:
        metrics = document_processor.get_metrics()
        optimizations = await document_processor.optimize_performance()

        return {"metrics": metrics.dict(), "optimizations": optimizations}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Dashboard integration endpoint
@app.get("/api/dashboard/executive")
async def get_executive_dashboard_data():
    """Get all data needed for executive dashboard in one call."""
    try:
        # Gather all data concurrently
        project_task = project_service.get_project_summary()
        team_task = project_service.get_team_performance()
        milestone_task = project_service.get_milestone_tracking()
        metrics_task = get_system_metrics()

        # Wait for all
        project_data, team_data, milestone_data, system_metrics = await asyncio.gather(
            project_task, team_task, milestone_task, metrics_task
        )

        return {
            "projects": project_data,
            "teams": team_data,
            "milestones": milestone_data,
            "system_health": system_metrics,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
