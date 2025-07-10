#!/usr/bin/env python3
"""
Pre-commit hook to check for one-time scripts that should be marked for deletion
"""

import re
import sys
from pathlib import Path

# Patterns that indicate a one-time script
ONE_TIME_PATTERNS = [
    r"fix_.*\.py$",
    r"migrate_.*\.py$",
    r"cleanup_.*\.py$",
    r"deploy_.*\.py$",
    r"consolidate_.*\.py$",
    r"remove_.*\.py$",
    r"execute_.*\.py$",
    r"create_pull_request\.py$",
    r"phase\d+_.*\.py$",
    r".*_one_time.*\.py$",
    r".*_temporary.*\.py$",
    r".*_temp.*\.py$",
]

# Required deletion markers
DELETION_MARKERS = [
    "🚨 ONE-TIME SCRIPT",
    "DELETE AFTER USE",
    "This script can now be deleted",
    "CLEANUP REQUIRED:",
    "CLEANUP REMINDER:",
    "PENDING_DELETION",
]

# Scripts that are exceptions (utility scripts that are reusable)
EXCEPTIONS = [
    "scripts/utils/",
    "scripts/monitoring/",
    "scripts/start_",
    "scripts/test_",
    "scripts/validate_",
    "scripts/check_",
    "scripts/security/",
]


def is_one_time_script(filepath: str) -> bool:
    """Check if a file path matches one-time script patterns"""
    path = Path(filepath)

    # Check exceptions first
    for exception in EXCEPTIONS:
        if exception in str(path):
            return False

    # Check if it matches one-time patterns
    for pattern in ONE_TIME_PATTERNS:
        if re.search(pattern, path.name):
            return True

    return False


def has_deletion_marker(filepath: str) -> bool:
    """Check if file contains a deletion marker"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Check first 1000 characters for efficiency
        header = content[:1000]

        for marker in DELETION_MARKERS:
            if marker in header:
                return True

        return False
    except Exception:
        # If we can't read the file, assume it doesn't have a marker
        return False


def main():
    """Main function to check files passed as arguments"""
    files_to_check = sys.argv[1:]
    issues_found = []

    for filepath in files_to_check:
        if is_one_time_script(filepath) and not has_deletion_marker(filepath):
            issues_found.append(filepath)

    if issues_found:
        print("❌ Found one-time scripts without deletion markers:")
        for file in issues_found:
            print(f"  - {file}")
        print("\nPlease add one of these markers to the file header:")
        print("  - 🚨 ONE-TIME SCRIPT - DELETE AFTER USE")
        print(
            "  - # CLEANUP REQUIRED: This file should be deleted after successful execution"
        )
        print("  - # CLEANUP REMINDER: This script can now be deleted")
        print("\nExample header:")
        print('"""')
        print("🚨 ONE-TIME SCRIPT - DELETE AFTER USE")
        print("Purpose: [specific purpose]")
        print("Created: [date]")
        print('"""')
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
