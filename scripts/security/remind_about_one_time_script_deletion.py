#!/usr/bin/env python3
"""
Remind about one-time script deletion
"""

from pathlib import Path


def check_for_one_time_scripts():
    """Check for scripts that should be deleted after use"""

    patterns = [
        "**/scripts/**/one_time_*.py",
        "**/scripts/**/temp_*.py",
        "**/scripts/**/setup_*.py",
        "**/scripts/**/migration_*.py",
    ]

    found_scripts = []
    for pattern in patterns:
        found_scripts.extend(Path(".").glob(pattern))

    if found_scripts:
        print("🧹 Reminder: Consider deleting these one-time scripts:")
        for script in found_scripts:
            print(f"  - {script}")
        print("\nRun: git rm <script> if no longer needed")
    else:
        print("✅ No one-time scripts found")


if __name__ == "__main__":
    check_for_one_time_scripts()
