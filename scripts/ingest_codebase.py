import asyncio
import logging
import os
from pathlib import Path
from typing import Any, Dict, List

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Constants
# In a real implementation, these would come from a config file
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
PINECONE_INDEX_NAME = "sophia-repository-context"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Add file types to explicitly include
INCLUDED_EXTENSIONS = {
    ".py",
    ".md",
    ".tsx",
    ".ts",
    ".jsx",
    ".js",
    ".sql",
    ".yml",
    ".yaml",
    ".json",
    "Dockerfile",
    ".env.example",
    ".sh",
}
# Add directories to explicitly exclude
EXCLUDED_DIRECTORIES = {
    "__pycache__",
    "node_modules",
    ".git",
    "venv",
    "sophia_venv",
    "dist",
    "build",
    ".vscode",
    ".idea",
}


class RepositoryIntelligenceService:
    """Analyzes, chunks, and prepares repository content for vectorization."""

    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        # In a real implementation, we would initialize clients here
        # self.vector_store = PineconeClient(...)
        # self.embedding_model = OpenAIEmbeddings(...)
        logging.info(
            f"Initializing Repository Intelligence Service for path: {self.root_path}"
        )

    def scan_repository(self) -> List[Path]:
        """Scans the repository for relevant files to ingest."""
        logging.info("Scanning repository for relevant files...")
        relevant_files = []
        for path in self.root_path.rglob("*"):
            if any(part in EXCLUDED_DIRECTORIES for part in path.parts):
                continue

            if path.is_file():
                if (
                    path.suffix in INCLUDED_EXTENSIONS
                    or path.name in INCLUDED_EXTENSIONS
                ):
                    relevant_files.append(path)

        logging.info(f"Found {len(relevant_files)} relevant files to process.")
        return relevant_files

    def chunk_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Chunk a single file into processable segments with metadata.

        This is a simple chunking strategy. More advanced strategies could use
        tree-sitter for code or specific markdown parsers.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            logging.warning(f"Could not read file {file_path}: {e}")
            return []

        # Simple strategy: chunk by lines, with overlap
        lines = content.splitlines()
        chunks = []
        chunk_size = 100  # lines
        overlap = 10  # lines

        for i in range(0, len(lines), chunk_size - overlap):
            chunk_content = "\n".join(lines[i : i + chunk_size])
            if not chunk_content:
                continue

            chunk = {
                "content": chunk_content,
                "metadata": {
                    "source": str(file_path.relative_to(self.root_path)),
                    "start_line": i + 1,
                    "end_line": i + len(chunk_content.splitlines()),
                    "file_type": file_path.suffix or file_path.name,
                },
            }
            chunks.append(chunk)

        return chunks

    async def process_repository(self) -> List[Dict[str, Any]]:
        """Processes all relevant files in the repository."""
        files = self.scan_repository()
        all_chunks = []

        for file_path in files:
            logging.info(f"Chunking file: {file_path}")
            file_chunks = self.chunk_file(file_path)
            all_chunks.extend(file_chunks)

        logging.info(f"Total chunks created: {len(all_chunks)}")
        # In the next step, these chunks would be passed to a vectorization and
        # storage service.
        return all_chunks


async def main():
    """Main execution function."""
    logging.info("Starting repository ingestion process...")

    # We assume the script is run from the root of the repository
    repo_path = os.getcwd()

    intelligence_service = RepositoryIntelligenceService(root_path=repo_path)
    chunks = await intelligence_service.process_repository()

    # Here we would add the logic to vectorize and upload to Pinecone
    # For now, we just show the count.
    logging.info(f"Successfully generated {len(chunks)} chunks for vectorization.")
    logging.info("Ingestion process script completed.")


if __name__ == "__main__":
    # NOTE: This script requires environment variables for API keys:
    # PINECONE_API_KEY, OPENAI_API_KEY
    # It is designed to be run within the project's environment.
    asyncio.run(main())
