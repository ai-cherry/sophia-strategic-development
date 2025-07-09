#!/usr/bin/env python3
"""
Consolidate Enhanced Unified Chat Service into main Unified Chat Service.
Merges Lambda Labs cost monitoring, routing, and enhanced command handling.
"""

import shutil
from pathlib import Path


def consolidate_chat_services():
    """Merge enhanced features into main chat service"""

    # Backup original file
    main_service = Path("backend/services/unified_chat_service.py")
    enhanced_service = Path("backend/services/enhanced_unified_chat_service.py")

    backup_path = main_service.with_suffix(".py.backup")
    shutil.copy2(main_service, backup_path)
    print(f"📋 Backed up original to {backup_path}")

    # Read both files
    with open(main_service) as f:
        main_content = f.read()

    with open(enhanced_service) as f:
        enhanced_content = f.read()

    # Extract enhanced features to merge
    enhanced_imports = """
from backend.services.lambda_labs_chat_integration import LambdaLabsChatIntegration
from infrastructure.monitoring.lambda_labs_cost_monitor import LambdaLabsCostMonitor
from infrastructure.services.lambda_labs_hybrid_router import LambdaLabsHybridRouter
from collections.abc import AsyncGenerator"""

    # Enhanced __init__ additions
    enhanced_init_additions = """
        # Enhanced Lambda Labs integration
        self.lambda_integration = LambdaLabsChatIntegration()
        self.cost_monitor = LambdaLabsCostMonitor()
        self.router = LambdaLabsHybridRouter()"""

    # Enhanced process_message method
    enhanced_process_message = '''
    async def process_message(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        user_context: Optional[dict[str, Any]] = None,
    ) -> AsyncGenerator[str, None]:
        """Process message with enhanced Lambda Labs integration and streaming.

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
            # Process with unified query system
            result = await self.process_unified_query(
                query=message,
                user_id=user_context.get("user_id", "anonymous") if user_context else "anonymous",
                session_id=conversation_id or "default"
            )
            yield result["response"]
            return

        # Analyze intent for routing
        intent = await self.lambda_integration.analyze_intent(message)

        # Add routing metadata to context
        enhanced_context = user_context or {}
        enhanced_context.update({
            "intent": intent["intent"],
            "recommended_backend": intent["recommended_backend"],
            "recommended_model": intent["recommended_model"],
        })

        # Process with Lambda Labs
        try:
            result = await self.lambda_integration.process_chat_message(
                message=message,
                conversation_history=await self._get_conversation_history(conversation_id),
                user_context=enhanced_context,
            )

            if result["success"]:
                # Stream the response
                response = result["response"]
                for i in range(0, len(response), 50):  # Chunk for streaming
                    yield response[i : i + 50]
                    await asyncio.sleep(0.01)  # Small delay for streaming effect

                # Add usage metadata
                yield f"\\n\\n---\\n📊 Model: {result.get('model')} | Backend: {result.get('backend')}"
            else:
                # Fallback to unified query processing
                yield f"Error: {result.get('error')}\\n"
                unified_result = await self.process_unified_query(
                    query=message,
                    user_id=enhanced_context.get("user_id", "anonymous"),
                    session_id=conversation_id or "default"
                )
                yield unified_result["response"]

        except Exception as e:
            logger.error(f"Lambda Labs integration error: {e}")
            # Fallback to unified query processing
            unified_result = await self.process_unified_query(
                query=message,
                user_id=enhanced_context.get("user_id", "anonymous"),
                session_id=conversation_id or "default"
            )
            yield unified_result["response"]'''

    # Enhanced Lambda command methods
    enhanced_lambda_methods = '''
    async def _is_lambda_command(self, message: str) -> bool:
        """Check if message is a Lambda-specific command."""
        lambda_keywords = [
            "lambda cost", "lambda usage", "serverless cost", "estimate cost",
            "optimize cost", "lambda budget", "lambda stats",
        ]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in lambda_keywords)

    async def _handle_lambda_command(
        self,
        message: str,
        user_context: Optional[dict[str, Any]] = None,
    ) -> AsyncGenerator[str, None]:
        """Handle Lambda-specific commands."""
        message_lower = message.lower()

        # Cost estimation
        if "estimate cost" in message_lower:
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
                "llama-4-maverick-17b-128e-instruct-fp8": (estimated_tokens / 1_000_000) * 0.88,
            }

            yield "💰 **Cost Estimation**\\n\\n"
            yield f"Estimated tokens: {estimated_tokens:,}\\n\\n"
            for model, cost in costs.items():
                yield f"- **{model}**: ${cost:.4f}\\n"

        # Usage statistics
        elif "lambda usage" in message_lower or "lambda stats" in message_lower:
            stats = self.router.serverless.get_usage_stats(days=7)
            budget_status = await self.cost_monitor.check_and_alert()

            yield "📊 **Lambda Labs Usage Report (7 days)**\\n\\n"
            yield "**Budget Status:**\\n"
            yield f"- Daily: ${budget_status['daily']:.2f} / ${budget_status['daily_budget']:.2f} "
            yield f"({budget_status['daily_percentage']:.1f}%)\\n"
            yield f"- Monthly: ${budget_status['monthly']:.2f} / ${budget_status['monthly_budget']:.2f} "
            yield f"({budget_status['monthly_percentage']:.1f}%)\\n\\n"

            yield "**Model Usage:**\\n"
            for model, model_stats in stats.get("model_stats", {}).items():
                yield f"\\n**{model}:**\\n"
                yield f"- Requests: {model_stats['requests']:,}\\n"
                yield f"- Tokens: {model_stats['tokens']:,}\\n"
                yield f"- Cost: ${model_stats['cost']:.2f}\\n"
                yield f"- Avg latency: {model_stats['avg_latency_ms']:.0f}ms\\n"

        # Cost optimization
        elif "optimize cost" in message_lower:
            remaining = message.replace("optimize cost", "").strip()
            yield "🎯 **Cost Optimization Analysis**\\n\\n"

            if not remaining:
                yield "Please describe your workload for optimization recommendations."
                return

            is_simple = any(kw in remaining.lower() for kw in ["simple", "basic", "quick"])
            is_complex = any(kw in remaining.lower() for kw in ["complex", "detailed", "analysis"])

            if is_simple:
                yield "**Recommendation**: Use `llama3.1-8b-instruct`\\n"
                yield "- Cost: $0.07/1M tokens (80% savings vs default)\\n"
                yield "- Suitable for: Simple queries, summaries, basic tasks\\n"
            elif is_complex:
                yield "**Recommendation**: Use `llama-4-maverick-17b-128e-instruct-fp8`\\n"
                yield "- Cost: $0.88/1M tokens\\n"
                yield "- Suitable for: Complex analysis, detailed reasoning\\n"
            else:
                yield "**Recommendation**: Use `llama3.1-70b-instruct-fp8` (default)\\n"
                yield "- Cost: $0.35/1M tokens\\n"
                yield "- Suitable for: Balanced performance and cost\\n"

            yield "\\n**Additional Tips:**\\n"
            yield "- Batch similar requests together\\n"
            yield "- Cache frequently used completions\\n"
            yield "- Use smaller models for simple tasks\\n"
            yield "- Schedule non-urgent tasks for off-peak\\n"

        else:
            yield "Unknown Lambda command. Available commands:\\n"
            yield "- `estimate cost [prompt]` - Estimate cost for a prompt\\n"
            yield "- `lambda usage` or `lambda stats` - Show usage statistics\\n"
            yield "- `optimize cost [workload description]` - Get optimization tips\\n"

    async def _get_conversation_history(
        self,
        conversation_id: Optional[str],
    ) -> list[dict[str, str]]:
        """Get conversation history."""
        if conversation_id:
            return await self.ai_memory.get_session_history(conversation_id)
        return []'''

    # Start building the consolidated content
    consolidated_content = main_content

    # 1. Add enhanced imports after existing imports
    import_insert_pos = consolidated_content.find(
        "logger = logging.getLogger(__name__)"
    )
    if import_insert_pos != -1:
        insert_pos = consolidated_content.rfind("\n", 0, import_insert_pos) + 1
        consolidated_content = (
            consolidated_content[:insert_pos]
            + enhanced_imports
            + "\n\n"
            + consolidated_content[insert_pos:]
        )

    # 2. Add enhanced initialization to __init__ method
    init_method_pos = consolidated_content.find(
        "self.workflow = self._build_orchestration_workflow()"
    )
    if init_method_pos != -1:
        insert_pos = consolidated_content.find("\n", init_method_pos) + 1
        consolidated_content = (
            consolidated_content[:insert_pos]
            + enhanced_init_additions
            + "\n"
            + consolidated_content[insert_pos:]
        )

    # 3. Add the enhanced process_message method before process_unified_query
    unified_query_pos = consolidated_content.find("async def process_unified_query(")
    if unified_query_pos != -1:
        # Find the start of the method (beginning of line)
        insert_pos = consolidated_content.rfind("\n", 0, unified_query_pos) + 1
        consolidated_content = (
            consolidated_content[:insert_pos]
            + enhanced_process_message
            + "\n\n    "
            + consolidated_content[insert_pos:]
        )

    # 4. Add Lambda command methods at the end of the class
    last_method_pos = consolidated_content.rfind("async def natural_language_control(")
    if last_method_pos != -1:
        # Find the end of this method
        method_end = consolidated_content.find("\n        ", last_method_pos)
        if method_end == -1:
            method_end = len(consolidated_content)

        # Find the end of the method by looking for the next method or class end
        method_lines = consolidated_content[last_method_pos:].split("\n")
        end_line_idx = 1
        for i, line in enumerate(method_lines[1:], 1):
            if line and not line.startswith(" ") and not line.startswith("\t"):
                end_line_idx = i
                break

        # Insert at the end of the class
        consolidated_content = consolidated_content + "\n" + enhanced_lambda_methods

    # Write the consolidated file
    with open(main_service, "w") as f:
        f.write(consolidated_content)

    print(f"✅ Consolidated enhanced features into {main_service}")
    print("📁 Enhanced service can now be safely removed")

    return True


def clean_up_enhanced_service():
    """Remove the enhanced service file after successful consolidation"""
    enhanced_service = Path("backend/services/enhanced_unified_chat_service.py")

    if enhanced_service.exists():
        # Move to archive instead of deleting
        archive_dir = Path("archive/unified_chat_duplicates")
        archive_dir.mkdir(parents=True, exist_ok=True)

        archive_path = archive_dir / "enhanced_unified_chat_service.py.archived"
        shutil.move(enhanced_service, archive_path)
        print(f"📦 Archived enhanced service to {archive_path}")


def main():
    """Main consolidation function"""
    print("🔄 Consolidating Enhanced Unified Chat Service...")

    try:
        success = consolidate_chat_services()

        if success:
            print("✅ Chat service consolidation successful!")

            # Ask for cleanup
            print("\n🧹 Cleaning up duplicate files...")
            clean_up_enhanced_service()

            print("\n📋 Consolidation Summary:")
            print("✅ Enhanced Lambda Labs integration merged")
            print("✅ Cost monitoring and routing added")
            print("✅ Streaming message processing added")
            print("✅ Lambda command handling integrated")
            print("✅ Conversation history integration added")
            print("✅ Duplicate file archived")

            print("\n🧪 Next steps:")
            print("1. Test the consolidated chat service")
            print("2. Verify Lambda Labs integration works")
            print("3. Test streaming responses")

        else:
            print("❌ Consolidation failed - manual review needed")

    except Exception as e:
        print(f"❌ Error during consolidation: {e}")
        print("Manual consolidation may be required")


if __name__ == "__main__":
    main()
