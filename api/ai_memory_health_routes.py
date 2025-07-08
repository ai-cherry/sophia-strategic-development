import secrets
import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/ai-memory", tags=["ai-memory-health"])


@router.get("/health")
async def get_ai_memory_health():
    """Get comprehensive AI Memory health status with mock data"""
    return {
        "performance_score": secrets.randbelow(99 - 90 + 1) + 90,
        "response_times": {
            "average": secrets.randbelow(50 - 35 + 1) + 35,
            "p95": secrets.randbelow(120 - 80 + 1) + 80,
            "p99": secrets.randbelow(200 - 150 + 1) + 150,
        },
        "cache_performance": {
            "hit_rate": random.uniform(0.85, 0.95),
            "size": secrets.randbelow(10000 - 5000 + 1) + 5000,
            "efficiency": random.uniform(0.9, 0.98),
        },
        "operation_stats": {
            "total_operations": secrets.randbelow(2000 - 1000 + 1) + 1000,
            "successful_operations": secrets.randbelow(1980 - 990 + 1) + 990,
            "error_rate": random.uniform(0.001, 0.01),
        },
        "memory_usage": {
            "current": secrets.randbelow(2048 - 1024 + 1) + 1024,
            "peak": secrets.randbelow(4096 - 2048 + 1) + 2048,
            "efficiency": random.uniform(0.8, 0.95),
        },
        "recent_operations": [
            {
                "id": str(uuid.uuid4()),
                "operation": "recall_memory",
                "duration": secrets.randbelow(50 - 20 + 1) + 20,
                "status": "success",
                "timestamp": (
                    datetime.utcnow()
                    - timedelta(seconds=secrets.randbelow(10 - 1 + 1) + 1)
                ).isoformat()
                + "Z",
            }
            for _ in range(10)
        ],
    }


@router.get("/performance-trends")
async def get_performance_trends():
    """Get AI Memory performance trends over time"""
    return {
        "labels": ["1h ago", "45m ago", "30m ago", "15m ago", "now"],
        "response_times": [45, 42, 38, 41, 39],
        "cache_hit_rates": [85, 87, 89, 88, 91],
        "operation_counts": [150, 165, 180, 175, 195],
    }
