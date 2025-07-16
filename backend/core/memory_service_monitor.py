"""
Memory Service Monitoring
Provides comprehensive monitoring and metrics for memory service
"""

import logging
import time
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class MemoryServiceMetrics:
    """Memory service performance metrics"""
    timestamp: float
    query_count: int = 0
    average_query_time: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    connection_pool_active: int = 0
    connection_pool_idle: int = 0
    error_count: int = 0
    

class MemoryServiceMonitor:
    """Monitors memory service performance"""
    
    def __init__(self):
        self._metrics: List[MemoryServiceMetrics] = []
        self._current_metrics = MemoryServiceMetrics(timestamp=time.time())
        self._query_times: List[float] = []
    
    def record_query(self, duration: float, success: bool = True):
        """Record query execution"""
        self._current_metrics.query_count += 1
        
        if success:
            self._query_times.append(duration)
            if len(self._query_times) > 100:  # Keep last 100 queries
                self._query_times.pop(0)
            
            self._current_metrics.average_query_time = sum(self._query_times) / len(self._query_times)
        else:
            self._current_metrics.error_count += 1
    
    def record_cache_hit(self):
        """Record cache hit"""
        self._current_metrics.cache_hits += 1
    
    def record_cache_miss(self):
        """Record cache miss"""
        self._current_metrics.cache_misses += 1
    
    def update_pool_stats(self, active: int, idle: int):
        """Update connection pool statistics"""
        self._current_metrics.connection_pool_active = active
        self._current_metrics.connection_pool_idle = idle
    
    def get_current_metrics(self) -> MemoryServiceMetrics:
        """Get current metrics snapshot"""
        self._current_metrics.timestamp = time.time()
        return self._current_metrics
    
    def get_cache_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total = self._current_metrics.cache_hits + self._current_metrics.cache_misses
        if total == 0:
            return 0.0
        return self._current_metrics.cache_hits / total
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        cache_hit_rate = self.get_cache_hit_rate()
        
        return {
            "query_performance": {
                "total_queries": self._current_metrics.query_count,
                "average_time": f"{self._current_metrics.average_query_time:.3f}s",
                "error_rate": f"{(self._current_metrics.error_count / max(1, self._current_metrics.query_count)) * 100:.1f}%"
            },
            "cache_performance": {
                "hit_rate": f"{cache_hit_rate * 100:.1f}%",
                "total_hits": self._current_metrics.cache_hits,
                "total_misses": self._current_metrics.cache_misses
            },
            "connection_pool": {
                "active_connections": self._current_metrics.connection_pool_active,
                "idle_connections": self._current_metrics.connection_pool_idle,
                "total_connections": self._current_metrics.connection_pool_active + self._current_metrics.connection_pool_idle
            }
        }
    
    def log_performance_summary(self):
        """Log performance summary"""
        summary = self.get_performance_summary()
        logger.info("📊 Memory Service Performance Summary:")
        logger.info(f"   Query Performance: {summary['query_performance']}")
        logger.info(f"   Cache Performance: {summary['cache_performance']}")
        logger.info(f"   Connection Pool: {summary['connection_pool']}")


# Global monitor instance
_monitor: Optional[MemoryServiceMonitor] = None


def get_memory_monitor() -> MemoryServiceMonitor:
    """Get global memory service monitor"""
    global _monitor
    
    if _monitor is None:
        _monitor = MemoryServiceMonitor()
    
    return _monitor
