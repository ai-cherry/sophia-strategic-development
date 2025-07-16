"""
MultiAgentWorkflow
Modularized implementation - see multi_agent_workflow/ directory
"""

# Import all functionality from modular implementation
from .multi_agent_workflow import (
    MultiAgentWorkflow,
    __all__
)

# Maintain backward compatibility
__all__ = [
    "MultiAgentWorkflow",
    # Add other exports as needed
]
