
"""
Service Discovery Client
Provides centralized service endpoint resolution for MCP services
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional, List
import httpx

logger = logging.getLogger(__name__)

class ServiceDiscoveryClient:
    """Client for service discovery and health checking"""
    
    def __init__(self):
        self.registry_file = Path(__file__).parent.parent / "config" / "service_registry.json"
        self.registry = self._load_registry()
    
    def _load_registry(self) -> Dict:
        """Load service registry from configuration"""
        try:
            if self.registry_file.exists():
                return json.loads(self.registry_file.read_text())
            return {"services": {}, "instances": {}}
        except Exception as e:
            logger.error(f"Failed to load service registry: {e}")
            return {"services": {}, "instances": {}}
    
    def get_service_url(self, service_name: str) -> Optional[str]:
        """Get URL for a service"""
        return self.registry.get("services", {}).get(service_name, {}).get("url")
    
    def get_service_health_url(self, service_name: str) -> Optional[str]:
        """Get health check URL for a service"""
        return self.registry.get("services", {}).get(service_name, {}).get("health_url")
    
    async def check_service_health(self, service_name: str) -> bool:
        """Check if a service is healthy"""
        health_url = self.get_service_health_url(service_name)
        if not health_url:
            return False
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(health_url)
                return response.status_code == 200
        except Exception:
            return False
    
    def list_services(self) -> List[str]:
        """List all registered services"""
        return list(self.registry.get("services", {}).keys())

# Global instance
service_discovery = ServiceDiscoveryClient()
