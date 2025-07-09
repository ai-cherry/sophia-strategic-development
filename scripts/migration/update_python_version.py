#!/usr/bin/env python3
"""Update Python version in all Dockerfiles from 3.11 to 3.12."""

import re
from pathlib import Path


def update_dockerfile_python_version(file_path: Path) -> bool:
    """Update Python version in a Dockerfile."""
    try:
        content = file_path.read_text()
        original_content = content

        # Update FROM python:3.11-slim to FROM python:3.12-slim
        content = re.sub(r"FROM\s+python:3\.11(-slim)?", r"FROM python:3.12\1", content)

        if content != original_content:
            file_path.write_text(content)
            return True
        return False
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False


def main():
    """Update Python version in all Dockerfiles."""
    root = Path.cwd()
    dockerfiles = list(root.rglob("Dockerfile*"))

    updated = 0
    for dockerfile in dockerfiles:
        # Skip external directories
        if "external/" in str(dockerfile):
            continue

        if update_dockerfile_python_version(dockerfile):
            print(f"✅ Updated: {dockerfile}")
            updated += 1

    print(f"\n🎉 Updated {updated} Dockerfiles to Python 3.12")


if __name__ == "__main__":
    main()
