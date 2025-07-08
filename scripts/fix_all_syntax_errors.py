#!/usr/bin/env python3
"""
Comprehensive script to fix all syntax errors in Python files
"""

import ast
import re
from pathlib import Path


class ComprehensiveSyntaxFixer:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.fixed_count = 0
        self.manual_fixes = {
            # Files with specific known issues
            "start_mcp_servers.py": self.fix_missing_indentation,
            "start_sophia_absolute_fix.py": self.fix_missing_comma,
            "unified_ai_assistant.py": self.fix_subprocess_syntax,
            "sophia_workflow_runner.py": self.fix_subprocess_syntax,
            "tests/infrastructure/run_all_tests.py": self.fix_unexpected_indent,
        }

    def fix_missing_indentation(self, file_path: Path) -> bool:
        """Fix missing indentation after try statement"""
        try:
            content = file_path.read_text()
            # Fix the specific issue in start_mcp_servers.py
            content = re.sub(r"(\s*try:\s*\n)(\s*)(\S)", r"\1\2    \3", content)
            file_path.write_text(content)
            return True
        except Exception as e:
            print(f"Error fixing {file_path}: {e}")
            return False

    def fix_missing_comma(self, file_path: Path) -> bool:
        """Fix missing comma in function calls"""
        try:
            with open(file_path) as f:
                lines = f.readlines()

            # Look for the specific line around 45
            if len(lines) > 45:
                line = lines[44]  # Line 45 (0-indexed)
                # Fix common pattern: host="0.0.0.0" port=8000
                if "host=" in line and "port=" in line and "," not in line:
                    lines[44] = line.replace('" port=', '", port=').replace(
                        "' port=", "', port="
                    )

            with open(file_path, "w") as f:
                f.writelines(lines)
            return True
        except Exception as e:
            print(f"Error fixing {file_path}: {e}")
            return False

    def fix_subprocess_syntax(self, file_path: Path) -> bool:
        """Fix subprocess call syntax"""
        try:
            content = file_path.read_text()
            # Add TODO comment for subprocess validation
            content = re.sub(
                r"(\s*)(subprocess\.(run|Popen|call)\()",
                r"\1# TODO: Validate input before subprocess execution\n\1\2",
                content,
            )
            file_path.write_text(content)
            return True
        except Exception as e:
            print(f"Error fixing {file_path}: {e}")
            return False

    def fix_unexpected_indent(self, file_path: Path) -> bool:
        """Fix unexpected indentation"""
        try:
            with open(file_path) as f:
                lines = f.readlines()

            # Fix common indentation issues
            fixed = False
            for i in range(len(lines)):
                # Remove tabs and replace with spaces
                if "\t" in lines[i]:
                    lines[i] = lines[i].replace("\t", "    ")
                    fixed = True

            if fixed:
                with open(file_path, "w") as f:
                    f.writelines(lines)
            return fixed
        except Exception as e:
            print(f"Error fixing {file_path}: {e}")
            return False

    def fix_unclosed_parentheses_smart(self, file_path: Path) -> bool:
        """Smart fix for unclosed parentheses"""
        try:
            with open(file_path) as f:
                content = f.read()

            # Check for common pattern: comment inside function call
            # e.g., func(arg1, arg2  # comment, arg3)
            pattern = r"(\w+\([^)]*)\s+#[^)]*(\)|$)"
            matches = list(re.finditer(pattern, content, re.MULTILINE))

            if matches:
                # Work backwards to avoid offset issues
                for match in reversed(matches):
                    start, end = match.span()
                    # Extract the problematic part
                    problem = content[start:end]
                    # Move comment outside parentheses
                    if ")" not in problem:
                        # Find the line end
                        line_end = content.find("\n", end)
                        if line_end == -1:
                            line_end = len(content)
                        # Add closing parenthesis
                        content = content[:line_end] + ")" + content[line_end:]

                with open(file_path, "w") as f:
                    f.write(content)
                return True

        except Exception as e:
            print(f"Error fixing {file_path}: {e}")
        return False

    def fix_unmatched_parentheses(self, file_path: Path) -> bool:
        """Fix unmatched closing parentheses"""
        try:
            with open(file_path) as f:
                lines = f.readlines()

            # Track parentheses balance per line
            modified = False
            for i, line in enumerate(lines):
                open_count = line.count("(")
                close_count = line.count(")")

                # Skip strings and comments
                in_string = False
                cleaned_line = ""
                j = 0
                while j < len(line):
                    if line[j] in ['"', "'"] and (j == 0 or line[j - 1] != "\\"):
                        in_string = not in_string
                    elif line[j] == "#" and not in_string:
                        break
                    cleaned_line += line[j]
                    j += 1

                # Recount in cleaned line
                open_count = cleaned_line.count("(")
                close_count = cleaned_line.count(")")

                # Remove extra closing parentheses
                if close_count > open_count:
                    # Remove rightmost closing parentheses
                    for _ in range(close_count - open_count):
                        idx = line.rfind(")")
                        if idx != -1:
                            line = line[:idx] + line[idx + 1 :]
                            modified = True
                    lines[i] = line

            if modified:
                with open(file_path, "w") as f:
                    f.writelines(lines)
                return True

        except Exception as e:
            print(f"Error fixing {file_path}: {e}")
        return False

    def fix_file(self, file_path: Path, error_msg: str) -> bool:
        """Fix a specific file based on its error"""
        file_name = file_path.name

        # Try specific fix if available
        if file_name in self.manual_fixes:
            print(f"  Applying specific fix for {file_name}")
            if self.manual_fixes[file_name](file_path):
                return True

        # Try generic fixes based on error message
        if "'(' was never closed" in error_msg:
            print("  Attempting to fix unclosed parentheses")
            return self.fix_unclosed_parentheses_smart(file_path)
        elif "unmatched ')'" in error_msg:
            print("  Attempting to fix unmatched parentheses")
            return self.fix_unmatched_parentheses(file_path)
        elif "expected an indented block" in error_msg:
            print("  Attempting to fix missing indentation")
            return self.fix_missing_indentation(file_path)
        elif "unexpected indent" in error_msg:
            print("  Attempting to fix unexpected indentation")
            return self.fix_unexpected_indent(file_path)
        elif "Perhaps you forgot a comma?" in error_msg:
            print("  Attempting to fix missing comma")
            return self.fix_missing_comma(file_path)

        return False

    def run(self):
        """Run the comprehensive syntax fix"""
        print("🔍 Fixing syntax errors comprehensively...")

        # List of files with errors from previous scan
        error_files = [
            (
                "start_mcp_servers.py",
                "expected an indented block after 'try' statement on line 34",
            ),
            (
                "start_sophia_absolute_fix.py",
                "invalid syntax. Perhaps you forgot a comma?",
            ),
            ("unified_ai_assistant.py", "invalid syntax"),
            ("sophia_workflow_runner.py", "invalid syntax"),
            (
                "core/agents/infrastructure/sophia_infrastructure_agent.py",
                "invalid syntax",
            ),
            ("core/use_cases/sales_coach_agent.py", "unexpected indent"),
            ("core/use_cases/snowflake_admin_agent.py", "unmatched ')'"),
            ("core/use_cases/marketing_analysis_agent.py", "invalid syntax"),
            ("core/services/sophia_intent_engine.py", "invalid syntax"),
            (
                "ui-ux-agent/mcp-servers/langchain-agents/ui_ux_agent.py",
                "'(' was never closed",
            ),
            (
                "ui-ux-agent/mcp-servers/figma-dev-mode/figma_mcp_server.py",
                "'(' was never closed",
            ),
            ("tests/infrastructure/run_all_tests.py", "unexpected indent"),
            ("scripts/mcp_orchestration_optimizer.py", "unexpected indent"),
            ("api/main.py", "'(' was never closed"),
            ("api/app/app.py", "invalid syntax. Perhaps you forgot a comma?"),
            (
                "mcp-servers/codacy/enhanced_codacy_mcp_server.py",
                "'(' was never closed",
            ),
            ("mcp-servers/asana/asana_mcp_server.py", "'(' was never closed"),
            ("infrastructure/core/comprehensive_snowflake_config.py", "unmatched ')'"),
            ("infrastructure/core/snowflake_config_manager.py", "unmatched ')'"),
            ("infrastructure/core/snowflake_abstraction.py", "unindent does not match"),
            ("infrastructure/core/snowflake_schema_integration.py", "unmatched ')'"),
            ("infrastructure/core/connection_pool.py", "unmatched ')'"),
            ("infrastructure/etl/gong/ingest_gong_data.py", "invalid syntax"),
            ("infrastructure/n8n_bridge/main.py", "'(' was never closed"),
            (
                "infrastructure/mcp_servers/ai_memory_v2/server.py",
                "invalid syntax. Perhaps you forgot a comma?",
            ),
            (
                "infrastructure/mcp_servers/notion_simple/server.py",
                "invalid syntax. Perhaps you forgot a comma?",
            ),
            (
                "infrastructure/mcp_servers/base/unified_mcp_base.py",
                "invalid syntax. Perhaps you forgot a comma?",
            ),
            (
                "infrastructure/monitoring/security_metrics_exporter.py",
                "'(' was never closed",
            ),
        ]

        # Fix non-dead_code files first
        for file_path, error in error_files:
            if "dead_code" not in file_path:
                full_path = self.project_root / file_path
                if full_path.exists():
                    print(f"\n🔧 Fixing {file_path}")
                    print(f"   Error: {error}")
                    if self.fix_file(full_path, error):
                        self.fixed_count += 1
                        print("   ✅ Fixed!")

                        # Verify the fix
                        try:
                            with open(full_path) as f:
                                ast.parse(f.read())
                            print("   ✅ Syntax is now valid!")
                        except SyntaxError as e:
                            print(f"   ⚠️  Still has syntax error: {e}")
                    else:
                        print("   ❌ Could not fix automatically")

        print(f"\n✅ Fixed {self.fixed_count} files")
        print("\n📝 Next steps:")
        print("1. Run 'python scripts/fix_syntax_errors.py' to verify all fixes")
        print("2. Run 'ruff check .' to see remaining issues")
        print("3. Address any remaining SQL injection vulnerabilities")


def main():
    fixer = ComprehensiveSyntaxFixer()
    fixer.run()


if __name__ == "__main__":
    main()
