#!/usr/bin/env python3
"""
🚀 Performance Monitor for Sophia AI
Comprehensive performance tracking and alerting system
"""

import asyncio
import json
import logging
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Union
import threading
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class PerformanceLevel(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    WARNING = "warning"
    CRITICAL = "critical"

@dataclass
class PerformanceMetric:
    """Individual performance metric tracking"""
    name: str
    value: float
    timestamp: float
    level: PerformanceLevel
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PerformanceThreshold:
    """Performance threshold configuration"""
    warning_threshold: float
    critical_threshold: float
    measurement_window: int = 60  # seconds
    min_samples: int = 5

class PerformanceMonitor:
    """
    Comprehensive performance monitoring system
    
    Features:
    - Real-time performance tracking
    - Configurable thresholds and alerting
    - Performance regression detection
    - Automated performance optimization suggestions
    - Integration with connection manager
    """
    
    def __init__(self, max_history: int = 10000):
        self.max_history = max_history
        self._metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        self._thresholds: Dict[str, PerformanceThreshold] = {}
        self._alerts: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
        
        # Performance counters
        self._counters = defaultdict(int)
        self._timers = defaultdict(list)
        
        # Default thresholds
        self._setup_default_thresholds()

    def _setup_default_thresholds(self):
        """Setup default performance thresholds"""
        self._thresholds.update({
            'database_query': PerformanceThreshold(100, 500),  # ms
            'api_request': PerformanceThreshold(200, 1000),    # ms
            'agent_processing': PerformanceThreshold(500, 2000), # ms
            'memory_usage': PerformanceThreshold(70, 85),      # %
            'cpu_usage': PerformanceThreshold(80, 95),         # %
            'cache_hit_ratio': PerformanceThreshold(70, 50),   # % (inverted)
            'error_rate': PerformanceThreshold(5, 10),         # %
        })

    def monitor_performance(self, metric_name: str, threshold_ms: Optional[float] = None):
        """
        Decorator for automatic performance monitoring
        
        Args:
            metric_name: Name of the metric to track
            threshold_ms: Optional custom threshold in milliseconds
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    execution_time = (time.time() - start_time) * 1000  # Convert to ms
                    
                    # Record metric
                    self.record_metric(
                        metric_name,
                        execution_time,
                        context={
                            'function': func.__name__,
                            'args_count': len(args),
                            'kwargs_count': len(kwargs),
                            'success': True
                        }
                    )
                    
                    # Check threshold if provided
                    if threshold_ms and execution_time > threshold_ms:
                        self._create_alert(
                            metric_name,
                            f"Function {func.__name__} exceeded threshold: {execution_time:.2f}ms > {threshold_ms}ms",
                            PerformanceLevel.WARNING
                        )
                    
                    return result
                    
                except Exception as e:
                    execution_time = (time.time() - start_time) * 1000
                    
                    # Record failed metric
                    self.record_metric(
                        metric_name,
                        execution_time,
                        context={
                            'function': func.__name__,
                            'args_count': len(args),
                            'kwargs_count': len(kwargs),
                            'success': False,
                            'error': str(e)
                        }
                    )
                    
                    self._create_alert(
                        metric_name,
                        f"Function {func.__name__} failed after {execution_time:.2f}ms: {e}",
                        PerformanceLevel.CRITICAL
                    )
                    
                    raise
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    execution_time = (time.time() - start_time) * 1000
                    
                    self.record_metric(
                        metric_name,
                        execution_time,
                        context={
                            'function': func.__name__,
                            'args_count': len(args),
                            'kwargs_count': len(kwargs),
                            'success': True
                        }
                    )
                    
                    if threshold_ms and execution_time > threshold_ms:
                        self._create_alert(
                            metric_name,
                            f"Function {func.__name__} exceeded threshold: {execution_time:.2f}ms > {threshold_ms}ms",
                            PerformanceLevel.WARNING
                        )
                    
                    return result
                    
                except Exception as e:
                    execution_time = (time.time() - start_time) * 1000
                    
                    self.record_metric(
                        metric_name,
                        execution_time,
                        context={
                            'function': func.__name__,
                            'args_count': len(args),
                            'kwargs_count': len(kwargs),
                            'success': False,
                            'error': str(e)
                        }
                    )
                    
                    self._create_alert(
                        metric_name,
                        f"Function {func.__name__} failed after {execution_time:.2f}ms: {e}",
                        PerformanceLevel.CRITICAL
                    )
                    
                    raise
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        
        return decorator

    def record_metric(
        self,
        name: str,
        value: float,
        level: Optional[PerformanceLevel] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """Record a performance metric"""
        with self._lock:
            # Determine performance level if not provided
            if level is None:
                level = self._determine_performance_level(name, value)
            
            metric = PerformanceMetric(
                name=name,
                value=value,
                timestamp=time.time(),
                level=level,
                context=context or {}
            )
            
            self._metrics[name].append(metric)
            
            # Update counters
            self._counters[f"{name}_total"] += 1
            self._counters[f"{name}_{level.value}"] += 1
            
            # Check for alerts
            self._check_threshold_alerts(name, value)

    def _determine_performance_level(self, name: str, value: float) -> PerformanceLevel:
        """Determine performance level based on thresholds"""
        if name not in self._thresholds:
            return PerformanceLevel.GOOD
        
        threshold = self._thresholds[name]
        
        # Handle inverted metrics (like cache hit ratio)
        if name in ['cache_hit_ratio']:
            if value < threshold.critical_threshold:
                return PerformanceLevel.CRITICAL
            elif value < threshold.warning_threshold:
                return PerformanceLevel.WARNING
            else:
                return PerformanceLevel.EXCELLENT
        else:
            if value > threshold.critical_threshold:
                return PerformanceLevel.CRITICAL
            elif value > threshold.warning_threshold:
                return PerformanceLevel.WARNING
            elif value < threshold.warning_threshold * 0.5:
                return PerformanceLevel.EXCELLENT
            else:
                return PerformanceLevel.GOOD

    def _check_threshold_alerts(self, name: str, value: float):
        """Check if metric exceeds thresholds and create alerts"""
        if name not in self._thresholds:
            return
        
        threshold = self._thresholds[name]
        level = self._determine_performance_level(name, value)
        
        if level in [PerformanceLevel.WARNING, PerformanceLevel.CRITICAL]:
            self._create_alert(
                name,
                f"Metric {name} exceeded threshold: {value:.2f}",
                level
            )

    def _create_alert(self, metric_name: str, message: str, level: PerformanceLevel):
        """Create a performance alert"""
        alert = {
            'metric_name': metric_name,
            'message': message,
            'level': level.value,
            'timestamp': time.time(),
            'datetime': datetime.now().isoformat()
        }
        
        self._alerts.append(alert)
        
        # Keep only recent alerts
        if len(self._alerts) > 1000:
            self._alerts = self._alerts[-500:]
        
        # Log alert
        if level == PerformanceLevel.CRITICAL:
            logger.error(f"🚨 CRITICAL PERFORMANCE ALERT: {message}")
        elif level == PerformanceLevel.WARNING:
            logger.warning(f"⚠️ PERFORMANCE WARNING: {message}")

    def get_metrics_summary(self, metric_name: Optional[str] = None) -> Dict[str, Any]:
        """Get summary of performance metrics"""
        with self._lock:
            if metric_name:
                if metric_name not in self._metrics:
                    return {}
                
                metrics = list(self._metrics[metric_name])
                if not metrics:
                    return {}
                
                values = [m.value for m in metrics]
                recent_values = [m.value for m in metrics if time.time() - m.timestamp < 300]  # Last 5 minutes
                
                return {
                    'name': metric_name,
                    'total_samples': len(values),
                    'recent_samples': len(recent_values),
                    'avg': sum(values) / len(values),
                    'recent_avg': sum(recent_values) / len(recent_values) if recent_values else 0,
                    'min': min(values),
                    'max': max(values),
                    'p95': sorted(values)[int(len(values) * 0.95)] if values else 0,
                    'p99': sorted(values)[int(len(values) * 0.99)] if values else 0,
                    'current_level': metrics[-1].level.value if metrics else 'unknown'
                }
            else:
                # Summary of all metrics
                summary = {}
                for name in self._metrics:
                    summary[name] = self.get_metrics_summary(name)
                
                return summary

    def get_recent_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent performance alerts"""
        with self._lock:
            return self._alerts[-limit:] if self._alerts else []

    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        with self._lock:
            report = {
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'total_metrics': len(self._metrics),
                    'total_samples': sum(len(metrics) for metrics in self._metrics.values()),
                    'active_alerts': len([a for a in self._alerts if time.time() - a['timestamp'] < 300]),
                    'critical_alerts': len([a for a in self._alerts if a['level'] == 'critical' and time.time() - a['timestamp'] < 300])
                },
                'metrics': self.get_metrics_summary(),
                'recent_alerts': self.get_recent_alerts(20),
                'recommendations': self._generate_recommendations()
            }
            
            return report

    def _generate_recommendations(self) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        # Check database performance
        if 'database_query' in self._metrics:
            db_summary = self.get_metrics_summary('database_query')
            if db_summary.get('recent_avg', 0) > 200:
                recommendations.append("Consider implementing connection pooling for database queries")
            if db_summary.get('p95', 0) > 500:
                recommendations.append("Optimize slow database queries - 95th percentile > 500ms")
        
        # Check API performance
        if 'api_request' in self._metrics:
            api_summary = self.get_metrics_summary('api_request')
            if api_summary.get('recent_avg', 0) > 300:
                recommendations.append("API response times are high - consider caching or optimization")
        
        # Check memory usage
        if 'memory_usage' in self._metrics:
            mem_summary = self.get_metrics_summary('memory_usage')
            if mem_summary.get('recent_avg', 0) > 80:
                recommendations.append("High memory usage detected - implement memory optimization")
        
        # Check cache performance
        if 'cache_hit_ratio' in self._metrics:
            cache_summary = self.get_metrics_summary('cache_hit_ratio')
            if cache_summary.get('recent_avg', 0) < 60:
                recommendations.append("Low cache hit ratio - review caching strategy")
        
        return recommendations

    def set_threshold(
        self,
        metric_name: str,
        warning_threshold: float,
        critical_threshold: float,
        measurement_window: int = 60
    ):
        """Set custom performance threshold"""
        self._thresholds[metric_name] = PerformanceThreshold(
            warning_threshold=warning_threshold,
            critical_threshold=critical_threshold,
            measurement_window=measurement_window
        )

    def clear_metrics(self, metric_name: Optional[str] = None):
        """Clear performance metrics"""
        with self._lock:
            if metric_name:
                if metric_name in self._metrics:
                    self._metrics[metric_name].clear()
            else:
                self._metrics.clear()
                self._alerts.clear()
                self._counters.clear()

    @asynccontextmanager
    async def measure_performance(self, metric_name: str, context: Optional[Dict[str, Any]] = None):
        """Context manager for measuring performance"""
        start_time = time.time()
        try:
            yield
        finally:
            execution_time = (time.time() - start_time) * 1000
            self.record_metric(metric_name, execution_time, context=context)

# Global performance monitor instance
performance_monitor = PerformanceMonitor()

