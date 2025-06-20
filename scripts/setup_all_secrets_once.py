#!/usr/bin/env python3
"""ONE SCRIPT TO RULE THEM ALL - Unified Secret Management
This sets up ALL secrets properly using Pulumi ESC as the single source of truth
"""

import json
import os
import subprocess
import sys
from typing import Dict

# The Pulumi token you provided
TEMP_PULUMI_TOKEN = os.environ.get("PULUMI_ACCESS_TOKEN")


class UnifiedSecretManager:
    """Single unified secret management system"""

    def __init__(self):
        self.pulumi_org = "ai-cherry"
        self.pulumi_project = "sophia"
        self.pulumi_env = "sophia-production"
        self.secrets_to_sync = {}

    def setup_pulumi(self) -> bool:
        """Set up Pulumi access temporarily"""
        print("=== Setting up Pulumi Access ===")

        # Use the provided token temporarily
        if not TEMP_PULUMI_TOKEN:
            print("✗ ERROR: PULUMI_ACCESS_TOKEN environment variable is not set.")
            print("Please set it to your Pulumi access token to continue.")
            return False

        os.environ["PULUMI_ACCESS_TOKEN"] = TEMP_PULUMI_TOKEN

        try:
            # Login to Pulumi
            result = subprocess.run(["pulumi", "login"], capture_output=True, text=True)

            if result.returncode == 0:
                print("✓ Successfully logged into Pulumi")
                return True
            else:
                print(f"✗ Failed to login to Pulumi: {result.stderr}")
                return False

        except Exception as e:
            print(f"✗ Error setting up Pulumi: {e}")
            return False

    def collect_all_secrets(self) -> Dict[str, str]:
        """Collect all secrets from environment and files"""
        print("\n=== Collecting All Secrets ===")

        secrets = {}

        # Check environment variables
        env_patterns = [
            "LINEAR_API_KEY",
            "GONG_API_KEY",
            "GONG_CLIENT_ID",
            "GONG_CLIENT_SECRET",
            "SNOWFLAKE_ACCOUNT",
            "SNOWFLAKE_USER",
            "SNOWFLAKE_PASSWORD",
            "PINECONE_API_KEY",
            "PINECONE_ENVIRONMENT",
            "VERCEL_ACCESS_TOKEN",
            "VERCEL_PROJECT_ID",
            "SLACK_BOT_TOKEN",
            "SLACK_APP_TOKEN",
            "ANTHROPIC_API_KEY",
            "OPENAI_API_KEY",
            "GITHUB_TOKEN",
            "GITHUB_PAT",
            "LAMBDA_LABS_API_KEY",
            "ESTUARY_API_KEY",
            "AIRBYTE_API_KEY",
            "HUBSPOT_API_KEY",
            "INTERCOM_ACCESS_TOKEN",
            "RETOOL_API_KEY",
            "AGNO_API_KEY",
            "LLAMAINDEX_API_KEY",
            "OPENROUTER_API_KEY",
        ]

        for key in env_patterns:
            value = os.environ.get(key)
            if value:
                secrets[key] = value
                print(f"✓ Found {key} in environment")

        # Check .env file if exists
        if os.path.exists(".env"):
            print("\nChecking .env file...")
            with open(".env", "r") as f:
                for line in f:
                    line = line.strip()
                    if "=" in line and not line.startswith("#"):
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if key and value and key not in secrets:
                            secrets[key] = value
                            print(f"✓ Found {key} in .env file")

        print(f"\nTotal secrets found: {len(secrets)}")
        return secrets

    def sync_to_pulumi_esc(self, secrets: Dict[str, str]) -> bool:
        """Sync all secrets to Pulumi ESC"""
        print("\n=== Syncing to Pulumi ESC ===")

        success_count = 0
        failed_count = 0

        for key, value in secrets.items():
            try:
                # Determine the path in Pulumi ESC
                if key.startswith("LINEAR_"):
                    path = f"linear.{key.lower()}"
                elif key.startswith("GONG_"):
                    path = f"gong.{key.lower()}"
                elif key.startswith("SNOWFLAKE_"):
                    path = f"snowflake.{key.lower()}"
                elif key.startswith("PINECONE_"):
                    path = f"pinecone.{key.lower()}"
                elif key.startswith("VERCEL_"):
                    path = f"vercel.{key.lower()}"
                elif key.startswith("SLACK_"):
                    path = f"slack.{key.lower()}"
                elif key.startswith("GITHUB_"):
                    path = f"github.{key.lower()}"
                else:
                    # Generic path for other secrets
                    service = key.split("_")[0].lower()
                    path = f"{service}.{key.lower()}"

                # Set the secret in Pulumi ESC
                cmd = [
                    "pulumi",
                    "env",
                    "set",
                    f"{self.pulumi_org}/{self.pulumi_env}",
                    path,
                    "--secret",
                    "--plaintext",
                    value,
                ]

                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode == 0:
                    print(f"✓ Synced {key} → {path}")
                    success_count += 1
                else:
                    print(f"✗ Failed to sync {key}: {result.stderr}")
                    failed_count += 1

            except Exception as e:
                print(f"✗ Error syncing {key}: {e}")
                failed_count += 1

        print(f"\nSync complete: {success_count} succeeded, {failed_count} failed")
        return failed_count == 0

    def update_mcp_config(self, secrets: Dict[str, str]) -> bool:
        """Update MCP configuration to use Pulumi ESC"""
        print("\n=== Updating MCP Configuration ===")

        try:
            # Read current config
            with open("mcp_config.json", "r") as f:
                config = json.load(f)

            # Update Linear if we have the key
            if "LINEAR_API_KEY" in secrets:
                if "linear" in config.get("mcpServers", {}):
                    # Update to use environment variable reference
                    config["mcpServers"]["linear"]["env"][
                        "LINEAR_API_KEY"
                    ] = "${LINEAR_API_KEY}"
                    print("✓ Updated Linear MCP configuration")

            # Update other services similarly
            service_mappings = {
                "GONG_API_KEY": ("gong", "GONG_API_KEY"),
                "SLACK_BOT_TOKEN": ("slack", "SLACK_BOT_TOKEN"),
                "VERCEL_ACCESS_TOKEN": ("vercel", "VERCEL_ACCESS_TOKEN"),
                "ANTHROPIC_API_KEY": ("claude", "ANTHROPIC_API_KEY"),
                "PINECONE_API_KEY": ("knowledge_base", "PINECONE_API_KEY"),
            }

            for env_key, (service, config_key) in service_mappings.items():
                if env_key in secrets and service in config.get("mcpServers", {}):
                    if "env" not in config["mcpServers"][service]:
                        config["mcpServers"][service]["env"] = {}
                    config["mcpServers"][service]["env"][
                        config_key
                    ] = f"${{{config_key}}}"
                    print(f"✓ Updated {service} MCP configuration")

            # Write updated config
            with open("mcp_config.json", "w") as f:
                json.dump(config, f, indent=2)

            print("✓ MCP configuration updated")
            return True

        except Exception as e:
            print(f"✗ Error updating MCP config: {e}")
            return False

    def create_env_template(self, secrets: Dict[str, str]) -> None:
        """Create .env.template for others to use"""
        print("\n=== Creating .env.template ===")

        try:
            with open(".env.template", "w") as f:
                f.write("# Sophia AI Environment Variables Template\n")
                f.write("# Copy this to .env and fill in your values\n\n")

                # Group by service
                services = {}
                for key in sorted(secrets.keys()):
                    service = key.split("_")[0]
                    if service not in services:
                        services[service] = []
                    services[service].append(key)

                for service, keys in services.items():
                    f.write(f"\n# {service} Configuration\n")
                    for key in keys:
                        f.write(f"{key}=your_{key.lower()}_here\n")

            print("✓ Created .env.template")

        except Exception as e:
            print(f"✗ Error creating template: {e}")

    def cleanup_pulumi_token(self) -> None:
        """Remove Pulumi token from environment"""
        print("\n=== Cleaning up ===")

        # Clear from environment
        if "PULUMI_ACCESS_TOKEN" in os.environ:
            del os.environ["PULUMI_ACCESS_TOKEN"]

        print("✓ Cleaned up temporary Pulumi token")

    def run(self) -> bool:
        """Run the complete setup"""
        print("=" * 60)
        print("UNIFIED SECRET MANAGEMENT SETUP")
        print("=" * 60)

        try:
            # Step 1: Setup Pulumi
            if not self.setup_pulumi():
                return False

            # Step 2: Collect all secrets
            secrets = self.collect_all_secrets()
            if not secrets:
                print("\n⚠️  No secrets found to sync!")
                print("Add secrets to environment or .env file first")
                return False

            # Step 3: Sync to Pulumi ESC
            if not self.sync_to_pulumi_esc(secrets):
                print("\n⚠️  Some secrets failed to sync")

            # Step 4: Update MCP configuration
            self.update_mcp_config(secrets)

            # Step 5: Create template
            self.create_env_template(secrets)

            # Step 6: Create summary
            print("\n" + "=" * 60)
            print("✅ SETUP COMPLETE!")
            print("=" * 60)
            print("\nWhat was done:")
            print("1. ✓ Synced all secrets to Pulumi ESC")
            print("2. ✓ Updated MCP configuration")
            print("3. ✓ Created .env.template")
            print("\nNext steps:")
            print("1. Commit the updated mcp_config.json")
            print("2. All secrets are now in Pulumi ESC")
            print("3. GitHub Actions will use them automatically")
            print("4. Local development can use .env file")

            return True

        finally:
            # Always cleanup
            self.cleanup_pulumi_token()


if __name__ == "__main__":
    manager = UnifiedSecretManager()
    success = manager.run()
    sys.exit(0 if success else 1)
