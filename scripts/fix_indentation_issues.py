#!/usr/bin/env python3
"""
Fix Indentation Issues Script
Quick fix for indentation problems caused by abstract method insertion
"""

import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fix_indentation_in_file(file_path: Path) -> bool:
    """Fix indentation issues in a Python file"""
    try:
        with open(file_path) as f:
            content = f.read()

        # Split into lines
        lines = content.split("\n")
        fixed_lines = []

        for _i, line in enumerate(lines):
            # Check for common indentation issues
            if line.strip().startswith("async def ") or line.strip().startswith("def "):
                # Ensure proper indentation for methods (4 spaces inside class)
                if not line.startswith("    ") and line.strip():
                    line = "    " + line.strip()

            # Fix lines that start with extra spaces
            if line.startswith("        ") and line.strip().startswith(
                ("async def ", "def ")
            ):
                line = "    " + line.strip()

            fixed_lines.append(line)

        # Write back
        fixed_content = "\n".join(fixed_lines)

        # Try to compile to check syntax
        try:
            compile(fixed_content, str(file_path), "exec")

            with open(file_path, "w") as f:
                f.write(fixed_content)

            logger.info(f"✅ Fixed indentation in {file_path.name}")
            return True

        except SyntaxError as e:
            logger.error(f"❌ Syntax error remains in {file_path.name}: {e}")
            return False

    except Exception as e:
        logger.error(f"❌ Failed to fix {file_path.name}: {e}")
        return False


def fix_missing_logging_import():
    """Fix the missing backend.utils.logging import in codacy"""
    codacy_file = (
        Path(__file__).parent.parent / "mcp-servers/codacy/codacy_mcp_server.py"
    )

    try:
        with open(codacy_file) as f:
            content = f.read()

        # Replace the problematic import
        content = content.replace(
            "from backend.utils.logging import get_logger",
            "import logging\n# from backend.utils.logging import get_logger",
        )

        # Also replace any usage of get_logger
        content = content.replace("get_logger(__name__)", "logging.getLogger(__name__)")

        with open(codacy_file, "w") as f:
            f.write(content)

        logger.info("✅ Fixed codacy logging import")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to fix codacy logging: {e}")
        return False


def main():
    """Fix indentation and import issues"""
    logger.info("🔧 Fixing Indentation and Import Issues...")

    # Files to fix
    files_to_fix = [
        Path(__file__).parent.parent / "mcp-servers/ai_memory/ai_memory_mcp_server.py",
        Path(__file__).parent.parent / "mcp-servers/ag_ui/ag_ui_mcp_server.py",
    ]

    fixed_count = 0

    # Fix indentation
    for file_path in files_to_fix:
        if file_path.exists():
            if fix_indentation_in_file(file_path):
                fixed_count += 1
        else:
            logger.warning(f"⚠️ File not found: {file_path}")

    # Fix logging import
    if fix_missing_logging_import():
        fixed_count += 1

    logger.info("\n🎯 INDENTATION FIX SUMMARY:")
    logger.info(f"   Fixed issues: {fixed_count}")

    if fixed_count >= 2:
        logger.info("   🎉 Key issues fixed!")
        return True
    else:
        logger.warning("   ⚠️ Some issues remain")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
