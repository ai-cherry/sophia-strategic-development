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
    print("🔧 Consolidating backend structure...\n")

    # Create archive directory
    archive_dir = "backend/archive/legacy"
    os.makedirs(archive_dir, exist_ok=True)

    moved_count = 0
    archived_count = 0

    # Archive unnecessary directories
    print("📦 Archiving legacy directories...")
    for dir_path in ARCHIVE_DIRECTORIES:
        if os.path.exists(dir_path):
            dst = os.path.join(archive_dir, os.path.basename(dir_path))
            try:
                shutil.move(dir_path, dst)
                print(f"   Archived: {dir_path} → {archive_dir}/")
                archived_count += 1
            except Exception as e:
                print(f"   ❌ Error archiving {dir_path}: {e}")

    # Move and consolidate directories
    print("\n🚚 Moving directories to new structure...")
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
                        print(f"   ⚠️  Conflict: {dst_item} already exists, skipping")
                        continue

                    shutil.move(src_item, dst_item)

                # Remove empty source directory
                os.rmdir(src)
                print(f"   ✅ Moved: {src} → {dst}")
                moved_count += 1
            except Exception as e:
                print(f"   ❌ Error moving {src}: {e}")

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
            print("   ✅ Moved: backend/monitoring → backend/core/monitoring")
            moved_count += 1
        except Exception as e:
            print(f"   ❌ Error moving monitoring: {e}")

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
            print("   ✅ Moved: backend/prompts → backend/services/prompts")
            moved_count += 1
        except Exception as e:
            print(f"   ❌ Error moving prompts: {e}")

    # Clean up empty directories
    print("\n🧹 Cleaning up empty directories...")
    cleanup_empty_dirs("backend")

    # Report results
    print("\n📊 Summary:")
    print(f"   Moved: {moved_count} directories")
    print(f"   Archived: {archived_count} directories")

    # Show new structure
    print("\n📁 New backend structure:")
    show_directory_structure("backend", max_depth=2)

    # Update imports
    print("\n⚠️  Next steps:")
    print("1. Run: python scripts/update_backend_imports.py")
    print("2. Run tests to ensure nothing broke")
    print("3. Update backend/__init__.py with new structure")


def cleanup_empty_dirs(path):
    """Remove empty directories recursively"""
    for root, dirs, files in os.walk(path, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            try:
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    print(f"   🗑️  Removed empty: {dir_path}")
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
        if os.path.isdir(item_path):
            print(f"{prefix}├── {item}/")
            if current_depth < max_depth - 1:
                show_directory_structure(
                    item_path, max_depth, current_depth + 1, prefix + "│   "
                )


if __name__ == "__main__":
    # Confirm before proceeding
    print("⚠️  This will restructure the entire backend directory!")
    print("   Make sure you have a backup or git commit.")
    response = input("\nProceed? (yes/no): ")

    if response.lower() == "yes":
        consolidate_backend()
    else:
        print("❌ Aborted")
