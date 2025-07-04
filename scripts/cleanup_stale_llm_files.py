#!/usr/bin/env python3
"""
Cleanup stale LLM files and consolidate LLM services
"""

import shutil
from datetime import datetime
from pathlib import Path

# Files to delete (stale/duplicate LLM services)
STALE_LLM_FILES = [
    # Duplicate/stale LLM gateway services
    "backend/services/portkey_gateway.py",  # Replaced by unified_llm_service.py
    "backend/services/smart_ai_service.py",  # Replaced by unified_llm_service.py
    "backend/services/simplified_portkey_service.py",  # Replaced by unified_llm_service.py
    "backend/services/enhanced_portkey_orchestrator.py",  # Replaced by unified_llm_service.py
    # Old test scripts
    "scripts/test_portkey_integration.py",
    "scripts/test_openrouter_integration.py",
    "scripts/test_llm_gateway.py",
]

# Files to update imports
FILES_TO_UPDATE_IMPORTS = [
    "backend/services/infrastructure_chat/sophia_infrastructure_chat.py",
    "backend/services/unified_intelligence_service.py",
    "backend/services/enhanced_unified_intelligence_service.py",
    "backend/services/advanced_ui_ux_agent_service.py",
    "backend/api/unified_chat_routes_v2.py",
]

# Import replacements
IMPORT_REPLACEMENTS = [
    # Replace old imports with new unified service
    (
        "from backend.services.smart_ai_service import SmartAIService",
        "from backend.services.unified_llm_service import UnifiedLLMService, TaskType",
    ),
    (
        "from backend.services.portkey_gateway import PortkeyGateway",
        "from backend.services.unified_llm_service import UnifiedLLMService, TaskType",
    ),
    (
        "from backend.services.simplified_portkey_service import SimplifiedPortkeyService",
        "from backend.services.unified_llm_service import UnifiedLLMService, TaskType",
    ),
    (
        "import backend.services.smart_ai_service",
        "import backend.services.unified_llm_service",
    ),
    ("smart_ai_service", "unified_llm_service"),
    ("SmartAIService", "UnifiedLLMService"),
    ("PortkeyGateway", "UnifiedLLMService"),
]


def create_backup_directory() -> Path:
    """Create a backup directory for deleted files"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(f"backups/llm_cleanup_{timestamp}")
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir


def backup_file(file_path: Path, backup_dir: Path) -> bool:
    """Backup a file before deletion"""
    if file_path.exists():
        # Make sure file_path is absolute
        if not file_path.is_absolute():
            file_path = Path.cwd() / file_path

        try:
            relative_path = file_path.relative_to(Path.cwd())
        except ValueError:
            # If file is not under current directory, use its name
            relative_path = Path(file_path.name)

        backup_path = backup_dir / relative_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, backup_path)
        print(f"✅ Backed up: {file_path} -> {backup_path}")
        return True
    return False


def delete_stale_files(backup_dir: Path) -> list[str]:
    """Delete stale LLM files"""
    deleted_files = []

    for file_path_str in STALE_LLM_FILES:
        file_path = Path(file_path_str)
        if file_path.exists():
            # Backup before deletion
            if backup_file(file_path, backup_dir):
                file_path.unlink()
                deleted_files.append(str(file_path))
                print(f"🗑️  Deleted: {file_path}")
        else:
            print(f"⚠️  File not found: {file_path}")

    return deleted_files


def update_imports_in_file(file_path: Path) -> int:
    """Update imports in a single file"""
    if not file_path.exists():
        print(f"⚠️  File not found: {file_path}")
        return 0

    content = file_path.read_text()
    original_content = content
    replacements_made = 0

    for old_import, new_import in IMPORT_REPLACEMENTS:
        if old_import in content:
            content = content.replace(old_import, new_import)
            replacements_made += content.count(new_import) - original_content.count(
                new_import
            )

    if content != original_content:
        file_path.write_text(content)
        print(f"✅ Updated imports in: {file_path} ({replacements_made} replacements)")

    return replacements_made


def update_all_imports() -> dict[str, int]:
    """Update imports in all affected files"""
    updates = {}

    for file_path_str in FILES_TO_UPDATE_IMPORTS:
        file_path = Path(file_path_str)
        replacements = update_imports_in_file(file_path)
        if replacements > 0:
            updates[str(file_path)] = replacements

    return updates


def find_additional_references() -> list[tuple[str, list[str]]]:
    """Find additional files that might reference old LLM services"""
    references = []

    # Search patterns
    patterns = [
        "SmartAIService",
        "PortkeyGateway",
        "SimplifiedPortkeyService",
        "smart_ai_service",
        "portkey_gateway",
        "simplified_portkey_service",
    ]

    # Directories to search
    search_dirs = ["backend", "scripts", "docs"]

    for search_dir in search_dirs:
        if not Path(search_dir).exists():
            continue

        for pattern in patterns:
            # Use grep to find references
            import subprocess

            try:
                result = subprocess.run(
                    ["grep", "-r", "-l", pattern, search_dir],
                    capture_output=True,
                    text=True,
                )
                if result.stdout:
                    files = result.stdout.strip().split("\n")
                    # Filter out files we're already handling or deleting
                    files = [
                        f
                        for f in files
                        if f
                        and f not in STALE_LLM_FILES
                        and f not in FILES_TO_UPDATE_IMPORTS
                    ]
                    if files:
                        references.append((pattern, files))
            except subprocess.CalledProcessError:
                pass

    return references


def main():
    """Main cleanup function"""
    print("🧹 Starting LLM files cleanup...")
    print("=" * 60)

    # Create backup directory
    backup_dir = create_backup_directory()
    print(f"📁 Backup directory: {backup_dir}")
    print()

    # Delete stale files
    print("🗑️  Deleting stale LLM files...")
    deleted_files = delete_stale_files(backup_dir)
    print(f"Deleted {len(deleted_files)} files")
    print()

    # Update imports
    print("📝 Updating imports...")
    updates = update_all_imports()
    print(
        f"Updated {len(updates)} files with {sum(updates.values())} total replacements"
    )
    print()

    # Find additional references
    print("🔍 Finding additional references...")
    references = find_additional_references()

    if references:
        print("\n⚠️  Additional files with references to old LLM services:")
        for pattern, files in references:
            print(f"\nPattern '{pattern}' found in:")
            for file in files[:10]:  # Limit to 10 files per pattern
                print(f"  - {file}")
            if len(files) > 10:
                print(f"  ... and {len(files) - 10} more files")

    # Summary
    print("\n" + "=" * 60)
    print("✅ LLM cleanup complete!")
    print(f"  - Deleted: {len(deleted_files)} files")
    print(f"  - Updated: {len(updates)} files")
    print(f"  - Backups: {backup_dir}")

    if references:
        print(
            f"\n⚠️  Found {sum(len(files) for _, files in references)} additional files with references"
        )
        print("   Review these files manually and update as needed.")

    # Create summary file
    summary_path = backup_dir / "cleanup_summary.txt"
    with open(summary_path, "w") as f:
        f.write("LLM Cleanup Summary\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Date: {datetime.now().isoformat()}\n\n")

        f.write("Deleted Files:\n")
        for file in deleted_files:
            f.write(f"  - {file}\n")

        f.write("\nUpdated Files:\n")
        for file, count in updates.items():
            f.write(f"  - {file} ({count} replacements)\n")

        if references:
            f.write("\nAdditional References Found:\n")
            for pattern, files in references:
                f.write(f"\n  Pattern '{pattern}':\n")
                for file in files:
                    f.write(f"    - {file}\n")

    print(f"\n📄 Summary saved to: {summary_path}")


if __name__ == "__main__":
    main()
