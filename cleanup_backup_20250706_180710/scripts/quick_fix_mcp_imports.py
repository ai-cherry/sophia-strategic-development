#!/usr/bin/env python3
"""
Quick fix for MCP import errors
Fixes 'from mcp import Server' to 'from mcp import server'
"""

import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def fix_mcp_imports():
    """Fix MCP import statements in all server files"""
    logger.info("🔧 Fixing MCP import statements...")

    # Find all Python files in mcp-servers directory
    mcp_dir = Path("mcp-servers")
    if not mcp_dir.exists():
        logger.error("mcp-servers directory not found!")
        return

    fixed_count = 0

    for py_file in mcp_dir.rglob("*.py"):
        try:
            with open(py_file) as f:
                content = f.read()

            # Check if file has the incorrect import
            if "from mcp import Server" in content:
                logger.info(f"  Fixing {py_file}")

                # Replace the import
                new_content = content.replace(
                    "from mcp import Server", "from mcp import server"
                )
                new_content = new_content.replace("Server(", "server(")

                # Write back
                with open(py_file, "w") as f:
                    f.write(new_content)

                fixed_count += 1

        except Exception as e:
            logger.error(f"  Error processing {py_file}: {e}")

    logger.info(f"\n✅ Fixed {fixed_count} files")


def validate_python_files():
    """Validate Python syntax in all MCP server files"""
    logger.info("\n🔍 Validating Python syntax...")

    import ast

    errors = []

    for py_file in Path("mcp-servers").rglob("*.py"):
        try:
            with open(py_file) as f:
                content = f.read()

            # Try to parse the file
            ast.parse(content)

        except SyntaxError as e:
            errors.append({"file": str(py_file), "line": e.lineno, "error": str(e.msg)})
            logger.error(f"  ❌ {py_file}:{e.lineno} - {e.msg}")

    if errors:
        logger.warning(f"\n⚠️  Found {len(errors)} syntax errors")

        # Save error report
        with open("mcp_syntax_errors.txt", "w") as f:
            for error in errors:
                f.write(f"{error['file']}:{error['line']} - {error['error']}\n")

        logger.info("  Error details saved to mcp_syntax_errors.txt")
    else:
        logger.info("\n✅ All files have valid syntax!")


def main():
    """Main execution"""
    logger.info("🚀 MCP Quick Fix Tool")

    # Fix imports
    fix_mcp_imports()

    # Validate syntax
    validate_python_files()

    logger.info("\n✅ Quick fix complete!")


if __name__ == "__main__":
    main()
