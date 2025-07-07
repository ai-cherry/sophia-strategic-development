#!/usr/bin/env python3
"""
Deep Audit Cleanup Script for Sophia AI
Gracefully implements recommendations from the deep audit report.
Focuses on safe deletion of non-production artifacts while preserving value.

Usage:
    python scripts/deep_audit_cleanup.py --scan        # Scan and report
    python scripts/deep_audit_cleanup.py --execute     # Execute cleanup
    python scripts/deep_audit_cleanup.py --archive     # Archive legacy files
"""

import argparse
import json
import shutil
import sys
import tarfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from backend.utils.custom_logger import setup_logger

    logger = setup_logger("deep_audit_cleanup")
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("deep_audit_cleanup")


class DeepAuditCleanup:
    """Implements deep audit cleanup recommendations gracefully"""

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path.cwd()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Categories from the deep audit report
        self.cleanup_categories = {
            "simplified_versions": {
                "description": "Simplified/mock versions that confuse production clarity",
                "patterns": [
                    "backup_compose_files/docker-compose.simple.yml",
                    "backup_compose_files/docker-compose.staging-simple.yml",
                    "backups/llm_cleanup_*/simplified_*.py",
                    "**/*simple*.yml",
                    "**/*simplified*.py",
                    "**/*mock*.py",
                    "**/*stub*.py",
                ],
                "action": "delete",
                "risk": "none",
                "reason": "Non-production workarounds harmful to clarity",
            },
            "one_time_scripts": {
                "description": "One-time fix/deployment/test scripts",
                "patterns": [
                    "backups/scripts_cleanup_*/fix_*.py",
                    "backups/scripts_cleanup_*/deploy_*.py",
                    "backups/scripts_cleanup_*/test_*.py",
                    "backups/scripts_cleanup_*/cleanup_*.py",
                    "backups/scripts_cleanup_*/validate_*.py",
                    "backups/scripts_cleanup_*/migrate_*.py",
                ],
                "action": "delete",
                "risk": "low",
                "reason": "Temporary scripts that should not be kept",
            },
            "backup_deployment_fixes": {
                "description": "Backup deployment fix directories",
                "patterns": [
                    "backup_deployment_fix_*/**/*.yml",
                    "backup_deployment_fix_*/**/*.py",
                    "backup_deployment_fix_*/**/*.sh",
                ],
                "action": "archive",
                "risk": "low",
                "reason": "Historical value but clutters active development",
            },
            "legacy_docker_compose": {
                "description": "Legacy Docker Compose configurations",
                "patterns": [
                    "backup_compose_files/docker-compose.ai.yml",
                    "backup_compose_files/docker-compose.containerized.yml",
                    "backup_compose_files/docker-compose.lambda.yml",
                    "backup_compose_files/docker-compose.mcp*.yml",
                    "backup_compose_files/docker-compose.monitoring.yml",
                    "backup_compose_files/docker-compose.*.yml",
                ],
                "action": "archive",
                "risk": "low",
                "reason": "Superseded by current deployment strategy",
            },
            "llm_migration_backups": {
                "description": "LLM migration snapshot directories",
                "patterns": [
                    "backups/llm_migration_*/**",
                    "backups/llm_cleanup_*/**",
                ],
                "action": "archive",
                "risk": "low",
                "reason": "Historical snapshots, not needed for operations",
            },
            "docs_backup_directories": {
                "description": "Documentation backup directories",
                "patterns": [
                    "docs_backup_*/**",
                ],
                "action": "archive",
                "risk": "low",
                "reason": "Redundant with version control",
            },
        }

        self.scan_results = {
            "timestamp": self.timestamp,
            "categories": {},
            "summary": {
                "total_files": 0,
                "delete_candidates": 0,
                "archive_candidates": 0,
                "size_to_recover_mb": 0,
            },
        }

    def scan(self) -> dict:
        """Scan for files matching deep audit patterns"""
        logger.info("🔍 Starting deep audit scan...")

        for category, config in self.cleanup_categories.items():
            logger.info(f"\n📊 Scanning: {config['description']}")
            matches = []
            total_size = 0

            for pattern in config["patterns"]:
                for path in self.project_root.glob(pattern):
                    if path.is_file():
                        size = path.stat().st_size
                        matches.append(
                            {
                                "path": str(path.relative_to(self.project_root)),
                                "size": size,
                                "modified": datetime.fromtimestamp(
                                    path.stat().st_mtime
                                ).isoformat(),
                            }
                        )
                        total_size += size

            self.scan_results["categories"][category] = {
                "description": config["description"],
                "action": config["action"],
                "risk": config["risk"],
                "reason": config["reason"],
                "matches": matches,
                "count": len(matches),
                "size_mb": round(total_size / 1024 / 1024, 2),
            }

            logger.info(
                f"   Found: {len(matches)} files ({round(total_size / 1024 / 1024, 2)} MB)"
            )

            # Update summary
            self.scan_results["summary"]["total_files"] += len(matches)
            if config["action"] == "delete":
                self.scan_results["summary"]["delete_candidates"] += len(matches)
            else:
                self.scan_results["summary"]["archive_candidates"] += len(matches)
            self.scan_results["summary"]["size_to_recover_mb"] += round(
                total_size / 1024 / 1024, 2
            )

        return self.scan_results

    def execute_cleanup(self, dry_run: bool = True) -> dict:
        """Execute the cleanup based on scan results"""
        results = {"deleted": [], "archived": [], "errors": [], "backup_path": None}

        if dry_run:
            logger.info("🧪 DRY RUN MODE - No files will be modified")
        else:
            # Create backup first
            backup_path = self._create_backup()
            results["backup_path"] = str(backup_path)
            logger.info(f"✅ Backup created: {backup_path}")

        for category, data in self.scan_results["categories"].items():
            if not data["matches"]:
                continue

            logger.info(f"\n🧹 Processing: {data['description']}")
            logger.info(f"   Action: {data['action'].upper()}")
            logger.info(f"   Risk: {data['risk']}")

            for file_info in data["matches"]:
                file_path = self.project_root / file_info["path"]

                try:
                    if data["action"] == "delete":
                        if dry_run:
                            logger.info(
                                f"   [DRY RUN] Would delete: {file_info['path']}"
                            )
                        else:
                            file_path.unlink()
                            results["deleted"].append(file_info["path"])
                            logger.info(f"   ✅ Deleted: {file_info['path']}")

                    elif data["action"] == "archive":
                        archive_dest = self._get_archive_destination(
                            category, file_path
                        )
                        if dry_run:
                            logger.info(
                                f"   [DRY RUN] Would archive: {file_info['path']} → {archive_dest}"
                            )
                        else:
                            self._archive_file(file_path, archive_dest)
                            results["archived"].append(
                                {
                                    "source": file_info["path"],
                                    "destination": str(archive_dest),
                                }
                            )
                            logger.info(f"   📦 Archived: {file_info['path']}")

                except Exception as e:
                    error_msg = f"Error processing {file_info['path']}: {e}"
                    results["errors"].append(error_msg)
                    logger.error(f"   ❌ {error_msg}")

        return results

    def create_archive_structure(self) -> Path:
        """Create the recommended archive directory structure"""
        archive_root = self.project_root / "archive"

        subdirs = [
            "docker-compose-history",
            "github-actions-history",
            "migration-snapshots",
            "infrastructure-evolution",
            "scripts-cleanup",
            "docs-backups",
        ]

        for subdir in subdirs:
            (archive_root / subdir).mkdir(parents=True, exist_ok=True)

        # Create README
        readme_content = f"""# Sophia AI Archive Directory

Created: {datetime.now().isoformat()}

This directory contains historical artifacts that have been archived to maintain
a clean working repository while preserving valuable historical context.

## Structure

- `docker-compose-history/` - Legacy Docker Compose configurations
- `github-actions-history/` - Old GitHub Actions workflows
- `migration-snapshots/` - Snapshots from major migrations
- `infrastructure-evolution/` - Evolution of deployment strategies
- `scripts-cleanup/` - One-time scripts and temporary fixes
- `docs-backups/` - Documentation backup directories

## Retention Policy

- Migration snapshots: 1 year
- Deployment configs: 6 months
- Scripts and fixes: 3 months
- Documentation backups: 3 months

## Access

These files are compressed and archived. To access:
```bash
tar -xzf archive_name.tar.gz
```
"""

        (archive_root / "README.md").write_text(readme_content)
        logger.info(f"✅ Created archive structure at: {archive_root}")

        return archive_root

    def _create_backup(self) -> Path:
        """Create a backup before cleanup operations"""
        backup_dir = self.project_root / f"deep_audit_backup_{self.timestamp}"
        backup_dir.mkdir(exist_ok=True)

        # Save scan results
        (backup_dir / "scan_results.json").write_text(
            json.dumps(self.scan_results, indent=2)
        )

        # Copy files to be deleted/archived
        for category, data in self.scan_results["categories"].items():
            if not data["matches"]:
                continue

            category_dir = backup_dir / category
            category_dir.mkdir(exist_ok=True)

            for file_info in data["matches"]:
                src = self.project_root / file_info["path"]
                if src.exists():
                    dst = category_dir / file_info["path"].replace("/", "_")
                    shutil.copy2(src, dst)

        return backup_dir

    def _get_archive_destination(self, category: str, file_path: Path) -> Path:
        """Determine appropriate archive destination for a file"""
        archive_root = self.project_root / "archive"

        # Map categories to archive subdirectories
        category_map = {
            "backup_deployment_fixes": "infrastructure-evolution",
            "legacy_docker_compose": "docker-compose-history",
            "llm_migration_backups": "migration-snapshots",
            "docs_backup_directories": "docs-backups",
        }

        subdir = category_map.get(category, "misc")
        timestamp = datetime.now().strftime("%Y%m")

        return archive_root / subdir / f"{category}_{timestamp}.tar.gz"

    def _archive_file(self, source: Path, archive_path: Path):
        """Archive a file or directory to compressed tar"""
        archive_path.parent.mkdir(parents=True, exist_ok=True)

        # If archive exists, add to it; otherwise create new
        mode = "a:gz" if archive_path.exists() else "w:gz"

        with tarfile.open(archive_path, mode) as tar:
            arcname = source.relative_to(self.project_root)
            tar.add(source, arcname=str(arcname))

        # Remove original after successful archival
        if source.is_dir():
            shutil.rmtree(source)
        else:
            source.unlink()

    def generate_report(self, results: dict | None = None):
        """Generate a comprehensive cleanup report"""
        report_path = (
            self.project_root / f"deep_audit_cleanup_report_{self.timestamp}.md"
        )

        report = f"""# Deep Audit Cleanup Report

**Generated**: {datetime.now().isoformat()}
**Mode**: {'DRY RUN' if results is None else 'EXECUTED'}

## 📊 Scan Summary

- **Total files identified**: {self.scan_results['summary']['total_files']}
- **Delete candidates**: {self.scan_results['summary']['delete_candidates']}
- **Archive candidates**: {self.scan_results['summary']['archive_candidates']}
- **Total size to recover**: {self.scan_results['summary']['size_to_recover_mb']} MB

## 📋 Category Breakdown

"""

        for category, data in self.scan_results["categories"].items():
            if data["count"] > 0:
                report += f"""### {data['description']}
- **Action**: {data['action'].upper()}
- **Risk**: {data['risk']}
- **Reason**: {data['reason']}
- **Files**: {data['count']}
- **Size**: {data['size_mb']} MB

"""

        if results:
            report += f"""## ✅ Execution Results

- **Files deleted**: {len(results['deleted'])}
- **Files archived**: {len(results['archived'])}
- **Errors**: {len(results['errors'])}
- **Backup location**: {results['backup_path']}

"""

            if results["errors"]:
                report += "### ❌ Errors\n\n"
                for error in results["errors"]:
                    report += f"- {error}\n"

        report += """## 🎯 Next Steps

1. Review the results and validate the cleanup
2. Update documentation with any extracted insights
3. Configure automated prevention for future accumulation
4. Monitor repository health metrics

## 🛡️ Prevention

The following systems are now in place to prevent future accumulation:
- Enhanced AI Junk Prevention Service
- Pre-commit hooks for dead code patterns
- Weekly GitHub Actions scanning
- Automated retention policies
"""

        report_path.write_text(report)
        logger.info(f"📄 Report saved: {report_path}")

        return report_path


def main():
    parser = argparse.ArgumentParser(description="Deep Audit Cleanup for Sophia AI")
    parser.add_argument(
        "--scan",
        action="store_true",
        help="Scan for files matching deep audit patterns",
    )
    parser.add_argument(
        "--execute", action="store_true", help="Execute cleanup (delete/archive files)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Perform dry run (default: True)",
    )
    parser.add_argument(
        "--archive", action="store_true", help="Create archive directory structure"
    )
    parser.add_argument(
        "--report",
        choices=["console", "markdown", "json"],
        default="console",
        help="Report format",
    )

    args = parser.parse_args()

    cleanup = DeepAuditCleanup()

    if args.archive:
        cleanup.create_archive_structure()
        return

    # Always scan first
    scan_results = cleanup.scan()

    # Generate summary
    logger.info("\n📊 SCAN SUMMARY")
    logger.info("=" * 50)
    logger.info(f"Total files found: {scan_results['summary']['total_files']}")
    logger.info(f"Files to delete: {scan_results['summary']['delete_candidates']}")
    logger.info(f"Files to archive: {scan_results['summary']['archive_candidates']}")
    logger.info(f"Space to recover: {scan_results['summary']['size_to_recover_mb']} MB")

    if args.execute:
        if args.dry_run:
            logger.info("\n🧪 Running in DRY RUN mode...")
            results = cleanup.execute_cleanup(dry_run=True)
        else:
            logger.info("\n⚠️  EXECUTING CLEANUP - This will modify files!")
            confirm = input("Are you sure? (yes/no): ")
            if confirm.lower() == "yes":
                results = cleanup.execute_cleanup(dry_run=False)
                cleanup.generate_report(results)
            else:
                logger.info("❌ Cleanup cancelled")
                return

    if args.report == "json":
        print(json.dumps(scan_results, indent=2))
    elif args.report == "markdown":
        cleanup.generate_report()


if __name__ == "__main__":
    main()
