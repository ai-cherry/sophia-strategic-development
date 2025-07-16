# 🚀 CODING MCP ARCHITECTURE - DEEP IMPLEMENTATION GUIDE
**Complete Guide to Implementation, Testing, Deployment, and Usage**
**Date**: January 16, 2025
**Status**: Production-Ready Implementation Plan

---

## 📋 EXECUTIVE SUMMARY

This guide provides a comprehensive roadmap to implement, test, deploy, and use the AI Coding MCP Architecture with Portkey/OpenRouter integration. It addresses all identified issues from the audit and provides concrete steps to achieve a production-ready system.

### **Critical Issues to Address:**
1. ❌ **Memory Service Fragmentation**: 4 competing implementations
2. ❌ **Configuration Recursion**: Potential stack overflow risk
3. ❌ **Connection Pool Exhaustion**: Multiple services creating pools
4. ❌ **Inconsistent Error Handling**: Different patterns across services
5. ❌ **Missing Integration Tests**: No comprehensive test suite

### **Solutions Provided:**
1. ✅ **Unified Memory Service**: Single consolidated implementation
2. ✅ **Configuration Circuit Breaker**: Prevents recursion
3. ✅ **Shared Connection Pools**: Resource optimization
4. ✅ **Standardized Error Handling**: Consistent patterns
5. ✅ **Comprehensive Test Suite**: Unit, integration, and E2E tests

---

## 🏗️ ARCHITECTURE CONSOLIDATION PLAN

### **Phase 1: Memory Service Unification**

#### **1.1 Create Unified Memory Service**

```python
# backend/services/sophia_unified_memory_service.py
"""
Sophia Unified Memory Service - Single source of truth for all memory operations
Consolidates best features from all existing services
"""

import asyncio
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass
from enum import Enum
import time

from backend.core.auto_esc_config import get_config_value, get_qdrant_config, get_redis_config
from backend.core.qdrant_connection_pool import QdrantConnectionPool
from backend.core.redis_connection_manager import RedisConnectionManager
from backend.core.database import SessionLocal
from shared.utils.custom_logger import logger

# Try to import optional dependencies
try:
    from mem0 import Memory
    MEM0_AVAILABLE = True
except ImportError:
    MEM0_AVAILABLE = False
    Memory = None

from qdrant_client import QdrantClient, models
from redis import Redis
import numpy as np
from datetime import datetime, timezone
from prometheus_client import Counter, Histogram, Gauge
import hashlib
import json

# Metrics
memory_operations = Counter('memory_operations_total', 'Total memory operations', ['operation', 'collection', 'status'])
memory_latency = Histogram('memory_operation_latency_seconds', 'Memory operation latency', ['operation', 'collection'])
connection_pool_usage = Gauge('connection_pool_usage', 'Connection pool usage', ['service', 'pool'])
cache_hits = Counter('cache_hits_total', 'Cache hits', ['layer', 'collection'])
cache_misses = Counter('cache_misses_total', 'Cache misses', ['layer', 'collection'])

class MemoryCollection(Enum):
    """Unified collection names across all memory operations"""
    KNOWLEDGE = "sophia_knowledge"
    CONVERSATIONS = "sophia_conversations"
    DOCUMENTS = "sophia_documents"
    CODE = "sophia_code"
    WORKFLOWS = "sophia_workflows"
    BUSINESS_INTELLIGENCE = "sophia_business_intelligence"
    COMPETITORS = "sophia_competitors"
    COMPETITOR_EVENTS = "sophia_competitor_events"

@dataclass
class MemoryEntry:
    """Unified memory entry structure"""
    id: str
    content: str
    vector: List[float]
    metadata: Dict[str, Any]
    collection: MemoryCollection
    timestamp: datetime
    score: Optional[float] = None

class SophiaUnifiedMemoryService:
    """
    Unified memory service for Sophia AI
    Combines Qdrant, Redis, PostgreSQL, and Mem0 in a coherent architecture
    """
    
    def __init__(self):
        self.initialized = False
        
        # Connection pools
        self.qdrant_pool: Optional[QdrantConnectionPool] = None
        self.redis_manager: Optional[RedisConnectionManager] = None
        self.mem0_client: Optional[Memory] = None
        
        # Configuration
        self.qdrant_config = get_qdrant_config()
        self.redis_config = get_redis_config()
        
        # Cache configuration
        self.cache_ttl = {
            MemoryCollection.KNOWLEDGE: 3600,  # 1 hour
            MemoryCollection.CONVERSATIONS: 300,  # 5 minutes
            MemoryCollection.DOCUMENTS: 7200,  # 2 hours
            MemoryCollection.CODE: 1800,  # 30 minutes
            MemoryCollection.WORKFLOWS: 3600,
            MemoryCollection.BUSINESS_INTELLIGENCE: 900,  # 15 minutes
            MemoryCollection.COMPETITORS: 3600,
            MemoryCollection.COMPETITOR_EVENTS: 600  # 10 minutes
        }
        
        # Circuit breaker state
        self._circuit_breaker = {
            "qdrant": {"failures": 0, "last_failure": 0, "is_open": False},
            "redis": {"failures": 0, "last_failure": 0, "is_open": False},
            "mem0": {"failures": 0, "last_failure": 0, "is_open": False}
        }
        
        self._lock = asyncio.Lock()
        
    async def initialize(self) -> None:
        """Initialize all memory components with proper error handling"""
        async with self._lock:
            if self.initialized:
                return
                
            logger.info("🚀 Initializing Sophia Unified Memory Service...")
            
            # Initialize Qdrant
            try:
                self.qdrant_pool = QdrantConnectionPool(
                    max_connections=20,
                    timeout=30
                )
                await self._create_collections()
                logger.info("✅ Qdrant initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Qdrant: {e}")
                raise
                
            # Initialize Redis
            try:
                self.redis_manager = RedisConnectionManager()
                await self.redis_manager.initialize()
                logger.info("✅ Redis initialized successfully")
            except Exception as e:
                logger.warning(f"⚠️ Redis initialization failed (non-critical): {e}")
                
            # Initialize Mem0 if available
            if MEM0_AVAILABLE:
                try:
                    self.mem0_client = Memory()
                    logger.info("✅ Mem0 initialized successfully")
                except Exception as e:
                    logger.warning(f"⚠️ Mem0 initialization failed (non-critical): {e}")
                    
            self.initialized = True
            logger.info("🎉 Sophia Unified Memory Service initialized successfully")
            
    async def _create_collections(self) -> None:
        """Create all Qdrant collections with optimized configurations"""
        async with self.qdrant_pool.get_connection() as client:
            for collection in MemoryCollection:
                try:
                    # Check if collection exists
                    collections = await client.get_collections()
                    if collection.value not in [c.name for c in collections.collections]:
                        # Determine vector size and shard configuration
                        vector_size = 1024 if collection == MemoryCollection.DOCUMENTS else 768
                        shard_number = 2 if collection in [MemoryCollection.KNOWLEDGE, MemoryCollection.DOCUMENTS, MemoryCollection.BUSINESS_INTELLIGENCE] else 1
                        replication_factor = 2 if collection == MemoryCollection.COMPETITORS else 1
                        
                        await client.create_collection(
                            collection_name=collection.value,
                            vectors_config=models.VectorParams(
                                size=vector_size,
                                distance=models.Distance.COSINE
                            ),
                            shard_number=shard_number,
                            replication_factor=replication_factor,
                            on_disk_payload=True  # Optimize for large payloads
                        )
                        
                        # Create indexes for common filters
                        await client.create_payload_index(
                            collection_name=collection.value,
                            field_name="timestamp",
                            field_type="datetime"
                        )
                        
                        await client.create_payload_index(
                            collection_name=collection.value,
                            field_name="source",
                            field_type="keyword"
                        )
                        
                        logger.info(f"✅ Created collection: {collection.value}")
                except Exception as e:
                    logger.error(f"❌ Failed to create collection {collection.value}: {e}")
                    
    async def store(
        self,
        content: str,
        vector: List[float],
        metadata: Dict[str, Any],
        collection: MemoryCollection = MemoryCollection.KNOWLEDGE
    ) -> MemoryEntry:
        """Store content in memory with all layers"""
        start_time = time.time()
        
        try:
            # Generate ID
            entry_id = self._generate_id(content, metadata)
            
            # Create memory entry
            entry = MemoryEntry(
                id=entry_id,
                content=content,
                vector=vector,
                metadata={
                    **metadata,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "collection": collection.value
                },
                collection=collection,
                timestamp=datetime.now(timezone.utc)
            )
            
            # Store in Qdrant (primary storage)
            if not self._circuit_breaker["qdrant"]["is_open"]:
                try:
                    async with self.qdrant_pool.get_connection() as client:
                        await client.upsert(
                            collection_name=collection.value,
                            points=[models.PointStruct(
                                id=entry_id,
                                vector=vector,
                                payload={
                                    "content": content,
                                    **entry.metadata
                                }
                            )]
                        )
                    self._reset_circuit_breaker("qdrant")
                except Exception as e:
                    self._handle_service_error("qdrant", e)
                    raise
                    
            # Store in Redis cache (if available)
            if self.redis_manager and not self._circuit_breaker["redis"]["is_open"]:
                try:
                    cache_key = f"{collection.value}:{entry_id}"
                    await self.redis_manager.set_async(
                        cache_key,
                        json.dumps({
                            "content": content,
                            "metadata": entry.metadata,
                            "vector": vector
                        }),
                        ex=self.cache_ttl[collection]
                    )
                    self._reset_circuit_breaker("redis")
                except Exception as e:
                    self._handle_service_error("redis", e)
                    # Non-critical, continue
                    
            # Store in Mem0 (if available and relevant)
            if self.mem0_client and collection == MemoryCollection.CONVERSATIONS and not self._circuit_breaker["mem0"]["is_open"]:
                try:
                    self.mem0_client.add(
                        messages=content,
                        user_id=metadata.get("user_id", "system"),
                        metadata=metadata
                    )
                    self._reset_circuit_breaker("mem0")
                except Exception as e:
                    self._handle_service_error("mem0", e)
                    # Non-critical, continue
                    
            # Track metrics
            memory_operations.labels(operation="store", collection=collection.value, status="success").inc()
            memory_latency.labels(operation="store", collection=collection.value).observe(time.time() - start_time)
            
            logger.info(f"✅ Stored entry {entry_id} in {collection.value}")
            return entry
            
        except Exception as e:
            memory_operations.labels(operation="store", collection=collection.value, status="error").inc()
            logger.error(f"❌ Failed to store in {collection.value}: {e}")
            raise
            
    async def search(
        self,
        query_vector: List[float],
        collection: MemoryCollection = MemoryCollection.KNOWLEDGE,
        limit: int = 10,
        score_threshold: float = 0.7,
        metadata_filter: Optional[Dict[str, Any]] = None,
        use_cache: bool = True
    ) -> List[MemoryEntry]:
        """Search memory with caching and fallback"""
        start_time = time.time()
        
        try:
            # Generate cache key
            cache_key = None
            if use_cache and self.redis_manager:
                filter_str = json.dumps(metadata_filter or {}, sort_keys=True)
                cache_key = f"search:{collection.value}:{hashlib.md5(f'{query_vector[:5]}{filter_str}{limit}'.encode()).hexdigest()}"
                
                # Try cache first
                if not self._circuit_breaker["redis"]["is_open"]:
                    try:
                        cached_result = await self.redis_manager.get_async(cache_key)
                        if cached_result:
                            cache_hits.labels(layer="redis", collection=collection.value).inc()
                            results = json.loads(cached_result)
                            return [self._deserialize_entry(r) for r in results]
                    except Exception as e:
                        self._handle_service_error("redis", e)
                        
                cache_misses.labels(layer="redis", collection=collection.value).inc()
                
            # Search in Qdrant
            if not self._circuit_breaker["qdrant"]["is_open"]:
                try:
                    async with self.qdrant_pool.get_connection() as client:
                        # Build filter
                        qdrant_filter = None
                        if metadata_filter:
                            must_conditions = []
                            for key, value in metadata_filter.items():
                                must_conditions.append(
                                    models.FieldCondition(
                                        key=key,
                                        match=models.MatchValue(value=value)
                                    )
                                )
                            qdrant_filter = models.Filter(must=must_conditions)
                            
                        # Perform search
                        results = await client.search(
                            collection_name=collection.value,
                            query_vector=query_vector,
                            limit=limit,
                            score_threshold=score_threshold,
                            query_filter=qdrant_filter
                        )
                        
                        # Convert to MemoryEntry objects
                        entries = []
                        for result in results:
                            entry = MemoryEntry(
                                id=result.id,
                                content=result.payload.get("content", ""),
                                vector=query_vector,  # Original vector not stored in search
                                metadata=result.payload,
                                collection=collection,
                                timestamp=datetime.fromisoformat(result.payload.get("timestamp", datetime.now(timezone.utc).isoformat())),
                                score=result.score
                            )
                            entries.append(entry)
                            
                        # Cache results
                        if cache_key and self.redis_manager and not self._circuit_breaker["redis"]["is_open"]:
                            try:
                                await self.redis_manager.set_async(
                                    cache_key,
                                    json.dumps([self._serialize_entry(e) for e in entries]),
                                    ex=300  # 5 minute cache for searches
                                )
                            except Exception:
                                pass  # Non-critical
                                
                        # Track metrics
                        memory_operations.labels(operation="search", collection=collection.value, status="success").inc()
                        memory_latency.labels(operation="search", collection=collection.value).observe(time.time() - start_time)
                        
                        return entries
                        
                except Exception as e:
                    self._handle_service_error("qdrant", e)
                    raise
                    
            else:
                raise Exception("Qdrant circuit breaker is open")
                
        except Exception as e:
            memory_operations.labels(operation="search", collection=collection.value, status="error").inc()
            logger.error(f"❌ Search failed in {collection.value}: {e}")
            
            # Fallback to Mem0 if available for conversations
            if self.mem0_client and collection == MemoryCollection.CONVERSATIONS and not self._circuit_breaker["mem0"]["is_open"]:
                try:
                    mem0_results = self.mem0_client.search(
                        query=metadata_filter.get("query", ""),
                        user_id=metadata_filter.get("user_id", "system"),
                        limit=limit
                    )
                    return self._convert_mem0_results(mem0_results)
                except Exception as mem0_error:
                    self._handle_service_error("mem0", mem0_error)
                    
            raise
            
    async def delete(
        self,
        entry_id: str,
        collection: MemoryCollection = MemoryCollection.KNOWLEDGE
    ) -> bool:
        """Delete entry from all layers"""
        try:
            # Delete from Qdrant
            if not self._circuit_breaker["qdrant"]["is_open"]:
                async with self.qdrant_pool.get_connection() as client:
                    await client.delete(
                        collection_name=collection.value,
                        points_selector=models.PointIdsList(points=[entry_id])
                    )
                    
            # Delete from Redis cache
            if self.redis_manager and not self._circuit_breaker["redis"]["is_open"]:
                try:
                    cache_key = f"{collection.value}:{entry_id}"
                    await self.redis_manager.delete_async(cache_key)
                except Exception:
                    pass  # Non-critical
                    
            memory_operations.labels(operation="delete", collection=collection.value, status="success").inc()
            return True
            
        except Exception as e:
            memory_operations.labels(operation="delete", collection=collection.value, status="error").inc()
            logger.error(f"❌ Failed to delete {entry_id} from {collection.value}: {e}")
            return False
            
    async def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status of all components"""
        status = {
            "healthy": True,
            "components": {},
            "metrics": {}
        }
        
        # Check Qdrant
        try:
            if self.qdrant_pool:
                qdrant_health = await self.qdrant_pool.health_check()
                status["components"]["qdrant"] = {
                    "healthy": qdrant_health["healthy"],
                    "pool_size": qdrant_health["pool_size"],
                    "in_use": qdrant_health["in_use"],
                    "circuit_breaker": self._circuit_breaker["qdrant"]
                }
            else:
                status["components"]["qdrant"] = {"healthy": False, "error": "Not initialized"}
                status["healthy"] = False
        except Exception as e:
            status["components"]["qdrant"] = {"healthy": False, "error": str(e)}
            status["healthy"] = False
            
        # Check Redis
        try:
            if self.redis_manager:
                redis_health = await self.redis_manager.health_check()
                status["components"]["redis"] = {
                    "healthy": redis_health,
                    "circuit_breaker": self._circuit_breaker["redis"]
                }
            else:
                status["components"]["redis"] = {"healthy": False, "error": "Not initialized"}
        except Exception as e:
            status["components"]["redis"] = {"healthy": False, "error": str(e)}
            
        # Check Mem0
        if MEM0_AVAILABLE and self.mem0_client:
            status["components"]["mem0"] = {
                "healthy": not self._circuit_breaker["mem0"]["is_open"],
                "circuit_breaker": self._circuit_breaker["mem0"]
            }
        else:
            status["components"]["mem0"] = {"healthy": False, "error": "Not available"}
            
        # Connection pool metrics
        if self.qdrant_pool:
            connection_pool_usage.labels(service="qdrant", pool="connections").set(
                len(self.qdrant_pool._in_use)
            )
            
        return status
        
    async def cleanup(self) -> None:
        """Clean up all resources"""
        logger.info("🧹 Cleaning up Sophia Unified Memory Service...")
        
        if self.qdrant_pool:
            await self.qdrant_pool.close()
            
        if self.redis_manager:
            await self.redis_manager.cleanup()
            
        self.initialized = False
        logger.info("✅ Cleanup completed")
        
    # Helper methods
    
    def _generate_id(self, content: str, metadata: Dict[str, Any]) -> str:
        """Generate unique ID for memory entry"""
        unique_string = f"{content}{json.dumps(metadata, sort_keys=True)}{time.time()}"
        return hashlib.sha256(unique_string.encode()).hexdigest()[:16]
        
    def _serialize_entry(self, entry: MemoryEntry) -> Dict[str, Any]:
        """Serialize MemoryEntry for caching"""
        return {
            "id": entry.id,
            "content": entry.content,
            "metadata": entry.metadata,
            "collection": entry.collection.value,
            "timestamp": entry.timestamp.isoformat(),
            "score": entry.score
        }
        
    def _deserialize_entry(self, data: Dict[str, Any]) -> MemoryEntry:
        """Deserialize cached data to MemoryEntry"""
        return MemoryEntry(
            id=data["id"],
            content=data["content"],
            vector=[],  # Vector not cached
            metadata=data["metadata"],
            collection=MemoryCollection(data["collection"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            score=data.get("score")
        )
        
    def _convert_mem0_results(self, mem0_results: List[Any]) -> List[MemoryEntry]:
        """Convert Mem0 results to MemoryEntry format"""
        entries = []
        for result in mem0_results:
            entry = MemoryEntry(
                id=str(result.get("id", "")),
                content=result.get("text", ""),
                vector=[],
                metadata=result.get("metadata", {}),
                collection=MemoryCollection.CONVERSATIONS,
                timestamp=datetime.now(timezone.utc),
                score=result.get("score", 0.0)
            )
            entries.append(entry)
        return entries
        
    def _handle_service_error(self, service: str, error: Exception) -> None:
        """Handle service errors and update circuit breaker"""
        cb = self._circuit_breaker[service]
        cb["failures"] += 1
        cb["last_failure"] = time.time()
        
        # Open circuit breaker after 3 failures
        if cb["failures"] >= 3:
            cb["is_open"] = True
            logger.warning(f"⚠️ Circuit breaker opened for {service}")
            
        # Auto-reset after 60 seconds
        elif cb["is_open"] and time.time() - cb["last_failure"] > 60:
            cb["is_open"] = False
            cb["failures"] = 0
            logger.info(f"✅ Circuit breaker reset for {service}")
            
    def _reset_circuit_breaker(self, service: str) -> None:
        """Reset circuit breaker on successful operation"""
        self._circuit_breaker[service]["failures"] = 0
        self._circuit_breaker[service]["is_open"] = False


# Singleton instance
_unified_memory_instance: Optional[SophiaUnifiedMemoryService] = None
_lock = asyncio.Lock()

async def get_unified_memory_service() -> SophiaUnifiedMemoryService:
    """Get or create singleton instance of unified memory service"""
    global _unified_memory_instance
    
    if _unified_memory_instance is None:
        async with _lock:
            if _unified_memory_instance is None:
                _unified_memory_instance = SophiaUnifiedMemoryService()
                await _unified_memory_instance.initialize()
                
    return _unified_memory_instance
```

#### **1.2 Fix Configuration Recursion**

```python
# backend/core/auto_esc_config_fixed.py
"""
Fixed version of auto_esc_config.py with recursion prevention
"""

import os
import json
from typing import Optional, Dict, Any
from functools import lru_cache
import subprocess
from shared.utils.custom_logger import logger

# Circuit breaker to prevent recursion
_config_loading = False
_config_cache: Dict[str, Any] = {}
_esc_cache: Optional[Dict[str, Any]] = None

def get_config_value(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get configuration value with recursion prevention"""
    global _config_loading, _config_cache
    
    # Check cache first
    if key in _config_cache:
        return _config_cache[key]
    
    # Prevent recursion
    if _config_loading:
        return os.getenv(key, default)
    
    _config_loading = True
    try:
        # Try environment variable first
        env_value = os.getenv(key)
        if env_value:
            _config_cache[key] = env_value
            return env_value
            
        # Try Pulumi ESC
        try:
            esc_data = _load_esc_environment()
            if esc_data and key in esc_data:
                value = esc_data[key]
                _config_cache[key] = value
                return value
        except Exception as e:
            logger.warning(f"Failed to load from ESC: {e}")
            
        # Return default
        if default:
            _config_cache[key] = default
        return default
        
    finally:
        _config_loading = False

@lru_cache(maxsize=1)
def _load_esc_environment() -> Dict[str, Any]:
    """Load ESC environment with caching"""
    global _esc_cache
    
    if _esc_cache is not None:
        return _esc_cache
        
    try:
        pulumi_org = os.getenv("PULUMI_ORG", "scoobyjava-org")
        environment = os.getenv("ENVIRONMENT", "prod")
        
        env_path = f"{pulumi_org}/default/sophia-ai-{environment}"
        
        result = subprocess.run(
            ["pulumi", "env", "get", env_path, "--json"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            _esc_cache = json.loads(result.stdout)
            return _esc_cache
        else:
            logger.error(f"Pulumi ESC failed: {result.stderr}")
            return {}
            
    except Exception as e:
        logger.error(f"Failed to load ESC environment: {e}")
        return {}
```

### **Phase 2: MCP Server Integration**

#### **2.1 Coding MCP Server Orchestrator**

```python
# backend/services/coding_mcp_orchestrator.py
"""
Coding MCP Server Orchestrator
Coordinates AI Memory, Codacy, GitHub, Portkey, and Lambda Labs MCPs
"""

import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json

from backend.services.sophia_unified_memory_service import get_unified_memory_service, MemoryCollection
from backend.services.mcp_client import MCPClient
from backend.services.portkey_gateway import PortkeyGateway
from backend.core.auto_esc_config_fixed import get_config_value
from shared.utils.custom_logger import logger

class CodingTask(Enum):
    """Types of coding tasks"""
    GENERATE = "generate"
    REFACTOR = "refactor"
    DEBUG = "debug"
    REVIEW = "review"
    DOCUMENT = "document"
    TEST = "test"
    DEPLOY = "deploy"

@dataclass
class CodingRequest:
    """Coding request structure"""
    task: CodingTask
    description: str
    context: Optional[Dict[str, Any]] = None
    files: Optional[List[str]] = None
    requirements: Optional[Dict[str, Any]] = None

@dataclass
class CodingResponse:
    """Coding response structure"""
    success: bool
    code: Optional[str] = None
    analysis: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None
    suggestions: Optional[List[str]] = None
    artifacts: Optional[Dict[str, Any]] = None

class CodingMCPOrchestrator:
    """
    Orchestrates coding MCP servers for AI-assisted development
    """
    
    def __init__(self):
        self.memory_service = None
        self.portkey_gateway = None
        
        # MCP clients
        self.mcp_clients = {
            "ai_memory": MCPClient("ai_memory", 9000),
            "codacy": MCPClient("codacy", 3008),
            "github": MCPClient("github", 9001),
            "lambda_labs": MCPClient("lambda_labs", 9020),
            "openrouter_search": MCPClient("openrouter_search", 9014)
        }
        
        # Task routing configuration
        self.task_routing = {
            CodingTask.GENERATE: ["ai_memory", "github", "codacy"],
            CodingTask.REFACTOR: ["ai_memory", "codacy", "github"],
            CodingTask.DEBUG: ["ai_memory", "codacy"],
            CodingTask.REVIEW: ["codacy", "github"],
            CodingTask.DOCUMENT: ["ai_memory", "github"],
            CodingTask.TEST: ["codacy", "lambda_labs"],
            CodingTask.DEPLOY: ["lambda_labs", "github"]
        }
        
    async def initialize(self):
        """Initialize all components"""
        logger.info("🚀 Initializing Coding MCP Orchestrator...")
        
        # Initialize memory service
        self.memory_service = await get_unified_memory_service()
        
        # Initialize Portkey
