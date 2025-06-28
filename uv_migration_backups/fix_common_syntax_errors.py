#!/usr/bin/env python3
"""
Fix common syntax errors across the Sophia AI codebase.

Common patterns:
1. Lines ending with periods after statements (e.g., 'try:.' -> 'try:')
2. Lines with multiple periods at the end
3. Misplaced periods in method calls
4. Triple-quote string issues
"""

import json
import re
from pathlib import Path
from typing import List, Tuple

# Load syntax validation report
with open("syntax_validation_report.json", "r") as f:
    report = json.load(f)


def fix_common_syntax_errors(content: str) -> Tuple[str, List[str]]:
    """Fix common syntax errors in Python code."""
    lines = content.split("\n")
    fixes_made = []

    for i, line in enumerate(lines):
        original_line = line

        # Fix 1: Remove periods at the end of statements
        # Pattern: try:. -> try:
        if re.match(
            r"^(\s*)(try|except|finally|def|class|if|elif|else|while|for|with)(.*):\.$",
            line,
        ):
            line = re.sub(r":\.$", ":", line)
            if line != original_line:
                fixes_made.append(f"Line {i + 1}: Removed period after colon")

        # Fix 2: Remove periods at the end of method/function definitions
        # Pattern: def __init__(self):. -> def __init__(self):
        if re.match(r"^(\s*)def\s+\w+\(.*\):\.$", line):
            line = re.sub(r":\.$", ":", line)
            if line != original_line:
                fixes_made.append(
                    f"Line {i + 1}: Removed period after function definition"
                )

        # Fix 3: Remove periods at the end of assignments or statements
        # Pattern: variable = value. -> variable = value
        if (
            not line.strip().startswith("#")
            and line.strip()
            and line.strip().endswith(".")
            and not line.strip().endswith("...")
        ):
            # Check if this is likely a statement (not a string or comment)
            if (
                '"""' not in line
                and "'''" not in line
                and not re.search(r'["\'].*\.$', line)
            ):
                # Check if it's not a valid method call ending with .
                if not re.search(r"\)\.$", line):  # Method calls can end with ).
                    line = line.rstrip(".").rstrip()
                    if line != original_line:
                        fixes_made.append(f"Line {i + 1}: Removed trailing period")

        # Fix 4: Fix method calls with misplaced periods
        # Pattern: method(). -> method()
        if re.search(r"\(\)\.\s*$", line):
            line = re.sub(r"\(\)\.\s*$", "()", line)
            if line != original_line:
                fixes_made.append(
                    f"Line {i + 1}: Fixed method call with trailing period"
                )

        # Fix 5: Fix docstrings that start incorrectly
        # Pattern: def func():."""Doc -> def func():\n    """Doc
        if re.match(r'^(\s*)def\s+\w+\(.*\):\.?"""', line):
            match = re.match(r'^(\s*)(def\s+\w+\(.*\)):\.?(""".*)', line)
            if match:
                indent = match.group(1)
                func_def = match.group(2)
                docstring = match.group(3)
                lines[i] = f"{indent}{func_def}"
                lines.insert(i + 1, f"{indent}    {docstring}")
                fixes_made.append(f"Line {i + 1}: Fixed docstring placement")
                continue

        # Fix 6: Fix return statements with periods
        # Pattern: return value. -> return value
        if re.match(r"^(\s*)return\s+.*\.$", line) and "..." not in line:
            line = line.rstrip(".")
            if line != original_line:
                fixes_made.append(f"Line {i + 1}: Fixed return statement")

        # Fix 7: Fix list/dict definitions with trailing periods
        # Pattern: list = [. -> list = [
        if re.search(r"[\[\{]\.$", line):
            line = re.sub(r"([\[\{])\.$", r"\1", line)
            if line != original_line:
                fixes_made.append(f"Line {i + 1}: Fixed list/dict opening bracket")

        lines[i] = line

    return "\n".join(lines), fixes_made


def process_file(file_path: Path) -> bool:
    """Process a single file to fix syntax errors."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        fixed_content, fixes = fix_common_syntax_errors(content)

        if fixes:
            # Backup original file
            backup_path = file_path.with_suffix(file_path.suffix + ".backup")
            with open(backup_path, "w", encoding="utf-8") as f:
                f.write(content)

            # Write fixed content
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(fixed_content)

            print(f"✅ Fixed {file_path}")
            for fix in fixes:
                print(f"   - {fix}")
            return True

        return False

    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False


def main():
    """Main function to fix syntax errors in all error files."""
    print("🔧 Fixing Common Syntax Errors in Sophia AI Codebase")
    print("=" * 60)

    errors = report.get("errors", {})
    fixed_count = 0

    # Process only files that exist
    for file_path_str, error_msg in errors.items():
        file_path = Path(file_path_str)

        if file_path.exists():
            # Skip node_modules files
            if "node_modules" in str(file_path):
                continue

            # Look for specific error patterns we can fix
            if any(
                pattern in error_msg
                for pattern in [
                    "invalid syntax at line",
                    "expected an indented block",
                    "unexpected indent",
                    ":.",
                    ").",
                    "= [.",
                    "return .",
                ]
            ):
                if process_file(file_path):
                    fixed_count += 1

    print(f"\n📊 Summary: Fixed {fixed_count} files")
    print("\n⚠️  Note: Backup files created with .backup extension")
    print("Run syntax validation again to check remaining issues")


if __name__ == "__main__":
    main()
