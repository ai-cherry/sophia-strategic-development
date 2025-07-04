#!/usr/bin/env python3
"""
Find all files that need UnifiedLLMService migration
"""

import os
import re
from pathlib import Path
from typing import List, Set

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
    for pattern in EXCLUDE_PATTERNS:
        if pattern in file_path:
            return True
    return False

def search_file(file_path: Path) -> List[str]:
    """Search a file for patterns"""
    matches = []
    try:
        content = file_path.read_text()
        for pattern in SEARCH_PATTERNS:
            if re.search(pattern, content):
                matches.append(pattern)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return matches

def find_files_to_migrate() -> List[str]:
    """Find all files that need migration"""
    files_to_migrate = []
    
    for search_dir in SEARCH_DIRS:
        if not Path(search_dir).exists():
            continue
            
        for root, dirs, files in os.walk(search_dir):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                # Only process Python and Markdown files
                if not (file.endswith('.py') or file.endswith('.md')):
                    continue
                    
                file_path = Path(root) / file
                
                # Skip excluded files
                if should_exclude_file(str(file_path)):
                    continue
                
                # Search for patterns
                matches = search_file(file_path)
                if matches:
                    files_to_migrate.append(str(file_path))
                    print(f"✓ {file_path}: {', '.join(set(matches))}")
    
    return sorted(set(files_to_migrate))

def main():
    print("Searching for files that need UnifiedLLMService migration...")
    print("=" * 60)
    
    files = find_files_to_migrate()
    
    print("\n" + "=" * 60)
    print(f"Found {len(files)} files that need migration:")
    print("\nPython list format (for migration script):")
    print("FILES_TO_MIGRATE = [")
    for file in files:
        print(f'    "{file}",')
    print("]")
    
    # Save to file
    with open("files_to_migrate.txt", "w") as f:
        for file in files:
            f.write(f"{file}\n")
    
    print(f"\nFile list saved to: files_to_migrate.txt")

if __name__ == "__main__":
    main() 