"""
Sophia AI Memory MCP Server V2
Refactored to use UnifiedMemoryService for all operations
Date: July 10, 2025
"""

import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent))

from base.unified_standardized_base import (
    ServerConfig,
    StandardizedMCPServer,
)
from mcp.types import Tool

# Import UnifiedMemoryService
from backend.services.unified_memory_service import get_unified_memory_service


class MemoryRecord(BaseModel):
    """Memory record model for MCP interface"""

    id: str = Field(default_factory=lambda: str(uuid4()))
    content: str
    category: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    score: float = 1.0


class AIMemoryServerV2(StandardizedMCPServer):
    """AI Memory MCP Server using UnifiedMemoryService"""

    def __init__(self):
        config = ServerConfig(
            name="ai-memory",
            version="2.2.0",
            description="AI Memory server with UnifiedMemoryService backend",
        )
        super().__init__(config)

        # Initialize UnifiedMemoryService
        try:
            self.memory_service = get_unified_memory_service()
            self.logger.info(
                f"UnifiedMemoryService initialized - Degraded mode: {self.memory_service.degraded_mode}"
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize UnifiedMemoryService: {e}")
            # Still allow server to start but in limited mode
            self.memory_service = None

    async def get_custom_tools(self) -> list[Tool]:
        """Define AI Memory tools"""
        return [
            Tool(
                name="store_memory",
                description="Store a new memory with category and metadata",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "Memory content to store",
                        },
                        "category": {
                            "type": "string",
                            "description": "Memory category",
                        },
                        "metadata": {
                            "type": "object",
                            "description": "Additional metadata",
                        },
                        "user_id": {
                            "type": "string",
                            "description": "User ID for the memory",
                            "default": "system",
                        },
                    },
                    "required": ["content", "category"],
                },
            ),
            Tool(
                name="search_memories",
                description="Search memories by query or category",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "category": {
                            "type": "string",
                            "description": "Filter by category",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum results",
                            "default": 10,
                        },
                        "user_id": {"type": "string", "description": "Filter by user"},
                    },
                    "required": [],
                },
            ),
            Tool(
                name="get_memory",
                description="Get a specific memory by ID (from search results)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "memory_id": {"type": "string", "description": "Memory ID"}
                    },
                    "required": ["memory_id"],
                },
            ),
            Tool(
                name="store_conversation",
                description="Store a conversation in memory",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "User ID"},
                        "messages": {
                            "type": "array",
                            "description": "Array of message objects with 'role' and 'content'",
                        },
                        "metadata": {
                            "type": "object",
                            "description": "Conversation metadata",
                        },
                    },
                    "required": ["user_id", "messages"],
                },
            ),
            Tool(
                name="get_conversation_context",
                description="Get conversation history for a user",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "User ID"},
                        "limit": {
                            "type": "integer",
                            "description": "Maximum messages to retrieve",
                            "default": 10,
                        },
                    },
                    "required": ["user_id"],
                },
            ),
            Tool(
                name="get_memory_stats",
                description="Get memory statistics and health",
                inputSchema={"type": "object", "properties": {}, "required": []},
            ),
        ]

    async def handle_custom_tool(self, name: str, arguments: dict) -> dict[str, Any]:
        """Handle custom tool calls"""
        if not self.memory_service:
            return {"success": False, "error": "Memory service not available"}

        if name == "store_memory":
            return await self.store_memory(arguments)
        elif name == "search_memories":
            return await self.search_memories(arguments)
        elif name == "get_memory":
            return await self.get_memory(arguments)
        elif name == "store_conversation":
            return await self.store_conversation(arguments)
        elif name == "get_conversation_context":
            return await self.get_conversation_context(arguments)
        elif name == "get_memory_stats":
            return await self.get_memory_stats()
        else:
            raise ValueError(f"Unknown tool: {name}")

    async def store_memory(self, params: dict[str, Any]) -> dict[str, Any]:
        """Store a new memory using UnifiedMemoryService"""
        try:
            # Add category to metadata
            metadata = params.get("metadata", {})
            metadata["category"] = params["category"]

            # Store in Snowflake via UnifiedMemoryService
            memory_id = await self.memory_service.add_knowledge(
                content=params["content"],
                source=f"ai_memory_mcp/{params['category']}",
                metadata=metadata,
                user_id=params.get("user_id", "system"),
            )

            self.logger.info(
                f"Stored memory {memory_id} in category {params['category']}"
            )

            return {
                "success": True,
                "memory_id": memory_id,
                "timestamp": datetime.now(UTC).isoformat(),
                "storage": "snowflake_cortex",
            }

        except Exception as e:
            self.logger.error(f"Error storing memory: {e}")
            return {"success": False, "error": str(e)}

    async def search_memories(self, params: dict[str, Any]) -> dict[str, Any]:
        """Search memories using UnifiedMemoryService"""
        try:
            query = params.get("query", "")
            category = params.get("category")
            limit = params.get("limit", 10)
            user_id = params.get("user_id")

            # Build metadata filter
            metadata_filter = {}
            if category:
                metadata_filter["category"] = category

            # Search using Snowflake Cortex
            results = await self.memory_service.search_knowledge(
                query=query
                or category
                or "",  # Use category as query if no query provided
                limit=limit,
                metadata_filter=metadata_filter if metadata_filter else None,
                user_id=user_id,
            )

            # Format results for MCP interface
            memories = []
            for result in results:
                memories.append(
                    {
                        "id": result["id"],
                        "content": result["content"],
                        "category": result["metadata"].get("category", "unknown"),
                        "metadata": result["metadata"],
                        "timestamp": result.get(
                            "created_at", datetime.now(UTC).isoformat()
                        ),
                        "score": result.get("similarity", 1.0),
                    }
                )

            return {
                "success": True,
                "memories": memories,
                "total": len(memories),
                "storage": "snowflake_cortex",
            }

        except Exception as e:
            self.logger.error(f"Error searching memories: {e}")
            return {"success": False, "error": str(e)}

    async def get_memory(self, params: dict[str, Any]) -> dict[str, Any]:
        """Get specific memory by searching for its ID"""
        try:
            memory_id = params["memory_id"]

            # Search by ID in metadata
            results = await self.memory_service.search_knowledge(
                query=memory_id,
                limit=1,
                metadata_filter={"id": memory_id},
            )

            if not results:
                return {"success": False, "error": "Memory not found"}

            result = results[0]

            return {
                "success": True,
                "memory": {
                    "id": result["id"],
                    "content": result["content"],
                    "category": result["metadata"].get("category", "unknown"),
                    "metadata": result["metadata"],
                    "timestamp": result.get(
                        "created_at", datetime.now(UTC).isoformat()
                    ),
                    "score": result.get("similarity", 1.0),
                },
                "storage": "snowflake_cortex",
            }

        except Exception as e:
            self.logger.error(f"Error getting memory: {e}")
            return {"success": False, "error": str(e)}

    async def store_conversation(self, params: dict[str, Any]) -> dict[str, Any]:
        """Store conversation using UnifiedMemoryService"""
        try:
            user_id = params["user_id"]
            messages = params["messages"]
            metadata = params.get("metadata", {})

            # Store conversation in Mem0
            await self.memory_service.add_conversation_memory(
                user_id=user_id,
                messages=messages,
                metadata=metadata,
            )

            return {
                "success": True,
                "user_id": user_id,
                "messages_stored": len(messages),
                "timestamp": datetime.now(UTC).isoformat(),
                "storage": "mem0",
            }

        except Exception as e:
            self.logger.error(f"Error storing conversation: {e}")
            return {"success": False, "error": str(e)}

    async def get_conversation_context(self, params: dict[str, Any]) -> dict[str, Any]:
        """Get conversation context using UnifiedMemoryService"""
        try:
            user_id = params["user_id"]
            limit = params.get("limit", 10)

            # Get conversation from Mem0
            context = await self.memory_service.get_conversation_context(
                user_id=user_id,
                limit=limit,
            )

            return {
                "success": True,
                "user_id": user_id,
                "conversations": context,
                "total": len(context),
                "storage": "mem0",
            }

        except Exception as e:
            self.logger.error(f"Error getting conversation context: {e}")
            return {"success": False, "error": str(e)}

    async def get_memory_stats(self) -> dict[str, Any]:
        """Get memory statistics from UnifiedMemoryService"""
        try:
            stats = {
                "service_status": "healthy"
                if not self.memory_service.degraded_mode
                else "degraded",
                "degraded_mode": self.memory_service.degraded_mode,
                "tiers": {
                    "L1_redis": "available"
                    if self.memory_service.redis_client
                    else "unavailable",
                    "L2_mem0": "available"
                    if self.memory_service.mem0_client
                    else "unavailable",
                    "L3_L4_L5_snowflake": "available"
                    if self.memory_service.snowflake_conn
                    else "unavailable",
                },
                "features": {
                    "vector_search": not self.memory_service.degraded_mode,
                    "conversation_memory": self.memory_service.mem0_client is not None,
                    "knowledge_storage": not self.memory_service.degraded_mode,
                    "cortex_ai": not self.memory_service.degraded_mode,
                },
                "timestamp": datetime.now(UTC).isoformat(),
            }

            # Get Redis stats if available
            if self.memory_service.redis_client:
                try:
                    redis_info = self.memory_service.redis_client.info()
                    stats["redis_stats"] = {
                        "used_memory_human": redis_info.get("used_memory_human", "0"),
                        "connected_clients": redis_info.get("connected_clients", 0),
                    }
                except Exception:
                    pass

            return {"success": True, "stats": stats}

        except Exception as e:
            self.logger.error(f"Error getting stats: {e}")
            return {"success": False, "error": str(e)}

    async def on_startup(self):
        """Initialize AI Memory server"""
        self.logger.info("AI Memory server V2 starting with UnifiedMemoryService...")

        if self.memory_service:
            self.logger.info("Memory tiers available:")
            self.logger.info(
                f"  L1 Redis: {self.memory_service.redis_client is not None}"
            )
            self.logger.info(
                f"  L2 Mem0: {self.memory_service.mem0_client is not None}"
            )
            self.logger.info(
                f"  L3-L5 Snowflake: {self.memory_service.snowflake_conn is not None}"
            )
            self.logger.info(f"  Degraded mode: {self.memory_service.degraded_mode}")
        else:
            self.logger.error("AI Memory server running without UnifiedMemoryService!")

    async def on_shutdown(self):
        """Cleanup AI Memory server"""
        self.logger.info("AI Memory server V2 shutting down...")

        # UnifiedMemoryService handles its own cleanup
        if self.memory_service:
            self.memory_service.close()

        self.logger.info("AI Memory server V2 stopped")


# Create and run server
if __name__ == "__main__":
    import asyncio

    async def main():
        server = AIMemoryServerV2()
        await server.run()

    asyncio.run(main())
