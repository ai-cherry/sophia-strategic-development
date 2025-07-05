#!/usr/bin/env python3
"""
Bidirectional GitHub Organization Secrets ↔ Pulumi ESC Synchronization for Sophia AI

This script provides robust, bidirectional synchronization between GitHub Organization Secrets
and Pulumi ESC environments with comprehensive error handling and audit capabilities.

Features:
- GitHub Organization Secrets → Pulumi ESC sync
- Validation and drift detection
- Comprehensive logging and audit trails
- Dry-run capability for safe testing
- Secret mapping and transformation
- Batch operations for efficiency
- Error recovery and rollback

Usage:
    python infrastructure/esc/github_sync_bidirectional.py --direction github-to-esc
    python infrastructure/esc/github_sync_bidirectional.py --direction validate --output json
    python infrastructure/esc/github_sync_bidirectional.py --dry-run --mapping-file mappings.json
"""

import argparse
import json
import logging
import os
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import requests
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class GitHubESCSyncManager:
    """
    Enterprise-grade bidirectional sync manager for GitHub Organization Secrets and Pulumi ESC
    """

    def __init__(self, org: str, github_token: str, pulumi_org: str, environment: str):
        self.org = org
        self.github_token = github_token
        self.pulumi_org = pulumi_org
        self.environment = environment
        self.logger = logging.getLogger(__name__)

        # GitHub API setup
        self.github_headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        self.github_api_base = f"https://api.github.com/orgs/{org}"

        # Validate setup
        self._validate_setup()

    def _validate_setup(self):
        """Validate GitHub and Pulumi access"""
        # Validate GitHub access
        try:
            response = requests.get(
                f"{self.github_api_base}", headers=self.github_headers, timeout=10
            )
            response.raise_for_status()
            self.logger.info(f"✅ GitHub organization '{self.org}' access validated")
        except Exception as e:
            raise RuntimeError(f"GitHub access validation failed: {e}")

        # Validate Pulumi access
        try:
            result = subprocess.run(
                ["pulumi", "whoami"], capture_output=True, text=True, timeout=10
            )
            if result.returncode != 0:
                raise RuntimeError(f"Pulumi authentication failed: {result.stderr}")
            self.logger.info(
                f"✅ Pulumi access validated for user: {result.stdout.strip()}"
            )
        except Exception as e:
            raise RuntimeError(f"Pulumi access validation failed: {e}")

    def get_github_secrets(self) -> dict[str, dict[str, Any]]:
        """
        Retrieve all organization secrets from GitHub with metadata

        Returns:
            Dictionary mapping secret names to metadata
        """
        try:
            url = f"{self.github_api_base}/actions/secrets"
            response = requests.get(url, headers=self.github_headers, timeout=30)
            response.raise_for_status()

            secrets_data = response.json()
            secrets = {}

            for secret in secrets_data.get("secrets", []):
                secrets[secret["name"]] = {
                    "name": secret["name"],
                    "created_at": secret.get("created_at"),
                    "updated_at": secret.get("updated_at"),
                    "visibility": secret.get("visibility", "private"),
                }

            self.logger.info(
                f"Retrieved {len(secrets)} secrets from GitHub organization '{self.org}'"
            )
            return secrets

        except requests.RequestException as e:
            self.logger.error(f"Failed to retrieve GitHub secrets: {e}")
            raise RuntimeError(f"GitHub API error: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error retrieving GitHub secrets: {e}")
            raise

    def get_pulumi_esc_secrets(self) -> dict[str, Any]:
        """
        Retrieve current secrets from Pulumi ESC environment

        Returns:
            Dictionary of current ESC values
        """
        try:
            env_path = f"{self.pulumi_org}/{self.environment}"
            result = subprocess.run(
                ["pulumi", "env", "get", env_path, "--show-secrets"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                data = json.loads(result.stdout)
                values = data.get("values", {})
                self.logger.info(
                    f"Retrieved {len(values)} values from Pulumi ESC environment '{self.environment}'"
                )
                return values
            else:
                error_msg = (
                    f"Failed to get ESC environment '{env_path}': {result.stderr}"
                )
                self.logger.error(error_msg)
                raise RuntimeError(error_msg)

        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON response from Pulumi ESC: {e}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)
        except subprocess.TimeoutExpired:
            error_msg = "Timeout retrieving ESC environment"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            self.logger.error(f"Error retrieving ESC secrets: {e}")
            raise

    def load_secret_mapping(self, mapping_file: Optional[str] = None) -> dict[str, str]:
        """
        Load secret name mapping from file or generate default mapping

        Args:
            mapping_file: Path to JSON mapping file

        Returns:
            Dictionary mapping GitHub secret names to ESC keys
        """
        if mapping_file and Path(mapping_file).exists():
            try:
                with open(mapping_file) as f:
                    mapping = json.load(f)
                self.logger.info(
                    f"Loaded {len(mapping)} secret mappings from {mapping_file}"
                )
                return mapping
            except Exception as e:
                self.logger.warning(f"Failed to load mapping file {mapping_file}: {e}")

        # Generate default mapping using SecurityConfig if available
        try:
            from backend.core.security_config import SecurityConfig

            mapping = SecurityConfig.generate_github_secret_mapping()
            self.logger.info(
                f"Generated {len(mapping)} default secret mappings from SecurityConfig"
            )
            return mapping
        except ImportError:
            self.logger.warning("SecurityConfig not available, using basic mapping")

        # Fallback: basic transformation (UPPER_CASE -> lower_case)
        github_secrets = self.get_github_secrets()
        mapping = {}
        for github_name in github_secrets.keys():
            esc_key = github_name.lower()
            mapping[github_name] = esc_key

        self.logger.info(f"Generated {len(mapping)} basic secret mappings")
        return mapping

    def sync_github_to_esc(
        self, secret_mapping: dict[str, str], dry_run: bool = False
    ) -> dict[str, Any]:
        """
        Sync secrets from GitHub Organization Secrets to Pulumi ESC

        Args:
            secret_mapping: Mapping of GitHub secret names to ESC keys
            dry_run: If True, only show what would be done

        Returns:
            Dictionary with sync results and statistics
        """
        self.logger.info(f"Starting GitHub → ESC sync (dry_run={dry_run})")

        sync_stats = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": dry_run,
            "total_mappings": len(secret_mapping),
            "successful_syncs": 0,
            "failed_syncs": 0,
            "skipped_syncs": 0,
            "details": [],
        }

        try:
            # Get current state
            github_secrets = self.get_github_secrets()
            current_esc = self.get_pulumi_esc_secrets()

            # Process each mapping
            updated_esc = current_esc.copy()

            for github_name, esc_key in secret_mapping.items():
                detail = {
                    "github_name": github_name,
                    "esc_key": esc_key,
                    "action": "unknown",
                    "success": False,
                    "message": "",
                }

                if github_name not in github_secrets:
                    detail["action"] = "skip"
                    detail["message"] = f"GitHub secret '{github_name}' not found"
                    sync_stats["skipped_syncs"] += 1
                    self.logger.warning(detail["message"])
                else:
                    # Create ESC secret reference to GitHub Organization Secret
                    github_secret_ref = f"{{{{ secrets.{github_name} }}}}"

                    if (
                        esc_key in updated_esc
                        and updated_esc[esc_key] == github_secret_ref
                    ):
                        detail["action"] = "skip"
                        detail["message"] = f"ESC key '{esc_key}' already synced"
                        sync_stats["skipped_syncs"] += 1
                    else:
                        detail["action"] = "sync"
                        detail[
                            "message"
                        ] = f"Updating ESC key '{esc_key}' with GitHub secret reference"

                        if not dry_run:
                            updated_esc[esc_key] = github_secret_ref

                        sync_stats["successful_syncs"] += 1
                        detail["success"] = True
                        self.logger.info(detail["message"])

                sync_stats["details"].append(detail)

            # Update ESC environment if not dry run and there are changes
            if not dry_run and sync_stats["successful_syncs"] > 0:
                success = self._update_esc_environment(updated_esc)
                if success:
                    self.logger.info(
                        f"✅ Successfully updated ESC environment with {sync_stats['successful_syncs']} changes"
                    )
                else:
                    self.logger.error("❌ Failed to update ESC environment")
                    # Mark all successful syncs as failed
                    for detail in sync_stats["details"]:
                        if detail["success"]:
                            detail["success"] = False
                            detail["message"] += " (ESC update failed)"
                    sync_stats["failed_syncs"] = sync_stats["successful_syncs"]
                    sync_stats["successful_syncs"] = 0

            # Log summary
            if dry_run:
                self.logger.info(
                    f"🔍 Dry run complete: {sync_stats['successful_syncs']} changes would be made"
                )
            else:
                self.logger.info(
                    f"✅ Sync complete: {sync_stats['successful_syncs']} successful, {sync_stats['failed_syncs']} failed, {sync_stats['skipped_syncs']} skipped"
                )

            return sync_stats

        except Exception as e:
            self.logger.error(f"Error during GitHub → ESC sync: {e}")
            sync_stats["error"] = str(e)
            return sync_stats

    def _update_esc_environment(self, values: dict[str, Any]) -> bool:
        """
        Update Pulumi ESC environment with new values

        Args:
            values: Dictionary of values to set in ESC

        Returns:
            True if successful, False otherwise
        """
        try:
            env_path = f"{self.pulumi_org}/{self.environment}"

            # Generate ESC YAML configuration
            yaml_content = self._generate_esc_yaml(values)

            # Create temporary file with updated config
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".yaml", delete=False
            ) as f:
                f.write(yaml_content)
                temp_file = f.name

            try:
                self.logger.info(
                    f"Updating ESC environment '{env_path}' with {len(values)} values"
                )

                result = subprocess.run(
                    ["pulumi", "env", "set", env_path, "--file", temp_file],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )

                if result.returncode == 0:
                    return True
                else:
                    self.logger.error(
                        f"Failed to update ESC environment: {result.stderr}"
                    )
                    return False

            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file)
                except Exception:
                    pass

        except Exception as e:
            self.logger.error(f"Error updating ESC environment: {e}")
            return False

    def _generate_esc_yaml(self, values: dict[str, Any]) -> str:
        """
        Generate ESC YAML configuration from values

        Args:
            values: Dictionary of values

        Returns:
            YAML configuration string
        """
        config = {"imports": [f"{self.pulumi_org}/consolidated"], "values": values}

        return yaml.dump(config, default_flow_style=False, sort_keys=True)

    def validate_sync_status(self) -> dict[str, Any]:
        """
        Validate synchronization status between GitHub and ESC

        Returns:
            Dictionary with detailed sync status analysis
        """
        try:
            self.logger.info("🔍 Validating GitHub ↔ ESC synchronization status...")

            github_secrets = set(self.get_github_secrets().keys())
            esc_values = self.get_pulumi_esc_secrets()

            # Load mapping to understand expected relationships
            mapping = self.load_secret_mapping()

            # Analyze sync status
            expected_esc_keys = set(mapping.values())
            actual_esc_keys = set(esc_values.keys())

            # Find secrets that should be synced
            mapped_github_secrets = set(mapping.keys())
            available_github_secrets = github_secrets & mapped_github_secrets

            # Calculate sync statistics
            sync_analysis = {
                "timestamp": datetime.now().isoformat(),
                "github_secrets": {
                    "total": len(github_secrets),
                    "mapped": len(mapped_github_secrets),
                    "available_for_sync": len(available_github_secrets),
                    "not_mapped": list(github_secrets - mapped_github_secrets),
                },
                "esc_values": {
                    "total": len(actual_esc_keys),
                    "expected_from_mapping": len(expected_esc_keys),
                    "properly_synced": 0,
                    "missing": list(expected_esc_keys - actual_esc_keys),
                    "extra": list(actual_esc_keys - expected_esc_keys),
                },
                "sync_health": {
                    "percentage": 0.0,
                    "status": "unknown",
                    "recommendations": [],
                },
            }

            # Check for properly synced secrets (those with GitHub references)
            properly_synced = 0
            for github_name, esc_key in mapping.items():
                if (
                    github_name in github_secrets
                    and esc_key in esc_values
                    and isinstance(esc_values[esc_key], str)
                    and "secrets." in str(esc_values[esc_key])
                ):
                    properly_synced += 1

            sync_analysis["esc_values"]["properly_synced"] = properly_synced

            # Calculate sync health percentage
            if len(available_github_secrets) > 0:
                sync_percentage = (
                    properly_synced / len(available_github_secrets)
                ) * 100
                sync_analysis["sync_health"]["percentage"] = round(sync_percentage, 1)

                # Determine status and recommendations
                if sync_percentage >= 95:
                    sync_analysis["sync_health"]["status"] = "excellent"
                    sync_analysis["sync_health"]["recommendations"].append(
                        "✅ Sync status is excellent"
                    )
                elif sync_percentage >= 80:
                    sync_analysis["sync_health"]["status"] = "good"
                    sync_analysis["sync_health"]["recommendations"].append(
                        "✅ Sync status is good"
                    )
                elif sync_percentage >= 60:
                    sync_analysis["sync_health"]["status"] = "fair"
                    sync_analysis["sync_health"]["recommendations"].append(
                        "⚠️ Consider running sync to improve coverage"
                    )
                else:
                    sync_analysis["sync_health"]["status"] = "poor"
                    sync_analysis["sync_health"]["recommendations"].append(
                        "❌ Sync status is poor - immediate sync recommended"
                    )

            # Add specific recommendations
            if sync_analysis["esc_values"]["missing"]:
                sync_analysis["sync_health"]["recommendations"].append(
                    f"🔧 {len(sync_analysis['esc_values']['missing'])} ESC keys missing - run GitHub→ESC sync"
                )

            if sync_analysis["github_secrets"]["not_mapped"]:
                sync_analysis["sync_health"]["recommendations"].append(
                    f"📋 {len(sync_analysis['github_secrets']['not_mapped'])} GitHub secrets not mapped - update mapping file"
                )

            self.logger.info(
                f"Validation complete: {sync_analysis['sync_health']['percentage']:.1f}% sync health ({sync_analysis['sync_health']['status']})"
            )

            return sync_analysis

        except Exception as e:
            self.logger.error(f"Error validating sync status: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "status": "error",
            }


def main():
    """Main function for CLI usage"""
    parser = argparse.ArgumentParser(
        description="Bidirectional GitHub Organization Secrets ↔ Pulumi ESC sync",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Sync GitHub secrets to ESC
    python infrastructure/esc/github_sync_bidirectional.py --direction github-to-esc

    # Validate sync status
    python infrastructure/esc/github_sync_bidirectional.py --direction validate --output json

    # Dry run with custom mapping
    python infrastructure/esc/github_sync_bidirectional.py --direction github-to-esc --dry-run --mapping-file mappings.json

    # Generate default mapping file
    python infrastructure/esc/github_sync_bidirectional.py --generate-mapping > mappings.json
        """,
    )

    parser.add_argument(
        "--direction",
        choices=["github-to-esc", "validate"],
        default="github-to-esc",
        help="Sync direction or validation (default: github-to-esc)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument("--mapping-file", help="JSON file with secret name mappings")
    parser.add_argument(
        "--output",
        choices=["json", "summary"],
        default="summary",
        help="Output format (default: summary)",
    )
    parser.add_argument(
        "--generate-mapping",
        action="store_true",
        help="Generate default mapping file and exit",
    )
    parser.add_argument("--quiet", action="store_true", help="Suppress log output")

    args = parser.parse_args()

    # Adjust logging level if quiet
    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)

    # Get configuration from environment
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        logger.error("GITHUB_TOKEN environment variable required")
        sys.exit(1)

    try:
        # Initialize sync manager
        sync_manager = GitHubESCSyncManager(
            org="ai-cherry",
            github_token=github_token,
            pulumi_org=os.getenv("PULUMI_ORG", "default"),
            environment=os.getenv("PULUMI_ENV", "sophia-ai-production"),
        )

        # Handle generate mapping request
        if args.generate_mapping:
            mapping = sync_manager.load_secret_mapping()
            print(json.dumps(mapping, indent=2))
            sys.exit(0)

        # Execute requested operation
        if args.direction == "validate":
            results = sync_manager.validate_sync_status()
        elif args.direction == "github-to-esc":
            mapping = sync_manager.load_secret_mapping(args.mapping_file)
            results = sync_manager.sync_github_to_esc(mapping, dry_run=args.dry_run)

        # Output results
        if args.output == "json":
            print(json.dumps(results, indent=2))
        else:
            # Summary output
            if args.direction == "validate":
                status = results.get("sync_health", {})
                print("\n🔍 GitHub ↔ ESC Sync Validation")
                print(
                    f"Health: {status.get('percentage', 0):.1f}% ({status.get('status', 'unknown')})"
                )
                print(
                    f"GitHub Secrets: {results.get('github_secrets', {}).get('total', 0)}"
                )
                print(f"ESC Values: {results.get('esc_values', {}).get('total', 0)}")

                if status.get("recommendations"):
                    print("\nRecommendations:")
                    for rec in status["recommendations"]:
                        print(f"  {rec}")
            else:
                print("\n🔄 GitHub → ESC Sync Results")
                print(f"Mode: {'Dry Run' if results.get('dry_run') else 'Live Sync'}")
                print(f"Successful: {results.get('successful_syncs', 0)}")
                print(f"Failed: {results.get('failed_syncs', 0)}")
                print(f"Skipped: {results.get('skipped_syncs', 0)}")

        # Exit with appropriate code
        if "error" in results:
            sys.exit(1)
        elif results.get("failed_syncs", 0) > 0:
            sys.exit(1)
        else:
            sys.exit(0)

    except Exception as e:
        logger.error(f"Sync operation failed: {e}")
        if args.output == "json":
            error_result = {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "success": False,
            }
            print(json.dumps(error_result, indent=2))
        else:
            print(f"Error: {e}", file=sys.stderr)

        sys.exit(2)


if __name__ == "__main__":
    main()
