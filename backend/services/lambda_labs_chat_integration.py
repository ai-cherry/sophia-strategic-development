"""Integration of Lambda Labs with Sophia AI unified chat service."""

import logging
from typing import Any, Optional

from infrastructure.services.lambda_labs_hybrid_router import LambdaLabsHybridRouter

logger = logging.getLogger(__name__)


class LambdaLabsChatIntegration:
    """Integrates Lambda Labs inference with Sophia AI chat.

    This class provides seamless integration between Lambda Labs
    serverless/GPU inference and Sophia AI's unified chat interface,
    enabling natural language control of infrastructure.

    Attributes:
        router: Lambda Labs hybrid router instance
        default_model: Default model for chat completions
    """

    def __init__(self, default_model: str = "llama3.1-70b-instruct-fp8"):
        """Initialize chat integration.

        Args:
            default_model: Default model to use for completions
        """
        self.router = LambdaLabsHybridRouter()
        self.default_model = default_model

    async def process_chat_message(
        self,
        message: str,
        conversation_history: Optional[list[dict[str, str]]] = None,
        user_context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Process a chat message through Lambda Labs.

        Args:
            message: User's message
            conversation_history: Previous messages in conversation
            user_context: Additional context (user_id, session_id, etc.)

        Returns:
            Response dictionary with completion and metadata
        """
        # Build messages list
        messages = []

        # Add system prompt
        messages.append(
            {
                "role": "system",
                "content": "You are Sophia AI, an intelligent business assistant. Provide helpful, accurate, and concise responses.",
            }
        )

        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history[-10:])  # Last 10 messages

        # Add current message
        messages.append({"role": "user", "content": message})

        # Determine cost priority from context
        cost_priority = "balanced"
        if user_context:
            # CEO gets performance priority
            if user_context.get("user_role") == "CEO":
                cost_priority = "performance"
            # Bulk operations get cost priority
            elif user_context.get("operation_type") == "bulk":
                cost_priority = "low_cost"

        # Generate response
        try:
            result = await self.router.generate(
                messages=messages,
                model=self.default_model,
                cost_priority=cost_priority,
                max_tokens=1000,
                user_id=user_context.get("user_id") if user_context else None,
                session_id=user_context.get("session_id") if user_context else None,
            )

            # Extract completion
            completion = (
                result.get("choices", [{}])[0].get("message", {}).get("content", "")
            )

            # Build response
            return {
                "success": True,
                "response": completion,
                "model": result.get("model", self.default_model),
                "backend": result.get("backend", "unknown"),
                "usage": result.get("usage", {}),
                "metadata": {
                    "cost_priority": cost_priority,
                    "conversation_length": len(messages),
                },
            }

        except Exception as e:
            logger.error(f"Lambda Labs chat integration error: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "I apologize, but I'm having trouble processing your request. Please try again.",
            }

    async def analyze_intent(self, message: str) -> dict[str, Any]:
        """Analyze user intent for routing decisions.

        Args:
            message: User's message

        Returns:
            Intent analysis with routing recommendations
        """
        # Simple keyword-based intent detection
        message_lower = message.lower()

        # Infrastructure commands
        if any(
            kw in message_lower for kw in ["deploy", "scale", "provision", "lambda"]
        ):
            return {
                "intent": "infrastructure_control",
                "confidence": 0.9,
                "recommended_backend": "gpu",  # Low latency for ops
                "recommended_model": "llama3.1-70b-instruct-fp8",
            }

        # Analytics queries
        elif any(
            kw in message_lower for kw in ["analyze", "report", "statistics", "metrics"]
        ):
            return {
                "intent": "analytics",
                "confidence": 0.8,
                "recommended_backend": "serverless",
                "recommended_model": "llama3.1-70b-instruct-fp8",
            }

        # Simple queries
        elif len(message.split()) < 10:
            return {
                "intent": "simple_query",
                "confidence": 0.7,
                "recommended_backend": "serverless",
                "recommended_model": "llama3.1-8b-instruct",
            }

        # Complex analysis
        else:
            return {
                "intent": "complex_analysis",
                "confidence": 0.6,
                "recommended_backend": "gpu",
                "recommended_model": "llama-4-maverick-17b-128e-instruct-fp8",
            }
