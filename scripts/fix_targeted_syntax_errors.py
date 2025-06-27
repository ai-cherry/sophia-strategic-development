#!/usr/bin/env python3
"""
Fix specific syntax errors in files with known patterns.
Focuses on the most common issues found in the syntax validation report.
"""

import re
from pathlib import Path
from typing import List, Tuple


def fix_file_syntax(file_path: Path) -> Tuple[bool, List[str]]:
    """Fix syntax errors in a single file."""
    fixes = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Fix 1: Remove periods at the end of lines with colons
        # Pattern: try:. -> try:
        content = re.sub(r":\.\s*\n", ":\n", content)
        if content != original_content:
            fixes.append("Fixed colon-period pattern (:. -> :)")
            original_content = content

        # Fix 2: Fix method definitions with periods
        # Pattern: def method():. -> def method():
        content = re.sub(r"(def\s+\w+\([^)]*\)):\.(.*)", r"\1:\2", content)
        if content != original_content:
            fixes.append("Fixed method definitions with periods")
            original_content = content

        # Fix 3: Fix statements ending with periods (excluding strings)
        # This is more complex, need to process line by line
        lines = content.split("\n")
        fixed_lines = []

        for i, line in enumerate(lines):
            # Skip comments and strings
            if line.strip().startswith("#"):
                fixed_lines.append(line)
                continue

            # Check if line contains string literals
            if (
                '"""' in line
                or "'''" in line
                or ('"' in line and line.count('"') % 2 == 0)
                or ("'" in line and line.count("'") % 2 == 0)
            ):
                # More complex string detection needed, skip for safety
                fixed_lines.append(line)
                continue

            # Fix common patterns
            original_line = line

            # Remove trailing periods from statements
            if (
                line.strip()
                and line.strip()[-1] == "."
                and not line.strip().endswith("...")
            ):
                # Check if it's not a valid method call or attribute access
                if not re.search(r"\)[.]$", line.strip()) and not re.search(
                    r"\w+[.]$", line.strip()
                ):
                    line = line.rstrip().rstrip(".")
                    if line != original_line:
                        fixes.append(f"Line {i+1}: Removed trailing period")

            # Fix specific patterns
            # Pattern: if condition:. -> if condition:
            line = re.sub(
                r"^(\s*)(if|elif|else|try|except|finally|while|for|with|class)\s+(.*?):\.$",
                r"\1\2 \3:",
                line,
            )

            # Pattern: return value. -> return value
            if re.match(r"^\s*return\s+.*\.$", line) and "..." not in line:
                line = line.rstrip(".")

            # Pattern: variable = value. -> variable = value
            if re.match(r"^\s*\w+\s*=\s*.*\.$", line) and "..." not in line:
                line = line.rstrip(".")

            # Pattern: method(). -> method()
            line = re.sub(r"\(\)\.\s*$", "()", line)

            # Pattern: list = [. -> list = [
            line = re.sub(r"([\[\{])\.\s*$", r"\1", line)

            if line != original_line and original_line not in fixes:
                fixes.append(f"Line {i+1}: Fixed syntax")

            fixed_lines.append(line)

        content = "\n".join(fixed_lines)

        # Fix 4: Fix docstring placement issues
        # Pattern: def func():."""Docstring""" -> def func():\n    """Docstring"""
        content = re.sub(
            r'^(\s*)(def\s+\w+\([^)]*\)):\.?"""([^"]+)"""',
            r'\1\2:\n\1    """\3"""',
            content,
            flags=re.MULTILINE,
        )

        # Fix 5: Fix missing newlines in docstrings
        content = re.sub(r'"""([^"]+)"""(\w)', r'"""\1"""\n\2', content)

        # Fix 6: Fix specific problematic patterns
        # Pattern: def __init__(self):."Initialize... -> def __init__(self):\n    """Initialize...
        content = re.sub(
            r'(def\s+__init__\([^)]*\)):\.?"*([^"]*)"*',
            r'\1:\n        """\2"""',
            content,
        )

        if content != original_content or fixes:
            # Write the fixed content
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True, fixes

        return False, []

    except Exception as e:
        return False, [f"Error: {str(e)}"]


def main():
    """Main function to fix syntax errors."""
    print("🔧 Fixing Targeted Syntax Errors")
    print("=" * 60)

    # List of files with known syntax errors to fix
    target_files = [
        "backend/agents/core/llm_client.py",
        "backend/agents/core/mcp_crew_orchestrator.py",
        "backend/agents/specialized/agent_implementations.py",
        "backend/agents/specialized/crm_sync_agent.py",
        "backend/agents/specialized/executive_agent.py",
        "backend/agents/specialized/research_agent.py",
        "backend/app/dependencies.py",
        "backend/codebase_awareness/code_ingestion.py",
        "backend/core/secret_manager.py",
        "backend/core/deployment_oversight_system.py",
        "backend/database/schema_migration_system.py",
        "backend/imports/data_import_api_feeds.py",
        "backend/integrations/estuary_integration.py",
        "backend/integrations/apify_integration.py",
        "backend/integrations/apollo_integration.py",
        "backend/integrations/estuary_flow_integration.py",
        "backend/integrations/hubspot/hubspot_integration.py",
        "backend/integrations/huggingface_mcp.py",
        "backend/integrations/openrouter_integration.py",
        "backend/integrations/slack/admin_migration.py",
        "backend/integrations/vercel_integration.py",
        "backend/knowledge/hybrid_rag_manager.py",
        "backend/knowledge/knowledge_base_stub.py",
        "backend/knowledge/workflow_manager.py",
        "backend/mcp/ai_memory_auto_discovery.py",
        "backend/mcp/ai_memory_mcp_server.py",
        "backend/mcp/costar_mcp_server.py",
        "backend/monitoring/enhanced_monitoring.py",
        "backend/monitoring/sophia_monitoring.py",
        "backend/pipelines/gong_snowflake_pipeline.py",
        "scripts/dev/simple_ai_memory_test.py",
        "scripts/dev/test_infrastructure.py",
        "scripts/sync_validated_secrets_to_esc.py",
        "examples/memory_manager_client.py",
        "examples/gong_mcp_client.py",
    ]

    fixed_count = 0

    for file_path_str in target_files:
        file_path = Path(file_path_str)

        if file_path.exists():
            print(f"\n📄 Processing {file_path}...")
            fixed, fixes = fix_file_syntax(file_path)

            if fixed:
                fixed_count += 1
                print(f"✅ Fixed {file_path}")
                for fix in fixes:
                    print(f"   - {fix}")
            else:
                if fixes:  # Error occurred
                    print(f"❌ Error in {file_path}: {fixes[0]}")
                else:
                    print(f"ℹ️  No fixes needed for {file_path}")

    print(f"\n📊 Summary: Fixed {fixed_count} files")
    print("\n💡 Run syntax validation again to check for remaining issues")


if __name__ == "__main__":
    main()
