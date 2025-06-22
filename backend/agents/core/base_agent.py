"""Common agent base classes and utilities."""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .orchestrator import AgentCapability, AgentStatus, Task

logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Runtime configuration for an agent."""

    agent_id: str
    agent_type: str
    specialization: str
    redis_host: str = "localhost"
    redis_port: int = 6379
    openai_api_key: Optional[str] = None
    max_concurrent_tasks: int = 5


@dataclass
class TaskResult:
    """Result returned by ``process_task``."""
    status: str
    output: Any
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseAgent(ABC):
    """Base class for all agents in the Sophia platform."""

    def __init__(self, config: AgentConfig) -> None:
        self.config = config
        self.agent_id = config.agent_id
        self.agent_type = config.agent_type
        self.specialization = config.specialization
        self.status = AgentStatus.INACTIVE
        self.logger = logging.getLogger(self.__class__.__name__)
        self.is_running = False

    async def start(self) -> None:
        """Mark the agent as running."""
        self.logger.info("Starting agent %s", self.agent_id)
        self.is_running = True
        self.status = AgentStatus.ACTIVE

    async def stop(self) -> None:
        """Stop the agent."""
        self.logger.info("Stopping agent %s", self.agent_id)
        self.is_running = False
        self.status = AgentStatus.INACTIVE

    @abstractmethod
    async def get_capabilities(self) -> List[AgentCapability]:
        """Return the capabilities supported by this agent."""

    @abstractmethod
    async def process_task(self, task: Task) -> Dict[str, Any]:
        """Process a task and return the result payload."""


async def create_agent_response(
    success: bool,
    data: Any = None,
    error: str | None = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Helper to build a standardized response dictionary."""
    return {
        "success": success,
        "data": data,
        "error": error,
        "metadata": metadata or {},
    }


async def validate_task_data(task: Task, required_fields: List[str]) -> bool:
    """Validate that the required fields exist in ``task.task_data``."""
    missing = [field for field in required_fields if field not in task.task_data]
    if missing:
        logger.error("Missing required fields: %s", ", ".join(missing))
        return False
    return True
