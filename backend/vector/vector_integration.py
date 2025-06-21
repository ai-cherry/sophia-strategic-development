"""Unified vector database integration used across the Sophia project.

The original project supports multiple vector database backends.  For the
purposes of unit testing and static analysis the implementation here keeps only a
simple in-memory backend while preserving the public API of the original
module.  This allows other modules to import and interact with the integration
layer without requiring any external services.
"""

from __future__ import annotations

import asyncio
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

try:  # pragma: no cover - optional dependency
    import numpy as np
except Exception:  # pragma: no cover - fallback if numpy is missing
    np = None

try:  # pragma: no cover - optional dependency
    from sentence_transformers import SentenceTransformer

    SENTENCE_TRANSFORMERS_AVAILABLE = True
except Exception:  # pragma: no cover - optional dependency
    SentenceTransformer = None
    SENTENCE_TRANSFORMERS_AVAILABLE = False

logger = logging.getLogger(__name__)


class VectorDBType(Enum):
    """Supported vector database types."""

    MEMORY = "memory"


@dataclass
class VectorConfig:
    """Configuration for the vector database."""

    db_type: VectorDBType
    index_name: str
    dimension: int = 384
    metric: str = "cosine"
    namespace: Optional[str] = None


@dataclass
class VectorSearchResult:
    """Result from a vector search."""

    id: str
    score: float
    metadata: Dict[str, Any]
    text: Optional[str] = None


class VectorDBInterface(ABC):
    """Abstract interface for vector databases."""

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the vector database connection."""

    @abstractmethod
    async def index_content(
        self,
        content_id: str,
        embedding: List[float],
        metadata: Dict[str, Any],
        namespace: Optional[str] = None,
    ) -> bool:
        """Index content with embedding and metadata."""

    @abstractmethod
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None,
        namespace: Optional[str] = None,
    ) -> List[VectorSearchResult]:
        """Search for similar vectors."""

    @abstractmethod
    async def delete_content(
        self, content_id: str, namespace: Optional[str] = None
    ) -> bool:
        """Delete content by ID."""

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Return basic health information."""


class MemoryVectorDB(VectorDBInterface):
    """In-memory vector database used for tests."""

    def __init__(self, config: VectorConfig) -> None:
        self.config = config
        self.vectors: Dict[str, np.ndarray] = {}
        self.metadata: Dict[str, Dict[str, Any]] = {}

    async def initialize(self) -> None:  # pragma: no cover - trivial
        logger.info("Initialized in-memory vector database")

    async def index_content(
        self,
        content_id: str,
        embedding: List[float],
        metadata: Dict[str, Any],
        namespace: Optional[str] = None,
    ) -> bool:
        key = f"{namespace or 'default'}:{content_id}"
        self.vectors[key] = np.array(embedding) if np is not None else list(embedding)
        self.metadata[key] = metadata
        return True

    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None,
        namespace: Optional[str] = None,
    ) -> List[VectorSearchResult]:
        query_vec = (
            np.array(query_embedding) if np is not None else list(query_embedding)
        )
        results: List[Tuple[str, float, Dict[str, Any]]] = []
        for key, vec in self.vectors.items():
            if namespace and not key.startswith(f"{namespace}:"):
                continue
            meta = self.metadata.get(key, {})
            if filter_metadata and not all(
                meta.get(k) == v for k, v in filter_metadata.items()
            ):
                continue
            if np is not None:
                sim = float(
                    np.dot(query_vec, vec)
                    / (np.linalg.norm(query_vec) * np.linalg.norm(vec))
                )
            else:
                dot = sum(a * b for a, b in zip(query_vec, vec))
                norm_q = sum(a * a for a in query_vec) ** 0.5
                norm_v = sum(a * a for a in vec) ** 0.5
                sim = float(dot / (norm_q * norm_v)) if norm_q and norm_v else 0.0
            results.append((key.split(":", 1)[1], sim, meta))
        results.sort(key=lambda x: x[1], reverse=True)
        return [
            VectorSearchResult(
                id=r[0], score=r[1], metadata=r[2], text=r[2].get("text")
            )
            for r in results[:top_k]
        ]

    async def delete_content(
        self, content_id: str, namespace: Optional[str] = None
    ) -> bool:
        key = f"{namespace or 'default'}:{content_id}"
        if key in self.vectors:
            del self.vectors[key]
            del self.metadata[key]
            return True
        return False

    async def health_check(self) -> Dict[str, Any]:
        return {
            "status": "healthy",
            "total_vectors": len(self.vectors),
            "db_type": self.config.db_type.value,
        }


class VectorIntegration:
    """Facade that manages vector database operations."""

    def __init__(self, config: Optional[VectorConfig] = None) -> None:
        self.config = config or self._get_default_config()
        self.db: Optional[VectorDBInterface] = None
        self.encoder: Optional[Any] = None
        self.initialized = False

    def _get_default_config(self) -> VectorConfig:
        return VectorConfig(db_type=VectorDBType.MEMORY, index_name="default")

    async def initialize(self) -> None:
        if self.initialized:
            return
        self.db = MemoryVectorDB(self.config)
        await self.db.initialize()
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
        self.initialized = True
        logger.info("Vector integration initialized")

    async def generate_embedding(self, text: str) -> List[float]:
        if self.encoder is None:
            # Simple deterministic fallback embedding
            return [float(ord(c)) for c in text][: self.config.dimension]
        embedding = self.encoder.encode(text)
        return embedding.tolist()

    async def index_content(
        self,
        content_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        namespace: Optional[str] = None,
    ) -> bool:
        if not self.initialized:
            await self.initialize()
        embedding = await self.generate_embedding(text)
        meta = dict(metadata or {}, text=text)
        assert self.db is not None
        return await self.db.index_content(content_id, embedding, meta, namespace)

    async def search(
        self,
        query: str,
        top_k: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None,
        namespace: Optional[str] = None,
    ) -> List[VectorSearchResult]:
        if not self.initialized:
            await self.initialize()
        query_embedding = await self.generate_embedding(query)
        assert self.db is not None
        return await self.db.search(query_embedding, top_k, filter_metadata, namespace)

    async def delete_content(
        self, content_id: str, namespace: Optional[str] = None
    ) -> bool:
        if not self.initialized:
            await self.initialize()
        assert self.db is not None
        return await self.db.delete_content(content_id, namespace)

    async def health_check(self) -> Dict[str, Any]:
        if not self.initialized:
            return {"status": "uninitialized", "db_type": self.config.db_type.value}
        assert self.db is not None
        health = await self.db.health_check()
        health["encoder_available"] = self.encoder is not None
        return health

    # Compatibility helpers
    async def index_content_pinecone(
        self, content_id: str, text: str, metadata: Dict[str, Any]
    ) -> bool:
        return await self.index_content(content_id, text, metadata)

    async def search_pinecone(
        self,
        query: str,
        top_k: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None,
        namespace: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        results = await self.search(query, top_k, filter_metadata, namespace)
        return [
            {"id": r.id, "score": r.score, "metadata": r.metadata, "text": r.text}
            for r in results
        ]

    async def index_content_weaviate(
        self, content_id: str, text: str, metadata: Dict[str, Any]
    ) -> bool:
        return await self.index_content(content_id, text, metadata)

    async def search_weaviate(
        self, query: str, top_k: int = 10, category_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        filter_metadata = {"category": category_filter} if category_filter else None
        results = await self.search(query, top_k, filter_metadata)
        return [
            {"id": r.id, "score": r.score, "metadata": r.metadata, "text": r.text}
            for r in results
        ]

    def batch_index_content(
        self, vector_data_items: List[Tuple[str, List[float], Dict[str, Any]]]
    ) -> Dict[str, Any]:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success = 0
        for content_id, embedding, metadata in vector_data_items:
            try:
                result = loop.run_until_complete(
                    self.db.index_content(content_id, embedding, metadata)
                )
                if result:
                    success += 1
            except Exception as exc:  # pragma: no cover - diagnostic
                logger.error("Failed to index %s: %s", content_id, exc)
        loop.close()
        return {
            "total": len(vector_data_items),
            "success": success,
            "failed": len(vector_data_items) - success,
        }


# Global singleton instance
vector_integration = VectorIntegration()

# Backwards compatibility aliases
VectorConfig = VectorConfig
VectorIntegration = VectorIntegration
