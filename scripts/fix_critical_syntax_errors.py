#!/usr/bin/env python3
"""
Fix Critical Syntax Errors in Sophia AI
Targets the specific syntax errors identified by ruff
"""

import re
import sys
from pathlib import Path


def fix_async_def_syntax_errors():
    """Fix the 'async def' syntax errors in for/with statements"""

    files_to_fix = [
        "backend/agents/infrastructure/sophia_infrastructure_agent.py",
        "backend/agents/specialized/marketing_analysis_agent.py",
        "backend/services/enhanced_unified_chat_service.py",
        "backend/services/sales_intelligence_service.py",
    ]

    fixed_count = 0

    for file_path in files_to_fix:
        path = Path(file_path)
        if not path.exists():
            print(f"⚠️  File not found: {file_path}")
            continue

        try:
            content = path.read_text()
            original_content = content

            # Fix pattern: for async def ... or with async def ...
            # These are invalid syntax and need to be refactored

            # Pattern 1: for async def method_name...
            content = re.sub(r"for\s+async\s+def\s+(\w+)", r"for \1", content)

            # Pattern 2: with async def method_name...
            content = re.sub(r"with\s+async\s+def\s+(\w+)", r"with \1", content)

            # Pattern 3: Missing colons after function definitions
            lines = content.split("\n")
            new_lines = []

            for i, line in enumerate(lines):
                # Check if line looks like it should end with a colon
                if re.match(
                    r"^\s*(async\s+)?def\s+\w+\s*\([^)]*\)\s*(->\s*[^:]+)?\s*$", line
                ):
                    if not line.rstrip().endswith(":"):
                        line = line.rstrip() + ":"
                        print(f"  Added missing colon at line {i+1}")

                # Fix indentation after for/if/while/etc without colon
                if re.match(
                    r"^\s*(if|elif|else|for|while|try|except|finally|with|class)\s+.*[^:]$",
                    line,
                ):
                    if not line.rstrip().endswith(":"):
                        line = line.rstrip() + ":"
                        print(f"  Added missing colon at line {i+1}")

                new_lines.append(line)

            content = "\n".join(new_lines)

            if content != original_content:
                path.write_text(content)
                print(f"✅ Fixed {file_path}")
                fixed_count += 1
            else:
                print(f"ℹ️  No changes needed for {file_path}")

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")

    return fixed_count


def fix_specific_syntax_errors():
    """Fix specific known syntax errors"""

    fixes = [
        # File path, line number, old pattern, new pattern
        (
            "backend/agents/infrastructure/sophia_infrastructure_agent.py",
            384,
            r"for async def get_deployment_status",
            "async def get_deployment_status",
        ),
        (
            "backend/agents/infrastructure/sophia_infrastructure_agent.py",
            399,
            r"^\s*$",  # Empty line that should have a colon
            ":",
        ),
        (
            "backend/agents/specialized/marketing_analysis_agent.py",
            302,
            r"with async def generate_content",
            "async def generate_content",
        ),
    ]

    fixed_count = 0

    for file_path, line_num, old_pattern, new_text in fixes:
        path = Path(file_path)
        if not path.exists():
            print(f"⚠️  File not found: {file_path}")
            continue

        try:
            lines = path.read_text().split("\n")

            if line_num <= len(lines):
                line_idx = line_num - 1
                old_line = lines[line_idx]

                if re.search(old_pattern, old_line):
                    # Apply the fix
                    if old_pattern == r"^\s*$":
                        # Special case for empty lines
                        indent = len(lines[line_idx - 1]) - len(
                            lines[line_idx - 1].lstrip()
                        )
                        lines[line_idx] = " " * indent + new_text
                    else:
                        lines[line_idx] = re.sub(old_pattern, new_text, old_line)

                    # Write back
                    path.write_text("\n".join(lines))
                    print(f"✅ Fixed {file_path}:{line_num}")
                    fixed_count += 1
                else:
                    print(f"ℹ️  Pattern not found at {file_path}:{line_num}")

        except Exception as e:
            print(f"❌ Error fixing {file_path}:{line_num}: {e}")

    return fixed_count


def main():
    """Main entry point"""
    print("=" * 80)
    print("🔧 FIXING CRITICAL SYNTAX ERRORS IN SOPHIA AI")
    print("=" * 80)

    # Fix async def syntax errors
    print("\n📍 Fixing async def syntax errors...")
    async_fixed = fix_async_def_syntax_errors()

    # Fix specific known errors
    print("\n📍 Fixing specific syntax errors...")
    specific_fixed = fix_specific_syntax_errors()

    total_fixed = async_fixed + specific_fixed

    print("\n" + "=" * 80)
    print(f"✅ Total fixes applied: {total_fixed}")
    print("=" * 80)

    if total_fixed > 0:
        print("\n🎯 Next steps:")
        print("1. Run 'ruff check .' to verify remaining issues")
        print("2. Run 'ruff check . --fix' to auto-fix additional issues")
        print("3. Check the AI Code Quality MCP Server at port 9025")

    return 0 if total_fixed > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
