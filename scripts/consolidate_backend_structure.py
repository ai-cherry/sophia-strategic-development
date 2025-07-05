#!/usr/bin/env python3
"""
Consolidate backend structure from 26 directories to 5 core modules
"""

import os
import shutil

# Directory mappings - from current to new structure
DIRECTORY_MAPPINGS = {
    # API layer consolidation
    "backend/presentation": "backend/api/routes",
    "backend/application": "backend/api/handlers",
    # Services consolidation
    "backend/domain": "backend/services/domain",
    "backend/agents": "backend/services/agents",
    "backend/workflows": "backend/services/workflows",
    "backend/orchestration": "backend/services/orchestration",
    # Integrations consolidation
    "backend/mcp_servers": "backend/integrations/mcp_servers",
    # Core consolidation
    "backend/utils": "backend/core/utils",
    "backend/security": "backend/core/security",
    "backend/models": "backend/core/models",
    "backend/infrastructure": "backend/core/infrastructure",
    # Database consolidation
    "backend/snowflake_setup": "backend/database/snowflake_setup",
    "backend/etl": "backend/database/etl",
}

# Directories to archive (not needed in new structure)
ARCHIVE_DIRECTORIES = [
    "backend/rag",
    "backend/n8n_bridge",
    "backend/websocket",
    "backend/prompts",  # Move to services
    "backend/monitoring",  # Move to core
]


def consolidate_backend():
    """Consolidate backend directories"""

    # Create archive directory
    archive_dir = "backend/archive/legacy"
    os.makedirs(archive_dir, exist_ok=True)

    moved_count = 0
    archived_count = 0

    # Archive unnecessary directories
    for dir_path in ARCHIVE_DIRECTORIES:
        if os.path.exists(dir_path):
            dst = os.path.join(archive_dir, os.path.basename(dir_path))
            try:
                shutil.move(dir_path, dst)
                archived_count += 1
            except Exception:
                pass

    # Move and consolidate directories
    for src, dst in DIRECTORY_MAPPINGS.items():
        if os.path.exists(src):
            # Create destination directory
            os.makedirs(dst, exist_ok=True)

            # Move contents, not the directory itself
            try:
                for item in os.listdir(src):
                    src_item = os.path.join(src, item)
                    dst_item = os.path.join(dst, item)

                    # Skip __pycache__
                    if item == "__pycache__":
                        continue

                    # Handle conflicts
                    if os.path.exists(dst_item):
                        continue

                    shutil.move(src_item, dst_item)

                # Remove empty source directory
                os.rmdir(src)
                moved_count += 1
            except Exception:
                pass

    # Special handling for monitoring (move to core)
    if os.path.exists("backend/monitoring"):
        dst = "backend/core/monitoring"
        os.makedirs(dst, exist_ok=True)
        try:
            for item in os.listdir("backend/monitoring"):
                if item != "__pycache__":
                    shutil.move(
                        os.path.join("backend/monitoring", item),
                        os.path.join(dst, item),
                    )
            os.rmdir("backend/monitoring")
            moved_count += 1
        except Exception:
            pass

    # Special handling for prompts (move to services)
    if os.path.exists("backend/prompts"):
        dst = "backend/services/prompts"
        os.makedirs(dst, exist_ok=True)
        try:
            for item in os.listdir("backend/prompts"):
                if item != "__pycache__":
                    shutil.move(
                        os.path.join("backend/prompts", item), os.path.join(dst, item)
                    )
            os.rmdir("backend/prompts")
            moved_count += 1
        except Exception:
            pass

    # Clean up empty directories
    cleanup_empty_dirs("backend")

    # Report results

    # Show new structure
    show_directory_structure("backend", max_depth=2)

    # Update imports


def cleanup_empty_dirs(path):
    """Remove empty directories recursively"""
    for root, dirs, _files in os.walk(path, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            try:
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
            except:
                pass


def show_directory_structure(path, max_depth=2, current_depth=0, prefix=""):
    """Display directory structure"""
    if current_depth >= max_depth:
        return

    items = sorted(os.listdir(path))
    for item in items:
        if item.startswith(".") or item == "__pycache__":
            continue

        item_path = os.path.join(path, item)
        if os.path.isdir(item_path) and current_depth < max_depth - 1:
            show_directory_structure(
                item_path, max_depth, current_depth + 1, prefix + "│   "
            )


if __name__ == "__main__":
    # Confirm before proceeding
    response = input("\nProceed? (yes/no): ")

    if response.lower() == "yes":
        consolidate_backend()
    else:
        pass
