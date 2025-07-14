"""
Enhanced Lambda GPU Service
Modularized implementation - see enhanced_modern_stack_cortex_service/ directory
"""

# Import all functionality from modular implementation
from .enhanced_modern_stack_cortex_service import *

# Maintain backward compatibility
__all__ = [
    "EnhancedModernStackCortexService",
    # Add other exports as needed
]
