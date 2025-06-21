"""HubSpot Agent for Sophia AI - Placeholder"""

import logging

from backend.agents.core.base_agent import AgentConfig, BaseAgent, Task, TaskResult

logger = logging.getLogger(__name__)


class HubSpotAgent(BaseAgent):
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        logger.info("HubSpotAgent placeholder initialized.")

    async def execute_task(self, task: Task) -> TaskResult:
        logger.warning("HubSpotAgent is a placeholder and has no functionality.")
        return TaskResult(
            status="not_implemented",
            output="HubSpot integration is not fully connected yet.",
        )
