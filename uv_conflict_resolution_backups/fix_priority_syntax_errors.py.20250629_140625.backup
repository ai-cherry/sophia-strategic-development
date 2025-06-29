#!/usr/bin/env python3
"""
Script to fix priority syntax errors in existing files.
"""

import logging
import re
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Priority files to fix based on the syntax validation report
PRIORITY_FILES = [
    "backend/mcp/ai_memory_mcp_server.py",
    "backend/mcp/costar_mcp_server.py",
    "backend/core/comprehensive_memory_manager.py",
    "backend/core/contextual_memory_intelligence.py",
    "backend/core/hierarchical_cache.py",
    "backend/core/integration_registry.py",
    "backend/core/real_time_streaming.py",
    "backend/core/secure_credential_manager.py",
]


def fix_syntax_in_file(file_path):
    """Fix syntax errors in a specific file."""
    path = Path(file_path)
    if not path.exists():
        logger.warning(f"File not found: {file_path}")
        return False

    try:
        with open(path, encoding="utf-8") as f:
            content = f.read()

        original_content = content
        lines = content.split("\n")
        fixed_lines = []

        for i, line in enumerate(lines):
            original_line = line

            # Fix 1: Remove trailing periods after parentheses, brackets, etc.
            line = re.sub(r"([)\]}])\.\s*$", r"\1", line)

            # Fix 2: Fix "try:." pattern
            line = re.sub(r"try:\.\s*$", "try:", line)

            # Fix 3: Fix return statements with .^ pattern
            line = re.sub(r"return\s+\[\.\s*$", "return [", line)

            # Fix 4: Fix await statements with trailing period
            line = re.sub(r"(await\s+[^.]+)\.\s*$", r"\1", line)

            # Fix 5: Fix if statements with trailing period
            line = re.sub(r"if\s+([^:]+):\.\s*$", r"if \1:", line)

            # Fix 6: Fix assignment statements with trailing period
            line = re.sub(r"=\s*([^.]+)\.\s*$", r"= \1", line)

            # Fix 7: Fix logger statements with trailing period
            line = re.sub(r"(logger\.\w+\([^)]+\))\.\s*$", r"\1", line)

            # Fix 8: Fix print statements with trailing period
            line = re.sub(r"(print\([^)]+\))\.\s*$", r"\1", line)

            # Fix 9: Fix method calls with trailing period
            line = re.sub(r"(\w+\([^)]*\))\.\s*$", r"\1", line)

            # Fix 10: Fix docstring followed by code on same line
            match = re.match(r'^(\s*)("""[^"]+""")((?!$).+)$', line)
            if match:
                indent, docstring, code = match.groups()
                fixed_lines.append(f"{indent}{docstring}")
                fixed_lines.append(f"{indent}{code}")
                if line != original_line:
                    logger.info(f"  Line {i + 1}: Split docstring and code")
                continue

            if line != original_line:
                logger.info(f"  Line {i + 1}: Fixed syntax error")

            fixed_lines.append(line)

        fixed_content = "\n".join(fixed_lines)

        if fixed_content != original_content:
            # Create backup
            backup_path = path.with_suffix(path.suffix + ".backup")
            with open(backup_path, "w", encoding="utf-8") as f:
                f.write(original_content)

            # Write fixed content
            with open(path, "w", encoding="utf-8") as f:
                f.write(fixed_content)

            logger.info(f"✓ Fixed and backed up: {file_path}")
            return True
        else:
            logger.info(f"✓ No changes needed: {file_path}")

        return False
    except Exception as e:
        logger.error(f"✗ Error processing {file_path}: {e}")
        return False


def main():
    """Main function to fix priority syntax errors."""
    logger.info("Starting priority syntax error fixes...\n")

    fixed_count = 0
    for file_path in PRIORITY_FILES:
        logger.info(f"Processing: {file_path}")
        if fix_syntax_in_file(file_path):
            fixed_count += 1
        print()  # Empty line for readability

    logger.info(f"\nSummary: Fixed {fixed_count} out of {len(PRIORITY_FILES)} files")


if __name__ == "__main__":
    main()
