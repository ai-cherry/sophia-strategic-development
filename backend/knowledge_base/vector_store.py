"""Vector Store for the Knowledge Base
Handles the storage and retrieval of text embeddings (vectors) using Pinecone.
"""
import asyncio
import logging
from typing import Any, Dict, List

import numpy as np
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer

from backend.knowledge_base.chunking import Chunk
from infrastructure.esc.pinecone_secrets import pinecone_secret_manager

logger = logging.getLogger(__name__)


class VectorStore:
    """An abstraction for Pinecone's vector database."""

    INDEX_NAME = "sophia-knowledge-base"
    NAMESPACE = "default"  # Add a default namespace

    def __init__(self, embedding_model_name: str = "all-MiniLM-L6-v2"):
        logger.info(f"Initializing vector store with model: {embedding_model_name}")
        self.model = SentenceTransformer(embedding_model_name)
        self.pinecone_client = None
        self.index = None

    async def initialize(self):
        """Initializes the Pinecone client and ensures the index exists."""
        if self.index:
            return

        try:
            api_key = await pinecone_secret_manager.get_pinecone_api_key()
            if not api_key:
                raise ValueError("Pinecone API key not found.")

            self.pinecone_client = Pinecone(api_key=api_key)

            if self.INDEX_NAME not in self.pinecone_client.list_indexes().names():
                logger.info(
                    f"Pinecone index '{self.INDEX_NAME}' not found. Creating it now..."
                )
                self.pinecone_client.create_index(
                    name=self.INDEX_NAME,
                    dimension=self.model.get_sentence_embedding_dimension(),
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region="us-west-2"),
                )
            else:
                logger.info(f"Found existing Pinecone index: '{self.INDEX_NAME}'")

            self.index = self.pinecone_client.Index(self.INDEX_NAME)
            logger.info("Vector store initialized successfully.")

        except Exception as e:
            logger.error(
                f"Failed to initialize Pinecone VectorStore: {e}", exc_info=True
            )
            raise

    def embed_chunks(self, chunks: List[Chunk]) -> List[np.ndarray]:
        """Embeds a list of Chunks."""
        contents = [chunk.content for chunk in chunks]
        return self.model.encode(contents)

    async def upsert(self, chunks: List[Chunk]):
        """Upserts a list of Chunks into the vector store."""
        if not self.index:
            await self.initialize()
        if not chunks:
            return

        embeddings = self.embed_chunks(chunks)
        vectors_to_upsert = []
        for i, chunk in enumerate(chunks):
            document_id = chunk.metadata.get("document_id", "unknown_doc")
            chunk_id = f"{document_id}_{chunk.metadata.get('chunk_index', i)}"

            pinecone_metadata = {
                k: v
                for k, v in chunk.metadata.items()
                if isinstance(v, (str, int, float, bool, list))
            }
            # Crucially, store the original text content in the metadata for retrieval
            pinecone_metadata["content"] = chunk.content

            vectors_to_upsert.append(
                {
                    "id": chunk_id,
                    "values": embeddings[i].tolist(),
                    "metadata": pinecone_metadata,
                }
            )

        await asyncio.to_thread(
            self.index.upsert, vectors=vectors_to_upsert, namespace=self.NAMESPACE
        )
        logger.info(
            f"Upserted {len(chunks)} vectors into Pinecone index '{self.INDEX_NAME}'."
        )

    async def query(
        self, query_text: str, top_k: int = 5, filter_dict: Dict = None
    ) -> List[Dict[str, Any]]:
        if not self.index:
            await self.initialize()

        query_embedding = self.model.encode(query_text).tolist()

        results = await asyncio.to_thread(
            self.index.query,
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            filter=filter_dict,
            namespace=self.NAMESPACE,
        )

        processed_results = []
        for match in results.get("matches", []):
            processed_results.append(
                {
                    "score": match["score"],
                    "content": match["metadata"].get("content", ""),
                    "metadata": match["metadata"],
                }
            )
        return processed_results


async def main():
    """A simple main function to test the VectorStore with Pinecone."""
    logging.basicConfig(level=logging.INFO)

    try:
        store = VectorStore()
        await store.initialize()
    except Exception as e:
        logger.error(f"Failed to run main test: {e}")
        return

    chunks = [
        Chunk(
            content="Sophia AI is an orchestrator.",
            metadata={"document_id": "doc1", "chunk_index": 0, "type": "tech"},
        ),
        Chunk(
            content="Pay Ready focuses on automation.",
            metadata={"document_id": "doc1", "chunk_index": 1, "type": "business"},
        ),
    ]

    await store.upsert(chunks)
    await asyncio.sleep(5)

    query = "What is Sophia AI?"
    results = await store.query(query, top_k=1)

    print(f"\n--- Query Results for '{query}' ---")
    for res in results:
        print(
            f"Score: {res['score']:.4f}\nContent: '{res['content']}'\nMetadata: {res['metadata']}\n---"
        )


if __name__ == "__main__":
    asyncio.run(main())
