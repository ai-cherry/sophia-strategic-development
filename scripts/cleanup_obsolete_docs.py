#!/usr/bin/env python3
"""
Cleanup Obsolete Documentation
Identifies and removes outdated documentation files
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

# Define obsolete documentation patterns
OBSOLETE_DOCS = {
    # Migration documents that are completed
    "*MCP_V2_MIGRATION*",
    "*AIRBYTE_V2*",
    "*_MIGRATION_STATUS*",
    "*_MIGRATION_GUIDE*",
    # Old implementation plans
    "*_V2_IMPLEMENTATION*",
    "*_LEGACY_*",
    "*_OLD_*",
    "*_DEPRECATED_*",
    # Completed deployment plans
    "*_DEPLOYMENT_COMPLETE*",
    "*_SUCCESS_REPORT*",
    "*_COMPLETED_*",
    # Temporary documentation
    "*_TEMP_*",
    "*_WIP_*",
    "*_DRAFT_*",
}

# Define directories to check
DOCS_DIRECTORIES = [
    "docs/implementation",
    "docs/deployment",
    "docs/migration",
    "docs/archive",
]


def find_obsolete_docs(base_dir: Path = Path(".")) -> list[Path]:
    """Find all obsolete documentation files"""
    obsolete_files = []

    for docs_dir in DOCS_DIRECTORIES:
        dir_path = base_dir / docs_dir
        if not dir_path.exists():
            continue

        for pattern in OBSOLETE_DOCS:
            for file_path in dir_path.rglob(pattern):
                if file_path.is_file():
                    obsolete_files.append(file_path)

    # Also check root directory for obsolete docs
    for pattern in OBSOLETE_DOCS:
        for file_path in base_dir.glob(pattern):
            if file_path.is_file() and file_path.suffix == ".md":
                obsolete_files.append(file_path)

    # Remove duplicates
    obsolete_files = list(set(obsolete_files))

    return sorted(obsolete_files)


def archive_obsolete_docs(files: list[Path], base_dir: Path = Path(".")):
    """Archive obsolete documentation files"""

    if not files:
        print("✨ No obsolete documentation found!")
        return

    # Create archive directory
    archive_dir = (
        base_dir
        / "docs"
        / "archive"
        / f"obsolete_docs_{datetime.now().strftime('%Y%m%d')}"
    )
    archive_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n📦 Archiving {len(files)} obsolete documentation files...")

    archived_count = 0
    for file_path in files:
        try:
            # Create relative path in archive
            rel_path = file_path.relative_to(base_dir)
            archive_path = archive_dir / rel_path
            archive_path.parent.mkdir(parents=True, exist_ok=True)

            # Move file to archive
            shutil.move(str(file_path), str(archive_path))
            print(f"📄 Archived: {rel_path}")
            archived_count += 1

        except Exception as e:
            print(f"❌ Error archiving {file_path}: {e}")

    # Generate archive report
    report_path = archive_dir / "ARCHIVE_REPORT.md"
    with open(report_path, "w") as f:
        f.write("# Obsolete Documentation Archive Report\n\n")
        f.write(f"Archived on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Summary\n")
        f.write(f"- Total files archived: {archived_count}\n")
        f.write(f"- Archive location: {archive_dir}\n\n")
        f.write("## Archived Files\n\n")

        for file_path in files:
            rel_path = file_path.relative_to(base_dir)
            f.write(f"- {rel_path}\n")

    print(f"\n✅ Archived {archived_count} files to: {archive_dir}")
    print(f"📄 Archive report: {report_path}")


def clean_empty_directories(base_dir: Path = Path(".")):
    """Remove empty directories"""
    print("\n🧹 Cleaning up empty directories...")

    empty_dirs = []
    for root, dirs, files in os.walk(base_dir, topdown=False):
        root_path = Path(root)

        # Skip certain directories
        if any(
            skip in str(root_path)
            for skip in [".git", "node_modules", "__pycache__", ".venv"]
        ):
            continue

        # Check if directory is empty
        if not files and not dirs:
            empty_dirs.append(root_path)

    # Remove empty directories
    for empty_dir in empty_dirs:
        try:
            empty_dir.rmdir()
            print(f"🗑️  Removed empty directory: {empty_dir}")
        except:
            pass


def main():
    """Main cleanup function"""
    print("🔍 Searching for obsolete documentation...")

    # Find obsolete docs
    obsolete_files = find_obsolete_docs()

    if obsolete_files:
        print(f"\n📊 Found {len(obsolete_files)} obsolete documentation files:")
        for file_path in obsolete_files[:10]:  # Show first 10
            print(f"  - {file_path}")
        if len(obsolete_files) > 10:
            print(f"  ... and {len(obsolete_files) - 10} more")

        # Archive them
        archive_obsolete_docs(obsolete_files)

    # Clean up empty directories
    clean_empty_directories()

    print("\n✅ Documentation cleanup complete!")


if __name__ == "__main__":
    main()
