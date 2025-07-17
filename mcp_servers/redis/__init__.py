"""
Redis MCP Server - Tier 3 of the Hybrid Memory Architecture

This module provides high-performance caching with:
- Separate databases for coding and business data
- LRU eviction policies
- Session-based caching
- Aggregation caching for dashboards
"""

from .redis_cache_layer import RedisCacheMCPServer

__all__ = ['RedisCacheMCPServer']
