"""
Unified Memory Service - Main Entry Point
Redirects to primary implementation
"""

from backend.services.unified_memory_service_primary import UnifiedMemoryService

# Export primary service
__all__ = ['UnifiedMemoryService']
