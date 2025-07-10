#!/usr/bin/env python3
"""
🚨 ONE-TIME SCRIPT - DELETE AFTER USE
Purpose: Migrate vectors from Pinecone/Weaviate to Snowflake Cortex
Created: July 9, 2025

Migrate Vectors to Snowflake
Migrates all vectors from Pinecone and Weaviate to Snowflake Cortex

This script handles the critical migration from fragmented vector databases
to the unified Snowflake Cortex architecture.
"""

import argparse
import json
import logging
import sys
import time

# Import what we need, but these will be removed after migration
try:
    import pinecone

    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    print("⚠️ Pinecone not installed. Install with: pip install pinecone-client")

try:
    import weaviate

    WEAVIATE_AVAILABLE = True
except ImportError:
    WEAVIATE_AVAILABLE = False
    print("⚠️ Weaviate not installed. Install with: pip install weaviate-client")

import snowflake.connector
from snowflake.connector import DictCursor

from backend.core.auto_esc_config import get_config_value
from backend.core.date_time_manager import date_manager
from backend.services.unified_memory_service import get_unified_memory_service

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class VectorMigrator:
    """Handles migration of vectors from Pinecone/Weaviate to Snowflake"""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.current_date = date_manager.now()
        self.stats = {
            "pinecone_vectors": 0,
            "weaviate_vectors": 0,
            "migrated_vectors": 0,
            "failed_vectors": 0,
            "start_time": time.time(),
        }

        # Initialize connections
        self.unified_memory = None
        self.pinecone_index = None
        self.weaviate_client = None
        self.snowflake_conn = None

        logger.info(f"🗓️ Migration starting on {self.current_date} (July 9, 2025)")
        if self.dry_run:
            logger.info("🔍 DRY RUN MODE - No data will be modified")

    def initialize_connections(self):
        """Initialize all necessary connections"""
        # Unified Memory Service (target)
        logger.info("Initializing UnifiedMemoryService...")
        self.unified_memory = get_unified_memory_service()

        # Snowflake direct connection for batch operations
        logger.info("Connecting to Snowflake...")
        self.snowflake_conn = snowflake.connector.connect(
            account=get_config_value("snowflake_account"),
            user=get_config_value("snowflake_user"),
            password=get_config_value("snowflake_password"),
            warehouse=get_config_value("snowflake_warehouse", "SOPHIA_AI_COMPUTE_WH"),
            database="AI_MEMORY",
            schema="VECTORS",
        )

        # Pinecone (source)
        if PINECONE_AVAILABLE:
            try:
                api_key = get_config_value("pinecone_api_key")
                if api_key:
                    logger.info("Initializing Pinecone connection...")
                    pinecone.init(api_key=api_key)

                    # Get the index name
                    index_name = get_config_value(
                        "pinecone_index_name", "sophia-knowledge"
                    )
                    self.pinecone_index = pinecone.Index(index_name)

                    # Get index stats
                    stats = self.pinecone_index.describe_index_stats()
                    total_vectors = stats.total_vector_count
                    self.stats["pinecone_vectors"] = total_vectors
                    logger.info(
                        f"✅ Connected to Pinecone index '{index_name}' with {total_vectors} vectors"
                    )
                else:
                    logger.warning(
                        "No Pinecone API key found - skipping Pinecone migration"
                    )
            except Exception as e:
                logger.exception(f"Failed to connect to Pinecone: {e}")

        # Weaviate (source)
        if WEAVIATE_AVAILABLE:
            try:
                weaviate_url = get_config_value("weaviate_url")
                if weaviate_url:
                    logger.info("Initializing Weaviate connection...")
                    auth_config = None

                    # Check for API key
                    api_key = get_config_value("weaviate_api_key")
                    if api_key:
                        auth_config = weaviate.AuthApiKey(api_key=api_key)

                    self.weaviate_client = weaviate.Client(
                        url=weaviate_url, auth_client_secret=auth_config
                    )

                    # Get object count
                    result = (
                        self.weaviate_client.query.aggregate("Knowledge")
                        .with_meta_count()
                        .do()
                    )
                    if result and "data" in result:
                        count = result["data"]["Aggregate"]["Knowledge"][0]["meta"][
                            "count"
                        ]
                        self.stats["weaviate_vectors"] = count
                        logger.info(
                            f"✅ Connected to Weaviate with {count} vectors in 'Knowledge' class"
                        )
                else:
                    logger.warning(
                        "No Weaviate URL found - skipping Weaviate migration"
                    )
            except Exception as e:
                logger.exception(f"Failed to connect to Weaviate: {e}")

    def migrate_pinecone_vectors(self, batch_size: int = 100):
        """Migrate vectors from Pinecone to Snowflake"""
        if not self.pinecone_index:
            logger.info("Skipping Pinecone migration - not connected")
            return

        logger.info(f"\n{'='*60}")
        logger.info("🔄 MIGRATING PINECONE VECTORS")
        logger.info(f"{'='*60}")

        try:
            # Fetch all vectors (paginated)
            cursor = None
            total_migrated = 0

            while True:
                # Fetch a batch
                logger.info(f"Fetching batch (cursor: {cursor})...")

                if cursor:
                    results = self.pinecone_index.fetch(
                        ids=[], namespace="", limit=batch_size  # Fetch by pagination
                    )
                else:
                    # For first batch, we need to query
                    # Pinecone doesn't have a great way to fetch all, so we'll query with a dummy vector
                    dummy_vector = [0.0] * 768  # Assuming 768 dimensions
                    results = self.pinecone_index.query(
                        vector=dummy_vector,
                        top_k=batch_size,
                        include_values=True,
                        include_metadata=True,
                    )

                if not results or "matches" not in results or not results["matches"]:
                    logger.info("No more vectors to migrate from Pinecone")
                    break

                # Process this batch
                batch_vectors = []
                for match in results["matches"]:
                    vector_data = {
                        "id": match.get("id"),
                        "values": match.get("values"),
                        "metadata": match.get("metadata", {}),
                        "score": match.get("score"),
                    }
                    batch_vectors.append(vector_data)

                # Migrate the batch
                if not self.dry_run:
                    migrated = self._migrate_batch_to_snowflake(
                        batch_vectors, source="pinecone"
                    )
                    total_migrated += migrated
                else:
                    logger.info(f"[DRY RUN] Would migrate {len(batch_vectors)} vectors")
                    total_migrated += len(batch_vectors)

                # Check if we have more
                if len(results["matches"]) < batch_size:
                    break

                # Update cursor for next batch
                cursor = results["matches"][-1]["id"]

            logger.info(f"✅ Migrated {total_migrated} vectors from Pinecone")

        except Exception as e:
            logger.exception(f"Error during Pinecone migration: {e}")

    def migrate_weaviate_vectors(self, batch_size: int = 100):
        """Migrate vectors from Weaviate to Snowflake"""
        if not self.weaviate_client:
            logger.info("Skipping Weaviate migration - not connected")
            return

        logger.info(f"\n{'='*60}")
        logger.info("🔄 MIGRATING WEAVIATE VECTORS")
        logger.info(f"{'='*60}")

        try:
            # Weaviate pagination
            offset = 0
            total_migrated = 0

            while True:
                # Fetch a batch
                logger.info(f"Fetching batch (offset: {offset})...")

                result = (
                    self.weaviate_client.query.get(
                        "Knowledge", ["content", "source", "metadata"]
                    )
                    .with_additional(["id", "vector"])
                    .with_limit(batch_size)
                    .with_offset(offset)
                    .do()
                )

                if (
                    not result
                    or "data" not in result
                    or not result["data"]["Get"]["Knowledge"]
                ):
                    logger.info("No more vectors to migrate from Weaviate")
                    break

                # Process this batch
                batch_vectors = []
                for obj in result["data"]["Get"]["Knowledge"]:
                    vector_data = {
                        "id": obj["_additional"]["id"],
                        "values": obj["_additional"]["vector"],
                        "metadata": {
                            "content": obj.get("content", ""),
                            "source": obj.get("source", ""),
                            "weaviate_metadata": obj.get("metadata", {}),
                        },
                    }
                    batch_vectors.append(vector_data)

                # Migrate the batch
                if not self.dry_run:
                    migrated = self._migrate_batch_to_snowflake(
                        batch_vectors, source="weaviate"
                    )
                    total_migrated += migrated
                else:
                    logger.info(f"[DRY RUN] Would migrate {len(batch_vectors)} vectors")
                    total_migrated += len(batch_vectors)

                # Update offset
                offset += batch_size

                # Check if we got a full batch
                if len(result["data"]["Get"]["Knowledge"]) < batch_size:
                    break

            logger.info(f"✅ Migrated {total_migrated} vectors from Weaviate")

        except Exception as e:
            logger.exception(f"Error during Weaviate migration: {e}")

    def _migrate_batch_to_snowflake(self, vectors: list[dict], source: str) -> int:
        """Migrate a batch of vectors to Snowflake"""
        if not vectors or not self.snowflake_conn:
            return 0

        cursor = self.snowflake_conn.cursor()
        migrated = 0

        try:
            for vector_data in vectors:
                try:
                    # Extract content from metadata
                    metadata = vector_data.get("metadata", {})

                    # For Weaviate, content is in metadata
                    if source == "weaviate":
                        content = metadata.get("content", "")
                        source_info = metadata.get(
                            "source", f'weaviate_import_{vector_data["id"]}'
                        )
                    else:
                        # For Pinecone, try to get content from metadata
                        content = metadata.get(
                            "text",
                            metadata.get("content", f'Vector {vector_data["id"]}'),
                        )
                        source_info = metadata.get(
                            "source", f'pinecone_import_{vector_data["id"]}'
                        )

                    # Prepare metadata for Snowflake
                    snowflake_metadata = {
                        "original_id": vector_data["id"],
                        "migrated_from": source,
                        "migration_date": self.current_date.isoformat(),
                        "original_metadata": metadata,
                    }

                    # Get the vector values
                    vector_values = vector_data.get("values", [])

                    # Skip if no vector
                    if not vector_values:
                        logger.warning(
                            f"Skipping vector {vector_data['id']} - no values"
                        )
                        continue

                    # Convert vector to string format for Snowflake
                    vector_str = "[" + ",".join(map(str, vector_values)) + "]"

                    # Insert into Snowflake
                    sql = """
                        INSERT INTO AI_MEMORY.VECTORS.KNOWLEDGE_BASE
                        (content, embedding, metadata, source, created_at)
                        VALUES (?, TO_VECTOR(?, 'FLOAT', 768), PARSE_JSON(?), ?, ?)
                    """

                    cursor.execute(
                        sql,
                        (
                            content,
                            vector_str,
                            json.dumps(snowflake_metadata),
                            source_info,
                            self.current_date,
                        ),
                    )

                    migrated += 1

                except Exception as e:
                    logger.exception(
                        f"Failed to migrate vector {vector_data.get('id')}: {e}"
                    )
                    self.stats["failed_vectors"] += 1

            # Commit the batch
            self.snowflake_conn.commit()
            self.stats["migrated_vectors"] += migrated
            logger.info(f"✅ Migrated batch of {migrated} vectors to Snowflake")

        except Exception as e:
            self.snowflake_conn.rollback()
            logger.exception(f"Batch migration failed: {e}")
        finally:
            cursor.close()

        return migrated

    def verify_migration(self):
        """Verify the migration was successful"""
        logger.info(f"\n{'='*60}")
        logger.info("🔍 VERIFYING MIGRATION")
        logger.info(f"{'='*60}")

        if not self.snowflake_conn:
            logger.error("No Snowflake connection for verification")
            return

        cursor = self.snowflake_conn.cursor(DictCursor)
        try:
            # Count migrated vectors by source
            sql = """
                SELECT
                    metadata:migrated_from::string as source,
                    COUNT(*) as count
                FROM AI_MEMORY.VECTORS.KNOWLEDGE_BASE
                WHERE metadata:migrated_from IS NOT NULL
                GROUP BY metadata:migrated_from
            """

            cursor.execute(sql)
            results = cursor.fetchall()

            logger.info("\nMigrated vectors by source:")
            for row in results:
                # DictCursor returns dict-like objects
                if isinstance(row, dict):
                    source_name = row.get("SOURCE", "unknown")
                    count = row.get("COUNT", 0)
                else:
                    # Fallback for tuple results
                    source_name = row[0] if len(row) > 0 else "unknown"
                    count = row[1] if len(row) > 1 else 0
                logger.info(f"  {source_name}: {count}")

            # Test search functionality
            logger.info("\nTesting search functionality...")
            memory = get_unified_memory_service()
            test_results = memory.search_knowledge("test query", limit=5)
            logger.info(f"✅ Search test returned {len(test_results)} results")

        except Exception as e:
            logger.exception(f"Verification failed: {e}")
        finally:
            cursor.close()

    def print_summary(self):
        """Print migration summary"""
        duration = time.time() - self.stats["start_time"]

        logger.info(f"\n{'='*60}")
        logger.info("📊 MIGRATION SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"Date: {self.current_date} (July 9, 2025)")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info("\nSource Vectors:")
        logger.info(f"  Pinecone: {self.stats['pinecone_vectors']}")
        logger.info(f"  Weaviate: {self.stats['weaviate_vectors']}")
        logger.info("\nMigration Results:")
        logger.info(f"  Migrated: {self.stats['migrated_vectors']}")
        logger.info(f"  Failed: {self.stats['failed_vectors']}")

        if self.dry_run:
            logger.info("\n⚠️ This was a DRY RUN - no data was actually migrated")
        else:
            logger.info("\n✅ Migration complete!")

    def cleanup(self):
        """Clean up connections"""
        if self.snowflake_conn:
            self.snowflake_conn.close()


def main():
    """Main migration function"""
    parser = argparse.ArgumentParser(description="Migrate vectors to Snowflake")
    parser.add_argument(
        "--source",
        choices=["pinecone", "weaviate", "all"],
        default="all",
        help="Source to migrate from",
    )
    parser.add_argument(
        "--batch-size", type=int, default=100, help="Batch size for migration"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Run without actually migrating data"
    )
    parser.add_argument(
        "--verify-only", action="store_true", help="Only verify existing migration"
    )

    args = parser.parse_args()

    # Create migrator
    migrator = VectorMigrator(dry_run=args.dry_run)

    try:
        # Initialize connections
        migrator.initialize_connections()

        if args.verify_only:
            # Just verify
            migrator.verify_migration()
        else:
            # Run migration
            if args.source in ["pinecone", "all"]:
                migrator.migrate_pinecone_vectors(batch_size=args.batch_size)

            if args.source in ["weaviate", "all"]:
                migrator.migrate_weaviate_vectors(batch_size=args.batch_size)

            # Verify
            if not args.dry_run:
                migrator.verify_migration()

        # Print summary
        migrator.print_summary()

    except Exception as e:
        logger.exception(f"Migration failed: {e}")
        sys.exit(1)
    finally:
        migrator.cleanup()

    logger.info("\n🎉 Migration process complete!")
    logger.info("Next steps:")
    logger.info("1. Run validation: python scripts/validate_memory_architecture.py")
    logger.info("2. Update services to use UnifiedMemoryService")
    logger.info("3. Remove Pinecone/Weaviate dependencies from pyproject.toml")
    logger.info("4. Remove Pinecone/Weaviate secrets from Pulumi ESC")


if __name__ == "__main__":
    main()
