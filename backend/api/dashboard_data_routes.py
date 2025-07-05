"""
Dashboard Data API Routes
=========================

Provides all the data endpoints that the UnifiedDashboard frontend expects.
"""

import logging
import random
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.services.unified_service_registry import (
    get_cache_service,
    registry,
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1", tags=["Dashboard Data"])


# Simple dependency for current user
async def get_current_user() -> dict:
    """Get current user - simplified for now"""
    return {"user_id": "user", "role": "admin"}


class DashboardSummary(BaseModel):
    """CEO Dashboard summary data"""

    project_health: int = Field(description="Overall project health percentage")
    budget_usage: int = Field(description="Budget usage percentage")
    team_utilization: int = Field(description="Team utilization percentage")
    on_time_delivery: int = Field(description="On-time delivery percentage")
    timestamp: datetime = Field(default_factory=datetime.now)


class ProjectInfo(BaseModel):
    """Project information"""

    id: str
    name: str
    platform: str
    health_score: int
    completion_percentage: int
    team_members: list[str]
    okr_alignment: str


class LLMStats(BaseModel):
    """LLM usage statistics"""

    daily_cost: float
    cost_change: float
    daily_requests: int
    request_change: float
    avg_response_time: int
    response_time_change: float
    cache_hit_rate: int
    cache_improvement: float
    providers: list[dict[str, Any]]
    task_costs: dict[str, float]
    request_trend: dict[str, Any]
    snowflake_savings: float
    data_movement_avoided: int
    snowflake_percentage: int
    budget_status: dict[str, Any]
    alerts: list[dict[str, Any]]


class CacheStats(BaseModel):
    """Cache statistics"""

    total_entries: int
    memory_usage_mb: float
    hit_rate: float
    miss_rate: float
    eviction_rate: float
    avg_ttl_seconds: int
    top_cached_queries: list[dict[str, Any]]
    cache_by_type: dict[str, int]


@router.get("/unified/dashboard/summary", response_model=DashboardSummary)
async def get_dashboard_summary(current_user: dict = Depends(get_current_user)):
    """Get CEO dashboard summary metrics"""
    try:
        # In production, these would come from real data sources
        # For now, return realistic mock data
        return DashboardSummary(
            project_health=85, budget_usage=62, team_utilization=78, on_time_delivery=91
        )
    except Exception as e:
        logger.error(f"Error getting dashboard summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects", response_model=dict[str, list[ProjectInfo]])
async def get_projects(current_user: dict = Depends(get_current_user)):
    """Get cross-platform project information"""
    try:
        # Mock project data
        projects = [
            ProjectInfo(
                id="proj_001",
                name="AI Chat Enhancement",
                platform="Linear",
                health_score=92,
                completion_percentage=75,
                team_members=["Alice", "Bob"],
                okr_alignment="Q4-KR1",
            ),
            ProjectInfo(
                id="proj_002",
                name="Customer Onboarding Flow",
                platform="Asana",
                health_score=78,
                completion_percentage=45,
                team_members=["Charlie", "Diana"],
                okr_alignment="Q4-KR2",
            ),
            ProjectInfo(
                id="proj_003",
                name="Performance Optimization",
                platform="GitHub",
                health_score=85,
                completion_percentage=60,
                team_members=["Eve", "Frank"],
                okr_alignment="Q4-KR3",
            ),
        ]

        return {"projects": projects}
    except Exception as e:
        logger.error(f"Error getting projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge/stats")
async def get_knowledge_stats(current_user: dict = Depends(get_current_user)):
    """Get knowledge base statistics"""
    try:
        return {
            "total_documents": 1247,
            "total_embeddings": 45892,
            "ingestion_jobs": {"active": 2, "completed": 156, "failed": 3},
            "data_sources": {
                "gong": {
                    "status": "active",
                    "last_sync": datetime.now() - timedelta(hours=1),
                },
                "hubspot": {
                    "status": "active",
                    "last_sync": datetime.now() - timedelta(hours=2),
                },
                "snowflake": {
                    "status": "active",
                    "last_sync": datetime.now() - timedelta(minutes=30),
                },
            },
            "ai_learning_metrics": {
                "concepts_learned": 892,
                "accuracy_improvement": 12.5,
                "query_success_rate": 94.2,
            },
        }
    except Exception as e:
        logger.error(f"Error getting knowledge stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sales/summary")
async def get_sales_summary(current_user: dict = Depends(get_current_user)):
    """Get sales intelligence summary"""
    try:
        return {
            "pipeline_value": 2450000,
            "deals_in_progress": 23,
            "win_rate": 68.5,
            "avg_deal_size": 106521,
            "top_opportunities": [
                {"name": "Enterprise Corp", "value": 450000, "probability": 75},
                {"name": "Tech Startup Inc", "value": 280000, "probability": 85},
                {"name": "Global Solutions", "value": 320000, "probability": 60},
            ],
            "team_performance": {
                "top_performer": "Sarah Johnson",
                "calls_this_week": 147,
                "meetings_scheduled": 23,
            },
        }
    except Exception as e:
        logger.error(f"Error getting sales summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/llm/stats", response_model=LLMStats)
async def get_llm_stats(current_user: dict = Depends(get_current_user)):
    """Get LLM usage statistics"""
    try:
        # Generate realistic mock data
        providers = [
            {
                "provider": "openai",
                "model": "gpt-4o",
                "requests": 3456,
                "cost": 45.23,
                "avg_latency": 342,
                "primary_task_type": "analysis",
            },
            {
                "provider": "snowflake",
                "model": "cortex-large",
                "requests": 8923,
                "cost": 12.45,
                "avg_latency": 128,
                "primary_task_type": "embeddings",
            },
            {
                "provider": "anthropic",
                "model": "claude-3-opus",
                "requests": 1234,
                "cost": 28.91,
                "avg_latency": 456,
                "primary_task_type": "generation",
            },
        ]

        task_costs = {
            "analysis": 34.12,
            "generation": 28.91,
            "embeddings": 12.45,
            "search": 8.23,
            "classification": 5.67,
        }

        # Generate trend data
        labels = [
            (datetime.now() - timedelta(days=i)).strftime("%m/%d")
            for i in range(6, -1, -1)
        ]
        values = [random.randint(8000, 12000) for _ in range(7)]

        alerts = []
        daily_cost = sum(p["cost"] for p in providers)

        # Check if over budget
        daily_budget = 100
        if daily_cost > daily_budget * 0.8:
            alerts.append(
                {
                    "severity": "warning" if daily_cost < daily_budget else "critical",
                    "title": "Budget Alert",
                    "message": f"Daily spend at {(daily_cost/daily_budget)*100:.1f}% of budget",
                    "timestamp": datetime.now().isoformat(),
                }
            )

        return LLMStats(
            daily_cost=daily_cost,
            cost_change=-5.2,
            daily_requests=sum(p["requests"] for p in providers),
            request_change=12.3,
            avg_response_time=int(
                sum(p["avg_latency"] * p["requests"] for p in providers)
                / sum(p["requests"] for p in providers)
            ),
            response_time_change=-8.1,
            cache_hit_rate=72,
            cache_improvement=5.3,
            providers=providers,
            task_costs=task_costs,
            request_trend={"labels": labels, "values": values},
            snowflake_savings=156.78,
            data_movement_avoided=234,
            snowflake_percentage=65,
            budget_status={
                "daily_budget": daily_budget,
                "weekly_budget": 700,
                "monthly_budget": 3000,
                "is_over_budget": daily_cost > daily_budget,
            },
            alerts=alerts,
        )
    except Exception as e:
        logger.error(f"Error getting LLM stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cache/stats", response_model=CacheStats)
async def get_cache_stats(current_user: dict = Depends(get_current_user)):
    """Get cache statistics"""
    try:
        # Try to get real cache stats
        cache_service = await get_cache_service()

        if cache_service and hasattr(cache_service, "get_stats"):
            stats = cache_service.get_stats()
            if hasattr(stats, "__await__"):
                stats = await stats
            return CacheStats(**stats)

        # Mock data if cache service not available
        return CacheStats(
            total_entries=3456,
            memory_usage_mb=234.5,
            hit_rate=0.72,
            miss_rate=0.28,
            eviction_rate=0.05,
            avg_ttl_seconds=3600,
            top_cached_queries=[
                {
                    "query": "revenue last quarter",
                    "hits": 234,
                    "last_accessed": datetime.now(),
                },
                {
                    "query": "customer churn rate",
                    "hits": 189,
                    "last_accessed": datetime.now() - timedelta(minutes=15),
                },
                {
                    "query": "team performance metrics",
                    "hits": 156,
                    "last_accessed": datetime.now() - timedelta(hours=1),
                },
            ],
            cache_by_type={
                "embeddings": 1234,
                "llm_responses": 892,
                "search_results": 678,
                "analytics": 652,
            },
        )
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health/dashboard")
async def dashboard_health_check():
    """Health check for dashboard services"""
    try:
        # Check critical services
        services_health = await registry.health_check()

        # Determine overall health
        critical_services = ["sophia_orchestrator", "cache_service", "knowledge_base"]
        critical_healthy = all(
            services_health.get(s, {}).get("status") == "healthy"
            for s in critical_services
            if s in services_health
        )

        return {
            "status": "healthy" if critical_healthy else "degraded",
            "timestamp": datetime.now().isoformat(),
            "services": services_health,
            "dashboard_ready": critical_healthy,
        }
    except Exception as e:
        logger.error(f"Dashboard health check error: {e}")
        return {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "dashboard_ready": False,
        }
