"""Main handler for ai_memory_v2 MCP server."""

import hashlib
import logging
from datetime import datetime
from typing import Any

import numpy as np

from infrastructure.mcp_servers.ai_memory_v2.config import settings
from infrastructure.mcp_servers.ai_memory_v2.models.data_models import (
    BulkMemoryRequest,
    MemoryCategory,
    MemoryEntry,
    MemoryStats,
    MemoryUpdateRequest,
    SearchRequest,
    SearchResult,
)

logger = logging.getLogger(__name__)


class AiMemoryV2Handler:
    """Handler for ai_memory_v2 operations."""

    def __init__(self):
        """Initialize handler."""
        self.openai_client = None
        self.db_session = None

    async def initialize(self):
        """Initialize handler with required clients."""
        if settings.OPENAI_API_KEY:
            import openai

            self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            logger.warning("No OpenAI API key configured - embeddings will be disabled")

        logger.info("AiMemoryV2 handler initialized")

    async def store_memory(
        self,
        content: str,
        category: MemoryCategory | None = None,
        metadata: dict[str, Any] | None = None,
        tags: list[str] | None = None,
        user_id: str | None = None,
        source: str | None = None,
    ) -> MemoryEntry:
        """Store a single memory with embedding."""
        try:
            # Validate content length
            if len(content) > settings.MAX_MEMORY_SIZE:
                raise ValueError(
                    f"Content exceeds maximum size of {settings.MAX_MEMORY_SIZE} characters"
                )

            # Generate embedding if OpenAI is configured
            embedding = None
            if self.openai_client:
                embedding = await self._generate_embedding(content)

            # Auto-categorize if enabled
            if settings.ENABLE_AUTO_CATEGORIZATION and not category:
                category = await self._auto_categorize(content)

            # Check for duplicates if enabled
            if settings.ENABLE_DUPLICATE_DETECTION:
                duplicate_id = await self._check_duplicate(content, embedding)
                if duplicate_id:
                    logger.info(f"Duplicate memory detected: {duplicate_id}")
                    # Return existing memory instead of creating new
                    return await self._get_memory_by_id(duplicate_id)

            # Create memory entry
            memory = MemoryEntry(
                content=content,
                embedding=embedding.tolist() if embedding is not None else None,
                category=category or MemoryCategory.GENERAL,
                metadata=metadata or {},
                tags=tags or [],
                user_id=user_id,
                source=source,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            # Store in database (placeholder - actual DB implementation needed)
            memory.id = await self._store_in_db(memory)

            logger.info(f"Stored memory {memory.id} with category {memory.category}")
            return memory

        except Exception as e:
            logger.exception(f"Error storing memory: {e}")
            raise

    async def search_memories(self, request: SearchRequest) -> list[SearchResult]:
        """Search memories using semantic similarity and filters."""
        try:
            # Generate query embedding
            query_embedding = None
            if self.openai_client:
                query_embedding = await self._generate_embedding(request.query)

            # Perform search (placeholder - actual DB implementation needed)
            results = await self._search_in_db(
                query_embedding=query_embedding,
                limit=request.limit,
                threshold=request.threshold,
                categories=request.categories,
                tags=request.tags,
                user_id=request.user_id,
                date_from=request.date_from,
                date_to=request.date_to,
            )

            # Format results
            search_results = []
            for memory, similarity in results:
                search_results.append(
                    SearchResult(
                        memory=memory,
                        similarity=similarity,
                        highlights=self._generate_highlights(
                            memory.content, request.query
                        ),
                    )
                )

            logger.info(
                f"Found {len(search_results)} memories for query: {request.query[:50]}..."
            )
            return search_results

        except Exception as e:
            logger.exception(f"Error searching memories: {e}")
            raise

    async def get_memory_stats(self) -> MemoryStats:
        """Get memory system statistics."""
        try:
            # Get stats from database (placeholder)
            stats = await self._get_stats_from_db()

            return MemoryStats(
                total_memories=stats.get("total", 0),
                memories_by_category=stats.get("by_category", {}),
                top_tags=stats.get("top_tags", []),
                storage_size_mb=stats.get("storage_mb", 0.0),
                oldest_memory=stats.get("oldest"),
                newest_memory=stats.get("newest"),
            )

        except Exception as e:
            logger.exception(f"Error getting memory stats: {e}")
            raise

    async def bulk_store_memories(
        self, request: BulkMemoryRequest
    ) -> list[MemoryEntry]:
        """Store multiple memories in bulk."""
        stored_memories = []

        for memory_data in request.memories:
            try:
                memory = await self.store_memory(
                    content=memory_data.content,
                    category=memory_data.category,
                    metadata=memory_data.metadata,
                    tags=memory_data.tags,
                    user_id=memory_data.user_id,
                    source=memory_data.source,
                )
                stored_memories.append(memory)
            except Exception as e:
                if not request.skip_duplicates:
                    raise
                logger.warning(f"Skipping memory due to error: {e}")

        logger.info(f"Bulk stored {len(stored_memories)} memories")
        return stored_memories

    async def update_memory(
        self, memory_id: int, request: MemoryUpdateRequest
    ) -> MemoryEntry:
        """Update an existing memory."""
        try:
            # Get existing memory
            memory = await self._get_memory_by_id(memory_id)
            if not memory:
                raise ValueError(f"Memory {memory_id} not found")

            # Update fields
            if request.content is not None:
                memory.content = request.content
                # Regenerate embedding
                if self.openai_client:
                    embedding = await self._generate_embedding(request.content)
                    memory.embedding = embedding.tolist()

            if request.category is not None:
                memory.category = request.category

            if request.metadata is not None:
                memory.metadata.update(request.metadata)

            if request.tags is not None:
                memory.tags = request.tags

            memory.updated_at = datetime.utcnow()

            # Update in database
            await self._update_in_db(memory)

            logger.info(f"Updated memory {memory_id}")
            return memory

        except Exception as e:
            logger.exception(f"Error updating memory {memory_id}: {e}")
            raise

    async def delete_memory(self, memory_id: int) -> bool:
        """Delete a memory."""
        try:
            success = await self._delete_from_db(memory_id)
            if success:
                logger.info(f"Deleted memory {memory_id}")
            return success
        except Exception as e:
            logger.exception(f"Error deleting memory {memory_id}: {e}")
            raise

    # Private helper methods

    async def _generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding using OpenAI."""
        response = await self.openai_client.embeddings.create(
            model=settings.EMBEDDING_MODEL, input=text
        )
        return np.array(response.data[0].embedding)

    async def _auto_categorize(self, content: str) -> MemoryCategory:
        """Auto-categorize content using simple heuristics."""
        content_lower = content.lower()

        # Simple keyword-based categorization
        if any(
            word in content_lower
            for word in ["code", "function", "api", "bug", "error"]
        ):
            return MemoryCategory.TECHNICAL
        elif any(
            word in content_lower for word in ["revenue", "customer", "sales", "market"]
        ):
            return MemoryCategory.BUSINESS
        elif any(
            word in content_lower
            for word in ["project", "task", "milestone", "deadline"]
        ):
            return MemoryCategory.PROJECT
        elif any(
            word in content_lower for word in ["learn", "study", "research", "article"]
        ):
            return MemoryCategory.LEARNING
        else:
            return MemoryCategory.GENERAL

    async def _check_duplicate(
        self, content: str, embedding: np.ndarray | None
    ) -> int | None:
        """Check for duplicate memories using content hash or embedding similarity."""
        # Simple content hash check
        hashlib.sha256(content.encode()).hexdigest()

        # Check in database (placeholder)
        # In real implementation, check both content hash and embedding similarity
        return None  # Placeholder

    def _generate_highlights(self, content: str, query: str) -> list[str]:
        """Generate highlighted snippets from content."""
        # Simple implementation - find sentences containing query terms
        query_terms = query.lower().split()
        sentences = content.split(". ")

        highlights = []
        for sentence in sentences:
            if any(term in sentence.lower() for term in query_terms):
                highlights.append(sentence.strip())
                if len(highlights) >= 3:  # Limit to 3 highlights
                    break

        return highlights

    # Database placeholder methods - implement with actual DB

    async def _store_in_db(self, memory: MemoryEntry) -> int:
        """Store memory in database and return ID."""
        # Placeholder - implement actual database storage
        return 1

    async def _get_memory_by_id(self, memory_id: int) -> MemoryEntry | None:
        """Get memory by ID from database."""
        # Placeholder
        return None

    async def _search_in_db(self, **kwargs) -> list[tuple[MemoryEntry, float]]:
        """Search memories in database."""
        # Placeholder
        return []

    async def _get_stats_from_db(self) -> dict[str, Any]:
        """Get statistics from database."""
        # Placeholder
        return {"total": 0, "by_category": {}, "top_tags": [], "storage_mb": 0.0}

    async def _update_in_db(self, memory: MemoryEntry) -> None:
        """Update memory in database."""
        # Placeholder
        pass

    async def _delete_from_db(self, memory_id: int) -> bool:
        """Delete memory from database."""
        # Placeholder
        return True
