#!/usr/bin/env python3
"""
Prevent dead code patterns in commits
Simple implementation that focuses on obvious issues
"""

import sys
from pathlib import Path


def check_for_dead_code(file_path: Path) -> bool:
    """Check file for common dead code patterns"""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Basic checks for obvious dead code patterns
        lines = content.split("\n")
        issues = []

        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()

            # Check for obvious dead code patterns
            if line_stripped.startswith("# TODO: DELETE"):
                issues.append(f"Line {i}: Marked for deletion")
            elif "DEAD_CODE" in line_stripped:
                issues.append(f"Line {i}: Dead code marker found")
            elif line_stripped.startswith("def UNUSED_"):
                issues.append(f"Line {i}: Unused function detected")

        if issues:
            print(f"Dead code issues found in {file_path}:")
            for issue in issues:
                print(f"  - {issue}")
            return False

        return True

    except Exception as e:
        print(f"Warning: Could not analyze {file_path}: {e}")
        return True  # Allow file if can't parse


def main():
    """Main function for command line usage"""
    if len(sys.argv) < 2:
        print("Usage: python prevent_dead_code_patterns.py <file1> [file2] ...")
        sys.exit(0)

    all_clean = True
    for file_arg in sys.argv[1:]:
        file_path = Path(file_arg)
        if file_path.suffix == ".py" and file_path.exists():
            if not check_for_dead_code(file_path):
                all_clean = False

    if not all_clean:
        print("\n❌ Dead code patterns detected!")
        sys.exit(1)
    else:
        print("✅ No dead code patterns detected")
        sys.exit(0)


if __name__ == "__main__":
    main()
