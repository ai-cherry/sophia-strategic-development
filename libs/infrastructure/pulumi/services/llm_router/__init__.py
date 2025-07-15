"""
LLM Router Module - Unified interface for all LLM interactions
Provides single entry point with intelligent routing and observability
"""

from .enums import Provider, TaskComplexity, TaskType
from .router import LLMRouter

# Create singleton instance
llm_router = LLMRouter()

__all__ = [
    "Provider",
    "TaskComplexity",
    "TaskType",
    "llm_router",
]
