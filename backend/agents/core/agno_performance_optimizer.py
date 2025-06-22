"""Agno Performance Optimizer for Sophia AI.

Ultra-fast agent instantiation, pooling, and memory optimization for all agents.
Integrates with Agno framework and supports both traditional and Agno agents.
"""

import asyncio
import logging
from collections import defaultdict, deque
from datetime import datetime
from typing import Any, Dict, Optional, Type

logger = logging.getLogger(__name__)


class AgnoPerformanceOptimizer:
    """Optimizes agent performance using Agno's lightweight architecture.

    - Ultra-fast agent instantiation (~3μs)
    - Memory pooling and optimization
    - Agent pooling for high concurrency
    - Performance metrics tracking
    """

    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, pool_size_per_type: int = 10):
        self.agent_pools: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=pool_size_per_type)
        )
        self.agent_classes: Dict[str, Type] = {}
        self.performance_metrics: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.pool_size_per_type = pool_size_per_type
        self._initialized = False

    async def register_agent_class(self, agent_type: str, agent_class: Type):
        """Register an agent class for pooling and instantiation."""
        self.agent_classes[agent_type] = agent_class
        logger.info(f"Registered agent class for type: {agent_type}")

    async def get_or_create_agent(self, agent_type: str, config: Dict[str, Any]) -> Any:
        """Ultra-fast agent instantiation with pooling."""
        pool = self.agent_pools[agent_type]
        if pool:
            agent = pool.popleft()
            logger.debug(f"Reusing pooled agent for type: {agent_type}")
        else:
            agent_class = self.agent_classes.get(agent_type)
            if not agent_class:
                raise ValueError(f"Agent class not registered for type: {agent_type}")
            start_time = datetime.now()
            agent = agent_class(**config)
            duration_us = (datetime.now() - start_time).total_seconds() * 1e6
            self._track_performance(agent_type, "instantiation_us", duration_us)
            logger.info(
                f"Instantiated new agent for type: {agent_type} in {duration_us:.2f}μs"
            )
        return agent

    async def release_agent(self, agent_type: str, agent: Any):
        """Return an agent to the pool for reuse."""
        pool = self.agent_pools[agent_type]
        if len(pool) < self.pool_size_per_type:
            pool.append(agent)
            logger.debug(f"Agent returned to pool for type: {agent_type}")
        else:
            logger.debug(f"Agent pool full for type: {agent_type}, discarding agent")

    def _track_performance(self, agent_type: str, metric: str, value: Any):
        """Track performance metrics for each agent type."""
        metrics = self.performance_metrics[agent_type]
        if metric not in metrics:
            metrics[metric] = []
        metrics[metric].append(value)

    def get_metrics(self, agent_type: Optional[str] = None) -> Dict[str, Any]:
        """Get performance metrics for all or a specific agent type."""
        if agent_type:
            return self.performance_metrics.get(agent_type, {})
        return dict(self.performance_metrics)

    def clear_pools(self):
        """Clear all agent pools (for testing or memory management)."""
        self.agent_pools.clear()
        logger.info("Cleared all agent pools.")

    def clear_metrics(self):
        """Clear all performance metrics."""
        self.performance_metrics.clear()
        logger.info("Cleared all performance metrics.")
