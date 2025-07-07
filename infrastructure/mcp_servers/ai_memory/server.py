#!/usr/bin/env python3
"""
Unified AI Memory MCP Server
Enterprise-grade implementation with performance optimization
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.types import Resource, Tool

from .core.config import AIMemoryConfig
from .core.models import MemoryEntry, SearchResult
from .core.performance import PerformanceMonitor
from .handlers.memory_handlers import MemoryHandler
from .handlers.search_handlers import SearchHandler
from .utils.monitoring import HealthMonitor

logger = logging.getLogger(__name__)


class UnifiedAIMemoryServer:
    """Unified AI Memory MCP Server with enterprise features"""

    def __init__(self, config: Optional[AIMemoryConfig] = None):
        self.config = config or AIMemoryConfig()
        self.server = Server("ai-memory")
        self.performance_monitor = PerformanceMonitor()
        self.health_monitor = HealthMonitor()
        self.memory_handler = MemoryHandler(self.config)
        self.search_handler = SearchHandler(self.config)

        # Register handlers
        self._register_tools()
        self._register_resources()

    def _register_tools(self):
        """Register MCP tools"""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            return [
                Tool(
                    name="store_memory",
                    description="Store a memory entry with semantic indexing",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {"type": "string"},
                            "metadata": {"type": "object"},
                            "tags": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["content"],
                    },
                ),
                Tool(
                    name="search_memory",
                    description="Search memories using semantic similarity",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"},
                            "limit": {"type": "integer", "default": 10},
                            "threshold": {"type": "number", "default": 0.7},
                        },
                        "required": ["query"],
                    },
                ),
                Tool(
                    name="get_memory_stats",
                    description="Get memory system statistics",
                    inputSchema={"type": "object", "properties": {}},
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> list[Any]:
            """Handle tool calls with performance monitoring"""
            async with self.performance_monitor.measure(f"tool_{name}"):
                if name == "store_memory":
                    return await self.memory_handler.store_memory(**arguments)
                elif name == "search_memory":
                    return await self.search_handler.search_memories(**arguments)
                elif name == "get_memory_stats":
                    return await self._get_stats()
                else:
                    raise ValueError(f"Unknown tool: {name}")

    def _register_resources(self):
        """Register MCP resources"""

        @self.server.list_resources()
        async def list_resources() -> list[Resource]:
            return [
                Resource(
                    uri="memory://stats",
                    name="Memory Statistics",
                    description="Current memory system statistics",
                ),
                Resource(
                    uri="memory://health",
                    name="Health Status",
                    description="System health and performance metrics",
                ),
            ]

    async def _get_stats(self) -> dict[str, Any]:
        """Get comprehensive system statistics"""
        return {
            "memory_count": await self.memory_handler.get_memory_count(),
            "performance_metrics": self.performance_monitor.get_metrics(),
            "health_status": await self.health_monitor.get_status(),
            "uptime": self.performance_monitor.get_uptime(),
        }

    async def start(self):
        """Start the AI Memory server"""
        logger.info("🧠 Starting Unified AI Memory MCP Server...")
        await self.health_monitor.start()
        await self.performance_monitor.start()
        logger.info("✅ AI Memory server ready")

    async def stop(self):
        """Stop the AI Memory server"""
        logger.info("🛑 Stopping AI Memory server...")
        await self.health_monitor.stop()
        await self.performance_monitor.stop()


async def main():
    """Main entry point"""
    server = UnifiedAIMemoryServer()
    await server.start()

    try:
        # Keep server running
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        await server.stop()


if __name__ == "__main__":
    asyncio.run(main())
