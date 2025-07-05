"""
Unified Service Registry
=======================

Central registry for all Sophia AI services.
Prevents duplicate instances and provides unified access.
"""

import logging
from typing import Any

from backend.services.advanced_ui_ux_agent_service import AdvancedUIUXAgentService
from backend.services.enhanced_knowledge_base_service import (
    EnhancedKnowledgeBaseService,
)
from backend.services.foundational_knowledge_service import FoundationalKnowledgeService
from backend.services.gptcache_service import GPTCacheService
from backend.services.mcp_orchestration_service import MCPOrchestrationService
from backend.services.payready_business_intelligence import (
    PayReadyBusinessIntelligenceOrchestrator,
)
from backend.services.predictive_automation_service import PredictiveAutomationService
from backend.services.sophia_ai_orchestrator import SophiaAIOrchestrator
from backend.services.unified_chat_service import UnifiedChatService

logger = logging.getLogger(__name__)


class UnifiedServiceRegistry:
    """
    Unified Service Registry - Single source of truth for all services

    This registry ensures:
    - Single instance of each service
    - Lazy initialization
    - Proper lifecycle management
    - Service discovery
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.services: dict[str, Any] = {}
            self.service_configs = {
                "sophia_orchestrator": {
                    "class": SophiaAIOrchestrator,
                    "description": "Main AI orchestration service",
                    "critical": True,
                },
                "mcp_orchestrator": {
                    "class": MCPOrchestrationService,
                    "description": "MCP server orchestration",
                    "critical": True,
                },
                "business_intelligence": {
                    "class": PayReadyBusinessIntelligenceOrchestrator,
                    "description": "Business intelligence and analytics",
                    "critical": False,
                },
                "ui_ux_agent": {
                    "class": AdvancedUIUXAgentService,
                    "description": "AI-powered UI/UX design",
                    "critical": False,
                },
                "cache_service": {
                    "class": GPTCacheService,
                    "description": "Intelligent caching service",
                    "critical": True,
                },
                "knowledge_base": {
                    "class": EnhancedKnowledgeBaseService,
                    "description": "Knowledge management service",
                    "critical": True,
                },
                "chat_service": {
                    "class": UnifiedChatService,
                    "description": "Unified chat interface",
                    "critical": True,
                },
                "foundational_knowledge": {
                    "class": FoundationalKnowledgeService,
                    "description": "Core knowledge service",
                    "critical": False,
                },
                "predictive_automation": {
                    "class": PredictiveAutomationService,
                    "description": "Predictive automation and insights",
                    "critical": False,
                },
            }
            self._initialized = True
            logger.info("UnifiedServiceRegistry initialized")

    async def get_service(self, service_name: str) -> Any | None:
        """
        Get or create a service instance

        Args:
            service_name: Name of the service to retrieve

        Returns:
            Service instance or None if not found
        """
        # Check if service already exists
        if service_name in self.services:
            return self.services[service_name]

        # Check if service is configured
        if service_name not in self.service_configs:
            logger.error(f"Unknown service requested: {service_name}")
            return None

        # Create service instance
        config = self.service_configs[service_name]
        try:
            service_class = config["class"]

            logger.info(f"Creating service: {service_name}")
            service_instance = service_class()

            # Initialize if it has an initialize method
            if hasattr(service_instance, "initialize"):
                await service_instance.initialize()

            # Store instance
            self.services[service_name] = service_instance
            logger.info(f"✅ Service created: {service_name}")

            return service_instance

        except Exception as e:
            logger.error(f"Failed to create service {service_name}: {e}")
            if config.get("critical", False):
                raise
            return None

    async def initialize_all_critical(self) -> bool:
        """
        Initialize all critical services

        Returns:
            True if all critical services initialized successfully
        """
        success = True

        for service_name, config in self.service_configs.items():
            if config.get("critical", False):
                service = await self.get_service(service_name)
                if service is None:
                    logger.error(
                        f"Failed to initialize critical service: {service_name}"
                    )
                    success = False

        return success

    async def get_all_services(self) -> dict[str, Any]:
        """Get all initialized services"""
        return self.services.copy()

    async def health_check(self) -> dict[str, dict[str, Any]]:
        """
        Perform health check on all services

        Returns:
            Health status for each service
        """
        health_status = {}

        for service_name, service in self.services.items():
            try:
                if hasattr(service, "health_check"):
                    status = await service.health_check()
                else:
                    # Basic check - service exists
                    status = {"healthy": True, "message": "Service active"}

                health_status[service_name] = {
                    "status": "healthy" if status.get("healthy", True) else "unhealthy",
                    "details": status,
                }
            except Exception as e:
                health_status[service_name] = {
                    "status": "error",
                    "details": {"error": str(e)},
                }

        return health_status

    async def shutdown(self):
        """Gracefully shutdown all services"""
        logger.info("Shutting down all services...")

        for service_name, service in self.services.items():
            try:
                if hasattr(service, "shutdown"):
                    await service.shutdown()
                logger.info(f"Service {service_name} shut down")
            except Exception as e:
                logger.error(f"Error shutting down {service_name}: {e}")

        self.services.clear()
        logger.info("All services shut down")


# Global registry instance
registry = UnifiedServiceRegistry()


# Convenience functions
async def get_service(service_name: str) -> Any | None:
    """Get a service from the registry"""
    return await registry.get_service(service_name)


async def get_sophia_orchestrator() -> SophiaAIOrchestrator | None:
    """Get the Sophia AI orchestrator"""
    return await registry.get_service("sophia_orchestrator")


async def get_mcp_orchestrator() -> MCPOrchestrationService | None:
    """Get the MCP orchestrator"""
    return await registry.get_service("mcp_orchestrator")


async def get_business_intelligence() -> PayReadyBusinessIntelligenceOrchestrator | None:
    """Get the business intelligence service"""
    return await registry.get_service("business_intelligence")


async def get_cache_service() -> GPTCacheService | None:
    """Get the cache service"""
    return await registry.get_service("cache_service")
