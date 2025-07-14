"""
Unified Memory Service - Qdrant Fortress Edition
Primary memory service for Sophia AI using Qdrant as vector store

This service provides unified access to:
- Qdrant vector search
- Redis caching
- PostgreSQL hybrid queries
- Lambda GPU embeddings
"""

from backend.services.unified_memory_service import UnifiedMemoryService

# Export V3 as primary service
UnifiedMemoryService = UnifiedMemoryService

# Backward compatibility
class UnifiedMemoryService:
    """Deprecated V2 service - redirects to V3"""
    
    def __init__(self, *args, **kwargs):
        import warnings
        warnings.warn(
            "UnifiedMemoryService is deprecated. Use UnifiedMemoryService instead.",
            DeprecationWarning,
            stacklevel=2
        )
        self._service = UnifiedMemoryService(*args, **kwargs)
    
    def __getattr__(self, name):
        return getattr(self._service, name)
