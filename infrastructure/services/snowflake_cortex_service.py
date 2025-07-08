"""Snowflake Cortex service with async context management."""

import logging
from collections.abc import Sequence
from typing import Any, Optional

from infrastructure.adapters.snowflake_adapter import SnowflakeConfigManager

logger = logging.getLogger(__name__)


class SnowflakeCortexService:
    """Service for Snowflake Cortex AI operations.

    This service provides:
    - Text completion with Cortex LLMs
    - Embedding generation
    - Sentiment analysis
    - Semantic search

    All operations use proper async context management
    and error handling.

    Attributes:
        config_manager: Snowflake configuration manager
        default_model: Default Cortex model
    """

    def __init__(
        self,
        default_model: str = "llama3.1-70b",
        warehouse: str = "SOPHIA_AI_COMPUTE_WH",
    ):
        """Initialize Cortex service.

        Args:
            default_model: Default model for completions
            warehouse: Snowflake warehouse to use
        """
        self.config_manager = SnowflakeConfigManager(warehouse=warehouse)
        self.default_model = default_model

    async def __aenter__(self) -> "SnowflakeCortexService":
        """Async context manager entry.

        Returns:
            Self with active connection
        """
        await self.config_manager.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit.

        Args:
            exc_type: Exception type if any
            exc_val: Exception value if any
            exc_tb: Exception traceback if any
        """
        await self.config_manager.__aexit__(exc_type, exc_val, exc_tb)

    async def complete(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> dict[str, Any]:
        """Generate text completion using Cortex.

        Args:
            prompt: Input prompt
            model: Optional model override
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Completion result with text and metadata

        Raises:
            ValueError: If prompt is invalid
            RuntimeError: If service not initialized
        """
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Prompt must be a non-empty string")

        model_name = model or self.default_model

        try:
            result = await self.config_manager.execute_query(
                f"""
                SELECT SNOWFLAKE.CORTEX.COMPLETE(
                    '{model_name}',
                    :prompt,
                    {{
                        'temperature': {temperature},
                        'max_tokens': {max_tokens}
                    }}
                ) as completion
                """,
                {"prompt": prompt},
            )

            if result and len(result) > 0:
                return {
                    "text": result[0]["COMPLETION"],
                    "model": model_name,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                }
            else:
                return {"text": "", "error": "No completion generated"}

        except Exception as e:
            logger.error(f"Cortex completion failed: {e}")
            raise

    async def embed(
        self,
        texts: Sequence[str],
        model: str = "e5-base-v2",
    ) -> list[list[float]]:
        """Generate embeddings for texts.

        Args:
            texts: List of texts to embed
            model: Embedding model to use

        Returns:
            List of embedding vectors

        Raises:
            ValueError: If texts is invalid
            RuntimeError: If service not initialized
        """
        if not isinstance(texts, (list, tuple)) or not texts:
            raise ValueError("Texts must be a non-empty sequence")

        embeddings = []

        for text in texts:
            if not isinstance(text, str):
                raise ValueError("Each text must be a string")

            result = await self.config_manager.execute_query(
                f"""
                SELECT SNOWFLAKE.CORTEX.EMBED_TEXT(
                    '{model}',
                    :text
                ) as embedding
                """,
                {"text": text},
            )

            if result and len(result) > 0:
                embeddings.append(result[0]["EMBEDDING"])
            else:
                embeddings.append([])

        return embeddings

    async def analyze_sentiment(
        self,
        text: str,
    ) -> dict[str, Any]:
        """Analyze sentiment of text.

        Args:
            text: Text to analyze

        Returns:
            Sentiment analysis results

        Raises:
            ValueError: If text is invalid
            RuntimeError: If service not initialized
        """
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Text must be a non-empty string")

        result = await self.config_manager.execute_query(
            """
            SELECT SNOWFLAKE.CORTEX.SENTIMENT(:text) as sentiment
            """,
            {"text": text},
        )

        if result and len(result) > 0:
            return {
                "sentiment": result[0]["SENTIMENT"],
                "text_length": len(text),
            }
        else:
            return {"sentiment": "neutral", "error": "Analysis failed"}

    async def semantic_search(
        self,
        query: str,
        table: str,
        text_column: str,
        embedding_column: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Perform semantic search using embeddings.

        Args:
            query: Search query
            table: Table to search
            text_column: Column containing text
            embedding_column: Column containing embeddings
            limit: Maximum results to return

        Returns:
            List of search results with scores

        Raises:
            ValueError: If parameters are invalid
            RuntimeError: If service not initialized
        """
        if not isinstance(query, str) or not query.strip():
            raise ValueError("Query must be a non-empty string")

        if not isinstance(limit, int) or limit < 1:
            raise ValueError("Limit must be a positive integer")

        # Generate query embedding
        query_embedding = await self.embed([query], model="e5-base-v2")

        if not query_embedding or not query_embedding[0]:
            raise RuntimeError("Failed to generate query embedding")

        # Search with cosine similarity
        results = await self.config_manager.execute_query(
            f"""
            SELECT
                {text_column} as text,
                VECTOR_COSINE_SIMILARITY(
                    {embedding_column},
                    :query_embedding::VECTOR(FLOAT, 768)
                ) as score
            FROM {table}
            WHERE {embedding_column} IS NOT NULL
            ORDER BY score DESC
            LIMIT {limit}
            """,
            {"query_embedding": query_embedding[0]},
        )

        return results
