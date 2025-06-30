#!/usr/bin/env python3
"""
Comprehensive Dead Code and Backup File Cleanup for Sophia AI
Removes all backup, archived, duplicate, and dead files that cause conflicts

This script safely removes:
- All .bak, .backup, .old, .orig files
- Backup directories (uv_migration_backups, docs_backup, backups)
- Duplicate and conflicting scripts
- Archive directories
- Temporary and cache files
- Dead configuration files
"""

import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import List

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class ComprehensiveDeadCodeCleanup:
    """Comprehensive cleanup of dead code, backups, and conflicting files"""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.root_path = Path(".")
        self.removed_files: List[Path] = []
        self.removed_dirs: List[Path] = []
        self.total_size_freed = 0

        # Create final backup before cleanup
        self.final_backup_dir = Path(
            f"final_cleanup_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

    def get_cleanup_targets(self) -> dict:
        """Define all cleanup targets"""
        return {
            "backup_files": [
                "**/*.bak",
                "**/*.backup",
                "**/*.old",
                "**/*.orig",
                "**/*_backup.*",
                "**/*_old.*",
                "**/*.batch_backup",
                "**/.*backup*",
            ],
            "backup_directories": [
                "uv_migration_backups",
                "docs_backup",
                "backups",
                "docs/archive",
                "**/backup_*",
                "**/archive_*",
                "**/*_backup_*",
            ],
            "duplicate_scripts": [
                # Duplicate cleanup scripts
                "scripts/cleanup/comprehensive_workspace_cleanup.py",
                "scripts/safe_cleanup.py",
                "scripts/infrastructure_cleanup.py",
                "scripts/comprehensive_codebase_cleanup.py",
                "scripts/modernization/modernize_fastapi_lifespan.py",
                "scripts/fix_syntax_errors.py",
                # Duplicate documentation cleanup
                "docs/cleanup_documentation.py",
                # Root level backup files
                "comprehensive_alignment_analysis_and_fix.py.batch_backup",
                "setup_enhanced_coding_workflow.py.batch_backup",
                "enhanced_coding_workflow_integration.py.batch_backup",
                "SOPHIA_AI_DOCUMENTATION_MASTER_INDEX.md.backup",
            ],
            "cache_and_temp": [
                "**/__pycache__",
                "**/*.pyc",
                "**/*.pyo",
                "**/.pytest_cache",
                "**/.mypy_cache",
                "**/*.tmp",
                "**/*.temp",
                "**/.DS_Store",
                "**/Thumbs.db",
                "**/*.log",
                "**/*.pid",
                "**/*.lock",
                "**/node_modules/.cache",
            ],
            "dead_configs": [
                # Old patch files
                "snowflake_connection_fix.patch",
                # Broken or unused configs
                "config/agno_vsa_configuration.yaml",  # Agno was removed
                # Log files
                "fastapi.log",
                "fastapi_fixed.log",
            ],
            "watched_files": [
                # Empty or unused watched directories
                "backend/watched_costar_files",
                "watched_costar_files",
            ],
        }

    def create_final_backup(self) -> bool:
        """Create a final backup of important files before cleanup"""
        try:
            if self.dry_run:
                logger.info(
                    f"[DRY RUN] Would create final backup at {self.final_backup_dir}"
                )
                return True

            self.final_backup_dir.mkdir(exist_ok=True)
            logger.info(f"📦 Creating final backup at {self.final_backup_dir}")

            # Backup critical files that might be accidentally removed
            critical_files = [
                "backend/core/auto_esc_config.py",
                "backend/core/optimized_connection_manager.py",
                "backend/core/snowflake_config_override.py",
                "scripts/fix_snowflake_connectivity.py",
                "LAMBDA_LABS_CONFIGURATION_GUIDE.md",
            ]

            for file_path in critical_files:
                if Path(file_path).exists():
                    backup_path = self.final_backup_dir / file_path
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, backup_path)
                    logger.info(f"  ✅ Backed up critical file: {file_path}")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to create final backup: {e}")
            return False

    def remove_file(self, file_path: Path, category: str) -> bool:
        """Safely remove a file"""
        try:
            if self.dry_run:
                logger.info(f"[DRY RUN] Would remove {category}: {file_path}")
                return True

            file_size = file_path.stat().st_size if file_path.exists() else 0
            file_path.unlink()

            self.removed_files.append(file_path)
            self.total_size_freed += file_size
            logger.info(f"  🗑️  Removed {category}: {file_path}")
            return True

        except Exception as e:
            logger.error(f"  ❌ Failed to remove {file_path}: {e}")
            return False

    def remove_directory(self, dir_path: Path, category: str) -> bool:
        """Safely remove a directory"""
        try:
            if self.dry_run:
                logger.info(f"[DRY RUN] Would remove {category}: {dir_path}")
                return True

            # Calculate directory size
            dir_size = sum(f.stat().st_size for f in dir_path.rglob("*") if f.is_file())

            shutil.rmtree(dir_path)

            self.removed_dirs.append(dir_path)
            self.total_size_freed += dir_size
            logger.info(f"  🗂️  Removed {category}: {dir_path}")
            return True

        except Exception as e:
            logger.error(f"  ❌ Failed to remove directory {dir_path}: {e}")
            return False

    def should_preserve_file(self, file_path: Path) -> bool:
        """Check if file should be preserved"""
        preserve_patterns = [
            ".git/",
            ".venv/",
            "node_modules/",
            ".env",
            "requirements.txt",
            "package.json",
            "pyproject.toml",
            "uv.lock",
        ]

        file_str = str(file_path)
        return any(pattern in file_str for pattern in preserve_patterns)

    def cleanup_backup_files(self):
        """Remove all backup files"""
        logger.info("🧹 Cleaning up backup files...")

        cleanup_targets = self.get_cleanup_targets()
        removed_count = 0

        for pattern in cleanup_targets["backup_files"]:
            for file_path in self.root_path.glob(pattern):
                if file_path.is_file() and not self.should_preserve_file(file_path):
                    if self.remove_file(file_path, "backup file"):
                        removed_count += 1

        logger.info(f"  ✅ Removed {removed_count} backup files")

    def cleanup_backup_directories(self):
        """Remove all backup directories"""
        logger.info("🗂️  Cleaning up backup directories...")

        cleanup_targets = self.get_cleanup_targets()
        removed_count = 0

        for pattern in cleanup_targets["backup_directories"]:
            for dir_path in self.root_path.glob(pattern):
                if dir_path.is_dir() and not self.should_preserve_file(dir_path):
                    if self.remove_directory(dir_path, "backup directory"):
                        removed_count += 1

        logger.info(f"  ✅ Removed {removed_count} backup directories")

    def cleanup_duplicate_scripts(self):
        """Remove duplicate and conflicting scripts"""
        logger.info("🔄 Cleaning up duplicate scripts...")

        cleanup_targets = self.get_cleanup_targets()
        removed_count = 0

        for script_path in cleanup_targets["duplicate_scripts"]:
            file_path = self.root_path / script_path
            if file_path.exists():
                if self.remove_file(file_path, "duplicate script"):
                    removed_count += 1

        logger.info(f"  ✅ Removed {removed_count} duplicate scripts")

    def cleanup_cache_and_temp(self):
        """Remove cache and temporary files"""
        logger.info("🧽 Cleaning up cache and temporary files...")

        cleanup_targets = self.get_cleanup_targets()
        removed_count = 0

        for pattern in cleanup_targets["cache_and_temp"]:
            for path in self.root_path.glob(pattern):
                if not self.should_preserve_file(path):
                    if path.is_file():
                        if self.remove_file(path, "cache/temp file"):
                            removed_count += 1
                    elif path.is_dir():
                        if self.remove_directory(path, "cache/temp directory"):
                            removed_count += 1

        logger.info(f"  ✅ Removed {removed_count} cache/temp items")

    def cleanup_dead_configs(self):
        """Remove dead configuration files"""
        logger.info("⚙️  Cleaning up dead configuration files...")

        cleanup_targets = self.get_cleanup_targets()
        removed_count = 0

        for config_path in cleanup_targets["dead_configs"]:
            file_path = self.root_path / config_path
            if file_path.exists():
                if file_path.is_file():
                    if self.remove_file(file_path, "dead config"):
                        removed_count += 1
                elif file_path.is_dir():
                    if self.remove_directory(file_path, "dead config directory"):
                        removed_count += 1

        logger.info(f"  ✅ Removed {removed_count} dead config items")

    def cleanup_watched_files(self):
        """Remove unused watched file directories"""
        logger.info("👁️  Cleaning up unused watched file directories...")

        cleanup_targets = self.get_cleanup_targets()
        removed_count = 0

        for watched_path in cleanup_targets["watched_files"]:
            dir_path = self.root_path / watched_path
            if dir_path.exists() and dir_path.is_dir():
                # Check if directory is empty or contains only temp files
                files = list(dir_path.rglob("*"))
                if len(files) == 0 or all(f.name.startswith(".") for f in files):
                    if self.remove_directory(dir_path, "unused watched directory"):
                        removed_count += 1

        logger.info(f"  ✅ Removed {removed_count} unused watched directories")

    def generate_cleanup_report(self):
        """Generate final cleanup report"""
        logger.info("📊 Generating cleanup report...")

        size_mb = self.total_size_freed / (1024 * 1024)

        report = f"""# Sophia AI Comprehensive Cleanup Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- Files removed: {len(self.removed_files)}
- Directories removed: {len(self.removed_dirs)}
- Total space freed: {size_mb:.2f} MB

## Categories Cleaned
✅ Backup files (.bak, .backup, .old, .orig)
✅ Backup directories (uv_migration_backups, docs_backup, backups)
✅ Duplicate and conflicting scripts
✅ Cache and temporary files
✅ Dead configuration files
✅ Unused watched file directories

## Files Removed
"""

        if self.removed_files:
            report += "\n### Files:\n"
            for file_path in sorted(self.removed_files):
                report += f"- {file_path}\n"

        if self.removed_dirs:
            report += "\n### Directories:\n"
            for dir_path in sorted(self.removed_dirs):
                report += f"- {dir_path}/\n"

        report_file = Path("CLEANUP_REPORT.md")
        if not self.dry_run:
            with open(report_file, "w") as f:
                f.write(report)
            logger.info(f"📄 Cleanup report saved to {report_file}")
        else:
            logger.info("[DRY RUN] Cleanup report:")
            print(report)

    def run_comprehensive_cleanup(self):
        """Execute comprehensive cleanup"""
        logger.info("🚀 Starting Comprehensive Dead Code Cleanup")
        logger.info("=" * 60)

        if self.dry_run:
            logger.info("🔍 DRY RUN MODE - No files will be actually removed")
        else:
            logger.info("⚠️  LIVE MODE - Files will be permanently removed")

            # Create final backup
            if not self.create_final_backup():
                logger.error("❌ Failed to create backup - aborting cleanup")
                return False

        # Execute cleanup phases
        self.cleanup_backup_files()
        self.cleanup_backup_directories()
        self.cleanup_duplicate_scripts()
        self.cleanup_cache_and_temp()
        self.cleanup_dead_configs()
        self.cleanup_watched_files()

        # Generate report
        self.generate_cleanup_report()

        logger.info("🎉 Comprehensive cleanup completed successfully!")
        logger.info(
            f"📊 Summary: {len(self.removed_files)} files, {len(self.removed_dirs)} directories removed"
        )
        logger.info(f"💾 Space freed: {self.total_size_freed / (1024 * 1024):.2f} MB")

        if not self.dry_run:
            logger.info(f"📦 Final backup saved at: {self.final_backup_dir}")

        return True


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Comprehensive dead code cleanup for Sophia AI"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be removed without actually removing",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually execute the cleanup (removes files)",
    )

    args = parser.parse_args()

    if not args.dry_run and not args.execute:
        logger.info("Use --dry-run to preview or --execute to run cleanup")
        parser.print_help()
        return 1

    cleanup = ComprehensiveDeadCodeCleanup(dry_run=args.dry_run)

    if cleanup.run_comprehensive_cleanup():
        logger.info("✅ Cleanup completed successfully")
        return 0
    else:
        logger.error("❌ Cleanup failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
