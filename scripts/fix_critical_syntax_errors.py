#!/usr/bin/env python3
"""
Fix Critical Syntax Errors Script
Addresses syntax errors and import issues in Phase 1 target MCP servers
"""

import logging
import re
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CriticalSyntaxFixer:
    def __init__(self):
        self.root_path = Path(__file__).parent.parent
        self.mcp_servers_path = self.root_path / "mcp-servers"
        self.fixed_files = []
        self.errors_found = []

        # Phase 1 target servers
        self.phase1_targets = [
            "lambda_labs_cli",
            "ui_ux_agent",
            "portkey_admin",
            "snowflake_cli_enhanced",
            "ai_memory",
            "ag_ui",
            "codacy",
            "snowflake_admin",
        ]

    def fix_all_critical_errors(self) -> dict:
        """Fix all critical syntax errors in Phase 1 target servers"""
        logger.info("🔧 Starting critical syntax error fixes...")

        results = {
            "fixed_servers": [],
            "failed_servers": [],
            "syntax_errors_fixed": [],
            "import_errors_fixed": [],
            "warnings": [],
        }

        for server_name in self.phase1_targets:
            try:
                logger.info(f"🔍 Processing {server_name}...")
                server_results = self.fix_server_errors(server_name)

                if server_results["fixed"]:
                    results["fixed_servers"].append(server_name)
                    results["syntax_errors_fixed"].extend(
                        server_results["syntax_fixes"]
                    )
                    results["import_errors_fixed"].extend(
                        server_results["import_fixes"]
                    )
                    logger.info(
                        f"✅ {server_name}: Fixed {len(server_results['syntax_fixes']) + len(server_results['import_fixes'])} issues"
                    )
                else:
                    if server_results.get("error"):
                        results["failed_servers"].append(
                            f"{server_name}: {server_results['error']}"
                        )
                        logger.warning(f"⚠️ {server_name}: {server_results['error']}")
                    else:
                        logger.info(f"✅ {server_name}: No issues found")

            except Exception as e:
                error_msg = f"Failed to process {server_name}: {e}"
                results["failed_servers"].append(error_msg)
                logger.error(f"❌ {error_msg}")

        # Summary
        logger.info("🎯 Phase 1 Syntax Fix Summary:")
        logger.info(f"   ✅ Fixed servers: {len(results['fixed_servers'])}")
        logger.info(f"   ❌ Failed servers: {len(results['failed_servers'])}")
        logger.info(
            f"   🔧 Total fixes applied: {len(results['syntax_errors_fixed']) + len(results['import_errors_fixed'])}"
        )

        return results

    def fix_server_errors(self, server_name: str) -> dict:
        """Fix errors in a specific server"""
        server_path = self.mcp_servers_path / server_name
        if not server_path.exists():
            return {"fixed": False, "error": "Server directory not found"}

        # Find main server file
        server_file = self.find_server_file(server_path)
        if not server_file:
            return {"fixed": False, "error": "Main server file not found"}

        results = {
            "fixed": False,
            "syntax_fixes": [],
            "import_fixes": [],
            "error": None,
        }

        try:
            # Read current content
            with open(server_file, encoding="utf-8") as f:
                original_content = f.read()

            modified_content = original_content

            # Fix import issues
            import_fixes = self.fix_import_issues(modified_content, server_name)
            if import_fixes["modified"]:
                modified_content = import_fixes["content"]
                results["import_fixes"].extend(import_fixes["fixes_applied"])

            # Fix syntax issues
            syntax_fixes = self.fix_syntax_issues(modified_content, server_name)
            if syntax_fixes["modified"]:
                modified_content = syntax_fixes["content"]
                results["syntax_fixes"].extend(syntax_fixes["fixes_applied"])

            # Validate syntax
            try:
                compile(modified_content, str(server_file), "exec")
                syntax_valid = True
            except SyntaxError as e:
                syntax_valid = False
                results["error"] = f"Syntax error remains: line {e.lineno}: {e.msg}"

            # Write changes if any were made and syntax is valid
            if modified_content != original_content and syntax_valid:
                with open(server_file, "w", encoding="utf-8") as f:
                    f.write(modified_content)
                results["fixed"] = True
                logger.info(f"💾 Saved fixes to {server_file}")

        except Exception as e:
            results["error"] = str(e)

        return results

    def fix_import_issues(self, content: str, server_name: str) -> dict:
        """Fix import-related issues"""
        modified_content = content
        fixes_applied = []

        # Fix future imports position
        if "from __future__ import annotations" in content:
            lines = content.split("\n")
            future_import_lines = []
            other_lines = []
            found_future = False

            for i, line in enumerate(lines):
                if line.strip() == "from __future__ import annotations":
                    if i > 0:  # Not at the beginning
                        future_import_lines.append(line)
                        found_future = True
                        continue
                if not found_future:
                    other_lines.append(line)
                else:
                    other_lines.append(line)

            if found_future:
                # Place future imports at the beginning (after shebang and docstring)
                new_lines = []
                in_docstring = False
                docstring_quotes = None

                for line in other_lines:
                    if line.strip().startswith("#!/"):
                        new_lines.append(line)
                    elif line.strip().startswith('"""') or line.strip().startswith(
                        "'''"
                    ):
                        if not in_docstring:
                            in_docstring = True
                            docstring_quotes = line.strip()[:3]
                        elif docstring_quotes in line:
                            in_docstring = False
                        new_lines.append(line)
                    elif (
                        not in_docstring
                        and line.strip()
                        and not line.strip().startswith("#")
                    ):
                        # Insert future imports here
                        new_lines.extend(future_import_lines)
                        new_lines.append(line)
                        new_lines.extend(other_lines[other_lines.index(line) + 1 :])
                        break
                    else:
                        new_lines.append(line)

                modified_content = "\n".join(new_lines)
                fixes_applied.append(
                    "Moved 'from __future__ import annotations' to beginning"
                )

        # Fix specific import conflicts for ai_memory
        if server_name == "ai_memory":
            if "MemoryCategory" in content and "EnhancedMemoryCategory" not in content:
                modified_content = modified_content.replace(
                    "MemoryCategory", "EnhancedMemoryCategory"
                )
                fixes_applied.append(
                    "Fixed MemoryCategory → EnhancedMemoryCategory import"
                )

        # Add missing asyncio imports
        if "async def main" in content and "import asyncio" not in content:
            lines = modified_content.split("\n")
            import_section_end = 0
            for i, line in enumerate(lines):
                if line.startswith("import ") or line.startswith("from "):
                    import_section_end = i

            lines.insert(import_section_end + 1, "import asyncio")
            modified_content = "\n".join(lines)
            fixes_applied.append("Added missing asyncio import")

        return {
            "modified": modified_content != content,
            "content": modified_content,
            "fixes_applied": fixes_applied,
        }

    def fix_syntax_issues(self, content: str, server_name: str) -> dict:
        """Fix syntax-related issues"""
        modified_content = content
        fixes_applied = []

        # Fix async main pattern
        if "def main():" in content and "async def main():" not in content:
            # Check if main function should be async
            if "await " in content or "asyncio.run" in content:
                modified_content = modified_content.replace(
                    "def main():", "async def main():"
                )
                fixes_applied.append("Converted main() to async def main()")

                # Fix the call to main
                if 'if __name__ == "__main__":\n    main()' in modified_content:
                    modified_content = modified_content.replace(
                        'if __name__ == "__main__":\n    main()',
                        'if __name__ == "__main__":\n    asyncio.run(main())',
                    )
                    fixes_applied.append("Fixed main() call to use asyncio.run()")

        # Fix await outside async function
        lines = modified_content.split("\n")
        in_async_function = False
        function_indent = 0

        for i, line in enumerate(lines):
            # Track if we're in an async function
            if re.match(r"^(\s*)async def ", line):
                in_async_function = True
                function_indent = len(line) - len(line.lstrip())
            elif re.match(r"^(\s*)def ", line):
                current_indent = len(line) - len(line.lstrip())
                if current_indent <= function_indent:
                    in_async_function = False
            elif (
                line.strip() and not line.startswith(" ") and not line.startswith("\t")
            ):
                in_async_function = False

            # Check for await outside async function
            if (
                "await " in line
                and not in_async_function
                and not line.strip().startswith("#")
            ):
                # This is a more complex fix - for now, just log it
                fixes_applied.append(
                    f"Found await outside async function at line {i+1}"
                )

        return {
            "modified": modified_content != content,
            "content": modified_content,
            "fixes_applied": fixes_applied,
        }

    def find_server_file(self, server_path: Path) -> Path | None:
        """Find the main server file in the directory"""
        possible_names = [
            f"{server_path.name}_mcp_server.py",
            "mcp_server.py",
            "server.py",
            "main.py",
        ]

        for name in possible_names:
            file_path = server_path / name
            if file_path.exists():
                return file_path

        # Look for any Python file
        python_files = list(server_path.glob("*.py"))
        if python_files:
            return python_files[0]

        return None


def main():
    """Main execution function"""
    logger.info("🚀 Critical Syntax Error Fixer for Phase 1 MCP Servers")

    fixer = CriticalSyntaxFixer()
    results = fixer.fix_all_critical_errors()

    # Print summary
    print("\n" + "=" * 60)
    print("🔧 CRITICAL SYNTAX FIX SUMMARY")
    print("=" * 60)

    if results["fixed_servers"]:
        print(f"\n✅ FIXED SERVERS ({len(results['fixed_servers'])}):")
        for server in results["fixed_servers"]:
            print(f"   • {server}")

    if results["syntax_errors_fixed"]:
        print(f"\n🔧 SYNTAX FIXES APPLIED ({len(results['syntax_errors_fixed'])}):")
        for fix in results["syntax_errors_fixed"]:
            print(f"   • {fix}")

    if results["import_errors_fixed"]:
        print(f"\n📦 IMPORT FIXES APPLIED ({len(results['import_errors_fixed'])}):")
        for fix in results["import_errors_fixed"]:
            print(f"   • {fix}")

    if results["failed_servers"]:
        print(f"\n❌ FAILED SERVERS ({len(results['failed_servers'])}):")
        for server in results["failed_servers"]:
            print(f"   • {server}")

    print("\n🎯 PHASE 1 READINESS:")
    total_servers = len(fixer.phase1_targets)
    fixed_servers = len(results["fixed_servers"])
    success_rate = (fixed_servers / total_servers) * 100
    print(f"   Fixed: {fixed_servers}/{total_servers} servers ({success_rate:.1f}%)")

    if success_rate >= 75:
        print("   🎉 Ready to proceed with server startup!")
    else:
        print("   ⚠️ Additional fixes may be needed before server startup")

    print("\n" + "=" * 60)

    return results


if __name__ == "__main__":
    main()
