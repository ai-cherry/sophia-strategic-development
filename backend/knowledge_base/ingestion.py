"""Ingestion Pipeline for the Knowledge Base
Coordinates parsing, chunking, and storing documents and their embeddings.
"""
import logging
import uuid
from pathlib import Path

from backend.knowledge_base.chunking import TextChunker
from backend.knowledge_base.metadata_store import DocumentMetadata, MetadataStore
from backend.knowledge_base.parsers import DocumentParser
from backend.knowledge_base.vector_store import VectorStore

logger = logging.getLogger(__name__)


class IngestionPipeline:
    """Orchestrates the process of ingesting a document into the knowledge base.
    """

    def __init__(self, vector_store: VectorStore, metadata_store: MetadataStore):
        """Initializes the ingestion pipeline.

        Args:
            vector_store: An instance of the VectorStore.
            metadata_store: An instance of the MetadataStore.
        """
        self.vector_store = vector_store
        self.metadata_store = metadata_store
        self.parser = DocumentParser()
        self.chunker = TextChunker()  # Using default chunking settings

    async def ingest_document(
        self, file_path: Path, document_type: str, tags: list = None
    ):
        """Processes a single document and adds it to the knowledge base.

        The process involves:
        1. Creating a unique ID and metadata for the document.
        2. Parsing the document to extract text.
        3. Splitting the text into manageable chunks.
        4. Storing the document and chunk metadata.
        5. Embedding the chunks and storing the vectors.

        Args:
            file_path: The path to the document file.
            document_type: A string describing the type of document (e.g., 'sales_deck').
            tags: A list of tags to associate with the document.
        """
        logger.info(f"Starting ingestion for document: {file_path}")
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return

        # 1. Create document metadata
        doc_id = str(uuid.uuid4())
        doc_meta = DocumentMetadata(
            document_id=doc_id,
            source=str(file_path),
            file_name=file_path.name,
            document_type=document_type,
            tags=tags or [],
        )

        # 2. Parse the document
        text_content = self.parser.parse(file_path)
        if not text_content:
            logger.error(
                f"Failed to extract text from {file_path}. Aborting ingestion."
            )
            return

        # 3. Split the text into chunks
        # Add the document ID to each chunk's metadata
        chunk_base_metadata = {"document_id": doc_id, "file_name": file_path.name}
        chunks = self.chunker.create_chunks(text_content, chunk_base_metadata)

        # Add original content to metadata for Pinecone retrieval
        for chunk in chunks:
            chunk.metadata["content"] = chunk.content
            chunk.metadata["document_type"] = document_type

        if not chunks:
            logger.warning(
                f"No chunks were created for {file_path}. Nothing to ingest."
            )
            return

        # 4. Store document and chunk metadata
        self.metadata_store.add_document(doc_meta)
        self.metadata_store.add_chunks(chunks)

        # 5. Embed and store vectors
        await self.vector_store.upsert(chunks)

        logger.info(
            f"Successfully ingested document {file_path.name} with {len(chunks)} chunks."
        )


async def main():
    """A simple main function to test the ingestion pipeline."""
    import asyncio

    logging.basicConfig(level=logging.INFO)
    logger.info("--- Testing Ingestion Pipeline ---")

    # Initialize components
    vector_store = VectorStore()
    metadata_store = MetadataStore()
    pipeline = IngestionPipeline(vector_store, metadata_store)

    # Create a dummy file for testing
    test_dir = Path("test_ingestion_docs")
    test_dir.mkdir(exist_ok=True)
    test_file_path = test_dir / "pay_ready_mission.txt"
    with open(test_file_path, "w") as f:
        f.write("Pay Ready's mission is to revolutionize business intelligence.\n")
        f.write("Our culture is built on innovation and customer focus.")

    # Ingest the document
    await pipeline.ingest_document(
        file_path=test_file_path,
        document_type="mission_statement",
        tags=["core_values", "company_info"],
    )

    # Verify ingestion
    print("\n--- Verification ---")
    # Check metadata store
    doc_id = list(metadata_store.documents.keys())[0]
    doc = metadata_store.get_document(doc_id)
    print(f"Document in metadata store: {doc.file_name}, Type: {doc.document_type}")
    chunks_in_meta = metadata_store.get_chunks_for_document(doc_id)
    print(f"Chunks in metadata store: {len(chunks_in_meta)}")

    # Check vector store (by querying)
    # Give Pinecone a moment to index if it's the first run
    await asyncio.sleep(5)
    query_results = await vector_store.query("What is the company mission?", top_k=1)
    print("\nQuerying for 'What is the company mission?'...")
    if query_results:
        print(f"Found result in vector store: '{query_results[0]['content']}'")
    else:
        print("Did not find a result in the vector store.")

    # Clean up
    import shutil

    shutil.rmtree(test_dir)


if __name__ == "__main__":
    asyncio.run(main())
