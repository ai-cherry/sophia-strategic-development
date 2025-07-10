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
    ToolDefinition,
    ToolParameter,
    UnifiedStandardizedMCPServer,
)

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


class AIMemoryServerV2(UnifiedStandardizedMCPServer):
    """AI Memory MCP Server using UnifiedMemoryService"""

    def __init__(self):
        config = ServerConfig(
            name="ai-memory",
            version="2.2.0",
            port=9000,
            capabilities=["MEMORY", "EMBEDDING", "SEARCH", "ANALYTICS"],
            tier="PRIMARY",
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

    def get_tool_definitions(self) -> list[ToolDefinition]:
        """Define AI Memory tools"""
        return [
            ToolDefinition(
                name="store_memory",
                description="Store a new memory with category and metadata",
                parameters=[
                    ToolParameter(
                        name="content",
                        type="string",
                        description="Memory content to store",
                        required=True,
                    ),
                    ToolParameter(
                        name="category",
                        type="string",
                        description="Memory category",
                        required=True,
                    ),
                    ToolParameter(
                        name="metadata",
                        type="object",
                        description="Additional metadata",
                        required=False,
                    ),
                    ToolParameter(
                        name="user_id",
                        type="string",
                        description="User ID for the memory",
                        required=False,
                        default="system",
                    ),
                ],
            ),
            ToolDefinition(
                name="search_memories",
                description="Search memories by query or category",
                parameters=[
                    ToolParameter(
                        name="query",
                        type="string",
                        description="Search query",
                        required=False,
                    ),
                    ToolParameter(
                        name="category",
                        type="string",
                        description="Filter by category",
                        required=False,
                    ),
                    ToolParameter(
                        name="limit",
                        type="integer",
                        description="Maximum results",
                        required=False,
                        default=10,
                    ),
                    ToolParameter(
                        name="user_id",
                        type="string",
                        description="Filter by user",
                        required=False,
                    ),
                ],
            ),
            ToolDefinition(
                name="get_memory",
                description="Get a specific memory by ID (from search results)",
                parameters=[
                    ToolParameter(
                        name="memory_id",
                        type="string",
                        description="Memory ID",
                        required=True,
                    )
                ],
            ),
            ToolDefinition(
                name="store_conversation",
                description="Store a conversation in memory",
                parameters=[
                    ToolParameter(
                        name="user_id",
                        type="string",
                        description="User ID",
                        required=True,
                    ),
                    ToolParameter(
                        name="messages",
                        type="array",
                        description="Array of message objects with 'role' and 'content'",
                        required=True,
                    ),
                    ToolParameter(
                        name="metadata",
                        type="object",
                        description="Conversation metadata",
                        required=False,
                    ),
                ],
            ),
            ToolDefinition(
                name="get_conversation_context",
                description="Get conversation history for a user",
                parameters=[
                    ToolParameter(
                        name="user_id",
                        type="string",
                        description="User ID",
                        required=True,
                    ),
                    ToolParameter(
                        name="limit",
                        type="integer",
                        description="Maximum messages to retrieve",
                        required=False,
                        default=10,
                    ),
                ],
            ),
            ToolDefinition(
                name="get_memory_stats",
                description="Get memory statistics and health",
                parameters=[],
            ),
        ]

    async def execute_tool(
        self, tool_name: str, parameters: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute memory operations using UnifiedMemoryService"""

        if not self.memory_service:
            return {"success": False, "error": "Memory service not available"}

        if tool_name == "store_memory":
            return await self.store_memory(parameters)
        elif tool_name == "search_memories":
            return await self.search_memories(parameters)
        elif tool_name == "get_memory":
            return await self.get_memory(parameters)
        elif tool_name == "store_conversation":
            return await self.store_conversation(parameters)
        elif tool_name == "get_conversation_context":
            return await self.get_conversation_context(parameters)
        elif tool_name == "get_memory_stats":
            return await self.get_memory_stats()
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

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
            self.metrics["operations_total"].labels(
                operation="store", status="success"
            ).inc()

            return {
                "success": True,
                "memory_id": memory_id,
                "timestamp": datetime.now(UTC).isoformat(),
                "storage": "snowflake_cortex",
            }

        except Exception as e:
            self.logger.error(f"Error storing memory: {e}")
            self.metrics["operations_total"].labels(
                operation="store", status="error"
            ).inc()
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

            self.metrics["operations_total"].labels(
                operation="search", status="success"
            ).inc()

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
            self.metrics["operations_total"].labels(
                operation="search", status="error"
            ).inc()
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

            self.metrics["operations_total"].labels(
                operation="get", status="success"
            ).inc()

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
            self.metrics["operations_total"].labels(
                operation="get", status="error"
            ).inc()
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

            self.metrics["operations_total"].labels(
                operation="store_conversation", status="success"
            ).inc()

            return {
                "success": True,
                "user_id": user_id,
                "messages_stored": len(messages),
                "timestamp": datetime.now(UTC).isoformat(),
                "storage": "mem0",
            }

        except Exception as e:
            self.logger.error(f"Error storing conversation: {e}")
            self.metrics["operations_total"].labels(
                operation="store_conversation", status="error"
            ).inc()
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

            self.metrics["operations_total"].labels(
                operation="get_conversation", status="success"
            ).inc()

            return {
                "success": True,
                "user_id": user_id,
                "conversations": context,
                "total": len(context),
                "storage": "mem0",
            }

        except Exception as e:
            self.logger.error(f"Error getting conversation context: {e}")
            self.metrics["operations_total"].labels(
                operation="get_conversation", status="error"
            ).inc()
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

            self.metrics["operations_total"].labels(
                operation="stats", status="success"
            ).inc()

            return {"success": True, "stats": stats}

        except Exception as e:
            self.logger.error(f"Error getting stats: {e}")
            self.metrics["operations_total"].labels(
                operation="stats", status="error"
            ).inc()
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
    server = AIMemoryServerV2()
    server.run()
