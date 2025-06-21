"""Ingestion Pipeline for the Codebase Awareness System.

Scans the codebase, applies the appropriate architectural parsers,
and prepares the structured data for vectorization and storage.
"""

import logging
import uuid
from pathlib import Path
from typing import Any, Dict, List

from backend.codebase_awareness.architecture_parsers import ArchitectureParser
from backend.knowledge_base.chunking import Chunk  # Re-using the Chunk dataclass
from backend.knowledge_base.metadata_store import (
    MetadataStore,  # Can be adapted for code
)
from backend.knowledge_base.vector_store import VectorStore

logger = logging.getLogger(__name__)


class CodebaseIngestionPipeline:
    """Orchestrates the process of scanning and ingesting the entire codebase.

            to build the architectural awareness knowledge base.
    """

    def __init__(
        self,
        vector_store: VectorStore,
        metadata_store: MetadataStore,
        project_root: Path,
    ):
        self.vector_store = vector_store
        self.metadata_store = (
            metadata_store  # We can use the same metadata store for now
        )
        self.project_root = project_root
        self.parser = ArchitectureParser()

    def scan_and_parse_project(self) -> List[Dict[str, Any]]:
        """Scans the entire project directory and uses the specialized parsers.

                        to extract structured architectural information.

                        Returns:
                            A flat list of all discovered architectural items (functions, classes,
                            API endpoints, MCP tools, DB tables).
        """
        all_items = []

        # Define directories to scan for specific components
        mcp_dir = self.project_root / "backend" / "mcp"
        routes_dir = self.project_root / "backend" / "app" / "routes"
        db_dir = self.project_root / "database" / "init"

        logger.info(f"Starting codebase scan from root: {self.project_root}")

        for p in self.project_root.rglob("*"):
            if p.is_file():
                if self._should_ignore(p):
                    continue

                try:
                    content = p.read_text(encoding="utf-8")

                    if p.suffix == ".py":
                        all_items.extend(self.parser.parse_python_code(content, str(p)))
                        # Check for specific Python file types
                        if mcp_dir in p.parents:
                            all_items.extend(
                                self.parser.parse_mcp_tools(content, str(p))
                            )
                        if routes_dir in p.parents:
                            all_items.extend(
                                self.parser.parse_fastapi_routes(content, str(p))
                            )

                    elif p.suffix == ".sql":
                        if db_dir in p.parents:
                            all_items.extend(
                                self.parser.parse_db_schema(content, str(p))
                            )

                except Exception as e:
                    logger.warning(f"Could not read or parse file {p}: {e}")

        logger.info(
            f"Codebase scan complete. Found {len(all_items)} architectural items."
        )
        return all_items

    async def ingest_codebase(self):
        """Performs a full scan and ingestion of the project codebase."""

        logger.info("Starting full codebase ingestion...")

        architectural_items = self.scan_and_parse_project()

        if not architectural_items:
            logger.warning("No architectural items found to ingest.")
            return

        # Convert these items into the Chunk format for the stores
        chunks_to_ingest = []
        for item in architectural_items:
            # Create a descriptive content string for embedding
            content_for_embedding = self._create_embedding_content(item)

            # Use a unique ID for each architectural item
            item_id = str(uuid.uuid4())
            item["item_id"] = item_id

            chunks_to_ingest.append(Chunk(content=content_for_embedding, metadata=item))

        # Upsert into the vector and metadata stores
        await self.vector_store.upsert(chunks_to_ingest)
        # The metadata store might need adaptation, but for now we'll assume it can handle this
        # self.metadata_store.add_chunks(chunks_to_ingest)

        logger.info(f"Successfully ingested {len(chunks_to_ingest)} codebase items.")

    def _create_embedding_content(self, item: Dict[str, Any]) -> str:
        """Creates a single string from a structured item to be used for embedding.

                        This string should contain all the semantically important information.
        """item_type = item.get("type").

        if item_type == "python_function":
            return f"Function Name: {item.get('name')}\nDocstring: {item.get('docstring')}\nCode:\n{item.get('code')}"
        elif item_type == "python_class":
            return f"Class Name: {item.get('name')}\nDocstring: {item.get('docstring')}"
        elif item_type == "api_endpoint":
            return f"API Endpoint: {item.get('method')} {item.get('path')}\nDescription: {item.get('docstring')}"
        elif item_type == "mcp_tool":
            return (
                f"MCP Tool: {item.get('name')}\nDescription: {item.get('description')}"
            )
        elif item_type == "db_table":
            return f"Database Table: {item.get('table_name')}\nSchema: {item.get('raw_schema')}"
        else:
            return str(item)

    def _should_ignore(self, path: Path) -> bool:
        """Determines if a file or directory should be ignored during scanning."""ignored_dirs = ["__pycache__", ".git", "node_modules", "venv", "sophia_venv"].

        ignored_parts = set(path.parts).intersection(ignored_dirs)
        return bool(ignored_parts)


async def main():
    """A simple main function to test the codebase ingestion pipeline."""
    logging.basicConfig(level=logging.INFO)

    # We need a dedicated vector store for the codebase
    # For testing, we can simulate this by changing the index name
    codebase_vector_store = VectorStore()
    codebase_vector_store.INDEX_NAME = "sophia-codebase-awareness-test"

    # We can reuse the metadata store logic
    codebase_metadata_store = MetadataStore()

    # The pipeline needs the project root
    project_root = Path(__file__).parent.parent.parent

    pipeline = CodebaseIngestionPipeline(
        codebase_vector_store, codebase_metadata_store, project_root
    )

    # Perform the ingestion
    await pipeline.ingest_codebase()


if __name__ == "__main__":
    asyncio.run(main())
