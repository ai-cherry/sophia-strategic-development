#!/usr/bin/env python3
"""
Fix Pydantic V1 validators to V2 field_validators
"""

import re
from pathlib import Path


def fix_pydantic_file(file_path: Path):
    """Fix Pydantic validators in a single file"""
    content = file_path.read_text()
    original = content

    # Remove validator from imports if field_validator is present
    if "field_validator" in content and "validator" in content:
        content = re.sub(
            r"from pydantic import (.*?)field_validator",
            r"from pydantic import \1field_validator",
            content,
        )

    # Replace @validator with @field_validator
    content = re.sub(
        r'@validator\("([^"]+)"\)',
        r'@field_validator("\1", mode="before")\n    @classmethod',
        content,
    )

    # If the method doesn't have cls as first parameter, add it
    content = re.sub(
        r"def validate_(\w+)\(self, v\)", r"def validate_\1(cls, v)", content
    )

    if content != original:
        file_path.write_text(content)
        print(f"Fixed: {file_path}")
        return True
    return False


def main():
    """Fix all Pydantic validators"""
    # Fix the specific file we know about
    models_file = Path("infrastructure/security/ephemeral_credentials/models.py")
    if models_file.exists():
        fix_pydantic_file(models_file)

    # Search for other files with validator decorators
    root = Path.cwd()
    fixed_count = 0

    for py_file in root.rglob("*.py"):
        if any(skip in str(py_file) for skip in [".venv", "__pycache__", "external/"]):
            continue

        try:
            content = py_file.read_text()
            if "@validator(" in content and "pydantic" in content:
                if fix_pydantic_file(py_file):
                    fixed_count += 1
        except Exception as e:
            print(f"Error processing {py_file}: {e}")

    print(f"\nFixed {fixed_count} files with Pydantic validators")


if __name__ == "__main__":
    main()
