"""Performance monitoring utilities."""

import time
from contextlib import contextmanager
from typing import Dict, Any

class PerformanceMonitor:
    """Simple performance monitoring."""
    
    def __init__(self):
        self.metrics: Dict[str, Any] = {}
    
    @contextmanager
    def measure(self, operation: str):
        """Measure operation performance."""
        start = time.time()
        try:
            yield
        finally:
            duration = time.time() - start
            self.metrics[operation] = {
                'duration': duration,
                'timestamp': time.time()
            }

performance_monitor = PerformanceMonitor()
