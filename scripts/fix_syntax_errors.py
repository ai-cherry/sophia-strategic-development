DDD #!/usr/bin/env python3
"""
Script to fix common syntax errors in Python files.
"""

import json
import re
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def load_syntax_errors():
    """Load syntax errors from the validation report."""
    report_path = Path("syntax_validation_report.json")
    if not report_path.exists():
        logger.error("syntax_validation_report.json not found")
        return {}

    with open(report_path, "r") as f:
        data = json.load(f)
        return data.get("errors", {})


def fix_common_syntax_patterns(content):
    """Fix common syntax error patterns."""
    lines = content.split("\n")
    fixed_lines = []

    for i, line in enumerate(lines):
        original_line = line

        # Fix 1: Remove trailing periods after parentheses, brackets, etc.
        # Matches patterns like ").^", "].^", "}.^"
        line = re.sub(r"([)\]}])\.\s*$", r"\1", line)
        if line != original_line:
            logger.info(f"Fixed trailing period after closing bracket on line {i+1}")

        # Fix 2: Fix "try:." pattern
        line = re.sub(r"try:\.\s*$", "try:", line)
        if line != original_line:
            logger.info(f"Fixed 'try:.' pattern on line {i+1}")

        # Fix 3: Fix common method/function definition errors
        line = re.sub(r"def\s+(\w+)\s*\([^)]*\)\s*:\.\s*$", r"def \1():", line)
        if line != original_line:
            logger.info(f"Fixed method definition on line {i+1}")

        # Fix 4: Fix docstring followed by code on same line
        # Pattern: """docstring"""code -> """docstring"""\ncode
        match = re.match(r'^(\s*)("""[^"]+""")((?!$).+)$', line)
        if match:
            indent, docstring, code = match.groups()
            fixed_lines.append(f"{indent}{docstring}")
            fixed_lines.append(f"{indent}{code}")
            logger.info(f"Split docstring and code on line {i+1}")
            continue

        # Fix 5: Fix improper string concatenation
        line = re.sub(r'"\\n"join\(', r'"\n".join(', line)
        if line != original_line:
            logger.info(f"Fixed string join syntax on line {i+1}")

        # Fix 6: Fix return statement with trailing period
        line = re.sub(r"return\s+([^.]+)\.\s*$", r"return \1", line)
        if line != original_line:
            logger.info(f"Fixed return statement on line {i+1}")

        # Fix 7: Fix assignment with trailing period
        line = re.sub(r"=\s*([^.]+)\.\s*$", r"= \1", line)
        if line != original_line:
            logger.info(f"Fixed assignment statement on line {i+1}")

        # Fix 8: Fix if statement errors
        line = re.sub(r"if\s+([^:]+):\.\s*$", r"if \1:", line)
        if line != original_line:
            logger.info(f"Fixed if statement on line {i+1}")

        # Fix 9: Fix logger statements with trailing period
        line = re.sub(r"(logger\.\w+\([^)]+\))\.\s*$", r"\1", line)
        if line != original_line:
            logger.info(f"Fixed logger statement on line {i+1}")

        # Fix 10: Fix await statements with trailing period
        line = re.sub(r"(await\s+[^.]+)\.\s*$", r"\1", line)
        if line != original_line:
            logger.info(f"Fixed await statement on line {i+1}")

        fixed_lines.append(line)

    return "\n".join(fixed_lines)


def process_file(file_path):
    """Process a single file to fix syntax errors."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content
        fixed_content = fix_common_syntax_patterns(content)

        if fixed_content != original_content:
            # Create backup
            backup_path = file_path.with_suffix(file_path.suffix + ".backup")
            with open(backup_path, "w", encoding="utf-8") as f:
                f.write(original_content)

            # Write fixed content
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(fixed_content)

            logger.info(f"Fixed and backed up: {file_path}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")
        return False


def main():
    """Main function to fix syntax errors."""
    errors = load_syntax_errors()

    if not errors:
        logger.info("No syntax errors found in report")
        return

    logger.info(f"Found {len(errors)} files with syntax errors")

    fixed_count = 0
    for file_path, error_msg in errors.items():
        path = Path(file_path)
        if path.exists():
            logger.info(f"\nProcessing: {file_path}")
            logger.info(f"Error: {error_msg}")
            if process_file(path):
                fixed_count += 1
        else:
            logger.warning(f"File not found: {file_path}")

    logger.info(f"\nFixed {fixed_count} files")


if __name__ == "__main__":
    main()
