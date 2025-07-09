#!/usr/bin/env python3
"""
Automated Model Cleanup Script
Updates outdated model references to modern equivalents
"""

import shutil
from datetime import datetime
from pathlib import Path

# Define model replacements
MODEL_REPLACEMENTS = {
    # OpenAI model updates
    "text-davinci-003": "gpt-3.5-turbo",
    "text-davinci-002": "gpt-3.5-turbo",
    "code-davinci-002": "gpt-3.5-turbo",
    "text-curie-001": "gpt-3.5-turbo",
    "text-babbage-001": "gpt-3.5-turbo",
    "text-ada-001": "gpt-3.5-turbo",
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


def update_files(files_to_update: list[Path], dry_run: bool = False) -> int:
    """Update files with new model names"""
    changes = []
    total_replacements = 0

    for file_path in files_to_update:
        try:
            with open(file_path) as f:
                content = f.read()

            original_content = content

            # Apply model replacements
            for old_model, new_model in MODEL_REPLACEMENTS.items():
                if old_model in content:
                    new_content = content.replace(old_model, new_model)
                    changes.append(f"  - {old_model} → {new_model}")
                    total_replacements += content.count(old_model)

            if changes and not dry_run:
                create_backup(file_path)
                with open(file_path, "w") as f:
                    f.write(new_content)
                print(f"✅ Updated {file_path}: {total_replacements} replacements")
            elif changes:
                print(f"🔍 Would update {file_path}: {total_replacements} replacements")

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")

    return total_replacements


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
            changes = update_files([full_path], dry_run)
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

            changes = update_files([file_path], dry_run)
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
