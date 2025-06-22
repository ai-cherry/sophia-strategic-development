#!/usr/bin/env python3
"""Fix remaining docstring merge issues in specific files."""

import re
from pathlib import Path


def fix_docstring_merge_issues(content: str) -> str:
    """Fix docstring merge issues where docstring and code are on the same line."""
    # Pattern to find docstrings merged with code on the same line
    # Matches: """docstring"""code
    pattern = r'("""[^"]+""")([^"\s#\n])'

    def replacer(match):
        docstring = match.group(1)
        code = match.group(2)
        # Add newline and proper indentation after docstring
        # Detect indentation from the line
        lines = content[: match.start()].split("\n")
        current_line = lines[-1] if lines else ""
        indent_match = re.match(r"^(\s*)", current_line)
        indent = indent_match.group(1) if indent_match else ""

        return f"{docstring}\n{indent}{code}"

    # Apply the fix
    fixed_content = re.sub(pattern, replacer, content)

    return fixed_content


def process_file(filepath: Path) -> bool:
    """Process a single file to fix docstring issues."""
    try:
        content = filepath.read_text(encoding="utf-8")
        original_content = content

        # Fix docstring merge issues
        content = fix_docstring_merge_issues(content)

        if content != original_content:
            filepath.write_text(content, encoding="utf-8")
            print(f"Fixed: {filepath}")
            return True
        else:
            print(f"No changes needed: {filepath}")
            return False

    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False


def main():
    """Main function to fix docstring issues in specific files."""
    files_to_fix = [
        "backend/agents/docker_agent.py",
        "backend/agents/pulumi_agent.py",
        "backend/core/context_manager.py",
        "backend/integrations/pulumi_mcp_client.py",
        "backend/integrations/portkey_client.py",
    ]

    fixed_count = 0
    for file_path in files_to_fix:
        path = Path(file_path)
        if path.exists():
            if process_file(path):
                fixed_count += 1
        else:
            print(f"File not found: {file_path}")

    print(f"\nFixed {fixed_count} files")


if __name__ == "__main__":
    main()
