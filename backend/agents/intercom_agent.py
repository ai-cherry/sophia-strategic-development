"""Intercom Agent for Sophia AI - Placeholder
"""
import logging

from backend.agents.core.base_agent import AgentConfig, BaseAgent, Task, TaskResult

logger = logging.getLogger(__name__)


class IntercomAgent(BaseAgent):
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        logger.info("IntercomAgent placeholder initialized.")

    async def execute_task(self, task: Task) -> TaskResult:
        logger.warning("IntercomAgent is a placeholder and has no functionality.")
        return TaskResult(
            status="not_implemented",
            output="Intercom integration is not fully connected yet.",
        )
