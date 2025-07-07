# File: backend/services/comprehensive_memory_service.py

import json
import logging
from datetime import UTC
from typing import Any

from backend.agents.enhanced.data_models import MemoryRecord
from core.hierarchical_cache import HierarchicalCache
from domain.models.conversation import IntegratedConversationRecord
from shared.utils.enhanced_snowflake_cortex_service import (
    EnhancedSnowflakeCortexService,
)

try:
    import pinecone

    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False

logger = logging.getLogger(__name__)


class ComprehensiveMemoryService:
    """
    A centralized service for all memory operations, acting as a single source of truth.
    It orchestrates interactions with Snowflake, vector databases (Pinecone), and caching layers.
    """

    def __init__(self):
        self.cortex_service = EnhancedSnowflakeCortexService()
        self.cache = HierarchicalCache()
        self.pinecone_index = self._initialize_pinecone()

    def _initialize_pinecone(self) -> Any | None:
        """Initializes the Pinecone index if configured."""
        if not PINECONE_AVAILABLE:
            logger.info(
                "Pinecone SDK not installed, vector search will be limited to Snowflake."
            )
            return None

        from core.config_manager import get_config_value

        api_key = get_config_value("pinecone_api_key")
        environment = get_config_value("pinecone_environment")

        if not api_key or not environment:
            logger.warning("Pinecone API key or environment not configured.")
            return None

        try:
            pinecone.init(api_key=api_key, environment=environment)
            index_name = "sophia-ai-memory"
            if index_name not in pinecone.list_indexes():
                pinecone.create_index(name=index_name, dimension=1536, metric="cosine")
            logger.info("Pinecone initialized successfully.")
            return pinecone.Index(index_name)
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}", exc_info=True)
            return None

    async def store_memory(self, memory_record: MemoryRecord) -> str:
        """
        Stores a memory record in the appropriate backend (Snowflake, Pinecone).
        This is the single authoritative method for creating memories.
        """
        logger.info(
            f"Storing memory: {memory_record.id} in category {memory_record.category}"
        )

        # 1. Generate embedding if not present
        if not memory_record.embedding:
            memory_record.embedding = await self.cortex_service.generate_embedding(
                memory_record.content
            )

        # 2. Store in Snowflake (as the primary source of truth)
        # This is a conceptual query; a real implementation would be more complex.
        # It would insert into the MEMORY_RECORDS table from our schema.
        await self.cortex_service.execute_query(
            "INSERT INTO AI_MEMORY.MEMORY_RECORDS (MEMORY_ID, CONTENT_SUMMARY, CATEGORY, TAGS) VALUES (%s, %s, %s, %s);",
            (
                memory_record.id,
                memory_record.content[:200],
                memory_record.category,
                json.dumps(memory_record.tags),
            ),
        )

        # 3. Upsert to Pinecone for vector search
        if self.pinecone_index and memory_record.embedding:
            metadata = {
                "category": memory_record.category,
                "tags": memory_record.tags,
                "importance_score": memory_record.importance_score,
                "created_at": memory_record.created_at.isoformat(),
            }
            self.pinecone_index.upsert(
                vectors=[(memory_record.id, memory_record.embedding, metadata)]
            )
            logger.info(f"Upserted memory {memory_record.id} to Pinecone.")

        # 4. Update cache
        await self.cache.set(f"memory:{memory_record.id}", memory_record.dict())

        return memory_record.id

    async def recall_memories(
        self, query: str, top_k: int = 5, category: str | None = None
    ) -> list[MemoryRecord]:
        """
        Recalls memories using a hybrid search strategy (vector search + metadata filtering).
        """
        logger.info(f"Recalling memories for query: '{query}'")

        query_embedding = await self.cortex_service.generate_embedding(query)

        if not self.pinecone_index or not query_embedding:
            logger.warning(
                "Cannot perform vector search. Pinecone not configured or embedding failed."
            )
            return []

        pinecone_filter = {}
        if category:
            pinecone_filter["category"] = {"$eq": category}

        search_results = self.pinecone_index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            filter=pinecone_filter,
        )

        recalled_memories = []
        for match in search_results["matches"]:
            # In a real app, we'd fetch the full record from Snowflake using the ID.
            # Here, we'll reconstruct from metadata for demonstration.
            recalled_memories.append(
                MemoryRecord(
                    id=match["id"],
                    content="Full content would be fetched from Snowflake.",
                    category=match["metadata"].get("category"),
                    tags=match["metadata"].get("tags", []),
                    importance_score=match["metadata"].get("importance_score", 0.5),
                    # ... and other fields
                )
            )

        logger.info(f"Recalled {len(recalled_memories)} memories.")
        return recalled_memories

    async def get_memory_by_id(self, memory_id: str) -> MemoryRecord | None:
        """Retrieves a single memory by its unique ID."""
        cached_memory = await self.cache.get(f"memory:{memory_id}")
        if cached_memory:
            return MemoryRecord(**cached_memory)

        # If not in cache, fetch from Snowflake
        # Conceptual query
        result = await self.cortex_service.execute_query(
            "SELECT * FROM AI_MEMORY.MEMORY_RECORDS WHERE MEMORY_ID = %s;", (memory_id,)
        )
        if result:
            # Reconstruct the MemoryRecord object
            # ...
            return MemoryRecord(**result[0])
        return None

    # =====================================================
    # GONG & SLACK DATA INTEGRATION METHODS
    # =====================================================

    async def get_raw_gong_data(self, limit: int = 100) -> list[dict]:
        """Retrieve raw Gong data from Snowflake for processing."""
        try:
            query = f"""
            SELECT call_id, title, started_at, duration, transcript, participants,
                   meeting_url, call_type
            FROM SOPHIA_GONG_RAW.gong_calls
            WHERE transcript IS NOT NULL AND transcript != ''
            ORDER BY started_at DESC
            LIMIT {limit}
            """
            results = await self.cortex_service.execute_query(query)
            logger.info(f"Retrieved {len(results) if results else 0} Gong call records")
            return results or []
        except Exception as e:
            logger.error(f"Failed to retrieve Gong data: {e}", exc_info=True)
            return []

    async def get_raw_slack_data(self, limit: int = 100) -> list[dict]:
        """Retrieve raw Slack data from Snowflake for processing."""
        try:
            query = f"""
            SELECT channel_id, channel_name, user_id, text, ts, thread_ts, type
            FROM SOPHIA_SLACK_RAW.slack_messages
            WHERE text IS NOT NULL AND text != ''
            ORDER BY ts DESC
            LIMIT {limit}
            """
            results = await self.cortex_service.execute_query(query)
            logger.info(
                f"Retrieved {len(results) if results else 0} Slack message records"
            )
            return results or []
        except Exception as e:
            logger.error(f"Failed to retrieve Slack data: {e}", exc_info=True)
            return []

    async def process_and_vectorize_gong_data(self, batch_size: int = 50) -> int:
        """
        Process raw Gong call data and convert to memory records with embeddings.
        Returns the number of records processed.
        """
        logger.info("Starting Gong data processing and vectorization")
        processed_count = 0

        try:
            raw_gong_data = await self.get_raw_gong_data(limit=batch_size)

            for call_data in raw_gong_data:
                try:
                    # Convert to GongCallData model
                    from datetime import datetime

                    from backend.agents.enhanced.data_models import GongCallData

                    gong_call = GongCallData(
                        call_id=call_data.get("call_id", ""),
                        title=call_data.get("title", "Untitled Call"),
                        started_at=call_data.get("started_at", datetime.now(UTC)),
                        duration=call_data.get("duration", 0),
                        transcript=call_data.get("transcript", ""),
                        participants=call_data.get("participants", []),
                        meeting_url=call_data.get("meeting_url"),
                        call_type=call_data.get("call_type"),
                    )

                    # Convert to memory record
                    memory_record = gong_call.to_memory_record()

                    # Store in memory system
                    await self.store_memory(memory_record)
                    processed_count += 1

                    logger.debug(f"Processed Gong call: {gong_call.call_id}")

                except Exception as e:
                    logger.error(
                        f"Failed to process Gong call {call_data.get('call_id', 'unknown')}: {e}"
                    )
                    continue

            logger.info(f"Successfully processed {processed_count} Gong call records")
            return processed_count

        except Exception as e:
            logger.error(f"Failed to process Gong data batch: {e}", exc_info=True)
            return processed_count

    async def process_and_vectorize_slack_data(self, batch_size: int = 100) -> int:
        """
        Process raw Slack message data and convert to memory records with embeddings.
        Returns the number of records processed.
        """
        logger.info("Starting Slack data processing and vectorization")
        processed_count = 0

        try:
            raw_slack_data = await self.get_raw_slack_data(limit=batch_size)

            for message_data in raw_slack_data:
                try:
                    # Convert to SlackMessageData model
                    from datetime import datetime

                    from backend.agents.enhanced.data_models import SlackMessageData

                    # Convert timestamp from Slack format
                    timestamp = datetime.fromtimestamp(float(message_data.get("ts", 0)))

                    slack_message = SlackMessageData(
                        message_id=f"{message_data.get('channel_id', '')}_{message_data.get('ts', '')}",
                        channel_id=message_data.get("channel_id", ""),
                        channel_name=message_data.get("channel_name", "unknown"),
                        user_id=message_data.get("user_id", ""),
                        text=message_data.get("text", ""),
                        timestamp=timestamp,
                        thread_ts=message_data.get("thread_ts"),
                        message_type=message_data.get("type", "message"),
                    )

                    # Only process messages with substantial content
                    if len(slack_message.text.strip()) < 10:
                        continue

                    # Convert to memory record
                    memory_record = slack_message.to_memory_record()

                    # Store in memory system
                    await self.store_memory(memory_record)
                    processed_count += 1

                    logger.debug(f"Processed Slack message: {slack_message.message_id}")

                except Exception as e:
                    logger.error(
                        f"Failed to process Slack message {message_data.get('ts', 'unknown')}: {e}"
                    )
                    continue

            logger.info(
                f"Successfully processed {processed_count} Slack message records"
            )
            return processed_count

        except Exception as e:
            logger.error(f"Failed to process Slack data batch: {e}", exc_info=True)
            return processed_count

    async def create_integrated_conversation_memories(self, limit: int = 50) -> int:
        """
        Create integrated conversation memories that combine insights from multiple platforms.
        Returns the number of integrated memories created.
        """
        logger.info("Creating integrated conversation memories")
        created_count = 0

        try:
            # Query the integrated conversations view
            query = f"""
            SELECT conversation_id, source_platform, conversation_time,
                   conversation_title, conversation_content, participants,
                   duration_seconds, platform_metadata
            FROM SOPHIA_AI_CORE.AI_MEMORY.INTEGRATED_CONVERSATIONS
            ORDER BY conversation_time DESC
            LIMIT {limit}
            """

            results = await self.cortex_service.execute_query(query)

            for conv_data in results or []:
                try:
                    from backend.agents.enhanced.data_models import (
                        IntegratedConversationRecord,
                    )

                    integrated_conv = IntegratedConversationRecord(
                        conversation_id=conv_data.get("conversation_id", ""),
                        source_platform=conv_data.get("source_platform", ""),
                        conversation_time=conv_data.get("conversation_time"),
                        conversation_title=conv_data.get("conversation_title", ""),
                        conversation_content=conv_data.get("conversation_content", ""),
                        participants=conv_data.get("participants", []),
                        duration_seconds=conv_data.get("duration_seconds", 0),
                        platform_metadata=conv_data.get("platform_metadata", {}),
                    )

                    # Generate AI insights for the conversation
                    insights = await self._generate_conversation_insights(
                        integrated_conv
                    )
                    integrated_conv.key_insights = insights.get("insights", [])
                    integrated_conv.action_items = insights.get("action_items", [])
                    integrated_conv.sentiment_score = insights.get("sentiment_score")
                    integrated_conv.summary = insights.get("summary")

                    # Convert to memory record and store
                    memory_record = integrated_conv.to_memory_record()
                    await self.store_memory(memory_record)
                    created_count += 1

                    logger.debug(
                        f"Created integrated memory: {integrated_conv.conversation_id}"
                    )

                except Exception as e:
                    logger.error(
                        f"Failed to create integrated memory for {conv_data.get('conversation_id', 'unknown')}: {e}"
                    )
                    continue

            logger.info(
                f"Successfully created {created_count} integrated conversation memories"
            )
            return created_count

        except Exception as e:
            logger.error(
                f"Failed to create integrated conversation memories: {e}", exc_info=True
            )
            return created_count

    async def _generate_conversation_insights(
        self, conversation: "IntegratedConversationRecord"
    ) -> dict:
        """Generate AI insights for a conversation using Snowflake Cortex."""
        try:
            # Use Snowflake Cortex to analyze the conversation
            analysis_prompt = f"""
            Analyze this {conversation.source_platform} conversation and provide:
            1. Key insights (max 3)
            2. Action items (max 3)
            3. Sentiment score (0-1)
            4. Brief summary (max 100 words)

            Title: {conversation.conversation_title}
            Content: {conversation.conversation_content[:1000]}
            Participants: {", ".join(conversation.participants)}
            """

            analysis_result = await self.cortex_service.generate_completion(
                analysis_prompt
            )

            # Parse the analysis result (this would need more sophisticated parsing in production)
            return {
                "insights": [
                    "Insight 1",
                    "Insight 2",
                ],  # Placeholder - would parse from analysis_result
                "action_items": [
                    "Action 1"
                ],  # Placeholder - would parse from analysis_result
                "sentiment_score": 0.7,  # Placeholder - would extract from analysis_result
                "summary": (
                    analysis_result[:100] if analysis_result else "No summary available"
                ),
            }

        except Exception as e:
            logger.error(
                f"Failed to generate insights for conversation {conversation.conversation_id}: {e}"
            )
            return {
                "insights": [],
                "action_items": [],
                "sentiment_score": None,
                "summary": None,
            }

    async def search_cross_platform_memories(
        self, query: str, platforms: list[str] = None, top_k: int = 10
    ) -> list[MemoryRecord]:
        """
        Search for memories across multiple platforms (Gong, Slack, etc.).
        """
        logger.info(
            f"Searching cross-platform memories for: '{query}' across platforms: {platforms}"
        )

        try:
            # Build platform filter
            platform_filter = ""
            if platforms:
                platform_conditions = [
                    f"source_system = '{platform}'" for platform in platforms
                ]
                platform_filter = f"AND ({' OR '.join(platform_conditions)})"

            # Search in Snowflake using vector similarity (conceptual)
            search_query = f"""
            SELECT memory_id, content, category, tags, importance_score, source_system,
                   additional_metadata, created_at
            FROM SOPHIA_AI_CORE.AI_MEMORY.MEMORY_RECORDS
            WHERE content ILIKE '%{query}%'
            {platform_filter}
            ORDER BY importance_score DESC, created_at DESC
            LIMIT {top_k}
            """

            results = await self.cortex_service.execute_query(search_query)

            memories = []
            for result in results or []:
                memory = MemoryRecord(
                    id=result.get("memory_id", ""),
                    content=result.get("content", ""),
                    category=result.get("category", ""),
                    tags=result.get("tags", []),
                    importance_score=result.get("importance_score", 0.5),
                    source_system=result.get("source_system", ""),
                    created_at=result.get("created_at"),
                    additional_metadata=result.get("additional_metadata", {}),
                )
                memories.append(memory)

            logger.info(f"Found {len(memories)} cross-platform memories")
            return memories

        except Exception as e:
            logger.error(
                f"Failed to search cross-platform memories: {e}", exc_info=True
            )
            return []

    async def get_platform_memory_stats(self) -> dict:
        """Get statistics about memories from different platforms."""
        try:
            stats_query = """
            SELECT
                source_system,
                COUNT(*) as total_memories,
                AVG(importance_score) as avg_importance,
                MAX(created_at) as latest_memory,
                MIN(created_at) as earliest_memory
            FROM SOPHIA_AI_CORE.AI_MEMORY.MEMORY_RECORDS
            GROUP BY source_system
            ORDER BY total_memories DESC
            """

            results = await self.cortex_service.execute_query(stats_query)

            stats = {}
            for result in results or []:
                platform = result.get("source_system", "unknown")
                stats[platform] = {
                    "total_memories": result.get("total_memories", 0),
                    "avg_importance": result.get("avg_importance", 0.0),
                    "latest_memory": result.get("latest_memory"),
                    "earliest_memory": result.get("earliest_memory"),
                }

            logger.info(f"Retrieved memory stats for {len(stats)} platforms")
            return stats

        except Exception as e:
            logger.error(f"Failed to get platform memory stats: {e}", exc_info=True)
            return {}
