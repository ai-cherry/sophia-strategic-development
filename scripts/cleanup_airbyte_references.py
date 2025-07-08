#!/usr/bin/env python3
"""
Cleanup Airbyte References
Replaces Airbyte references with Estuary Flow equivalents
"""

import shutil
from datetime import datetime
from pathlib import Path

# Define Airbyte to Estuary Flow replacements
AIRBYTE_REPLACEMENTS = {
    # Table/Schema references
    "RAW_ESTUARY": "RAW_ESTUARY",
    "raw_estuary": "raw_estuary",
    "ESTUARY_INTERNAL": "ESTUARY_INTERNAL",
    "estuary_internal": "estuary_internal",
    "_ESTUARY_": "_ESTUARY_",
    "_estuary_": "_estuary_",
    # Service/Component references
    "EstuaryFlowOrchestrator": "EstuaryFlowOrchestrator",
    "EstuaryFlowConfiguration": "EstuaryFlowConfiguration",
    "EstuaryFlowIntegration": "EstuaryFlowIntegration",
    "estuary_flow_configuration_manager": "estuary_flow_configuration_manager",
    "estuary_flow_gong_setup": "estuary_flow_gong_setup",
    # Environment variables and secrets
    "ESTUARY_API_KEY": "ESTUARY_API_KEY",
    "ESTUARY_API_TOKEN": "ESTUARY_API_TOKEN",
    "LAMBDA_ESTUARY_TOKEN": "ESTUARY_FLOW_TOKEN",
    "ESTUARY_HOST": "ESTUARY_HOST",
    "ESTUARY_PORT": "ESTUARY_PORT",
    # Comments and documentation
    "Estuary Flow integration": "Estuary Flow integration",
    "Estuary Flow connector": "Estuary Flow connector",
    "Estuary Flow pipeline": "Estuary Flow pipeline",
    "Estuary Flow sync": "Estuary Flow sync",
}

# Define files to skip
SKIP_PATTERNS = {
    "*.git*",
    "*node_modules*",
    "*venv*",
    "*.venv*",
    "*__pycache__*",
    "*.pyc",
    "*cleanup_backup*",
    "*archive*",
    "*external*",
}


def should_skip_file(file_path: Path) -> bool:
    """Check if file should be skipped"""
    path_str = str(file_path)

    # Skip patterns
    for pattern in SKIP_PATTERNS:
        if pattern.replace("*", "") in path_str:
            return True

    # Skip binary files
    try:
        with open(file_path, encoding="utf-8") as f:
            f.read(1024)
        return False
    except:
        return True


def clean_estuary_references(directory: Path = Path(".")):
    """Clean up Airbyte references in the codebase"""

    print("🔍 Scanning for Airbyte references...")

    files_to_update = []
    total_replacements = 0

    # Find all files with Airbyte references
    for file_path in directory.rglob("*"):
        if file_path.is_file() and not should_skip_file(file_path):
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                # Check if file contains Airbyte references
                if any(pattern in content for pattern in AIRBYTE_REPLACEMENTS.keys()):
                    files_to_update.append(file_path)

                    # Count replacements
                    for old, new in AIRBYTE_REPLACEMENTS.items():
                        count = content.count(old)
                        if count > 0:
                            total_replacements += count

            except Exception:
                continue

    print(f"\n📊 Found {len(files_to_update)} files with Airbyte references")
    print(f"📊 Total replacements to make: {total_replacements}")

    # Create backup
    backup_dir = Path(
        f"airbyte_cleanup_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    backup_dir.mkdir(exist_ok=True)

    # Apply replacements
    print("\n✨ Applying replacements...")
    for file_path in files_to_update:
        try:
            # Create backup
            backup_path = backup_dir / file_path.relative_to(directory)
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, backup_path)

            # Read content
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Apply replacements
            updated_content = content
            replacements_made = 0

            for old, new in AIRBYTE_REPLACEMENTS.items():
                if old in updated_content:
                    count = updated_content.count(old)
                    updated_content = updated_content.replace(old, new)
                    replacements_made += count

            # Write back if changes were made
            if replacements_made > 0:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(updated_content)
                print(f"✅ Updated {file_path}: {replacements_made} replacements")

        except Exception as e:
            print(f"❌ Error updating {file_path}: {e}")

    # Generate report
    report_path = Path("reports/airbyte_cleanup_report.md")
    report_path.parent.mkdir(exist_ok=True)

    with open(report_path, "w") as f:
        f.write("# Airbyte to Estuary Flow Cleanup Report\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Summary\n")
        f.write(f"- Files updated: {len(files_to_update)}\n")
        f.write(f"- Total replacements: {total_replacements}\n")
        f.write(f"- Backup location: {backup_dir}\n\n")
        f.write("## Files Updated\n\n")

        for file_path in sorted(files_to_update):
            f.write(f"- {file_path}\n")

        f.write("\n## Replacement Patterns\n\n")
        f.write("| Old Pattern | New Pattern |\n")
        f.write("|-------------|-------------|\n")
        for old, new in AIRBYTE_REPLACEMENTS.items():
            f.write(f"| {old} | {new} |\n")

    print(f"\n📄 Report generated: {report_path}")
    print(f"💾 Backup created: {backup_dir}")

    # Clean up the messy cleanup_backup directory
    print("\n🧹 Cleaning up nested backup directories...")
    cleanup_backup_dir = Path("cleanup_backup")
    if cleanup_backup_dir.exists():
        try:
            shutil.rmtree(cleanup_backup_dir)
            print("✅ Removed nested cleanup_backup directory")
        except Exception as e:
            print(f"⚠️  Could not remove cleanup_backup directory: {e}")


if __name__ == "__main__":
    clean_estuary_references()
