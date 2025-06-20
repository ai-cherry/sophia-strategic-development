"""Metadata Store for the Knowledge Base
Handles the storage and retrieval of document and chunk metadata.
"""
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.knowledge_base.chunking import Chunk

logger = logging.getLogger(__name__)


@dataclass
class DocumentMetadata:
    """Represents the metadata for a single document."""

    document_id: str
    source: str  # e.g., file path, URL
    file_name: Optional[str] = None
    document_type: Optional[str] = None  # e.g., 'pdf', 'sales_deck', 'client_list'
    created_at: datetime = field(default_factory=datetime.utcnow)
    tags: List[str] = field(default_factory=list)
    custom_properties: Dict[str, Any] = field(default_factory=dict)


class MetadataStore:
    """An abstraction for a metadata database (e.g., PostgreSQL).
    This implementation uses a simple in-memory store for demonstration.
    """

    def __init__(self):
        """Initializes the MetadataStore."""
        # In-memory storage
        # {document_id: DocumentMetadata}
        self.documents: Dict[str, DocumentMetadata] = {}
        # {chunk_id: Chunk}
        self.chunks: Dict[str, Chunk] = {}
        logger.info("In-memory metadata store initialized.")

    def add_document(self, doc_meta: DocumentMetadata) -> bool:
        """Adds a new document to the store.

        Args:
            doc_meta: The DocumentMetadata object to add.

        Returns:
            True if the document was added, False if it already exists.
        """
        if doc_meta.document_id in self.documents:
            logger.warning(f"Document with ID {doc_meta.document_id} already exists.")
            return False

        self.documents[doc_meta.document_id] = doc_meta
        logger.info(f"Added document: {doc_meta.file_name or doc_meta.document_id}")
        return True

    def get_document(self, document_id: str) -> Optional[DocumentMetadata]:
        """Retrieves a document by its ID."""
        return self.documents.get(document_id)

    def add_chunks(self, chunks: List[Chunk]):
        """Adds a list of chunks to the store.

        Args:
            chunks: A list of Chunk objects.
        """
        for i, chunk in enumerate(chunks):
            document_id = chunk.metadata.get("document_id")
            if not document_id:
                logger.warning(
                    "Chunk is missing a document_id in its metadata. Skipping."
                )
                continue

            chunk_id = f"{document_id}_{chunk.metadata.get('chunk_index', i)}"
            self.chunks[chunk_id] = chunk

        logger.info(f"Added {len(chunks)} chunks to the metadata store.")

    def get_chunk(self, chunk_id: str) -> Optional[Chunk]:
        """Retrieves a chunk by its unique ID."""
        return self.chunks.get(chunk_id)

    def filter_documents(self, key: str, value: Any) -> List[DocumentMetadata]:
        """Filters documents based on a metadata key-value pair.

        Args:
            key: The metadata key to filter on (e.g., 'document_type', 'tag').
            value: The value to match.

        Returns:
            A list of matching DocumentMetadata objects.
        """
        results = []
        for doc in self.documents.values():
            if key == "tag" and value in doc.tags:
                results.append(doc)
            elif hasattr(doc, key) and getattr(doc, key) == value:
                results.append(doc)
            elif key in doc.custom_properties and doc.custom_properties[key] == value:
                results.append(doc)

        logger.info(
            f"Filtered documents on '{key}={value}', found {len(results)} results."
        )
        return results

    def get_chunks_for_document(self, document_id: str) -> List[Chunk]:
        """Retrieves all chunks associated with a specific document.

        Args:
            document_id: The ID of the document.

        Returns:
            A list of Chunk objects.
        """
        # This is inefficient for an in-memory store, but mimics a DB query.
        return [
            chunk
            for chunk in self.chunks.values()
            if chunk.metadata.get("document_id") == document_id
        ]


async def main():
    """A simple main function to test the MetadataStore."""
    store = MetadataStore()

    # Create and add a document
    doc1_meta = DocumentMetadata(
        document_id="doc_001",
        source="/path/to/sales_deck.pptx",
        file_name="sales_deck.pptx",
        document_type="sales_presentation",
        tags=["q1", "finance"],
    )
    store.add_document(doc1_meta)

    # Create and add chunks for that document
    chunks = [
        Chunk(
            content="The first key point about ROI.",
            metadata={"document_id": "doc_001", "chunk_index": 0},
        ),
        Chunk(
            content="A detailed breakdown of financial benefits.",
            metadata={"document_id": "doc_001", "chunk_index": 1},
        ),
    ]
    store.add_chunks(chunks)

    print("\n--- Metadata Store Content ---")
    print(f"Total documents: {len(store.documents)}")
    print(f"Total chunks: {len(store.chunks)}")

    # Test filtering
    print("\n--- Filtering for sales presentations ---")
    sales_docs = store.filter_documents("document_type", "sales_presentation")
    for doc in sales_docs:
        print(f"Found doc: {doc.file_name}")

    # Test getting chunks for a document
    print("\n--- Getting chunks for doc_001 ---")
    doc1_chunks = store.get_chunks_for_document("doc_001")
    for chunk in doc1_chunks:
        print(f"Chunk {chunk.metadata['chunk_index']}: '{chunk.content}'")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
