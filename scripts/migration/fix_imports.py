#!/usr/bin/env python3
"""
Fix missing field_validator imports in files
"""

import re
from pathlib import Path


def fix_imports_in_file(file_path: Path):
    """Fix imports in a single file"""
    content = file_path.read_text()
    original = content

    # Check if file uses field_validator but doesn't import it
    if (
        "@field_validator" in content
        and "field_validator" not in content.split("@field_validator")[0]
    ):
        # Find the pydantic import line
        import_match = re.search(r"from pydantic import ([^\n]+)", content)
        if import_match:
            imports = import_match.group(1)
            # Add field_validator if not present
            if "field_validator" not in imports:
                new_imports = imports.rstrip() + ", field_validator"
                content = content.replace(
                    f"from pydantic import {imports}",
                    f"from pydantic import {new_imports}",
                )
        else:
            # No pydantic import found, add one
            # Find where to add it (after other imports)
            lines = content.split("\n")
            import_end = 0
            for i, line in enumerate(lines):
                if line.startswith("import ") or line.startswith("from "):
                    import_end = i

            lines.insert(import_end + 1, "from pydantic import field_validator")
            content = "\n".join(lines)

    if content != original:
        file_path.write_text(content)
        print(f"Fixed imports in: {file_path}")
        return True
    return False


def main():
    """Fix imports in all files that need field_validator"""
    files_to_fix = [
        "infrastructure/integrations/gong_api_client_enhanced.py",
        "infrastructure/mcp_servers/ai_memory/ai_memory_models.py",
        "infrastructure/mcp_servers/ai_memory/core/config.py",
        "infrastructure/mcp_servers/ai_memory/core/models.py",
        "mcp-servers/codacy/codacy_server.py",
    ]

    fixed_count = 0
    for file_path in files_to_fix:
        path = Path(file_path)
        if path.exists():
            if fix_imports_in_file(path):
                fixed_count += 1

    print(f"\nFixed imports in {fixed_count} files")


if __name__ == "__main__":
    main()
