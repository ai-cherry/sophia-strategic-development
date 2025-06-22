"""Minimal agent router used for testing imports."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict

logger = logging.getLogger(__name__)


class AgentCapability(Enum):
    """Capabilities that an agent may expose."""

    DOCKER = "docker"
    PULUMI = "pulumi"
    GENERAL = "general"


@dataclass
class AgentRegistration:
    """Information describing a registered agent."""

    name: str
    capabilities: list[AgentCapability]
    handler: Callable[..., Any]
    description: str


class CentralizedAgentRouter:
    """Extremely small registry for agents."""

    def __init__(self) -> None:
        self._registry: Dict[str, AgentRegistration] = {}
        self.context_manager: Any = None

    def register_agent(self, registration: AgentRegistration, name: str | None = None) -> None:
        key = name or registration.name
        self._registry[key] = registration
        logger.debug("Registered agent %s", key)

    def get_registered_agents(self) -> Dict[str, AgentRegistration]:
        return dict(self._registry)

    def set_default_agent(self, name: str) -> None:
        self.default_agent = name


# Shared router instance used across the project
agent_router = CentralizedAgentRouter()

__all__ = [
    "AgentCapability",
    "AgentRegistration",
    "CentralizedAgentRouter",
    "agent_router",
]
