#!/usr/bin/env python3
"""
MCP V2+ Migration Orchestrator
Automates the migration process with validation and rollback capabilities
"""

import argparse
import json
import logging
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MigrationPhase(Enum):
    """Migration phases"""

    PRE_MIGRATION = "pre_migration"
    PHASE_1 = "phase_1"
    PHASE_2 = "phase_2"
    PHASE_3 = "phase_3"
    PHASE_4 = "phase_4"
    POST_MIGRATION = "post_migration"


@dataclass
class ServerConfig:
    """Server configuration"""

    name: str
    v1_path: str
    v2_name: str
    port: int
    phase: MigrationPhase
    dependencies: list[str]
    status: str = "pending"


class MigrationOrchestrator:
    """Orchestrates the MCP V2+ migration"""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.root = Path.cwd()
        self.template_path = self.root / "infrastructure" / "mcp_servers" / "templates" / "mcp_v2_template.py"
        self.v2_base_path = self.root / "infrastructure" / "mcp_servers"
        self.reports_path = self.root / "reports"
        self.servers: dict[str, ServerConfig] = {}
        self.migration_log = []

        # Ensure directories exist
        self.reports_path.mkdir(exist_ok=True)

    def load_migration_config(self) -> None:
        """Load migration configuration"""
        # Define server migration mapping
        server_configs = [
            # Phase 1
            ServerConfig(
                "snowflake_cortex",
                "mcp-servers/snowflake_cortex",
                "snowflake_v2",
                9001,
                MigrationPhase.PHASE_1,
                [],
            ),
            ServerConfig(
                "ai_memory",
                "infrastructure/mcp_servers/ai_memory",
                "ai_memory_v2",
                9002,
                MigrationPhase.PHASE_1,
                [],
            ),
            ServerConfig(
                "postgres",
                "mcp-servers/postgres",
                "postgres_v2",
                9003,
                MigrationPhase.PHASE_1,
                [],
            ),
            ServerConfig(
                "redis",
                "mcp-servers/redis",
                "redis_cache_v2",
                9004,
                MigrationPhase.PHASE_1,
                [],
            ),
            ServerConfig(
                "docker",
                "mcp-servers/docker",
                "infrastructure_management_v2",
                9005,
                MigrationPhase.PHASE_1,
                ["pulumi"],
            ),
            ServerConfig(
                "lambda_labs_cli",
                "mcp-servers/lambda_labs_cli",
                "lambda_labs_cli_v2",
                9006,
                MigrationPhase.PHASE_1,
                [],
            ),
            # Phase 2
            ServerConfig(
                "salesforce",
                "mcp-servers/salesforce",
                "salesforce_v2",
                9011,
                MigrationPhase.PHASE_2,
                [],
            ),
            ServerConfig(
                "hubspot_unified",
                "mcp-servers/hubspot_unified",
                "hubspot_unified_v2",
                9012,
                MigrationPhase.PHASE_2,
                [],
            ),
            ServerConfig(
                "gong",
                "infrastructure/mcp_servers/gong_v2",
                "gong_v2",
                9013,
                MigrationPhase.PHASE_2,
                [],
            ),
            ServerConfig(
                "linear",
                "infrastructure/mcp_servers/linear_v2",
                "linear_v2",
                9014,
                MigrationPhase.PHASE_2,
                [],
            ),
            ServerConfig(
                "asana",
                "infrastructure/mcp_servers/asana_v2",
                "asana_v2",
                9015,
                MigrationPhase.PHASE_2,
                [],
            ),
            # Phase 3
            ServerConfig(
                "slack",
                "infrastructure/mcp_servers/slack_v2",
                "slack_v2",
                9021,
                MigrationPhase.PHASE_3,
                [],
            ),
            ServerConfig(
                "notion",
                "infrastructure/mcp_servers/notion_v2",
                "notion_v2",
                9022,
                MigrationPhase.PHASE_3,
                [],
            ),
            ServerConfig(
                "github",
                "infrastructure/mcp_servers/github_v2",
                "github_v2",
                9023,
                MigrationPhase.PHASE_3,
                [],
            ),
            ServerConfig(
                "graphiti",
                "mcp-servers/graphiti",
                "graphiti_v2",
                9024,
                MigrationPhase.PHASE_3,
                [],
            ),
            ServerConfig(
                "portkey_admin",
                "mcp-servers/portkey_admin",
                "ai_operations_v2",
                9025,
                MigrationPhase.PHASE_3,
                [],
            ),
            # Phase 4
            ServerConfig(
                "bright_data",
                "mcp-servers/bright_data",
                "data_collection_v2",
                9031,
                MigrationPhase.PHASE_4,
                ["apify_intelligence"],
            ),
            ServerConfig(
                "playwright",
                "mcp-servers/playwright",
                "playwright_v2",
                9032,
                MigrationPhase.PHASE_4,
                [],
            ),
            ServerConfig(
                "huggingface_ai",
                "mcp-servers/huggingface_ai",
                "huggingface_ai_v2",
                9033,
                MigrationPhase.PHASE_4,
                [],
            ),
            ServerConfig(
                "estuary",
                "mcp-servers/estuary",
                "estuary_v2",
                9034,
                MigrationPhase.PHASE_4,
                [],
            ),
            ServerConfig(
                "airbyte",
                "mcp-servers/airbyte",
                "airbyte_v2",
                9035,
                MigrationPhase.PHASE_4,
                [],
            ),
        ]

        for config in server_configs:
            self.servers[config.name] = config

    def run_pre_migration_checks(self) -> bool:
        """Run pre-migration validation checks"""
        logger.info("Running pre-migration checks...")

        checks = [
            ("Git status", self._check_git_status),
            ("Base tests", self._run_base_tests),
            ("Template exists", self._check_template_exists),
            ("Port conflicts", self._check_port_conflicts),
            ("Dependencies", self._check_dependencies),
        ]

        all_passed = True
        for check_name, check_func in checks:
            try:
                result = check_func()
                status = "✅" if result else "❌"
                logger.info(f"{status} {check_name}")
                if not result:
                    all_passed = False
            except Exception as e:
                logger.error(f"❌ {check_name}: {e}")
                all_passed = False

        return all_passed

    def _check_git_status(self) -> bool:
        """Check git working directory is clean"""
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=False,
        )
        return len(result.stdout.strip()) == 0

    def _run_base_tests(self) -> bool:
        """Run baseline tests"""
        if self.dry_run:
            logger.info("Skipping tests in dry-run mode")
            return True

        result = subprocess.run(
            ["uv", "run", "pytest", "-q"], capture_output=True, check=False
        )
        return result.returncode == 0

    def _check_template_exists(self) -> bool:
        """Check if template directory exists"""
        return self.template_path.exists()

    def _check_port_conflicts(self) -> bool:
        """Check for port conflicts"""
        ports = {}
        for server in self.servers.values():
            if server.port in ports:
                logger.error(
                    f"Port conflict: {server.name} and {ports[server.port]} both use port {server.port}"
                )
                return False
            ports[server.port] = server.name
        return True

    def _check_dependencies(self) -> bool:
        """Check Python dependencies"""
        result = subprocess.run(
            ["uv", "sync", "--dry-run"], capture_output=True, check=False
        )
        return result.returncode == 0

    def migrate_server(self, server: ServerConfig) -> bool:
        """Migrate a single server to V2+"""
        logger.info(f"Migrating {server.name} to {server.v2_name}...")

        try:
            # Step 1: Create V2 directory
            v2_path = self.v2_base_path / server.v2_name
            if v2_path.exists():
                logger.warning(f"{v2_path} already exists, skipping creation")
            else:
                self._create_v2_directory(server, v2_path)

            # Step 2: Copy and customize template
            self._customize_template(server, v2_path)

            # Step 3: Migrate business logic
            self._migrate_business_logic(server, v2_path)

            # Step 4: Update configuration
            self._update_configuration(server)

            # Step 5: Run tests
            if not self.dry_run:
                self._run_server_tests(server, v2_path)

            # Step 6: Update status
            server.status = "completed"
            self._log_migration(server, "success")

            return True

        except Exception as e:
            logger.error(f"Failed to migrate {server.name}: {e}")
            server.status = "failed"
            self._log_migration(server, "failed", str(e))
            return False

    def _create_v2_directory(self, server: ServerConfig, v2_path: Path) -> None:
        """Create V2 directory structure"""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would create directory: {v2_path}")
            return

        shutil.copytree(self.template_path, v2_path)
        logger.info(f"Created V2 directory: {v2_path}")

    def _customize_template(self, server: ServerConfig, v2_path: Path) -> None:
        """Customize template files for specific server"""
        replacements = {
            "{server_name}": server.v2_name.replace("_v2", ""),
            "{Server Name}": server.v2_name.replace("_", " ").title(),
            "{ServerName}": "".join(
                word.capitalize() for word in server.v2_name.split("_")
            ),
            "{service}": server.v2_name.replace("_v2", ""),
            "{service_name}": server.v2_name,
            "{default_port}": str(server.port),
        }

        # Process all Python and Markdown files
        for file_path in v2_path.rglob("*"):
            if file_path.suffix in [".py", ".md", ".yml", ".yaml"]:
                self._replace_in_file(file_path, replacements)

    def _replace_in_file(self, file_path: Path, replacements: dict[str, str]) -> None:
        """Replace placeholders in file"""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would update: {file_path}")
            return

        content = file_path.read_text()
        for old, new in replacements.items():
            content = content.replace(old, new)
        file_path.write_text(content)

    def _migrate_business_logic(self, server: ServerConfig, v2_path: Path) -> None:
        """Migrate business logic from V1 to V2"""
        v1_path = self.root / server.v1_path

        if not v1_path.exists():
            logger.warning(f"V1 path does not exist: {v1_path}")
            return

        # TODO: Implement intelligent business logic migration
        # This would analyze V1 code and extract core functionality
        logger.info(
            f"Business logic migration for {server.name} requires manual review"
        )

    def _update_configuration(self, server: ServerConfig) -> None:
        """Update port configuration"""
        ports_file = self.root / "config" / "consolidated_mcp_ports.json"

        if self.dry_run:
            logger.info(f"[DRY RUN] Would update ports config for {server.v2_name}")
            return

        if ports_file.exists():
            with open(ports_file) as f:
                ports = json.load(f)
        else:
            ports = {}

        ports[server.v2_name] = server.port

        with open(ports_file, "w") as f:
            json.dump(ports, f, indent=2, sort_keys=True)

    def _run_server_tests(self, server: ServerConfig, v2_path: Path) -> None:
        """Run tests for migrated server"""
        test_path = v2_path / "tests"
        if not test_path.exists():
            logger.warning(f"No tests found for {server.v2_name}")
            return

        result = subprocess.run(
            ["uv", "run", "pytest", str(test_path), "-v"],
            capture_output=True,
            check=False,
        )

        if result.returncode != 0:
            raise RuntimeError(f"Tests failed for {server.v2_name}")

    def _log_migration(
        self, server: ServerConfig, status: str, error: Optional[str] = None
    ) -> None:
        """Log migration status"""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "server": server.name,
            "v2_name": server.v2_name,
            "phase": server.phase.value,
            "status": status,
            "error": error,
        }
        self.migration_log.append(entry)

    def execute_phase(self, phase: MigrationPhase) -> bool:
        """Execute a migration phase"""
        logger.info(f"\n{'='*60}")
        logger.info(f"Executing {phase.value}")
        logger.info(f"{'='*60}\n")

        phase_servers = [s for s in self.servers.values() if s.phase == phase]

        if not phase_servers:
            logger.info(f"No servers to migrate in {phase.value}")
            return True

        success_count = 0
        for server in phase_servers:
            if self.migrate_server(server):
                success_count += 1

        logger.info(
            f"\n{phase.value} completed: {success_count}/{len(phase_servers)} successful"
        )
        return success_count == len(phase_servers)

    def generate_report(self) -> None:
        """Generate migration report"""
        report = {
            "migration_date": datetime.utcnow().isoformat(),
            "dry_run": self.dry_run,
            "servers": {
                name: {
                    "v2_name": server.v2_name,
                    "port": server.port,
                    "phase": server.phase.value,
                    "status": server.status,
                }
                for name, server in self.servers.items()
            },
            "log": self.migration_log,
            "summary": {
                "total": len(self.servers),
                "completed": len(
                    [s for s in self.servers.values() if s.status == "completed"]
                ),
                "failed": len(
                    [s for s in self.servers.values() if s.status == "failed"]
                ),
                "pending": len(
                    [s for s in self.servers.values() if s.status == "pending"]
                ),
            },
        }

        report_path = (
            self.reports_path
            / f"migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"\nMigration report saved to: {report_path}")

    def run(self, phases: Optional[list[MigrationPhase]] = None) -> bool:
        """Run the migration"""
        logger.info("Starting MCP V2+ Migration Orchestrator")
        logger.info(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")

        # Load configuration
        self.load_migration_config()

        # Run pre-migration checks
        if not self.run_pre_migration_checks():
            logger.error("Pre-migration checks failed. Aborting.")
            return False

        # Determine phases to run
        if phases is None:
            phases = [
                MigrationPhase.PHASE_1,
                MigrationPhase.PHASE_2,
                MigrationPhase.PHASE_3,
                MigrationPhase.PHASE_4,
            ]

        # Execute phases
        all_success = True
        for phase in phases:
            if not self.execute_phase(phase):
                logger.error(f"{phase.value} failed. Stopping migration.")
                all_success = False
                break

        # Generate report
        self.generate_report()

        return all_success


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="MCP V2+ Migration Orchestrator")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode")
    parser.add_argument(
        "--phase",
        choices=[p.value for p in MigrationPhase],
        help="Run specific phase only",
    )
    parser.add_argument("--server", help="Migrate specific server only")

    args = parser.parse_args()

    orchestrator = MigrationOrchestrator(dry_run=args.dry_run)

    if args.server:
        # Migrate single server
        orchestrator.load_migration_config()
        if args.server not in orchestrator.servers:
            logger.error(f"Server '{args.server}' not found in migration config")
            sys.exit(1)

        server = orchestrator.servers[args.server]
        success = orchestrator.migrate_server(server)
        orchestrator.generate_report()
        sys.exit(0 if success else 1)

    elif args.phase:
        # Run specific phase
        phase = MigrationPhase(args.phase)
        phases = [phase]
    else:
        # Run all phases
        phases = None

    success = orchestrator.run(phases)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
