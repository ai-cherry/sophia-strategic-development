"""
System Monitoring Service for Sophia AI
Provides system health and performance monitoring functionality
"""

import logging
import psutil
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class SystemMonitoringService:
    """Service for monitoring system health and performance"""
    
    def __init__(self):
        self.logger = logger
        self.initialized = False
        
    async def initialize(self) -> None:
        """Initialize the system monitoring service"""
        try:
            self.logger.info("Initializing System Monitoring Service...")
            self.initialized = True
            self.logger.info("✅ System Monitoring Service initialized successfully")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize System Monitoring Service: {e}")
            raise
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            if not self.initialized:
                await self.initialize()
                
            # Get system metrics using psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            metrics = {
                "timestamp": datetime.utcnow().isoformat(),
                "cpu": {
                    "percent": cpu_percent,
                    "count": psutil.cpu_count(),
                    "load_avg": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": (disk.used / disk.total) * 100
                },
                "health_status": "healthy" if cpu_percent < 80 and memory.percent < 85 else "degraded"
            }
            
            self.logger.info("Retrieved system metrics")
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error retrieving system metrics: {e}")
            return {
                "error": str(e),
                "health_status": "error"
            }
    
    async def get_service_status(self) -> List[Dict[str, Any]]:
        """Get status of running services"""
        try:
            # Check common Sophia AI services
            services = [
                {"name": "backend", "port": 8000, "status": "unknown"},
                {"name": "frontend", "port": 5173, "status": "unknown"},
                {"name": "mcp_memory", "port": 9001, "status": "unknown"},
                {"name": "mcp_ui_ux", "port": 9002, "status": "unknown"}
            ]
            
            # Check each service port
            import socket
            for service in services:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        sock.settimeout(1)
                        result = sock.connect_ex(('localhost', service['port']))
                        service['status'] = "running" if result == 0 else "down"
                except Exception:
                    service['status'] = "down"
            
            return services
            
        except Exception as e:
            self.logger.error(f"Error checking service status: {e}")
            return []
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the monitoring service"""
        return {
            "service": "SystemMonitoringService",
            "status": "healthy" if self.initialized else "not_initialized",
            "initialized": self.initialized,
            "version": "1.0.0"
        }


# Create a global instance for easy import
system_monitoring_service = SystemMonitoringService() 