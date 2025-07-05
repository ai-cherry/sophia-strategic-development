#!/usr/bin/env python3
"""
Script to audit and cleanup one-time scripts from the scripts directory
Part of the Sophia AI code hygiene enforcement initiative
"""

import shutil
from datetime import datetime
from pathlib import Path

# Patterns that indicate one-time scripts
ONE_TIME_PATTERNS = [
    "fix_",
    "deploy_",
    "cleanup_",
    "migrate_",
    "test_",
    "validate_",
    "one_time_",
    "week",  # Week-specific scripts like week2_3_function_complexity
    "phase",  # Phase-specific scripts
]

# Known reusable scripts that should NOT be deleted
REUSABLE_SCRIPTS = [
    # Core operational scripts
    "run_all_mcp_servers.py",
    "activate_sophia_production.py",
    "comprehensive_health_check.py",
    "performance_monitor.py",
    "start_mcp_servers.py",
    "start_all_mcp_servers.py",
    "start_mcp_server.py",
    "start_unified_api.py",
    # Configuration scripts
    "update_cursor_mcp_config.py",
    "snowflake_config_manager.py",
    "optimize_cursor_config.py",
    # Monitoring scripts
    "real_time_monitoring.py",
    "monitor_services.sh",
    "monitor_swarm_performance.sh",
    # Security scripts (in security/ subdirectory)
    "remediate_secrets.py",
    # This cleanup script itself
    "cleanup_one_time_scripts.py",
]


def audit_scripts() -> tuple[list[Path], list[Path]]:
    """
    Audit scripts directory and categorize scripts

    Returns:
        Tuple of (one_time_candidates, reusable_scripts)
    """
    scripts_dir = Path("scripts")
    one_time_candidates = []
    reusable_list = []

    # Get all Python and shell scripts
    all_scripts = list(scripts_dir.glob("*.py")) + list(scripts_dir.glob("*.sh"))

    for script in all_scripts:
        if script.name in REUSABLE_SCRIPTS:
            reusable_list.append(script)
            continue

        # Check if matches one-time pattern
        is_one_time = False
        for pattern in ONE_TIME_PATTERNS:
            if script.name.startswith(pattern):
                is_one_time = True
                break

        if is_one_time:
            one_time_candidates.append(script)
        else:
            # Scripts that don't match patterns but aren't in reusable list
            # These need manual review
            reusable_list.append(script)

    return one_time_candidates, reusable_list


def get_script_info(script: Path) -> dict:
    """Get information about a script"""
    stat = script.stat()
    return {
        "name": script.name,
        "size": stat.st_size,
        "modified": datetime.fromtimestamp(stat.st_mtime),
        "lines": len(script.read_text().splitlines()) if script.suffix == ".py" else 0,
    }


def cleanup_scripts(scripts: list[Path], backup: bool = True, dry_run: bool = True):
    """
    Remove one-time scripts with optional backup

    Args:
        scripts: List of script paths to remove
        backup: Whether to backup before deletion
        dry_run: If True, only show what would be done
    """
    if not scripts:
        print("No scripts to clean up.")
        return

    backup_dir = None
    if backup and not dry_run:
        backup_dir = Path(f"backups/scripts_cleanup_{datetime.now():%Y%m%d_%H%M%S}")
        backup_dir.mkdir(parents=True, exist_ok=True)
        print(f"\nBackup directory: {backup_dir}")

    total_size = 0
    for script in scripts:
        info = get_script_info(script)
        total_size += info["size"]

        if dry_run:
            print(
                f"Would remove: {info['name']} ({info['size']:,} bytes, {info['lines']} lines)"
            )
        else:
            if backup and backup_dir:
                backup_path = backup_dir / script.name
                shutil.copy2(script, backup_path)
                print(f"Backed up: {script.name}")

            script.unlink()
            print(f"Removed: {script.name}")

    print(
        f"\nTotal space {'to be ' if dry_run else ''}freed: {total_size:,} bytes ({total_size/1024/1024:.2f} MB)"
    )


def main():
    """Main function to run the cleanup process"""
    print("Sophia AI Script Cleanup Audit")
    print("=" * 50)

    # Audit scripts
    one_time_candidates, reusable_scripts = audit_scripts()

    print("\nAudit Results:")
    print(f"- One-time script candidates: {len(one_time_candidates)}")
    print(f"- Reusable/unknown scripts: {len(reusable_scripts)}")

    if one_time_candidates:
        print("\nOne-time Script Candidates:")
        print("-" * 50)

        # Sort by pattern type
        by_pattern = {}
        for script in one_time_candidates:
            for pattern in ONE_TIME_PATTERNS:
                if script.name.startswith(pattern):
                    if pattern not in by_pattern:
                        by_pattern[pattern] = []
                    by_pattern[pattern].append(script)
                    break

        for pattern, scripts in sorted(by_pattern.items()):
            print(f"\n{pattern}* scripts ({len(scripts)}):")
            for script in sorted(scripts, key=lambda x: x.name):
                info = get_script_info(script)
                age_days = (datetime.now() - info["modified"]).days
                print(f"  - {info['name']} (modified {age_days} days ago)")

        # Ask for confirmation
        print("\n" + "=" * 50)
        response = (
            input(
                "\nDo you want to remove these scripts? (dry-run/backup/remove/no) [dry-run]: "
            )
            .lower()
            .strip()
        )

        if response == "dry-run" or response == "":
            cleanup_scripts(one_time_candidates, backup=True, dry_run=True)
        elif response == "backup":
            cleanup_scripts(one_time_candidates, backup=True, dry_run=False)
        elif response == "remove":
            confirm = (
                input("Are you sure you want to remove WITHOUT backup? (yes/no) [no]: ")
                .lower()
                .strip()
            )
            if confirm == "yes":
                cleanup_scripts(one_time_candidates, backup=False, dry_run=False)
            else:
                print("Cancelled.")
        else:
            print("No action taken.")

    # Show reusable scripts for reference
    print(f"\n\nReusable/Unknown Scripts ({len(reusable_scripts)}):")
    print("-" * 50)
    for script in sorted(reusable_scripts, key=lambda x: x.name):
        print(f"  - {script.name}")


if __name__ == "__main__":
    main()
