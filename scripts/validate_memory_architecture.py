#!/usr/bin/env python3
"""
Validate Memory Architecture Compliance
Ensures no forbidden vector databases are used
"""

import sys
import re
from pathlib import Path

# Forbidden imports that violate our memory architecture
FORBIDDEN_IMPORTS = ["pinecone", "weaviate", "chromadb", "qdrant", "milvus", "faiss"]

# Allowed exceptions (Qdrant is only allowed internally within Mem0)
ALLOWED_EXCEPTIONS = {"qdrant": ["mem0/", ".venv/", "site-packages/"]}


def check_file_for_forbidden_imports(file_path: Path) -> list[str]:
    """Check a single file for forbidden imports"""
    violations = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for various import patterns
        for forbidden in FORBIDDEN_IMPORTS:
            patterns = [
                f"import {forbidden}",
                f"from {forbidden}",
                f"{forbidden}\\.",
                f"{forbidden}\\(",
                f'"{forbidden}"',
                f"'{forbidden}'",
            ]

            for pattern in patterns:
                if re.search(pattern, content):
                    # Check if it's an allowed exception
                    is_exception = False
                    if forbidden in ALLOWED_EXCEPTIONS:
                        for allowed_path in ALLOWED_EXCEPTIONS[forbidden]:
                            if allowed_path in str(file_path):
                                is_exception = True
                                break

                    if not is_exception:
                        violations.append(
                            f"{file_path}: Found forbidden import '{forbidden}'"
                        )
                        break

    except Exception as e:
        print(f"Error reading {file_path}: {e}")

    return violations


def scan_directory(root_dir: Path) -> list[str]:
    """Scan directory tree for violations"""
    violations = []

    # Directories to skip
    skip_dirs = {".git", ".venv", "__pycache__", "node_modules", "archive", "external"}

    for path in root_dir.rglob("*"):
        # Skip directories
        if path.is_dir():
            continue

        # Skip non-Python files
        if path.suffix not in [".py", ".yaml", ".yml", ".json"]:
            continue

        # Skip if in skip directory
        if any(skip_dir in path.parts for skip_dir in skip_dirs):
            continue

        # Skip the validation script itself
        if path.name == "validate_memory_architecture.py":
            continue

        # Check file
        file_violations = check_file_for_forbidden_imports(path)
        violations.extend(file_violations)

    return violations


def check_config_files() -> list[str]:
    """Check configuration files for problematic settings"""
    violations = []

    # Check unified MCP configuration
    mcp_config_path = Path("config/unified_mcp_configuration.yaml")
    if mcp_config_path.exists():
        with open(mcp_config_path, "r") as f:
            content = f.read()
            if "pinecone_enabled: true" in content:
                violations.append(f"{mcp_config_path}: pinecone_enabled is set to true")

    # Check other config files
    config_patterns = {
        "pinecone_api_key": "Pinecone API key configured",
        "weaviate_url": "Weaviate URL configured",
        "chromadb_host": "ChromaDB host configured",
    }

    for config_file in Path("config").glob("*.yaml"):
        with open(config_file, "r") as f:
            content = f.read().lower()
            for pattern, message in config_patterns.items():
                if pattern in content:
                    violations.append(f"{config_file}: {message}")

    return violations


def main():
    """Main validation function"""
    print("🔍 Validating Memory Architecture Compliance...")
    print("=" * 60)

    # Get project root
    project_root = Path(__file__).parent.parent

    # Run checks
    import_violations = scan_directory(project_root)
    config_violations = check_config_files()

    all_violations = import_violations + config_violations

    if all_violations:
        print("❌ VALIDATION FAILED - Forbidden dependencies detected:")
        print()
        for violation in all_violations:
            print(f"  - {violation}")
        print()
        print(f"Total violations: {len(all_violations)}")
        print()
        print("To fix:")
        print("1. Remove/replace forbidden imports with UnifiedMemoryService")
        print("2. Update configuration files to disable forbidden services")
        print(
            "3. Use 'from backend.services.unified_memory_service import get_unified_memory_service'"
        )
        sys.exit(1)
    else:
        print("✅ VALIDATION PASSED - No forbidden dependencies detected!")
        print()
        print("Memory architecture compliance verified:")
        print("  - No Pinecone imports found")
        print("  - No Weaviate imports found")
        print("  - No ChromaDB imports found")
        print("  - Configuration files are clean")
        print()
        print("All memory operations properly use UnifiedMemoryService! 🎉")
        sys.exit(0)


if __name__ == "__main__":
    main()
