"""
PostgreSQL MCP Server - Tier 4 of the Hybrid Memory Architecture

This module provides structured data storage with:
- Separate schemas for coding and business data
- Relational data management
- Transaction support
- Query optimization
"""

from .structured_data_store import PostgreSQLMCPServer

__all__ = ['PostgreSQLMCPServer']
