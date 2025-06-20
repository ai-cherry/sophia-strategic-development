"""Query Engine for the Knowledge Base
Handles performing hybrid search over the vector and metadata stores.
"""
import logging
from typing import Any, Dict, List, Optional

from backend.knowledge_base.metadata_store import MetadataStore
from backend.knowledge_base.vector_store import VectorStore

logger = logging.getLogger(__name__)


class QueryEngine:
    """Handles search queries against the knowledge base, combining
    semantic vector search with structured metadata filtering.
    """

    def __init__(self, vector_store: VectorStore, metadata_store: MetadataStore):
        """Initializes the QueryEngine.

        Args:
            vector_store: An instance of the VectorStore.
            metadata_store: An instance of the MetadataStore.
        """
        self.vector_store = vector_store
        self.metadata_store = metadata_store

    async def search(
        self, query_text: str, top_k: int = 5, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Performs a hybrid search.

        Args:
            query_text: The natural language query.
            top_k: The maximum number of results to return.
            filters: A dictionary of metadata key-value pairs to filter on.
                     Example: {"document_type": "sales_deck", "tag": "q1"}

        Returns:
            A list of result dictionaries, each containing the content,
            metadata, and similarity score.
        """
        logger.info(
            f"Performing search for query: '{query_text}' with filters: {filters}"
        )

        # The filtering logic depends on the vector database's capabilities.
        # Pinecone supports metadata filtering directly in the query.
        # We will pass the filter dictionary to the vector store's query method.

        # Note: If the vector DB did not support filtering, the logic would be:
        # 1. Filter documents in the metadata store.
        # 2. Get the IDs of the resulting chunks.
        # 3. Pass those IDs as a filter to the vector store query.
        # But since Pinecone is powerful, we can do it in one step.

        try:
            vector_search_results = await self.vector_store.query(
                query_text=query_text, top_k=top_k, filter_dict=filters
            )

            # The results from vector_store.query are already in the desired format.
            # We could potentially add more information from the metadata store here if needed,
            # for example, fetching the full document metadata.

            enriched_results = []
            for res in vector_search_results:
                doc_id = res["metadata"].get("document_id")
                if doc_id:
                    doc_meta = self.metadata_store.get_document(doc_id)
                    if doc_meta:
                        # Add full document metadata to the result
                        res["document_metadata"] = {
                            "source": doc_meta.source,
                            "tags": doc_meta.tags,
                            "created_at": doc_meta.created_at.isoformat(),
                        }
                enriched_results.append(res)

            logger.info(f"Search completed with {len(enriched_results)} results.")
            return enriched_results

        except Exception as e:
            logger.error(f"An error occurred during search: {e}", exc_info=True)
            return []


async def main():
    """A simple main function to test the QueryEngine."""
    import asyncio
    from pathlib import Path

    from backend.knowledge_base.ingestion import IngestionPipeline

    logging.basicConfig(level=logging.INFO)
    logger.info("--- Testing Query Engine ---")

    # 1. Setup and Ingest Data
    vector_store = VectorStore()
    metadata_store = MetadataStore()
    ingestion_pipeline = IngestionPipeline(vector_store, metadata_store)
    query_engine = QueryEngine(vector_store, metadata_store)

    # Create dummy files
    test_dir = Path("test_query_docs")
    test_dir.mkdir(exist_ok=True)

    file1_path = test_dir / "product_A_deck.txt"
    with open(file1_path, "w") as f:
        f.write(
            "Product A increases team productivity by 20%. It is designed for enterprise clients."
        )

    file2_path = test_dir / "product_B_sheet.txt"
    with open(file2_path, "w") as f:
        f.write(
            "Product B reduces operational costs. It is ideal for small businesses."
        )

    # Ingest documents
    await ingestion_pipeline.ingest_document(
        file1_path, "sales_deck", ["enterprise", "productivity"]
    )
    await ingestion_pipeline.ingest_document(file2_path, "fact_sheet", ["smb", "costs"])

    # Give Pinecone a moment to index
    logger.info("Waiting for indexing...")
    await asyncio.sleep(5)

    # 2. Perform Searches

    # Simple semantic search
    print("\n--- Test 1: Simple Semantic Search ---")
    results1 = await query_engine.search("How can I make my team more efficient?")
    for res in results1:
        print(f"Score: {res['score']:.4f} | Content: '{res['content']}'")

    # Search with metadata filter
    print("\n--- Test 2: Search with Metadata Filter ---")
    results2 = await query_engine.search(
        "Tell me about your products", filters={"document_type": "fact_sheet"}
    )
    for res in results2:
        print(
            f"Score: {res['score']:.4f} | Content: '{res['content']}' | Metadata: {res['metadata']}"
        )

    # Clean up
    import shutil

    shutil.rmtree(test_dir)


if __name__ == "__main__":
    asyncio.run(main())
