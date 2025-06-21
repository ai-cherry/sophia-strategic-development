"""Unified Vector Integration for Sophia AI.

Provides a consistent interface for vector database operations across Pinecone and Weaviate.
This module consolidates all vector database interactions to avoid duplication
"""

import asyncio
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# Import with fallback for optional dependencies
try:
except Exception:
    pass
    import pinecone
    from pinecone import Pinecone, ServerlessSpec

    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    pinecone = None
    Pinecone = None
    ServerlessSpec = None

try:
except Exception:
    pass
    import weaviate
    from weaviate import Client as WeaviateClient

    WEAVIATE_AVAILABLE = True
except ImportError:
    WEAVIATE_AVAILABLE = False
    weaviate = None
    WeaviateClient = None

try:
except Exception:
    pass
    from sentence_transformers import SentenceTransformer

    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None

from backend.core.auto_esc_config import config

logger = logging.getLogger(__name__)


class VectorDBType(Enum):
    """Supported vector database types"""

    PINECONE = "pinecone"
    WEAVIATE = "weaviate"
    MEMORY = "memory"  # In-memory for testing


@dataclass
class VectorConfig:
    """Configuration for vector database"""

    db_type: VectorDBType

    index_name: str
    dimension: int = 384  # Default for all-MiniLM-L6-v2
    metric: str = "cosine"
    namespace: Optional[str] = None
    api_key: Optional[str] = None
    url: Optional[str] = None
    region: Optional[str] = "us-east-1"
    cloud: Optional[str] = "aws"


@dataclass
class VectorSearchResult:
    """Result from vector search"""
id: str

    score: float
    metadata: Dict[str, Any]
    text: Optional[str] = None


class VectorDBInterface(ABC):
    """Abstract interface for vector databases"""
@abstractmethod
    async def initialize(self) -> None:
        """Initialize the vector database connection"""
pass.

    @abstractmethod
    async def index_content(
        self,
        content_id: str,
        embedding: List[float],
        metadata: Dict[str, Any],
        namespace: Optional[str] = None,
    ) -> bool:
        """Index content with embedding and metadata"""
pass.

    @abstractmethod
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None,
        namespace: Optional[str] = None,
    ) -> List[VectorSearchResult]:
        """Search for similar vectors"""
pass

    @abstractmethod
    async def delete_content(
        self, content_id: str, namespace: Optional[str] = None
    ) -> bool:
        """Delete content by ID"""
pass
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check health of the vector database"""
pass.


class PineconeVectorDB(VectorDBInterface):
    """Pinecone vector database implementation"""
def __init__(self, config: VectorConfig):

        self.config = config
        self.client = None
        self.index = None

    async def initialize(self) -> None:
        """Initialize Pinecone connection"""
        if not PINECONE_AVAILABLE:

            raise ImportError(
                "Pinecone is not available. Please install pinecone-client."
            )

        try:
        except Exception:
            pass
            # Get API key from config or environment
            api_key = self.config.api_key or await config.get_secret("PINECONE_API_KEY")
            if not api_key:
                raise ValueError("PINECONE_API_KEY not found")

            self.client = Pinecone(api_key=api_key)

            # Create index if it doesn't exist
            if self.config.index_name not in self.client.list_indexes().names():
                self.client.create_index(
                    name=self.config.index_name,
                    dimension=self.config.dimension,
                    metric=self.config.metric,
                    spec=ServerlessSpec(
                        cloud=self.config.cloud, region=self.config.region
                    ),
                )
                logger.info(f"Created Pinecone index: {self.config.index_name}")

            self.index = self.client.Index(self.config.index_name)
            logger.info(f"Connected to Pinecone index: {self.config.index_name}")

        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}")
            raise

    async def index_content(
        self,
        content_id: str,
        embedding: List[float],
        metadata: Dict[str, Any],
        namespace: Optional[str] = None,
    ) -> bool:
        """Index content in Pinecone"""

    try:
    except Exception:
        pass
            namespace = namespace or self.config.namespace
            self.index.upsert(
                vectors=[(content_id, embedding, metadata)], namespace=namespace
            )
            return True
        except Exception as e:
            logger.error(f"Failed to index content in Pinecone: {e}")
            return False

    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None,
        namespace: Optional[str] = None,
    ) -> List[VectorSearchResult]:
        """Search in Pinecone"""

    try:
    except Exception:
        pass
            namespace = namespace or self.config.namespace
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter_metadata,
                namespace=namespace,
            )

            return [
                VectorSearchResult(
                    id=match.id,
                    score=match.score,
                    metadata=match.metadata,
                    text=match.metadata.get("text", ""),
                )
                for match in results.matches
            ]
        except Exception as e:
            logger.error(f"Failed to search in Pinecone: {e}")
            return []

    async def delete_content(
        self, content_id: str, namespace: Optional[str] = None
    ) -> bool:
        """Delete content from Pinecone"""

    try:
    except Exception:
        pass
            namespace = namespace or self.config.namespace
            self.index.delete(ids=[content_id], namespace=namespace)
            return True
        except Exception as e:
            logger.error(f"Failed to delete content from Pinecone: {e}")
            return False

    async def health_check(self) -> Dict[str, Any]:
        """Check Pinecone health"""

    try:
    except Exception:
        pass
            stats = self.index.describe_index_stats()
            return {
                "status": "healthy",
                "total_vectors": stats.total_vector_count,
                "index_fullness": stats.index_fullness,
                "dimension": self.config.dimension,
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


class WeaviateVectorDB(VectorDBInterface):
    """Weaviate vector database implementation"""

    def __init__(self, config: VectorConfig):

        self.config = config
        self.client = None
        self.class_name = "SophiaContent"

    async def initialize(self) -> None:
        """Initialize Weaviate connection"""

    if not WEAVIATE_AVAILABLE:

            raise ImportError(
                "Weaviate is not available. Please install weaviate-client."
            )

        try:
        except Exception:
            pass
            # Get URL from config or use default
            url = self.config.url or "http://localhost:8080"

            # Get API key if provided
            api_key = self.config.api_key or await config.get_secret("WEAVIATE_API_KEY")

            if api_key:
                self.client = WeaviateClient(
                    url=url, auth_client_secret=weaviate.AuthApiKey(api_key=api_key)
                )
            else:
                self.client = WeaviateClient(url=url)

            # Create schema if it doesn't exist
            if not self.client.schema.exists(self.class_name):
                class_obj = {
                    "class": self.class_name,
                    "vectorizer": "none",  # We provide our own embeddings
                    "properties": [
                        {"name": "content_id", "dataType": ["string"]},
                        {"name": "text", "dataType": ["text"]},
                        {"name": "metadata", "dataType": ["string"]},  # JSON string
                    ],
                }
                self.client.schema.create_class(class_obj)
                logger.info(f"Created Weaviate class: {self.class_name}")

            logger.info("Connected to Weaviate")

        except Exception as e:
            logger.error(f"Failed to initialize Weaviate: {e}")
            raise

    async def index_content(
        self,
        content_id: str,
        embedding: List[float],
        metadata: Dict[str, Any],
        namespace: Optional[str] = None,
    ) -> bool:
        """Index content in Weaviate"""

    try:
    except Exception:
        pass
            import json

            data_object = {
                "content_id": content_id,
                "text": metadata.get("text", ""),
                "metadata": json.dumps(metadata),
            }

            self.client.data_object.create(
                data_object=data_object, class_name=self.class_name, vector=embedding
            )
            return True
        except Exception as e:
            logger.error(f"Failed to index content in Weaviate: {e}")
            return False

    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None,
        namespace: Optional[str] = None,
    ) -> List[VectorSearchResult]:
        """Search in Weaviate"""

    try:
    except Exception:
        pass
            import json

            near_vector = {"vector": query_embedding}

            query = (
                self.client.query.get(
                    self.class_name, ["content_id", "text", "metadata"]
                )
                .with_near_vector(near_vector)
                .with_limit(top_k)
                .with_additional(["distance"])
            )

            # Add filters if provided
            if filter_metadata:
                # This is a simplified filter - Weaviate has more complex filtering
                where_filter = {
                    "path": ["metadata"],
                    "operator": "Like",
                    "valueString": f"*{list(filter_metadata.values())[0]}*",
                }
                query = query.with_where(where_filter)

            result = query.do()

            results = []
            if self.class_name in result.get("data", {}).get("Get", {}):
                for item in result["data"]["Get"][self.class_name]:
                    metadata = json.loads(item.get("metadata", "{}"))
                    results.append(
                        VectorSearchResult(
                            id=item.get("content_id", ""),
                            score=1.0
                            - item["_additional"][
                                "distance"
                            ],  # Convert distance to similarity
                            metadata=metadata,
                            text=item.get("text", ""),
                        )
                    )

            return results
        except Exception as e:
            logger.error(f"Failed to search in Weaviate: {e}")
            return []

    async def delete_content(
        self, content_id: str, namespace: Optional[str] = None
    ) -> bool:
        """Delete content from Weaviate"""

    try:
    except Exception:
        pass
            where_filter = {
                "path": ["content_id"],
                "operator": "Equal",
                "valueString": content_id,
            }

            self.client.data_object.delete(
                class_name=self.class_name, where=where_filter
            )
            return True
        except Exception as e:
            logger.error(f"Failed to delete content from Weaviate: {e}")
            return False

    async def health_check(self) -> Dict[str, Any]:
        """Check Weaviate health"""

    try:
    except Exception:
        pass
            if self.client.is_ready():
                # Get object count
                result = (
                    self.client.query.aggregate(self.class_name).with_meta_count().do()
                )
                count = result["data"]["Aggregate"][self.class_name][0]["meta"]["count"]

                return {
                    "status": "healthy",
                    "total_vectors": count,
                    "class_name": self.class_name,
                }
            else:
                return {"status": "unhealthy", "error": "Weaviate is not ready"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


class MemoryVectorDB(VectorDBInterface):
    """In-memory vector database for testing"""
def __init__(self, config: VectorConfig):

        self.config = config
        self.vectors = {}
        self.metadata = {}

    async def initialize(self) -> None:
        """Initialize in-memory storage"""

    logger.info("Initialized in-memory vector database")

    async def index_content(
        self,
        content_id: str,
        embedding: List[float],
        metadata: Dict[str, Any],
        namespace: Optional[str] = None,
    ) -> bool:
        """Store content in memory"""

    key = f"{namespace or 'default'}:{content_id}"

        self.vectors[key] = np.array(embedding)
        self.metadata[key] = metadata
        return True

    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None,
        namespace: Optional[str] = None,
    ) -> List[VectorSearchResult]:
        """Search in memory using cosine similarity"""

    query_vec = np.array(query_embedding)

        results = []

        for key, vec in self.vectors.items():
            # Check namespace
            if namespace and not key.startswith(f"{namespace}:"):
                continue

            # Check metadata filters
            if filter_metadata:
                meta = self.metadata.get(key, {})
                if not all(meta.get(k) == v for k, v in filter_metadata.items()):
                    continue

            # Calculate cosine similarity
            similarity = np.dot(query_vec, vec) / (
                np.linalg.norm(query_vec) * np.linalg.norm(vec)
            )

            results.append(
                (
                    key.split(":", 1)[1],  # Extract content_id
                    float(similarity),
                    self.metadata.get(key, {}),
                )
            )

        # Sort by similarity and return top_k
        results.sort(key=lambda x: x[1], reverse=True)

        return [
            VectorSearchResult(
                id=r[0], score=r[1], metadata=r[2], text=r[2].get("text", "")
            )
            for r in results[:top_k]
        ]

    async def delete_content(
        self, content_id: str, namespace: Optional[str] = None
    ) -> bool:
        """Delete content from memory"""

    key = f"{namespace or 'default'}:{content_id}"

        if key in self.vectors:
            del self.vectors[key]
            del self.metadata[key]
            return True
        return False

    async def health_check(self) -> Dict[str, Any]:
        """Check memory database health"""

    return {

            "status": "healthy",
            "total_vectors": len(self.vectors),
            "type": "memory",
        }


class VectorIntegration:
    """Main vector integration class that manages different vector databases"""
def __init__(self, config: Optional[VectorConfig] = None):

        self.config = config or self._get_default_config()
        self.db: Optional[VectorDBInterface] = None
        self.encoder = None
        self.initialized = False

    def _get_default_config(self) -> VectorConfig:
        """Get default configuration based on environment"""# Check which vector DB is configured

        if os.getenv("PINECONE_API_KEY"):
            return VectorConfig(
                db_type=VectorDBType.PINECONE,
                index_name="sophia-knowledge-base",
                dimension=384,
            )
        elif os.getenv("WEAVIATE_URL"):
            return VectorConfig(
                db_type=VectorDBType.WEAVIATE,
                index_name="SophiaContent",
                dimension=384,
                url=os.getenv("WEAVIATE_URL"),
            )
        else:
            # Default to in-memory for testing
            return VectorConfig(
                db_type=VectorDBType.MEMORY, index_name="test", dimension=384
            )

    async def initialize(self) -> None:
        """Initialize the vector database and encoder"""

    if self.initialized:

            return

        try:
        except Exception:
            pass
            # Initialize the appropriate vector database
            if self.config.db_type == VectorDBType.PINECONE:
                self.db = PineconeVectorDB(self.config)
            elif self.config.db_type == VectorDBType.WEAVIATE:
                self.db = WeaviateVectorDB(self.config)
            else:
                self.db = MemoryVectorDB(self.config)

            await self.db.initialize()

            # Initialize encoder if available
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
                logger.info("Initialized sentence transformer encoder")
            else:
                logger.warning(
                    "Sentence transformers not available - embeddings must be provided"
                )

            self.initialized = True
            logger.info(
                f"Vector integration initialized with {self.config.db_type.value}"
            )

        except Exception as e:
            logger.error(f"Failed to initialize vector integration: {e}")
            raise

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""

    if not self.encoder:

            raise RuntimeError("Encoder not available - install sentence-transformers")

        embedding = self.encoder.encode(text)
        return embedding.tolist()

    async def index_content(
        self,
        content_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        namespace: Optional[str] = None,
    ) -> bool:
        """Index content with automatic embedding generation"""

    if not self.initialized:

            await self.initialize()

        try:
        except Exception:
            pass
            # Generate embedding
            embedding = await self.generate_embedding(text)

            # Add text to metadata
            if metadata is None:
                metadata = {}
            metadata["text"] = text

            # Index in vector database
            return await self.db.index_content(
                content_id=content_id,
                embedding=embedding,
                metadata=metadata,
                namespace=namespace,
            )
        except Exception as e:
            logger.error(f"Failed to index content: {e}")
            return False

    async def search(
        self,
        query: str,
        top_k: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None,
        namespace: Optional[str] = None,
    ) -> List[VectorSearchResult]:
        """Search for similar content"""

    if not self.initialized:

            await self.initialize()

        try:
        except Exception:
            pass
            # Generate query embedding
            query_embedding = await self.generate_embedding(query)

            # Search in vector database
            return await self.db.search(
                query_embedding=query_embedding,
                top_k=top_k,
                filter_metadata=filter_metadata,
                namespace=namespace,
            )
        except Exception as e:
            logger.error(f"Failed to search: {e}")
            return []

    async def delete_content(
        self, content_id: str, namespace: Optional[str] = None
    ) -> bool:
        """Delete content by ID"""
if not self.initialized:

            await self.initialize()

        return await self.db.delete_content(content_id=content_id, namespace=namespace)

    async def health_check(self) -> Dict[str, Any]:
        """Check health of the vector integration"""

    if not self.initialized:

            return {"status": "uninitialized", "db_type": self.config.db_type.value}

        health = await self.db.health_check()
        health["db_type"] = self.config.db_type.value
        health["encoder_available"] = self.encoder is not None
        return health

    # Compatibility methods for existing code
    async def index_content_pinecone(
        self, content_id: str, text: str, metadata: Dict[str, Any]
    ) -> bool:
        """Compatibility method for Pinecone indexing"""
return await self.index_content(content_id, text, metadata)

    async def search_pinecone(
        self,
        query: str,
        top_k: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None,
        namespace: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Compatibility method for Pinecone search"""

    results = await self.search(query, top_k, filter_metadata, namespace)

        return [
            {"id": r.id, "score": r.score, "metadata": r.metadata, "text": r.text}
            for r in results
        ]

    async def index_content_weaviate(
        self, content_id: str, text: str, metadata: Dict[str, Any]
    ) -> bool:
        """Compatibility method for Weaviate indexing"""
return await self.index_content(content_id, text, metadata)

    async def search_weaviate(
        self, query: str, top_k: int = 10, category_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Compatibility method for Weaviate search"""

    filter_metadata = {"category": category_filter} if category_filter else None

        results = await self.search(query, top_k, filter_metadata)
        return [
            {"id": r.id, "score": r.score, "metadata": r.metadata, "text": r.text}
            for r in results
        ]

    def batch_index_content(
        self, vector_data_items: List[Tuple[str, List[float], Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Synchronous batch indexing for compatibility"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        success_count = 0
        for content_id, embedding, metadata in vector_data_items:
            try:
            except Exception:
                pass
                result = loop.run_until_complete(
                    self.db.index_content(content_id, embedding, metadata)
                )
                if result:
                    success_count += 1
            except Exception as e:
                logger.error(f"Failed to index {content_id}: {e}")

        loop.close()

        return {
            "total": len(vector_data_items),
            "success": success_count,
            "failed": len(vector_data_items) - success_count,
        }


# Global singleton instance
vector_integration = VectorIntegration()


# For backward compatibility with imports
VectorConfig = VectorConfig
VectorIntegration = VectorIntegration
