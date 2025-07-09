"""
Backward compatibility wrapper for Snowflake Cortex service.

This module maintains the old import path while using the new modular implementation.
TODO: Decompose this monolithic service into smaller, focused modules - COMPLETED
"""

# Import everything from the new modular structure
from .snowflake_cortex import (
    CortexAuthenticationError,
    CortexConnectionError,
    CortexError,
    CortexModel,
    CortexModelError,
    CortexQuotaError,
    MCPMode,
    MCPServerError,
    SnowflakeCortexService,
    TaskType,
)

# Re-export for backward compatibility
__all__ = [
    "SnowflakeCortexService",
    "CortexModel",
    "TaskType",
    "MCPMode",
    "CortexError",
    "CortexConnectionError",
    "CortexAuthenticationError",
    "CortexModelError",
    "CortexQuotaError",
    "MCPServerError",
]
