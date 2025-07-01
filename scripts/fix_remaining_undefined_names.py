#!/usr/bin/env python3
"""
Fix Remaining Undefined Names Script
Comprehensive fix for all undefined name issues in Sophia AI codebase
"""

import subprocess
from pathlib import Path


def get_undefined_names() -> dict[str, list[str]]:
    """Get all undefined names and the files they appear in"""
    try:
        result = subprocess.run(
            ["ruff", "check", ".", "--select=F821"],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
        )

        undefined_names = {}

        for line in result.stdout.split("\n"):
            if "F821" in line and "Undefined name" in line:
                # Extract file path and undefined name
                parts = line.split(":")
                if len(parts) >= 4:
                    file_path = parts[0]
                    # Extract the undefined name from the message
                    if "`" in line:
                        name = line.split("`")[1]
                        if name not in undefined_names:
                            undefined_names[name] = []
                        if file_path not in undefined_names[name]:
                            undefined_names[name].append(file_path)

        return undefined_names

    except Exception as e:
        print(f"Error getting undefined names: {e}")
        return {}


def fix_utc_imports(files: list[str]) -> int:
    """Fix missing UTC imports from datetime"""
    fixed_count = 0

    for file_path in files:
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Check if UTC is used but not imported
            if "UTC" not in content:
                continue

            # Check if already imported
            if "from datetime import" in content and "UTC" in content:
                continue

            lines = content.split("\n")

            # Find existing datetime import and add UTC
            datetime_import_found = False
            for i, line in enumerate(lines):
                if "from datetime import" in line and "UTC" not in line:
                    # Add UTC to existing import
                    if line.strip().endswith(","):
                        lines[i] = line.rstrip() + " UTC"
                    else:
                        lines[i] = line.rstrip() + ", UTC"
                    datetime_import_found = True
                    break
                elif "import datetime" in line and "from datetime" not in line:
                    # Replace with from datetime import
                    lines[i] = "from datetime import datetime, UTC"
                    datetime_import_found = True
                    break

            # If no datetime import found, add it
            if not datetime_import_found:
                # Find the best place to add the import
                import_idx = 0
                for i, line in enumerate(lines):
                    if line.strip().startswith(("import ", "from ")):
                        import_idx = i + 1
                    elif line.strip() and not line.strip().startswith("#"):
                        break

                lines.insert(import_idx, "from datetime import datetime, UTC")

            # Write back the file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))

            print(f"✅ Fixed UTC import in {file_path}")
            fixed_count += 1

        except Exception as e:
            print(f"❌ Error fixing UTC in {file_path}: {e}")

    return fixed_count


def fix_logger_imports(files: list[str]) -> int:
    """Fix missing logger imports"""
    fixed_count = 0

    for file_path in files:
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Check if logger is used but not defined
            if "logger" not in content:
                continue

            # Check if already imported or defined
            if "import logging" in content or "logger = " in content:
                continue

            lines = content.split("\n")

            # Add logging import and logger setup
            import_idx = 0
            for i, line in enumerate(lines):
                if line.strip().startswith(("import ", "from ")):
                    import_idx = i + 1
                elif line.strip() and not line.strip().startswith("#"):
                    break

            # Add logging import
            lines.insert(import_idx, "import logging")
            lines.insert(import_idx + 1, "")
            lines.insert(import_idx + 2, "logger = logging.getLogger(__name__)")
            lines.insert(import_idx + 3, "")

            # Write back the file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))

            print(f"✅ Fixed logger import in {file_path}")
            fixed_count += 1

        except Exception as e:
            print(f"❌ Error fixing logger in {file_path}: {e}")

    return fixed_count


def fix_common_imports(name: str, files: list[str]) -> int:
    """Fix common missing imports based on the undefined name"""
    fixed_count = 0

    # Define common import mappings
    import_mappings = {
        "asyncio": "import asyncio",
        "json": "import json",
        "os": "import os",
        "sys": "import sys",
        "Path": "from pathlib import Path",
        "Optional": "from typing import Optional",
        "List": "from typing import List",
        "Dict": "from typing import Dict",
        "Any": "from typing import Any",
        "Union": "from typing import Union",
        "Tuple": "from typing import Tuple",
        "requests": "import requests",
        "time": "import time",
        "uuid": "import uuid",
        "subprocess": "import subprocess",
        "shlex": "import shlex",
        "HTTPException": "from fastapi import HTTPException",
        "Request": "from fastapi import Request",
        "Response": "from fastapi import Response",
    }

    if name not in import_mappings:
        return 0

    import_line = import_mappings[name]

    for file_path in files:
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Check if name is used but not imported
            if name not in content:
                continue

            # Check if already imported
            if import_line in content:
                continue

            lines = content.split("\n")

            # Find the best place to add the import
            import_idx = 0
            for i, line in enumerate(lines):
                if line.strip().startswith(("import ", "from ")):
                    import_idx = i + 1
                elif line.strip() and not line.strip().startswith("#"):
                    break

            lines.insert(import_idx, import_line)

            # Write back the file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))

            print(f"✅ Fixed {name} import in {file_path}")
            fixed_count += 1

        except Exception as e:
            print(f"❌ Error fixing {name} in {file_path}: {e}")

    return fixed_count


def main():
    """Main function to fix all remaining undefined names"""
    print("🔧 Fixing Remaining Undefined Names in Sophia AI")
    print("=" * 60)

    # Get all undefined names
    print("🔍 Analyzing undefined names...")
    undefined_names = get_undefined_names()

    if not undefined_names:
        print("✅ No undefined names found!")
        return

    print(f"Found {len(undefined_names)} different undefined names")

    total_fixed = 0

    # Fix UTC imports specifically
    if "UTC" in undefined_names:
        print(f"\n📅 Fixing UTC imports in {len(undefined_names['UTC'])} files...")
        fixed = fix_utc_imports(undefined_names["UTC"])
        total_fixed += fixed
        print(f"✅ Fixed UTC in {fixed} files")

    # Fix logger imports specifically
    if "logger" in undefined_names:
        print(
            f"\n📝 Fixing logger imports in {len(undefined_names['logger'])} files..."
        )
        fixed = fix_logger_imports(undefined_names["logger"])
        total_fixed += fixed
        print(f"✅ Fixed logger in {fixed} files")

    # Fix other common imports
    for name, files in undefined_names.items():
        if name in ["UTC", "logger"]:
            continue  # Already handled

        print(f"\n🔧 Fixing {name} imports in {len(files)} files...")
        fixed = fix_common_imports(name, files)
        total_fixed += fixed
        if fixed > 0:
            print(f"✅ Fixed {name} in {fixed} files")
        else:
            print(f"⚠️  No automatic fix available for '{name}' - manual review needed")

    # Run final check
    print(f"\n🎯 Total imports fixed: {total_fixed}")
    print("\n3️⃣ Running final validation...")
    result = subprocess.run(
        ["ruff", "check", ".", "--select=F821", "--statistics"],
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )

    print("Final undefined names status:")
    print(result.stdout)

    print("\n✅ Undefined names fix complete!")


if __name__ == "__main__":
    main()
