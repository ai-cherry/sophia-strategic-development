#!/usr/bin/env python3
"""
Automated migration script to refactor Snowflake usage to CortexGateway.
Handles common patterns and generates migration patches.
"""

import re
import shutil
from datetime import datetime
from pathlib import Path

# Migration patterns
MIGRATION_PATTERNS = [
    # Direct connection pattern
    {
        "pattern": re.compile(r"snowflake\.connector\.connect\s*\([^)]+\)"),
        "replacement": "get_gateway()",
        "imports_add": ["from core.infra.cortex_gateway import get_gateway"],
        "imports_remove": ["import snowflake.connector"],
    },
    # SnowflakeCortexService pattern
    {
        "pattern": re.compile(r"SnowflakeCortexService\s*\(\s*\)"),
        "replacement": "get_gateway()",
        "imports_add": ["from core.infra.cortex_gateway import get_gateway"],
        "imports_remove": [
            "from shared.utils.snowflake_cortex_service import SnowflakeCortexService"
        ],
    },
    # Direct Cortex SQL patterns
    {
        "pattern": re.compile(r"SELECT\s+SNOWFLAKE\.CORTEX\.COMPLETE\s*\([^)]+\)"),
        "replacement": "await gateway.complete(prompt, model)",
        "needs_await": True,
    },
    {
        "pattern": re.compile(r"SELECT\s+SNOWFLAKE\.CORTEX\.EMBED_TEXT\s*\([^)]+\)"),
        "replacement": "await gateway.embed(text, model)",
        "needs_await": True,
    },
]


class SnowflakeMigrator:
    """Automated migrator for Snowflake to CortexGateway."""

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.backup_dir = Path("migration_backups") / datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )
        self.migration_log = []

    def backup_file(self, file_path: Path):
        """Create backup of file before migration."""
        if not self.dry_run:
            backup_path = self.backup_dir / file_path.relative_to(".")
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, backup_path)

    def add_imports(self, content: str, imports_to_add: list[str]) -> str:
        """Add required imports to file."""
        lines = content.splitlines()

        # Find where to insert imports (after existing imports)
        import_end = 0
        for i, line in enumerate(lines):
            if line.startswith("import ") or line.startswith("from "):
                import_end = i + 1
            elif import_end > 0 and line.strip() and not line.startswith("#"):
                break

        # Add new imports
        for imp in imports_to_add:
            if imp not in content:
                lines.insert(import_end, imp)
                import_end += 1

        return "\n".join(lines)

    def remove_imports(self, content: str, imports_to_remove: list[str]) -> str:
        """Remove deprecated imports."""
        lines = content.splitlines()
        filtered_lines = []

        for line in lines:
            should_keep = True
            for imp in imports_to_remove:
                if imp in line:
                    should_keep = False
                    break
            if should_keep:
                filtered_lines.append(line)

        return "\n".join(filtered_lines)

    def migrate_direct_connections(self, content: str) -> tuple[str, list[str]]:
        """Migrate direct snowflake.connector.connect() calls."""
        changes = []

        # Pattern 1: conn = snowflake.connector.connect(...)
        pattern = re.compile(r"(\w+)\s*=\s*snowflake\.connector\.connect\s*\([^)]+\)")

        def replace_connection(match):
            var_name = match.group(1)
            changes.append(f"Replaced connection: {var_name}")
            return f"# Migrated to CortexGateway\ngateway = get_gateway()\n# Original: {match.group(0)}"

        content = pattern.sub(replace_connection, content)

        # Pattern 2: cursor.execute() calls
        cursor_pattern = re.compile(r"(\w+)\.cursor\(\)\.execute\s*\(([^)]+)\)")

        def replace_cursor_execute(match):
            sql_part = match.group(2)
            changes.append("Replaced cursor.execute()")
            return f"await gateway.execute_sql({sql_part})"

        content = cursor_pattern.sub(replace_cursor_execute, content)

        return content, changes

    def migrate_cortex_functions(self, content: str) -> tuple[str, list[str]]:
        """Migrate Cortex function calls to gateway methods."""
        changes = []

        # COMPLETE function
        complete_pattern = re.compile(
            r'SELECT\s+SNOWFLAKE\.CORTEX\.COMPLETE\s*\(\s*[\'"]([^\'\"]+)[\'\"]\s*,\s*([^)]+)\)',
            re.IGNORECASE,
        )

        def replace_complete(match):
            model = match.group(1)
            prompt = match.group(2)
            changes.append("Migrated CORTEX.COMPLETE")
            return f'await gateway.complete({prompt}, model="{model}")'

        content = complete_pattern.sub(replace_complete, content)

        # EMBED_TEXT function
        embed_pattern = re.compile(
            r'SELECT\s+SNOWFLAKE\.CORTEX\.EMBED_TEXT(?:_768)?\s*\(\s*[\'"]([^\'\"]+)[\'\"]\s*,\s*([^)]+)\)',
            re.IGNORECASE,
        )

        def replace_embed(match):
            model = match.group(1)
            text = match.group(2)
            changes.append("Migrated CORTEX.EMBED_TEXT")
            return f'await gateway.embed({text}, model="{model}")'

        content = embed_pattern.sub(replace_embed, content)

        return content, changes

    def migrate_service_usage(self, content: str) -> tuple[str, list[str]]:
        """Migrate SnowflakeCortexService usage."""
        changes = []

        # Service instantiation
        service_pattern = re.compile(
            r"self\.(\w+)\s*=\s*SnowflakeCortexService\s*\(\s*\)"
        )

        def replace_service(match):
            attr_name = match.group(1)
            changes.append(f"Migrated service: self.{attr_name}")
            return f"self.{attr_name} = get_gateway()"

        content = service_pattern.sub(replace_service, content)

        # Method calls
        method_patterns = [
            (r"\.complete_text\s*\(", ".complete("),
            (r"\.generate_embedding\s*\(", ".embed("),
            (r"\.batch_generate_embeddings\s*\(", ".batch_embed("),
            (r"\.analyze_sentiment\s*\(", ".sentiment("),
        ]

        for old_method, new_method in method_patterns:
            pattern = re.compile(old_method)
            if pattern.search(content):
                content = pattern.sub(new_method, content)
                changes.append(f"Migrated method: {old_method} -> {new_method}")

        return content, changes

    def add_async_await(self, content: str) -> str:
        """Add async/await where needed."""
        # Simple heuristic: if we have gateway calls, make functions async
        if "await gateway." in content:
            # Find function definitions and make them async
            func_pattern = re.compile(r"^(\s*)def\s+(\w+)\s*\(", re.MULTILINE)

            def make_async(match):
                indent = match.group(1)
                func_name = match.group(2)
                # Skip if already async
                if f"async def {func_name}" in content:
                    return match.group(0)
                return f"{indent}async def {func_name}("

            content = func_pattern.sub(make_async, content)

        return content

    def migrate_file(self, file_path: Path) -> dict[str, any] | None:
        """Migrate a single Python file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                original_content = f.read()

            # Skip if already migrated
            if "from core.infra.cortex_gateway import get_gateway" in original_content:
                return None

            # Skip if no Snowflake usage
            if (
                "snowflake" not in original_content.lower()
                and "cortex" not in original_content.lower()
            ):
                return None

            content = original_content
            all_changes = []

            # Apply migrations
            content, changes = self.migrate_direct_connections(content)
            all_changes.extend(changes)

            content, changes = self.migrate_cortex_functions(content)
            all_changes.extend(changes)

            content, changes = self.migrate_service_usage(content)
            all_changes.extend(changes)

            # Add async/await
            content = self.add_async_await(content)

            # Update imports
            if all_changes:
                content = self.add_imports(
                    content, ["from core.infra.cortex_gateway import get_gateway"]
                )
                content = self.remove_imports(
                    content,
                    [
                        "import snowflake.connector",
                        "from snowflake.connector import",
                        "from shared.utils.snowflake_cortex_service import SnowflakeCortexService",
                    ],
                )

            # Save if changes were made
            if content != original_content:
                if not self.dry_run:
                    self.backup_file(file_path)
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)

                return {
                    "file": str(file_path),
                    "changes": all_changes,
                    "lines_changed": len(original_content.splitlines())
                    - len(content.splitlines()),
                }

        except Exception as e:
            print(f"Error migrating {file_path}: {e}")

        return None

    def generate_migration_report(self, results: list[dict]) -> str:
        """Generate migration report."""
        report = [
            "# Snowflake to CortexGateway Migration Report",
            f"Generated: {datetime.now().isoformat()}",
            f"Mode: {'DRY RUN' if self.dry_run else 'APPLIED'}",
            "",
            "## Summary",
            f"- Files migrated: {len(results)}",
            f"- Total changes: {sum(len(r['changes']) for r in results)}",
            "",
            "## Files Modified",
            "",
        ]

        for result in results:
            report.append(f"### {result['file']}")
            report.append(f"Changes: {len(result['changes'])}")
            for change in result["changes"]:
                report.append(f"  - {change}")
            report.append("")

        return "\n".join(report)


def main():
    """Run the migration."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Migrate Snowflake usage to CortexGateway"
    )
    parser.add_argument(
        "--apply", action="store_true", help="Apply changes (default is dry-run)"
    )
    parser.add_argument("--file", help="Migrate single file")
    parser.add_argument("--directory", default=".", help="Directory to scan")
    args = parser.parse_args()

    migrator = SnowflakeMigrator(dry_run=not args.apply)
    results = []

    if args.file:
        # Single file migration
        result = migrator.migrate_file(Path(args.file))
        if result:
            results.append(result)
    else:
        # Directory migration
        for py_file in Path(args.directory).rglob("*.py"):
            # Skip test files and migrations
            if "test" in str(py_file) or "migration" in str(py_file):
                continue

            result = migrator.migrate_file(py_file)
            if result:
                results.append(result)

    # Generate report
    if results:
        report = migrator.generate_migration_report(results)
        report_path = (
            Path("reports")
            / f'migration_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        )
        report_path.parent.mkdir(exist_ok=True)

        with open(report_path, "w") as f:
            f.write(report)

        print(report)
        print(f"\n✅ Migration report saved to: {report_path}")

        if migrator.dry_run:
            print("\n⚠️  This was a DRY RUN. Use --apply to apply changes.")
    else:
        print("No files needed migration.")


if __name__ == "__main__":
    main()
