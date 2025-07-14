"""
Performance Monitoring Service
Provides comprehensive performance tracking for all services
"""

import time
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json

logger = logging.getLogger(__name__)

class PerformanceMonitoringService:
    """
    Comprehensive performance monitoring for Sophia AI services
    """
    
    def __init__(self, max_history_size: int = 1000):
        self.max_history_size = max_history_size
        self.metrics = defaultdict(lambda: {
            "response_times": deque(maxlen=max_history_size),
            "error_rates": deque(maxlen=max_history_size),
            "throughput": deque(maxlen=max_history_size),
            "last_updated": None
        })
        self.alerts = []
        self.thresholds = {
            "response_time_ms": 200,  # Alert if >200ms
            "error_rate_percent": 5,  # Alert if >5% errors
            "throughput_min": 10      # Alert if <10 req/min
        }
    
    async def track_request(self, service_name: str, request_start: float, 
                           success: bool = True) -> Dict[str, Any]:
        """Track a service request"""
        response_time = (time.time() - request_start) * 1000  # Convert to ms
        
        metrics = self.metrics[service_name]
        metrics["response_times"].append(response_time)
        metrics["error_rates"].append(0 if success else 1)
        metrics["throughput"].append(time.time())
        metrics["last_updated"] = datetime.now()
        
        # Check thresholds
        await self._check_thresholds(service_name)
        
        return {
            "service": service_name,
            "response_time_ms": response_time,
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _check_thresholds(self, service_name: str):
        """Check if service metrics exceed thresholds"""
        metrics = self.metrics[service_name]
        
        if len(metrics["response_times"]) < 5:  # Need minimum data
            return
        
        # Check average response time (last 10 requests)
        recent_times = list(metrics["response_times"])[-10:]
        avg_response_time = sum(recent_times) / len(recent_times)
        
        if avg_response_time > self.thresholds["response_time_ms"]:
            await self._create_alert(
                service_name, 
                "HIGH_RESPONSE_TIME",
                f"Average response time {avg_response_time:.2f}ms exceeds threshold"
            )
        
        # Check error rate (last 20 requests)
        recent_errors = list(metrics["error_rates"])[-20:]
        error_rate = (sum(recent_errors) / len(recent_errors)) * 100
        
        if error_rate > self.thresholds["error_rate_percent"]:
            await self._create_alert(
                service_name,
                "HIGH_ERROR_RATE", 
                f"Error rate {error_rate:.2f}% exceeds threshold"
            )
    
    async def _create_alert(self, service_name: str, alert_type: str, message: str):
        """Create a performance alert"""
        alert = {
            "service": service_name,
            "type": alert_type,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "severity": "WARNING"
        }
        
        self.alerts.append(alert)
        logger.warning(f"Performance Alert: {alert}")
        
        # Keep only last 100 alerts
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
    
    def get_service_metrics(self, service_name: str) -> Dict[str, Any]:
        """Get metrics for a specific service"""
        if service_name not in self.metrics:
            return {"error": "Service not found"}
        
        metrics = self.metrics[service_name]
        
        if not metrics["response_times"]:
            return {"service": service_name, "status": "no_data"}
        
        response_times = list(metrics["response_times"])
        error_rates = list(metrics["error_rates"])
        
        return {
            "service": service_name,
            "avg_response_time_ms": sum(response_times) / len(response_times),
            "p95_response_time_ms": sorted(response_times)[int(len(response_times) * 0.95)],
            "error_rate_percent": (sum(error_rates) / len(error_rates)) * 100,
            "total_requests": len(response_times),
            "last_updated": metrics["last_updated"].isoformat() if metrics["last_updated"] else None
        }
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get metrics for all services"""
        return {
            service: self.get_service_metrics(service) 
            for service in self.metrics.keys()
        }
    
    def get_alerts(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        return self.alerts[-limit:]

# Global instance
performance_monitor = PerformanceMonitoringService()
