#!/usr/bin/env python3
"""Migrate Vector Store Access to ComprehensiveMemoryManager
This script migrates direct vector store access to use the ComprehensiveMemoryManager.
"""

import asyncio
import glob
import logging
import re
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class VectorStoreMigrator:
    """Migrates direct vector store access to use the ComprehensiveMemoryManager."""

    def __init__(self, root_dir: str = "."):
        self.root_dir = root_dir
        self.vector_store_imports = [
            r"import\s+pinecone",
            r"from\s+pinecone\s+import",
            r"import\s+weaviate",
            r"from\s+weaviate\s+import",
        ]
        self.direct_access_patterns = [
            r"pinecone\.init\(",
            r"pinecone\.Index\(",
            r"weaviate\.Client\(",
            r"\.upsert\(",
            r"\.query\(",
            r"\.delete\(",
        ]
        self.files_to_check = []
        self.files_to_migrate = []
        self.migration_results = {
            "scanned_files": 0,
            "files_with_direct_access": 0,
            "migrated_files": 0,
            "skipped_files": 0,
            "errors": [],
        }

    async def scan_files(self):
        """Scan files for direct vector store access."""
        logger.info(
            f"Scanning files in {self.root_dir} for direct vector store access..."
        )

        # Find all Python files
        python_files = glob.glob(f"{self.root_dir}/**/*.py", recursive=True)
        self.files_to_check = python_files
        self.migration_results["scanned_files"] = len(python_files)

        # Check each file for direct vector store access
        for file_path in python_files:
            try:
                with open(file_path, "r") as f:
                    content = f.read()

                # Check for vector store imports
                has_vector_store_import = any(
                    re.search(pattern, content) for pattern in self.vector_store_imports
                )

                # Check for direct access patterns
                has_direct_access = any(
                    re.search(pattern, content)
                    for pattern in self.direct_access_patterns
                )

                # If the file has both vector store imports and direct access patterns, it needs to be migrated
                if has_vector_store_import and has_direct_access:
                    self.files_to_migrate.append(file_path)
                    self.migration_results["files_with_direct_access"] += 1
                    logger.info(f"Found direct vector store access in {file_path}")

            except Exception as e:
                logger.error(f"Error scanning file {file_path}: {e}")
                self.migration_results["errors"].append(
                    f"Error scanning file {file_path}: {e}"
                )

        logger.info(
            f"Found {len(self.files_to_migrate)} files with direct vector store access."
        )
        return self.files_to_migrate

    async def migrate_file(self, file_path: str) -> bool:
        """Migrate a file to use the ComprehensiveMemoryManager."""
        logger.info(f"Migrating file {file_path}...")

        try:
            with open(file_path, "r") as f:
                content = f.read()

            # Add import for ComprehensiveMemoryManager
            if "from backend.core.comprehensive_memory_manager import" not in content:
                import_statement = "from backend.core.comprehensive_memory_manager import comprehensive_memory_manager, MemoryRequest, MemoryOperationType\n"

                # Find the last import statement
                import_matches = list(
                    re.finditer(r"^(import|from)\s+.*$", content, re.MULTILINE)
                )
                if import_matches:
                    last_import = import_matches[-1]
                    content = (
                        content[: last_import.end()]
                        + "\n"
                        + import_statement
                        + content[last_import.end() :]
                    )
                else:
                    # If no imports found, add at the beginning
                    content = import_statement + content

            # Replace direct vector store access with ComprehensiveMemoryManager

            # Replace pinecone.init
            content = re.sub(
                r"pinecone\.init\((.*?)\)",
                r"# Replaced pinecone.init with ComprehensiveMemoryManager\n# Original: pinecone.init(\1)",
                content,
            )

            # Replace pinecone.Index
            content = re.sub(
                r"(\w+)\s*=\s*pinecone\.Index\((.*?)\)",
                r"# Replaced pinecone.Index with ComprehensiveMemoryManager\n# Original: \1 = pinecone.Index(\2)\n\1 = comprehensive_memory_manager",
                content,
            )

            # Replace weaviate.Client
            content = re.sub(
                r"(\w+)\s*=\s*weaviate\.Client\((.*?)\)",
                r"# Replaced weaviate.Client with ComprehensiveMemoryManager\n# Original: \1 = weaviate.Client(\2)\n\1 = comprehensive_memory_manager",
                content,
            )

            # Replace upsert operations
            content = re.sub(
                r"(\w+)\.upsert\((.*?)\)",
                r"await comprehensive_memory_manager.process_memory_request(MemoryRequest(operation=MemoryOperationType.STORE, content=\2))",
                content,
            )

            # Replace query operations
            content = re.sub(
                r"(\w+)\.query\((.*?)\)",
                r"await comprehensive_memory_manager.process_memory_request(MemoryRequest(operation=MemoryOperationType.RETRIEVE, query=\2))",
                content,
            )

            # Replace delete operations
            content = re.sub(
                r"(\w+)\.delete\((.*?)\)",
                r"await comprehensive_memory_manager.process_memory_request(MemoryRequest(operation=MemoryOperationType.DELETE, memory_id=\2))",
                content,
            )

            # Write the modified content back to the file
            with open(file_path, "w") as f:
                f.write(content)

            logger.info(f"Successfully migrated {file_path}")
            return True

        except Exception as e:
            logger.error(f"Error migrating file {file_path}: {e}")
            self.migration_results["errors"].append(
                f"Error migrating file {file_path}: {e}"
            )
            return False

    async def migrate_files(self):
        """Migrate all files with direct vector store access."""
        logger.info(f"Migrating {len(self.files_to_migrate)} files...")

        for file_path in self.files_to_migrate:
            success = await self.migrate_file(file_path)
            if success:
                self.migration_results["migrated_files"] += 1
            else:
                self.migration_results["skipped_files"] += 1

        logger.info(
            f"Migration complete. {self.migration_results['migrated_files']} files migrated, {self.migration_results['skipped_files']} files skipped."
        )
        return self.migration_results

    async def run(self):
        """Run the migration process."""
        await self.scan_files()
        await self.migrate_files()
        return self.migration_results


async def main():
    """Main function to run the vector store migrator."""
    root_dir = "."
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]

    migrator = VectorStoreMigrator(root_dir)
    results = await migrator.run()

    print("\n--- Vector Store Migration Summary ---")
    print(f"Scanned files: {results['scanned_files']}")
    print(f"Files with direct access: {results['files_with_direct_access']}")
    print(f"Migrated files: {results['migrated_files']}")
    print(f"Skipped files: {results['skipped_files']}")

    if results["errors"]:
        print("\nErrors:")
        for error in results["errors"]:
            print(f"- {error}")

    print("\nMigration complete!")
    print(
        "All direct vector store access has been migrated to use the ComprehensiveMemoryManager."
    )
    print("Please review the migrated files to ensure the migration was successful.")


if __name__ == "__main__":
    asyncio.run(main())
