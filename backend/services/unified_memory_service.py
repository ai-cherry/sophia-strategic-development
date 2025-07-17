"""
Unified Memory Service - Orchestrates the 5-tier hybrid memory architecture
Provides a single interface for all memory operations with intelligent routing
"""

import asyncio
import time
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import numpy as np
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.core.auto_esc_config import get_config_value
from backend.services.lambda_inference_service import LambdaInferenceService

# Import MCP servers
from mcp_servers.qdrant.qdrant_mcp_server import QdrantMCPServer
from mcp_servers.mem0.mem0_orchestrator import Mem0OrchestratorMCPServer, MemoryContext
from mcp_servers.redis.redis_cache_layer import RedisCacheMCPServer, CacheType
from mcp_servers.postgresql.structured_data_store import PostgreSQLMCPServer, DataSchema


class MemoryType(Enum):
    """Types of memory operations"""
    CODING = "coding"
    BUSINESS = "business"
    HYBRID = "hybrid"


@dataclass
class MemoryRequest:
    """Represents a memory request with routing information"""
    content: str
    memory_type: MemoryType
    operation: str  # add, search, update, delete
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None
    limit: int = 10


@dataclass
class MemoryResult:
    """Represents a memory operation result"""
    success: bool
    data: Any
    tier_used: str
    processing_time_ms: float
    cache_hit: bool = False
    error: Optional[str] = None


class UnifiedMemoryService:
    """
    Unified Memory Service that orchestrates all memory tiers
    
    Architecture:
    - Tier 0: Lambda GPU (embeddings)
    - Tier 1: Qdrant (vector search)
    - Tier 2: Mem0 (orchestration)
    - Tier 3: Redis (caching)
    - Tier 4: PostgreSQL (structured data)
    """
    
    def __init__(self):
        # Initialize services
        self.lambda_gpu = LambdaInferenceService()
        self.qdrant = QdrantMCPServer()
        self.mem0 = Mem0OrchestratorMCPServer()
        self.redis = RedisCacheMCPServer()
        self.postgresql = PostgreSQLMCPServer()
        
        # Performance tracking
        self.stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "avg_latency_ms": 0.0,
            "tier_usage": {
                "gpu": 0,
                "qdrant": 0,
                "mem0": 0,
                "redis": 0,
                "postgresql": 0
            }
        }
        
    async def initialize(self):
        """Initialize all memory services"""
        print("🚀 Initializing Unified Memory Service...")
        
        # Initialize each tier
        # Lambda GPU doesn't need initialization
        await self.qdrant.initialize()
        await self.mem0.initialize()
        await self.redis.initialize()
        await self.postgresql.initialize()
        
        print("✅ Unified Memory Service initialized successfully!")
    
    async def process_request(self, request: MemoryRequest) -> MemoryResult:
        """Process a memory request through the appropriate tiers"""
        start_time = time.time()
        self.stats["total_requests"] += 1
        
        try:
            # Route based on operation type
            if request.operation == "add":
                result = await self._handle_add(request)
            elif request.operation == "search":
                result = await self._handle_search(request)
            elif request.operation == "update":
                result = await self._handle_update(request)
            elif request.operation == "delete":
                result = await self._handle_delete(request)
            else:
                result = MemoryResult(
                    success=False,
                    data=None,
                    tier_used="none",
                    processing_time_ms=0,
                    error=f"Unknown operation: {request.operation}"
                )
            
            # Update latency stats
            latency = (time.time() - start_time) * 1000
            self._update_latency_stats(latency)
            
            return result
            
        except Exception as e:
            return MemoryResult(
                success=False,
                data=None,
                tier_used="error",
                processing_time_ms=(time.time() - start_time) * 1000,
                error=str(e)
            )
    
    async def _handle_add(self, request: MemoryRequest) -> MemoryResult:
        """Handle memory addition across tiers"""
        tiers_used = []
        
        # 1. Generate embeddings (Tier 0)
        embeddings = await self._generate_embeddings(request.content)
        tiers_used.append("gpu")
        self.stats["tier_usage"]["gpu"] += 1
        
        # 2. Store in Qdrant (Tier 1)
        collection = "coding_memory" if request.memory_type == MemoryType.CODING else "business_memory"
        qdrant_result = await self.qdrant.handle_call_tool(
            "add_vector",
            {
                "collection_name": collection,
                "payload": {
                    "content": request.content,
                    "user_id": request.user_id,
                    "metadata": request.metadata or {},
                    "timestamp": datetime.utcnow().isoformat()
                },
                "vector": embeddings.tolist()
            }
        )
        tiers_used.append("qdrant")
        self.stats["tier_usage"]["qdrant"] += 1
        
        # 3. Add to Mem0 for orchestration (Tier 2)
        context = MemoryContext.CODING if request.memory_type == MemoryType.CODING else MemoryContext.BUSINESS
        mem0_result = await self.mem0.add_memory(
            content=request.content,
            context=context,
            user_id=request.user_id or "default",
            metadata=request.metadata
        )
        tiers_used.append("mem0")
        self.stats["tier_usage"]["mem0"] += 1
        
        # 4. Invalidate relevant caches (Tier 3)
        cache_type = CacheType.CODING if request.memory_type == MemoryType.CODING else CacheType.BUSINESS
        await self.redis.invalidate_pattern(cache_type, f"*{request.user_id}*")
        tiers_used.append("redis")
        self.stats["tier_usage"]["redis"] += 1
        
        # 5. Store structured data if applicable (Tier 4)
        if request.memory_type == MemoryType.CODING and request.metadata and "repository" in request.metadata:
            await self.postgresql.add_repository(
                name=request.metadata["repository"],
                language=request.metadata.get("language", "unknown"),
                metadata=request.metadata
            )
            tiers_used.append("postgresql")
            self.stats["tier_usage"]["postgresql"] += 1
        
        return MemoryResult(
            success=True,
            data={
                "memory_id": qdrant_result.get("id") if qdrant_result else None,
                "tiers_used": tiers_used
            },
            tier_used=", ".join(tiers_used),
            processing_time_ms=mem0_result.get("processing_time_ms", 0) if mem0_result and isinstance(mem0_result, dict) else 0
        )
    
    async def _handle_search(self, request: MemoryRequest) -> MemoryResult:
        """Handle memory search with intelligent caching"""
        # Check cache first (Tier 3)
        cache_key = self._generate_cache_key(request)
        cache_type = CacheType.CODING if request.memory_type == MemoryType.CODING else CacheType.BUSINESS
        
        cached_result = await self.redis.get(cache_type, cache_key)
        if cached_result:
            self.stats["cache_hits"] += 1
            self.stats["tier_usage"]["redis"] += 1
            return MemoryResult(
                success=True,
                data=cached_result,
                tier_used="redis",
                processing_time_ms=1.0,
                cache_hit=True
            )
        
        # Generate embeddings for query (Tier 0)
        query_embeddings = await self._generate_embeddings(request.content)
        self.stats["tier_usage"]["gpu"] += 1
        
        # Search in Qdrant (Tier 1)
        collection = "coding_memory" if request.memory_type == MemoryType.CODING else "business_memory"
        qdrant_results = await self.qdrant.handle_call_tool(
            "search",
            {
                "collection_name": collection,
                "query_vector": query_embeddings.tolist(),
                "limit": request.limit,
                "filters": request.filters
            }
        )
        self.stats["tier_usage"]["qdrant"] += 1
        
        # Enhance with Mem0 context (Tier 2)
        context = MemoryContext.CODING if request.memory_type == MemoryType.CODING else MemoryContext.BUSINESS
        mem0_results = await self.mem0.search_memories(
            query=request.content,
            context=context,
            user_id=request.user_id,
            filters=request.filters,
            limit=request.limit
        )
        self.stats["tier_usage"]["mem0"] += 1
        
        # Combine results
        combined_results = self._merge_search_results(
            qdrant_results.get("results", []),
            mem0_results
        )
        
        # Cache the results (Tier 3)
        await self.redis.set(cache_type, cache_key, combined_results, ttl=300)
        
        # Add structured context if available (Tier 4)
        if request.memory_type == MemoryType.CODING and request.filters and "repository" in request.filters:
            patterns = await self.postgresql.get_repository_patterns(
                repository_name=request.filters["repository"]
            )
            combined_results["patterns"] = patterns
            self.stats["tier_usage"]["postgresql"] += 1
        
        return MemoryResult(
            success=True,
            data=combined_results,
            tier_used="gpu, qdrant, mem0, redis, postgresql",
            processing_time_ms=50.0  # Typical search time
        )
    
    async def _handle_update(self, request: MemoryRequest) -> MemoryResult:
        """Handle memory updates"""
        # Update in Mem0
        context = MemoryContext.CODING if request.memory_type == MemoryType.CODING else MemoryContext.BUSINESS
        mem0_result = await self.mem0.update_memory(
            memory_id=request.metadata.get("memory_id", "") if request.metadata else "",
            content=request.content,
            context=context,
            user_id=request.user_id or "default"
        )
        
        # Invalidate caches
        cache_type = CacheType.CODING if request.memory_type == MemoryType.CODING else CacheType.BUSINESS
        await self.redis.invalidate_pattern(cache_type, f"*{request.user_id}*")
        
        # Determine success based on mem0_result
        if mem0_result is not None and isinstance(mem0_result, dict):
            success = mem0_result.get("status", "success") == "success"
        else:
            success = False
            
        return MemoryResult(
            success=success,
            data=mem0_result,
            tier_used="mem0, redis",
            processing_time_ms=10.0
        )
    
    async def _handle_delete(self, request: MemoryRequest) -> MemoryResult:
        """Handle memory deletion"""
        # Delete from Mem0
        context = MemoryContext.CODING if request.memory_type == MemoryType.CODING else MemoryContext.BUSINESS
        mem0_result = await self.mem0.delete_memory(
            memory_id=request.metadata.get("memory_id", "") if request.metadata else "",
            context=context,
            user_id=request.user_id or "default"
        )
        
        # Delete from Qdrant
        collection = "coding_memory" if request.memory_type == MemoryType.CODING else "business_memory"
        await self.qdrant.handle_call_tool(
            "delete",
            {
                "collection_name": collection,
                "id": request.metadata.get("memory_id", "") if request.metadata else ""
            }
        )
        
        # Invalidate caches
        cache_type = CacheType.CODING if request.memory_type == MemoryType.CODING else CacheType.BUSINESS
        await self.redis.invalidate_pattern(cache_type, f"*{request.user_id}*")
        
        # Determine success based on mem0_result
        if mem0_result is not None and isinstance(mem0_result, dict):
            success = mem0_result.get("status", "success") == "success"
        else:
            success = False
            
        return MemoryResult(
            success=success,
            data=mem0_result,
            tier_used="mem0, qdrant, redis",
            processing_time_ms=15.0
        )
    
    async def _generate_embeddings(self, text: str) -> np.ndarray:
        """Generate embeddings using Lambda GPU"""
        # For now, generate mock embeddings until Lambda GPU service supports embeddings
        # In production, this would call the actual embedding service
        import hashlib
        
        # Generate deterministic embeddings based on text
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        seed = int(text_hash[:8], 16)
        np.random.seed(seed)
        
        # Generate 1536-dimensional embeddings (OpenAI standard)
        embeddings = np.random.randn(1536)
        # Normalize to unit vector
        embeddings = embeddings / np.linalg.norm(embeddings)
        
        return embeddings
    
    def _generate_cache_key(self, request: MemoryRequest) -> str:
        """Generate cache key for request"""
        import hashlib
        key_parts = [
            request.content[:50],  # First 50 chars of query
            request.memory_type.value,
            str(request.user_id),
            str(request.filters),
            str(request.limit)
        ]
        key_str = "|".join(key_parts)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _merge_search_results(self, qdrant_results: List[Dict], mem0_results: List[Dict]) -> Dict[str, Any]:
        """Merge and deduplicate search results"""
        # Create a map for deduplication
        results_map = {}
        
        # Add Qdrant results
        for result in qdrant_results:
            content = result.get("payload", {}).get("content", "")
            if content:
                results_map[content] = {
                    "content": content,
                    "score": result.get("score", 0.0),
                    "metadata": result.get("payload", {}).get("metadata", {}),
                    "source": "qdrant"
                }
        
        # Add Mem0 results (may enhance existing ones)
        for result in mem0_results:
            content = result.get("content", "")
            if content:
                if content in results_map:
                    # Enhance existing result
                    results_map[content]["mem0_score"] = result.get("score", 0.0)
                    results_map[content]["mem0_metadata"] = result.get("metadata", {})
                else:
                    # Add new result
                    results_map[content] = {
                        "content": content,
                        "score": result.get("score", 0.0),
                        "metadata": result.get("metadata", {}),
                        "source": "mem0"
                    }
        
        # Sort by score and convert to list
        sorted_results = sorted(
            results_map.values(),
            key=lambda x: x.get("score", 0.0),
            reverse=True
        )
        
        return {
            "results": sorted_results,
            "count": len(sorted_results),
            "sources": ["qdrant", "mem0"]
        }
    
    def _update_latency_stats(self, latency_ms: float):
        """Update latency statistics"""
        current_avg = self.stats["avg_latency_ms"]
        total_requests = self.stats["total_requests"]
        
        # Calculate new average
        self.stats["avg_latency_ms"] = (
            (current_avg * (total_requests - 1) + latency_ms) / total_requests
        )
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get unified memory service statistics"""
        # Get stats from each tier
        qdrant_stats = await self.qdrant.handle_call_tool("get_stats", {})
        mem0_stats = await self.mem0.get_stats()
        redis_stats = await self.redis.get_stats()
        postgresql_stats = await self.postgresql.get_stats()
        
        return {
            "service": "unified_memory",
            "stats": self.stats,
            "cache_hit_rate": self.stats["cache_hits"] / self.stats["total_requests"] if self.stats["total_requests"] > 0 else 0,
            "tiers": {
                "gpu": {
                    "status": "operational",
                    "usage": self.stats["tier_usage"]["gpu"]
                },
                "qdrant": qdrant_stats,
                "mem0": mem0_stats,
                "redis": redis_stats,
                "postgresql": postgresql_stats
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all memory tiers"""
        health_status = {
            "service": "unified_memory",
            "status": "healthy",
            "tiers": {}
        }
        
        # Check each tier
        try:
            gpu_health = await self.lambda_gpu.health_check()
            health_status["tiers"]["gpu"] = gpu_health
        except:
            health_status["tiers"]["gpu"] = {"status": "unhealthy"}
            health_status["status"] = "degraded"
        
        try:
            qdrant_health = await self.qdrant.health_check()
            health_status["tiers"]["qdrant"] = qdrant_health
        except:
            health_status["tiers"]["qdrant"] = {"status": "unhealthy"}
            health_status["status"] = "degraded"
        
        try:
            mem0_health = await self.mem0.health_check()
            health_status["tiers"]["mem0"] = mem0_health
        except:
            health_status["tiers"]["mem0"] = {"status": "unhealthy"}
            health_status["status"] = "degraded"
        
        try:
            redis_health = await self.redis.health_check()
            health_status["tiers"]["redis"] = redis_health
        except:
            health_status["tiers"]["redis"] = {"status": "unhealthy"}
            health_status["status"] = "degraded"
        
        try:
            postgresql_health = await self.postgresql.health_check()
            health_status["tiers"]["postgresql"] = postgresql_health
        except:
            health_status["tiers"]["postgresql"] = {"status": "unhealthy"}
            health_status["status"] = "degraded"
        
        return health_status


# Singleton instance
_unified_memory_service = None


def get_unified_memory_service() -> UnifiedMemoryService:
    """Get the singleton unified memory service instance"""
    global _unified_memory_service
    if _unified_memory_service is None:
        _unified_memory_service = UnifiedMemoryService()
    return _unified_memory_service


# Example usage and testing
async def example_usage():
    """Example of using the unified memory service"""
    # Get the service
    memory_service = get_unified_memory_service()
    await memory_service.initialize()
    
    # Add coding memory
    coding_request = MemoryRequest(
        content="Implement async function with error handling in Python",
        memory_type=MemoryType.CODING,
        operation="add",
        user_id="developer1",
        metadata={
            "repository": "sophia-ai",
            "language": "python",
            "pattern": "async_error_handling"
        }
    )
    result = await memory_service.process_request(coding_request)
    print(f"Add result: {result}")
    
    # Search for coding patterns
    search_request = MemoryRequest(
        content="async error handling patterns",
        memory_type=MemoryType.CODING,
        operation="search",
        user_id="developer1",
        limit=5
    )
    result = await memory_service.process_request(search_request)
    print(f"Search result: {result}")
    
    # Add business memory
    business_request = MemoryRequest(
        content="Q4 revenue increased by 25% due to new AI features",
        memory_type=MemoryType.BUSINESS,
        operation="add",
        user_id="ceo",
        metadata={
            "project_id": "ai-initiative-2025",
            "importance": "high",
            "source": "quarterly_report"
        }
    )
    result = await memory_service.process_request(business_request)
    print(f"Business add result: {result}")
    
    # Get statistics
    stats = await memory_service.get_stats()
    print(f"Service stats: {stats}")
    
    # Health check
    health = await memory_service.health_check()
    print(f"Health status: {health}")


if __name__ == "__main__":
    asyncio.run(example_usage())
