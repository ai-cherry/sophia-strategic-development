#!/usr/bin/env python3
"""
Fix specific syntax patterns found in the error report.
Targets the exact patterns causing syntax errors.
"""

import re
from pathlib import Path


def fix_syntax_patterns(file_path: Path) -> tuple[bool, list[str]]:
    """Fix specific syntax patterns in a file."""
    fixes = []

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Pattern 1: Fix "try:." -> "try:"
        content = re.sub(r"(\btry):\.\s*$", r"\1:", content, flags=re.MULTILINE)

        # Pattern 2: Fix "def method():." -> "def method():"
        content = re.sub(
            r"(def\s+\w+\([^)]*\)):\.\s*$", r"\1:", content, flags=re.MULTILINE
        )

        # Pattern 3: Fix docstrings that are on same line as function def
        # "def __init__(self):."""Initialize..." -> "def __init__(self):\n    """Initialize..."
        content = re.sub(
            r'(def\s+\w+\([^)]*\)):\.?"*([^"\n]+)"*',
            lambda m: f'{m.group(1)}:\n    """{m.group(2).strip()}"""',
            content,
            flags=re.MULTILINE,
        )

        # Pattern 4: Fix statements ending with period
        lines = content.split("\n")
        fixed_lines = []

        for i, line in enumerate(lines):
            original_line = line

            # Skip empty lines and comments
            if not line.strip() or line.strip().startswith("#"):
                fixed_lines.append(line)
                continue

            # Fix common endings with periods
            # Pattern: statement.
            if line.strip().endswith(".") and not line.strip().endswith("..."):
                # Check if it's not inside a string
                if not ('"' in line or "'" in line):
                    line = line.rstrip().rstrip(".")
                    fixes.append(f"Line {i + 1}: Removed trailing period")
                # Handle specific cases
                elif re.match(r".*\)\.\s*$", line):
                    line = re.sub(r"\)\.\s*$", ")", line)
                    fixes.append(f"Line {i + 1}: Fixed method call period")
                elif re.match(r".*\]\.\s*$", line):
                    line = re.sub(r"\]\.\s*$", "]", line)
                    fixes.append(f"Line {i + 1}: Fixed list/array period")

            # Fix specific patterns with periods
            # if condition:.
            line = re.sub(
                r"^(\s*)(if|elif|else|try|except|finally|while|for|with|def|class)\s+(.*):\.\s*$",
                r"\1\2 \3:",
                line,
            )

            # Fix variable assignments ending with period
            line = re.sub(r"^(\s*\w+\s*=\s*[^.]+)\.\s*$", r"\1", line)

            # Fix return statements ending with period
            line = re.sub(r"^(\s*return\s+[^.]+)\.\s*$", r"\1", line)

            # Fix docstring + code on same line
            if '"""' in line and not line.strip().startswith('"""'):
                # Split docstring to new line
                match = re.match(r'^(\s*)(.*?)"""(.*)"""(.*)$', line)
                if match:
                    indent = match.group(1)
                    prefix = match.group(2)
                    docstring_content = match.group(3)
                    suffix = match.group(4)
                    if prefix:
                        fixed_lines.append(f"{indent}{prefix}")
                        fixed_lines.append(f'{indent}    """{docstring_content}"""')
                        if suffix:
                            fixed_lines.append(f"{indent}{suffix}")
                        continue

            if line != original_line:
                fixes.append(f"Line {i + 1}: Fixed syntax")

            fixed_lines.append(line)

        content = "\n".join(fixed_lines)

        # Pattern 5: Fix list/array definitions ending with period
        content = re.sub(r"(\[)\.\s*$", r"\1", content, flags=re.MULTILINE)
        content = re.sub(r"(\{)\.\s*$", r"\1", content, flags=re.MULTILINE)

        # Pattern 6: Fix missing newline between docstring and next statement
        content = re.sub(r'"""([^"]+)"""([a-zA-Z])', r'"""\1"""\n\2', content)

        # Pattern 7: Fix specific problematic patterns
        # Fix: def __init__(self):."Initialize -> def __init__(self):\n    """Initialize
        content = re.sub(
            r'def\s+__init__\s*\([^)]*\)\s*:\s*\.\s*"([^"]+)',
            r'def __init__(self):\n    """\1',
            content,
        )

        # Pattern 8: Fix try:. patterns
        content = re.sub(r"try:\.\s*\n", "try:\n", content)

        # Pattern 9: Fix if statements with periods
        content = re.sub(r"if\s+([^:]+):\.\s*\n", r"if \1:\n", content)

        if content != original_content:
            # Write the fixed content
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True, fixes if fixes else ["Applied syntax fixes"]

        return False, []

    except Exception as e:
        return False, [f"Error: {str(e)}"]


def main():
    """Main function to fix specific syntax patterns."""
    print("🔧 Fixing Specific Syntax Patterns")
    print("=" * 60)

    # Get all Python files with syntax errors from the report
    import json

    try:
        with open("syntax_validation_report.json") as f:
            report = json.load(f)

        errors = report.get("errors", {})
        fixed_count = 0

        for file_path_str, error_msg in errors.items():
            # Skip node_modules
            if "node_modules" in file_path_str:
                continue

            file_path = Path(file_path_str)

            if file_path.exists():
                print(f"\n📄 Processing {file_path}...")
                fixed, fixes = fix_syntax_patterns(file_path)

                if fixed:
                    fixed_count += 1
                    print(f"✅ Fixed {file_path}")
                    for fix in fixes:
                        print(f"   - {fix}")
                else:
                    if fixes:  # Error occurred
                        print(f"❌ Error in {file_path}: {fixes[0]}")

        print(f"\n📊 Summary: Fixed {fixed_count} files")
        print("\n💡 Run syntax validation again to check for remaining issues")

    except Exception as e:
        print(f"❌ Error loading syntax report: {e}")


if __name__ == "__main__":
    main()
