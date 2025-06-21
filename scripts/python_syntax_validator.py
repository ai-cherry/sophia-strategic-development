#!/usr/bin/env python3
"""Python syntax validator and auto-fixer for the Sophia AI codebase.

This tool provides comprehensive validation and fixing of common Python syntax issues,
particularly focusing on docstring formatting, import spacing, and code structure.
"""

import argparse
import ast
import json
import re
import sys
from pathlib import Path
from typing import Dict, List


class SyntaxIssue:
    """Represents a syntax issue found in the code."""

    def __init__(
        self,
        file_path: str,
        line_number: int,
        issue_type: str,
        description: str,
        severity: str = "warning",
    ):
        self.file_path = file_path
        self.line_number = line_number
        self.issue_type = issue_type
        self.description = description
        self.severity = severity

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "file": self.file_path,
            "line": self.line_number,
            "type": self.issue_type,
            "description": self.description,
            "severity": self.severity,
        }


class PythonSyntaxValidator:
    """Validates and fixes Python syntax issues."""

    # Common patterns that cause issues
    DOCSTRING_PATTERNS = [
        # Docstring immediately followed by code
        (r'"""([^"]+)"""(\w+)', r'"""\1"""\n\n    \2', "docstring_no_spacing"),
        (r'"""([^"]+)"""(self\.\w+)', r'"""\1"""\n        \2', "docstring_no_spacing"),
        (r'"""([^"]+)"""(return\s+)', r'"""\1"""\n        \2', "docstring_no_spacing"),
        (r'"""([^"]+)"""(if\s+)', r'"""\1"""\n        \2', "docstring_no_spacing"),
        (r'"""([^"]+)"""(try:)', r'"""\1"""\n        \2', "docstring_no_spacing"),
        (r'"""([^"]+)"""(async def)', r'"""\1"""\n\n    \2', "docstring_no_spacing"),
        (r'"""([^"]+)"""(def\s+)', r'"""\1"""\n\n    \2', "docstring_no_spacing"),
        (r'"""([^"]+)"""(class\s+)', r'"""\1"""\n\n\2', "docstring_no_spacing"),
        (r'"""([^"]+)"""(@)', r'"""\1"""\n\n\2', "docstring_no_spacing"),
    ]

    IMPORT_PATTERNS = [
        # Module docstring followed by import without blank line
        (r'("""[^"]+""")\n(import\s+)', r"\1\n\n\2", "import_spacing"),
        (r'("""[^"]+""")\n(from\s+)', r"\1\n\n\2", "import_spacing"),
    ]

    TRAILING_PERIOD_PATTERNS = [
        # Trailing periods on statements
        (r"(\s*)(self\.\w+\s*=\s*[^.]+)\.\s*$", r"\1\2", "trailing_period"),
        (r"(\s*)(\w+\s*=\s*[^.]+)\.\s*$", r"\1\2", "trailing_period"),
        (r"(\s*)(self\.\w+\.clear\(\))\.\s*$", r"\1\2", "trailing_period"),
        (r"(\s*)(self\.\w+\.\w+\(\))\.\s*$", r"\1\2", "trailing_period"),
    ]

    def __init__(self, auto_fix: bool = False):
        self.auto_fix = auto_fix
        self.issues: List[SyntaxIssue] = []

    def validate_file(self, file_path: Path) -> List[SyntaxIssue]:
        """Validate a single Python file."""
        issues = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check for basic Python syntax
            try:
                ast.parse(content)
            except SyntaxError as e:
                issues.append(
                    SyntaxIssue(
                        str(file_path),
                        e.lineno or 0,
                        "syntax_error",
                        f"Python syntax error: {e.msg}",
                        "error",
                    )
                )
                return issues

            # Check for specific patterns
            lines = content.split("\n")

            # Check docstring spacing
            for i, line in enumerate(lines):
                for pattern, _, issue_type in self.DOCSTRING_PATTERNS:
                    if re.search(pattern, line):
                        issues.append(
                            SyntaxIssue(
                                str(file_path),
                                i + 1,
                                issue_type,
                                "Docstring not properly separated from following code",
                            )
                        )

            # Check import spacing
            for i in range(len(lines) - 1):
                if lines[i].strip().endswith('"""') and lines[i + 1].strip().startswith(
                    ("import ", "from ")
                ):
                    issues.append(
                        SyntaxIssue(
                            str(file_path),
                            i + 2,
                            "import_spacing",
                            "Import statement should be separated from module docstring by blank line",
                        )
                    )

            # Check trailing periods
            for i, line in enumerate(lines):
                if re.search(r"\.\s*$", line) and not line.strip().endswith(
                    ("...", '."', ".'", ".)")
                ):
                    # Check if it's likely a statement ending with period
                    if re.search(
                        r"(=\s*[^.]+|\.clear\(\)|\.append\([^)]+\))\.\s*$", line
                    ):
                        issues.append(
                            SyntaxIssue(
                                str(file_path),
                                i + 1,
                                "trailing_period",
                                "Statement has unnecessary trailing period",
                            )
                        )

            # Check for try without except/finally
            for i, line in enumerate(lines):
                if line.strip() == "try:":
                    # Look ahead for except or finally
                    found_handler = False
                    j = i + 1
                    indent_level = len(line) - len(line.lstrip())

                    while j < len(lines):
                        next_line = lines[j]
                        if next_line.strip():
                            next_indent = len(next_line) - len(next_line.lstrip())
                            if next_indent <= indent_level:
                                if next_line.strip().startswith(("except", "finally")):
                                    found_handler = True
                                break
                        j += 1

                    if not found_handler:
                        issues.append(
                            SyntaxIssue(
                                str(file_path),
                                i + 1,
                                "incomplete_try",
                                "Try block without except or finally clause",
                                "error",
                            )
                        )

        except Exception as e:
            issues.append(
                SyntaxIssue(
                    str(file_path), 0, "read_error", f"Error reading file: {e}", "error"
                )
            )

        return issues

    def fix_file(self, file_path: Path) -> bool:
        """Fix syntax issues in a file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Apply docstring fixes
            for pattern, replacement, _ in self.DOCSTRING_PATTERNS:
                content = re.sub(pattern, replacement, content)

            # Apply import fixes
            for pattern, replacement, _ in self.IMPORT_PATTERNS:
                content = re.sub(pattern, replacement, content)

            # Apply trailing period fixes
            for pattern, replacement, _ in self.TRAILING_PERIOD_PATTERNS:
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

            # Fix try blocks without except/finally
            lines = content.split("\n")
            fixed_lines = []
            i = 0

            while i < len(lines):
                line = lines[i]
                if line.strip() == "try:":
                    # Check if needs fixing
                    indent_level = len(line) - len(line.lstrip())
                    needs_fix = True
                    j = i + 1

                    while j < len(lines) and lines[j].strip():
                        if lines[j].strip().startswith(("except", "finally")):
                            needs_fix = False
                            break
                        j += 1

                    if needs_fix:
                        fixed_lines.append(line)
                        # Add content until we need to add except
                        j = i + 1
                        while j < len(lines) and (
                            not lines[j].strip()
                            or len(lines[j]) - len(lines[j].lstrip()) > indent_level
                        ):
                            fixed_lines.append(lines[j])
                            j += 1
                        # Add generic except
                        fixed_lines.append(" " * indent_level + "except Exception:")
                        fixed_lines.append(" " * (indent_level + 4) + "pass")
                        i = j - 1
                    else:
                        fixed_lines.append(line)
                else:
                    fixed_lines.append(line)
                i += 1

            content = "\n".join(fixed_lines)

            # Only write if changes were made
            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return True

            return False

        except Exception:
            return False

    def validate_directory(
        self, directory: Path, fix: bool = False
    ) -> List[SyntaxIssue]:
        """Validate all Python files in a directory."""
        all_issues = []

        for py_file in directory.rglob("*.py"):
            # Skip virtual environments and cache directories
            if any(
                part in py_file.parts
                for part in [".venv", "venv", "__pycache__", ".git"]
            ):
                continue

            issues = self.validate_file(py_file)
            all_issues.extend(issues)

            if fix and issues:
                if self.fix_file(py_file):
                    print(f"✅ Fixed {py_file}")
                else:
                    print(f"❌ Failed to fix {py_file}")

        return all_issues


def main():
    """Main entry point for the syntax validator."""
    parser = argparse.ArgumentParser(description="Python syntax validator and fixer")
    parser.add_argument(
        "path", nargs="?", default=".", help="Path to validate (file or directory)"
    )
    parser.add_argument("--fix", action="store_true", help="Automatically fix issues")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument(
        "--severity",
        choices=["all", "error", "warning"],
        default="all",
        help="Minimum severity to report",
    )

    args = parser.parse_args()

    validator = PythonSyntaxValidator(auto_fix=args.fix)
    path = Path(args.path)

    if path.is_file():
        issues = validator.validate_file(path)
        if args.fix and issues:
            validator.fix_file(path)
    else:
        issues = validator.validate_directory(path, fix=args.fix)

    # Filter by severity
    if args.severity != "all":
        issues = [
            i
            for i in issues
            if i.severity == args.severity
            or (args.severity == "warning" and i.severity == "error")
        ]

    # Output results
    if args.json:
        print(json.dumps([i.to_dict() for i in issues], indent=2))
    else:
        if not issues:
            print("✅ No syntax issues found!")
            return 0

        print(f"\n🔍 Found {len(issues)} syntax issues:\n")

        # Group by file
        by_file = {}
        for issue in issues:
            if issue.file_path not in by_file:
                by_file[issue.file_path] = []
            by_file[issue.file_path].append(issue)

        for file_path, file_issues in by_file.items():
            print(f"\n📄 {file_path}:")
            for issue in sorted(file_issues, key=lambda x: x.line_number):
                severity_icon = "❌" if issue.severity == "error" else "⚠️"
                print(
                    f"  {severity_icon} Line {issue.line_number}: {issue.description} ({issue.issue_type})"
                )

    return 1 if any(i.severity == "error" for i in issues) else 0


if __name__ == "__main__":
    sys.exit(main())
