#!/usr/bin/env python3
"""
Infrastructure Cleanup Script
Removes legacy and broken infrastructure files to streamline the codebase
"""

import sys
from pathlib import Path

# Define legacy files to remove
LEGACY_FILES_TO_REMOVE = [
    # Broken MCP configurations
    "infrastructure/mcp/broken_server.py",
    "infrastructure/mcp/legacy_config.yaml",
    # Old Pulumi TypeScript files
    "infrastructure/pulumi/*.ts",
    "infrastructure/pulumi/node_modules",
    "infrastructure/pulumi/package*.json",
    # Duplicate ESC environments
    "infrastructure/esc/sophia-ai-staging.yaml",
    "infrastructure/esc/sophia-ai-dev.yaml",
    "infrastructure/esc/sophia-ai-test.yaml",
    # Legacy GitHub workflows
    ".github/workflows/deploy-legacy.yml",
    ".github/workflows/test-all.yml",
    ".github/workflows/manual-deploy.yml",
]

# Define patterns to clean
PATTERNS_TO_CLEAN = [
    "**/*_backup.py",
    "**/*_old.py",
    "**/*.pyc",
    "**/__pycache__",
    "**/.DS_Store",
    "**/node_modules",
    "**/*.log",
]


def remove_files(files: list[str], dry_run: bool = True) -> list[tuple[str, bool]]:
    """Remove specified files and return results"""
    results = []

    for file_pattern in files:
        for file_path in Path(".").glob(file_pattern):
            try:
                if dry_run:
                    print(f"[DRY RUN] Would remove: {file_path}")
                    results.append((str(file_path), True))
                else:
                    if file_path.is_file():
                        file_path.unlink()
                    elif file_path.is_dir():
                        import shutil

                        shutil.rmtree(file_path)
                    print(f"✓ Removed: {file_path}")
                    results.append((str(file_path), True))
            except Exception as e:
                print(f"✗ Failed to remove {file_path}: {e}")
                results.append((str(file_path), False))

    return results


def main():
    """Main cleanup function"""
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv

    print("=== Sophia AI Infrastructure Cleanup ===")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print()

    # Clean legacy files
    print("Cleaning legacy files...")
    legacy_results = remove_files(LEGACY_FILES_TO_REMOVE, dry_run)

    # Clean patterns
    print("\nCleaning file patterns...")
    pattern_results = remove_files(PATTERNS_TO_CLEAN, dry_run)

    # Summary
    total_files = len(legacy_results) + len(pattern_results)
    successful = sum(1 for _, success in legacy_results + pattern_results if success)

    print("\n=== Summary ===")
    print(f"Total files processed: {total_files}")
    print(f"Successfully {'would remove' if dry_run else 'removed'}: {successful}")
    print(f"Failed: {total_files - successful}")

    if dry_run:
        print("\nRun without --dry-run to actually remove files")


if __name__ == "__main__":
    main()
