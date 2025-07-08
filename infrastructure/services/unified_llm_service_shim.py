"""
Unified LLM Service - Backward Compatibility Shim
Redirects all calls to the new LLM Router while maintaining API compatibility
"""

import warnings
from collections.abc import AsyncGenerator
from typing import Any

from infrastructure.services.llm_router import TaskComplexity, TaskType, llm_router

# Warn about deprecation
warnings.warn(
    "unified_llm_service is deprecated. Use llm_router directly from infrastructure.services.llm_router",
    DeprecationWarning,
    stacklevel=2,
)


class UnifiedLLMService:
    """
    Backward compatibility wrapper for UnifiedLLMService
    All methods delegate to the new LLM Router
    """

    def __init__(self):
        self.initialized = True  # Always initialized

    async def initialize(self):
        """No-op for compatibility"""
        pass

    async def complete(
        self,
        prompt: str,
        task_type: TaskType,
        stream: bool = True,
        metadata: dict | None = None,
        model_override: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> AsyncGenerator[str, None]:
        """
        Delegate to LLM Router with appropriate complexity mapping
        """
        # Map task type to complexity (simplified)
        complexity_map = {
            TaskType.ARCHITECTURE_DESIGN: TaskComplexity.ARCHITECTURE,
            TaskType.CODE_GENERATION: TaskComplexity.COMPLEX,
            TaskType.CODE_ANALYSIS: TaskComplexity.COMPLEX,
            TaskType.BUSINESS_INTELLIGENCE: TaskComplexity.COMPLEX,
            TaskType.DATA_ANALYSIS: TaskComplexity.MODERATE,
            TaskType.DOCUMENT_SUMMARY: TaskComplexity.MODERATE,
            TaskType.CHAT_CONVERSATION: TaskComplexity.SIMPLE,
        }

        complexity = complexity_map.get(task_type, TaskComplexity.MODERATE)

        # Delegate to router
        async for chunk in llm_router.complete(
            prompt=prompt,
            task=task_type,
            complexity=complexity,
            stream=stream,
            temperature=temperature,
            max_tokens=max_tokens,
            model_override=model_override,
            metadata=metadata,
        ):
            yield chunk

    async def estimate_cost(
        self, prompt: str, task_type: TaskType, model_override: str | None = None
    ) -> dict[str, Any]:
        """Delegate cost estimation to router"""
        complexity_map = {
            TaskType.ARCHITECTURE_DESIGN: TaskComplexity.ARCHITECTURE,
            TaskType.CODE_GENERATION: TaskComplexity.COMPLEX,
            TaskType.CODE_ANALYSIS: TaskComplexity.COMPLEX,
            TaskType.BUSINESS_INTELLIGENCE: TaskComplexity.COMPLEX,
            TaskType.DATA_ANALYSIS: TaskComplexity.MODERATE,
            TaskType.DOCUMENT_SUMMARY: TaskComplexity.MODERATE,
            TaskType.CHAT_CONVERSATION: TaskComplexity.SIMPLE,
        }

        complexity = complexity_map.get(task_type, TaskComplexity.MODERATE)

        return await llm_router.estimate_cost(
            prompt=prompt,
            task=task_type,
            complexity=complexity,
            model_override=model_override,
        )

    async def get_available_models(self) -> dict[str, Any]:
        """Delegate to router"""
        return await llm_router.get_available_models()

    async def close(self):
        """Delegate to router"""
        await llm_router.close()


# Singleton instance for compatibility
_unified_service = UnifiedLLMService()


async def get_unified_llm_service() -> UnifiedLLMService:
    """Get unified LLM service instance (deprecated)"""
    warnings.warn(
        "get_unified_llm_service is deprecated. Use llm_router from infrastructure.services.llm_router",
        DeprecationWarning,
        stacklevel=2,
    )
    return _unified_service


# Direct function for simple migration
async def completion(
    prompt: str, task="code_generation", **kwargs
) -> AsyncGenerator[str, None]:
    """
    Simple completion function for backward compatibility
    """
    task_type = TaskType(task) if isinstance(task, str) else task

    async for chunk in _unified_service.complete(
        prompt=prompt, task_type=task_type, **kwargs
    ):
        yield chunk
