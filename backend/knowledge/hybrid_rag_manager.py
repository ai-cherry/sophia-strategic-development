"""
Hybrid RAG Manager for Sophia AI
Orchestrates Retrieval-Augmented Generation (RAG) queries across
structured (SQL) and unstructured (vector) data sources.
"""

import asyncio
import logging
from typing import Dict, Any, Optional

from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone

from backend.core.config_manager import config_manager

logger = logging.getLogger(__name__)

class HybridRAGManager:
    """
    Manages complex RAG queries by combining vector search with structured data lookups.
    """
    
    def __init__(self):
        self.vector_store = None
        self.vector_index = None
        self.pinecone_client = None
        self.initialized = False

    async def initialize(self):
        """
        Initializes the connection to Pinecone and sets up the LlamaIndex components.
        """
        if self.initialized:
            return
            
        logger.info("Initializing Hybrid RAG Manager...")
        try:
            pinecone_api_key = await config_manager.get_secret("PINECONE_API_KEY")
            if not pinecone_api_key:
                raise ValueError("PINECONE_API_KEY secret not found.")

            self.pinecone_client = Pinecone(api_key=pinecone_api_key)
            
            # Assuming our knowledge base index is named 'sophia-knowledge-base'
            index_name = "sophia-knowledge-base"
            pinecone_index = self.pinecone_client.Index(index_name)
            
            self.vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
            self.vector_index = VectorStoreIndex.from_vector_store(self.vector_store)
            
            self.initialized = True
            logger.info("Hybrid RAG Manager initialized successfully.")

        except Exception as e:
            logger.error(f"Failed to initialize Hybrid RAG Manager: {e}", exc_info=True)
            self.initialized = False

    async def answer_complex_question(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Answers a complex question by performing a hybrid RAG query.
        
        This is a foundational implementation. It currently only queries the vector store.
        Future enhancements will add a structured data retrieval step.
        """
        if not self.initialized:
            return {"error": "RAG Manager not initialized."}

        logger.info(f"Performing RAG query for: '{query}'")

        try:
            # Step 1: Retrieve from Vector Store using LlamaIndex
            retriever = VectorIndexRetriever(index=self.vector_index, similarity_top_k=top_k)
            query_engine = RetrieverQueryEngine(retriever=retriever)
            
            vector_response = await query_engine.aquery(query)
            
            # Step 2 (Future): Query structured data based on the query or vector results
            # For example, look up financial details from Snowflake for a retrieved company name.
            structured_context = "No structured data queried in this version."

            # Step 3 (Future): Synthesize results from both sources using an LLM
            # For now, we return the retrieved vector context directly.
            
            return {
                "success": True,
                "query": query,
                "vector_context": [node.get_content() for node in vector_response.source_nodes],
                "structured_context": structured_context,
                "final_answer_source": "Vector Store Only (synthesis not yet implemented)"
            }

        except Exception as e:
            logger.error(f"Error during RAG query: {e}", exc_info=True)
            return {"error": str(e)}

# Global instance
hybrid_rag_manager = HybridRAGManager()

async def main():
    """Manual test for the HybridRAGManager."""
    print("Testing Hybrid RAG Manager...")
    # NOTE: Requires PINECONE_API_KEY to be set
    await config_manager.initialize()
    await hybrid_rag_manager.initialize()
    
    if hybrid_rag_manager.initialized:
        test_query = "What were the key takeaways from the latest all-hands meeting?"
        result = await hybrid_rag_manager.answer_complex_question(test_query)
        print("\nQuery Result:")
        print(json.dumps(result, indent=2))
        print("\n✅ Hybrid RAG Manager test completed.")
    else:
        print("\n❌ Hybrid RAG Manager test failed during initialization.")

if __name__ == '__main__':
    import json
    asyncio.run(main()) 