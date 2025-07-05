"""
UI Generation Intent Handler for Sophia AI
Automatically handles UI generation requests from the unified chat interface.
Routes to V0.dev MCP server through the orchestration service.

IMPORTANT: This is an internal service. Users interact only through the unified chat
within the unified dashboard. No direct API access or separate commands.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from backend.services.mcp_orchestration_service import (
    BusinessTask,
    TaskPriority,
    get_orchestration_service,
)

logger = logging.getLogger(__name__)


@dataclass
class UIGenerationRequest:
    """Request for UI component generation"""

    description: str
    component_type: str | None = None
    style_preferences: dict[str, Any] | None = None
    target_framework: str = "react"
    include_preview: bool = True
    user_id: str | None = None
    session_id: str | None = None


@dataclass
class UIGenerationResponse:
    """Response from UI generation"""

    success: bool
    component_code: str | None = None
    preview_url: str | None = None
    design_tokens: dict[str, Any] | None = None
    accessibility_score: float | None = None
    code_quality_score: float | None = None
    suggestions: list[str] = field(default_factory=list)
    error_message: str | None = None


class UIGenerationIntentHandler:
    """
    Handles UI generation intents from unified chat service
    Routes requests to V0.dev and orchestrates with other MCP servers
    """

    def __init__(self):
        self.orchestrator = get_orchestration_service()
        self.ui_generation_patterns = [
            "create",
            "build",
            "design",
            "generate",
            "make",
            "component",
            "interface",
            "ui",
            "ux",
            "dashboard",
            "form",
            "button",
            "modal",
            "layout",
            "page",
            "screen",
        ]

    def detect_ui_generation_intent(self, message: str) -> bool:
        """Detect if the message contains UI generation intent"""
        message_lower = message.lower()

        # Check for UI generation patterns
        ui_keywords = any(
            keyword in message_lower for keyword in self.ui_generation_patterns
        )

        # Check for specific UI requests
        ui_specific = any(
            phrase in message_lower
            for phrase in [
                "create a component",
                "build a ui",
                "design an interface",
                "generate a dashboard",
                "make a form",
                "create ui",
                "build interface",
            ]
        )

        return ui_keywords or ui_specific

    def extract_ui_requirements(self, message: str) -> UIGenerationRequest:
        """Extract UI requirements from natural language message"""
        # Simple extraction for now - can be enhanced with NLP
        component_type = None

        # Try to detect component type
        message_lower = message.lower()
        if "dashboard" in message_lower:
            component_type = "dashboard"
        elif "form" in message_lower:
            component_type = "form"
        elif "button" in message_lower:
            component_type = "button"
        elif "modal" in message_lower:
            component_type = "modal"
        elif "chart" in message_lower:
            component_type = "chart"
        elif "table" in message_lower:
            component_type = "table"
        elif "card" in message_lower:
            component_type = "card"
        elif "navigation" in message_lower or "nav" in message_lower:
            component_type = "navigation"

        # Extract style preferences
        style_preferences = {}
        if "glassmorphism" in message_lower:
            style_preferences["style"] = "glassmorphism"
        elif "minimal" in message_lower:
            style_preferences["style"] = "minimal"
        elif "modern" in message_lower:
            style_preferences["style"] = "modern"
        elif "dark" in message_lower:
            style_preferences["theme"] = "dark"

        return UIGenerationRequest(
            description=message,
            component_type=component_type,
            style_preferences=style_preferences,
        )

    async def process_ui_generation_request(
        self, request: UIGenerationRequest
    ) -> UIGenerationResponse:
        """Process UI generation request through MCP orchestration"""
        try:
            # Create business task for UI generation
            task = BusinessTask(
                task_id=f"ui_gen_{request.session_id or 'direct'}_{datetime.now().timestamp()}",
                task_type="ui_generation",
                description=request.description,
                priority=TaskPriority.MEDIUM,
                context_data={
                    "user_id": request.user_id,
                    "session_id": request.session_id,
                    "component_type": request.component_type,
                    "style_preferences": request.style_preferences,
                    "target_framework": request.target_framework,
                    "include_preview": request.include_preview,
                },
                required_capabilities=["ui_generation", "component_design"],
                requires_synthesis=True,
            )

            # Execute through orchestration service
            result = await self.orchestrator.execute_business_task(task)

            if not result.success:
                return UIGenerationResponse(
                    success=False,
                    error_message=result.error_message or "UI generation failed",
                )

            # Extract results from different servers
            v0dev_result = result.results.get("v0dev", {})
            figma_result = result.results.get("figma_context", {})
            ui_ux_result = result.results.get("ui_ux_agent", {})
            codacy_result = result.results.get("codacy", {})

            # Extract component code
            component_code = None
            if v0dev_result and "code" in v0dev_result:
                component_code = v0dev_result["code"]

            # Extract preview URL
            preview_url = None
            if v0dev_result and "preview_url" in v0dev_result:
                preview_url = v0dev_result["preview_url"]

            # Extract design tokens
            design_tokens = None
            if figma_result and "design_tokens" in figma_result:
                design_tokens = figma_result["design_tokens"]

            # Extract accessibility score
            accessibility_score = None
            if ui_ux_result and "accessibility_score" in ui_ux_result:
                accessibility_score = ui_ux_result["accessibility_score"]

            # Extract code quality score
            code_quality_score = None
            if codacy_result and "quality_score" in codacy_result:
                code_quality_score = codacy_result["quality_score"]

            # Compile suggestions
            suggestions = []
            if ui_ux_result and "suggestions" in ui_ux_result:
                suggestions.extend(ui_ux_result["suggestions"])
            if codacy_result and "suggestions" in codacy_result:
                suggestions.extend(codacy_result["suggestions"])

            return UIGenerationResponse(
                success=True,
                component_code=component_code,
                preview_url=preview_url,
                design_tokens=design_tokens,
                accessibility_score=accessibility_score,
                code_quality_score=code_quality_score,
                suggestions=suggestions,
            )

        except Exception as e:
            logger.error(f"UI generation failed: {e}")
            return UIGenerationResponse(success=False, error_message=str(e))

    async def generate_ui_from_chat(
        self,
        message: str,
        user_id: str | None = None,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Main entry point from chat service
        Returns chat-friendly response
        """
        # Extract requirements
        request = self.extract_ui_requirements(message)
        request.user_id = user_id
        request.session_id = session_id

        # Process through orchestration
        response = await self.process_ui_generation_request(request)

        # Format for chat response
        if response.success:
            chat_response = {
                "content": f"I've created the UI component based on your requirements:\n\n```tsx\n{response.component_code}\n```",
                "metadata": {
                    "type": "ui_generation",
                    "preview_url": response.preview_url,
                    "accessibility_score": response.accessibility_score,
                    "code_quality_score": response.code_quality_score,
                    "design_tokens": response.design_tokens,
                    "suggestions": response.suggestions,
                },
                "actions": [
                    {
                        "type": "preview",
                        "label": "Preview Component",
                        "url": response.preview_url,
                    },
                    {
                        "type": "deploy",
                        "label": "Deploy to Production",
                        "enabled": response.code_quality_score
                        and response.code_quality_score > 0.8,
                    },
                ],
            }
        else:
            chat_response = {
                "content": f"I encountered an issue creating the UI component: {response.error_message}. Let me know if you'd like me to try a different approach.",
                "metadata": {
                    "type": "ui_generation_error",
                    "error": response.error_message,
                },
            }

        return chat_response


# Global instance
_ui_handler = None


def get_ui_generation_handler() -> UIGenerationIntentHandler:
    """Get singleton instance of UI generation handler"""
    global _ui_handler
    if _ui_handler is None:
        _ui_handler = UIGenerationIntentHandler()
    return _ui_handler
