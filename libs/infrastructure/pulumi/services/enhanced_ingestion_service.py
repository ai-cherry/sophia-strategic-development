"""
EnhancedIngestionService
Modularized implementation - see enhanced_ingestion_service/ directory
"""

# Import all functionality from modular implementation
from .enhanced_ingestion_service import (
    EnhancedIngestionService,
    __all__
)

# Maintain backward compatibility
__all__ = [
    "EnhancedIngestionService",
    # Add other exports as needed
]
