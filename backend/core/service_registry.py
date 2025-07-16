"""
Service Registry for Sophia AI
Provides centralized service access to avoid circular dependencies
"""

import logging
from typing import Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ServiceConfig:
    """Service configuration"""
    name: str
    module_path: str
    class_name: str
    singleton: bool = True
    dependencies: list = None

class ServiceRegistry:
    """Central service registry to avoid circular dependencies"""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._configs: Dict[str, ServiceConfig] = {}
        self._initialized = False
        
    def register_service(self, config: ServiceConfig):
        """Register a service configuration"""
        self._configs[config.name] = config
        logger.info(f"Registered service: {config.name}")
    
    async def get_service(self, name: str) -> Any:
        """Get service instance"""
        if name in self._services:
            return self._services[name]
        
        if name not in self._configs:
            raise ValueError(f"Service not registered: {name}")
        
        config = self._configs[name]
        
        # Dynamic import to avoid circular dependencies
        module = __import__(config.module_path, fromlist=[config.class_name])
        service_class = getattr(module, config.class_name)
        
        # Create instance
        service_instance = service_class()
        
        # Initialize if needed
        if hasattr(service_instance, 'initialize'):
            await service_instance.initialize()
        
        # Store if singleton
        if config.singleton:
            self._services[name] = service_instance
        
        logger.info(f"Created service instance: {name}")
        return service_instance
    
    async def initialize(self):
        """Initialize service registry"""
        if self._initialized:
            return
        
        # Register core services
        self.register_service(ServiceConfig(
            name="redis_manager",
            module_path="backend.core.redis_connection_manager",
            class_name="RedisConnectionManager"
        ))
        
        self.register_service(ServiceConfig(
            name="qdrant_memory",
            module_path="backend.services.qdrant_unified_memory_service",
            class_name="QdrantUnifiedMemoryService"
        ))
        
        self.register_service(ServiceConfig(
            name="etl_adapter",
            module_path="backend.etl.adapters.unified_etl_adapter",
            class_name="UnifiedETLAdapter"
        ))
        
        self._initialized = True
        logger.info("✅ Service Registry initialized")

# Global registry instance
service_registry = ServiceRegistry()

async def get_service(name: str) -> Any:
    """Get service from registry"""
    if not service_registry._initialized:
        await service_registry.initialize()
    return await service_registry.get_service(name)
