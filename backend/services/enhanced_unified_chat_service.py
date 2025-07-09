"""Enhanced Unified Chat Service with Lambda Labs Integration."""

import asyncio
import logging
from collections.abc import AsyncGenerator
from typing import Any, Optional

from backend.services.lambda_labs_chat_integration import LambdaLabsChatIntegration
from backend.services.unified_chat_service import UnifiedChatService
from infrastructure.monitoring.lambda_labs_cost_monitor import LambdaLabsCostMonitor
from infrastructure.services.lambda_labs_hybrid_router import LambdaLabsHybridRouter

logger = logging.getLogger(__name__)


class EnhancedUnifiedChatService(UnifiedChatService):
    """Enhanced chat service with Lambda Labs serverless integration.

    This service extends the base unified chat with:
    - Lambda Labs serverless inference
    - Cost optimization routing
    - Usage monitoring and alerts
    - Natural language infrastructure control
    """

    def __init__(self):
        """Initialize enhanced chat service."""
        super().__init__()
        self.lambda_integration = LambdaLabsChatIntegration()
        self.cost_monitor = LambdaLabsCostMonitor()
        self.router = LambdaLabsHybridRouter()

    async def process_message(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        user_context: Optional[dict[str, Any]] = None,
    ) -> AsyncGenerator[str, None]:
        """Process message with Lambda Labs integration.

        Args:
            message: User's message
            conversation_id: Optional conversation ID
            user_context: Optional user context

        Yields:
            Response chunks for streaming
        """
        # Check for Lambda-specific commands
        if await self._is_lambda_command(message):
            async for chunk in self._handle_lambda_command(message, user_context):
                yield chunk
            return

        # Check budget before processing
        if not self.cost_monitor.is_within_budget():
            yield "⚠️ Lambda Labs budget exceeded. Using fallback model."
            # Fall back to base implementation
            async for chunk in super().process_message(
                message, conversation_id, user_context
            ):
                yield chunk
            return

        # Analyze intent for routing
        intent = await self.lambda_integration.analyze_intent(message)

        # Add routing metadata to context
        enhanced_context = user_context or {}
        enhanced_context.update(
            {
                "intent": intent["intent"],
                "recommended_backend": intent["recommended_backend"],
                "recommended_model": intent["recommended_model"],
            }
        )

        # Process with Lambda Labs
        try:
            result = await self.lambda_integration.process_chat_message(
                message=message,
                conversation_history=await self._get_conversation_history(
                    conversation_id
                ),
                user_context=enhanced_context,
            )

            if result["success"]:
                # Stream the response
                response = result["response"]
                for i in range(0, len(response), 50):  # Chunk for streaming
                    yield response[i : i + 50]
                    await asyncio.sleep(0.01)  # Small delay for streaming effect

                # Add usage metadata
                yield f"\n\n---\n📊 Model: {result.get('model')} | Backend: {result.get('backend')}"
            else:
                # Fallback on error
                yield f"Error: {result.get('error')}"
                async for chunk in super().process_message(
                    message, conversation_id, user_context
                ):
                    yield chunk

        except Exception as e:
            logger.error(f"Lambda Labs integration error: {e}")
            # Fallback to base implementation
            async for chunk in super().process_message(
                message, conversation_id, user_context
            ):
                yield chunk

    async def _is_lambda_command(self, message: str) -> bool:
        """Check if message is a Lambda-specific command.

        Args:
            message: User's message

        Returns:
            True if Lambda command
        """
        lambda_keywords = [
            "lambda cost",
            "lambda usage",
            "serverless cost",
            "estimate cost",
            "optimize cost",
            "lambda budget",
            "lambda stats",
        ]

        message_lower = message.lower()
        return any(keyword in message_lower for keyword in lambda_keywords)

    async def _handle_lambda_command(
        self,
        message: str,
        user_context: Optional[dict[str, Any]] = None,
    ) -> AsyncGenerator[str, None]:
        """Handle Lambda-specific commands.

        Args:
            message: User's message
            user_context: Optional user context

        Yields:
            Response chunks
        """
        message_lower = message.lower()

        # Cost estimation
        if "estimate cost" in message_lower:
            # Extract prompt from message
            prompt = message.replace("estimate cost", "").strip()
            if not prompt:
                yield "Please provide a prompt to estimate cost for."
                return

            # Estimate tokens (rough approximation)
            estimated_tokens = len(prompt) // 4 + 500

            # Calculate costs for different models
            costs = {
                "llama3.1-8b-instruct": (estimated_tokens / 1_000_000) * 0.07,
                "llama3.1-70b-instruct-fp8": (estimated_tokens / 1_000_000) * 0.35,
                "llama-4-maverick-17b-128e-instruct-fp8": (estimated_tokens / 1_000_000)
                * 0.88,
            }

            yield "💰 **Cost Estimation**\n\n"
            yield f"Estimated tokens: {estimated_tokens:,}\n\n"
            for model, cost in costs.items():
                yield f"- **{model}**: ${cost:.4f}\n"

        # Usage statistics
        elif "lambda usage" in message_lower or "lambda stats" in message_lower:
            # Get usage stats
            stats = self.router.serverless.get_usage_stats(days=7)
            budget_status = await self.cost_monitor.check_and_alert()

            yield "📊 **Lambda Labs Usage Report (7 days)**\n\n"

            # Budget status
            yield "**Budget Status:**\n"
            yield f"- Daily: ${budget_status['daily']:.2f} / ${budget_status['daily_budget']:.2f} "
            yield f"({budget_status['daily_percentage']:.1f}%)\n"
            yield f"- Monthly: ${budget_status['monthly']:.2f} / ${budget_status['monthly_budget']:.2f} "
            yield f"({budget_status['monthly_percentage']:.1f}%)\n\n"

            # Model usage
            yield "**Model Usage:**\n"
            for model, model_stats in stats.get("model_stats", {}).items():
                yield f"\n**{model}:**\n"
                yield f"- Requests: {model_stats['requests']:,}\n"
                yield f"- Tokens: {model_stats['tokens']:,}\n"
                yield f"- Cost: ${model_stats['cost']:.2f}\n"
                yield f"- Avg latency: {model_stats['avg_latency_ms']:.0f}ms\n"

        # Cost optimization
        elif "optimize cost" in message_lower:
            # Get optimization recommendations
            remaining = message.replace("optimize cost", "").strip()

            yield "🎯 **Cost Optimization Analysis**\n\n"

            if not remaining:
                yield "Please describe your workload for optimization recommendations."
                return

            # Analyze workload
            is_simple = any(
                kw in remaining.lower() for kw in ["simple", "basic", "quick"]
            )
            is_complex = any(
                kw in remaining.lower() for kw in ["complex", "detailed", "analysis"]
            )

            if is_simple:
                yield "**Recommendation**: Use `llama3.1-8b-instruct`\n"
                yield "- Cost: $0.07/1M tokens (80% savings vs default)\n"
                yield "- Suitable for: Simple queries, summaries, basic tasks\n"
            elif is_complex:
                yield "**Recommendation**: Use `llama-4-maverick-17b-128e-instruct-fp8`\n"
                yield "- Cost: $0.88/1M tokens\n"
                yield "- Suitable for: Complex analysis, detailed reasoning\n"
            else:
                yield "**Recommendation**: Use `llama3.1-70b-instruct-fp8` (default)\n"
                yield "- Cost: $0.35/1M tokens\n"
                yield "- Suitable for: Balanced performance and cost\n"

            yield "\n**Additional Tips:**\n"
            yield "- Batch similar requests together\n"
            yield "- Cache frequently used completions\n"
            yield "- Use smaller models for simple tasks\n"
            yield "- Schedule non-urgent tasks for off-peak\n"

        else:
            yield "Unknown Lambda command. Available commands:\n"
            yield "- `estimate cost [prompt]` - Estimate cost for a prompt\n"
            yield "- `lambda usage` or `lambda stats` - Show usage statistics\n"
            yield "- `optimize cost [workload description]` - Get optimization tips\n"

    async def _get_conversation_history(
        self,
        conversation_id: Optional[str],
    ) -> list[dict[str, str]]:
        """Get conversation history.

        Args:
            conversation_id: Optional conversation ID

        Returns:
            List of previous messages
        """
        # TODO: Implement conversation history retrieval
        return []
