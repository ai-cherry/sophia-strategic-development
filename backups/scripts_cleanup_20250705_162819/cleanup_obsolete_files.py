#!/usr/bin/env python3
"""
Cleanup obsolete files from backend/app/archive/
"""

import contextlib
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

    deleted_count = 0
    for file_path, _reason in OBSOLETE_FILES.items():
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                deleted_count += 1
            except Exception:
                pass
        else:
            pass

    # Check if archive directory is empty and remove it
    archive_dir = "backend/app/archive"
    if os.path.exists(archive_dir) and not os.listdir(archive_dir):
        with contextlib.suppress(Exception):
            os.rmdir(archive_dir)

    # Suggest next steps


if __name__ == "__main__":
    cleanup_obsolete_files()
