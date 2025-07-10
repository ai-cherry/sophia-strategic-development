"""
Sophia AI Memory MCP Server v2
Using official Anthropic MCP SDK

Date: July 10, 2025
"""

import asyncio
import json
import sys
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
from pydantic import BaseModel, Field
from mcp.types import Tool, TextContent

from base.unified_standardized_base import StandardizedMCPServer, ServerConfig


class MemoryRecord(BaseModel):
    """Memory record model"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    content: str
    category: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    embedding: Optional[List[float]] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    score: float = 1.0


class AIMemoryServer(StandardizedMCPServer):
    """AI Memory MCP Server using official SDK"""
    
    def __init__(self):
        config = ServerConfig(
            name="ai_memory",
            version="2.0.0",
            description="AI Memory storage and retrieval server"
        )
        super().__init__(config)
        
        # Memory storage
        self.memories: Dict[str, MemoryRecord] = {}
        self.memory_index: Dict[str, List[str]] = {}  # category -> memory_ids
        
    async def get_custom_tools(self) -> List[Tool]:
        """Define custom tools for AI Memory"""
        return [
            Tool(
                name="store_memory",
                description="Store a new memory with category and metadata",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "Memory content to store"
                        },
                        "category": {
                            "type": "string",
                            "description": "Memory category"
                        },
                        "metadata": {
                            "type": "object",
                            "description": "Additional metadata",
                            "additionalProperties": True
                        }
                    },
                    "required": ["content", "category"]
                }
            ),
            Tool(
                name="search_memories",
                description="Search memories by query or category",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "category": {
                            "type": "string",
                            "description": "Filter by category"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum results",
                            "default": 10
                        }
                    },
                    "required": []
                }
            ),
            Tool(
                name="get_memory",
                description="Get a specific memory by ID",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "memory_id": {
                            "type": "string",
                            "description": "Memory ID"
                        }
                    },
                    "required": ["memory_id"]
                }
            ),
            Tool(
                name="update_memory",
                description="Update an existing memory",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "memory_id": {
                            "type": "string",
                            "description": "Memory ID"
                        },
                        "content": {
                            "type": "string",
                            "description": "Updated content"
                        },
                        "metadata": {
                            "type": "object",
                            "description": "Updated metadata",
                            "additionalProperties": True
                        }
                    },
                    "required": ["memory_id"]
                }
            ),
            Tool(
                name="delete_memory",
                description="Delete a memory",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "memory_id": {
                            "type": "string",
                            "description": "Memory ID to delete"
                        }
                    },
                    "required": ["memory_id"]
                }
            ),
            Tool(
                name="get_memory_stats",
                description="Get memory statistics",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            )
        ]
    
    async def handle_custom_tool(self, name: str, arguments: dict) -> Dict[str, Any]:
        """Handle custom tool calls"""
        try:
            if name == "store_memory":
                return await self._store_memory(arguments)
            elif name == "search_memories":
                return await self._search_memories(arguments)
            elif name == "get_memory":
                return await self._get_memory(arguments)
            elif name == "update_memory":
                return await self._update_memory(arguments)
            elif name == "delete_memory":
                return await self._delete_memory(arguments)
            elif name == "get_memory_stats":
                return await self._get_memory_stats()
            else:
                raise ValueError(f"Unknown tool: {name}")
        except Exception as e:
            self.logger.error(f"Error handling tool {name}: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _store_memory(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Store a new memory"""
        try:
            # Create memory record
            memory = MemoryRecord(
                content=params["content"],
                category=params["category"],
                metadata=params.get("metadata", {})
            )
            
            # Generate embedding (placeholder - would use real embedding model)
            memory.embedding = np.random.rand(768).tolist()
            
            # Store memory
            self.memories[memory.id] = memory
            
            # Update index
            if memory.category not in self.memory_index:
                self.memory_index[memory.category] = []
            self.memory_index[memory.category].append(memory.id)
            
            self.logger.info(f"Stored memory {memory.id} in category {memory.category}")
            
            return {
                "status": "success",
                "memory_id": memory.id,
                "timestamp": memory.timestamp.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error storing memory: {e}")
            raise
    
    async def _search_memories(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search memories"""
        try:
            query = params.get("query", "")
            category = params.get("category")
            limit = params.get("limit", 10)
            
            # Get candidate memories
            candidates = []
            if category:
                memory_ids = self.memory_index.get(category, [])
                candidates = [
                    self.memories[mid] for mid in memory_ids 
                    if mid in self.memories
                ]
            else:
                candidates = list(self.memories.values())
            
            # Simple text search (would use vector search in production)
            if query:
                results = []
                for memory in candidates:
                    if query.lower() in memory.content.lower():
                        results.append(memory)
            else:
                results = candidates
            
            # Sort by timestamp and limit
            results.sort(key=lambda m: m.timestamp, reverse=True)
            results = results[:limit]
            
            return {
                "status": "success",
                "memories": [
                    {
                        "id": m.id,
                        "content": m.content,
                        "category": m.category,
                        "metadata": m.metadata,
                        "timestamp": m.timestamp.isoformat(),
                        "score": m.score
                    }
                    for m in results
                ],
                "total": len(results)
            }
            
        except Exception as e:
            self.logger.error(f"Error searching memories: {e}")
            raise
    
    async def _get_memory(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get specific memory"""
        try:
            memory_id = params["memory_id"]
            memory = self.memories.get(memory_id)
            
            if not memory:
                return {"status": "error", "error": "Memory not found"}
            
            return {
                "status": "success",
                "memory": {
                    "id": memory.id,
                    "content": memory.content,
                    "category": memory.category,
                    "metadata": memory.metadata,
                    "timestamp": memory.timestamp.isoformat(),
                    "score": memory.score
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting memory: {e}")
            raise
    
    async def _update_memory(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update memory"""
        try:
            memory_id = params["memory_id"]
            memory = self.memories.get(memory_id)
            
            if not memory:
                return {"status": "error", "error": "Memory not found"}
            
            # Update fields
            if "content" in params:
                memory.content = params["content"]
                # Regenerate embedding
                memory.embedding = np.random.rand(768).tolist()
            
            if "metadata" in params:
                memory.metadata.update(params["metadata"])
            
            memory.timestamp = datetime.now(UTC)
            
            return {
                "status": "success",
                "memory_id": memory.id,
                "updated": True
            }
            
        except Exception as e:
            self.logger.error(f"Error updating memory: {e}")
            raise
    
    async def _delete_memory(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete memory"""
        try:
            memory_id = params["memory_id"]
            memory = self.memories.get(memory_id)
            
            if not memory:
                return {"status": "error", "error": "Memory not found"}
            
            # Remove from index
            if memory.category in self.memory_index:
                self.memory_index[memory.category] = [
                    mid for mid in self.memory_index[memory.category]
                    if mid != memory_id
                ]
            
            # Delete memory
            del self.memories[memory_id]
            
            return {
                "status": "success",
                "deleted": True,
                "memory_id": memory_id
            }
            
        except Exception as e:
            self.logger.error(f"Error deleting memory: {e}")
            raise
    
    async def _get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        try:
            stats = {
                "total_memories": len(self.memories),
                "categories": {},
                "memory_size_bytes": 0
            }
            
            # Category stats
            for category, memory_ids in self.memory_index.items():
                stats["categories"][category] = len(memory_ids)
            
            # Calculate approximate memory size
            for memory in self.memories.values():
                stats["memory_size_bytes"] += len(
                    json.dumps(memory.model_dump()).encode()
                )
            
            return {
                "status": "success",
                "stats": stats
            }
            
        except Exception as e:
            self.logger.error(f"Error getting stats: {e}")
            raise


async def main():
    """Main entry point"""
    server = AIMemoryServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main()) 