"""Health monitoring for MCP server"""

import asyncio
import time
from typing import Dict, Any

class HealthMonitor:
    """Health monitoring for MCP server"""
    
    def __init__(self):
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
    
    async def get_health(self) -> Dict[str, Any]:
        """Get health status"""
        uptime = time.time() - self.start_time
        error_rate = self.error_count / max(1, self.request_count)
        
        return {
            "status": "healthy" if error_rate < 0.1 else "degraded",
            "uptime_seconds": uptime,
            "request_count": self.request_count,
            "error_count": self.error_count,
            "error_rate": error_rate
        }
    
    def record_request(self):
        """Record a request"""
        self.request_count += 1
    
    def record_error(self):
        """Record an error"""
        self.error_count += 1
