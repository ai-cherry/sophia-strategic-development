#!/usr/bin/env python3
"""
Automated Model Cleanup Script
Updates outdated model references to modern equivalents
"""

import json
import re
import shutil
from datetime import datetime
from pathlib import Path

# Define model replacements
MODEL_REPLACEMENTS = {
    # Claude replacements
    "claude-3-5-sonnet-20241022": "claude-3-5-sonnet-20241022",
    "claude-3-5-sonnet-20241022": "claude-3-5-sonnet-20241022",
    "anthropic/claude-3.5-sonnet": "anthropic/claude-3.5-sonnet",
    # Gemini replacements
    "gemini-2.0-flash-exp": "gemini-2.0-flash-exp",
    "gemini-2.0-flash-exp": "gemini-2.0-flash-exp",
    "google/gemini-2.0-flash-exp": "google/gemini-2.0-flash-exp",
    # GPT replacements
    "gpt-4o": "gpt-4o",
    "gpt-4o": "gpt-4o",
    "openai/gpt-4o": "openai/gpt-4o",
    "openai/gpt-4o": "openai/gpt-4o",
}

# Estuary Flow to Estuary replacements
AIRBYTE_REPLACEMENTS = {
    "RAW_ESTUARY": "RAW_ESTUARY",
    "STG_ESTUARY": "STG_ESTUARY",
    "Estuary Flow": "Estuary Flow",
    "estuary": "estuary",
    "ESTUARY": "ESTUARY",
}

# Critical files to update
CRITICAL_FILES = [
    "config/llm_router.json",
    "config/services/optimization.yaml",
    "config/services/portkey.json",
    "config/portkey/sophia-ai-config.json",
    "infrastructure/services/llm_router/fallback.py",
    "infrastructure/services/llm_gateway/portkey_integration.py",
    "infrastructure/services/llm_gateway/openrouter_integration.py",
    "infrastructure/services/enhanced_portkey_llm_gateway.py",
]

# File patterns to process
FILE_PATTERNS = [
    "**/*.py",
    "**/*.json",
    "**/*.yaml",
    "**/*.yml",
    "**/*.md",
    "**/*.sql",
]

# Directories to skip
SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "archive",
    "external",
    "cleanup_backup*",
    "docs_backup*",
    "reports",
}


def create_backup(file_path: Path) -> Path:
    """Create a backup of the file before modification"""
    backup_dir = Path("cleanup_backup") / datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir.mkdir(parents=True, exist_ok=True)

    relative_path = file_path.relative_to(Path.cwd())
    backup_path = backup_dir / relative_path
    backup_path.parent.mkdir(parents=True, exist_ok=True)

    shutil.copy2(file_path, backup_path)
    return backup_path


def update_json_file(file_path: Path, dry_run: bool = False) -> int:
    """Update JSON file with model replacements"""
    changes = 0

    try:
        with open(file_path) as f:
            content = f.read()
            data = json.loads(content)

        original_content = content

        # Convert to string for replacement
        json_str = json.dumps(data, indent=2)

        # Replace models
        for old_model, new_model in MODEL_REPLACEMENTS.items():
            if old_model in json_str:
                json_str = json_str.replace(f'"{old_model}"', f'"{new_model}"')
                changes += json_str.count(f'"{new_model}"')

        if changes > 0 and not dry_run:
            # Parse back to ensure valid JSON
            updated_data = json.loads(json_str)

            # Create backup
            create_backup(file_path)

            # Write updated content
            with open(file_path, "w") as f:
                json.dump(updated_data, f, indent=2)
                f.write("\n")  # Add trailing newline

            print(f"✅ Updated {file_path}: {changes} replacements")
        elif changes > 0:
            print(f"🔍 Would update {file_path}: {changes} replacements")

    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")

    return changes


def update_yaml_file(file_path: Path, dry_run: bool = False) -> int:
    """Update YAML file with model replacements"""
    changes = 0

    try:
        with open(file_path) as f:
            content = f.read()

        original_content = content

        # Replace models
        for old_model, new_model in MODEL_REPLACEMENTS.items():
            # Count occurrences before replacement
            count_before = content.count(old_model)
            content = content.replace(old_model, new_model)
            changes += count_before

        # Replace Estuary Flow references
        for old_term, new_term in AIRBYTE_REPLACEMENTS.items():
            if old_term in ["estuary", "Estuary Flow", "ESTUARY"]:
                # Use word boundaries for these
                pattern = rf"\b{old_term}\b"
                count_before = len(re.findall(pattern, content))
                content = re.sub(pattern, new_term, content)
                changes += count_before
            else:
                count_before = content.count(old_term)
                content = content.replace(old_term, new_term)
                changes += count_before

        if changes > 0 and not dry_run:
            create_backup(file_path)
            with open(file_path, "w") as f:
                f.write(content)
            print(f"✅ Updated {file_path}: {changes} replacements")
        elif changes > 0:
            print(f"🔍 Would update {file_path}: {changes} replacements")

    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")

    return changes


def update_python_file(file_path: Path, dry_run: bool = False) -> int:
    """Update Python file with model replacements"""
    changes = 0

    try:
        with open(file_path) as f:
            content = f.read()

        original_content = content

        # Replace models in strings
        for old_model, new_model in MODEL_REPLACEMENTS.items():
            # Replace in double quotes
            pattern = f'"{old_model}"'
            replacement = f'"{new_model}"'
            count_before = content.count(pattern)
            content = content.replace(pattern, replacement)
            changes += count_before

            # Replace in single quotes
            pattern = f"'{old_model}'"
            replacement = f"'{new_model}'"
            count_before = content.count(pattern)
            content = content.replace(pattern, replacement)
            changes += count_before

        # Replace Estuary Flow references
        for old_term, new_term in AIRBYTE_REPLACEMENTS.items():
            if old_term in ["estuary", "Estuary Flow", "ESTUARY"]:
                # Use word boundaries for these
                pattern = rf"\b{old_term}\b"
                count_before = len(re.findall(pattern, content))
                content = re.sub(pattern, new_term, content)
                changes += count_before
            else:
                count_before = content.count(old_term)
                content = content.replace(old_term, new_term)
                changes += count_before

        if changes > 0 and not dry_run:
            create_backup(file_path)
            with open(file_path, "w") as f:
                f.write(content)
            print(f"✅ Updated {file_path}: {changes} replacements")
        elif changes > 0:
            print(f"🔍 Would update {file_path}: {changes} replacements")

    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")

    return changes


def update_sql_file(file_path: Path, dry_run: bool = False) -> int:
    """Update SQL file with schema replacements"""
    changes = 0

    try:
        with open(file_path) as f:
            content = f.read()

        original_content = content

        # Replace schemas
        for old_schema, new_schema in AIRBYTE_REPLACEMENTS.items():
            if old_schema in ["RAW_ESTUARY", "STG_ESTUARY"]:
                count_before = content.count(old_schema)
                content = content.replace(old_schema, new_schema)
                changes += count_before

        if changes > 0 and not dry_run:
            create_backup(file_path)
            with open(file_path, "w") as f:
                f.write(content)
            print(f"✅ Updated {file_path}: {changes} replacements")
        elif changes > 0:
            print(f"🔍 Would update {file_path}: {changes} replacements")

    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")

    return changes


def process_file(file_path: Path, dry_run: bool = False) -> int:
    """Process a single file based on its type"""
    if file_path.suffix == ".json":
        return update_json_file(file_path, dry_run)
    elif file_path.suffix in [".yaml", ".yml"]:
        return update_yaml_file(file_path, dry_run)
    elif file_path.suffix == ".py":
        return update_python_file(file_path, dry_run)
    elif file_path.suffix == ".sql":
        return update_sql_file(file_path, dry_run)
    elif file_path.suffix == ".md":
        return update_yaml_file(file_path, dry_run)  # Use same logic as YAML
    else:
        return 0


def main(dry_run: bool = True):
    """Main execution"""
    root_path = Path.cwd()
    total_changes = 0
    files_processed = 0

    print(f"🚀 Starting model cleanup {'(DRY RUN)' if dry_run else '(LIVE RUN)'}")
    print(f"📁 Working directory: {root_path}")

    # Process critical files first
    print("\n📌 Processing critical configuration files...")
    for file_path in CRITICAL_FILES:
        full_path = root_path / file_path
        if full_path.exists():
            changes = process_file(full_path, dry_run)
            if changes > 0:
                total_changes += changes
                files_processed += 1

    # Process all other files
    print("\n🔍 Processing all other files...")
    for pattern in FILE_PATTERNS:
        for file_path in root_path.glob(pattern):
            # Skip if in skip directory
            if any(skip_dir in str(file_path) for skip_dir in SKIP_DIRS):
                continue

            # Skip if already processed as critical
            if str(file_path.relative_to(root_path)) in CRITICAL_FILES:
                continue

            changes = process_file(file_path, dry_run)
            if changes > 0:
                total_changes += changes
                files_processed += 1

    # Summary
    print("\n📊 Summary:")
    print(f"- Files processed: {files_processed}")
    print(f"- Total replacements: {total_changes}")

    if dry_run:
        print("\n⚠️  This was a DRY RUN. No files were modified.")
        print("Run with --live to apply changes.")
    else:
        print("\n✅ All changes applied successfully!")
        print("Backups created in: cleanup_backup/")

    return 0


if __name__ == "__main__":
    import sys

    dry_run = "--live" not in sys.argv
    exit_code = main(dry_run)
    exit(exit_code)
