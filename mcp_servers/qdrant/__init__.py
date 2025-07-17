"""
Qdrant MCP Server - Tier 1 of the Hybrid Memory Architecture

This module provides high-performance vector search with:
- Separate collections for coding and business memory
- Optimized HNSW parameters per collection type
- GPU-accelerated search operations
- Clear separation of concerns
"""

from .qdrant_mcp_server import QdrantMCPServer

__all__ = ['QdrantMCPServer']
