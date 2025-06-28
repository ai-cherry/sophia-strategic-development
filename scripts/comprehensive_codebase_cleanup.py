#!/usr/bin/env python3
"""
Comprehensive Codebase Cleanup for Sophia AI
Identifies and removes duplications, conflicts, and confusion throughout the codebase
"""

import shutil
import json
import logging
from datetime import datetime
from pathlib import Path
import hashlib
import re

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ComprehensiveCodebaseCleanup:
    """Comprehensive cleanup tool for Sophia AI codebase"""

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.root_path = Path(".")
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = Path(f"cleanup_backup_{self.timestamp}")
        self.cleanup_report = {
            "timestamp": self.timestamp,
            "dry_run": dry_run,
            "removed_files": [],
            "consolidated_files": [],
            "conflicts_resolved": [],
            "duplicates_removed": [],
            "errors": [],
        }

    def run_comprehensive_cleanup(self):
        """Execute comprehensive cleanup"""
        logger.info("🧹 Starting Comprehensive Codebase Cleanup")
        logger.info("=" * 60)

        if not self.dry_run:
            self.backup_dir.mkdir(exist_ok=True)
            logger.info(f"📦 Backup directory created: {self.backup_dir}")

        # Step 1: Remove obvious backup and duplicate files
        self.remove_backup_files()

        # Step 2: Consolidate duplicate configuration files
        self.consolidate_configuration_files()

        # Step 3: Remove duplicate ESLint configurations
        self.consolidate_eslint_configs()

        # Step 4: Clean up requirements files
        self.consolidate_requirements_files()

        # Step 5: Remove duplicate documentation
        self.remove_duplicate_documentation()

        # Step 6: Clean up archive directories
        self.clean_archive_directories()

        # Step 7: Remove temporary and junk files
        self.remove_temporary_files()

        # Step 8: Resolve import conflicts
        self.resolve_import_conflicts()

        # Generate final report
        self.generate_cleanup_report()

    def remove_backup_files(self):
        """Remove obvious backup files"""
        logger.info("🗑️  Removing backup files...")

        backup_patterns = ["*.backup", "*.bak", "*_backup.*", "*_old.*", "*.orig", "*~"]

        removed_count = 0
        for pattern in backup_patterns:
            for file_path in self.root_path.rglob(pattern):
                if self._should_remove_file(file_path):
                    self._remove_file(file_path, "backup_file")
                    removed_count += 1

        # Specific backup files identified
        specific_backups = [
            "backend/app/fastapi_app.py.backup",
            "backend/mcp/costar_mcp_server.py.backup",
            "scripts/ingest_costar_data.py.backup",
        ]

        for backup_file in specific_backups:
            file_path = self.root_path / backup_file
            if file_path.exists():
                self._remove_file(file_path, "specific_backup")
                removed_count += 1

        logger.info(f"   Removed {removed_count} backup files")

    def consolidate_configuration_files(self):
        """Consolidate duplicate configuration files"""
        logger.info("⚙️  Consolidating configuration files...")

        # Handle duplicate ESLint configs
        eslint_configs = [
            "frontend/eslint.config.js",
            "frontend/knowledge-admin/eslint.config.js",
            "sophia-dashboard/eslint.config.js",
        ]

        # Keep the main frontend one, remove duplicates
        main_eslint = self.root_path / "frontend/eslint.config.js"
        if main_eslint.exists():
            for config_path in eslint_configs[1:]:  # Skip the first (main) one
                file_path = self.root_path / config_path
                if file_path.exists() and self._files_are_identical(
                    main_eslint, file_path
                ):
                    self._remove_file(file_path, "duplicate_eslint_config")

        # Handle duplicate jsconfig.json files
        jsconfig_files = [
            "frontend/jsconfig.json",
            "frontend/knowledge-admin/jsconfig.json",
            "sophia-dashboard/jsconfig.json",
        ]

        # Keep frontend/jsconfig.json as the main one
        main_jsconfig = self.root_path / "frontend/jsconfig.json"
        if main_jsconfig.exists():
            for config_path in jsconfig_files[1:]:
                file_path = self.root_path / config_path
                if file_path.exists() and self._files_are_similar(
                    main_jsconfig, file_path
                ):
                    self._remove_file(file_path, "duplicate_jsconfig")

        # Remove redundant .eslintrc.json (superseded by eslint.config.js)
        eslintrc_path = self.root_path / "frontend/.eslintrc.json"
        if eslintrc_path.exists():
            self._remove_file(eslintrc_path, "superseded_eslintrc")

    def consolidate_eslint_configs(self):
        """Consolidate ESLint configurations"""
        logger.info("📝 Consolidating ESLint configurations...")

        # Create a unified ESLint config at the root
        unified_eslint_config = {
            "root": True,
            "env": {"browser": True, "es2021": True, "node": True},
            "extends": ["eslint:recommended", "@typescript-eslint/recommended"],
            "parser": "@typescript-eslint/parser",
            "parserOptions": {"ecmaVersion": "latest", "sourceType": "module"},
            "plugins": ["@typescript-eslint"],
            "rules": {
                "@typescript-eslint/no-explicit-any": "warn",
                "@typescript-eslint/explicit-module-boundary-types": "off",
                "no-unused-vars": ["error", {"varsIgnorePattern": "^[A-Z_]"}],
            },
            "overrides": [
                {
                    "files": ["frontend/**/*.{js,jsx,ts,tsx}"],
                    "extends": [
                        "plugin:react/recommended",
                        "plugin:react-hooks/recommended",
                    ],
                    "plugins": ["react", "react-hooks", "react-refresh"],
                    "rules": {
                        "react/react-in-jsx-scope": "off",
                        "react/prop-types": "off",
                        "react-refresh/only-export-components": [
                            "warn",
                            {"allowConstantExport": True},
                        ],
                    },
                    "settings": {"react": {"version": "detect"}},
                }
            ],
        }

        root_eslint_path = self.root_path / ".eslintrc.json"
        if not self.dry_run:
            with open(root_eslint_path, "w") as f:
                json.dump(unified_eslint_config, f, indent=2)
            logger.info(f"   Created unified ESLint config: {root_eslint_path}")

    def consolidate_requirements_files(self):
        """Consolidate and clean up requirements files"""
        logger.info("📦 Consolidating requirements files...")

        # Find all requirements.txt files
        requirements_files = list(self.root_path.rglob("requirements.txt"))
        logger.info(f"   Found {len(requirements_files)} requirements.txt files")

        # Keep the main requirements.txt, document others
        main_requirements = self.root_path / "requirements.txt"
        specialized_requirements = []

        for req_file in requirements_files:
            if req_file != main_requirements:
                # Check if it's a specialized requirements file that should be kept
                if any(
                    component in str(req_file)
                    for component in ["mcp-servers", "infrastructure", "gong-webhook"]
                ):
                    specialized_requirements.append(req_file)
                    logger.info(f"   Keeping specialized requirements: {req_file}")
                else:
                    # Check if it's identical to main requirements
                    if main_requirements.exists() and self._files_are_identical(
                        main_requirements, req_file
                    ):
                        self._remove_file(req_file, "duplicate_requirements")

        # Clean up requirements-dev.txt patterns
        dev_requirements_pattern = list(self.root_path.rglob("requirements-dev.txt"))
        for dev_req in dev_requirements_pattern:
            # Only keep if it's not a duplicate
            if "docs_archive" not in str(dev_req):
                logger.info(f"   Keeping dev requirements: {dev_req}")
            else:
                self._remove_file(dev_req, "archived_dev_requirements")

    def remove_duplicate_documentation(self):
        """Remove duplicate documentation files"""
        logger.info("📚 Removing duplicate documentation...")

        # Remove numbered duplicates (file 2.md, file 3.md, etc.)
        duplicate_patterns = [
            "**/*[[:space:]]2.md",
            "**/*[[:space:]]3.md",
            "**/*[[:space:]]4.md",
            "**/*[[:space:]]5.md",
            "**/*_2.md",
            "**/*_3.md",
            "**/*_4.md",
        ]

        removed_count = 0
        for pattern in duplicate_patterns:
            # Use glob to find files matching pattern
            for file_path in self.root_path.glob(pattern.replace("[[:space:]]", " ")):
                if self._should_remove_file(file_path):
                    self._remove_file(file_path, "duplicate_documentation")
                    removed_count += 1

        # Remove specific duplicate docs identified
        specific_duplicates = [
            "docs/ARCHITECTURE_REVIEW_SUMMARY 2.md",
            "docs/ARCHITECTURE_REVIEW_SUMMARY 3.md",
            "docs/ARCHITECTURE_REVIEW_SUMMARY 4.md",
            "docs/ENHANCED_ARCHITECTURE_RECOMMENDATIONS 2.md",
            "docs/ENHANCED_ARCHITECTURE_RECOMMENDATIONS 3.md",
        ]

        for doc_file in specific_duplicates:
            file_path = self.root_path / doc_file
            if file_path.exists():
                self._remove_file(file_path, "specific_duplicate_doc")
                removed_count += 1

        logger.info(f"   Removed {removed_count} duplicate documentation files")

    def clean_archive_directories(self):
        """Clean up archive directories"""
        logger.info("🗂️  Cleaning archive directories...")

        # Find archive directories
        archive_patterns = ["docs_archive_*", "archive/modernization_*", "*_archive_*"]

        archived_count = 0
        for pattern in archive_patterns:
            for archive_path in self.root_path.glob(pattern):
                if archive_path.is_dir():
                    # Move to backup instead of deleting
                    if not self.dry_run:
                        backup_archive_path = self.backup_dir / archive_path.name
                        shutil.move(str(archive_path), str(backup_archive_path))
                        logger.info(f"   Moved archive to backup: {archive_path}")
                    else:
                        logger.info(f"   Would move archive: {archive_path}")
                    archived_count += 1

        logger.info(f"   Processed {archived_count} archive directories")

    def remove_temporary_files(self):
        """Remove temporary and junk files"""
        logger.info("🧽 Removing temporary files...")

        temp_patterns = [
            "**/*.pyc",
            "**/__pycache__",
            "**/.DS_Store",
            "**/*.tmp",
            "**/*.temp",
            "**/node_modules/.cache",
            "**/.pytest_cache",
            "**/.mypy_cache",
        ]

        removed_count = 0
        for pattern in temp_patterns:
            for temp_path in self.root_path.rglob(pattern.replace("**/", "")):
                if self._should_remove_file(temp_path):
                    if temp_path.is_dir():
                        self._remove_directory(temp_path, "temp_directory")
                    else:
                        self._remove_file(temp_path, "temp_file")
                    removed_count += 1

        logger.info(f"   Removed {removed_count} temporary files/directories")

    def resolve_import_conflicts(self):
        """Resolve import conflicts and circular dependencies"""
        logger.info("🔄 Resolving import conflicts...")

        # Check for aioredis vs redis.asyncio conflicts
        python_files = list(self.root_path.rglob("*.py"))
        conflicts_resolved = 0

        for py_file in python_files:
            if self._should_process_file(py_file):
                try:
                    with open(py_file, "r", encoding="utf-8") as f:
                        content = f.read()

                    original_content = content

                    # Fix aioredis imports to use redis.asyncio
                    content = re.sub(
                        r"import aioredis",
                        "import redis.asyncio as redis_client",
                        content,
                    )
                    content = re.sub(
                        r"from aioredis import", "from redis.asyncio import", content
                    )

                    # Fix direct aioredis usage
                    content = re.sub(r"aioredis\.", "redis_client.", content)

                    if content != original_content:
                        if not self.dry_run:
                            with open(py_file, "w", encoding="utf-8") as f:
                                f.write(content)
                        logger.info(f"   Fixed import conflicts in: {py_file}")
                        conflicts_resolved += 1
                        self.cleanup_report["conflicts_resolved"].append(str(py_file))

                except Exception as e:
                    logger.error(f"   Error processing {py_file}: {e}")
                    self.cleanup_report["errors"].append(
                        f"Import conflict resolution failed for {py_file}: {e}"
                    )

        logger.info(f"   Resolved {conflicts_resolved} import conflicts")

    def _should_remove_file(self, file_path: Path) -> bool:
        """Determine if a file should be removed"""
        # Don't remove files in git directories
        if ".git" in str(file_path):
            return False

        # Don't remove files in node_modules
        if "node_modules" in str(file_path):
            return False

        # Don't remove files in virtual environments
        if any(venv in str(file_path) for venv in [".venv", "venv", "env"]):
            return False

        return True

    def _should_process_file(self, file_path: Path) -> bool:
        """Determine if a file should be processed"""
        return self._should_remove_file(file_path) and file_path.suffix == ".py"

    def _files_are_identical(self, file1: Path, file2: Path) -> bool:
        """Check if two files are identical"""
        try:
            with open(file1, "rb") as f1, open(file2, "rb") as f2:
                return (
                    hashlib.md5(f1.read(), usedforsecurity=False).hexdigest()
                    == hashlib.md5(f2.read(), usedforsecurity=False).hexdigest()
                )
        except Exception:
            return False

    def _files_are_similar(self, file1: Path, file2: Path) -> bool:
        """Check if two files are similar (ignoring minor differences)"""
        try:
            with open(file1, "r") as f1, open(file2, "r") as f2:
                content1 = f1.read().strip()
                content2 = f2.read().strip()
                # Simple similarity check - can be enhanced
                return abs(len(content1) - len(content2)) < 100
        except Exception:
            return False

    def _remove_file(self, file_path: Path, reason: str):
        """Remove a file with backup"""
        if not self.dry_run:
            # Create backup
            backup_path = self.backup_dir / file_path.relative_to(self.root_path)
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, backup_path)

            # Remove original
            file_path.unlink()

        logger.info(f"   Removed ({reason}): {file_path}")
        self.cleanup_report["removed_files"].append(
            {"path": str(file_path), "reason": reason, "backed_up": not self.dry_run}
        )

    def _remove_directory(self, dir_path: Path, reason: str):
        """Remove a directory with backup"""
        if not self.dry_run:
            # Create backup
            backup_path = self.backup_dir / dir_path.relative_to(self.root_path)
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(dir_path, backup_path)

            # Remove original
            shutil.rmtree(dir_path)

        logger.info(f"   Removed directory ({reason}): {dir_path}")
        self.cleanup_report["removed_files"].append(
            {
                "path": str(dir_path),
                "reason": reason,
                "type": "directory",
                "backed_up": not self.dry_run,
            }
        )

    def generate_cleanup_report(self):
        """Generate comprehensive cleanup report"""
        logger.info("📊 Generating cleanup report...")

        report_file = f"cleanup_report_{self.timestamp}.json"

        # Add summary statistics
        self.cleanup_report["summary"] = {
            "total_files_removed": len(self.cleanup_report["removed_files"]),
            "conflicts_resolved": len(self.cleanup_report["conflicts_resolved"]),
            "errors_encountered": len(self.cleanup_report["errors"]),
            "backup_location": str(self.backup_dir) if not self.dry_run else None,
        }

        if not self.dry_run:
            with open(report_file, "w") as f:
                json.dump(self.cleanup_report, f, indent=2)

        logger.info("=" * 60)
        logger.info("🎉 Comprehensive Cleanup Complete!")
        logger.info("=" * 60)
        logger.info(
            f"📁 Files removed: {self.cleanup_report['summary']['total_files_removed']}"
        )
        logger.info(
            f"🔧 Conflicts resolved: {self.cleanup_report['summary']['conflicts_resolved']}"
        )
        logger.info(
            f"❌ Errors: {self.cleanup_report['summary']['errors_encountered']}"
        )

        if not self.dry_run:
            logger.info(f"💾 Backup location: {self.backup_dir}")
            logger.info(f"📋 Report saved: {report_file}")
        else:
            logger.info("🔍 This was a dry run - no files were actually modified")

        return self.cleanup_report


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Comprehensive Codebase Cleanup for Sophia AI"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually execute cleanup (default is dry-run)",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    dry_run = not args.execute

    if dry_run:
        logger.info("🔍 Running in DRY-RUN mode - no files will be modified")
        logger.info("   Use --execute to actually perform cleanup")
    else:
        logger.info("⚠️  EXECUTING CLEANUP - files will be modified!")

    cleanup = ComprehensiveCodebaseCleanup(dry_run=dry_run)
    report = cleanup.run_comprehensive_cleanup()

    return report


if __name__ == "__main__":
    main()
