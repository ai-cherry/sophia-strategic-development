"""Enhanced Embedding Manager for Sophia AI
Manages text embeddings with caching and multiple model support.
"""

import asyncio
import hashlib
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import numpy as np

# Import with fallback for optional dependencies
try:
    from sentence_transformers import SentenceTransformer

    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None

try:
    import openai

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None

from backend.core.auto_esc_config import config

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingMetadata:
    """Metadata for an embedding"""

    model: str
    dimension: int
    content_hash: str
    created_at: datetime
    token_count: Optional[int] = None


@dataclass
class EmbeddingResult:
    """Result of embedding generation"""

    embedding: List[float]
    metadata: EmbeddingMetadata


class EmbeddingCache:
    """Simple in-memory cache for embeddings"""

    def __init__(self, ttl_seconds: int = 3600):
        self.cache: Dict[str, Tuple[List[float], EmbeddingMetadata, datetime]] = {}
        self.ttl = timedelta(seconds=ttl_seconds)

    def get(self, key: str) -> Optional[EmbeddingResult]:
        """Get embedding from cache if not expired"""
        if key in self.cache:
            embedding, metadata, cached_at = self.cache[key]
            if datetime.now() - cached_at < self.ttl:
                return EmbeddingResult(embedding=embedding, metadata=metadata)
            else:
                # Remove expired entry
                del self.cache[key]
        return None

    def set(self, key: str, result: EmbeddingResult):
        """Store embedding in cache"""
        self.cache[key] = (result.embedding, result.metadata, datetime.now())

    def clear(self):
        """Clear all cached embeddings"""
        self.cache.clear()


class EnhancedEmbeddingManager:
    """Manages embeddings with multiple model support and caching"""

    def __init__(self):
        self.sentence_transformer = None
        self.openai_client = None
        self.cache = EmbeddingCache()
        self.default_model = "all-MiniLM-L6-v2"
        self.initialized = False

    async def initialize(self):
        """Initialize embedding models"""
        if self.initialized:
            return

        logger.info("Initializing enhanced embedding manager...")

        # Initialize sentence transformers if available
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.sentence_transformer = SentenceTransformer(self.default_model)
                logger.info(f"Initialized sentence transformer: {self.default_model}")
            except Exception as e:
                logger.error(f"Failed to initialize sentence transformer: {e}")

        # Initialize OpenAI if available
        if OPENAI_AVAILABLE:
            try:
                api_key = await config.get_secret("OPENAI_API_KEY")
                if api_key:
                    openai.api_key = api_key
                    self.openai_client = openai
                    logger.info("Initialized OpenAI client for embeddings")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI: {e}")

        self.initialized = True
        logger.info("Enhanced embedding manager initialized")

    def _compute_content_hash(self, text: str) -> str:
        """Compute hash of text content"""
        return hashlib.sha256(text.encode()).hexdigest()

    async def generate_text_embedding(
        self, text: str, model: Optional[str] = None, use_cache: bool = True
    ) -> Tuple[List[float], EmbeddingMetadata]:
        """Generate embedding for text with caching"""
        if not self.initialized:
            await self.initialize()

        # Use default model if not specified
        model = model or self.default_model

        # Compute content hash
        content_hash = self._compute_content_hash(text)
        cache_key = f"{model}:{content_hash}"

        # Check cache
        if use_cache:
            cached_result = self.cache.get(cache_key)
            if cached_result:
                logger.debug(f"Using cached embedding for hash {content_hash[:8]}")
                return cached_result.embedding, cached_result.metadata

        # Generate embedding based on model
        if model == "text-embedding-ada-002" and self.openai_client:
            embedding, metadata = await self._generate_openai_embedding(text, model)
        elif self.sentence_transformer:
            embedding, metadata = await self._generate_sentence_transformer_embedding(
                text, model
            )
        else:
            # Fallback to random embedding for testing
            embedding, metadata = await self._generate_random_embedding(text, model)

        # Cache the result
        if use_cache:
            result = EmbeddingResult(embedding=embedding, metadata=metadata)
            self.cache.set(cache_key, result)

        return embedding, metadata

    async def _generate_sentence_transformer_embedding(
        self, text: str, model: str
    ) -> Tuple[List[float], EmbeddingMetadata]:
        """Generate embedding using sentence transformers"""
        try:
            # Generate embedding
            embedding = self.sentence_transformer.encode(text)
            embedding_list = embedding.tolist()

            # Create metadata
            metadata = EmbeddingMetadata(
                model=model,
                dimension=len(embedding_list),
                content_hash=self._compute_content_hash(text),
                created_at=datetime.now(),
                token_count=len(text.split()),  # Approximate
            )

            return embedding_list, metadata

        except Exception as e:
            logger.error(f"Failed to generate sentence transformer embedding: {e}")
            raise

    async def _generate_openai_embedding(
        self, text: str, model: str
    ) -> Tuple[List[float], EmbeddingMetadata]:
        """Generate embedding using OpenAI"""
        try:
            # Create embedding
            response = await asyncio.to_thread(
                self.openai_client.Embedding.create, input=text, model=model
            )

            embedding = response["data"][0]["embedding"]

            # Create metadata
            metadata = EmbeddingMetadata(
                model=model,
                dimension=len(embedding),
                content_hash=self._compute_content_hash(text),
                created_at=datetime.now(),
                token_count=response.get("usage", {}).get("total_tokens"),
            )

            return embedding, metadata

        except Exception as e:
            logger.error(f"Failed to generate OpenAI embedding: {e}")
            raise

    async def _generate_random_embedding(
        self, text: str, model: str
    ) -> Tuple[List[float], EmbeddingMetadata]:
        """Generate random embedding for testing"""
        logger.warning(
            "Using random embeddings - install sentence-transformers for real embeddings"
        )

        # Use text hash as seed for consistent random embeddings
        seed = int(hashlib.md5(text.encode()).hexdigest()[:8], 16)
        np.random.seed(seed)

        # Generate random embedding
        dimension = 384  # Default dimension
        embedding = np.random.randn(dimension).tolist()

        # Create metadata
        metadata = EmbeddingMetadata(
            model=f"{model}-random",
            dimension=dimension,
            content_hash=self._compute_content_hash(text),
            created_at=datetime.now(),
            token_count=len(text.split()),
        )

        return embedding, metadata

    async def generate_batch_embeddings(
        self, texts: List[str], model: Optional[str] = None, use_cache: bool = True
    ) -> List[Tuple[List[float], EmbeddingMetadata]]:
        """Generate embeddings for multiple texts"""
        results = []

        for text in texts:
            embedding, metadata = await self.generate_text_embedding(
                text=text, model=model, use_cache=use_cache
            )
            results.append((embedding, metadata))

        return results

    def clear_cache(self):
        """Clear the embedding cache"""
        self.cache.clear()
        logger.info("Cleared embedding cache")

    async def get_available_models(self) -> List[str]:
        """Get list of available embedding models"""
        models = []

        if self.sentence_transformer:
            models.append(self.default_model)

        if self.openai_client:
            models.append("text-embedding-ada-002")

        if not models:
            models.append("random")

        return models

    async def get_model_info(self, model: str) -> Dict[str, any]:
        """Get information about a specific model"""
        info = {
            "model": model,
            "available": False,
            "dimension": None,
            "max_tokens": None,
        }

        if model == self.default_model and self.sentence_transformer:
            info["available"] = True
            info["dimension"] = 384
            info["max_tokens"] = 512
        elif model == "text-embedding-ada-002" and self.openai_client:
            info["available"] = True
            info["dimension"] = 1536
            info["max_tokens"] = 8191
        elif model == "random":
            info["available"] = True
            info["dimension"] = 384
            info["max_tokens"] = None

        return info


# Global instance
enhanced_embedding_manager = EnhancedEmbeddingManager()


# Example usage
async def main():
    """Example usage of enhanced embedding manager"""
    manager = enhanced_embedding_manager
    await manager.initialize()

    # Generate single embedding
    text = "This is a test sentence for embedding generation."
    embedding, metadata = await manager.generate_text_embedding(text)

    print(f"Generated embedding with dimension: {metadata.dimension}")
    print(f"Model used: {metadata.model}")
    print(f"Content hash: {metadata.content_hash[:8]}...")

    # Generate batch embeddings
    texts = ["First sentence", "Second sentence", "Third sentence"]

    results = await manager.generate_batch_embeddings(texts)
    print(f"\nGenerated {len(results)} embeddings")

    # Get available models
    models = await manager.get_available_models()
    print(f"\nAvailable models: {models}")


if __name__ == "__main__":
    asyncio.run(main())
