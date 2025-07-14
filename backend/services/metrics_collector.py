"""
Metrics Collector
Collects and aggregates metrics from all services
"""

import asyncio
import json
from typing import Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MetricsCollector:
    """
    Collects metrics from all Sophia AI services
    """
    
    def __init__(self):
        self.collected_metrics = {}
        self.collection_interval = 30  # seconds
        self.running = False
    
    async def start_collection(self):
        """Start continuous metrics collection"""
        self.running = True
        while self.running:
            try:
                await self._collect_all_metrics()
                await asyncio.sleep(self.collection_interval)
            except Exception as e:
                logger.error(f"Error in metrics collection: {e}")
                await asyncio.sleep(5)  # Brief pause on error
    
    def stop_collection(self):
        """Stop metrics collection"""
        self.running = False
    
    async def _collect_all_metrics(self):
        """Collect metrics from all services"""
        from backend.services.performance_monitoring_service import performance_monitor
        
        # Collect performance metrics
        perf_metrics = performance_monitor.get_all_metrics()
        
        # Collect system metrics
        system_metrics = await self._collect_system_metrics()
        
        # Combine all metrics
        self.collected_metrics = {
            "timestamp": datetime.now().isoformat(),
            "performance": perf_metrics,
            "system": system_metrics,
            "alerts": performance_monitor.get_alerts(10)
        }
        
        logger.debug(f"Collected metrics for {len(perf_metrics)} services")
    
    async def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system-level metrics"""
        try:
            import psutil
            
            return {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "active_connections": len(psutil.net_connections())
            }
        except ImportError:
            return {"error": "psutil not available"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_latest_metrics(self) -> Dict[str, Any]:
        """Get the latest collected metrics"""
        return self.collected_metrics

# Global instance
metrics_collector = MetricsCollector()
