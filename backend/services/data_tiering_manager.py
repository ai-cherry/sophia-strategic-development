"""
Data Tiering Manager for Sophia AI Memory Ecosystem.

Manages automatic data movement between hot, warm, and cold tiers
based on access patterns and age.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any

from backend.services.unified_memory_service_v2 import get_unified_memory_service
from shared.utils.monitoring import log_execution_time

logger = logging.getLogger(__name__)


class TieringConfig:
    """Configuration for data tiering thresholds"""

    # Time-based thresholds
    HOT_TIER_TTL = 3600  # 1 hour
    WARM_TIER_TTL = 604800  # 7 days
    COLD_TIER_THRESHOLD = 2592000  # 30 days

    # Access-based thresholds
    HOT_TIER_ACCESS_COUNT = 5  # Promote after 5 accesses
    COLD_TIER_ACCESS_THRESHOLD = 1  # Keep in cold if < 1 access/month

    # Batch processing
    BATCH_SIZE = 100
    MIGRATION_INTERVAL = 3600  # Run every hour

    # Tier identifiers
    HOT_TIER = "hot"
    WARM_TIER = "warm"
    COLD_TIER = "cold"


class DataTieringManager:
    """
    Manages automatic data movement between storage tiers.

    Hot Tier (L1 - Redis): Frequently accessed, < 1 hour old
    Warm Tier (L3 - Qdrant): Recent data, < 7 days old
    Cold Tier (L3 - Qdrant Compressed): Archival, > 30 days old
    """

    def __init__(self):
        """Initialize the data tiering manager"""
        self.memory_service = get_unified_memory_service()
        self.config = TieringConfig()
        self._migration_task = None

        logger.info("DataTieringManager initialized")

    async def start_automatic_tiering(self) -> None:
        """
        Start the automatic tiering background task.

        This runs periodically to analyze and migrate data.
        """
        if self._migration_task is not None:
            logger.warning("Automatic tiering already running")
            return

        self._migration_task = asyncio.create_task(self._automatic_tiering_loop())
        logger.info("Started automatic tiering background task")

    async def stop_automatic_tiering(self) -> None:
        """Stop the automatic tiering background task"""
        if self._migration_task is None:
            return

        self._migration_task.cancel()
        try:
            await self._migration_task
        except asyncio.CancelledError:
            pass

        self._migration_task = None
        logger.info("Stopped automatic tiering background task")

    async def _automatic_tiering_loop(self) -> None:
        """Background loop for automatic data tiering"""
        while True:
            try:
                logger.info("Running automatic tiering analysis...")

                # Analyze and migrate data
                await self.analyze_and_migrate()

                # Sleep until next run
                await asyncio.sleep(self.config.MIGRATION_INTERVAL)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in automatic tiering: {e}")
                await asyncio.sleep(60)  # Retry after 1 minute on error

    @log_execution_time
    async def analyze_and_migrate(self) -> dict[str, int]:
        """
        Analyze access patterns and migrate data between tiers.

        Returns:
            Dictionary with migration statistics
        """
        stats = {
            "analyzed": 0,
            "migrated_to_hot": 0,
            "migrated_to_warm": 0,
            "migrated_to_cold": 0,
            "errors": 0,
        }

        # Run migrations in parallel
        tasks = [
            self._migrate_cold_to_warm(stats),
            self._migrate_warm_to_hot(stats),
            self._migrate_hot_to_warm(stats),
            self._migrate_warm_to_cold(stats),
        ]

        await asyncio.gather(*tasks, return_exceptions=True)

        logger.info(
            f"Tiering complete - Analyzed: {stats['analyzed']}, "
            f"To Hot: {stats['migrated_to_hot']}, "
            f"To Warm: {stats['migrated_to_warm']}, "
            f"To Cold: {stats['migrated_to_cold']}, "
            f"Errors: {stats['errors']}"
        )

        return stats

    async def _migrate_cold_to_warm(self, stats: dict[str, int]) -> None:
        """
        Migrate frequently accessed cold data to warm tier.

        Cold → Warm: If accessed recently
        """
        try:
            # Query cold data accessed in last 7 days
            query = """
            SELECT
                id,
                content,
                source,
                metadata,
                created_at
            FROM AI_MEMORY.VECTORS.KNOWLEDGE_BASE
            WHERE
                metadata:tier = 'cold'
                AND metadata:last_accessed > DATEADD(day, -7, CURRENT_TIMESTAMP())
                AND metadata:access_count >= %s
            LIMIT %s
            """

            results = await self.memory_service.execute_qdrant_query(
                query, (self.config.COLD_TIER_ACCESS_THRESHOLD, self.config.BATCH_SIZE)
            )

            for row in results:
                try:
                    await self._update_tier(
                        row["ID"], self.config.WARM_TIER, row.get("METADATA", {})
                    )
                    stats["migrated_to_warm"] += 1
                except Exception as e:
                    logger.error(f"Failed to migrate {row['ID']} to warm: {e}")
                    stats["errors"] += 1

                stats["analyzed"] += 1

        except Exception as e:
            logger.error(f"Error in cold to warm migration: {e}")

    async def _migrate_warm_to_hot(self, stats: dict[str, int]) -> None:
        """
        Migrate frequently accessed warm data to hot tier.

        Warm → Hot: If accessed frequently
        """
        try:
            # Query warm data with high access count
            query = """
            SELECT
                id,
                content,
                source,
                metadata,
                created_at
            FROM AI_MEMORY.VECTORS.KNOWLEDGE_BASE
            WHERE
                (metadata:tier = 'warm' OR metadata:tier IS NULL)
                AND metadata:access_count >= %s
                AND metadata:last_accessed > DATEADD(hour, -1, CURRENT_TIMESTAMP())
            LIMIT %s
            """

            results = await self.memory_service.execute_qdrant_query(
                query, (self.config.HOT_TIER_ACCESS_COUNT, self.config.BATCH_SIZE)
            )

            for row in results:
                try:
                    # Add to Redis hot tier
                    if self.memory_service.redis_helper:
                        cache_key = f"knowledge:{row['ID']}"
                        await self.memory_service.redis_helper.cache_set(
                            cache_key,
                            {
                                "content": row["CONTENT"],
                                "source": row["SOURCE"],
                                "metadata": row.get("METADATA", {}),
                            },
                            ttl=self.config.HOT_TIER_TTL,
                        )

                    # Update tier metadata
                    await self._update_tier(
                        row["ID"], self.config.HOT_TIER, row.get("METADATA", {})
                    )

                    stats["migrated_to_hot"] += 1
                except Exception as e:
                    logger.error(f"Failed to migrate {row['ID']} to hot: {e}")
                    stats["errors"] += 1

                stats["analyzed"] += 1

        except Exception as e:
            logger.error(f"Error in warm to hot migration: {e}")

    async def _migrate_hot_to_warm(self, stats: dict[str, int]) -> None:
        """
        Migrate aging hot data to warm tier.

        Hot → Warm: If not accessed recently
        """
        # Redis handles TTL automatically, just update metadata
        try:
            query = """
            SELECT
                id,
                metadata
            FROM AI_MEMORY.VECTORS.KNOWLEDGE_BASE
            WHERE
                metadata:tier = 'hot'
                AND metadata:last_accessed < DATEADD(hour, -1, CURRENT_TIMESTAMP())
            LIMIT %s
            """

            results = await self.memory_service.execute_qdrant_query(
                query, (self.config.BATCH_SIZE,)
            )

            for row in results:
                try:
                    await self._update_tier(
                        row["ID"], self.config.WARM_TIER, row.get("METADATA", {})
                    )
                    stats["migrated_to_warm"] += 1
                except Exception as e:
                    logger.error(f"Failed to migrate {row['ID']} to warm: {e}")
                    stats["errors"] += 1

                stats["analyzed"] += 1

        except Exception as e:
            logger.error(f"Error in hot to warm migration: {e}")

    async def _migrate_warm_to_cold(self, stats: dict[str, int]) -> None:
        """
        Migrate old warm data to cold tier.

        Warm → Cold: If not accessed for extended period
        """
        try:
            query = """
            SELECT
                id,
                content,
                embedding,
                metadata
            FROM AI_MEMORY.VECTORS.KNOWLEDGE_BASE
            WHERE
                (metadata:tier = 'warm' OR metadata:tier IS NULL)
                AND created_at < DATEADD(day, -30, CURRENT_TIMESTAMP())
                AND (
                    metadata:last_accessed IS NULL
                    OR metadata:last_accessed < DATEADD(day, -30, CURRENT_TIMESTAMP())
                )
            LIMIT %s
            """

            results = await self.memory_service.execute_qdrant_query(
                query, (self.config.BATCH_SIZE,)
            )

            for row in results:
                try:
                    # Compress content for cold storage
                    compressed = await self._compress_for_cold_storage(row)

                    # Update with compressed data
                    await self._update_cold_storage(
                        row["ID"], compressed, row.get("METADATA", {})
                    )

                    stats["migrated_to_cold"] += 1
                except Exception as e:
                    logger.error(f"Failed to migrate {row['ID']} to cold: {e}")
                    stats["errors"] += 1

                stats["analyzed"] += 1

        except Exception as e:
            logger.error(f"Error in warm to cold migration: {e}")

    async def _update_tier(
        self, doc_id: str, new_tier: str, metadata: dict[str, Any]
    ) -> None:
        """Update the tier information for a document"""
        metadata = metadata or {}
        metadata["tier"] = new_tier
        metadata["tier_updated"] = datetime.utcnow().isoformat()

        update_query = """
        UPDATE AI_MEMORY.VECTORS.KNOWLEDGE_BASE
        SET metadata = PARSE_JSON(%s)
        WHERE id = %s
        """

        await self.memory_service.execute_qdrant_query(
            update_query, (json.dumps(metadata), doc_id)
        )

    async def _compress_for_cold_storage(self, row: dict[str, Any]) -> dict[str, Any]:
        """
        Compress data for cold storage.

        This could include:
        - Content compression (gzip)
        - Embedding quantization
        - Metadata pruning
        """
        import gzip

        compressed = {
            "id": row["ID"],
            "content_compressed": gzip.compress(
                row["CONTENT"].encode()
            ).hex(),  # Store as hex string
            "embedding_quantized": self._quantize_embedding(row.get("EMBEDDING", [])),
            "metadata_minimal": {
                "source": row.get("METADATA", {}).get("source"),
                "created_at": row.get("METADATA", {}).get("created_at"),
                "tier": "cold",
            },
        }

        return compressed

    def _quantize_embedding(self, embedding: list[float], bits: int = 8) -> list[int]:
        """
        Quantize embedding to reduce storage.

        Converts float32 to int8 for 4x compression.
        """
        if not embedding:
            return []

        # Simple linear quantization
        min_val = min(embedding)
        max_val = max(embedding)
        scale = (max_val - min_val) / (2**bits - 1)

        quantized = [int((val - min_val) / scale) for val in embedding]

        return quantized

    async def _update_cold_storage(
        self, doc_id: str, compressed_data: dict[str, Any], metadata: dict[str, Any]
    ) -> None:
        """Update document with compressed cold storage format"""
        # In a real implementation, this might move to a different table
        # or storage system entirely
        metadata = metadata or {}
        metadata["tier"] = "cold"
        metadata["compressed"] = True
        metadata["compression_ratio"] = len(
            compressed_data["content_compressed"]
        ) / len(compressed_data.get("original_size", 1))

        update_query = """
        UPDATE AI_MEMORY.VECTORS.KNOWLEDGE_BASE
        SET
            content = %s,
            metadata = PARSE_JSON(%s)
        WHERE id = %s
        """

        await self.memory_service.execute_qdrant_query(
            update_query,
            (compressed_data["content_compressed"], json.dumps(metadata), doc_id),
        )

    async def get_tier_statistics(self) -> dict[str, Any]:
        """
        Get statistics about data distribution across tiers.

        Returns:
            Dictionary with tier statistics
        """
        stats_query = """
        SELECT
            COALESCE(metadata:tier, 'warm') as tier,
            COUNT(*) as count,
            AVG(LENGTH(content)) as avg_size,
            SUM(LENGTH(content)) as total_size,
            AVG(metadata:access_count) as avg_access_count
        FROM AI_MEMORY.VECTORS.KNOWLEDGE_BASE
        GROUP BY tier
        """

        results = await self.memory_service.execute_qdrant_query(stats_query)

        stats = {
            "tiers": {},
            "total_documents": 0,
            "total_size": 0,
        }

        for row in results:
            tier = row["TIER"]
            stats["tiers"][tier] = {
                "count": row["COUNT"],
                "avg_size": row["AVG_SIZE"],
                "total_size": row["TOTAL_SIZE"],
                "avg_access_count": row["AVG_ACCESS_COUNT"],
            }
            stats["total_documents"] += row["COUNT"]
            stats["total_size"] += row["TOTAL_SIZE"]

        # Add Redis stats if available
        if self.memory_service.redis_helper:
            hot_keys = await self.memory_service.redis_client.keys("knowledge:*")
            stats["tiers"]["hot"] = {
                "count": len(hot_keys),
                "location": "Redis (L1)",
            }

        return stats

    async def promote_to_hot(self, doc_id: str) -> bool:
        """
        Manually promote a document to hot tier.

        Args:
            doc_id: Document ID to promote

        Returns:
            Success status
        """
        try:
            # Get document from Qdrant
            query = """
            SELECT id, content, source, metadata
            FROM AI_MEMORY.VECTORS.KNOWLEDGE_BASE
            WHERE id = %s
            """

            results = await self.memory_service.execute_qdrant_query(
                query, (doc_id,)
            )

            if not results:
                logger.warning(f"Document {doc_id} not found")
                return False

            row = results[0]

            # Add to Redis
            if self.memory_service.redis_helper:
                cache_key = f"knowledge:{doc_id}"
                await self.memory_service.redis_helper.cache_set(
                    cache_key,
                    {
                        "content": row["CONTENT"],
                        "source": row["SOURCE"],
                        "metadata": row.get("METADATA", {}),
                    },
                    ttl=self.config.HOT_TIER_TTL,
                )

            # Update tier metadata
            await self._update_tier(
                doc_id, self.config.HOT_TIER, row.get("METADATA", {})
            )

            logger.info(f"Promoted {doc_id} to hot tier")
            return True

        except Exception as e:
            logger.error(f"Failed to promote {doc_id} to hot tier: {e}")
            return False


# Singleton instance
_tiering_manager = None


def get_tiering_manager() -> DataTieringManager:
    """Get the singleton DataTieringManager instance"""
    global _tiering_manager

    if _tiering_manager is None:
        _tiering_manager = DataTieringManager()

    return _tiering_manager
