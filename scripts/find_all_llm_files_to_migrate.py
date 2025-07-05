#!/usr/bin/env python3
"""
Find all files that need UnifiedLLMService migration
"""

import os
import re
from pathlib import Path

# Patterns to search for
SEARCH_PATTERNS = [
    r"SmartAIService",
    r"PortkeyGateway",
    r"SimplifiedPortkeyService",
    r"EnhancedPortkeyOrchestrator",
    r"smart_ai_service",
    r"portkey_gateway",
    r"portkey_service",
]

# Directories to search
SEARCH_DIRS = [
    "backend",
    "scripts",
    "docs",
    "mcp-servers",
]

# Files to exclude
EXCLUDE_PATTERNS = [
    "test_",
    "_test.py",
    "archived",
    "backup",
    "unified_llm_service.py",
    "migrate_to_unified_llm.py",
    "find_all_llm_files_to_migrate.py",
    "cleanup_stale_llm_files.py",
    "__pycache__",
    ".pyc",
]


def should_exclude_file(file_path: str) -> bool:
    """Check if file should be excluded"""
    return any(pattern in file_path for pattern in EXCLUDE_PATTERNS)


def search_file(file_path: Path) -> list[str]:
    """Search a file for patterns"""
    matches = []
    try:
        content = file_path.read_text()
        for pattern in SEARCH_PATTERNS:
            if re.search(pattern, content):
                matches.append(pattern)
    except Exception:
        pass
    return matches


def find_files_to_migrate() -> list[str]:
    """Find all files that need migration"""
    files_to_migrate = []

    for search_dir in SEARCH_DIRS:
        if not Path(search_dir).exists():
            continue

        for root, dirs, files in os.walk(search_dir):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith(".")]

            for file in files:
                # Only process Python and Markdown files
                if not (file.endswith(".py") or file.endswith(".md")):
                    continue

                file_path = Path(root) / file

                # Skip excluded files
                if should_exclude_file(str(file_path)):
                    continue

                # Search for patterns
                matches = search_file(file_path)
                if matches:
                    files_to_migrate.append(str(file_path))

    return sorted(set(files_to_migrate))


def main():
    files = find_files_to_migrate()

    for file in files:
        pass

    # Save to file
    with open("files_to_migrate.txt", "w") as f:
        for file in files:
            f.write(f"{file}\n")


if __name__ == "__main__":
    main()
