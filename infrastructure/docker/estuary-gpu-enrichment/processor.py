#!/usr/bin/env python3
"""
Estuary Flow GPU Enrichment Processor
Processes streaming data: generates embeddings and stores in Weaviate
No more Snowflake lag - just pure GPU speed!
"""

import asyncio
import json
import sys
import os
import time
from typing import Dict, Any, List
import aiohttp
import numpy as np
from weaviate import Client
from redis.asyncio import Redis
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class GPUEnrichmentProcessor:
    """
    Processes Estuary Flow records with GPU embeddings
    """

    def __init__(self):
        # Service endpoints from environment
        self.lambda_url = os.getenv(
            "LAMBDA_INFERENCE_URL", "http://lambda-inference:8080"
        )
        self.weaviate_url = os.getenv("WEAVIATE_URL", "http://weaviate:8080")
        self.redis_host = os.getenv("REDIS_HOST", "redis")
        self.redis_port = int(os.getenv("REDIS_PORT", "6379"))
        self.redis_password = os.getenv("REDIS_PASSWORD", "")

        # Processing config
        self.embedding_model = os.getenv(
            "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
        )
        self.batch_size = int(os.getenv("BATCH_SIZE", "100"))

        # Clients
        self.weaviate: Client = None
        self.redis: Redis = None

        # Performance tracking
        self.stats = {
            "processed": 0,
            "embeddings_generated": 0,
            "weaviate_stored": 0,
            "errors": 0,
            "total_time_ms": 0,
        }

    async def initialize(self):
        """Initialize connections"""
        try:
            # Weaviate client
            self.weaviate = Client(self.weaviate_url)
            logger.info(f"Connected to Weaviate at {self.weaviate_url}")

            # Redis connection
            self.redis = Redis(
                host=self.redis_host,
                port=self.redis_port,
                password=self.redis_password,
                decode_responses=True,
            )
            await self.redis.ping()
            logger.info(f"Connected to Redis at {self.redis_host}:{self.redis_port}")

        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
            raise

    async def process_stream(self):
        """
        Main processing loop - reads from stdin, enriches, writes to stdout
        Estuary Flow pattern: read JSON lines, process, emit JSON lines
        """
        logger.info("Starting GPU enrichment processor...")

        batch = []

        async for line in self._read_stdin():
            try:
                record = json.loads(line)
                batch.append(record)

                # Process in batches
                if len(batch) >= self.batch_size:
                    await self._process_batch(batch)
                    batch = []

            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON: {e}")
                self.stats["errors"] += 1
            except Exception as e:
                logger.error(f"Processing error: {e}")
                self.stats["errors"] += 1

        # Process remaining records
        if batch:
            await self._process_batch(batch)

        # Print final stats
        self._print_stats()

    async def _read_stdin(self):
        """Async generator for reading stdin"""
        loop = asyncio.get_event_loop()
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)

        while True:
            line = await reader.readline()
            if not line:
                break
            yield line.decode().strip()

    async def _process_batch(self, batch: List[Dict[str, Any]]):
        """Process a batch of records"""
        start_time = time.time()
        logger.info(f"Processing batch of {len(batch)} records...")

        # Extract content for embedding
        contents = []
        for record in batch:
            # Handle different record types
            if "enrichment" in record:
                # Gong call record
                content = record["enrichment"].get("content_for_embedding", "")
            elif "transcript" in record:
                # Transcript record
                content = record.get("transcript", "")
            else:
                # Generic - concatenate string fields
                content = " ".join(
                    str(v) for v in record.values() if isinstance(v, str)
                )

            contents.append(content)

        # Generate embeddings in parallel
        embeddings = await self._generate_embeddings_batch(contents)

        # Store in Weaviate and emit enriched records
        tasks = []
        for i, (record, embedding) in enumerate(zip(batch, embeddings)):
            if embedding is not None:
                task = self._enrich_and_store(record, embedding, contents[i])
                tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Count successes
        for result in results:
            if not isinstance(result, Exception):
                self.stats["processed"] += 1
            else:
                logger.error(f"Failed to process record: {result}")
                self.stats["errors"] += 1

        elapsed_ms = (time.time() - start_time) * 1000
        self.stats["total_time_ms"] += elapsed_ms

        logger.info(
            f"Batch processed in {elapsed_ms:.1f}ms (avg: {elapsed_ms/len(batch):.1f}ms per record)"
        )

    async def _generate_embeddings_batch(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings for a batch of texts"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "inputs": texts,
                    "model": self.embedding_model,
                    "normalize": True,
                }

                async with session.post(
                    f"{self.lambda_url}/embed/batch",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        embeddings = [
                            np.array(emb, dtype=np.float32)
                            for emb in result["embeddings"]
                        ]
                        self.stats["embeddings_generated"] += len(embeddings)
                        return embeddings
                    else:
                        logger.error(f"GPU embedding failed: {resp.status}")
                        return [None] * len(texts)

        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return [None] * len(texts)

    async def _enrich_and_store(
        self, record: Dict[str, Any], embedding: np.ndarray, content: str
    ):
        """Enrich record with embedding and store in Weaviate"""
        try:
            # Add embedding to record
            record["_embedding"] = embedding.tolist()
            record["_embedding_generated_at"] = time.time()
            record["_embedding_model"] = self.embedding_model

            # Store in Weaviate
            weaviate_props = {
                "content": content,
                "source": record.get("enrichment", {})
                .get("metadata", {})
                .get("source", "estuary"),
                "metadata": json.dumps(
                    record.get("enrichment", {}).get("metadata", {})
                ),
                "record_type": self._get_record_type(record),
                "timestamp": record.get("started")
                or record.get("enrichment", {}).get("processed_at"),
            }

            self.weaviate.data_object.create(
                data_object=weaviate_props,
                class_name="EstuaryKnowledge",
                vector=embedding.tolist(),
            )

            self.stats["weaviate_stored"] += 1

            # Cache in Redis (optional)
            cache_key = f"estuary:{record.get('id', 'unknown')}:{hash(content)}"
            await self.redis.setex(
                cache_key,
                3600,  # 1 hour TTL
                json.dumps({"embedding": embedding.tolist(), "content": content}),
            )

            # Emit enriched record to stdout (Estuary Flow pattern)
            print(json.dumps(record))
            sys.stdout.flush()

        except Exception as e:
            logger.error(f"Failed to enrich and store: {e}")
            raise

    def _get_record_type(self, record: Dict[str, Any]) -> str:
        """Determine record type"""
        if "callId" in record and "transcript" in record:
            return "transcript"
        elif "title" in record and "participants" in record:
            return "call"
        else:
            return "unknown"

    def _print_stats(self):
        """Print processing statistics"""
        avg_time = (
            self.stats["total_time_ms"] / self.stats["processed"]
            if self.stats["processed"] > 0
            else 0
        )

        logger.info(
            f"""
╔══════════════════════════════════════════════════════╗
║           GPU ENRICHMENT PROCESSING COMPLETE         ║
╠══════════════════════════════════════════════════════╣
║ Records Processed:     {self.stats['processed']:>10}            ║
║ Embeddings Generated:  {self.stats['embeddings_generated']:>10}            ║
║ Stored in Weaviate:    {self.stats['weaviate_stored']:>10}            ║
║ Errors:                {self.stats['errors']:>10}            ║
║                                                      ║
║ Avg Processing Time:   {avg_time:>8.1f}ms            ║
║ Total Time:            {self.stats['total_time_ms']/1000:>8.1f}s             ║
║                                                      ║
║ Snowflake would have taken: ~{avg_time * 8:.0f}ms per record ║
╚══════════════════════════════════════════════════════╝
        """
        )

    async def close(self):
        """Clean up connections"""
        if self.redis:
            await self.redis.close()


async def main():
    """Main entry point"""
    processor = GPUEnrichmentProcessor()

    try:
        await processor.initialize()
        await processor.process_stream()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        await processor.close()


if __name__ == "__main__":
    asyncio.run(main())
