#!/usr/bin/env python3
"""
Replace estuary with Estuary Flow throughout Sophia AI codebase
Comprehensive migration script for complete estuary -> Estuary transition
"""

import json
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AirbyteToEstuaryMigrator:
    """Comprehensive migrator from estuary to Estuary Flow"""

    def __init__(self, project_root: str = None):
        self.project_root = (
            Path(project_root) if project_root else Path(__file__).parent.parent
        )
        self.migration_log = []
        self.files_modified = []
        self.backup_dir = (
            self.project_root
            / "migration_backup"
            / datetime.now().strftime("%Y%m%d_%H%M%S")
        )
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Mapping of estuary terms to Estuary equivalents
        self.term_mappings = {
            # Core concepts
            "estuary": "estuary",
            "estuary": "Estuary",
            "estuary": "ESTUARY",
            "estuary-": "estuary-",
            "estuary_": "estuary_",
            # Technical terms
            "estuary_api": "estuary_api",
            "estuary_client": "estuary_client",
            "estuary_config": "estuary_config",
            "estuary_connector": "estuary_connector",
            "estuary_integration": "estuary_integration",
            "estuary_manager": "estuary_manager",
            "estuary_service": "estuary_service",
            "estuary_setup": "estuary_setup",
            "estuary_sync": "estuary_sync",
            "estuary_webhook": "estuary_webhook",
            # File and class names
            "AirbyteAPI": "EstuaryAPI",
            "EstuaryClient": "EstuaryClient",
            "EstuaryConfig": "EstuaryConfig",
            "AirbyteConnector": "EstuaryConnector",
            "EstuaryIntegration": "EstuaryIntegration",
            "EstuaryManager": "EstuaryManager",
            "EstuaryService": "EstuaryService",
            "AirbyteSetup": "EstuarySetup",
            "AirbyteSync": "EstuarySync",
            "AirbyteWebhook": "EstuaryWebhook",
            # Environment variables
            "ESTUARY_ACCESS_TOKEN": "ESTUARY_ACCESS_TOKEN",
            "ESTUARY_CLIENT_ID": "ESTUARY_CLIENT_ID",
            "ESTUARY_CLIENT_SECRET": "ESTUARY_CLIENT_SECRET",
            "ESTUARY_REFRESH_TOKEN": "ESTUARY_REFRESH_TOKEN",
            "ESTUARY_API_URL": "ESTUARY_API_URL",
            "ESTUARY_WORKSPACE_ID": "ESTUARY_WORKSPACE_ID",
            # URLs and endpoints
            "api.estuary.com": "api.estuary.dev",
            "cloud.estuary.com": "dashboard.estuary.dev",
            "estuary.com": "estuary.dev",
            # Documentation references
            "estuary Cloud": "Estuary Flow",
            "estuary Open Source": "Estuary Flow Open Source",
            "estuary documentation": "Estuary Flow documentation",
            "estuary connector": "Estuary Flow connector",
            "estuary API": "Estuary Flow API",
            # Technical concepts
            "estuary sync": "estuary flow",
            "estuary connection": "estuary materialization",
            "estuary source": "estuary capture",
            "estuary destination": "estuary materialization",
            "estuary workspace": "estuary tenant",
            # CLI tools
            "estuary-cli": "flowctl",
            "estuary_cli": "flowctl",
        }

        # File extensions to process
        self.file_extensions = {
            ".py",
            ".js",
            ".ts",
            ".json",
            ".yaml",
            ".yml",
            ".md",
            ".txt",
            ".sh",
            ".env",
        }

        # Directories to skip
        self.skip_dirs = {
            ".git",
            "__pycache__",
            "node_modules",
            ".venv",
            "venv",
            "migration_backup",
            "docs_backup",
            ".pytest_cache",
        }

        # Files to skip
        self.skip_files = {
            "replace_estuary_with_estuary.py",  # This script itself
            ".gitignore",
            "LICENSE",
        }

    def log_change(
        self, file_path: str, old_text: str, new_text: str, line_number: int = None
    ):
        """Log a change made during migration"""
        change = {
            "file": file_path,
            "old": old_text,
            "new": new_text,
            "line": line_number,
            "timestamp": datetime.now().isoformat(),
        }
        self.migration_log.append(change)

        if file_path not in self.files_modified:
            self.files_modified.append(file_path)

    def backup_file(self, file_path: Path):
        """Create backup of file before modification"""
        try:
            relative_path = file_path.relative_to(self.project_root)
            backup_path = self.backup_dir / relative_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, backup_path)
            logger.debug(f"📁 Backed up: {relative_path}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to backup {file_path}: {e}")

    def should_process_file(self, file_path: Path) -> bool:
        """Determine if file should be processed"""
        # Skip if in skip directories
        for skip_dir in self.skip_dirs:
            if skip_dir in file_path.parts:
                return False

        # Skip if in skip files
        if file_path.name in self.skip_files:
            return False

        # Only process files with relevant extensions
        return file_path.suffix in self.file_extensions

    def replace_in_text(self, text: str, file_path: str) -> tuple[str, list[dict]]:
        """Replace estuary references in text content"""
        modified_text = text
        changes = []

        # Sort mappings by length (longest first) to avoid partial replacements
        sorted_mappings = sorted(
            self.term_mappings.items(), key=lambda x: len(x[0]), reverse=True
        )

        for old_term, new_term in sorted_mappings:
            if old_term in modified_text:
                # Count occurrences
                count = modified_text.count(old_term)
                if count > 0:
                    modified_text = modified_text.replace(old_term, new_term)
                    changes.append({"old": old_term, "new": new_term, "count": count})
                    logger.debug(
                        f"🔄 Replaced '{old_term}' -> '{new_term}' ({count} times) in {file_path}"
                    )

        return modified_text, changes

    def process_file(self, file_path: Path) -> bool:
        """Process a single file for estuary -> Estuary migration"""
        try:
            # Read file content
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                original_content = f.read()

            # Skip if no estuary references
            if "estuary" not in original_content.lower():
                return False

            # Backup file
            self.backup_file(file_path)

            # Replace content
            modified_content, changes = self.replace_in_text(
                original_content, str(file_path)
            )

            # Write modified content if changes were made
            if changes:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(modified_content)

                # Log changes
                for change in changes:
                    self.log_change(str(file_path), change["old"], change["new"])

                logger.info(
                    f"✅ Modified: {file_path.relative_to(self.project_root)} ({len(changes)} changes)"
                )
                return True

            return False

        except Exception as e:
            logger.error(f"❌ Failed to process {file_path}: {e}")
            return False

    def rename_files_and_directories(self):
        """Rename files and directories containing 'estuary'"""
        logger.info("📝 Renaming files and directories...")

        # Collect all paths that need renaming (files first, then directories)
        paths_to_rename = []

        for root, dirs, files in os.walk(self.project_root):
            root_path = Path(root)

            # Skip backup and other excluded directories
            if any(skip_dir in root_path.parts for skip_dir in self.skip_dirs):
                continue

            # Collect files to rename
            for file in files:
                if "estuary" in file.lower():
                    file_path = root_path / file
                    new_name = file
                    for old_term, new_term in self.term_mappings.items():
                        if old_term in new_name:
                            new_name = new_name.replace(old_term, new_term)

                    if new_name != file:
                        paths_to_rename.append(
                            (file_path, root_path / new_name, "file")
                        )

            # Collect directories to rename
            for dir_name in dirs:
                if "estuary" in dir_name.lower():
                    dir_path = root_path / dir_name
                    new_name = dir_name
                    for old_term, new_term in self.term_mappings.items():
                        if old_term in new_name:
                            new_name = new_name.replace(old_term, new_term)

                    if new_name != dir_name:
                        paths_to_rename.append(
                            (dir_path, root_path / new_name, "directory")
                        )

        # Rename files first, then directories (to avoid path issues)
        files_to_rename = [p for p in paths_to_rename if p[2] == "file"]
        dirs_to_rename = [p for p in paths_to_rename if p[2] == "directory"]

        for old_path, new_path, path_type in files_to_rename + dirs_to_rename:
            try:
                if old_path.exists() and not new_path.exists():
                    # Backup before renaming
                    self.backup_file(old_path)

                    # Rename
                    old_path.rename(new_path)
                    logger.info(
                        f"📝 Renamed {path_type}: {old_path.name} -> {new_path.name}"
                    )

                    # Log the change
                    self.log_change(str(old_path), old_path.name, new_path.name)

            except Exception as e:
                logger.error(f"❌ Failed to rename {old_path}: {e}")

    def update_import_statements(self):
        """Update import statements to use new Estuary modules"""
        logger.info("📦 Updating import statements...")

        import_mappings = {
            "from backend.integrations.estuary_": "from backend.integrations.estuary_",
            "import estuary_": "import estuary_",
            "from estuary_": "from estuary_",
            "import backend.integrations.estuary_": "import backend.integrations.estuary_",
        }

        for file_path in Path(self.project_root).rglob("*.py"):
            if not self.should_process_file(file_path):
                continue

            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                modified = False
                for old_import, new_import in import_mappings.items():
                    if old_import in content:
                        content = content.replace(old_import, new_import)
                        modified = True
                        logger.debug(
                            f"🔄 Updated import in {file_path.relative_to(self.project_root)}"
                        )

                if modified:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)

            except Exception as e:
                logger.error(f"❌ Failed to update imports in {file_path}: {e}")

    def create_estuary_config_files(self):
        """Create new Estuary configuration files"""
        logger.info("⚙️ Creating Estuary configuration files...")

        # Create Estuary configuration directory
        estuary_config_dir = self.project_root / "config" / "estuary"
        estuary_config_dir.mkdir(parents=True, exist_ok=True)

        # Create main Estuary configuration
        estuary_config = {
            "estuary": {
                "tenant": "Pay_Ready",
                "api_url": "https://api.estuary.dev",
                "dashboard_url": "https://dashboard.estuary.dev",
                "cli_tool": "flowctl",
                "authentication": {
                    "method": "token",
                    "access_token_env": "ESTUARY_ACCESS_TOKEN",
                    "refresh_token_env": "ESTUARY_REFRESH_TOKEN",
                },
                "connectors": {
                    "github": {
                        "image": "ghcr.io/estuary/source-github:dev",
                        "config_template": "github_capture_template.yaml",
                    },
                    "hubspot": {
                        "image": "ghcr.io/estuary/source-hubspot:dev",
                        "config_template": "hubspot_capture_template.yaml",
                    },
                    "slack": {
                        "image": "ghcr.io/estuary/source-slack:dev",
                        "config_template": "slack_capture_template.yaml",
                    },
                    "snowflake": {
                        "image": "ghcr.io/estuary/materialize-snowflake:dev",
                        "config_template": "snowflake_materialization_template.yaml",
                    },
                },
                "real_time_processing": {
                    "enabled": True,
                    "latency_target": "100ms",
                    "exactly_once_delivery": True,
                },
            }
        }

        config_file = estuary_config_dir / "estuary_config.json"
        with open(config_file, "w") as f:
            json.dump(estuary_config, f, indent=2)

        logger.info(f"✅ Created Estuary config: {config_file}")

        # Create environment template
        env_template = """# Estuary Flow Configuration
# Replace with actual values from Pulumi ESC or environment

# Estuary Authentication
ESTUARY_ACCESS_TOKEN=your_estuary_access_token_here
ESTUARY_REFRESH_TOKEN=your_estuary_refresh_token_here

# Business Tool API Keys (for captures)
GITHUB_ACCESS_TOKEN=your_github_token_here
HUBSPOT_CLIENT_ID=your_hubspot_client_id_here
HUBSPOT_CLIENT_SECRET=your_hubspot_client_secret_here
HUBSPOT_REFRESH_TOKEN=your_hubspot_refresh_token_here
SLACK_API_TOKEN=your_slack_api_token_here

# Custom Connector API Keys
USERGEMS_API_KEY=your_usergems_api_key_here
APOLLO_API_KEY=your_apollo_api_key_here

# Snowflake Configuration
SNOWFLAKE_ACCOUNT=UHDECNO-CVB64222
SNOWFLAKE_USER=SCOOBYJAVA15
SNOWFLAKE_PAT_TOKEN=your_snowflake_pat_token_here
SNOWFLAKE_ROLE=ACCOUNTADMIN
SNOWFLAKE_WAREHOUSE=CORTEX_COMPUTE_WH
SNOWFLAKE_DATABASE=SOPHIA_AI
SNOWFLAKE_SCHEMA=ESTUARY_STAGING
"""

        env_file = estuary_config_dir / "estuary.env.template"
        with open(env_file, "w") as f:
            f.write(env_template)

        logger.info(f"✅ Created environment template: {env_file}")

    def update_pulumi_config(self):
        """Update Pulumi configuration for Estuary"""
        logger.info("☁️ Updating Pulumi configuration...")

        pulumi_config_files = list(self.project_root.rglob("Pulumi.*.yaml"))

        for config_file in pulumi_config_files:
            try:
                with open(config_file) as f:
                    content = f.read()

                # Replace estuary references in Pulumi config
                modified_content, changes = self.replace_in_text(
                    content, str(config_file)
                )

                if changes:
                    self.backup_file(config_file)
                    with open(config_file, "w") as f:
                        f.write(modified_content)

                    logger.info(
                        f"✅ Updated Pulumi config: {config_file.relative_to(self.project_root)}"
                    )

            except Exception as e:
                logger.error(f"❌ Failed to update Pulumi config {config_file}: {e}")

        # Create new Pulumi ESC configuration for Estuary
        esc_config = {
            "values": {
                "estuary": {
                    "access_token": {"fn::secret": "${ESTUARY_ACCESS_TOKEN}"},
                    "refresh_token": {"fn::secret": "${ESTUARY_REFRESH_TOKEN}"},
                    "tenant": "Pay_Ready",
                },
                "connectors": {
                    "github": {
                        "access_token": {"fn::secret": "${GITHUB_ACCESS_TOKEN}"}
                    },
                    "hubspot": {
                        "client_id": {"fn::secret": "${HUBSPOT_CLIENT_ID}"},
                        "client_secret": {"fn::secret": "${HUBSPOT_CLIENT_SECRET}"},
                        "refresh_token": {"fn::secret": "${HUBSPOT_REFRESH_TOKEN}"},
                    },
                    "slack": {"api_token": {"fn::secret": "${SLACK_API_TOKEN}"}},
                },
            }
        }

        esc_file = self.project_root / "config" / "pulumi" / "estuary-secrets.yaml"
        esc_file.parent.mkdir(parents=True, exist_ok=True)

        with open(esc_file, "w") as f:
            import yaml

            yaml.dump(esc_config, f, default_flow_style=False)

        logger.info(f"✅ Created Pulumi ESC config: {esc_file}")

    def generate_migration_report(self) -> str:
        """Generate comprehensive migration report"""
        logger.info("📊 Generating migration report...")

        report = {
            "migration_summary": {
                "timestamp": datetime.now().isoformat(),
                "total_files_processed": len(self.files_modified),
                "total_changes": len(self.migration_log),
                "backup_location": str(self.backup_dir),
                "success": True,
            },
            "files_modified": self.files_modified,
            "changes_by_type": {},
            "detailed_changes": self.migration_log,
            "next_steps": [
                "Update API keys in Pulumi ESC or environment variables",
                "Test Estuary Flow connections with new configurations",
                "Deploy Estuary captures and materializations",
                "Verify real-time data processing",
                "Remove backup files after successful testing",
            ],
            "rollback_instructions": [
                f"Restore files from backup directory: {self.backup_dir}",
                "Run: git checkout . (if using git)",
                "Reinstall estuary dependencies if needed",
            ],
        }

        # Categorize changes
        for change in self.migration_log:
            old_term = change["old"]
            if old_term not in report["changes_by_type"]:
                report["changes_by_type"][old_term] = 0
            report["changes_by_type"][old_term] += 1

        # Save report
        report_file = (
            self.project_root
            / f"estuary_migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"📄 Migration report saved: {report_file}")
        return str(report_file)

    def run_migration(self) -> bool:
        """Execute complete estuary to Estuary migration"""
        logger.info("🚀 Starting estuary to Estuary migration...")

        try:
            # Step 1: Process all files for text replacements
            logger.info("📝 Step 1: Processing files for text replacements...")
            processed_count = 0

            for file_path in self.project_root.rglob("*"):
                if file_path.is_file() and self.should_process_file(file_path):
                    if self.process_file(file_path):
                        processed_count += 1

            logger.info(f"✅ Processed {processed_count} files")

            # Step 2: Rename files and directories
            self.rename_files_and_directories()

            # Step 3: Update import statements
            self.update_import_statements()

            # Step 4: Create Estuary configuration files
            self.create_estuary_config_files()

            # Step 5: Update Pulumi configuration
            self.update_pulumi_config()

            # Step 6: Generate migration report
            report_file = self.generate_migration_report()

            logger.info("✅ Migration completed successfully!")
            logger.info(f"📊 Report: {report_file}")
            logger.info(f"💾 Backup: {self.backup_dir}")

            return True

        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            return False


if __name__ == "__main__":
    # Run migration
    migrator = AirbyteToEstuaryMigrator()
    success = migrator.run_migration()

    if success:
        pass
    else:
        pass
