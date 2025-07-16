#!/usr/bin/env python3
"""
Enhanced 6-Tier Memory Architecture for Sophia AI Platform
Optimized for GGH200 GPUs with 96GB HBM3e memory and Lambda GPU integration
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

import redis

from core.auto_esc_config import get_config_value

logger = logging.getLogger(__name__)


class MemoryTier(Enum):
    """Enhanced memory tier enumeration"""

    L0_GPU_MEMORY = "l0_gpu_memory"  # <10ms - H200 HBM3e
    L1_SESSION_CACHE = "l1_session_cache"  # <50ms - Redis
    L2_CORTEX_CACHE = "l2_cortex_cache"  # <100ms - Qdrant + GPU
    L3_PERSISTENT_MEMORY = "l3_persistent_memory"  # <200ms - Qdrant
    L4_KNOWLEDGE_GRAPH = "l4_knowledge_graph"  # <300ms - Qdrant Vector
    L5_WORKFLOW_MEMORY = "l5_workflow_memory"  # <400ms - Qdrant Long-term


@dataclass
class MemoryTierConfig:
    """Configuration for each memory tier"""

    tier: MemoryTier
    size_limit: str
    latency_target: str
    eviction_policy: str
    compression: bool = False
    encryption: bool = False


@dataclass
class GPUMemoryPool:
    """GPU memory pool configuration for L0 tier"""

    active_models: str = "60GB"
    inference_cache: str = "40GB"
    vector_cache: str = "30GB"
    buffer: str = "11GB"
    total_memory: str = "96GB"


class EnhancedMemoryArchitecture:
    """
    Enhanced 6-Tier Memory Architecture Manager
    Optimized for GGH200 GPUs and Lambda GPU integration
    """

    def __init__(self):
        self.tier_configs = self._initialize_tier_configs()
        self.gpu_memory_pool = GPUMemoryPool()
        self.redis_client = self._initialize_redis()
        self.QDRANT_service = None
        self.gpu_memory_manager = None
        self.performance_metrics = {
            "l0_hits": 0,
            "l1_hits": 0,
            "l2_hits": 0,
            "l3_hits": 0,
            "l4_hits": 0,
            "l5_hits": 0,
            "total_requests": 0,
            "avg_latency": 0.0,
        }

    def _initialize_tier_configs(self) -> dict[MemoryTier, MemoryTierConfig]:
        """Initialize configuration for all memory tiers"""
        return {
            MemoryTier.L0_GPU_MEMORY: MemoryTierConfig(
                tier=MemoryTier.L0_GPU_MEMORY,
                size_limit="96GB",
                latency_target="<10ms",
                eviction_policy="lru",
                compression=False,
                encryption=False,
            ),
            MemoryTier.L1_SESSION_CACHE: MemoryTierConfig(
                tier=MemoryTier.L1_SESSION_CACHE,
                size_limit="16GB",
                latency_target="<50ms",
                eviction_policy="allkeys-lru",
                compression=True,
                encryption=False,
            ),
            MemoryTier.L2_CORTEX_CACHE: MemoryTierConfig(
                tier=MemoryTier.L2_CORTEX_CACHE,
                size_limit="unlimited",
                latency_target="<100ms",
                eviction_policy="smart",
                compression=True,
                encryption=True,
            ),
            MemoryTier.L3_PERSISTENT_MEMORY: MemoryTierConfig(
                tier=MemoryTier.L3_PERSISTENT_MEMORY,
                size_limit="unlimited",
                latency_target="<200ms",
                eviction_policy="time-based",
                compression=True,
                encryption=True,
            ),
            MemoryTier.L4_KNOWLEDGE_GRAPH: MemoryTierConfig(
                tier=MemoryTier.L4_KNOWLEDGE_GRAPH,
                size_limit="unlimited",
                latency_target="<300ms",
                eviction_policy="relevance-based",
                compression=True,
                encryption=True,
            ),
            MemoryTier.L5_WORKFLOW_MEMORY: MemoryTierConfig(
                tier=MemoryTier.L5_WORKFLOW_MEMORY,
                size_limit="unlimited",
                latency_target="<400ms",
                eviction_policy="archive",
                compression=True,
                encryption=True,
            ),
        }

    def _initialize_redis(self) -> redis.Redis:
        """Initialize Redis connection for L1 tier"""
        try:
            redis_config = {
                "host": get_config_value("redis_host", "localhost"),
                "port": int(get_config_value("redis_port", "6379")),
                "db": int(get_config_value("redis_db", "0")),
                "decode_responses": True,
                "socket_timeout": 5,
                "socket_connect_timeout": 5,
            }

            redis_password = get_config_value("redis_password")
            if redis_password:
                redis_config["password"] = redis_password

            client = redis.Redis(**redis_config)
            client.ping()
            logger.info("✅ Redis connection established for L1 tier")
            return client
        except Exception as e:
            logger.exception(f"❌ Redis connection failed: {e}")
            raise

    async def initialize_gpu_memory_manager(self):
        """Initialize GPU memory manager for L0 tier"""
        try:
            # This would integrate with Lambda Labs GGH200 GPU
            # For now, we'll simulate the GPU memory management
            self.gpu_memory_manager = {
                "active_models": {},
                "inference_cache": {},
                "vector_cache": {},
                "buffer": {},
                "total_usage": 0,
                "max_memory": 141 * 1024**3,  # 96GB in bytes
            }
            logger.info("✅ GPU memory manager initialized for L0 tier")
        except Exception as e:
            logger.exception(f"❌ GPU memory manager initialization failed: {e}")
            raise

    async def initialize_QDRANT_connection(self):
        """Initialize Qdrant connection for L2-L5 tiers"""
        try:
            # Use QdrantUnifiedMemoryService for L2-L5 tiers
            from backend.services.sophia_unified_memory_service import get_memory_service, SophiaUnifiedMemoryService
            
            self.QDRANT_service = QdrantSophiaUnifiedMemoryService()
            await self.QDRANT_service.initialize()
            
            logger.info("✅ Qdrant connection established for L2-L5 tiers")
        except Exception as e:
            logger.exception(f"❌ Qdrant connection failed: {e}")
            raise

    async def store_data(
        self,
        key: str,
        value: Any,
        tier: MemoryTier,
        ttl: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Store data in the specified memory tier"""
        start_time = time.time()

        try:
            if tier == MemoryTier.L0_GPU_MEMORY:
                success = await self._store_gpu_memory(key, value, ttl, metadata)
            elif tier == MemoryTier.L1_SESSION_CACHE:
                success = await self._store_redis_cache(key, value, ttl, metadata)
            elif tier == MemoryTier.L2_CORTEX_CACHE:
                success = await self._store_cortex_cache(key, value, ttl, metadata)
            elif tier == MemoryTier.L3_PERSISTENT_MEMORY:
                success = await self._store_persistent_memory(key, value, ttl, metadata)
            elif tier == MemoryTier.L4_KNOWLEDGE_GRAPH:
                success = await self._store_knowledge_graph(key, value, ttl, metadata)
            elif tier == MemoryTier.L5_WORKFLOW_MEMORY:
                success = await self._store_workflow_memory(key, value, ttl, metadata)
            else:
                logger.error(f"❌ Unknown memory tier: {tier}")
                return False

            latency = (time.time() - start_time) * 1000  # Convert to milliseconds
            self._update_performance_metrics(tier, latency, success)

            return success

        except Exception as e:
            logger.exception(f"❌ Failed to store data in {tier}: {e}")
            return False

    async def retrieve_data(
        self,
        key: str,
        preferred_tier: MemoryTier | None = None,
    ) -> Any | None:
        """Retrieve data with intelligent tier selection"""
        start_time = time.time()

        # Define tier search order (fastest to slowest)
        search_order = [
            MemoryTier.L0_GPU_MEMORY,
            MemoryTier.L1_SESSION_CACHE,
            MemoryTier.L2_CORTEX_CACHE,
            MemoryTier.L3_PERSISTENT_MEMORY,
            MemoryTier.L4_KNOWLEDGE_GRAPH,
            MemoryTier.L5_WORKFLOW_MEMORY,
        ]

        # If preferred tier is specified, try that first
        if preferred_tier:
            search_order = [preferred_tier] + [
                t for t in search_order if t != preferred_tier
            ]

        for tier in search_order:
            try:
                if tier == MemoryTier.L0_GPU_MEMORY:
                    result = await self._retrieve_gpu_memory(key)
                elif tier == MemoryTier.L1_SESSION_CACHE:
                    result = await self._retrieve_redis_cache(key)
                elif tier == MemoryTier.L2_CORTEX_CACHE:
                    result = await self._retrieve_cortex_cache(key)
                elif tier == MemoryTier.L3_PERSISTENT_MEMORY:
                    result = await self._retrieve_persistent_memory(key)
                elif tier == MemoryTier.L4_KNOWLEDGE_GRAPH:
                    result = await self._retrieve_knowledge_graph(key)
                elif tier == MemoryTier.L5_WORKFLOW_MEMORY:
                    result = await self._retrieve_workflow_memory(key)
                else:
                    continue

                if result is not None:
                    latency = (time.time() - start_time) * 1000
                    self._update_performance_metrics(tier, latency, True)

                    # Promote to faster tier if appropriate
                    await self._promote_to_faster_tier(key, result, tier)

                    return result

            except Exception as e:
                logger.warning(f"⚠️ Failed to retrieve from {tier}: {e}")
                continue

        # Data not found in any tier
        self.performance_metrics["total_requests"] += 1
        return None

    async def _store_gpu_memory(
        self,
        key: str,
        value: Any,
        ttl: int | None,
        metadata: dict[str, Any] | None,
    ) -> bool:
        """Store data in GPU memory (L0 tier)"""
        if not self.gpu_memory_manager:
            return False

        try:
            # Serialize value
            serialized_value = (
                json.dumps(value) if not isinstance(value, str) else value
            )
            value_size = len(serialized_value.encode("utf-8"))

            # Check if we have enough GPU memory
            if (
                self.gpu_memory_manager["total_usage"] + value_size
                > self.gpu_memory_manager["max_memory"]
            ):
                # Evict least recently used items
                await self._evict_gpu_memory()

            # Store in appropriate pool based on metadata
            pool = self._determine_gpu_memory_pool(metadata)
            self.gpu_memory_manager[pool][key] = {
                "value": serialized_value,
                "timestamp": time.time(),
                "ttl": ttl,
                "metadata": metadata,
                "size": value_size,
            }

            self.gpu_memory_manager["total_usage"] += value_size
            self.performance_metrics["l0_hits"] += 1

            logger.debug(f"✅ Stored {key} in GPU memory pool: {pool}")
            return True

        except Exception as e:
            logger.exception(f"❌ GPU memory storage failed: {e}")
            return False

    async def _retrieve_gpu_memory(self, key: str) -> Any | None:
        """Retrieve data from GPU memory (L0 tier)"""
        if not self.gpu_memory_manager:
            return None

        try:
            # Search all GPU memory pools
            for pool in self.gpu_memory_manager.values():
                if isinstance(pool, dict) and key in pool:
                    item = pool[key]

                    # Check TTL
                    if (
                        item.get("ttl")
                        and time.time() - item["timestamp"] > item["ttl"]
                    ):
                        del pool[key]
                        self.gpu_memory_manager["total_usage"] -= item["size"]
                        continue

                    # Update timestamp for LRU
                    item["timestamp"] = time.time()

                    # Deserialize value
                    try:
                        return json.loads(item["value"])
                    except (json.JSONDecodeError, TypeError):
                        return item["value"]

            return None

        except Exception as e:
            logger.exception(f"❌ GPU memory retrieval failed: {e}")
            return None

    async def _store_redis_cache(
        self,
        key: str,
        value: Any,
        ttl: int | None,
        metadata: dict[str, Any] | None,
    ) -> bool:
        """Store data in Redis cache (L1 tier)"""
        try:
            # Serialize value with metadata
            cache_data = {
                "value": value,
                "metadata": metadata,
                "timestamp": time.time(),
            }

            serialized_data = json.dumps(cache_data)

            if ttl:
                self.redis_client.setex(f"l1:{key}", ttl, serialized_data)
            else:
                self.redis_client.set(f"l1:{key}", serialized_data)

            self.performance_metrics["l1_hits"] += 1
            logger.debug(f"✅ Stored {key} in Redis cache")
            return True

        except Exception as e:
            logger.exception(f"❌ Redis cache storage failed: {e}")
            return False

    async def _retrieve_redis_cache(self, key: str) -> Any | None:
        """Retrieve data from Redis cache (L1 tier)"""
        try:
            cached_data = self.redis_client.get(f"l1:{key}")
            if cached_data:
                data = json.loads(cached_data)
                return data["value"]
            return None

        except Exception as e:
            logger.exception(f"❌ Redis cache retrieval failed: {e}")
            return None

    async def _store_cortex_cache(
        self,
        key: str,
        value: Any,
        ttl: int | None,
        metadata: dict[str, Any] | None,
    ) -> bool:
        """Store data in Lambda GPU cache (L2 tier)"""
        try:
            if not self.QDRANT_service:
                return False

            cursor = self.QDRANT_service.cursor()

            # Insert or update cache entry
            insert_query = """
            INSERT INTO SOPHIA_AI_MEMORY.CORTEX_CACHE (
                cache_key, cache_value, metadata, ttl, created_at, updated_at
            ) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP())
            """

            cursor.execute(
                insert_query,
                (
                    key,
                    json.dumps(value),
                    json.dumps(metadata) if metadata else None,
                    ttl,
                ),
            )

            cursor.close()
            self.performance_metrics["l2_hits"] += 1
            logger.debug(f"✅ Stored {key} in Cortex cache")
            return True

        except Exception as e:
            logger.exception(f"❌ Cortex cache storage failed: {e}")
            return False

    async def _retrieve_cortex_cache(self, key: str) -> Any | None:
        """Retrieve data from Lambda GPU cache (L2 tier)"""
        try:
            if not self.QDRANT_service:
                return None

            cursor = self.QDRANT_service.cursor()

            # Query with TTL check
            select_query = """
            SELECT cache_value, metadata
            FROM SOPHIA_AI_MEMORY.CORTEX_CACHE
            WHERE cache_key = ?
            AND (ttl IS NULL OR DATEDIFF(second, created_at, CURRENT_TIMESTAMP()) < ttl)
            """

            cursor.execute(select_query, (key,))
            result = cursor.fetchone()
            cursor.close()

            if result:
                return json.loads(result[0])
            return None

        except Exception as e:
            logger.exception(f"❌ Cortex cache retrieval failed: {e}")
            return None

    async def _store_persistent_memory(
        self,
        key: str,
        value: Any,
        ttl: int | None,
        metadata: dict[str, Any] | None,
    ) -> bool:
        """Store data in Qdrant persistent memory (L3 tier)"""
        try:
            if not self.QDRANT_service:
                return False

            cursor = self.QDRANT_service.cursor()

            # Insert into persistent memory table
            insert_query = """
            INSERT INTO SOPHIA_AI_MEMORY.MEMORY_RECORDS (
                memory_id, category, content, metadata, importance_score, created_at
            ) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP())
            """

            cursor.execute(
                insert_query,
                (
                    key,
                    metadata.get("category", "general") if metadata else "general",
                    json.dumps(value),
                    json.dumps(metadata) if metadata else None,
                    metadata.get("importance_score", 0.5) if metadata else 0.5,
                ),
            )

            cursor.close()
            self.performance_metrics["l3_hits"] += 1
            logger.debug(f"✅ Stored {key} in persistent memory")
            return True

        except Exception as e:
            logger.exception(f"❌ Persistent memory storage failed: {e}")
            return False

    async def _retrieve_persistent_memory(self, key: str) -> Any | None:
        """Retrieve data from Qdrant persistent memory (L3 tier)"""
        try:
            if not self.QDRANT_service:
                return None

            cursor = self.QDRANT_service.cursor()

            select_query = """
            SELECT content, metadata
            FROM SOPHIA_AI_MEMORY.MEMORY_RECORDS
            WHERE memory_id = ?
            """

            cursor.execute(select_query, (key,))
            result = cursor.fetchone()
            cursor.close()

            if result:
                return json.loads(result[0])
            return None

        except Exception as e:
            logger.exception(f"❌ Persistent memory retrieval failed: {e}")
            return None

    async def _store_knowledge_graph(
        self,
        key: str,
        value: Any,
        ttl: int | None,
        metadata: dict[str, Any] | None,
    ) -> bool:
        """Store data in Qdrant knowledge graph (L4 tier)"""
        # Implementation for knowledge graph storage
        # This would integrate with Qdrant's vector search capabilities
        return True

    async def _retrieve_knowledge_graph(self, key: str) -> Any | None:
        """Retrieve data from Qdrant knowledge graph (L4 tier)"""
        # Implementation for knowledge graph retrieval
        return None

    async def _store_workflow_memory(
        self,
        key: str,
        value: Any,
        ttl: int | None,
        metadata: dict[str, Any] | None,
    ) -> bool:
        """Store data in Qdrant workflow memory (L5 tier)"""
        # Implementation for workflow memory storage
        return True

    async def _retrieve_workflow_memory(self, key: str) -> Any | None:
        """Retrieve data from Qdrant workflow memory (L5 tier)"""
        # Implementation for workflow memory retrieval
        return None

    def _determine_gpu_memory_pool(self, metadata: dict[str, Any] | None) -> str:
        """Determine which GPU memory pool to use based on metadata"""
        if not metadata:
            return "buffer"

        data_type = metadata.get("type", "unknown")

        if data_type in ["model", "weights", "parameters"]:
            return "active_models"
        elif data_type in ["inference", "prediction", "response"]:
            return "inference_cache"
        elif data_type in ["embedding", "vector", "similarity"]:
            return "vector_cache"
        else:
            return "buffer"

    async def _evict_gpu_memory(self):
        """Evict items from GPU memory using LRU policy"""
        try:
            # Find oldest items across all pools
            oldest_items = []

            for pool_name, pool in self.gpu_memory_manager.items():
                if isinstance(pool, dict):
                    for key, item in pool.items():
                        oldest_items.append(
                            (item["timestamp"], pool_name, key, item["size"])
                        )

            # Sort by timestamp (oldest first)
            oldest_items.sort(key=lambda x: x[0])

            # Evict items until we have enough space (25% of total memory)
            target_free_space = self.gpu_memory_manager["max_memory"] * 0.25
            freed_space = 0

            for _timestamp, pool_name, key, size in oldest_items:
                if freed_space >= target_free_space:
                    break

                del self.gpu_memory_manager[pool_name][key]
                self.gpu_memory_manager["total_usage"] -= size
                freed_space += size

                logger.debug(f"🗑️ Evicted {key} from GPU memory pool: {pool_name}")

            logger.info(f"✅ Freed {freed_space / 1024**3:.2f}GB from GPU memory")

        except Exception as e:
            logger.exception(f"❌ GPU memory eviction failed: {e}")

    async def _promote_to_faster_tier(
        self, key: str, value: Any, current_tier: MemoryTier
    ):
        """Promote frequently accessed data to faster tiers"""
        try:
            if current_tier == MemoryTier.L1_SESSION_CACHE:
                # Promote to L0 (GPU memory)
                await self._store_gpu_memory(key, value, None, {"promoted": True})
            elif current_tier == MemoryTier.L2_CORTEX_CACHE:
                # Promote to L1 (Redis)
                await self._store_redis_cache(key, value, 3600, {"promoted": True})
            # Add more promotion logic as needed

        except Exception as e:
            logger.warning(f"⚠️ Failed to promote {key} to faster tier: {e}")

    def _update_performance_metrics(
        self, tier: MemoryTier, latency: float, success: bool
    ):
        """Update performance metrics"""
        self.performance_metrics["total_requests"] += 1

        if success:
            if tier == MemoryTier.L0_GPU_MEMORY:
                self.performance_metrics["l0_hits"] += 1
            elif tier == MemoryTier.L1_SESSION_CACHE:
                self.performance_metrics["l1_hits"] += 1
            elif tier == MemoryTier.L2_CORTEX_CACHE:
                self.performance_metrics["l2_hits"] += 1
            elif tier == MemoryTier.L3_PERSISTENT_MEMORY:
                self.performance_metrics["l3_hits"] += 1
            elif tier == MemoryTier.L4_KNOWLEDGE_GRAPH:
                self.performance_metrics["l4_hits"] += 1
            elif tier == MemoryTier.L5_WORKFLOW_MEMORY:
                self.performance_metrics["l5_hits"] += 1

        # Update average latency
        current_avg = self.performance_metrics["avg_latency"]
        total_requests = self.performance_metrics["total_requests"]
        self.performance_metrics["avg_latency"] = (
            current_avg * (total_requests - 1) + latency
        ) / total_requests

    async def get_performance_metrics(self) -> dict[str, Any]:
        """Get current performance metrics"""
        total_hits = sum(
            [
                self.performance_metrics["l0_hits"],
                self.performance_metrics["l1_hits"],
                self.performance_metrics["l2_hits"],
                self.performance_metrics["l3_hits"],
                self.performance_metrics["l4_hits"],
                self.performance_metrics["l5_hits"],
            ]
        )

        hit_rate = total_hits / max(self.performance_metrics["total_requests"], 1)

        return {
            **self.performance_metrics,
            "hit_rate": hit_rate,
            "tier_distribution": {
                "l0_percentage": self.performance_metrics["l0_hits"]
                / max(total_hits, 1),
                "l1_percentage": self.performance_metrics["l1_hits"]
                / max(total_hits, 1),
                "l2_percentage": self.performance_metrics["l2_hits"]
                / max(total_hits, 1),
                "l3_percentage": self.performance_metrics["l3_hits"]
                / max(total_hits, 1),
                "l4_percentage": self.performance_metrics["l4_hits"]
                / max(total_hits, 1),
                "l5_percentage": self.performance_metrics["l5_hits"]
                / max(total_hits, 1),
            },
            "gpu_memory_usage": {
                "total_usage": (
                    self.gpu_memory_manager["total_usage"]
                    if self.gpu_memory_manager
                    else 0
                ),
                "max_memory": (
                    self.gpu_memory_manager["max_memory"]
                    if self.gpu_memory_manager
                    else 0
                ),
                "usage_percentage": (
                    self.gpu_memory_manager["total_usage"]
                    / self.gpu_memory_manager["max_memory"]
                    if self.gpu_memory_manager
                    else 0
                ),
            },
        }

    async def health_check(self) -> dict[str, Any]:
        """Perform health check on all memory tiers"""
        health_status = {
            "overall_health": "healthy",
            "tiers": {},
            "timestamp": time.time(),
        }

        # Check L0 (GPU Memory)
        try:
            if self.gpu_memory_manager:
                health_status["tiers"]["l0_gpu_memory"] = {
                    "status": "healthy",
                    "usage": self.gpu_memory_manager["total_usage"],
                    "max_memory": self.gpu_memory_manager["max_memory"],
                }
            else:
                health_status["tiers"]["l0_gpu_memory"] = {
                    "status": "not_initialized",
                }
        except Exception as e:
            health_status["tiers"]["l0_gpu_memory"] = {
                "status": "unhealthy",
                "error": str(e),
            }

        # Check L1 (Redis)
        try:
            self.redis_client.ping()
            health_status["tiers"]["l1_session_cache"] = {
                "status": "healthy",
                "connection": "active",
            }
        except Exception as e:
            health_status["tiers"]["l1_session_cache"] = {
                "status": "unhealthy",
                "error": str(e),
            }

        # Check L2-L5 (Qdrant)
        try:
            if self.QDRANT_service:
                cursor = self.QDRANT_service.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()

                for tier in [
                    "l2_cortex_cache",
                    "l3_persistent_memory",
                    "l4_knowledge_graph",
                    "l5_workflow_memory",
                ]:
                    health_status["tiers"][tier] = {
                        "status": "healthy",
                        "connection": "active",
                    }
            else:
                for tier in [
                    "l2_cortex_cache",
                    "l3_persistent_memory",
                    "l4_knowledge_graph",
                    "l5_workflow_memory",
                ]:
                    health_status["tiers"][tier] = {
                        "status": "not_initialized",
                    }
        except Exception as e:
            for tier in [
                "l2_cortex_cache",
                "l3_persistent_memory",
                "l4_knowledge_graph",
                "l5_workflow_memory",
            ]:
                health_status["tiers"][tier] = {
                    "status": "unhealthy",
                    "error": str(e),
                }

        # Determine overall health
        unhealthy_tiers = [
            tier
            for tier, status in health_status["tiers"].items()
            if status["status"] == "unhealthy"
        ]

        if unhealthy_tiers:
            health_status["overall_health"] = "degraded"
            health_status["unhealthy_tiers"] = unhealthy_tiers

        return health_status


# Global instance
enhanced_memory_architecture = EnhancedMemoryArchitecture()


async def initialize_enhanced_memory_architecture():
    """Initialize the enhanced memory architecture"""
    logger.info("🚀 Initializing Enhanced 6-Tier Memory Architecture...")

    try:
        await enhanced_memory_architecture.initialize_gpu_memory_manager()
        await enhanced_memory_architecture.initialize_QDRANT_connection()

        logger.info("✅ Enhanced Memory Architecture initialized successfully")
        return enhanced_memory_architecture

    except Exception as e:
        logger.exception(f"❌ Enhanced Memory Architecture initialization failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(initialize_enhanced_memory_architecture())
