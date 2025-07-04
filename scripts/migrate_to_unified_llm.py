#!/usr/bin/env python3
"""
Automated migration script for UnifiedLLMService
Migrates files from old LLM services to the new unified service
"""

import argparse
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# Migration patterns for different services
MIGRATION_PATTERNS = [
    # Import replacements
    (
        r"from backend\.services\.smart_ai_service import SmartAIService",
        "from backend.services.unified_llm_service import get_unified_llm_service, TaskType",
    ),
    (
        r"from backend\.services\.portkey_gateway import PortkeyGateway",
        "from backend.services.unified_llm_service import get_unified_llm_service, TaskType",
    ),
    (
        r"from backend\.services\.simplified_portkey_service import SimplifiedPortkeyService",
        "from backend.services.unified_llm_service import get_unified_llm_service, TaskType",
    ),
    (
        r"from backend\.services\.enhanced_portkey_orchestrator import EnhancedPortkeyOrchestrator",
        "from backend.services.unified_llm_service import get_unified_llm_service, TaskType",
    ),
    # Import statement replacements
    (
        r"import backend\.services\.smart_ai_service",
        "import backend.services.unified_llm_service",
    ),
    # Class instantiation replacements
    (r"SmartAIService\(\)", "await get_unified_llm_service()"),
    (r"PortkeyGateway\(\)", "await get_unified_llm_service()"),
    (r"SimplifiedPortkeyService\(\)", "await get_unified_llm_service()"),
    # Variable name replacements
    (r"smart_ai_service", "llm_service"),
    (r"portkey_gateway", "llm_service"),
    (r"portkey_service", "llm_service"),
]

# Task type mappings for method calls
TASK_TYPE_MAPPINGS = {
    "generate_response": "TaskType.CHAT_CONVERSATION",
    "analyze_code": "TaskType.CODE_ANALYSIS",
    "generate_code": "TaskType.CODE_GENERATION",
    "business_analysis": "TaskType.BUSINESS_INTELLIGENCE",
    "sql_generation": "TaskType.SQL_GENERATION",
    "data_analysis": "TaskType.DATA_ANALYSIS",
}

# Files to migrate (from comprehensive search)
FILES_TO_MIGRATE = [
    "backend/agents/core/langgraph_agent_base.py",
    "backend/agents/infrastructure/sophia_infrastructure_agent.py",
    "backend/agents/specialized/asana_project_intelligence_agent.py",
    "backend/agents/specialized/marketing_analysis_agent.py",
    "backend/agents/specialized/sales_intelligence_agent.py",
    "backend/agents/specialized/sales_intelligence_agent_core.py",
    "backend/agents/specialized/sales_intelligence_agent_handlers.py",
    "backend/app/unified_fastapi_app.py",
    "backend/integrations/portkey_gateway_service.py",
    "backend/services/code_modification_service.py",
    "backend/services/enhanced_unified_chat_service.py",
    "backend/services/enhanced_unified_intelligence_service.py",
    "backend/services/intelligent_data_discovery_service.py",
    "backend/services/mcp_orchestration_service.py",
    "backend/services/simplified_unified_intelligence_service.py",
    "backend/services/sophia_intent_engine.py",
    "backend/services/unified_intelligence_service.py",
    "backend/workflows/enhanced_langgraph_patterns.py",
    "docs/CURRENT_LLM_USAGE_ANALYSIS.md",
    "docs/PHASE_2_FOUNDATION_IMPLEMENTATION_PLAN.md",
    "docs/PHASE_3_UNIFIED_LLM_MIGRATION_PLAN.md",
    "docs/SOPHIA_AI_UNIFIED_LLM_STRATEGY.md",
    "docs/UNIFIED_CHAT_TECHNICAL_IMPLEMENTATION.md",
    "docs/UNIFIED_LLM_SERVICE_SUMMARY.md",
    "docs/UNIFIED_LLM_STRATEGY_IMPLEMENTATION.md",
    "docs/architecture/CIRCULAR_DEPENDENCY_MIGRATION.md",
    "docs/architecture/SERVICE_CONSOLIDATION_PLAN.md",
    "scripts/implement_critical_refactoring.py",
    "scripts/mcp_ecosystem_validator.py",
    "scripts/validate_n8n_enterprise_readiness.py",
]


class UnifiedLLMMigrator:
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.backup_dir = Path(
            f"backups/llm_migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        self.changes_made = []
        self.errors = []

    def backup_file(self, file_path: Path) -> bool:
        """Backup a file before modification"""
        if not self.dry_run:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            backup_path = self.backup_dir / file_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, backup_path)
            return True
        return False

    def migrate_file(self, file_path: str) -> dict[str, Any]:
        """Migrate a single file"""
        path = Path(file_path)
        if not path.exists():
            self.errors.append(f"File not found: {file_path}")
            return {"status": "error", "file": file_path, "error": "File not found"}

        try:
            content = path.read_text()
            original_content = content
            changes = []

            # Apply migration patterns
            for old_pattern, new_pattern in MIGRATION_PATTERNS:
                matches = re.findall(old_pattern, content)
                if matches:
                    content = re.sub(old_pattern, new_pattern, content)
                    changes.append(
                        f"Replaced {len(matches)} occurrences of '{old_pattern}'"
                    )

            # Handle method call migrations (more complex)
            content = self._migrate_method_calls(content, changes)

            # Only write if changes were made
            if content != original_content:
                if not self.dry_run:
                    self.backup_file(path)
                    path.write_text(content)

                self.changes_made.append({"file": file_path, "changes": changes})

                return {"status": "modified", "file": file_path, "changes": changes}
            else:
                return {"status": "unchanged", "file": file_path}

        except Exception as e:
            self.errors.append(f"Error processing {file_path}: {str(e)}")
            return {"status": "error", "file": file_path, "error": str(e)}

    def _migrate_method_calls(self, content: str, changes: list[str]) -> str:
        """Migrate method calls to the new pattern"""
        # Pattern for smart_ai.generate_response(request)
        pattern = r"(\w+)\.generate_response\s*\(\s*([^)]+)\s*\)"

        def replace_method_call(match):
            var_name = match.group(1)
            args = match.group(2)

            # Extract the request object
            if "request" in args:
                # Assume request has prompt, task_type, etc.
                return f"""async for chunk in {var_name}.complete(
    prompt={args}.prompt if hasattr({args}, 'prompt') else {args}.get('prompt', ''),
    task_type=TaskType.BUSINESS_INTELLIGENCE,  # TODO: Set appropriate task type
    stream=True
)"""
            else:
                return f"""async for chunk in {var_name}.complete(
    prompt={args},
    task_type=TaskType.CHAT_CONVERSATION,  # TODO: Set appropriate task type
    stream=True
)"""

        new_content = re.sub(pattern, replace_method_call, content)
        if new_content != content:
            changes.append("Migrated method calls to new pattern")

        return new_content

    def run_migration(self, files: Optional[list[str]] = None):
        """Run the migration on specified files or all files"""
        if files is None:
            files = FILES_TO_MIGRATE

        print(
            f"{'DRY RUN: ' if self.dry_run else ''}Starting UnifiedLLMService migration..."
        )
        print(f"Processing {len(files)} files...")
        print("=" * 60)

        results = {"modified": [], "unchanged": [], "errors": []}

        for file_path in files:
            result = self.migrate_file(file_path)
            status = result["status"]
            if status == "error":
                results["errors"].append(result)
            else:
                results[status].append(result)

            # Print progress
            status_symbol = {"modified": "✓", "unchanged": "-", "error": "✗"}[status]

            print(f"{status_symbol} {file_path}")
            if status == "modified" and self.dry_run:
                for change in result["changes"]:
                    print(f"  → {change}")

        # Print summary
        print("\n" + "=" * 60)
        print("Migration Summary:")
        print(f"  Modified: {len(results['modified'])} files")
        print(f"  Unchanged: {len(results['unchanged'])} files")
        print(f"  Errors: {len(results['errors'])} files")

        if results["errors"]:
            print("\nErrors:")
            for error in results["errors"]:
                print(f"  ✗ {error['file']}: {error.get('error', 'Unknown error')}")

        if not self.dry_run and results["modified"]:
            print(f"\nBackups saved to: {self.backup_dir}")

            # Create migration report
            report_path = self.backup_dir / "migration_report.txt"
            with open(report_path, "w") as f:
                f.write("UnifiedLLMService Migration Report\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"Date: {datetime.now().isoformat()}\n")
                f.write(f"Files modified: {len(results['modified'])}\n\n")

                for result in results["modified"]:
                    f.write(f"\n{result['file']}:\n")
                    for change in result["changes"]:
                        f.write(f"  - {change}\n")

            print(f"Migration report saved to: {report_path}")

        return results


def main():
    parser = argparse.ArgumentParser(description="Migrate to UnifiedLLMService")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Show what would be changed without modifying files",
    )
    parser.add_argument(
        "--apply", action="store_true", help="Actually apply the changes"
    )
    parser.add_argument("--files", nargs="+", help="Specific files to migrate")

    args = parser.parse_args()

    # If --apply is specified, turn off dry-run
    if args.apply:
        args.dry_run = False

    migrator = UnifiedLLMMigrator(dry_run=args.dry_run)
    results = migrator.run_migration(files=args.files)

    # Return non-zero exit code if there were errors
    if results["errors"]:
        return 1
    return 0


if __name__ == "__main__":
    exit(main())
