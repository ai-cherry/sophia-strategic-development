"""
Repository Implementations

This module contains concrete implementations of the repository interfaces
defined in the application layer.
"""

from .qdrant_call_repository import QdrantCallRepository

__all__ = ["QdrantCallRepository"]
