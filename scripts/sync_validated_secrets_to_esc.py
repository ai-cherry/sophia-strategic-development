#!/usr/bin/env python3
"""Sophia AI - Sync Validated Secrets to Pulumi ESC.

This script syncs all validated GitHub organization secrets to Pulumi ESC
for automatic backend access via the permanent solution.

Usage:
    python scripts/sync_validated_secrets_to_esc.py
    python scripts/sync_validated_secrets_to_esc.py --force
    python scripts/sync_validated_secrets_to_esc.py --dry-run
"""import asyncio

import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PulumiESCSecretsSync:
    """Sync validated GitHub organization secrets to Pulumi ESC."""

    def __init__(self):
        self.github_org = "ai-cherry"
        self.pulumi_org = "scoobyjava-org"
        self.pulumi_env = "sophia-ai-production"
        self.esc_environment = f"{self.pulumi_org}/default/{self.pulumi_env}"

    def load_validation_results(self) -> Optional[Dict[str, Any]]:
        """Load the latest validation results."""# Look for the most recent validation results.

        validation_file = "docs/CURRENT_CAPABILITIES.json"

        if not os.path.exists(validation_file):
            logger.error(f"❌ Validation results not found: {validation_file}")
            logger.info("💡 Run 'python scripts/test_all_github_org_secrets.py' first")
            return None

        try:
            with open(validation_file, "r") as f:
                data = json.load(f)
            logger.info(f"✅ Loaded validation results from {validation_file}")
            return data
        except Exception as e:
            logger.error(f"❌ Failed to load validation results: {str(e)}")
            return None

    def check_esc_access(self) -> bool:
        """Check if Pulumi ESC is accessible."""try:.

            # Check if ESC CLI is available
            result = subprocess.run(["esc", "version"], capture_output=True, text=True)
            if result.returncode != 0:
                logger.error("❌ Pulumi ESC CLI not found. Please install it first.")
                return False

            # Check if we can access the environment
            result = subprocess.run(
                ["esc", "env", "get", self.esc_environment],
                capture_output=True, text=True
            )
            if result.returncode != 0:
                logger.error(f"❌ Cannot access Pulumi ESC environment: {self.esc_environment}")
                logger.error(f"Error: {result.stderr}")
                return False

            logger.info(f"✅ Pulumi ESC access confirmed for {self.esc_environment}")
            return True

        except Exception as e:
            logger.error(f"❌ ESC access check failed: {str(e)}")
            return False

    def get_current_esc_secrets(self) -> Dict[str, Any]:
        """Get current secrets in the ESC environment."""try:.

            result = subprocess.run(
                ["esc", "env", "get", self.esc_environment, "--show-secrets"],
                capture_output=True, text=True
            )

            if result.returncode == 0:
                data = json.loads(result.stdout)
                env_vars = data.get("properties", {}).get("environmentVariables", {})
                logger.info(f"📋 Found {len(env_vars)} existing secrets in ESC")
                return env_vars
            else:
                logger.warning(f"⚠️  Could not retrieve current ESC secrets: {result.stderr}")
                return {}

        except Exception as e:
            logger.error(f"❌ Failed to get current ESC secrets: {str(e)}")
            return {}

    def sync_secrets_to_esc(self, validation_data: Dict[str, Any], force: bool = False, dry_run: bool = False) -> Dict[str, Any]:
        """Sync validated secrets to Pulumi ESC."""logger.info(f"🔄 Syncing validated secrets to Pulumi ESC").

        if dry_run:
            logger.info("🧪 DRY RUN MODE - No actual changes will be made")

        sync_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "pulumi_org": self.pulumi_org,
            "pulumi_env": self.pulumi_env,
            "esc_environment": self.esc_environment,
            "dry_run": dry_run,
            "synced": 0,
            "skipped": 0,
            "errors": 0,
            "updated": 0,
            "secrets": {}
        }

        # Get current ESC secrets for comparison
        current_esc_secrets = self.get_current_esc_secrets()

        # Process each category of secrets
        for category, services in validation_data.get("categories", {}).items():
            logger.info(f"\n📂 Processing {category} secrets...")

            for service_info in services:
                secret_name = service_info["service"]
                secret_value = os.getenv(secret_name)

                if not secret_value:
                    sync_results["skipped"] += 1
                    sync_results["secrets"][secret_name] = "skipped: not in environment"
                    logger.warning(f"⚠️  {secret_name}: Not found in environment, skipping")
                    continue

                # Check if secret already exists in ESC
                current_value = current_esc_secrets.get(secret_name)

                if current_value and not force:
                    if current_value == secret_value:
                        sync_results["skipped"] += 1
                        sync_results["secrets"][secret_name] = "skipped: already up to date"
                        logger.info(f"✅ {secret_name}: Already up to date in ESC")
                        continue
                    else:
                        # Value differs, update it
                        action = "updated"
                        sync_results["updated"] += 1
                        logger.info(f"🔄 {secret_name}: Updating existing value in ESC")
                else:
                    # New secret
                    action = "synced"
                    sync_results["synced"] += 1
                    logger.info(f"➕ {secret_name}: Adding new secret to ESC")

                if not dry_run:
                    try:
                        # Use ESC CLI to set the secret
                        cmd = [
                            "esc", "env", "set",
                            self.esc_environment,
                            f"environmentVariables.{secret_name}",
                            secret_value
                        ]

                        result = subprocess.run(cmd, capture_output=True, text=True)
                        if result.returncode == 0:
                            sync_results["secrets"][secret_name] = action
                            logger.info(f"✅ {secret_name}: Successfully {action}")
                        else:
                            sync_results["errors"] += 1
                            sync_results["secrets"][secret_name] = f"error: {result.stderr}"
                            logger.error(f"❌ {secret_name}: Failed to sync - {result.stderr}")

                    except Exception as e:
                        sync_results["errors"] += 1
                        sync_results["secrets"][secret_name] = f"error: {str(e)}"
                        logger.error(f"❌ {secret_name}: Exception during sync - {str(e)}")
                else:
                    # Dry run mode
                    sync_results["secrets"][secret_name] = f"dry-run: would be {action}"
                    logger.info(f"🧪 {secret_name}: Would be {action}")

        return sync_results

    def generate_esc_environment_file(self, validation_data: Dict[str, Any]) -> str:
        """Generate a complete ESC environment file for reference."""logger.info("📝 Generating ESC environment file").

        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        esc_config = {
            "values": {
                "sophia": {
                    "description": f"Sophia AI production environment - Generated {timestamp}",
                    "environmentVariables": {}
                }
            }
        }

        # Add all validated secrets
        for category, services in validation_data.get("categories", {}).items():
            for service_info in services:
                secret_name = service_info["service"]
                secret_value = os.getenv(secret_name)

                if secret_value:
                    esc_config["values"]["sophia"]["environmentVariables"][secret_name] = {
                        "fn::secret": secret_value
                    }

        # Save the ESC configuration file
        config_file = "infrastructure/esc/sophia-ai-production-generated.yaml"
        os.makedirs("infrastructure/esc", exist_ok=True)

        import yaml
        with open(config_file, "w") as f:
            yaml.dump(esc_config, f, indent=2, default_flow_style=False)

        logger.info(f"💾 ESC environment file saved to {config_file}")
        return config_file

    def save_sync_results(self, sync_results: Dict[str, Any]):
        """Save sync results to files."""timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S").

        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)

        # Save detailed sync results
        sync_file = f"logs/esc_sync_{timestamp}.json"
        with open(sync_file, "w") as f:
            json.dump(sync_results, f, indent=2)
        logger.info(f"💾 Sync results saved to {sync_file}")

        # Generate human-readable summary
        self._generate_sync_report(sync_results)

    def _generate_sync_report(self, sync_results: Dict[str, Any]):
        """Generate a human-readable sync report."""timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC").

        report = f"""# Sophia AI - Pulumi ESC Sync Report
Generated: {timestamp}

## 📊 Sync Summary
- **ESC Environment**: {sync_results['esc_environment']}
- **Synced**: {sync_results['synced']} new secrets
- **Updated**: {sync_results['updated']} existing secrets
- **Skipped**: {sync_results['skipped']} secrets
- **Errors**: {sync_results['errors']} failed syncs
- **Dry Run**: {'Yes' if sync_results['dry_run'] else 'No'}

## 📋 Secret Details
"""for secret_name, status in sync_results["secrets"].items():.

            if status.startswith("error"):
                emoji = "❌"
            elif status.startswith("synced") or status.startswith("updated"):
                emoji = "✅"
            elif status.startswith("skipped"):
                emoji = "⚠️"
            elif status.startswith("dry-run"):
                emoji = "🧪"
            else:
                emoji = "❓"

            report += f"- {emoji} **{secret_name}**: {status}\n"

        if sync_results["errors"] > 0:
            report += f"\n## ⚠️  Errors Encountered\n"
            report += f"Please check the detailed logs and verify ESC permissions.\n"

        if not sync_results["dry_run"]:
            report += f"\n## 🎯 Next Steps\n"
            report += f"1. Verify secrets in Pulumi ESC dashboard\n"
            report += f"2. Test backend startup: `python backend/main.py`\n"
            report += f"3. Run validation: `python scripts/test_permanent_solution.py`\n"

        # Save report
        report_file = "docs/ESC_SYNC_REPORT.md"
        with open(report_file, "w") as f:
            f.write(report)
        logger.info(f"📄 Sync report saved to {report_file}")

def main():
"""Main function to sync validated secrets to Pulumi ESC."""
    import argparse

    parser = argparse.ArgumentParser(description="Sync Validated Secrets to Pulumi ESC")
    parser.add_argument("--force", action="store_true", help="Force update existing secrets")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be synced without making changes")
    args = parser.parse_args()

    syncer = PulumiESCSecretsSync()

    print("🔄 Sophia AI - Sync Validated Secrets to Pulumi ESC")
    print("=" * 60)

    # Load validation results
    validation_data = syncer.load_validation_results()
    if not validation_data:
        sys.exit(1)

    # Check ESC access
    if not syncer.check_esc_access():
        sys.exit(1)

    # Sync secrets
    sync_results = syncer.sync_secrets_to_esc(validation_data, args.force, args.dry_run)

    # Generate ESC environment file for reference
    esc_file = syncer.generate_esc_environment_file(validation_data)

    # Save results
    syncer.save_sync_results(sync_results)

    # Print summary
    print(f"\n🎯 Sync Results:")
    print(f"  Synced: {sync_results['synced']}")
    print(f"  Updated: {sync_results['updated']}")
    print(f"  Skipped: {sync_results['skipped']}")
    print(f"  Errors: {sync_results['errors']}")

    if sync_results["errors"] > 0:
        print(f"\n❌ Some secrets failed to sync. Check logs for details.")
        sys.exit(1)

    if not args.dry_run:
        print(f"\n✅ All secrets successfully synced to Pulumi ESC!")
        print(f"🔗 ESC Environment: {syncer.esc_environment}")
        print(f"📄 Reports saved to docs/ and logs/ directories")
    else:
        print(f"\n🧪 Dry run completed. Use --force to actually sync secrets.")

if __name__ == "__main__":
    main()
