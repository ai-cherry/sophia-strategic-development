"""CoStar Data Ingestion Script
This script provides a simple command-line interface to ingest CoStar data files
(e.g., .xlsx, .csv) into the Sophia AI Knowledge Base.
"""
import argparse
import asyncio
import logging

# This allows the script to be run from the root directory and still find the backend modules
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from backend.knowledge_base.ingestion import IngestionPipeline
from backend.knowledge_base.metadata_store import MetadataStore
from backend.knowledge_base.vector_store import VectorStore

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def ingest_costar_file(file_path: Path, market_area: str, data_year: int):
    """Initializes the ingestion pipeline and processes a single CoStar data file.

    Args:
        file_path: The path to the CoStar data file.
        market_area: The primary market area for the data (e.g., 'austin', 'national').
        data_year: The year the data represents (e.g., 2023).
    """
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return

    logger.info("Initializing knowledge base components for ingestion...")
    try:
        # Initialize the stores. The vector store will connect to Pinecone.
        vector_store = VectorStore()
        metadata_store = MetadataStore()  # Using in-memory store for metadata

        # Create the ingestion pipeline
        pipeline = IngestionPipeline(vector_store, metadata_store)

        logger.info(f"Starting ingestion for CoStar file: {file_path.name}")

        # Ingest the document with specific metadata for CoStar
        await pipeline.ingest_document(
            file_path=file_path,
            document_type="costar_market_data",
            tags=["costar", market_area, str(data_year)],
        )

        logger.info("--- Ingestion Complete ---")
        logger.info(
            f"Successfully ingested '{file_path.name}' into the knowledge base."
        )
        logger.info(
            "You can now query this data using the 'knowledge' MCP server or agent."
        )

    except Exception as e:
        logger.error(
            f"An error occurred during the ingestion process: {e}", exc_info=True
        )
        logger.error(
            "Please ensure your PINECONE_API_KEY and other environment variables are set correctly."
        )


def main():
    """Main function to parse command-line arguments and run the ingestion.
    """
    parser = argparse.ArgumentParser(
        description="Ingest CoStar data files into the Sophia AI Knowledge Base."
    )
    parser.add_argument(
        "file_path",
        type=str,
        help="The full path to the CoStar data file (e.g., /path/to/data.xlsx).",
    )
    parser.add_argument(
        "--market",
        type=str,
        required=True,
        help="The market area the data belongs to (e.g., 'austin').",
    )
    parser.add_argument(
        "--year",
        type=int,
        required=True,
        help="The year the data represents (e.g., 2023).",
    )

    args = parser.parse_args()

    file_to_ingest = Path(args.file_path)

    asyncio.run(ingest_costar_file(file_to_ingest, args.market, args.year))


if __name__ == "__main__":
    main()
