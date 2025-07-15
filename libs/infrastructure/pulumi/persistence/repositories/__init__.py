"""
Repository Implementations

This module contains concrete implementations of the repository interfaces
defined in the application layer.
"""

from .QDRANT_call_repository import QdrantCallRepository

__all__ = ["QdrantCallRepository"]
