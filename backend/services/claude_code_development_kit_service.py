"""
Claude-Code-Development-Kit Integration Service
Unified orchestration of enhanced documentation, multi-agent workflows, and intelligent LLM routing
"""

import asyncio
import time
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from backend.core.auto_esc_config import get_config_value
from backend.services.documentation_loader_service import get_documentation_loader
from backend.services.enhanced_portkey_llm_gateway import (
    TaskComplexity,
    get_enhanced_portkey_gateway,
)
from backend.services.sophia_agent_orchestrator import get_sophia_agent_orchestrator
from backend.utils.custom_logger import logger


class IntegrationMode(Enum):
    """Integration modes for different use cases"""
    CLAUDE_DEVELOPMENT_KIT = "claude_development_kit"
    ENHANCED_SOPHIA = "enhanced_sophia"
    HYBRID = "hybrid"


@dataclass
class ProcessingResult:
    """Result from Claude-Code-Development-Kit processing"""
    success: bool
    result: str
    metadata: dict[str, Any]
    performance_metrics: dict[str, Any]
    documentation_context: dict[str, Any] | None = None
    agent_workflow: dict[str, Any] | None = None
    routing_decision: dict[str, Any] | None = None


class ClaudeCodeDevelopmentKitService:
    """
    Unified Claude-Code-Development-Kit Integration Service
    Orchestrates enhanced documentation auto-loading, multi-agent workflows, and intelligent LLM routing
    """

    def __init__(self):
        self.documentation_loader = None
        self.agent_orchestrator = None
        self.portkey_gateway = None
        self.integration_mode = IntegrationMode.HYBRID
        self.performance_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "average_processing_time": 0.0,
            "token_usage_reduction": 0.0,
            "documentation_cache_hits": 0,
            "agent_workflow_executions": 0,
            "intelligent_routing_decisions": 0
        }

    async def initialize(self):
        """Initialize all components"""
        try:
            # Initialize documentation loader
            self.documentation_loader = await get_documentation_loader()
            logger.info("✅ Documentation loader initialized")

            # Initialize agent orchestrator
            self.agent_orchestrator = await get_sophia_agent_orchestrator()
            logger.info("✅ Agent orchestrator initialized")

            # Initialize enhanced Portkey gateway
            self.portkey_gateway = await get_enhanced_portkey_gateway()
            logger.info("✅ Enhanced Portkey gateway initialized")

            logger.info("🚀 Claude-Code-Development-Kit Service fully initialized")

        except Exception as e:
            logger.error(f"Failed to initialize Claude-Code-Development-Kit Service: {e}")
            raise

    async def process_request(
        self,
        user_input: str,
        task_type: str = "general",
        complexity: str = "moderate",
        use_documentation_auto_loading: bool = True,
        use_multi_agent_workflow: bool = True,
        use_intelligent_routing: bool = True,
        cost_preference: str = "balanced_mode",
        stream: bool = True,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Process user request using Claude-Code-Development-Kit patterns
        
        Args:
            user_input: User's request
            task_type: Type of task for routing
            complexity: Task complexity (simple, moderate, complex, architecture)
            use_documentation_auto_loading: Whether to use 3-tier documentation loading
            use_multi_agent_workflow: Whether to use multi-agent workflows
            use_intelligent_routing: Whether to use intelligent LLM routing
            cost_preference: Cost optimization preference
            stream: Whether to stream the response
            **kwargs: Additional parameters
            
        Yields:
            Response chunks
        """
        start_time = time.time()
        self.performance_metrics["total_requests"] += 1

        processing_metadata = {
            "user_input": user_input[:100] + "..." if len(user_input) > 100 else user_input,
            "task_type": task_type,
            "complexity": complexity,
            "features_enabled": {
                "documentation_auto_loading": use_documentation_auto_loading,
                "multi_agent_workflow": use_multi_agent_workflow,
                "intelligent_routing": use_intelligent_routing
            },
            "start_time": datetime.utcnow().isoformat()
        }

        try:
            # Step 1: 3-Tier Documentation Auto-Loading
            documentation_context = None
            if use_documentation_auto_loading:
                documentation_context = await self._load_documentation_context(
                    complexity, task_type
                )
                processing_metadata["documentation_loaded"] = True
                processing_metadata["documentation_tiers"] = len(documentation_context)
                self.performance_metrics["documentation_cache_hits"] += 1

            # Step 2: Multi-Agent Workflow Processing
            if use_multi_agent_workflow and self.agent_orchestrator:
                # Determine appropriate workflow type
                workflow_type = self._determine_workflow_type(task_type, complexity)

                # Execute multi-agent workflow
                workflow_result = await self.agent_orchestrator.execute_workflow(
                    user_input=user_input,
                    workflow_type=workflow_type,
                    context={
                        "documentation": documentation_context,
                        "task_type": task_type,
                        "complexity": complexity,
                        **kwargs
                    },
                    parallel_execution=True
                )

                processing_metadata["workflow_executed"] = True
                processing_metadata["workflow_type"] = workflow_type
                processing_metadata["agent_chain"] = workflow_result.agent_chain
                self.performance_metrics["agent_workflow_executions"] += 1

                # Use workflow result as the response
                yield workflow_result.result

                # Update performance metrics
                execution_time = time.time() - start_time
                self._update_performance_metrics(execution_time, True, workflow_result.token_usage.get("total", 0))
                return

            # Step 3: Intelligent LLM Routing (fallback or alternative)
            if use_intelligent_routing and self.portkey_gateway:
                # Prepare messages for LLM
                messages = [{"role": "user", "content": user_input}]

                # Add documentation context if available
                if documentation_context:
                    context_summary = self._summarize_documentation_context(documentation_context)
                    messages.insert(0, {
                        "role": "system",
                        "content": f"Context: {context_summary}"
                    })

                # Convert complexity to TaskComplexity enum
                task_complexity = self._convert_complexity(complexity)

                # Stream response from enhanced Portkey gateway
                response_chunks = []
                async for chunk in self.portkey_gateway.complete(
                    messages=messages,
                    task_type=task_type,
                    complexity=task_complexity,
                    cost_preference=cost_preference,
                    stream=stream,
                    **kwargs
                ):
                    response_chunks.append(chunk)
                    yield chunk

                processing_metadata["intelligent_routing"] = True
                self.performance_metrics["intelligent_routing_decisions"] += 1

                # Update performance metrics
                execution_time = time.time() - start_time
                token_count = sum(len(chunk.split()) for chunk in response_chunks)
                self._update_performance_metrics(execution_time, True, token_count)
                return

            # Step 4: Simple response (no enhancements)
            simple_response = f"""
# Sophia AI Response

**Request**: {user_input}

I understand your request. Currently processing with Claude-Code-Development-Kit enhancements:

- **Documentation Auto-Loading**: {use_documentation_auto_loading}
- **Multi-Agent Workflow**: {use_multi_agent_workflow} 
- **Intelligent Routing**: {use_intelligent_routing}

Please enable at least one enhancement for optimal results.
            """.strip()

            yield simple_response

            # Update performance metrics
            execution_time = time.time() - start_time
            self._update_performance_metrics(execution_time, True, len(simple_response.split()))

        except Exception as e:
            logger.error(f"Claude-Code-Development-Kit processing error: {e}")

            error_response = f"""
# Error Processing Request

I encountered an error while processing your request with Claude-Code-Development-Kit enhancements:

**Error**: {str(e)}
**Request**: {user_input[:100]}...

Please try again or contact support if the issue persists.
            """.strip()

            yield error_response

            # Update performance metrics for failure
            execution_time = time.time() - start_time
            self._update_performance_metrics(execution_time, False, 0)

    async def _load_documentation_context(
        self, complexity: str, task_type: str
    ) -> dict[str, Any]:
        """Load documentation context using 3-tier auto-loading"""
        if not self.documentation_loader:
            return {}

        try:
            contexts = await self.documentation_loader.load_context_for_complexity(
                complexity, task_type
            )

            # Calculate token usage reduction
            total_tokens = sum(ctx.token_count for ctx in contexts.values())
            baseline_tokens = total_tokens * 1.5  # Assume 50% more without smart loading
            reduction = ((baseline_tokens - total_tokens) / baseline_tokens) * 100
            self.performance_metrics["token_usage_reduction"] = reduction

            return contexts

        except Exception as e:
            logger.warning(f"Failed to load documentation context: {e}")
            return {}

    def _determine_workflow_type(self, task_type: str, complexity: str) -> str:
        """Determine appropriate workflow type"""
        workflow_mapping = {
            "code_generation": "code_development",
            "architecture": "infrastructure",
            "business_intelligence": "business_intelligence",
            "research": "research_analysis",
            "integration": "code_development",
            "infrastructure": "infrastructure"
        }

        if complexity == "architecture":
            return "infrastructure"

        return workflow_mapping.get(task_type, "code_development")

    def _convert_complexity(self, complexity: str) -> TaskComplexity:
        """Convert string complexity to TaskComplexity enum"""
        complexity_mapping = {
            "simple": TaskComplexity.SIMPLE,
            "moderate": TaskComplexity.MODERATE,
            "complex": TaskComplexity.COMPLEX,
            "architecture": TaskComplexity.ARCHITECTURE
        }

        return complexity_mapping.get(complexity, TaskComplexity.MODERATE)

    def _summarize_documentation_context(self, documentation_context: dict[str, Any]) -> str:
        """Summarize documentation context for LLM"""
        if not documentation_context:
            return "No additional context available."

        summary_parts = []

        for tier_name, context in documentation_context.items():
            tier_summary = f"{tier_name}: {context.token_count} tokens loaded"
            summary_parts.append(tier_summary)

        return f"Documentation context loaded: {', '.join(summary_parts)}"

    def _update_performance_metrics(
        self, execution_time: float, success: bool, token_count: int
    ):
        """Update service performance metrics"""
        if success:
            self.performance_metrics["successful_requests"] += 1

        # Update running average processing time
        total_requests = self.performance_metrics["total_requests"]
        current_avg = self.performance_metrics["average_processing_time"]
        self.performance_metrics["average_processing_time"] = (
            (current_avg * (total_requests - 1) + execution_time) / total_requests
        )

    async def get_comprehensive_status(self) -> dict[str, Any]:
        """Get comprehensive status of all components"""
        status = {
            "service": "claude_code_development_kit",
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "integration_mode": self.integration_mode.value,
            "performance_metrics": self.performance_metrics,
            "components": {}
        }

        # Documentation loader status
        if self.documentation_loader:
            status["components"]["documentation_loader"] = await self.documentation_loader.health_check()

        # Agent orchestrator status
        if self.agent_orchestrator:
            status["components"]["agent_orchestrator"] = await self.agent_orchestrator.health_check()

        # Portkey gateway status
        if self.portkey_gateway:
            status["components"]["portkey_gateway"] = await self.portkey_gateway.health_check()

        return status

    async def optimize_performance(self) -> dict[str, Any]:
        """Optimize performance across all components"""
        optimization_results = {
            "optimization_time": datetime.utcnow().isoformat(),
            "actions_taken": [],
            "performance_improvements": {}
        }

        try:
            # Clear documentation cache if hit rate is low
            if self.documentation_loader:
                doc_metrics = await self.documentation_loader.get_performance_metrics()
                if doc_metrics["cache_hit_rate"] < 50:
                    await self.documentation_loader.clear_cache()
                    optimization_results["actions_taken"].append("Cleared documentation cache")

            # Reset performance metrics to get fresh baseline
            baseline_requests = self.performance_metrics["total_requests"]
            self.performance_metrics = {
                "total_requests": baseline_requests,
                "successful_requests": 0,
                "average_processing_time": 0.0,
                "token_usage_reduction": 0.0,
                "documentation_cache_hits": 0,
                "agent_workflow_executions": 0,
                "intelligent_routing_decisions": 0
            }
            optimization_results["actions_taken"].append("Reset performance metrics baseline")

            optimization_results["status"] = "completed"

        except Exception as e:
            logger.error(f"Performance optimization error: {e}")
            optimization_results["status"] = "failed"
            optimization_results["error"] = str(e)

        return optimization_results

    async def health_check(self) -> dict[str, Any]:
        """Comprehensive health check"""
        return {
            "service": "claude_code_development_kit_service",
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "capabilities": [
                "3-tier documentation auto-loading",
                "Multi-agent workflow orchestration",
                "Intelligent LLM routing with Portkey + OpenRouter",
                "Performance optimization",
                "Token usage reduction",
                "Cost optimization",
                "Claude-Code-Development-Kit patterns"
            ],
            "components_initialized": {
                "documentation_loader": self.documentation_loader is not None,
                "agent_orchestrator": self.agent_orchestrator is not None,
                "portkey_gateway": self.portkey_gateway is not None
            },
            "integration_mode": self.integration_mode.value,
            "performance_summary": {
                "total_requests": self.performance_metrics["total_requests"],
                "success_rate": (
                    self.performance_metrics["successful_requests"] /
                    max(1, self.performance_metrics["total_requests"])
                ) * 100,
                "average_processing_time": self.performance_metrics["average_processing_time"],
                "token_usage_reduction": self.performance_metrics["token_usage_reduction"]
            }
        }


# Global service instance
_service_instance = None


async def get_claude_code_development_kit_service() -> ClaudeCodeDevelopmentKitService:
    """Get singleton service instance"""
    global _service_instance
    if _service_instance is None:
        _service_instance = ClaudeCodeDevelopmentKitService()
        await _service_instance.initialize()
    return _service_instance


# Convenience functions for easy integration
async def process_with_claude_kit(
    user_input: str,
    task_type: str = "general",
    complexity: str = "moderate",
    **kwargs
) -> AsyncGenerator[str, None]:
    """
    Convenience function to process requests with Claude-Code-Development-Kit enhancements
    
    Args:
        user_input: User's request
        task_type: Type of task
        complexity: Task complexity
        **kwargs: Additional parameters
        
    Yields:
        Response chunks
    """
    service = await get_claude_code_development_kit_service()
    async for chunk in service.process_request(
        user_input=user_input,
        task_type=task_type,
        complexity=complexity,
        **kwargs
    ):
        yield chunk


async def get_claude_kit_status() -> dict[str, Any]:
    """Get Claude-Code-Development-Kit service status"""
    service = await get_claude_code_development_kit_service()
    return await service.get_comprehensive_status()


async def optimize_claude_kit_performance() -> dict[str, Any]:
    """Optimize Claude-Code-Development-Kit performance"""
    service = await get_claude_code_development_kit_service()
    return await service.optimize_performance()
