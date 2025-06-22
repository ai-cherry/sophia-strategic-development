"""Compatibility wrapper for vector store access."""
from backend.vector.vector_integration import (
    VectorIntegration,
    VectorConfig,
    VectorSearchResult,
)

__all__ = ["VectorIntegration", "VectorConfig", "VectorSearchResult"]
