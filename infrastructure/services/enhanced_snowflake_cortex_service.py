"""
Enhanced Snowflake Cortex Service
Modularized implementation - see enhanced_snowflake_cortex_service/ directory
"""

# Import all functionality from modular implementation
from .enhanced_snowflake_cortex_service import *

# Maintain backward compatibility
__all__ = [
    "EnhancedSnowflakeCortexService",
    # Add other exports as needed
]
