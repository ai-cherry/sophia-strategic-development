#!/usr/bin/env python3
"""
Secret Synchronization Script
Syncs secrets from GitHub environment to Pulumi ESC
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import structlog
import yaml

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


class SecretSynchronizer:
    """Synchronize secrets from GitHub to Pulumi ESC"""

    def __init__(
        self, map_file: Path, environment: str, pulumi_org: str, pulumi_project: str
    ):
        self.map_file = map_file
        self.environment = environment
        self.pulumi_org = pulumi_org
        self.pulumi_project = pulumi_project
        self.secret_map: dict[str, str] = {}
        self.sync_results: list[dict[str, Any]] = []

    def load_secret_map(self) -> dict[str, str]:
        """Load secret mapping from YAML file"""
        try:
            with open(self.map_file) as f:
                self.secret_map = yaml.safe_load(f)

            logger.info(
                "loaded_secret_map", count=len(self.secret_map), file=str(self.map_file)
            )
            return self.secret_map

        except Exception as e:
            logger.exception(
                "failed_to_load_secret_map", error=str(e), file=str(self.map_file)
            )
            raise

    def get_github_secret(self, secret_name: str) -> str | None:
        """Get secret value from environment (set by GitHub Actions)"""
        value = os.environ.get(secret_name)

        if value:
            # Mask value in logs
            masked = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "***"
            logger.debug("github_secret_found", name=secret_name, masked_value=masked)
        else:
            logger.warning("github_secret_missing", name=secret_name)

        return value

    def set_pulumi_secret(self, esc_path: str, value: str) -> bool:
        """Set secret in Pulumi ESC"""
        try:
            # Construct the full ESC environment path
            env_path = f"{self.pulumi_org}/{self.pulumi_project}/{self.environment}"

            # Use pulumi env set command
            cmd = [
                "pulumi",
                "env",
                "set",
                env_path,
                esc_path,
                value,
                "--secret",  # Mark as secret
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=False)

            if result.returncode == 0:
                logger.info("pulumi_secret_set", path=esc_path, environment=env_path)
                return True
            else:
                logger.error("pulumi_secret_failed", path=esc_path, error=result.stderr)
                return False

        except Exception as e:
            logger.exception("pulumi_secret_error", path=esc_path, error=str(e))
            return False

    def sync_secret(self, github_name: str, esc_path: str) -> dict[str, Any]:
        """Sync a single secret from GitHub to Pulumi"""
        result = {
            "github_name": github_name,
            "esc_path": esc_path,
            "success": False,
            "error": None,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Get value from GitHub
        value = self.get_github_secret(github_name)

        if not value:
            result["error"] = "Secret not found in GitHub environment"
            return result

        # Set in Pulumi ESC
        if self.set_pulumi_secret(esc_path, value):
            result["success"] = True
        else:
            result["error"] = "Failed to set in Pulumi ESC"

        return result

    def sync_all(self) -> list[dict[str, Any]]:
        """Sync all secrets based on mapping"""
        logger.info(
            "starting_sync",
            total_secrets=len(self.secret_map),
            environment=self.environment,
        )

        for github_name, esc_path in self.secret_map.items():
            result = self.sync_secret(github_name, esc_path)
            self.sync_results.append(result)

            # Log progress
            if result["success"]:
                logger.info("secret_synced", name=github_name, path=esc_path)
            else:
                logger.error(
                    "secret_sync_failed",
                    name=github_name,
                    path=esc_path,
                    error=result["error"],
                )

        # Summary
        successful = sum(1 for r in self.sync_results if r["success"])
        failed = len(self.sync_results) - successful

        logger.info(
            "sync_complete",
            total=len(self.sync_results),
            successful=successful,
            failed=failed,
        )

        return self.sync_results

    def generate_report(self) -> dict[str, Any]:
        """Generate sync report"""
        successful = [r for r in self.sync_results if r["success"]]
        failed = [r for r in self.sync_results if not r["success"]]

        report = {
            "sync_metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "environment": self.environment,
                "pulumi_org": self.pulumi_org,
                "pulumi_project": self.pulumi_project,
                "map_file": str(self.map_file),
            },
            "summary": {
                "total_secrets": len(self.sync_results),
                "successful": len(successful),
                "failed": len(failed),
                "success_rate": len(successful) / len(self.sync_results)
                if self.sync_results
                else 0,
            },
            "successful_syncs": successful,
            "failed_syncs": failed,
        }

        return report

    def save_report(self, output_file: Path):
        """Save sync report to file"""
        report = self.generate_report()

        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(
            "report_saved",
            file=str(output_file),
            successful=report["summary"]["successful"],
            failed=report["summary"]["failed"],
        )


def validate_environment():
    """Validate required environment variables"""
    required = ["PULUMI_ACCESS_TOKEN"]
    missing = [var for var in required if not os.environ.get(var)]

    if missing:
        logger.error("missing_required_env_vars", variables=missing)
        return False

    return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Sync secrets from GitHub to Pulumi ESC"
    )
    parser.add_argument(
        "--map-file",
        type=Path,
        default="config/pulumi/secret_map.yaml",
        help="Path to secret mapping YAML file",
    )
    parser.add_argument(
        "--environment",
        default="production",
        choices=["production", "staging", "development"],
        help="Target environment",
    )
    parser.add_argument("--pulumi-org", default="ai-cherry", help="Pulumi organization")
    parser.add_argument(
        "--pulumi-project", default="lambda-labs-production", help="Pulumi project name"
    )
    parser.add_argument(
        "--report-file",
        type=Path,
        default="reports/sync_report.json",
        help="Output report file",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be synced without making changes",
    )

    args = parser.parse_args()

    # Validate environment
    if not validate_environment():
        logger.error("Environment validation failed")
        sys.exit(1)

    # Validate map file exists
    if not args.map_file.exists():
        logger.error("map_file_not_found", file=str(args.map_file))
        sys.exit(1)

    # Create synchronizer
    synchronizer = SecretSynchronizer(
        map_file=args.map_file,
        environment=args.environment,
        pulumi_org=args.pulumi_org,
        pulumi_project=args.pulumi_project,
    )

    try:
        # Load mapping
        synchronizer.load_secret_map()

        if args.dry_run:
            logger.info("DRY RUN - No changes will be made")
            for github_name, esc_path in synchronizer.secret_map.items():
                value = synchronizer.get_github_secret(github_name)
                status = "✓" if value else "✗"
                logger.info(f"{status} {github_name} → {esc_path}")
        else:
            # Perform sync
            synchronizer.sync_all()

            # Save report
            args.report_file.parent.mkdir(parents=True, exist_ok=True)
            synchronizer.save_report(args.report_file)

            # Exit with error if any failed
            report = synchronizer.generate_report()
            if report["summary"]["failed"] > 0:
                logger.error(
                    "sync_had_failures", failed_count=report["summary"]["failed"]
                )
                sys.exit(1)

    except Exception as e:
        logger.error("sync_failed", error=str(e), exc_info=True)
        sys.exit(1)

    logger.info("Secret sync completed successfully")


if __name__ == "__main__":
    main()
