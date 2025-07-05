#!/usr/bin/env python3

import os


def fix_future_imports(file_path):
    """Fix misplaced 'from __future__ import annotations' in a Python file"""
    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()

        # Find the future import
        future_import_line = None
        future_import_index = -1

        for i, line in enumerate(lines):
            if line.strip() == "from __future__ import annotations":
                future_import_line = line
                future_import_index = i
                break

        if future_import_index == -1:
            return False  # No future import found

        # Check if it's already in the right place
        if future_import_index == 0:
            return False  # Already at the beginning

        if future_import_index == 1 and lines[0].startswith("#!"):
            return False  # Already correct after shebang

        # Remove the misplaced import
        lines.pop(future_import_index)

        # Insert at the correct position
        if lines[0].startswith("#!"):
            # Insert after shebang
            lines.insert(1, future_import_line)
        else:
            # Insert at the very beginning
            lines.insert(0, future_import_line)

        # Write back to file
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        return True

    except Exception:
        return False


def main():
    # Files that need fixing based on the find command
    files_to_fix = [
        "backend/api/llm_strategy_routes.py",
        "backend/services/smart_ai_service.py",
    ]

    fixed_count = 0
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            if fix_future_imports(file_path):
                fixed_count += 1
        else:
            pass


if __name__ == "__main__":
    main()
