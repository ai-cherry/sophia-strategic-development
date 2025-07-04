#!/usr/bin/env python3
"""
Cleanup obsolete files from backend/app/archive/
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Files to delete with reasons
OBSOLETE_FILES = {
    "backend/app/archive/fastapi_app.py": "Fragment file, not a complete application",
    "backend/app/archive/main.py": "Superseded by backend/app/app.py - same functionality",
    "backend/app/archive/enhanced_minimal_app.py": "Superseded by backend/app/app.py - mock implementation",
    "backend/app/archive/unified_fastapi_app.py": "Superseded by backend/app/app.py - overly complex version",
}


def cleanup_obsolete_files():
    """Remove obsolete files from archive"""
    print("🧹 Cleaning up obsolete archived files...\n")

    deleted_count = 0
    for file_path, reason in OBSOLETE_FILES.items():
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"✅ Deleted: {file_path}")
                print(f"   Reason: {reason}\n")
                deleted_count += 1
            except Exception as e:
                print(f"❌ Error deleting {file_path}: {e}\n")
        else:
            print(f"⚠️  File not found: {file_path}\n")

    # Check if archive directory is empty and remove it
    archive_dir = "backend/app/archive"
    if os.path.exists(archive_dir) and not os.listdir(archive_dir):
        try:
            os.rmdir(archive_dir)
            print(f"✅ Removed empty directory: {archive_dir}")
        except Exception as e:
            print(f"❌ Error removing directory {archive_dir}: {e}")

    print(f"\n📊 Summary: Deleted {deleted_count} obsolete files")

    # Suggest next steps
    print("\n📋 Next Steps:")
    print("1. Review docs/archive/ for obsolete documentation")
    print("2. Run dependency audit: pip-audit")
    print("3. Check for unused imports: vulture backend/")


if __name__ == "__main__":
    cleanup_obsolete_files()
