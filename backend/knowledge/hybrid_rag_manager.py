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
from backend.integrations.snowflake_integration import snowflake_integration

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
        Initializes connections to Pinecone and Snowflake.
        """
        if self.initialized:
            return
            
        logger.info("Initializing Hybrid RAG Manager...")
        try:
            # Initialize Vector Store (LlamaIndex/Pinecone)
            pinecone_api_key = await config_manager.get_secret("PINECONE_API_KEY")
            if not pinecone_api_key:
                raise ValueError("PINECONE_API_KEY secret not found.")

            self.pinecone_client = Pinecone(api_key=pinecone_api_key)
            index_name = "sophia-knowledge-base"
            pinecone_index = self.pinecone_client.Index(index_name)
            self.vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
            self.vector_index = VectorStoreIndex.from_vector_store(self.vector_store)
            
            # Initialize Structured Data Store (Snowflake)
            await snowflake_integration.initialize()
            
            self.initialized = True
            logger.info("Hybrid RAG Manager initialized successfully (Pinecone & Snowflake).")

        except Exception as e:
            logger.error(f"Failed to initialize Hybrid RAG Manager: {e}", exc_info=True)
            self.initialized = False

    async def answer_complex_question(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Answers a complex question by performing a hybrid RAG query.
        """
        if not self.initialized:
            return {"error": "RAG Manager not initialized."}

        logger.info(f"Performing hybrid RAG query for: '{query}'")

        try:
            # Step 1: Retrieve from Vector Store (Unstructured Data)
            retriever = VectorIndexRetriever(index=self.vector_index, similarity_top_k=top_k)
            query_engine = RetrieverQueryEngine(retriever=retriever)
            vector_response = await query_engine.aquery(query)
            unstructured_context = [node.get_content() for node in vector_response.source_nodes]

            # Step 2: Retrieve from SQL Store (Structured Data)
            # This is a generic, pre-defined query for demonstration.
            # A future version would generate this SQL dynamically based on the user query.
            structured_query = "SELECT COUNT(*) as total_calls, AVG(apartment_relevance_score) as avg_relevance FROM gong_calls;"
            structured_context = await snowflake_integration.execute_query(structured_query)

            # Step 3 (Future): Synthesize results from both sources using an LLM
            
            return {
                "success": True,
                "query": query,
                "unstructured_context": unstructured_context,
                "structured_context": structured_context,
                "final_answer_source": "Vector Store + Snowflake (synthesis not yet implemented)"
            }

        except Exception as e:
            logger.error(f"Error during hybrid RAG query: {e}", exc_info=True)
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