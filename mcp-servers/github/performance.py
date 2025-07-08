"""Performance optimization utilities"""

import time
from collections.abc import Callable
from functools import wraps
from typing import Any


class PerformanceOptimizer:
    """Performance optimization utilities"""

    def __init__(self):
        self.metrics = {}
        self.cache = {}

    def measure_time(self, func_name: str):
        """Decorator to measure function execution time"""

        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    return result
                finally:
                    duration = time.time() - start_time
                    self._record_metric(func_name, duration)

            return wrapper

        return decorator

    def _record_metric(self, name: str, duration: float):
        """Record performance metric"""
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append(duration)

        # Keep only last 100 measurements
        if len(self.metrics[name]) > 100:
            self.metrics[name] = self.metrics[name][-100:]

    def get_metrics(self) -> dict[str, Any]:
        """Get performance metrics"""
        result = {}
        for name, durations in self.metrics.items():
            if durations:
                result[name] = {
                    "avg": sum(durations) / len(durations),
                    "min": min(durations),
                    "max": max(durations),
                    "count": len(durations),
                }
        return result
