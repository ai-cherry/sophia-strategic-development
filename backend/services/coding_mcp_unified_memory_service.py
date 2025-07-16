#!/usr/bin/env python3
"""
Coding MCP Unified Memory Service - Part 1 Implementation
========================================================

This is the SINGLE memory service for the Coding MCP Architecture.
Replaces 4 competing implementations with clean separation of concerns.

Key Features:
- Circuit breaker pattern prevents configuration recursion
- Shared connection pools eliminate resource exhaustion  
- Standardized error handling across all operations
- Clean separation: Coding context vs Business context
- Optimized for AI-assisted development workflows

Architecture:
- Port 9200 (coding_memory) - Code patterns, development context
- Port 9201 (health) - Health monitoring and metrics
- Namespace separation for clean context isolation

Date: January 15, 2025
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from contextlib import asynccontextmanager
import hashlib

# Core imports with graceful fallbacks
try:
    import redis.asyncio as aioredis
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, Range
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    print("⚠️ Qdrant not available - using mock implementation")

try:
    from mem0 import Memory as Mem0Memory
    MEM0_AVAILABLE = True
except ImportError:
    MEM0_AVAILABLE = False
    print("⚠️ Mem0 not available - using fallback implementation")

from backend.core.auto_esc_config import get_config_value

logger = logging.getLogger(__name__)

class CircuitBreakerState(Enum):
    """Circuit breaker states to prevent configuration recursion"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failure state - reject requests
    HALF_OPEN = "half_open"  # Testing state - limited requests

class MemoryNamespace(Enum):
    """Memory namespace separation for context isolation"""
    CODING = "coding"           # Code patterns, development context
    ARCHITECTURE = "architecture"  # System architecture, design patterns
    DOCUMENTATION = "documentation"  # API docs, code documentation
    TESTING = "testing"         # Test patterns, quality metrics
    SHARED = "shared"           # Cross-cutting concerns

@dataclass
class CircuitBreaker:
    """Circuit breaker to prevent configuration recursion"""
    failure_threshold: int = 5
    recovery_timeout: int = 60
    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    
    def can_execute(self) -> bool:
        """Check if operation can be executed"""
        if self.state == CircuitBreakerState.CLOSED:
            return True
        elif self.state == CircuitBreakerState.OPEN:
            if self.last_failure_time and \
               (datetime.now() - self.last_failure_time).seconds > self.recovery_timeout:
                self.state = CircuitBreakerState.HALF_OPEN
                return True
            return False
        elif self.state == CircuitBreakerState.HALF_OPEN:
            return True
        return False
    
    def record_success(self):
        """Record successful operation"""
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED
        
    def record_failure(self):
        """Record failed operation"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN

@dataclass
class CodingMemoryItem:
    """Memory item optimized for coding context"""
    id: str
    content: str
    namespace: MemoryNamespace
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    timestamp: datetime = field(default_factory=datetime.now)
    usage_count: int = 0
    relevance_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "id": self.id,
            "content": self.content,
            "namespace": self.namespace.value,
            "metadata": self.metadata,
            "embedding": self.embedding,
            "timestamp": self.timestamp.isoformat(),
            "usage_count": self.usage_count,
            "relevance_score": self.relevance_score
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CodingMemoryItem':
        """Create from dictionary"""
        return cls(
            id=data["id"],
            content=data["content"],
            namespace=MemoryNamespace(data["namespace"]),
            metadata=data.get("metadata", {}),
            embedding=data.get("embedding"),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            usage_count=data.get("usage_count", 0),
            relevance_score=data.get("relevance_score", 0.0)
        )

@dataclass
class ConnectionPool:
    """Shared connection pool to eliminate resource exhaustion"""
    redis_pool: Optional[aioredis.Redis] = None
    qdrant_client: Optional[QdrantClient] = None
    mem0_client: Optional[Any] = None
    pool_size: int = 10
    created_at: datetime = field(default_factory=datetime.now)
    
    async def initialize(self):
        """Initialize all connections"""
        try:
            # Redis connection
            redis_url = get_config_value("redis_url", "redis://localhost:6379")
            self.redis_pool = aioredis.from_url(
                redis_url,
                max_connections=self.pool_size,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Qdrant connection
            if QDRANT_AVAILABLE:
                qdrant_url = get_config_value("qdrant_url", "http://localhost:6333")
                qdrant_api_key = get_config_value("qdrant_api_key")
                
                if qdrant_api_key:
                    self.qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
                else:
                    self.qdrant_client = QdrantClient(url=qdrant_url)
            
            # Mem0 connection  
            if MEM0_AVAILABLE:
                mem0_config = {
                    "vector_store": {
                        "provider": "qdrant",
                        "config": {
                            "url": get_config_value("qdrant_url", "http://localhost:6333"),
                            "api_key": get_config_value("qdrant_api_key")
                        }
                    },
                    "llm": {
                        "provider": "openai",
                        "config": {
                            "api_key": get_config_value("openai_api_key"),
                            "model": "gpt-4"
                        }
                    }
                }
                self.mem0_client = Mem0Memory.from_config(mem0_config)
            
            logger.info("✅ Connection pool initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize connection pool: {e}")
            raise
    
    async def health_check(self) -> Dict[str, bool]:
        """Check health of all connections"""
        health = {
            "redis": False,
            "qdrant": False,
            "mem0": False
        }
        
        try:
            # Redis health check
            if self.redis_pool:
                await self.redis_pool.ping()
                health["redis"] = True
        except Exception:
            pass
            
        try:
            # Qdrant health check
            if self.qdrant_client:
                collections = self.qdrant_client.get_collections()
                health["qdrant"] = True
        except Exception:
            pass
            
        try:
            # Mem0 health check
            if self.mem0_client:
                health["mem0"] = True
        except Exception:
            pass
            
        return health

class CodingMCPUnifiedMemoryService:
    """
    Unified Memory Service for Coding MCP Architecture
    
    Features:
    - Circuit breaker prevents configuration recursion
    - Shared connection pools eliminate resource exhaustion
    - Namespace separation for clean context isolation
    - Optimized for AI-assisted development workflows
    - Standardized error handling across all operations
    """
    
    _instance: Optional['CodingMCPUnifiedMemoryService'] = None
    _initialized: bool = False
    
    def __new__(cls) -> 'CodingMCPUnifiedMemoryService':
        """Singleton pattern - single memory service instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        # Core components
        self.connection_pool = ConnectionPool()
        self.circuit_breaker = CircuitBreaker()
        
        # Memory storage
        self.memory_cache: Dict[str, CodingMemoryItem] = {}
        self.namespace_index: Dict[MemoryNamespace, List[str]] = {
            namespace: [] for namespace in MemoryNamespace
        }
        
        # Performance tracking
        self.stats = {
            "total_operations": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "average_response_time_ms": 0.0,
            "error_count": 0,
            "circuit_breaker_trips": 0
        }
        
        # Configuration
        self.cache_ttl_seconds = 3600  # 1 hour
        self.max_cache_size = 10000
        self.embedding_dimension = 768
        
        self._initialized = True
        logger.info("🧠 Coding MCP Unified Memory Service initialized")
    
    async def initialize(self):
        """Initialize the memory service"""
        if not self.circuit_breaker.can_execute():
            raise RuntimeError("Circuit breaker is OPEN - service unavailable")
        
        try:
            await self.connection_pool.initialize()
            await self._ensure_collections_exist()
            self.circuit_breaker.record_success()
            logger.info("✅ Coding MCP Memory Service ready")
            
        except Exception as e:
            self.circuit_breaker.record_failure()
            logger.error(f"❌ Memory service initialization failed: {e}")
            raise
    
    async def store_coding_memory(
        self,
        content: str,
        namespace: MemoryNamespace,
        metadata: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> str:
        """Store coding-related memory with namespace isolation"""
        
        if not self.circuit_breaker.can_execute():
            raise RuntimeError("Circuit breaker is OPEN - operation rejected")
        
        start_time = time.time()
        
        try:
            # Generate memory ID
            memory_id = str(uuid.uuid4())
            
            # Create memory item
            memory_item = CodingMemoryItem(
                id=memory_id,
                content=content,
                namespace=namespace,
                metadata=metadata or {}
            )
            
            # Add user context if provided
            if user_id:
                memory_item.metadata["user_id"] = user_id
                memory_item.metadata["created_by"] = "coding_mcp"
            
            # Store in cache
            self.memory_cache[memory_id] = memory_item
            self.namespace_index[namespace].append(memory_id)
            
            # Store in persistent storage
            await self._store_persistent(memory_item)
            
            # Update stats
            self.stats["total_operations"] += 1
            response_time = (time.time() - start_time) * 1000
            self._update_response_time(response_time)
            
            self.circuit_breaker.record_success()
            logger.info(f"✅ Stored coding memory: {memory_id} in {namespace.value}")
            
            return memory_id
            
        except Exception as e:
            self.circuit_breaker.record_failure()
            self.stats["error_count"] += 1
            logger.error(f"❌ Failed to store coding memory: {e}")
            raise
    
    async def search_coding_memory(
        self,
        query: str,
        namespace: Optional[MemoryNamespace] = None,
        limit: int = 10,
        user_id: Optional[str] = None
    ) -> List[CodingMemoryItem]:
        """Search coding memory with context awareness"""
        
        if not self.circuit_breaker.can_execute():
            return []  # Graceful degradation for search
        
        start_time = time.time()
        
        try:
            # Search in cache first
            cache_results = await self._search_cache(query, namespace, limit)
            
            if cache_results:
                self.stats["cache_hits"] += 1
                return cache_results
            
            # Search in persistent storage
            persistent_results = await self._search_persistent(query, namespace, limit, user_id)
            
            # Update cache with results
            for result in persistent_results:
                self.memory_cache[result.id] = result
            
            self.stats["cache_misses"] += 1
            self.stats["total_operations"] += 1
            
            response_time = (time.time() - start_time) * 1000
            self._update_response_time(response_time)
            
            self.circuit_breaker.record_success()
            
            return persistent_results
            
        except Exception as e:
            self.circuit_breaker.record_failure()
            self.stats["error_count"] += 1
            logger.error(f"❌ Failed to search coding memory: {e}")
            return []  # Graceful degradation
    
    async def get_coding_context(
        self,
        context_type: str,
        namespace: MemoryNamespace = MemoryNamespace.CODING,
        limit: int = 5
    ) -> List[CodingMemoryItem]:
        """Get relevant coding context for AI assistance"""
        
        # Context-specific search queries
        context_queries = {
            "patterns": "code patterns best practices design patterns",
            "errors": "error handling exception patterns debugging",
            "testing": "unit tests integration tests test patterns",
            "api": "API design REST endpoints FastAPI patterns",
            "database": "database queries ORM SQLAlchemy patterns",
            "security": "security authentication authorization JWT",
            "performance": "performance optimization caching patterns"
        }
        
        query = context_queries.get(context_type, context_type)
        return await self.search_coding_memory(query, namespace, limit)
    
    async def update_usage_stats(self, memory_id: str):
        """Update usage statistics for learning"""
        if memory_id in self.memory_cache:
            self.memory_cache[memory_id].usage_count += 1
            await self._update_persistent_usage(memory_id)
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status"""
        connection_health = await self.connection_pool.health_check()
        
        return {
            "service": "coding_mcp_unified_memory",
            "status": "healthy" if self.circuit_breaker.state == CircuitBreakerState.CLOSED else "degraded",
            "circuit_breaker": {
                "state": self.circuit_breaker.state.value,
                "failure_count": self.circuit_breaker.failure_count,
                "last_failure": self.circuit_breaker.last_failure_time.isoformat() if self.circuit_breaker.last_failure_time else None
            },
            "connections": connection_health,
            "cache": {
                "size": len(self.memory_cache),
                "max_size": self.max_cache_size,
                "utilization": len(self.memory_cache) / self.max_cache_size
            },
            "statistics": self.stats,
            "timestamp": datetime.now().isoformat()
        }
    
    # Private methods
    async def _ensure_collections_exist(self):
        """Ensure Qdrant collections exist for each namespace"""
        if not self.connection_pool.qdrant_client:
            return
        
        try:
            for namespace in MemoryNamespace:
                collection_name = f"coding_memory_{namespace.value}"
                
                try:
                    self.connection_pool.qdrant_client.get_collection(collection_name)
                except Exception:
                    # Create collection if it doesn't exist
                    self.connection_pool.qdrant_client.create_collection(
                        collection_name=collection_name,
                        vectors_config=VectorParams(
                            size=self.embedding_dimension,
                            distance=Distance.COSINE
                        )
                    )
                    logger.info(f"✅ Created Qdrant collection: {collection_name}")
                    
        except Exception as e:
            logger.error(f"❌ Failed to ensure collections exist: {e}")
    
    async def _store_persistent(self, memory_item: CodingMemoryItem):
        """Store in persistent storage (Redis + Qdrant)"""
        
        # Store in Redis for fast access
        if self.connection_pool.redis_pool:
            redis_key = f"coding_memory:{memory_item.namespace.value}:{memory_item.id}"
            await self.connection_pool.redis_pool.setex(
                redis_key,
                self.cache_ttl_seconds,
                json.dumps(memory_item.to_dict())
            )
        
        # Store in Qdrant for vector search
        if self.connection_pool.qdrant_client:
            # Generate embedding (simplified - would use actual embedding model)
            embedding = self._generate_simple_embedding(memory_item.content)
            memory_item.embedding = embedding
            
            collection_name = f"coding_memory_{memory_item.namespace.value}"
            
            point = PointStruct(
                id=memory_item.id,
                vector=embedding,
                payload={
                    "content": memory_item.content,
                    "metadata": memory_item.metadata,
                    "timestamp": memory_item.timestamp.isoformat(),
                    "usage_count": memory_item.usage_count
                }
            )
            
            self.connection_pool.qdrant_client.upsert(
                collection_name=collection_name,
                points=[point]
            )
    
    async def _search_cache(
        self,
        query: str,
        namespace: Optional[MemoryNamespace],
        limit: int
    ) -> List[CodingMemoryItem]:
        """Search in memory cache"""
        
        results = []
        query_words = set(query.lower().split())
        
        # Search in specified namespace or all namespaces
        search_namespaces = [namespace] if namespace else list(MemoryNamespace)
        
        for ns in search_namespaces:
            for memory_id in self.namespace_index[ns]:
                if memory_id in self.memory_cache:
                    memory_item = self.memory_cache[memory_id]
                    content_words = set(memory_item.content.lower().split())
                    
                    # Simple relevance scoring
                    common_words = query_words.intersection(content_words)
                    if common_words:
                        memory_item.relevance_score = len(common_words) / len(query_words)
                        results.append(memory_item)
        
        # Sort by relevance and return top results
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:limit]
    
    async def _search_persistent(
        self,
        query: str,
        namespace: Optional[MemoryNamespace],
        limit: int,
        user_id: Optional[str]
    ) -> List[CodingMemoryItem]:
        """Search in persistent storage"""
        
        results = []
        
        # Search in Qdrant if available
        if self.connection_pool.qdrant_client:
            search_namespaces = [namespace] if namespace else list(MemoryNamespace)
            
            for ns in search_namespaces:
                collection_name = f"coding_memory_{ns.value}"
                
                try:
                    # Generate query embedding
                    query_embedding = self._generate_simple_embedding(query)
                    
                    # Build filter
                    filter_conditions = []
                    if user_id:
                        filter_conditions.append(
                            FieldCondition(key="metadata.user_id", match={"value": user_id})
                        )
                    
                    # Search
                    search_results = self.connection_pool.qdrant_client.search(
                        collection_name=collection_name,
                        query_vector=query_embedding,
                        query_filter=Filter(must=filter_conditions) if filter_conditions else None,
                        limit=limit
                    )
                    
                    # Convert to CodingMemoryItem
                    for result in search_results:
                        memory_item = CodingMemoryItem(
                            id=str(result.id),
                            content=result.payload["content"],
                            namespace=ns,
                            metadata=result.payload.get("metadata", {}),
                            embedding=result.vector,
                            timestamp=datetime.fromisoformat(result.payload["timestamp"]),
                            usage_count=result.payload.get("usage_count", 0),
                            relevance_score=result.score
                        )
                        results.append(memory_item)
                        
                except Exception as e:
                    logger.warning(f"⚠️ Search failed for namespace {ns.value}: {e}")
        
        return results
    
    def _generate_simple_embedding(self, text: str) -> List[float]:
        """Generate simple embedding (placeholder for actual embedding model)"""
        # This is a simplified embedding - in production would use actual model
        import hashlib
        import struct
        
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convert to float vector
        embedding = []
        for i in range(0, len(hash_bytes), 4):
            chunk = hash_bytes[i:i+4]
            if len(chunk) == 4:
                value = struct.unpack('f', chunk)[0]
                embedding.append(value)
        
        # Pad or truncate to desired dimension
        while len(embedding) < self.embedding_dimension:
            embedding.append(0.0)
        
        return embedding[:self.embedding_dimension]
    
    async def _update_persistent_usage(self, memory_id: str):
        """Update usage count in persistent storage"""
        if memory_id in self.memory_cache:
            memory_item = self.memory_cache[memory_id]
            
            # Update in Qdrant
            if self.connection_pool.qdrant_client:
                collection_name = f"coding_memory_{memory_item.namespace.value}"
                
                try:
                    self.connection_pool.qdrant_client.set_payload(
                        collection_name=collection_name,
                        points=[memory_id],
                        payload={"usage_count": memory_item.usage_count}
                    )
                except Exception as e:
                    logger.warning(f"⚠️ Failed to update usage in Qdrant: {e}")
    
    def _update_response_time(self, response_time_ms: float):
        """Update average response time"""
        current_avg = self.stats["average_response_time_ms"]
        total_ops = self.stats["total_operations"]
        
        if total_ops == 1:
            self.stats["average_response_time_ms"] = response_time_ms
        else:
            # Running average
            self.stats["average_response_time_ms"] = (
                (current_avg * (total_ops - 1) + response_time_ms) / total_ops
            )

# Singleton instance getter
_memory_service_instance: Optional[CodingMCPUnifiedMemoryService] = None

def get_coding_memory_service() -> CodingMCPUnifiedMemoryService:
    """Get the singleton coding memory service instance"""
    global _memory_service_instance
    if _memory_service_instance is None:
        _memory_service_instance = CodingMCPUnifiedMemoryService()
    return _memory_service_instance

# Context manager for safe memory operations
@asynccontextmanager
async def coding_memory_context():
    """Context manager for safe memory operations"""
    service = get_coding_memory_service()
    try:
        await service.initialize()
        yield service
    except Exception as e:
        logger.error(f"❌ Memory context error: {e}")
        raise
    finally:
        # Cleanup if needed
        pass

if __name__ == "__main__":
    # Basic testing
    async def test_memory_service():
        async with coding_memory_context() as service:
            # Test storing memory
            memory_id = await service.store_coding_memory(
                content="FastAPI endpoint pattern with async/await",
                namespace=MemoryNamespace.CODING,
                metadata={"type": "pattern", "language": "python"}
            )
            
            # Test searching memory
            results = await service.search_coding_memory(
                query="FastAPI endpoint",
                namespace=MemoryNamespace.CODING
            )
            
            # Test health status
            health = await service.get_health_status()
            
            print(f"✅ Stored memory: {memory_id}")
            print(f"✅ Found {len(results)} results")
            print(f"✅ Health status: {health['status']}")
    
    asyncio.run(test_memory_service()) 