#!/usr/bin/env python3
"""Repository Cleanup Script
Automatically organizes and cleans up the Sophia AI repository
"""

import json
import logging
import shutil
import time
from pathlib import Path
from typing import Dict, List

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RepositoryCleanup:
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.repo_root = Path.cwd()
        self.cleanup_report = {
            "timestamp": time.time(),
            "dry_run": dry_run,
            "actions": [],
            "files_moved": 0,
            "files_deleted": 0,
            "directories_created": 0,
            "total_size_reduced": 0,
        }

    def create_backup(self):
        """Create a backup before cleanup"""
        if not self.dry_run:
            backup_dir = self.repo_root / f"backup_{int(time.time())}"
            logger.info(f"Creating backup at {backup_dir}")
            # Only backup root level files that will be moved/deleted
            backup_dir.mkdir(exist_ok=True)

            files_to_backup = self._get_files_to_move_or_delete()
            for file_path in files_to_backup:
                if file_path.exists():
                    shutil.copy2(file_path, backup_dir / file_path.name)

            self.cleanup_report["backup_location"] = str(backup_dir)
            logger.info(f"Backup created with {len(files_to_backup)} files")

    def create_directory_structure(self):
        """Create the new directory structure"""
        directories = [
            "archive/migrations/scripts",
            "archive/validation/scripts",
            "archive/development",
            "archive/retool",
            "archive/docs/retool",
            "archive/docs/migration",
            "archive/docs/historical",
            "scripts/dev",
            "scripts/deploy",
            "scripts/test",
            "config/environment",
            "config/services",
            "config/dashboards",
            "docs/deployment",
            "docs/guides",
            "docs/reference",
        ]

        for dir_path in directories:
            full_path = self.repo_root / dir_path
            if self.dry_run:
                logger.info(f"[DRY RUN] Would create directory: {dir_path}")
            else:
                full_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created directory: {dir_path}")

            self.cleanup_report["directories_created"] += 1
            self.cleanup_report["actions"].append(
                {
                    "action": "create_directory",
                    "path": dir_path,
                    "status": "dry_run" if self.dry_run else "completed",
                }
            )

    def move_migration_files(self):
        """Move completed migration files to archive"""
        migration_files = {
            # Reports and summaries
            "enhanced_migration_report_enhanced-migration-1750480853.json": "archive/migrations/",
            "next_level_enhancement_report_next-level-1750481373.json": "archive/migrations/",
            "ENHANCED_MIGRATION_SUCCESS_REPORT.md": "archive/migrations/",
            "COMPLETE_TRANSFORMATION_SUMMARY.md": "archive/migrations/",
            "PULUMI_IDP_MIGRATION_PLAN.md": "archive/migrations/",
            # Scripts
            "scripts/migrate_to_pulumi_idp.py": "archive/migrations/scripts/",
            "scripts/enhanced_migration_with_improvements.py": "archive/migrations/scripts/",
            "scripts/implement_next_level_enhancements.py": "archive/migrations/scripts/",
        }

        self._move_files(migration_files, "migration")

    def move_validation_files(self):
        """Move completed validation files to archive"""
        validation_files = {
            "CODEBASE_VALIDATION_PLAN.md": "archive/validation/",
            "VALIDATION_COMPLETION_SUMMARY.md": "archive/validation/",
            "validation_fixes_report.json": "archive/validation/",
            "scripts/comprehensive_validation.sh": "archive/validation/scripts/",
            "scripts/fix_validation_issues.py": "archive/validation/scripts/",
        }

        self._move_files(validation_files, "validation")

    def move_historical_files(self):
        """Move historical development files to archive"""
        historical_files = {
            "advanced_gong_integration_demo_20250617_143948.json": "archive/development/",
            "enhanced_gong_api_testing_20250617_153452.json": "archive/development/",
            "enhanced_gong_test_20250617_141528.json": "archive/development/",
            "ai_memory_test_results.json": "archive/development/",
            "architecture_consistency_report.md": "archive/development/",
            "architecture_inconsistencies_report.md": "archive/development/",
            "architecture_migration_plan.md": "archive/development/",
            "architecture_migration_report.md": "archive/development/",
            "architecture_migration_summary.md": "archive/development/",
        }

        self._move_files(historical_files, "historical")

    def move_retool_files(self):
        """Move Retool migration artifacts to archive"""
        retool_patterns = [
            "retool_*.json",
            "retool_*.md",
            "RETOOL_*.md",
            "build_retool_dashboards_modified.py",
        ]

        import glob

        retool_files = {}

        for pattern in retool_patterns:
            for file_path in glob.glob(str(self.repo_root / pattern)):
                rel_path = Path(file_path).relative_to(self.repo_root)
                retool_files[str(rel_path)] = "archive/retool/"

        self._move_files(retool_files, "retool")

    def organize_scripts(self):
        """Organize remaining scripts into proper subdirectories"""
        script_organization = {
            # Development utilities
            "setup_wizard.py": "scripts/dev/",
            "automated_health_check.py": "scripts/dev/",
            "test_infrastructure.py": "scripts/dev/",
            "validate_infrastructure.py": "scripts/dev/",
            "start_mcp_servers.py": "scripts/dev/",
            "load_env.py": "scripts/dev/",
            # Deployment scripts
            "deploy_production_mcp.py": "scripts/deploy/",
            "deploy_schema.py": "scripts/deploy/",
            "scripts/start_all_services.sh": "scripts/deploy/",
            "scripts/deploy_all_dashboards.py": "scripts/deploy/",
            # Test scripts
            "test_linear_integration.py": "scripts/test/",
            "test_claude_as_code.py": "scripts/test/",
            "test_integrations.py": "scripts/test/",
            "test_ai_memory_deployment.py": "scripts/test/",
            "unified_integration_test.py": "scripts/test/",
        }

        self._move_files(script_organization, "script organization")

    def organize_configuration(self):
        """Organize configuration files"""
        config_files = {
            "env.template": "config/environment/",
            "env.example": "config/environment/",
            "config/portkey.json": "config/services/",
            "config/pulumi-mcp.json": "config/services/",
            "dashboard_config.json": "config/dashboards/",
        }

        self._move_files(config_files, "configuration")

    def delete_obsolete_files(self):
        """Delete obsolete and duplicate files"""
        obsolete_files = [
            # Obsolete Gong Integration Files
            "advanced_gong_integration_prototype.py",
            "enhanced_gong_integration.py",
            "enhanced_gong_api_integration.py",
            "enhanced_gong_api_tester.py",
            "enhanced_gong_test.py",
            "gong_app_integration_analyzer.py",
            "gong_webhook_system.py",
            "gong_calls_api_fixed.py",
            "gong_api_alternative.py",
            "sophia_immediate_gong_extraction.py",
            "sophia_live_gong_integration.py",
            "sophia_fixed_gong_extraction.py",
            "sophia_updated_gong_extraction.py",
            "quick_setup_gong_integration.py",
            # Obsolete Setup/Configuration Files
            "simplified_api_test.py",
            "manage_integrations.py",
            "setup_new_repo.py",
            "multitenant_gong_architecture.py",
            "fix_call_participation_mapping.py",
            "configure_github_secrets.py",
            "configure_github_org_secrets.py",
            "sophia_secrets.py",
            "import_secrets_to_github.py",
            # Obsolete Test Files
            "test_mcp_client.py",
            "sophia_test_aggregator.py",
            "sophia_intelligence_test.py",
            "sophia_live_test_suite.py",
            "test_scripts.py",
            "test_setup.py",
            # Obsolete Admin/API Files
            "enhanced_sophia_admin_api.py",
            "sophia_admin_api.py",
            "enhanced_sophia_integration.py",
            # Obsolete Data Files
            "sophia_data_importer.py",
            "production_data_populator.py",
            "team_client_data_analysis.py",
            "schema_aligned_storage.py",
            "sophia_enhanced_schema.py",
            # Obsolete Fix Scripts
            "automated_health_check_fixed.py",
            "fix_database_storage.py",
            "fix_ssl_certificates.py",
            "fix_dependencies.py",
            "fix_sophia_insights.py",
            "run_with_ssl_fix.py",
            "unified_command_interface_fixed.py",
            "unified_command_interface.py",
        ]

        for file_name in obsolete_files:
            file_path = self.repo_root / file_name
            if file_path.exists():
                file_size = file_path.stat().st_size
                if self.dry_run:
                    logger.info(
                        f"[DRY RUN] Would delete: {file_name} ({file_size} bytes)"
                    )
                else:
                    file_path.unlink()
                    logger.info(f"Deleted: {file_name} ({file_size} bytes)")

                self.cleanup_report["files_deleted"] += 1
                self.cleanup_report["total_size_reduced"] += file_size
                self.cleanup_report["actions"].append(
                    {
                        "action": "delete_file",
                        "path": file_name,
                        "size": file_size,
                        "status": "dry_run" if self.dry_run else "completed",
                    }
                )

    def _move_files(self, file_mapping: Dict[str, str], category: str):
        """Helper method to move files"""
        for source, destination in file_mapping.items():
            source_path = self.repo_root / source
            dest_path = self.repo_root / destination / Path(source).name

            if source_path.exists():
                if self.dry_run:
                    logger.info(
                        f"[DRY RUN] Would move {category}: {source} -> {destination}"
                    )
                else:
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(source_path), str(dest_path))
                    logger.info(f"Moved {category}: {source} -> {destination}")

                self.cleanup_report["files_moved"] += 1
                self.cleanup_report["actions"].append(
                    {
                        "action": "move_file",
                        "category": category,
                        "source": source,
                        "destination": destination,
                        "status": "dry_run" if self.dry_run else "completed",
                    }
                )

    def _get_files_to_move_or_delete(self) -> List[Path]:
        """Get list of all files that will be moved or deleted"""
        files = []

        # Add all files from the root that match our patterns
        for item in self.repo_root.iterdir():
            if item.is_file() and not item.name.startswith("."):
                if any(
                    pattern in item.name
                    for pattern in [
                        "migration",
                        "validation",
                        "retool",
                        "gong",
                        "sophia",
                        "test_",
                        "enhanced_",
                        "fix_",
                        "configure_",
                    ]
                ):
                    files.append(item)

        return files

    def generate_report(self):
        """Generate cleanup report"""
        report_path = self.repo_root / "cleanup_report.json"

        self.cleanup_report["completion_time"] = time.time()
        self.cleanup_report["duration"] = (
            self.cleanup_report["completion_time"] - self.cleanup_report["timestamp"]
        )

        if not self.dry_run:
            with open(report_path, "w") as f:
                json.dump(self.cleanup_report, f, indent=2)
            logger.info(f"Cleanup report saved to {report_path}")

        # Print summary
        print(f"\n{'=' * 60}")
        print(f"REPOSITORY CLEANUP {'SIMULATION' if self.dry_run else 'SUMMARY'}")
        print(f"{'=' * 60}")
        print(f"Directories created: {self.cleanup_report['directories_created']}")
        print(f"Files moved: {self.cleanup_report['files_moved']}")
        print(f"Files deleted: {self.cleanup_report['files_deleted']}")
        print(
            f"Size reduced: {self.cleanup_report['total_size_reduced'] / 1024 / 1024:.2f} MB"
        )
        print(f"Total actions: {len(self.cleanup_report['actions'])}")

        if self.dry_run:
            print("\n⚠️  This was a DRY RUN. No files were actually moved or deleted.")
            print("Run with --execute to perform the actual cleanup.")

    def run_cleanup(self):
        """Execute the full cleanup process"""
        logger.info(
            f"Starting repository cleanup {'(DRY RUN)' if self.dry_run else ''}"
        )

        try:
            # Phase 1: Create backup
            if not self.dry_run:
                self.create_backup()

            # Phase 2: Create directory structure
            self.create_directory_structure()

            # Phase 3: Move files to archive
            self.move_migration_files()
            self.move_validation_files()
            self.move_historical_files()
            self.move_retool_files()

            # Phase 4: Organize remaining files
            self.organize_scripts()
            self.organize_configuration()

            # Phase 5: Delete obsolete files
            self.delete_obsolete_files()

            # Phase 6: Generate report
            self.generate_report()

            logger.info("Repository cleanup completed successfully!")

        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            raise


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Clean up Sophia AI repository")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute the cleanup (default is dry run)",
    )
    parser.add_argument(
        "--backup", action="store_true", help="Create backup before cleanup"
    )

    args = parser.parse_args()

    # Show warning for actual execution
    if args.execute:
        print("⚠️  WARNING: This will permanently reorganize your repository!")
        print("Make sure you have committed all important changes to git.")
        response = input("Continue? (yes/no): ")
        if response.lower() != "yes":
            print("Cleanup cancelled.")
            return

    cleanup = RepositoryCleanup(dry_run=not args.execute)
    cleanup.run_cleanup()


if __name__ == "__main__":
    main()
