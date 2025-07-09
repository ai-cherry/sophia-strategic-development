#!/usr/bin/env python3
"""
Comprehensive dead code cleanup for Sophia AI
Identifies and removes one-time scripts, old reports, backups, and other obsolete files
"""

import json
import os
import re
import shutil
from datetime import datetime
from pathlib import Path

# Categories of files to clean up
CATEGORIES = {
    "dated_reports": {
        "description": "Dated reports and logs",
        "patterns": [
            r".*_report_\d{8}_\d{6}\.(json|md)$",
            r".*_summary_\d{8}_\d{6}\.(json|md)$",
            r".*_log_\d{8}_\d{6}\.(json|md)$",
            r".*_results_\d{8}_\d{6}\.(json|md)$",
            r".*_plan_\d{8}_\d{6}\.(json|md)$",
            r".*_deployment_report_\d{8}_\d{6}\.(json|md)$",
            r".*_consolidation_report_\d{8}_\d{6}\.(json|md)$",
            r"modernization_report_\d{8}_\d{6}\.(json|md)$",
            r"modernization_log_\d{8}_\d{6}\.json$",
            r"cleanup_report_\d{8}_\d{6}\.json$",
            r"mcp_debug_report_\d{8}_\d{6}\.json$",
            r"comprehensive_mcp_debug_\d{8}_\d{6}_summary\.md$",
            r"estuary_migration_report_\d{8}_\d{6}\.json$",
        ],
    },
    "backup_directories": {
        "description": "Backup and temporary directories",
        "paths": [
            "backup_deployment_20250709_164922",
            "deployment_cleanup_backup_20250709_072050",
            "archive/unified_chat_duplicates",
            "archive/.github",
        ],
    },
    "backup_files": {
        "description": "Backup and original files",
        "patterns": [
            r".*\.original$",
            r".*\.backup$",
            r".*\.bak$",
            r".*\.old$",
        ],
    },
    "one_time_scripts": {
        "description": "One-time use scripts",
        "paths": [
            # Root directory one-time scripts
            "create_pull_request.py",
            "deploy_estuary_foundation_corrected.py",
            "deploy_estuary_foundation.py",
            "deploy_with_uv.py",
            "execute_strategic_chat_services.py",
            "consolidate_mcp_servers.py",
            "dead_code_cleanup.py",
            "execute_safe_refactoring_plan.py",
            "fix_critical_documentation_issues.py",
            "migrate_all_servers_to_unified_base.py",
            "phase1_ruff_remediation.py",
            "remove_mcp_technical_debt.py",
            "ULTIMATE_CLEANUP_EXECUTION.py",
            # Scripts directory one-time scripts
            "scripts/cleanup_deployment_scripts.py",
            "scripts/cleanup_deployment_technical_debt.py",
            "scripts/comprehensive_secret_cleanup_and_fix.py",
            "scripts/consolidate_chat_services.py",
            "scripts/consolidate_mcp_servers.py",
            "scripts/create_unified_mcp_base.py",
            "scripts/execute_safe_refactoring_plan.py",
            "scripts/fix_critical_documentation_issues.py",
            "scripts/fix_dependency_conflicts.py",
            "scripts/migrate_all_servers_to_unified_base.py",
            "scripts/remove_deprecated_docker_files.py",
            "scripts/remove_mcp_technical_debt.py",
        ],
    },
    "migration_scripts": {
        "description": "Migration scripts that have been executed",
        "paths": [
            "migration_scripts/phase1_critical.sh",
            "migration_scripts/phase2_production.sh",
            "migration_scripts/phase3_environments.sh",
        ],
    },
    "patches": {
        "description": "Applied patches",
        "paths": [
            "patches/snowflake_test_util_fix.py",
        ],
    },
    "empty_directories": {
        "description": "Empty directories",
        "paths": [
            "logs",
            "test_env",
            "test_reports",
            "reports",
        ],
    },
    "one_time_reports": {
        "description": "One-time analysis and implementation reports",
        "patterns": [
            r"AI_MEMORY_IMPLEMENTATION_FINAL_SUMMARY\.md$",
            r"COMPREHENSIVE_ARCHIVE_CLEANUP_REPORT\.md$",
            r"DEAD_CODE_AUDIT_SUMMARY\.md$",
            r"DEPLOYMENT_ERROR_ANALYSIS\.md$",
            r"deployment-error-analysis\.md$",
            r"PULUMI_INFRASTRUCTURE_SUCCESS_REPORT\.md$",
            r".*_IMPLEMENTATION_REPORT\.md$",
            r".*_ANALYSIS_REPORT\.md$",
            r".*_SUCCESS_REPORT\.md$",
            r".*_FINAL_REPORT\.md$",
            r".*_AUDIT_REPORT\.md$",
        ],
    },
    "analysis_artifacts": {
        "description": "Analysis and audit artifacts",
        "patterns": [
            r"codebase_audit_report\.json$",
            r"github_alignment_report\.json$",
            r"archive_cleanup_analysis\.json$",
            r"archive_cleanup_execution\.json$",
            r"comprehensive_test_results.*\.json$",
            r"analysis_report_.*\.json$",
        ],
    },
}

# Files that should NEVER be deleted
PROTECTED_FILES = {
    ".cursorrules",
    "README.md",
    "pyproject.toml",
    "requirements.txt",
    "LICENSE",
    ".gitignore",
    ".env.template",
    "Pulumi.yaml",
    "package.json",
}


class DeadCodeCleaner:
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.project_root = Path(".")
        self.files_to_delete = []
        self.directories_to_delete = []
        self.total_size = 0
        self.backup_dir = None

    def scan_files(self) -> None:
        """Scan for files and directories to delete"""
        print("🔍 Scanning for dead code and obsolete files...")

        # Scan by patterns
        for category, config in CATEGORIES.items():
            if "patterns" in config:
                self._scan_patterns(category, config["patterns"])
            if "paths" in config:
                self._scan_paths(category, config["paths"])

    def _scan_patterns(self, category: str, patterns: list[str]) -> None:
        """Scan files matching patterns"""
        for root, _, files in os.walk(self.project_root):
            # Skip hidden directories and virtual environments
            if "/.git" in root or "/.venv" in root or "/venv" in root:
                continue

            for file in files:
                if file in PROTECTED_FILES:
                    continue

                file_path = Path(root) / file
                rel_path = file_path.relative_to(self.project_root)

                for pattern in patterns:
                    if re.match(pattern, file) or re.match(pattern, str(rel_path)):
                        size = file_path.stat().st_size
                        self.files_to_delete.append((str(rel_path), category, size))
                        self.total_size += size
                        break

    def _scan_paths(self, category: str, paths: list[str]) -> None:
        """Scan specific paths"""
        for path_str in paths:
            path = self.project_root / path_str

            if path.is_file() and path.exists():
                if path.name not in PROTECTED_FILES:
                    size = path.stat().st_size
                    self.files_to_delete.append((path_str, category, size))
                    self.total_size += size
            elif path.is_dir() and path.exists():
                # Calculate directory size
                size = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
                self.directories_to_delete.append((path_str, category, size))
                self.total_size += size

    def create_backup(self) -> None:
        """Create backup of files to be deleted"""
        if self.dry_run:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = Path(f"cleanup_backup_{timestamp}")
        self.backup_dir.mkdir(exist_ok=True)

        print(f"\n📦 Creating backup in {self.backup_dir}...")

        # Backup files
        for file_path, _, _ in self.files_to_delete:
            src = self.project_root / file_path
            if src.exists():
                dst = self.backup_dir / file_path
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)

        # Backup directories
        for dir_path, _, _ in self.directories_to_delete:
            src = self.project_root / dir_path
            if src.exists():
                dst = self.backup_dir / dir_path
                shutil.copytree(src, dst)

    def delete_files(self) -> None:
        """Delete identified files and directories"""
        if self.dry_run:
            print("\n🔍 DRY RUN - No files will be deleted")
            return

        print("\n🗑️  Deleting files...")

        # Delete files
        for file_path, _, _ in self.files_to_delete:
            path = self.project_root / file_path
            if path.exists():
                path.unlink()
                print(f"  ✅ Deleted: {file_path}")

        # Delete directories
        for dir_path, _, _ in self.directories_to_delete:
            path = self.project_root / dir_path
            if path.exists():
                shutil.rmtree(path)
                print(f"  ✅ Deleted directory: {dir_path}")

    def generate_report(self) -> dict:
        """Generate cleanup report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": self.dry_run,
            "total_files": len(self.files_to_delete),
            "total_directories": len(self.directories_to_delete),
            "total_size_mb": round(self.total_size / 1024 / 1024, 2),
            "categories": {},
        }

        # Group by category
        for category in CATEGORIES:
            files = [f for f, c, _ in self.files_to_delete if c == category]
            dirs = [d for d, c, _ in self.directories_to_delete if c == category]

            if files or dirs:
                report["categories"][category] = {
                    "description": CATEGORIES[category]["description"],
                    "files": len(files),
                    "directories": len(dirs),
                    "items": files[:10] + dirs[:10],  # First 10 items
                }

        return report

    def print_summary(self) -> None:
        """Print summary of findings"""
        print("\n📊 CLEANUP SUMMARY")
        print("=" * 50)
        print(f"Total files to delete: {len(self.files_to_delete)}")
        print(f"Total directories to delete: {len(self.directories_to_delete)}")
        print(f"Total space to recover: {self.total_size / 1024 / 1024:.2f} MB")

        print("\n📂 By Category:")
        for category in CATEGORIES:
            files = [f for f, c, _ in self.files_to_delete if c == category]
            dirs = [d for d, c, _ in self.directories_to_delete if c == category]

            if files or dirs:
                size = sum(
                    s
                    for _, c, s in self.files_to_delete + self.directories_to_delete
                    if c == category
                )
                print(f"\n{CATEGORIES[category]['description']}:")
                print(f"  Files: {len(files)}, Directories: {len(dirs)}")
                print(f"  Size: {size / 1024 / 1024:.2f} MB")

                # Show first few items
                items = files[:3] + dirs[:3]
                for item in items[:5]:
                    print(f"    - {item}")
                if len(files) + len(dirs) > 5:
                    print(f"    ... and {len(files) + len(dirs) - 5} more")


def main():
    """Main cleanup function"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Clean up dead code and obsolete files"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually delete files (default is dry run)",
    )
    parser.add_argument("--report", help="Save report to JSON file")
    args = parser.parse_args()

    cleaner = DeadCodeCleaner(dry_run=not args.execute)

    # Scan for files
    cleaner.scan_files()

    # Print summary
    cleaner.print_summary()

    if not cleaner.dry_run:
        # Create backup
        cleaner.create_backup()

        # Confirm deletion
        print(
            f"\n⚠️  WARNING: This will delete {len(cleaner.files_to_delete)} files and {len(cleaner.directories_to_delete)} directories"
        )
        print(f"Backup created in: {cleaner.backup_dir}")
        response = input("\nProceed with deletion? (yes/no): ")

        if response.lower() == "yes":
            cleaner.delete_files()
            print("\n✅ Cleanup completed!")
        else:
            print("\n❌ Cleanup cancelled")
    else:
        print("\n💡 To execute cleanup, run with --execute flag")

    # Generate report
    if args.report:
        report = cleaner.generate_report()
        with open(args.report, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 Report saved to: {args.report}")


if __name__ == "__main__":
    main()
