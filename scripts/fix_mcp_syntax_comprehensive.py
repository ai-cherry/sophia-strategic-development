#!/usr/bin/env python3
"""
Comprehensive fix for all MCP server syntax errors
"""

import logging
import re
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def fix_malformed_error_handling(file_path: Path):
    """Fix the malformed error_handling pattern in Linear and Asana servers"""
    with open(file_path) as f:
        content = f.read()

    # Pattern to fix the malformed error handling
    pattern = r'def _error_handling_1\(self\):\s*"""Extracted error_handling logic"""\s*if name == "get_projects":'

    if re.search(pattern, content, re.DOTALL):
        logger.info(f"  Fixing malformed error_handling in {file_path}")

        # Replace the malformed pattern
        content = re.sub(
            pattern,
            '''def _error_handling_1(self):
        """Extracted error_handling logic"""
        pass

    async def handle_tool_call(self, name: str, arguments: dict):
        """Handle tool calls"""
        try:
            if name == "get_projects":''',
            content,
            flags=re.DOTALL,
        )

        # Fix the orphaned handle_call_tool method
        content = re.sub(
            r'@self\.server\.call_tool\(\)\s*async def handle_call_tool\(name: str, arguments: dict\) -> CallToolResult:\s*"""Handle tool calls\."""\s*self\._error_handling_1\(\)',
            '''@self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> CallToolResult:
            """Handle tool calls."""
            try:
                result = await self.handle_tool_call(name, arguments)''',
            content,
        )

        # Fix the orphaned result = await lines
        content = re.sub(
            r"(\s+)result = await self\.search_", r'\1elif name == "search_', content
        )

        with open(file_path, "w") as f:
            f.write(content)

        return True
    return False


def fix_huggingface_try_block(file_path: Path):
    """Fix the empty try block in huggingface_ai_mcp_server.py"""
    with open(file_path) as f:
        lines = f.readlines()

    # Look for try: followed by non-indented line around line 409
    for i in range(405, min(415, len(lines))):
        if i < len(lines) and lines[i].strip() == "try:":
            # Check if next line is not indented
            if i + 1 < len(lines) and not lines[i + 1].startswith("    "):
                logger.info(f"  Fixing empty try block at line {i + 1}")
                # Insert a pass statement
                lines.insert(i + 1, "        # TODO: Implement error handling\n")
                lines.insert(i + 2, "        pass\n")

                with open(file_path, "w") as f:
                    f.writelines(lines)
                return True
    return False


def fix_codacy_empty_function(file_path: Path):
    """Fix empty function definition in codacy_server.py"""
    with open(file_path) as f:
        lines = f.readlines()

    # Look for function definition without body around line 327
    for i in range(320, min(335, len(lines))):
        if (
            i < len(lines)
            and lines[i].strip().startswith("def ")
            and lines[i].strip().endswith(":")
        ):
            # Check if next line is not indented
            if i + 1 < len(lines) and not lines[i + 1].strip().startswith(" "):
                logger.info(f"  Fixing empty function at line {i + 1}")
                # Insert a pass statement
                lines.insert(i + 1, "    # TODO: Implement function\n")
                lines.insert(i + 2, "    pass\n")

                with open(file_path, "w") as f:
                    f.writelines(lines)
                return True
    return False


def fix_snowflake_cortex_try_except(file_path: Path):
    """Fix missing except block in snowflake_cortex_mcp_server.py"""
    with open(file_path) as f:
        content = f.read()

    # Check if there's a try without except
    lines = content.split("\n")

    in_try_block = False
    try_line = -1

    for i, line in enumerate(lines):
        if line.strip() == "try:" and i < 30:  # Near the beginning
            in_try_block = True
            try_line = i
        elif in_try_block and not line.startswith("    ") and line.strip() != "":
            # End of try block, check if there's an except
            if not line.strip().startswith("except"):
                logger.info(f"  Adding except block after try at line {try_line + 1}")
                lines.insert(i, "except Exception as e:")
                lines.insert(i + 1, "    logger.error(f'Import error: {e}')")
                lines.insert(i + 2, "    raise")

                with open(file_path, "w") as f:
                    f.write("\n".join(lines))
                return True
            break

    return False


def validate_syntax(file_path: Path) -> bool:
    """Validate Python syntax of a file"""
    import ast

    try:
        with open(file_path) as f:
            content = f.read()
        ast.parse(content)
        return True
    except SyntaxError as e:
        logger.error(f"    Syntax error at line {e.lineno}: {e.msg}")
        return False


def main():
    """Main execution"""
    logger.info("🚀 Comprehensive MCP Server Syntax Fix")
    logger.info("=" * 60)

    fixes = [
        ("mcp-servers/linear/linear_mcp_server.py", fix_malformed_error_handling),
        ("mcp-servers/asana/asana_mcp_server.py", fix_malformed_error_handling),
        (
            "mcp-servers/huggingface_ai/huggingface_ai_mcp_server.py",
            fix_huggingface_try_block,
        ),
        ("mcp-servers/codacy/codacy_server.py", fix_codacy_empty_function),
        (
            "mcp-servers/snowflake_cortex/snowflake_cortex_mcp_server.py",
            fix_snowflake_cortex_try_except,
        ),
    ]

    fixed_count = 0

    for file_path_str, fix_func in fixes:
        file_path = Path(file_path_str)
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            continue

        logger.info(f"\nProcessing {file_path}...")

        # Apply fix
        if fix_func(file_path):
            fixed_count += 1

        # Validate syntax
        if validate_syntax(file_path):
            logger.info("  ✅ Valid syntax after fix")
        else:
            logger.error("  ❌ Still has syntax errors")

    logger.info(f"\n{'=' * 60}")
    logger.info(f"✅ Fixed {fixed_count} files")

    # Run final validation
    logger.info("\n🔍 Final validation of all fixed files...")
    all_valid = True

    for file_path_str, _ in fixes:
        file_path = Path(file_path_str)
        if file_path.exists():
            logger.info(f"\n{file_path}:")
            if not validate_syntax(file_path):
                all_valid = False

    if all_valid:
        logger.info("\n✅ All files have valid syntax!")
    else:
        logger.warning("\n⚠️  Some files still have syntax errors")


if __name__ == "__main__":
    main()
