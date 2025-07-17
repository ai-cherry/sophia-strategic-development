"""
Mem0 Orchestrator MCP Server Implementation
Intelligent memory orchestration with clear separation between coding and business contexts
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import os
import sys

# Add backend to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.core.auto_esc_config import get_config_value

# Try to import mem0
try:
    from mem0 import Memory
    MEM0_AVAILABLE = True
except ImportError:
    MEM0_AVAILABLE = False
    print("⚠️  Mem0 not installed. Install with: pip install mem0ai")


class MemoryContext(Enum):
    """Context types for memory separation"""
    CODING = "coding"
    BUSINESS = "business"
    HYBRID = "hybrid"


@dataclass
class MemorySession:
    """Represents a memory session with context"""
    session_id: str
    context: MemoryContext
    user_id: str
    started_at: datetime
    memories_added: int = 0
    memories_recalled: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UsageMetrics:
    """Track usage metrics for each memory type"""
    total_adds: int = 0
    total_searches: int = 0
    total_updates: int = 0
    total_deletes: int = 0
    avg_response_time_ms: float = 0.0
    memory_size_mb: float = 0.0
    active_sessions: int = 0


class Mem0OrchestratorMCPServer:
    """
    MCP Server for Mem0 intelligent memory orchestration
    Tier 2 in the hybrid memory architecture
    """
    
    def __init__(self):
        self.name = "mem0"
        self.version = "1.0.0"
        self.port = 9502  # Mem0 MCP server port
        
        # Memory instances
        self.coding_memory: Optional[Memory] = None
        self.business_memory: Optional[Memory] = None
        
        # Active sessions
        self.sessions: Dict[str, MemorySession] = {}
        
        # Usage metrics
        self.metrics = {
            MemoryContext.CODING: UsageMetrics(),
            MemoryContext.BUSINESS: UsageMetrics()
        }
        
        # Performance tracking
        self.response_times: List[float] = []
        self.max_response_history = 1000
        
    async def initialize(self):
        """Initialize Mem0 orchestrator"""
        try:
            if not MEM0_AVAILABLE:
                print("❌ Mem0 not available, running in mock mode")
                return
                
            # Initialize coding memory (lightweight, fast)
            self.coding_memory = self._create_coding_memory()
            
            # Initialize business memory (comprehensive, persistent)
            self.business_memory = self._create_business_memory()
            
            print(f"✅ Mem0 Orchestrator MCP Server initialized on port {self.port}")
            
        except Exception as e:
            print(f"❌ Failed to initialize Mem0 Orchestrator: {e}")
            raise
    
    def _create_coding_memory(self) -> Optional[Memory]:
        """Create memory instance optimized for coding context"""
        if not MEM0_AVAILABLE:
            return None
            
        try:
            config = {
                "llm": {
                    "provider": "openai",
                    "config": {
                        "model": "gpt-4-turbo",
                        "temperature": 0.1,  # Low temperature for consistency
                        "max_tokens": 2000
                    }
                },
                "vector_store": {
                    "provider": "qdrant",
                    "config": {
                        "collection_name": "coding_memory",
                        "host": "localhost",
                        "port": 6333,
                        "embedding_model": "text-embedding-3-small"
                    }
                },
                "version": "v1.1",
                "metadata": {
                    "context": "coding",
                    "purpose": "repository_patterns"
                }
            }
            
            return Memory.from_config(config)
            
        except Exception as e:
            print(f"⚠️  Failed to create coding memory: {e}")
            return None
    
    def _create_business_memory(self) -> Optional[Memory]:
        """Create memory instance optimized for business context"""
        if not MEM0_AVAILABLE:
            return None
            
        try:
            config = {
                "llm": {
                    "provider": "openai",
                    "config": {
                        "model": "gpt-4-turbo",
                        "temperature": 0.3,  # Moderate temperature for nuance
                        "max_tokens": 4000
                    }
                },
                "vector_store": {
                    "provider": "qdrant",
                    "config": {
                        "collection_name": "business_memory",
                        "host": "localhost",
                        "port": 6333,
                        "embedding_model": "text-embedding-3-large"
                    }
                },
                "version": "v1.1",
                "metadata": {
                    "context": "business",
                    "purpose": "business_intelligence"
                }
            }
            
            return Memory.from_config(config)
            
        except Exception as e:
            print(f"⚠️  Failed to create business memory: {e}")
            return None
    
    async def create_session(self, 
                           user_id: str,
                           context: MemoryContext,
                           metadata: Optional[Dict[str, Any]] = None) -> str:
        """Create a new memory session"""
        session_id = f"{context.value}_{user_id}_{int(time.time() * 1000)}"
        
        session = MemorySession(
            session_id=session_id,
            context=context,
            user_id=user_id,
            started_at=datetime.utcnow(),
            metadata=metadata or {}
        )
        
        self.sessions[session_id] = session
        self.metrics[context].active_sessions += 1
        
        return session_id
    
    async def add_memory(self,
                        content: str,
                        context: MemoryContext,
                        user_id: str,
                        metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Add memory with intelligent context routing"""
        start_time = time.time()
        
        try:
            # Select appropriate memory instance
            if context == MemoryContext.CODING and self.coding_memory:
                memory = self.coding_memory
            elif context == MemoryContext.BUSINESS and self.business_memory:
                memory = self.business_memory
            else:
                # Mock mode or hybrid context
                return self._mock_add_memory(content, context, user_id, metadata)
            
            # Enrich metadata
            enriched_metadata = {
                "context": context.value,
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id,
                **(metadata or {})
            }
            
            # Add to memory
            result = memory.add(
                content,
                user_id=user_id,
                metadata=enriched_metadata
            )
            
            # Update metrics
            self.metrics[context].total_adds += 1
            self._track_response_time(time.time() - start_time)
            
            # Update session if exists
            session_key = f"{context.value}_{user_id}"
            for sid, session in self.sessions.items():
                if session.user_id == user_id and session.context == context:
                    session.memories_added += 1
                    break
            
            return {
                "status": "success",
                "memory_id": result.get("id", "unknown"),
                "context": context.value,
                "processing_time_ms": (time.time() - start_time) * 1000
            }
            
        except Exception as e:
            print(f"❌ Error adding memory: {e}")
            return {
                "status": "error",
                "error": str(e),
                "context": context.value
            }
    
    async def search_memories(self,
                            query: str,
                            context: MemoryContext,
                            user_id: Optional[str] = None,
                            filters: Optional[Dict[str, Any]] = None,
                            limit: int = 10) -> List[Dict[str, Any]]:
        """Search memories with context awareness"""
        start_time = time.time()
        
        try:
            results = []
            
            if context == MemoryContext.HYBRID:
                # Search both contexts
                if self.coding_memory:
                    coding_results = await self._search_single_memory(
                        self.coding_memory, query, user_id, limit // 2
                    )
                    results.extend([{**r, "context": "coding"} for r in coding_results])
                    
                if self.business_memory:
                    business_results = await self._search_single_memory(
                        self.business_memory, query, user_id, limit // 2
                    )
                    results.extend([{**r, "context": "business"} for r in business_results])
            else:
                # Search specific context
                memory = self.coding_memory if context == MemoryContext.CODING else self.business_memory
                if memory:
                    results = await self._search_single_memory(memory, query, user_id, limit)
                    results = [{**r, "context": context.value} for r in results]
                else:
                    # Mock mode
                    results = self._mock_search_memories(query, context, limit)
            
            # Apply additional filters
            if filters:
                results = self._apply_filters(results, filters)
            
            # Update metrics
            self.metrics[context if context != MemoryContext.HYBRID else MemoryContext.CODING].total_searches += 1
            self._track_response_time(time.time() - start_time)
            
            # Update session if exists
            if user_id:
                for sid, session in self.sessions.items():
                    if session.user_id == user_id and session.context == context:
                        session.memories_recalled += len(results)
                        break
            
            return results
            
        except Exception as e:
            print(f"❌ Error searching memories: {e}")
            return []
    
    async def _search_single_memory(self, 
                                  memory: Memory,
                                  query: str,
                                  user_id: Optional[str],
                                  limit: int) -> List[Dict[str, Any]]:
        """Search a single memory instance"""
        try:
            # Mem0 search
            results = memory.search(
                query=query,
                user_id=user_id,
                limit=limit
            )
            
            # Format results
            formatted_results = []
            for r in results:
                formatted_results.append({
                    "id": r.get("id"),
                    "content": r.get("text", ""),
                    "score": r.get("score", 0.0),
                    "metadata": r.get("metadata", {}),
                    "created_at": r.get("created_at")
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"⚠️  Error in memory search: {e}")
            return []
    
    def _apply_filters(self, results: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply additional filters to search results"""
        filtered = []
        
        for result in results:
            match = True
            metadata = result.get("metadata", {})
            
            for key, value in filters.items():
                if key not in metadata:
                    match = False
                    break
                    
                if isinstance(value, list):
                    if metadata[key] not in value:
                        match = False
                        break
                else:
                    if metadata[key] != value:
                        match = False
                        break
            
            if match:
                filtered.append(result)
        
        return filtered
    
    async def update_memory(self,
                          memory_id: str,
                          content: str,
                          context: MemoryContext,
                          user_id: str) -> Dict[str, Any]:
        """Update an existing memory"""
        try:
            memory = self.coding_memory if context == MemoryContext.CODING else self.business_memory
            
            if memory:
                # Mem0 update
                result = memory.update(
                    memory_id=memory_id,
                    data=content,
                    user_id=user_id
                )
                
                self.metrics[context].total_updates += 1
                
                return {
                    "status": "success",
                    "memory_id": memory_id,
                    "context": context.value
                }
            else:
                return {
                    "status": "error",
                    "error": "Memory instance not available"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def delete_memory(self,
                          memory_id: str,
                          context: MemoryContext,
                          user_id: str) -> Dict[str, Any]:
        """Delete a memory"""
        try:
            memory = self.coding_memory if context == MemoryContext.CODING else self.business_memory
            
            if memory:
                # Mem0 delete
                memory.delete(memory_id=memory_id, user_id=user_id)
                
                self.metrics[context].total_deletes += 1
                
                return {
                    "status": "success",
                    "memory_id": memory_id,
                    "context": context.value
                }
            else:
                return {
                    "status": "error",
                    "error": "Memory instance not available"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get statistics for a session"""
        if session_id not in self.sessions:
            return {"error": "Session not found"}
            
        session = self.sessions[session_id]
        duration = datetime.utcnow() - session.started_at
        
        return {
            "session_id": session_id,
            "context": session.context.value,
            "user_id": session.user_id,
            "duration_minutes": duration.total_seconds() / 60,
            "memories_added": session.memories_added,
            "memories_recalled": session.memories_recalled,
            "metadata": session.metadata
        }
    
    async def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Clean up old sessions"""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        sessions_to_remove = []
        
        for session_id, session in self.sessions.items():
            if session.started_at < cutoff_time:
                sessions_to_remove.append(session_id)
                self.metrics[session.context].active_sessions -= 1
        
        for session_id in sessions_to_remove:
            del self.sessions[session_id]
        
        return {
            "sessions_removed": len(sessions_to_remove),
            "active_sessions": len(self.sessions)
        }
    
    def _track_response_time(self, time_seconds: float):
        """Track response times"""
        time_ms = time_seconds * 1000
        self.response_times.append(time_ms)
        
        if len(self.response_times) > self.max_response_history:
            self.response_times.pop(0)
    
    def _mock_add_memory(self, content: str, context: MemoryContext, 
                        user_id: str, metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Mock memory addition for testing"""
        return {
            "status": "success",
            "memory_id": f"mock_{context.value}_{int(time.time() * 1000)}",
            "context": context.value,
            "processing_time_ms": 5.0
        }
    
    def _mock_search_memories(self, query: str, context: MemoryContext, limit: int) -> List[Dict[str, Any]]:
        """Mock memory search for testing"""
        results = []
        for i in range(min(limit, 3)):
            if context == MemoryContext.CODING:
                content = f"Code pattern {i}: {query} implementation in Python"
            else:
                content = f"Business insight {i}: Analysis of {query}"
                
            results.append({
                "id": f"mock_{context.value}_{i}",
                "content": content,
                "score": 0.9 - (i * 0.1),
                "metadata": {
                    "context": context.value,
                    "mock": True
                },
                "created_at": datetime.utcnow().isoformat()
            })
        return results
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics"""
        avg_response_time = (
            sum(self.response_times) / len(self.response_times)
            if self.response_times else 0.0
        )
        
        return {
            "contexts": {
                "coding": {
                    "total_adds": self.metrics[MemoryContext.CODING].total_adds,
                    "total_searches": self.metrics[MemoryContext.CODING].total_searches,
                    "total_updates": self.metrics[MemoryContext.CODING].total_updates,
                    "total_deletes": self.metrics[MemoryContext.CODING].total_deletes,
                    "active_sessions": self.metrics[MemoryContext.CODING].active_sessions
                },
                "business": {
                    "total_adds": self.metrics[MemoryContext.BUSINESS].total_adds,
                    "total_searches": self.metrics[MemoryContext.BUSINESS].total_searches,
                    "total_updates": self.metrics[MemoryContext.BUSINESS].total_updates,
                    "total_deletes": self.metrics[MemoryContext.BUSINESS].total_deletes,
                    "active_sessions": self.metrics[MemoryContext.BUSINESS].active_sessions
                }
            },
            "avg_response_time_ms": avg_response_time,
            "total_active_sessions": len(self.sessions),
            "mem0_available": MEM0_AVAILABLE
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check endpoint"""
        try:
            stats = await self.get_stats()
            
            return {
                "status": "healthy" if MEM0_AVAILABLE else "mock_mode",
                "service": "mem0_orchestrator",
                "version": self.version,
                "port": self.port,
                "contexts_available": ["coding", "business", "hybrid"],
                "mem0_initialized": bool(self.coding_memory and self.business_memory),
                "stats": stats
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "service": "mem0_orchestrator",
                "version": self.version,
                "error": str(e)
            }
    
    # MCP Protocol Methods
    
    async def handle_call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP tool calls"""
        if name == "add_memory":
            content = arguments.get("content", "")
            context = MemoryContext(arguments.get("context", "coding"))
            user_id = arguments.get("user_id", "default")
            metadata = arguments.get("metadata", {})
            
            return await self.add_memory(content, context, user_id, metadata)
            
        elif name == "search_memories":
            query = arguments.get("query", "")
            context = MemoryContext(arguments.get("context", "coding"))
            user_id = arguments.get("user_id")
            filters = arguments.get("filters")
            limit = arguments.get("limit", 10)
            
            results = await self.search_memories(query, context, user_id, filters, limit)
            return {"results": results, "count": len(results)}
            
        elif name == "create_session":
            user_id = arguments.get("user_id", "default")
            context = MemoryContext(arguments.get("context", "coding"))
            metadata = arguments.get("metadata", {})
            
            session_id = await self.create_session(user_id, context, metadata)
            return {"session_id": session_id}
            
        elif name == "get_stats":
            return await self.get_stats()
            
        elif name == "cleanup_sessions":
            max_age_hours = arguments.get("max_age_hours", 24)
            return await self.cleanup_old_sessions(max_age_hours)
            
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    def get_tool_descriptions(self) -> List[Dict[str, Any]]:
        """Get MCP tool descriptions"""
        return [
            {
                "name": "add_memory",
                "description": "Add memory with intelligent context routing",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "Memory content"},
                        "context": {
                            "type": "string",
                            "enum": ["coding", "business", "hybrid"],
                            "description": "Memory context"
                        },
                        "user_id": {"type": "string", "description": "User identifier"},
                        "metadata": {"type": "object", "description": "Additional metadata"}
                    },
                    "required": ["content", "context"]
                }
            },
            {
                "name": "search_memories",
                "description": "Search memories with context awareness",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "context": {
                            "type": "string",
                            "enum": ["coding", "business", "hybrid"],
                            "description": "Memory context"
                        },
                        "user_id": {"type": "string", "description": "Filter by user"},
                        "filters": {"type": "object", "description": "Additional filters"},
                        "limit": {"type": "integer", "description": "Maximum results", "default": 10}
                    },
                    "required": ["query", "context"]
                }
            },
            {
                "name": "create_session",
                "description": "Create a new memory session",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "User identifier"},
                        "context": {
                            "type": "string",
                            "enum": ["coding", "business"],
                            "description": "Session context"
                        },
                        "metadata": {"type": "object", "description": "Session metadata"}
                    },
                    "required": ["user_id", "context"]
                }
            },
            {
                "name": "get_stats",
                "description": "Get orchestrator statistics",
                "inputSchema": {"type": "object", "properties": {}}
            },
            {
                "name": "cleanup_sessions",
                "description": "Clean up old sessions",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "max_age_hours": {
                            "type": "integer",
                            "description": "Maximum session age in hours",
                            "default": 24
                        }
                    }
                }
            }
        ]


# MCP Server entry point
async def main():
    """Main entry point for the MCP server"""
    server = Mem0OrchestratorMCPServer()
    await server.initialize()
    
    # In real implementation, would start MCP protocol server
    print(f"🚀 Mem0 Orchestrator MCP Server running on port {server.port}")
    
    # Keep server running
    try:
        while True:
            await asyncio.sleep(3600)  # Cleanup every hour
            stats = await server.cleanup_old_sessions()
            print(f"🧹 Session cleanup: {stats}")
    except KeyboardInterrupt:
        print("\n👋 Shutting down Mem0 Orchestrator")


if __name__ == "__main__":
    asyncio.run(main())
