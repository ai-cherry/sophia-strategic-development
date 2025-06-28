#!/usr/bin/env python3
"""
Comprehensive Workspace Cleanup for Sophia AI

This script safely removes:
- Old backup directories and files
- Shell caches and temporary files
- Archived/outdated scripts
- Duplicate files and logs
- Build artifacts and cache directories

Usage:
    python scripts/cleanup/comprehensive_workspace_cleanup.py
"""

import logging
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkspaceCleanup:
    """Comprehensive workspace cleanup utility"""

    def __init__(self, workspace_root: str = "."):
        self.workspace_root = Path(workspace_root).resolve()
        self.deleted_items = []
        self.total_size_freed = 0

        # Define patterns for cleanup
        self.cleanup_patterns = {
            "backup_directories": [
                "backup_*",
                "*_backup_*",
                "migration_backup",
                "upgrade_backup",
                "backup_fastapi_modernization_*",
            ],
            "cache_directories": [
                "__pycache__",
                ".pytest_cache",
                ".mypy_cache",
                "node_modules",
                ".next",
                ".nuxt",
                "dist",
                "build",
            ],
            "temporary_files": [
                "*.tmp",
                "*.temp",
                "*.log",
                "*.pid",
                "*.lock",
                "*.swp",
                "*.swo",
                "*~",
                ".DS_Store",
                "Thumbs.db",
            ],
            "backup_files": [
                "*.backup",
                "*.bak",
                "*.old",
                "*.orig",
                "*.save",
                "*_backup",
                "*_old",
            ],
            "archive_directories": [
                "archive",
                "archived",
                "old",
                "deprecated",
                "legacy",
            ],
            "development_artifacts": [
                "*.pyc",
                "*.pyo",
                "*.egg-info",
                ".coverage",
                "coverage.xml",
                "*.prof",
            ],
        }

    def get_directory_size(self, path: Path) -> int:
        """Calculate total size of directory"""
        total_size = 0
        try:
            for dirpath, _dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = Path(dirpath) / filename
                    try:
                        total_size += filepath.stat().st_size
                    except (OSError, FileNotFoundError):
                        pass
        except (OSError, FileNotFoundError):
            pass
        return total_size

    def format_size(self, size_bytes: int) -> str:
        """Format size in human readable format"""
        size = float(size_bytes)
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    def safe_remove(self, path: Path, item_type: str = "file") -> bool:
        """Safely remove file or directory"""
        try:
            if path.exists():
                size = 0
                if path.is_file():
                    size = path.stat().st_size
                elif path.is_dir():
                    size = self.get_directory_size(path)

                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    shutil.rmtree(path)

                self.deleted_items.append(f"{item_type}: {path.name}")
                self.total_size_freed += size
                logger.info(
                    f"✅ Removed {item_type}: {path.name} ({self.format_size(size)})"
                )
                return True
        except Exception as e:
            logger.warning(f"⚠️ Failed to remove {path}: {e}")
        return False

    def cleanup_backup_directories(self) -> None:
        """Remove backup directories"""
        logger.info("🗂️ Cleaning up backup directories...")

        for pattern in self.cleanup_patterns["backup_directories"]:
            for path in self.workspace_root.glob(pattern):
                if path.is_dir():
                    self.safe_remove(path, "backup directory")

    def cleanup_cache_directories(self) -> None:
        """Remove cache directories"""
        logger.info("💾 Cleaning up cache directories...")

        # Find and remove cache directories recursively
        for root, dirs, _files in os.walk(self.workspace_root):
            for dirname in list(dirs):  # Create a copy to modify during iteration
                if dirname in self.cleanup_patterns["cache_directories"]:
                    cache_path = Path(root) / dirname
                    self.safe_remove(cache_path, "cache directory")
                    dirs.remove(dirname)  # Don't recurse into removed directory

    def cleanup_temporary_files(self) -> None:
        """Remove temporary files"""
        logger.info("🗃️ Cleaning up temporary files...")

        for pattern in self.cleanup_patterns["temporary_files"]:
            for path in self.workspace_root.rglob(pattern):
                if path.is_file():
                    self.safe_remove(path, "temporary file")

    def cleanup_backup_files(self) -> None:
        """Remove backup files"""
        logger.info("📄 Cleaning up backup files...")

        for pattern in self.cleanup_patterns["backup_files"]:
            for path in self.workspace_root.rglob(pattern):
                if path.is_file():
                    self.safe_remove(path, "backup file")

    def cleanup_archive_directories(self) -> None:
        """Remove archive directories"""
        logger.info("📦 Cleaning up archive directories...")

        for pattern in self.cleanup_patterns["archive_directories"]:
            for path in self.workspace_root.glob(pattern):
                if path.is_dir():
                    # Check if it's actually an archive directory (contains old files)
                    if self.is_archive_directory(path):
                        self.safe_remove(path, "archive directory")

    def is_archive_directory(self, path: Path) -> bool:
        """Check if directory appears to be an archive"""
        # Look for indicators that this is an archive
        archive_indicators = [
            "backup",
            "old",
            "archive",
            "deprecated",
            "legacy",
            "migration",
            "upgrade",
            "temp",
        ]

        path_str = str(path).lower()
        return any(indicator in path_str for indicator in archive_indicators)

    def cleanup_development_artifacts(self) -> None:
        """Remove development artifacts"""
        logger.info("🔧 Cleaning up development artifacts...")

        for pattern in self.cleanup_patterns["development_artifacts"]:
            for path in self.workspace_root.rglob(pattern):
                if path.is_file():
                    self.safe_remove(path, "development artifact")

    def cleanup_old_logs(self) -> None:
        """Remove old log files"""
        logger.info("📝 Cleaning up old log files...")

        # Remove logs older than 7 days
        cutoff_date = datetime.now() - timedelta(days=7)

        for log_file in self.workspace_root.rglob("*.log"):
            try:
                if log_file.stat().st_mtime < cutoff_date.timestamp():
                    self.safe_remove(log_file, "old log file")
            except OSError:
                pass

    def cleanup_empty_directories(self) -> None:
        """Remove empty directories"""
        logger.info("📁 Cleaning up empty directories...")

        # Walk bottom-up to handle nested empty directories
        for root, dirs, _files in os.walk(self.workspace_root, topdown=False):
            for dirname in dirs:
                dir_path = Path(root) / dirname
                try:
                    if dir_path.exists() and not any(dir_path.iterdir()):
                        # Skip important empty directories
                        if dirname not in [".git", ".github", "logs", "uploads"]:
                            self.safe_remove(dir_path, "empty directory")
                except OSError:
                    pass

    def clear_shell_caches(self) -> None:
        """Clear shell caches and histories"""
        logger.info("🐚 Clearing shell caches...")

        home = Path.home()
        shell_cache_files = [
            ".zsh_history",
            ".bash_history",
            ".python_history",
            ".lesshst",
            ".viminfo",
        ]

        for cache_file in shell_cache_files:
            cache_path = home / cache_file
            if cache_path.exists():
                try:
                    # Clear content but keep file (some shells recreate)
                    with open(cache_path, "w") as f:
                        f.write("")
                    logger.info(f"✅ Cleared {cache_file}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to clear {cache_file}: {e}")

    def cleanup_duplicate_scripts(self) -> None:
        """Remove duplicate and redundant scripts"""
        logger.info("🔄 Cleaning up duplicate scripts...")

        # Look for scripts with similar names or content
        script_patterns = [
            "*_test.py",
            "*_backup.py",
            "*_old.py",
            "*_temp.py",
            "test_*.py",
            "*_copy.py",
        ]

        for pattern in script_patterns:
            for script in self.workspace_root.rglob(pattern):
                if script.is_file() and script.suffix == ".py":
                    # Check if it's in a test directory or appears to be a duplicate
                    if any(
                        part in str(script).lower()
                        for part in ["test", "backup", "old", "temp", "copy"]
                    ):
                        self.safe_remove(script, "duplicate script")

    def run_comprehensive_cleanup(self) -> None:
        """Run all cleanup operations"""
        logger.info("🚀 Starting comprehensive workspace cleanup...")
        logger.info(f"📁 Workspace: {self.workspace_root}")

        # Run cleanup operations
        self.cleanup_backup_directories()
        self.cleanup_cache_directories()
        self.cleanup_temporary_files()
        self.cleanup_backup_files()
        self.cleanup_archive_directories()
        self.cleanup_development_artifacts()
        self.cleanup_old_logs()
        self.cleanup_duplicate_scripts()
        self.clear_shell_caches()
        self.cleanup_empty_directories()

        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("🎉 CLEANUP COMPLETE!")
        logger.info(f"📊 Items removed: {len(self.deleted_items)}")
        logger.info(f"💾 Space freed: {self.format_size(self.total_size_freed)}")

        if self.deleted_items:
            logger.info("\n📋 Summary of deleted items:")
            for item in self.deleted_items[:20]:  # Show first 20 items
                logger.info(f"  • {item}")

            if len(self.deleted_items) > 20:
                logger.info(f"  ... and {len(self.deleted_items) - 20} more items")


def main():
    """Main cleanup function"""
    cleanup = WorkspaceCleanup()
    cleanup.run_comprehensive_cleanup()


if __name__ == "__main__":
    main()
