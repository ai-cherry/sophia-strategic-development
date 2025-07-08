"""Embedding generation utilities for AI Memory V2.

Supports multiple embedding providers with fallback options.
"""
import logging
from abc import ABC, abstractmethod
from enum import Enum

import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingProvider(Enum):
    """Available embedding providers."""

    OPENAI = "openai"
    SENTENCE_TRANSFORMER = "sentence_transformer"
    SNOWFLAKE_CORTEX = "snowflake_cortex"
    COHERE = "cohere"


class BaseEmbeddingProvider(ABC):
    """Base class for embedding providers."""

    @abstractmethod
    async def generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for text."""
        pass

    @abstractmethod
    async def generate_batch_embeddings(self, texts: list[str]) -> list[np.ndarray]:
        """Generate embeddings for multiple texts."""
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return embedding dimension."""
        pass


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    """OpenAI embedding provider."""

    def __init__(self, api_key: str, model: str = "text-embedding-ada-002"):
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.model = model
        self._dimension = 1536

    async def generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding using OpenAI."""
        try:
            response = await self.client.embeddings.create(model=self.model, input=text)
            return np.array(response.data[0].embedding)
        except Exception as e:
            logger.exception(f"OpenAI embedding error: {e}")
            raise

    async def generate_batch_embeddings(self, texts: list[str]) -> list[np.ndarray]:
        """Generate embeddings for multiple texts."""
        try:
            response = await self.client.embeddings.create(
                model=self.model, input=texts
            )
            return [np.array(data.embedding) for data in response.data]
        except Exception as e:
            logger.exception(f"OpenAI batch embedding error: {e}")
            raise

    @property
    def dimension(self) -> int:
        return self._dimension


class SentenceTransformerProvider(BaseEmbeddingProvider):
    """Sentence Transformer embedding provider (self-hosted)."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(model_name)
        self._dimension = self.model.get_sentence_embedding_dimension()

    async def generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding using Sentence Transformers."""
        try:
            import asyncio

            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(None, self.model.encode, text)
            return np.array(embedding)
        except Exception as e:
            logger.exception(f"Sentence Transformer embedding error: {e}")
            raise

    async def generate_batch_embeddings(self, texts: list[str]) -> list[np.ndarray]:
        """Generate embeddings for multiple texts."""
        try:
            import asyncio

            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(None, self.model.encode, texts)
            return [np.array(emb) for emb in embeddings]
        except Exception as e:
            logger.exception(f"Sentence Transformer batch embedding error: {e}")
            raise

    @property
    def dimension(self) -> int:
        return self._dimension


class SnowflakeCortexProvider(BaseEmbeddingProvider):
    """Snowflake Cortex embedding provider."""

    def __init__(self, connection_params: dict):
        self.connection_params = connection_params
        self._dimension = 768

    async def generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding using Snowflake Cortex."""
        raise NotImplementedError("Snowflake Cortex provider not implemented")

    async def generate_batch_embeddings(self, texts: list[str]) -> list[np.ndarray]:
        """Generate embeddings for multiple texts."""
        raise NotImplementedError("Snowflake Cortex provider not implemented")

    @property
    def dimension(self) -> int:
        return self._dimension


class HybridEmbeddingService:
    """Hybrid embedding service with fallback support."""

    def __init__(
        self,
        primary_provider: BaseEmbeddingProvider,
        fallback_providers: list[BaseEmbeddingProvider] | None = None,
        cache_embeddings: bool = True,
    ):
        self.primary_provider = primary_provider
        self.fallback_providers = fallback_providers or []
        self.cache_embeddings = cache_embeddings
        if cache_embeddings:
            self._cache = {}

    async def generate_embedding(self, text: str, use_cache: bool = True) -> np.ndarray:
        """Generate embedding with fallback support."""
        if self.cache_embeddings and use_cache:
            cache_key = hash(text)
            if cache_key in self._cache:
                logger.debug("Returning cached embedding")
                return self._cache[cache_key]
        try:
            embedding = await self.primary_provider.generate_embedding(text)
            if self.cache_embeddings:
                self._cache[cache_key] = embedding
            return embedding
        except Exception as e:
            logger.warning(f"Primary provider failed: {e}")
            for provider in self.fallback_providers:
                try:
                    logger.info(
                        f"Trying fallback provider: {provider.__class__.__name__}"
                    )
                    embedding = await provider.generate_embedding(text)
                    if self.cache_embeddings:
                        self._cache[cache_key] = embedding
                    return embedding
                except Exception as fallback_error:
                    logger.warning(f"Fallback provider failed: {fallback_error}")
                    continue
            raise RuntimeError("All embedding providers failed")

    async def generate_batch_embeddings(
        self, texts: list[str], batch_size: int = 100
    ) -> list[np.ndarray]:
        """Generate embeddings for multiple texts with batching."""
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            try:
                embeddings = await self.primary_provider.generate_batch_embeddings(
                    batch
                )
                all_embeddings.extend(embeddings)
            except Exception as e:
                logger.warning(
                    f"Batch embedding failed, falling back to individual: {e}"
                )
                for text in batch:
                    embedding = await self.generate_embedding(text)
                    all_embeddings.append(embedding)
        return all_embeddings

    @property
    def dimension(self) -> int:
        """Get embedding dimension from primary provider."""
        return self.primary_provider.dimension


def create_embedding_service(
    primary: str = "openai", enable_fallback: bool = True, **kwargs
) -> HybridEmbeddingService:
    """Create embedding service with specified configuration."""
    if primary == "openai":
        primary_provider = OpenAIEmbeddingProvider(
            api_key=kwargs.get("openai_api_key"),
            model=kwargs.get("openai_model", "text-embedding-ada-002"),
        )
    elif primary == "sentence_transformer":
        primary_provider = SentenceTransformerProvider(
            model_name=kwargs.get("st_model", "all-MiniLM-L6-v2")
        )
    else:
        raise ValueError(f"Unknown primary provider: {primary}")
    fallback_providers = []
    if enable_fallback:
        if primary != "sentence_transformer":
            fallback_providers.append(
                SentenceTransformerProvider(model_name="all-MiniLM-L6-v2")
            )
    return HybridEmbeddingService(
        primary_provider=primary_provider,
        fallback_providers=fallback_providers,
        cache_embeddings=kwargs.get("cache_embeddings", True),
    )
