"""Core agent utilities and initialisation stubs."""

import logging
from typing import Any

from backend.agents.core.agent_router import CentralizedAgentRouter, agent_router
from backend.core.context_manager import context_manager

logger = logging.getLogger(__name__)


async def initialize_agent_system() -> bool:
    """Lightweight agent system initialisation used for tests."""
    try:
        await context_manager.initialize()
        agent_router.context_manager = context_manager
        logger.info("Agent system initialization complete")
        return True
    except Exception as exc:  # pragma: no cover - simple logging
        logger.error("Failed to initialize agent system: %s", exc)
        return False


async def shutdown_agent_system() -> None:
    """Shut down the agent system."""
    try:
        await context_manager.shutdown()
        logger.info("Agent system shutdown complete")
    except Exception as exc:  # pragma: no cover - simple logging
        logger.error("Error during agent system shutdown: %s", exc)


__all__ = [
    "agent_router",
    "context_manager",
    "initialize_agent_system",
    "shutdown_agent_system",
    "CentralizedAgentRouter",
]
