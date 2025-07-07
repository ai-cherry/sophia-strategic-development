"""
AI Memory MCP Server - Main Server Implementation
Consolidated, optimized, and type-safe MCP server for AI Memory operations
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

from .core import (
    AIMemoryConfig,
    MemoryRecord,
    MemoryType,
    MemoryCategory,
    MemoryPriority,
    SearchQuery,
    SearchResult,
    MemoryOperationResult,
    MemoryError,
    MemoryNotFoundError,
    MemoryValidationError,
    get_config,
)
from .core.performance import (
    performance_monitor,
    get_semaphore_pool,
    get_resource_monitor,
    with_timeout,
)
from .handlers import (
    MemoryStorageHandler,
    MemorySearchHandler,
    MemoryValidationHandler,
    MemoryEmbeddingHandler,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIMemoryMCPServer:
    """AI Memory MCP Server with enterprise-grade features"""
    
    def __init__(self, config: Optional[AIMemoryConfig] = None):
        self.config = config or get_config()
        self.server = Server("ai-memory")
        
        # Initialize handlers
        self.storage_handler = MemoryStorageHandler(self.config)
        self.search_handler = MemorySearchHandler(self.config)
        self.validation_handler = MemoryValidationHandler(self.config)
        self.embedding_handler = MemoryEmbeddingHandler(self.config)
        
        # Performance monitoring
        self.semaphore_pool = get_semaphore_pool()
        self.resource_monitor = get_resource_monitor()
        
        # Setup MCP handlers
        self._setup_tools()
        self._setup_resources()
        
        logger.info(f"AI Memory MCP Server initialized with config: {self.config.server_name}")
    
    def _setup_tools(self) -> None:
        """Setup MCP tools for memory operations"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available memory tools"""
            return [
                Tool(
                    name="store_memory",
                    description="Store a new memory record with automatic embedding generation",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "Memory content to store",
                                "minLength": 1,
                                "maxLength": 50000
                            },
                            "memory_type": {
                                "type": "string",
                                "enum": [t.value for t in MemoryType],
                                "description": "Type of memory"
                            },
                            "category": {
                                "type": "string", 
                                "enum": [c.value for c in MemoryCategory],
                                "description": "Memory category"
                            },
                            "priority": {
                                "type": "string",
                                "enum": [p.value for p in MemoryPriority],
                                "default": "medium",
                                "description": "Memory priority"
                            },
                            "summary": {
                                "type": "string",
                                "description": "Optional brief summary",
                                "maxLength": 500
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Tags for categorization"
                            },
                            "metadata": {
                                "type": "object",
                                "description": "Additional metadata"
                            }
                        },
                        "required": ["content", "memory_type", "category"]
                    }
                ),
                Tool(
                    name="search_memories",
                    description="Search memories using semantic similarity and filters",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query",
                                "minLength": 1,
                                "maxLength": 1000
                            },
                            "memory_types": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": [t.value for t in MemoryType]
                                },
                                "description": "Filter by memory types"
                            },
                            "categories": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": [c.value for c in MemoryCategory]
                                },
                                "description": "Filter by categories"
                            },
                            "limit": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 100,
                                "default": 10,
                                "description": "Maximum results"
                            },
                            "similarity_threshold": {
                                "type": "number",
                                "minimum": 0.0,
                                "maximum": 1.0,
                                "default": 0.7,
                                "description": "Minimum similarity score"
                            },
                            "include_archived": {
                                "type": "boolean",
                                "default": False,
                                "description": "Include archived memories"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="get_memory",
                    description="Retrieve a specific memory by ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "memory_id": {
                                "type": "string",
                                "description": "Memory ID to retrieve",
                                "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
                            }
                        },
                        "required": ["memory_id"]
                    }
                ),
                Tool(
                    name="update_memory",
                    description="Update an existing memory record",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "memory_id": {
                                "type": "string",
                                "description": "Memory ID to update",
                                "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
                            },
                            "content": {
                                "type": "string",
                                "description": "Updated content",
                                "minLength": 1,
                                "maxLength": 50000
                            },
                            "summary": {
                                "type": "string",
                                "description": "Updated summary",
                                "maxLength": 500
                            },
                            "priority": {
                                "type": "string",
                                "enum": [p.value for p in MemoryPriority],
                                "description": "Updated priority"
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Updated tags"
                            }
                        },
                        "required": ["memory_id"]
                    }
                ),
                Tool(
                    name="delete_memory",
                    description="Delete a memory record",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "memory_id": {
                                "type": "string",
                                "description": "Memory ID to delete",
                                "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
                            },
                            "permanent": {
                                "type": "boolean",
                                "default": False,
                                "description": "Permanently delete (vs archive)"
                            }
                        },
                        "required": ["memory_id"]
                    }
                ),
                Tool(
                    name="get_memory_stats",
                    description="Get statistics about stored memories",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "include_details": {
                                "type": "boolean",
                                "default": False,
                                "description": "Include detailed breakdown"
                            }
                        }
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls"""
            
            try:
                async with self.resource_monitor.track_operation(f"tool_{name}"):
                    if name == "store_memory":
                        result = await self._handle_store_memory(arguments)
                    elif name == "search_memories":
                        result = await self._handle_search_memories(arguments)
                    elif name == "get_memory":
                        result = await self._handle_get_memory(arguments)
                    elif name == "update_memory":
                        result = await self._handle_update_memory(arguments)
                    elif name == "delete_memory":
                        result = await self._handle_delete_memory(arguments)
                    elif name == "get_memory_stats":
                        result = await self._handle_get_memory_stats(arguments)
                    else:
                        raise MemoryError(f"Unknown tool: {name}")
                
                return [TextContent(type="text", text=str(result))]
                
            except Exception as e:
                logger.error(f"Tool call failed: {name} - {e}")
                error_result = MemoryOperationResult.error_result(
                    operation=name,
                    message=str(e),
                    error_details={"exception_type": type(e).__name__}
                )
                return [TextContent(type="text", text=str(error_result.dict()))]
    
    def _setup_resources(self) -> None:
        """Setup MCP resources for memory data"""
        
        @self.server.list_resources()
        async def handle_list_resources() -> List[Resource]:
            """List available memory resources"""
            return [
                Resource(
                    uri="memory://stats",
                    name="Memory Statistics",
                    description="Overall statistics about stored memories",
                    mimeType="application/json"
                ),
                Resource(
                    uri="memory://health",
                    name="Memory System Health",
                    description="Health status of memory system components",
                    mimeType="application/json"
                ),
                Resource(
                    uri="memory://config",
                    name="Memory Configuration",
                    description="Current memory system configuration",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Handle resource reads"""
            
            try:
                if uri == "memory://stats":
                    stats = await self._get_system_stats()
                    return str(stats)
                elif uri == "memory://health":
                    health = await self._get_system_health()
                    return str(health)
                elif uri == "memory://config":
                    config_dict = self.config.dict(exclude={"snowflake_password", "redis_password", "openai_api_key", "pinecone_api_key"})
                    return str(config_dict)
                else:
                    raise MemoryError(f"Unknown resource: {uri}")
                    
            except Exception as e:
                logger.error(f"Resource read failed: {uri} - {e}")
                return f"Error reading resource: {e}"
    
    @performance_monitor("store_memory")
    async def _handle_store_memory(self, arguments: Dict[str, Any]) -> MemoryOperationResult:
        """Handle store memory tool call"""
        
        try:
            # Validate input
            validated_args = await self.validation_handler.validate_store_request(arguments)
            
            # Create memory record
            memory = MemoryRecord(
                content=validated_args["content"],
                memory_type=MemoryType(validated_args["memory_type"]),
                category=MemoryCategory(validated_args["category"]),
                priority=MemoryPriority(validated_args.get("priority", "medium")),
                summary=validated_args.get("summary"),
            )
            
            # Add metadata if provided
            if "tags" in validated_args:
                memory.metadata.tags = validated_args["tags"]
            
            if "metadata" in validated_args:
                memory.metadata.custom_attributes.update(validated_args["metadata"])
            
            # Generate embedding
            embedding = await self.embedding_handler.generate_embedding(memory.content)
            memory.embedding = embedding
            
            # Store memory
            success = await self.storage_handler.store_memory(memory)
            
            if success:
                return MemoryOperationResult.success_result(
                    operation="store_memory",
                    memory_id=memory.id,
                    message="Memory stored successfully",
                    data={"memory": memory.dict()}
                )
            else:
                return MemoryOperationResult.error_result(
                    operation="store_memory",
                    message="Failed to store memory"
                )
                
        except Exception as e:
            logger.error(f"Store memory failed: {e}")
            return MemoryOperationResult.error_result(
                operation="store_memory",
                message=str(e),
                error_details={"exception_type": type(e).__name__}
            )
    
    @performance_monitor("search_memories")
    async def _handle_search_memories(self, arguments: Dict[str, Any]) -> MemoryOperationResult:
        """Handle search memories tool call"""
        
        try:
            # Create search query
            search_query = SearchQuery(
                query=arguments["query"],
                memory_types=[MemoryType(t) for t in arguments.get("memory_types", [])],
                categories=[MemoryCategory(c) for c in arguments.get("categories", [])],
                limit=arguments.get("limit", 10),
                similarity_threshold=arguments.get("similarity_threshold", 0.7),
                include_archived=arguments.get("include_archived", False)
            )
            
            # Perform search
            results = await self.search_handler.search_memories(search_query)
            
            return MemoryOperationResult.success_result(
                operation="search_memories",
                message=f"Found {len(results)} memories",
                data={
                    "results": [result.dict() for result in results],
                    "query": search_query.dict()
                }
            )
            
        except Exception as e:
            logger.error(f"Search memories failed: {e}")
            return MemoryOperationResult.error_result(
                operation="search_memories",
                message=str(e),
                error_details={"exception_type": type(e).__name__}
            )
    
    @performance_monitor("get_memory")
    async def _handle_get_memory(self, arguments: Dict[str, Any]) -> MemoryOperationResult:
        """Handle get memory tool call"""
        
        try:
            memory_id = arguments["memory_id"]
            memory = await self.storage_handler.get_memory(memory_id)
            
            if memory:
                return MemoryOperationResult.success_result(
                    operation="get_memory",
                    memory_id=memory_id,
                    message="Memory retrieved successfully",
                    data={"memory": memory.dict()}
                )
            else:
                raise MemoryNotFoundError(memory_id)
                
        except Exception as e:
            logger.error(f"Get memory failed: {e}")
            return MemoryOperationResult.error_result(
                operation="get_memory",
                message=str(e),
                error_details={"exception_type": type(e).__name__}
            )
    
    @performance_monitor("update_memory")
    async def _handle_update_memory(self, arguments: Dict[str, Any]) -> MemoryOperationResult:
        """Handle update memory tool call"""
        
        try:
            memory_id = arguments["memory_id"]
            
            # Get existing memory
            memory = await self.storage_handler.get_memory(memory_id)
            if not memory:
                raise MemoryNotFoundError(memory_id)
            
            # Update fields
            updated = False
            if "content" in arguments:
                memory.content = arguments["content"]
                # Regenerate embedding for new content
                memory.embedding = await self.embedding_handler.generate_embedding(memory.content)
                updated = True
            
            if "summary" in arguments:
                memory.summary = arguments["summary"]
                updated = True
            
            if "priority" in arguments:
                memory.priority = MemoryPriority(arguments["priority"])
                updated = True
            
            if "tags" in arguments:
                memory.metadata.tags = arguments["tags"]
                updated = True
            
            if updated:
                memory.update_timestamp()
                success = await self.storage_handler.update_memory(memory)
                
                if success:
                    return MemoryOperationResult.success_result(
                        operation="update_memory",
                        memory_id=memory_id,
                        message="Memory updated successfully",
                        data={"memory": memory.dict()}
                    )
                else:
                    return MemoryOperationResult.error_result(
                        operation="update_memory",
                        message="Failed to update memory"
                    )
            else:
                return MemoryOperationResult.success_result(
                    operation="update_memory",
                    memory_id=memory_id,
                    message="No changes to update"
                )
                
        except Exception as e:
            logger.error(f"Update memory failed: {e}")
            return MemoryOperationResult.error_result(
                operation="update_memory",
                message=str(e),
                error_details={"exception_type": type(e).__name__}
            )
    
    @performance_monitor("delete_memory")
    async def _handle_delete_memory(self, arguments: Dict[str, Any]) -> MemoryOperationResult:
        """Handle delete memory tool call"""
        
        try:
            memory_id = arguments["memory_id"]
            permanent = arguments.get("permanent", False)
            
            success = await self.storage_handler.delete_memory(memory_id, permanent=permanent)
            
            if success:
                action = "permanently deleted" if permanent else "archived"
                return MemoryOperationResult.success_result(
                    operation="delete_memory",
                    memory_id=memory_id,
                    message=f"Memory {action} successfully"
                )
            else:
                return MemoryOperationResult.error_result(
                    operation="delete_memory",
                    message="Failed to delete memory"
                )
                
        except Exception as e:
            logger.error(f"Delete memory failed: {e}")
            return MemoryOperationResult.error_result(
                operation="delete_memory",
                message=str(e),
                error_details={"exception_type": type(e).__name__}
            )
    
    @performance_monitor("get_memory_stats")
    async def _handle_get_memory_stats(self, arguments: Dict[str, Any]) -> MemoryOperationResult:
        """Handle get memory stats tool call"""
        
        try:
            include_details = arguments.get("include_details", False)
            stats = await self.storage_handler.get_memory_statistics(include_details=include_details)
            
            return MemoryOperationResult.success_result(
                operation="get_memory_stats",
                message="Statistics retrieved successfully",
                data={"statistics": stats}
            )
            
        except Exception as e:
            logger.error(f"Get memory stats failed: {e}")
            return MemoryOperationResult.error_result(
                operation="get_memory_stats",
                message=str(e),
                error_details={"exception_type": type(e).__name__}
            )
    
    async def _get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        
        try:
            memory_stats = await self.storage_handler.get_memory_statistics(include_details=True)
            cache_stats = await self.semaphore_pool.get_active_operations()
            
            return {
                "memory_statistics": memory_stats,
                "active_operations": len(cache_stats),
                "available_slots": self.semaphore_pool.get_available_slots(),
                "server_config": {
                    "name": self.config.server_name,
                    "port": self.config.server_port,
                    "debug_mode": self.config.debug_mode,
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get system stats: {e}")
            return {"error": str(e)}
    
    async def _get_system_health(self) -> Dict[str, Any]:
        """Get system health status"""
        
        try:
            health_status = {
                "overall_status": "healthy",
                "components": {},
                "timestamp": str(asyncio.get_event_loop().time())
            }
            
            # Check storage handler
            try:
                await self.storage_handler.health_check()
                health_status["components"]["storage"] = "healthy"
            except Exception as e:
                health_status["components"]["storage"] = f"unhealthy: {e}"
                health_status["overall_status"] = "degraded"
            
            # Check embedding handler
            try:
                await self.embedding_handler.health_check()
                health_status["components"]["embedding"] = "healthy"
            except Exception as e:
                health_status["components"]["embedding"] = f"unhealthy: {e}"
                health_status["overall_status"] = "degraded"
            
            return health_status
            
        except Exception as e:
            logger.error(f"Failed to get system health: {e}")
            return {
                "overall_status": "error",
                "error": str(e),
                "timestamp": str(asyncio.get_event_loop().time())
            }
    
    async def start(self) -> None:
        """Start the MCP server"""
        
        logger.info(f"Starting AI Memory MCP Server on port {self.config.server_port}")
        
        # Initialize handlers
        await self.storage_handler.initialize()
        await self.embedding_handler.initialize()
        
        # Start the server
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name=self.config.server_name,
                    server_version="2.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None
                    )
                )
            )
    
    async def shutdown(self) -> None:
        """Shutdown the MCP server"""
        
        logger.info("Shutting down AI Memory MCP Server")
        
        # Cleanup handlers
        await self.storage_handler.cleanup()
        await self.embedding_handler.cleanup()


async def main():
    """Main entry point for the AI Memory MCP server"""
    
    try:
        config = get_config()
        server = AIMemoryMCPServer(config)
        await server.start()
        
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server failed: {e}")
        raise
    finally:
        if 'server' in locals():
            await server.shutdown()


if __name__ == "__main__":
    asyncio.run(main())

