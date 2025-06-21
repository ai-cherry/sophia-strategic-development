#!/usr/bin/env python3
"""Comprehensive fix for all syntax issues in Python files."""

import re
from pathlib import Path
from typing import List


def fix_docstring_issues(content: str) -> str:
    """Fix all docstring concatenation issues."""
    # Fix docstring concatenations with various patterns
    patterns = [
        (r'"""([^"]+)"""(\w+)', r'"""\1"""\n\n    \2'),
        (r'"""([^"]+)"""(self\.\w+)', r'"""\1"""\n        \2'),
        (r'"""([^"]+)"""(return\s+)', r'"""\1"""\n        \2'),
        (r'"""([^"]+)"""(if\s+)', r'"""\1"""\n        \2'),
        (r'"""([^"]+)"""(try:)', r'"""\1"""\n        \2'),
        (r'"""([^"]+)"""(async def)', r'"""\1"""\n\n    \2'),
        (r'"""([^"]+)"""(def\s+)', r'"""\1"""\n\n    \2'),
        (r'"""([^"]+)"""(class\s+)', r'"""\1"""\n\n\2'),
        (r'"""([^"]+)"""(@)', r'"""\1"""\n\n\2'),
    ]

    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)

    return content


def fix_import_issues(content: str) -> str:
    """Fix import statement issues."""
    # Fix module docstring followed by import without blank line
    content = re.sub(r'("""[^"]+""")\n(import\s+)', r"\1\n\n\2", content)
    content = re.sub(r'("""[^"]+""")\n(from\s+)', r"\1\n\n\2", content)

    return content


def fix_trailing_periods(content: str) -> str:
    """Fix trailing periods on statements."""
    # Remove trailing periods from assignments
    content = re.sub(
        r"(\s*)(self\.\w+\s*=\s*[^.]+)\.\s*$", r"\1\2", content, flags=re.MULTILINE
    )
    content = re.sub(
        r"(\s*)(\w+\s*=\s*[^.]+)\.\s*$", r"\1\2", content, flags=re.MULTILINE
    )

    # Fix method calls with trailing periods
    content = re.sub(
        r"(\s*)(self\.\w+\.clear\(\))\.\s*$", r"\1\2", content, flags=re.MULTILINE
    )
    content = re.sub(
        r"(\s*)(self\.\w+\.\w+\(\))\.\s*$", r"\1\2", content, flags=re.MULTILINE
    )

    return content


def fix_multiline_strings(content: str) -> str:
    """Fix multiline string issues."""
    # Fix SQL queries and other multiline strings
    content = re.sub(r'(\s*)("""[^"]*?)\n\s*([^"]*?""")', r"\1\2\n\1\3", content)

    return content


def fix_try_except_blocks(content: str) -> str:
    """Fix try-except block issues."""
    # Ensure try blocks have except or finally
    lines = content.split("\n")
    fixed_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("try:"):
            # Look for the next non-empty line
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1

            # Check if it's except or finally
            if j < len(lines) and not (
                lines[j].strip().startswith("except")
                or lines[j].strip().startswith("finally")
            ):
                # Insert a generic except block
                indent = len(line) - len(line.lstrip())
                fixed_lines.append(line)
                fixed_lines.append(" " * indent + "except Exception:")
                fixed_lines.append(" " * (indent + 4) + "pass")
                i = j
                continue

        fixed_lines.append(line)
        i += 1

    return "\n".join(fixed_lines)


def fix_indentation_issues(content: str) -> str:
    """Fix common indentation issues."""
    lines = content.split("\n")
    fixed_lines = []

    for i, line in enumerate(lines):
        # Skip empty lines
        if not line.strip():
            fixed_lines.append(line)
            continue

        # Fix unexpected indentation after docstrings
        if (
            i > 0
            and lines[i - 1].strip().endswith('"""')
            and line.strip()
            and not line[0].isspace()
        ):
            # This line should not be indented
            fixed_lines.append(line.lstrip())
        else:
            fixed_lines.append(line)

    return "\n".join(fixed_lines)


def fix_file(file_path: Path) -> bool:
    """Fix syntax issues in a single file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Apply all fixes
        content = fix_import_issues(content)
        content = fix_docstring_issues(content)
        content = fix_trailing_periods(content)
        content = fix_multiline_strings(content)
        content = fix_try_except_blocks(content)
        content = fix_indentation_issues(content)

        # Only write if changes were made
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True

        return False
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False


def get_python_files() -> List[Path]:
    """Get all Python files that need fixing."""
    # List of specific files with known issues
    problem_files = [
        # Backend core files
        "backend/core/enhanced_embedding_manager.py",
        "backend/core/config_loader.py",
        "backend/core/contextual_memory_intelligence.py",
        "backend/core/hierarchical_cache.py",
        "backend/core/real_time_streaming.py",
        "backend/core/comprehensive_memory_manager.py",
        # Backend integration files
        "backend/integrations/base_integration.py",
        # Backend MCP files
        "backend/mcp/unified_mcp_servers.py",
        # Backend app files
        "backend/app/websocket_manager.py",
        # Backend vector files
        "backend/vector/vector_integration.py",
        # Backend pipeline files
        "backend/pipeline/data_pipeline_architecture.py",
        # Backend agent files
        "backend/agents/core/persistent_memory.py",
        "backend/agents/specialized/call_analysis_agent.py",
        # Script files
        "scripts/check_imports.py",
        "scripts/start_backend_simple.py",
        "scripts/fix_all_docstrings.py",
        "scripts/fix_comprehensive_syntax.py",
        "scripts/fix_precommit_issues.py",
        "scripts/fix_precommit_issues_v2.py",
        "scripts/fix_precommit_final.py",
        "scripts/fix_precommit_complete.py",
        "scripts/fix_docstrings_v2.py",
        "scripts/fix_syntax_errors.py",
        "scripts/fix_docstrings_improved.py",
        "scripts/fix_all_syntax_issues.py",
        "scripts/fix_python_syntax_complete.py",
        "scripts/fix_syntax_final.py",
        "scripts/fix_final_syntax_issues.py",
        "scripts/fix_docstring_syntax_final.py",
        "scripts/fix_streaming_sql_strings.py",
        "scripts/fix_sql_multiline_strings.py",
        "scripts/fix_duplicate_sql_calls.py",
        "scripts/fix_streaming_final.py",
        "scripts/final_cleanup.py",
    ]

    files = []
    for file_path in problem_files:
        path = Path(file_path)
        if path.exists():
            files.append(path)

    return files


def main():
    """Fix syntax issues in all problematic Python files."""
    print("🔧 Applying comprehensive syntax fixes...\n")

    files = get_python_files()
    fixed_count = 0

    for file_path in files:
        if fix_file(file_path):
            print(f"✅ Fixed {file_path}")
            fixed_count += 1
        else:
            print(f"⏭️  No changes needed for {file_path}")

    print(f"\n✨ Fixed {fixed_count} files out of {len(files)} total files.")


if __name__ == "__main__":
    main()
