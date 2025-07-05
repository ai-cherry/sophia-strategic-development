#!/usr/bin/env python3
"""
Fix all syntax errors in MCP servers
Addresses indentation and missing code blocks
"""

import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def fix_linear_mcp_server():
    """Fix indentation error in linear_mcp_server.py line 67"""
    file_path = Path("mcp-servers/linear/linear_mcp_server.py")
    if not file_path.exists():
        logger.warning(f"File not found: {file_path}")
        return

    logger.info(f"Fixing {file_path}...")

    with open(file_path) as f:
        lines = f.readlines()

    # Fix line 67 - it's an indented if statement that should be at function level
    if len(lines) > 66 and lines[66].strip().startswith("if name =="):
        # Remove extra indentation
        lines[66] = lines[66].lstrip() + "\n"

        # Write back
        with open(file_path, "w") as f:
            f.writelines(lines)

        logger.info("  ✅ Fixed indentation error")
    else:
        logger.warning("  ⚠️  Could not find expected pattern at line 67")


def fix_asana_mcp_server():
    """Fix indentation error in asana_mcp_server.py line 70"""
    file_path = Path("mcp-servers/asana/asana_mcp_server.py")
    if not file_path.exists():
        logger.warning(f"File not found: {file_path}")
        return

    logger.info(f"Fixing {file_path}...")

    with open(file_path) as f:
        lines = f.readlines()

    # Fix line 70 - similar indentation issue
    if len(lines) > 69 and lines[69].strip().startswith("if name =="):
        lines[69] = lines[69].lstrip() + "\n"

        with open(file_path, "w") as f:
            f.writelines(lines)

        logger.info("  ✅ Fixed indentation error")
    else:
        logger.warning("  ⚠️  Could not find expected pattern at line 70")


def fix_huggingface_ai_server():
    """Fix missing indented block in huggingface_ai_mcp_server.py line 410"""
    file_path = Path("mcp-servers/huggingface_ai/huggingface_ai_mcp_server.py")
    if not file_path.exists():
        logger.warning(f"File not found: {file_path}")
        return

    logger.info(f"Fixing {file_path}...")

    with open(file_path) as f:
        lines = f.readlines()

    # Check if line 409 has a try statement without body
    if len(lines) > 409 and lines[408].strip() == "try:":
        # Insert a pass statement if the next line is not indented
        if len(lines) > 409 and not lines[409].startswith("    "):
            lines.insert(409, "        pass  # TODO: Implement error handling\n")

            with open(file_path, "w") as f:
                f.writelines(lines)

            logger.info("  ✅ Added missing indented block")
        else:
            logger.info("  ℹ️  Already has indented block")
    else:
        logger.warning("  ⚠️  Could not find try statement at line 409")


def fix_codacy_server():
    """Fix missing indented block in codacy_server.py line 328"""
    file_path = Path("mcp-servers/codacy/codacy_server.py")
    if not file_path.exists():
        logger.warning(f"File not found: {file_path}")
        return

    logger.info(f"Fixing {file_path}...")

    with open(file_path) as f:
        lines = f.readlines()

    # Check if line 327 has a function definition without body
    if len(lines) > 327 and "def " in lines[326]:
        # Insert a pass statement if the next line is not indented
        if len(lines) > 327 and not lines[327].startswith("    "):
            lines.insert(327, "    pass  # TODO: Implement function\n")

            with open(file_path, "w") as f:
                f.writelines(lines)

            logger.info("  ✅ Added missing function body")
        else:
            logger.info("  ℹ️  Already has function body")
    else:
        logger.warning("  ⚠️  Could not find function definition at line 327")


def fix_snowflake_cortex_server():
    """Fix missing except block in snowflake_cortex_mcp_server.py line 14"""
    file_path = Path("mcp-servers/snowflake_cortex/snowflake_cortex_mcp_server.py")
    if not file_path.exists():
        logger.warning(f"File not found: {file_path}")
        return

    logger.info(f"Fixing {file_path}...")

    with open(file_path) as f:
        content = f.read()

    # Look for try block without except
    if "try:" in content and "except" not in content.split("try:")[1].split("\n")[0:10]:
        # Find the try block and add a generic except
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if line.strip() == "try:" and i < 20:  # Near line 14
                # Find the end of the try block
                j = i + 1
                while j < len(lines) and (
                    lines[j].startswith("    ") or lines[j].strip() == ""
                ):
                    j += 1

                # Insert except block
                lines.insert(j, "except Exception as e:")
                lines.insert(j + 1, "    logger.error(f'Error: {e}')")
                lines.insert(j + 2, "    raise")

                with open(file_path, "w") as f:
                    f.write("\n".join(lines))

                logger.info("  ✅ Added missing except block")
                break
    else:
        logger.info("  ℹ️  Except block already exists or no try block found")


def validate_all_fixes():
    """Validate Python syntax after fixes"""
    logger.info("\n🔍 Validating all fixes...")

    import ast

    files_to_check = [
        "mcp-servers/linear/linear_mcp_server.py",
        "mcp-servers/asana/asana_mcp_server.py",
        "mcp-servers/huggingface_ai/huggingface_ai_mcp_server.py",
        "mcp-servers/codacy/codacy_server.py",
        "mcp-servers/snowflake_cortex/snowflake_cortex_mcp_server.py",
    ]

    all_valid = True

    for file_path in files_to_check:
        path = Path(file_path)
        if path.exists():
            try:
                with open(path) as f:
                    content = f.read()
                ast.parse(content)
                logger.info(f"  ✅ {file_path} - Valid syntax")
            except SyntaxError as e:
                logger.error(
                    f"  ❌ {file_path} - Still has syntax error at line {e.lineno}: {e.msg}"
                )
                all_valid = False
        else:
            logger.warning(f"  ⚠️  {file_path} - File not found")

    return all_valid


def main():
    """Main execution"""
    logger.info("🚀 Fixing All MCP Server Syntax Errors")
    logger.info("=" * 60)

    # Fix each server
    fix_linear_mcp_server()
    fix_asana_mcp_server()
    fix_huggingface_ai_server()
    fix_codacy_server()
    fix_snowflake_cortex_server()

    # Validate fixes
    if validate_all_fixes():
        logger.info("\n✅ All syntax errors fixed successfully!")
    else:
        logger.warning(
            "\n⚠️  Some syntax errors remain. Manual intervention may be needed."
        )


if __name__ == "__main__":
    main()
