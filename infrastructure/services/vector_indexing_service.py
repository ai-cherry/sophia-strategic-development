# File: backend/services/vector_indexing_service.py

import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Any

from core.config_manager import get_config_value
from infrastructure.integrations.gong_api_client import GongAPIClient
from infrastructure.services.semantic_layer_service import SemanticLayerService
from backend.services.unified_memory_service_v2 import UnifiedMemoryServiceV2

logger = logging.getLogger(__name__)


@dataclass
class VectorDocument:
    """Document structure for vector indexing"""

    id: str
    content: str
    metadata: dict[str, Any]
    source_type: str
    embedding: list[float] | None = None


class VectorIndexingService:
    """
    Comprehensive vector indexing service for all unstructured content.
    Integrates with Weaviate vector database and pgvector.
    """

    def __init__(self):
        self.semantic_service = SemanticLayerService()
        self.memory_service = UnifiedMemoryServiceV2()
        gong_api_key = get_config_value("gong_access_key")
        if not gong_api_key:
            logger.warning(
                "Gong API key not configured. Gong integration will be disabled."
            )
            self.gong_client = None
        else:
            self.gong_client = GongAPIClient(api_key=gong_api_key)

    async def _create_weaviate_collection(self, config: dict[str, Any]) -> None:
        """Creates a Weaviate collection for vector storage."""
        collection_name = config["name"]
        
        # Initialize memory service which handles Weaviate
        await self.memory_service.initialize()
        
        logger.info(
            f"Weaviate collection '{collection_name}' ready via UnifiedMemoryServiceV2"
        )
        # The memory service already handles schema creation
        await asyncio.sleep(0.1)  # Simulate async operation

    async def initialize_vector_indexes(self) -> bool:
        """Initialize vector search indexes for all content types"""
        try:
            # Create Weaviate collections for different content types
            index_configs = [
                {
                    "name": "SLACK_MESSAGES_INDEX",
                    "table": "SLACK_DATA.MESSAGES_VECTORIZED",
                    "content_column": "message_text",
                    "metadata_columns": [
                        "channel_name",
                        "user_id",
                        "timestamp",
                        "thread_ts",
                    ],
                },
                {
                    "name": "GONG_TRANSCRIPTS_INDEX",
                    "table": "GONG_DATA.CALL_TRANSCRIPTS_VECTORIZED",
                    "content_column": "transcript_segment",
                    "metadata_columns": [
                        "call_id",
                        "speaker_id",
                        "timestamp",
                        "sentiment_score",
                    ],
                },
                {
                    "name": "KNOWLEDGE_BASE_INDEX",
                    "table": "FOUNDATIONAL_KNOWLEDGE.DOCUMENTS_VECTORIZED",
                    "content_column": "document_content",
                    "metadata_columns": [
                        "document_type",
                        "category",
                        "last_updated",
                        "author",
                    ],
                },
            ]

            for config in index_configs:
                await self._create_weaviate_collection(config)

            logger.info("Vector indexes initialized successfully")
            return True

        except Exception as e:
            logger.exception(f"Failed to initialize vector indexes: {e}")
            return False

    async def index_slack_content(self) -> int:
        """Index all Slack messages with vector embeddings"""
        logger.info("Starting Slack content indexing.")
        query = """
        SELECT message_id, message_text, channel_name, user_id, timestamp, thread_ts
        FROM SLACK_DATA.MESSAGES
        WHERE message_text IS NOT NULL AND LENGTH(message_text) > 10
        ORDER BY timestamp DESC
        LIMIT 10000;
        """

        messages = await self.semantic_service._execute_query(query)
        indexed_count = 0

        for message in messages:
            try:
                # Generate embedding using memory service
                embedding = await self.memory_service.generate_embedding(
                    message["message_text"]
                )

                if embedding:
                    # Store vectorized content
                    insert_query = """
                    INSERT INTO SLACK_DATA.MESSAGES_VECTORIZED
                    (message_id, message_text, embedding, channel_name, user_id, timestamp, thread_ts)
                    VALUES (%s, %s, %s, %s, %s, %s, %s);
                    """

                    await self.semantic_service._execute_query(
                        insert_query,
                        [
                            message["message_id"],
                            message["message_text"],
                            json.dumps(embedding),
                            message["channel_name"],
                            message["user_id"],
                            message["timestamp"],
                            message["thread_ts"],
                        ],
                    )

                    indexed_count += 1
                else:
                    logger.warning(
                        f"Could not generate embedding for message {message['message_id']}"
                    )

            except Exception as e:
                logger.warning(f"Failed to index message {message['message_id']}: {e}")
                continue

        logger.info(f"Indexed {indexed_count} Slack messages")
        return indexed_count

    async def index_gong_transcripts(self) -> int:
        """Index Gong call transcripts with vector embeddings"""
        logger.info("Starting Gong transcript indexing.")
        query = """
        SELECT call_id, transcript, call_date, participants, sentiment_score
        FROM GONG_DATA.CALLS
        WHERE transcript IS NOT NULL
        ORDER BY call_date DESC
        LIMIT 1000;
        """

        calls = await self.semantic_service._execute_query(query)
        indexed_count = 0

        for call in calls:
            # Segment transcript into chunks
            segments = self._segment_transcript(call["transcript"])

            for i, segment in enumerate(segments):
                try:
                    # Generate embedding using memory service
                    embedding = await self.memory_service.generate_embedding(
                        segment
                    )

                    if embedding:
                        # Store vectorized segment
                        insert_query = """
                        INSERT INTO GONG_DATA.CALL_TRANSCRIPTS_VECTORIZED
                        (call_id, segment_id, transcript_segment, embedding, call_date,
                         participants, sentiment_score, segment_order)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                        """

                        await self.semantic_service._execute_query(
                            insert_query,
                            [
                                call["call_id"],
                                f"{call['call_id']}_segment_{i}",
                                segment,
                                json.dumps(embedding),
                                call["call_date"],
                                json.dumps(call["participants"]),
                                call["sentiment_score"],
                                i,
                            ],
                        )

                        indexed_count += 1
                    else:
                        logger.warning(
                            f"Could not generate embedding for call segment {call['call_id']}_{i}"
                        )
                except Exception as e:
                    logger.warning(
                        f"Failed to index call segment {call['call_id']}_{i}: {e}"
                    )
                    continue

        logger.info(f"Indexed {indexed_count} Gong transcript segments")
        return indexed_count

    def _segment_transcript(self, transcript: str, max_length: int = 500) -> list[str]:
        """Segment long transcripts into searchable chunks"""
        if not transcript:
            return []

        sentences = transcript.split(". ")
        segments = []
        current_segment = ""

        for sentence in sentences:
            if not sentence:
                continue
            if len(current_segment) + len(sentence) + 2 < max_length:
                current_segment += sentence + ". "
            else:
                if current_segment:
                    segments.append(current_segment.strip())
                current_segment = sentence + ". "

        if current_segment:
            segments.append(current_segment.strip())

        return segments

    async def health_check(self) -> dict[str, Any]:
        """Performs a health check on the vector indexing service."""
        # For now, this just checks the semantic service health.
        # A more complete implementation would check for index existence, etc.
        semantic_health = await self.semantic_service.health_check()
        if semantic_health["status"] == "healthy":
            return {"status": "healthy", "message": "Dependent services are healthy."}
        else:
            return {
                "status": "unhealthy",
                "message": "SemanticLayerService is unhealthy.",
            }
