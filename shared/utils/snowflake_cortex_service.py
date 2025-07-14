"""
Backward compatibility wrapper for Lambda GPU service.

This module maintains the old import path while using the new modular implementation.
TODO: Decompose this monolithic service into smaller, focused modules - COMPLETED
"""

# Import everything from the new modular structure
from .modern_stack_cortex import (
    CortexAuthenticationError,
    CortexConnectionError,
    CortexError,
    CortexModel,
    CortexModelError,
    CortexQuotaError,
    MCPMode,
    MCPServerError,
    ModernStackCortexService,
    TaskType,
)

# Re-export for backward compatibility
__all__ = [
    "CortexAuthenticationError",
    "CortexConnectionError",
    "CortexError",
    "CortexModel",
    "CortexModelError",
    "CortexQuotaError",
    "MCPMode",
    "MCPServerError",
    "ModernStackCortexService",
    "TaskType",
]
