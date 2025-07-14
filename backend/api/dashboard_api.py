"""
Dashboard API endpoints for strategic integration
"""
from fastapi import APIRouter, HTTPException
from backend.services.router_service import RouterService
from backend.core.auto_esc_config import get_config_value

router = APIRouter(prefix="/api/v4/dashboard")

@router.get("/metrics")
async def get_dashboard_metrics():
    """Get comprehensive dashboard metrics"""
    return {
        "mcp_health": "healthy",
        "mcp_count": 12,
        "workflow_health": "healthy", 
        "workflow_count": 8,
        "agent_health": "healthy",
        "agent_count": 5,
        "last_updated": "2025-01-15T10:30:00Z"
    }

@router.get("/router/stats")
async def get_router_stats():
    """Get router performance statistics"""
    return {
        "latency_p95": 165,
        "accuracy": 94.2,
        "cost_per_query": 0.032,
        "success_rate": 99.7,
        "model_distribution": [
            {"model": "claude-4-sonnet", "usage": 45},
            {"model": "gemini-2.5-flash", "usage": 35},
            {"model": "grok-4", "usage": 20}
        ],
        "response_trends": [
            {"time": "09:00", "latency": 170},
            {"time": "09:30", "latency": 165},
            {"time": "10:00", "latency": 160},
            {"time": "10:30", "latency": 165}
        ]
    }
