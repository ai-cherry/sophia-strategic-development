"""
Unified Sophia Service
Single entry point for all interactions with Sophia AI
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Optional

from backend.orchestration.continuous_learning_framework import (
    ContinuousLearningFramework,
    Feedback,
)
from backend.orchestration.cross_group_intelligence_hub import CrossGroupIntelligenceHub
from backend.orchestration.intelligent_meta_orchestrator import (
    IntelligentMetaOrchestrator,
)

# Placeholder for workflow designer integration
# from backend.orchestration.nl_workflow_integration import NaturalLanguageWorkflowIntegration

logger = logging.getLogger(__name__)


@dataclass
class SophiaResponse:
    """Standardized response format from Sophia"""

    content: str
    suggestions: list[str]
    metadata: dict[str, Any]
    workflow_id: str


class UnifiedSophiaService:
    """
    Single, intelligent entry point for all Sophia AI interactions.
    Integrates the meta-orchestrator, learning framework, and intelligence hub.
    """

    def __init__(self):
        self.orchestrator = IntelligentMetaOrchestrator()
        self.learning_framework = ContinuousLearningFramework()
        self.cross_group_hub = CrossGroupIntelligenceHub()
        # self.workflow_designer = NaturalLanguageWorkflowIntegration()
        self.initialized = False

    async def initialize(self):
        """Initialize all underlying components"""
        # In a real app, agent registration would happen here
        # self.orchestrator.agent_registry.register_agent(...)
        self.initialized = True
        logger.info("✅ UnifiedSophiaService initialized")

    async def process_message(
        self,
        message: str,
        user_id: str,
        session_id: str,
        context: dict[str, Any] | None = None,
    ) -> SophiaResponse:
        """
        Process a user message through the entire intelligent pipeline.
        """
        if not self.initialized:
            await self.initialize()

        # 1. Build full context for the interaction
        full_context = await self._build_full_context(user_id, session_id, context)

        # 2. Process request through the meta-orchestrator
        orchestration_result = await self.orchestrator.process_request(
            message, full_context
        )

        # 3. Learn from the interaction
        await self.learning_framework.learn_from_interaction(
            request=message,
            intent=orchestration_result["intent"],
            workflow_execution=orchestration_result[
                "result"
            ],  # This needs to be a WorkflowResult object
        )

        # 4. Format the final response
        response = await self._format_response(orchestration_result)

        return response

    async def _build_full_context(
        self, user_id: str, session_id: str, initial_context: dict[str, Any] | None
    ) -> dict[str, Any]:
        """Build a comprehensive context for the request"""
        # In a real app, this would fetch user roles, permissions, conversation history, etc.
        return {
            "user_id": user_id,
            "session_id": session_id,
            "user_role": "ceo",  # Placeholder
            "recent_messages": [],  # Placeholder
            **(initial_context or {}),
        }

    async def _format_response(self, result: dict[str, Any]) -> SophiaResponse:
        """Format the orchestration result into a user-facing response"""
        # This is a simplified formatter
        workflow_result = result.get("result", {})

        if workflow_result.get("status") == "success":
            content = f"I have successfully completed the task. Details: {workflow_result.get('details')}"
        else:
            content = (
                f"I encountered an issue. Details: {workflow_result.get('details')}"
            )

        # Generate suggestions for next steps
        recommendations = await self.learning_framework.get_recommendations(
            result["intent"].primary_category
        )

        return SophiaResponse(
            content=content,
            suggestions=recommendations,
            metadata={
                "intent": result["intent"].primary_category.value,
                "confidence": result["intent"].confidence,
                "workflow_type": result["workflow"].get("workflow_type"),
            },
            workflow_id=result["workflow"].get("id", "N/A"),
        )

    async def submit_feedback(self, workflow_id: str, feedback: Feedback):
        """Submit user feedback for a specific interaction"""
        # TODO: Implement feedback submission to the learning framework
        logger.info(f"Feedback submitted for workflow {workflow_id}: {feedback}")
        pass


# Singleton instance
_unified_service: UnifiedSophiaService | None = None


def get_unified_sophia_service() -> UnifiedSophiaService:
    """Get the singleton instance of the UnifiedSophiaService"""
    global _unified_service
    if _unified_service is None:
        _unified_service = UnifiedSophiaService()
    return _unified_service
