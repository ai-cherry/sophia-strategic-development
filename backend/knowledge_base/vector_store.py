"""
Vector Store for the Knowledge Base
Handles the storage and retrieval of text embeddings (vectors) using Pinecone.
"""
import logging
import asyncio
from typing import List, Dict, Any, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec

from backend.knowledge_base.chunking import Chunk
from infrastructure.esc.pinecone_secrets import pinecone_secret_manager

logger = logging.getLogger(__name__)

class VectorStore:
    """
    An abstraction for Pinecone's vector database.
    """
    INDEX_NAME = "sophia-knowledge-base"

    def __init__(self, embedding_model_name: str = 'all-MiniLM-L6-v2'):
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
                logger.info(f"Pinecone index '{self.INDEX_NAME}' not found. Creating it now...")
                self.pinecone_client.create_index(
                    name=self.INDEX_NAME,
                    dimension=self.model.get_sentence_embedding_dimension(),
                    metric='cosine',
                    spec=ServerlessSpec(cloud='aws', region='us-west-2')
                )
                logger.info("Pinecone index created successfully.")
            else:
                logger.info(f"Found existing Pinecone index: '{self.INDEX_NAME}'")

            self.index = self.pinecone_client.Index(self.INDEX_NAME)
            logger.info("Vector store initialized successfully.")
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone VectorStore: {e}", exc_info=True)
            raise

    def embed_chunks(self, chunks: List[Chunk]) -> List[np.ndarray]:
        logger.info(f"Embedding {len(chunks)} chunks...")
        contents = [chunk.content for chunk in chunks]
        embeddings = self.model.encode(contents, show_progress_bar=True)
        logger.info("Finished embedding chunks.")
        return embeddings

    async def upsert(self, chunks: List[Chunk]):
        if not self.index:
            await self.initialize()
        if not chunks:
            return
            
        embeddings = self.embed_chunks(chunks)
        vectors_to_upsert = []
        for i, chunk in enumerate(chunks):
            document_id = chunk.metadata.get('document_id', 'unknown_doc')
            chunk_id = f"{document_id}_{chunk.metadata.get('chunk_index', i)}"
            
            # Pinecone metadata must have string, number, or boolean values
            pinecone_metadata = {k: v for k, v in chunk.metadata.items() if isinstance(v, (str, int, float, bool, list))}
            
            vectors_to_upsert.append({
                "id": chunk_id,
                "values": embeddings[i].tolist(),
                "metadata": pinecone_metadata
            })
        
        self.index.upsert(vectors=vectors_to_upsert)
        logger.info(f"Upserted {len(chunks)} vectors into Pinecone index '{self.INDEX_NAME}'.")

    async def query(self, query_text: str, top_k: int = 5, filter_dict: Dict = None) -> List[Dict[str, Any]]:
        if not self.index:
            await self.initialize()
            
        logger.info(f"Executing query: '{query_text}' with filter: {filter_dict}")
        query_embedding = self.model.encode(query_text).tolist()
        
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            filter=filter_dict
        )
        
        processed_results = []
        for match in results.get('matches', []):
            processed_results.append({
                "score": match['score'],
                "content": match['metadata'].get('content', ''), # Assuming content is stored in metadata
                "metadata": match['metadata']
            })
            
        logger.info(f"Query returned {len(processed_results)} results from Pinecone.")
        return processed_results


async def main():
    """A simple main function to test the VectorStore with Pinecone."""
    logging.basicConfig(level=logging.INFO)
    
    # This requires PINECONE_API_KEY to be in the environment for fallback
    # or Pulumi ESC to be configured correctly.
    try:
        store = VectorStore()
        await store.initialize()
    except Exception as e:
        logger.error(f"Failed to run main test: {e}")
        logger.info("Please ensure PINECONE_API_KEY is set in your environment or Pulumi ESC is configured.")
        return

    # Create some dummy chunks
    chunks = [
        Chunk(content="Sophia AI is an orchestrator for Pay Ready.", metadata={"document_id": "doc1", "chunk_index": 0, "type": "tech"}),
        Chunk(content="Pay Ready focuses on business intelligence and automation.", metadata={"document_id": "doc1", "chunk_index": 1, "type": "business"}),
        Chunk(content="The primary CRM integration is with HubSpot.", metadata={"document_id": "doc2", "chunk_index": 0, "type": "tech"}),
        Chunk(content="Gong.io is used for call analysis.", metadata={"document_id": "doc2", "chunk_index": 1, "type": "tech"}),
    ]
    # Add content to metadata for retrieval
    for chunk in chunks:
        chunk.metadata['content'] = chunk.content

    # Upsert the chunks
    await store.upsert(chunks)
    
    # Give Pinecone a moment to index
    await asyncio.sleep(5)

    # Perform a query
    query = "What is the main focus of the company?"
    results = await store.query(query, top_k=2)
    
    print(f"\n--- Query Results for '{query}' ---")
    for res in results:
        print(f"Score: {res['score']:.4f}")
        print(f"Content: '{res['content']}'")
        print(f"Metadata: {res['metadata']}")
        print("-" * 20)

    # Perform a filtered query
    filtered_query = "What tools are used?"
    results_filtered = await store.query(filtered_query, top_k=2, filter_dict={"type": "tech"})
    
    print(f"\n--- Filtered Query Results for '{filtered_query}' (type=tech) ---")
    for res in results_filtered:
        print(f"Score: {res['score']:.4f}")
        print(f"Content: '{res['content']}'")
        print(f"Metadata: {res['metadata']}")
        print("-" * 20)
        
if __name__ == "__main__":
    asyncio.run(main()) 