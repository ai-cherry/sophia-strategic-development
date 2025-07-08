"""
LangGraph Agent Base Class

Pure Python base class for all Sophia AI agents designed for LangGraph integration.
Replaces AgnoMCPBridge with optimized Python patterns and LangGraph compatibility.
"""
from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from core.integration_registry import IntegrationRegistry

logger = logging.getLogger(__name__)


class AgentCapability(Enum):
    """Agent capability types for intelligent routing"""

    SALES_INTELLIGENCE = "sales_intelligence"
    CALL_ANALYSIS = "call_analysis"
    MARKETING_ANALYSIS = "marketing_analysis"
    PROJECT_HEALTH = "project_health"
    SLACK_ANALYSIS = "slack_analysis"
    KNOWLEDGE_CURATION = "knowledge_curation"
    BUSINESS_INTELLIGENCE = "business_intelligence"
    EXECUTIVE_INTELLIGENCE = "executive_intelligence"
    SNOWFLAKE_ADMIN = "snowflake_admin"


class AgentStatus(Enum):
    """Agent execution status"""

    PENDING = "pending"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class AgentMetrics:
    """Performance metrics for agent monitoring"""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time_ms: float = 0.0
    total_response_time_ms: float = 0.0
    instantiation_time_ms: float = 0.0
    memory_usage_mb: float = 0.0
    last_activity: datetime | None = None

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests * 100

    def update_response_time(self, response_time_ms: float) -> None:
        """Update average response time with new measurement"""
        self.total_response_time_ms += response_time_ms
        self.avg_response_time_ms = self.total_response_time_ms / max(
            1, self.total_requests
        )

    def record_request(self, success: bool, response_time_ms: float) -> None:
        """Record a new request with success status and timing"""
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        self.update_response_time(response_time_ms)
        self.last_activity = datetime.now()


@dataclass
class AgentContext:
    """Context information for agent execution"""

    request_id: str
    user_id: str | None = None
    session_id: str | None = None
    workflow_id: str | None = None
    priority: str = "normal"
    timeout_ms: int = 30000
    metadata: dict[str, Any] = field(default_factory=dict)


class LangGraphAgentBase(ABC):
    """
    Base class for all LangGraph-compatible agents in Sophia AI.

    Provides optimized Python patterns for performance while maintaining
    LangGraph compatibility. Replaces AgnoMCPBridge functionality with
    pure Python implementation.

    Key Features:
    - Async-first design for optimal I/O performance
    - Built-in performance monitoring and metrics
    - LangGraph state compatibility
    - Intelligent caching and resource management
    - Comprehensive error handling and recovery
    """

    def __init__(
        self,
        agent_type: AgentCapability,
        name: str,
        capabilities: list[str],
        mcp_integrations: list[str],
        performance_target_ms: int = 200,
    ):
        self.agent_type = agent_type
        self.name = name
        self.capabilities = capabilities
        self.mcp_integrations = mcp_integrations
        self.performance_target_ms = performance_target_ms
        self.llm_service = None
        self.cortex_service = None
        self.ai_memory = None
        self.integration_registry = IntegrationRegistry()
        self.metrics = AgentMetrics()
        self.status = AgentStatus.PENDING
        self.initialized = False
        self.cache: dict[str, Any] = {}
        self.cache_ttl: dict[str, datetime] = {}
        self.config = {
            "cache_ttl_seconds": 300,
            "max_cache_size": 1000,
            "enable_metrics": True,
            "enable_caching": True,
            "log_performance": True,
        }
        logger.info(f"Initialized {self.name} agent with capabilities: {capabilities}")

    async def initialize(self) -> None:
        """Initialize the agent with all required services"""
        if self.initialized:
            return
        start_time = time.time()
        self.status = AgentStatus.INITIALIZING
        try:
            await self._initialize_services()
            await self.integration_registry.register(self.name, self)
            await self._agent_specific_initialization()
            init_time_ms = (time.time() - start_time) * 1000
            self.metrics.instantiation_time_ms = init_time_ms
            self.initialized = True
            self.status = AgentStatus.READY
            logger.info(f"✅ {self.name} agent initialized in {init_time_ms:.2f}ms")
        except Exception as e:
            self.status = AgentStatus.FAILED
            logger.exception(f"❌ Failed to initialize {self.name} agent: {e}")
            raise

    async def _initialize_services(self) -> None:
        """Initialize core services used by all agents"""
        try:
            from infrastructure.mcp_servers.enhanced_ai_memory_mcp_server import (
                EnhancedAiMemoryMCPServer,
            )
            from infrastructure.services.llm_router import llm_router
            from shared.utils.snowflake_cortex_service import SnowflakeCortexService

            self.llm_service = await get_unified_llm_service()
            await self.llm_service.initialize()
            self.cortex_service = SnowflakeCortexService()
            await self.cortex_service.initialize()
            self.ai_memory = EnhancedAiMemoryMCPServer()
            await self.ai_memory.initialize()
        except ImportError as e:
            logger.warning(f"Some services not available during initialization: {e}")
        except Exception as e:
            logger.exception(f"Failed to initialize services: {e}")
            raise

    @abstractmethod
    async def _agent_specific_initialization(self) -> None:
        """Agent-specific initialization logic to be implemented by subclasses"""
        pass

    async def process_request(
        self, request: dict[str, Any], context: AgentContext | None = None
    ) -> dict[str, Any]:
        """
        Process a request through the agent with performance monitoring

        Args:
            request: The request payload
            context: Optional execution context

        Returns:
            Agent response with metadata
        """
        if not self.initialized:
            await self.initialize()
        start_time = time.time()
        request_id = context.request_id if context else f"req_{int(time.time() * 1000)}"
        try:
            self.status = AgentStatus.RUNNING
            cache_key = self._generate_cache_key(request)
            if self.config["enable_caching"] and cache_key in self.cache:
                if self._is_cache_valid(cache_key):
                    cached_response = self.cache[cache_key]
                    cached_response["metadata"]["cache_hit"] = True
                    logger.debug(f"Cache hit for {self.name}: {cache_key}")
                    return cached_response
            response = await self._process_request_internal(request, context)
            processing_time_ms = (time.time() - start_time) * 1000
            response["metadata"] = response.get("metadata", {})
            response["metadata"].update(
                {
                    "agent_name": self.name,
                    "agent_type": self.agent_type.value,
                    "request_id": request_id,
                    "processing_time_ms": processing_time_ms,
                    "cache_hit": False,
                    "capabilities_used": self.capabilities,
                    "mcp_integrations": self.mcp_integrations,
                    "performance_target_ms": self.performance_target_ms,
                    "performance_achieved": processing_time_ms
                    <= self.performance_target_ms,
                }
            )
            if self.config["enable_caching"] and cache_key:
                self._cache_response(cache_key, response)
            self.metrics.record_request(True, processing_time_ms)
            self.status = AgentStatus.COMPLETED
            if self.config["log_performance"]:
                performance_status = (
                    "✅" if processing_time_ms <= self.performance_target_ms else "⚠️"
                )
                logger.info(
                    f"{performance_status} {self.name} processed request in {processing_time_ms:.2f}ms (target: {self.performance_target_ms}ms)"
                )
            return response
        except Exception as e:
            processing_time_ms = (time.time() - start_time) * 1000
            self.metrics.record_request(False, processing_time_ms)
            self.status = AgentStatus.FAILED
            logger.exception(
                f"❌ {self.name} request failed after {processing_time_ms:.2f}ms: {e}"
            )
            return {
                "success": False,
                "error": str(e),
                "metadata": {
                    "agent_name": self.name,
                    "agent_type": self.agent_type.value,
                    "request_id": request_id,
                    "processing_time_ms": processing_time_ms,
                    "error_type": type(e).__name__,
                },
            }

    @abstractmethod
    async def _process_request_internal(
        self, request: dict[str, Any], context: AgentContext | None = None
    ) -> dict[str, Any]:
        """Internal request processing logic to be implemented by subclasses"""
        pass

    def _generate_cache_key(self, request: dict[str, Any]) -> str | None:
        """Generate cache key for request (can be overridden by subclasses)"""
        if not self.config["enable_caching"]:
            return None
        import hashlib
        import json

        try:
            request_str = json.dumps(request, sort_keys=True)
            return hashlib.md5(request_str.encode(), usedforsecurity=False).hexdigest()
        except (TypeError, ValueError):
            return None

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached response is still valid"""
        if cache_key not in self.cache_ttl:
            return False
        expiry_time = self.cache_ttl[cache_key]
        return datetime.now() < expiry_time

    def _cache_response(self, cache_key: str, response: dict[str, Any]) -> None:
        """Cache response with TTL"""
        if len(self.cache) >= self.config["max_cache_size"]:
            oldest_key = min(self.cache_ttl.keys(), key=lambda k: self.cache_ttl[k])
            del self.cache[oldest_key]
            del self.cache_ttl[oldest_key]
        self.cache[cache_key] = response
        self.cache_ttl[cache_key] = (
            datetime.now().timestamp() + self.config["cache_ttl_seconds"]
        )

    async def health_check(self) -> dict[str, Any]:
        """Perform comprehensive health check"""
        health_status = {
            "agent_name": self.name,
            "agent_type": self.agent_type.value,
            "status": self.status.value,
            "initialized": self.initialized,
            "capabilities": self.capabilities,
            "mcp_integrations": self.mcp_integrations,
            "metrics": {
                "total_requests": self.metrics.total_requests,
                "success_rate": self.metrics.success_rate,
                "avg_response_time_ms": self.metrics.avg_response_time_ms,
                "instantiation_time_ms": self.metrics.instantiation_time_ms,
                "last_activity": self.metrics.last_activity.isoformat()
                if self.metrics.last_activity
                else None,
            },
            "cache_stats": {
                "cache_size": len(self.cache),
                "max_cache_size": self.config["max_cache_size"],
                "cache_enabled": self.config["enable_caching"],
            },
            "performance": {
                "target_ms": self.performance_target_ms,
                "achieving_target": self.metrics.avg_response_time_ms
                <= self.performance_target_ms
                if self.metrics.avg_response_time_ms > 0
                else True,
            },
        }
        return health_status

    async def get_performance_metrics(self) -> dict[str, Any]:
        """Get detailed performance metrics"""
        return {
            "agent_name": self.name,
            "agent_type": self.agent_type.value,
            "metrics": {
                "total_requests": self.metrics.total_requests,
                "successful_requests": self.metrics.successful_requests,
                "failed_requests": self.metrics.failed_requests,
                "success_rate_percent": self.metrics.success_rate,
                "avg_response_time_ms": self.metrics.avg_response_time_ms,
                "instantiation_time_ms": self.metrics.instantiation_time_ms,
                "last_activity": self.metrics.last_activity.isoformat()
                if self.metrics.last_activity
                else None,
            },
            "performance": {
                "target_response_time_ms": self.performance_target_ms,
                "achieving_target": self.metrics.avg_response_time_ms
                <= self.performance_target_ms
                if self.metrics.avg_response_time_ms > 0
                else True,
                "performance_ratio": self.performance_target_ms
                / max(1, self.metrics.avg_response_time_ms)
                if self.metrics.avg_response_time_ms > 0
                else 1.0,
            },
            "cache": {
                "size": len(self.cache),
                "max_size": self.config["max_cache_size"],
                "hit_ratio": "N/A",
                "enabled": self.config["enable_caching"],
            },
        }

    async def clear_cache(self) -> None:
        """Clear agent cache"""
        self.cache.clear()
        self.cache_ttl.clear()
        logger.info(f"Cleared cache for {self.name} agent")

    async def shutdown(self) -> None:
        """Gracefully shutdown the agent"""
        logger.info(f"Shutting down {self.name} agent...")
        await self.clear_cache()
        self.metrics = AgentMetrics()
        self.status = AgentStatus.PENDING
        self.initialized = False
        logger.info(f"✅ {self.name} agent shutdown complete")
