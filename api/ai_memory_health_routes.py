import random
import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/ai-memory", tags=["ai-memory-health"])


@router.get("/health")
async def get_ai_memory_health():
    """Get comprehensive AI Memory health status with mock data"""
    return {
        "performance_score": random.randint(90, 99),
        "response_times": {
            "average": random.randint(35, 50),
            "p95": random.randint(80, 120),
            "p99": random.randint(150, 200),
        },
        "cache_performance": {
            "hit_rate": random.uniform(0.85, 0.95),
            "size": random.randint(5000, 10000),
            "efficiency": random.uniform(0.9, 0.98),
        },
        "operation_stats": {
            "total_operations": random.randint(1000, 2000),
            "successful_operations": random.randint(990, 1980),
            "error_rate": random.uniform(0.001, 0.01),
        },
        "memory_usage": {
            "current": random.randint(1024, 2048),
            "peak": random.randint(2048, 4096),
            "efficiency": random.uniform(0.8, 0.95),
        },
        "recent_operations": [
            {
                "id": str(uuid.uuid4()),
                "operation": "recall_memory",
                "duration": random.randint(20, 50),
                "status": "success",
                "timestamp": (
                    datetime.utcnow() - timedelta(seconds=random.randint(1, 10))
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
