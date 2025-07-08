from fastapi import APIRouter

from api.ai_memory_health_routes import get_ai_memory_health
from api.deployment_status_routes import get_deployment_status

# Import functions from other route modules
from api.lambda_labs_health_routes import get_lambda_labs_health

router = APIRouter(prefix="/api/v1/unified", tags=["unified-health"])


def calculate_weighted_health(
    infrastructure: float, ai_memory: float, deployment: float
) -> float:
    """Calculate a weighted overall health score."""
    # Weights can be adjusted based on business priority
    weights = {"infrastructure": 0.4, "ai_memory": 0.3, "deployment": 0.3}

    weighted_score = (
        infrastructure * weights["infrastructure"]
        + ai_memory * weights["ai_memory"]
        + deployment * weights["deployment"]
    )
    return round(weighted_score, 2)


async def get_system_alerts():
    """Get mock system-wide alerts."""
    alerts = [
        {
            "id": "alert-1",
            "severity": "warning",
            "title": "High GPU Usage",
            "message": "Instance 'sophia-ai-prod' GPU usage is at 85%.",
            "timestamp": "2025-07-07T10:00:00Z",
            "instance": "sophia-ai-prod",
        },
        {
            "id": "alert-2",
            "severity": "info",
            "title": "Deployment Complete",
            "message": "Frontend deployment to Vercel succeeded.",
            "timestamp": "2025-07-07T09:30:00Z",
            "server": "Vercel",
        },
    ]
    return alerts


async def get_health_recommendations():
    """Get mock health recommendations."""
    recommendations = [
        {
            "id": "rec-1",
            "title": "Scale Up AI Memory Cache",
            "description": "Cache hit rate is below target. Consider increasing cache size to improve performance.",
        },
        {
            "id": "rec-2",
            "title": "Review Backend Service",
            "description": "'Sophia Backend' is in a restart loop. Check container logs for errors.",
        },
    ]
    return recommendations


@router.get("/health")
async def get_unified_health():
    """Get correlated health status across all systems"""
    # Aggregate health from all services
    lambda_health = await get_lambda_labs_health()
    ai_memory_health = await get_ai_memory_health()
    deployment_status = await get_deployment_status()

    overall_health = calculate_weighted_health(
        infrastructure=lambda_health.overall_health,
        ai_memory=ai_memory_health.get("performance_score", 0),
        deployment=deployment_status.get("deployment_health", 0),
    )

    return {
        "overall_health": overall_health,
        "infrastructure": lambda_health.dict(),
        "ai_memory": ai_memory_health,
        "deployment": deployment_status,
        "alerts": await get_system_alerts(),
        "recommendations": await get_health_recommendations(),
    }
