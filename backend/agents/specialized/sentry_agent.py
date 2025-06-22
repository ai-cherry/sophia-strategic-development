import logging
from typing import Any, Dict, List

from backend.agents.core.base_agent import (
    AgentCapability,
    AgentConfig,
    BaseAgent,
    Task,
    create_agent_response,
)
from backend.mcp.mcp_client import MCPClient

logger = logging.getLogger(__name__)

SENTRY_MCP_REMOTE_URL = "https://mcp.sentry.dev/mcp"  # Remote hosted Sentry MCP

class SentryAgent(BaseAgent):
    """
    Sophia AI - Sentry Agent (Agno-compatible)

    Connects to the Sentry MCP Server to fetch error context, trigger Seer AI fixes,
    and enable automated debugging workflows for Pay Ready.
    """
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.mcp_client = MCPClient()
        # Future: Add Agno stateful workflow support here

    @classmethod
    async def pooled(cls, config: AgentConfig) -> "SentryAgent":
        """Get a pooled or new instance using AgnoPerformanceOptimizer."""
        from ..core.agno_performance_optimizer import AgnoPerformanceOptimizer
        optimizer = AgnoPerformanceOptimizer()
        await optimizer.register_agent_class("sentry", cls)
        agent = await optimizer.get_or_create_agent("sentry", {"config": config})
        logger.info("[AgnoPerformanceOptimizer] Provided SentryAgent instance (pooled or new)")
        return agent

    async def get_capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="fetch_sentry_issue_context",
                description="Fetches full context for a Sentry issue (error details, stack trace, project info).",
                input_types=["issue_id", "project_slug"],
                output_types=["issue_context"],
                estimated_duration=5.0,
            ),
            AgentCapability(
                name="trigger_seer_ai_fix",
                description="Triggers Sentry Seer AI to attempt an automated fix for a given issue.",
                input_types=["issue_id", "project_slug"],
                output_types=["fix_status"],
                estimated_duration=10.0,
            ),
        ]

    async def process_task(self, task: Task) -> Dict[str, Any]:
        """Process assigned Sentry-related task."""
        try:
            task_type = task.task_type
            if task_type == "fetch_sentry_issue_context":
                return await self._fetch_sentry_issue_context(task)
            elif task_type == "trigger_seer_ai_fix":
                return await self._trigger_seer_ai_fix(task)
            else:
                return await create_agent_response(
                    False, error=f"Unknown task type: {task_type}"
                )
        except Exception as e:
            logger.error(f"SentryAgent task failed: {e}")
            return await create_agent_response(False, error=str(e))

    async def _fetch_sentry_issue_context(self, task: Task) -> Dict[str, Any]:
        """Fetch full context for a Sentry issue via MCP tool call."""
        try:
            issue_id = task.task_data.get("issue_id")
            project_slug = task.task_data.get("project_slug")
            if not issue_id or not project_slug:
                return await create_agent_response(False, error="Missing issue_id or project_slug.")
            # Compose MCP tool call (example: get_sentry_issue)
            request = f"get_sentry_issue: project={project_slug}, issue={issue_id}"
            context = {"project_slug": project_slug, "issue_id": issue_id}
            response = await self.mcp_client.get_context(
                service_name="sentry", request=request, context=context
            )
            return await create_agent_response(True, data=response)
        except Exception as e:
            logger.error(f"Failed to fetch Sentry issue context: {e}")
            return await create_agent_response(False, error=str(e))

    async def _trigger_seer_ai_fix(self, task: Task) -> Dict[str, Any]:
        """Trigger Sentry Seer AI to attempt an automated fix for an issue."""
        try:
            issue_id = task.task_data.get("issue_id")
            project_slug = task.task_data.get("project_slug")
            if not issue_id or not project_slug:
                return await create_agent_response(False, error="Missing issue_id or project_slug.")
            # Compose MCP tool call (example: call_seer)
            request = f"call_seer: project={project_slug}, issue={issue_id}"
            context = {"project_slug": project_slug, "issue_id": issue_id}
            response = await self.mcp_client.get_context(
                service_name="sentry", request=request, context=context
            )
            return await create_agent_response(True, data=response)
        except Exception as e:
            logger.error(f"Failed to trigger Seer AI fix: {e}")
            return await create_agent_response(False, error=str(e))

# Future: Add Agno stateful workflow support for advanced Sentry debugging and triage 