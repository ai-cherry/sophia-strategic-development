"""
Sophia AI Data Flow API Routes

Simple and practical API endpoints for data ingestion and monitoring.
Focuses on stability and ease of use without over-complexity.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
from datetime import datetime

from backend.core.data_flow_manager import get_data_flow_manager, DataFlowManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/data-flow", tags=["data-flow"])


class DataIngestionRequest(BaseModel):
    source_name: str
    data: Dict[str, Any]
    priority: Optional[int] = 2  # 1=high, 2=medium, 3=low


class HealthResponse(BaseModel):
    overall_status: str
    data_sources: Dict[str, Dict[str, Any]]
    queue_status: Dict[str, Any]
    metrics: Dict[str, Any]
    timestamp: str


@router.post("/ingest")
async def ingest_data(
    request: DataIngestionRequest,
    background_tasks: BackgroundTasks,
    data_manager: DataFlowManager = Depends(get_data_flow_manager),
):
    """
    Ingest data from external sources

    Simple endpoint that accepts data and queues it for processing
    with appropriate reliability patterns based on source type.
    """
    try:
        logger.info(f"Received data ingestion request from {request.source_name}")

        # Validate source
        if request.source_name not in data_manager.data_sources:
            raise HTTPException(
                status_code=400, detail=f"Unknown data source: {request.source_name}"
            )

        # Ingest data with reliability patterns
        success = await data_manager.ingest_data(request.source_name, request.data)

        if not success:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to ingest data from {request.source_name}",
            )

        return {
            "status": "success",
            "message": f"Data from {request.source_name} queued for processing",
            "source": request.source_name,
            "timestamp": datetime.now().isoformat(),
            "queue_size": data_manager.processing_queue.qsize(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Data ingestion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=HealthResponse)
async def get_health_status(
    data_manager: DataFlowManager = Depends(get_data_flow_manager),
):
    """
    Get comprehensive health status of the data flow system

    Returns status of all data sources, processing queues, workers,
    and system metrics for monitoring and debugging.
    """
    try:
        health_data = await data_manager.get_health_status()

        return HealthResponse(
            overall_status=health_data["overall_status"],
            data_sources=health_data["data_sources"],
            queue_status=health_data["queues"],
            metrics=health_data["metrics"],
            timestamp=datetime.now().isoformat(),
        )

    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sources")
async def list_data_sources(
    data_manager: DataFlowManager = Depends(get_data_flow_manager),
):
    """
    List all registered data sources and their configurations

    Simple endpoint to see what data sources are available
    and their current status.
    """
    try:
        sources = []
        for name, source in data_manager.data_sources.items():
            sources.append(
                {
                    "name": source.name,
                    "type": source.source_type,
                    "reliability_pattern": source.reliability_pattern,
                    "health_status": source.health_status,
                    "last_sync": (
                        source.last_sync.isoformat() if source.last_sync else None
                    ),
                }
            )

        return {
            "sources": sources,
            "total_count": len(sources),
            "healthy_count": len(
                [s for s in sources if s["health_status"] == "healthy"]
            ),
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"List sources error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_processing_metrics(
    data_manager: DataFlowManager = Depends(get_data_flow_manager),
):
    """
    Get detailed processing metrics

    Returns metrics about data processing performance,
    cache efficiency, and system health indicators.
    """
    try:
        health_data = await data_manager.get_health_status()

        # Calculate additional metrics
        total_events = (
            health_data["metrics"]["processed_events"]
            + health_data["metrics"]["failed_events"]
        )
        success_rate = (
            (health_data["metrics"]["processed_events"] / total_events * 100)
            if total_events > 0
            else 100
        )

        cache_total = (
            health_data["metrics"]["cache_hits"]
            + health_data["metrics"]["cache_misses"]
        )
        cache_hit_rate = (
            (health_data["metrics"]["cache_hits"] / cache_total * 100)
            if cache_total > 0
            else 0
        )

        return {
            "processing_metrics": {
                "total_events_processed": total_events,
                "successful_events": health_data["metrics"]["processed_events"],
                "failed_events": health_data["metrics"]["failed_events"],
                "success_rate_percent": round(success_rate, 2),
                "current_queue_size": health_data["queues"]["processing_queue_size"],
                "dead_letter_queue_size": health_data["queues"][
                    "dead_letter_queue_size"
                ],
                "active_workers": health_data["queues"]["active_workers"],
            },
            "cache_metrics": {
                "cache_hits": health_data["metrics"]["cache_hits"],
                "cache_misses": health_data["metrics"]["cache_misses"],
                "hit_rate_percent": round(cache_hit_rate, 2),
                "cache_status": health_data["cache_status"],
            },
            "system_status": {
                "overall_health": health_data["overall_status"],
                "last_health_check": health_data["metrics"]["last_health_check"],
            },
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Metrics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sources/{source_name}/test")
async def test_data_source(
    source_name: str, data_manager: DataFlowManager = Depends(get_data_flow_manager)
):
    """
    Test a specific data source connection

    Simple endpoint to test if a data source is reachable
    and functioning properly.
    """
    try:
        if source_name not in data_manager.data_sources:
            raise HTTPException(
                status_code=404, detail=f"Data source '{source_name}' not found"
            )

        source = data_manager.data_sources[source_name]

        # Test data ingestion with minimal test data
        test_data = {
            "test": True,
            "timestamp": datetime.now().isoformat(),
            "source": source_name,
        }

        success = await data_manager.ingest_data(source_name, test_data)

        return {
            "source_name": source_name,
            "test_result": "success" if success else "failed",
            "source_type": source.source_type,
            "reliability_pattern": source.reliability_pattern,
            "current_health": source.health_status,
            "timestamp": datetime.now().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Source test error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queue/status")
async def get_queue_status(
    data_manager: DataFlowManager = Depends(get_data_flow_manager),
):
    """
    Get detailed queue status and worker information

    Returns information about processing queues and worker status
    for monitoring system performance.
    """
    try:
        health_data = await data_manager.get_health_status()
        queue_info = health_data["queues"]

        # Get circuit breaker status
        circuit_breaker_info = health_data.get("circuit_breakers", {})

        return {
            "processing_queue": {
                "size": queue_info["processing_queue_size"],
                "status": (
                    "healthy" if queue_info["processing_queue_size"] < 100 else "busy"
                ),
            },
            "dead_letter_queue": {
                "size": queue_info["dead_letter_queue_size"],
                "status": (
                    "ok"
                    if queue_info["dead_letter_queue_size"] == 0
                    else "attention_needed"
                ),
            },
            "workers": {
                "active_count": queue_info["active_workers"],
                "total_configured": data_manager.worker_count,
                "status": (
                    "healthy"
                    if queue_info["active_workers"] == data_manager.worker_count
                    else "degraded"
                ),
            },
            "circuit_breakers": circuit_breaker_info,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Queue status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cache/clear")
async def clear_cache(
    cache_type: Optional[str] = None,
    data_manager: DataFlowManager = Depends(get_data_flow_manager),
):
    """
    Clear cache data

    Simple endpoint to clear cache when needed for debugging
    or when data needs to be refreshed.
    """
    try:
        if cache_type:
            # Clear specific cache type
            keys_to_remove = [
                k for k in data_manager.cache.l1_cache.keys() if cache_type in k
            ]
            for key in keys_to_remove:
                del data_manager.cache.l1_cache[key]

            # Clear from Redis if available
            if data_manager.cache.redis_client:
                pattern = f"*{cache_type}*"
                keys = await data_manager.cache.redis_client.keys(pattern)
                if keys:
                    await data_manager.cache.redis_client.delete(*keys)

            return {
                "status": "success",
                "message": f"Cleared cache for type: {cache_type}",
                "keys_cleared": len(keys_to_remove),
                "timestamp": datetime.now().isoformat(),
            }
        else:
            # Clear all cache
            data_manager.cache.l1_cache.clear()

            if data_manager.cache.redis_client:
                await data_manager.cache.redis_client.flushdb()

            return {
                "status": "success",
                "message": "Cleared all cache data",
                "timestamp": datetime.now().isoformat(),
            }

    except Exception as e:
        logger.error(f"Cache clear error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Webhook endpoints for real-time data ingestion
@router.post("/webhook/{source_name}")
async def webhook_endpoint(
    source_name: str,
    data: Dict[str, Any],
    data_manager: DataFlowManager = Depends(get_data_flow_manager),
):
    """
    Webhook endpoint for real-time data ingestion

    Simple webhook that external systems can call to send data
    directly to the processing pipeline.
    """
    try:
        logger.info(f"Webhook data received from {source_name}")

        # Add webhook metadata
        webhook_data = {
            **data,
            "ingestion_method": "webhook",
            "received_at": datetime.now().isoformat(),
            "source": source_name,
        }

        success = await data_manager.ingest_data(source_name, webhook_data)

        if not success:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process webhook data from {source_name}",
            )

        return {
            "status": "received",
            "source": source_name,
            "timestamp": datetime.now().isoformat(),
            "queue_position": data_manager.processing_queue.qsize(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
