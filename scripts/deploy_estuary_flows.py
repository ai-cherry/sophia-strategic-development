#!/usr/bin/env python3
"""
🚨 ONE-TIME SCRIPT - DELETE AFTER USE
Deploy Estuary Flow Configurations
Manages Estuary Flow collections, captures, and materializations

Purpose: Deploy Estuary Flow configurations as part of migration
Created: July 9, 2025
Usage: python scripts/deploy_estuary_flows.py
"""

import asyncio
import json
import os
import subprocess
from pathlib import Path

from backend.core.auto_esc_config import get_config_value


class EstuaryFlowDeployer:
    """Deploys and manages Estuary Flow configurations"""

    def __init__(self):
        self.flow_cli = "flowctl"  # Estuary CLI
        self.config_dir = Path("config/estuary")

        # Get Estuary credentials from Pulumi ESC
        self.estuary_token = get_config_value("estuary_token")
        self.estuary_endpoint = get_config_value(
            "estuary_endpoint", "https://api.estuary.dev"
        )

    async def deploy_all(self):
        """Deploy all Estuary Flow configurations"""
        print("🚀 Estuary Flow Deployment")
        print("=" * 60)

        # Authenticate with Estuary
        await self._authenticate()

        # Find all flow configurations
        flow_configs = list(self.config_dir.glob("*.flow.yaml"))

        if not flow_configs:
            print("❌ No Flow configurations found in config/estuary/")
            return

        print(f"\n📁 Found {len(flow_configs)} Flow configurations")

        # Deploy each configuration
        for config_file in flow_configs:
            await self._deploy_config(config_file)

        # Verify deployments
        await self._verify_deployments()

    async def _authenticate(self):
        """Authenticate with Estuary Flow"""
        print("\n🔑 Authenticating with Estuary Flow...")

        # Set auth token
        if self.estuary_token:
            os.environ["ESTUARY_TOKEN"] = self.estuary_token
        else:
            raise Exception("ESTUARY_TOKEN not found in configuration")

        # Test authentication
        result = subprocess.run(
            [self.flow_cli, "auth", "test"], capture_output=True, text=True, check=False
        )

        if result.returncode == 0:
            print("✅ Authentication successful")
        else:
            print(f"❌ Authentication failed: {result.stderr}")
            raise Exception("Failed to authenticate with Estuary")

    async def _deploy_config(self, config_file: Path):
        """Deploy a single Flow configuration"""
        print(f"\n📄 Deploying {config_file.name}...")

        # Validate configuration
        print("  🔍 Validating configuration...")
        result = subprocess.run(
            [self.flow_cli, "validate", str(config_file)],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            print(f"  ❌ Validation failed: {result.stderr}")
            return

        print("  ✅ Configuration valid")

        # Apply configuration
        print("  📤 Applying configuration...")
        result = subprocess.run(
            [self.flow_cli, "apply", "--file", str(config_file)],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            print("  ✅ Configuration applied successfully")
            print(f"  📊 Output: {result.stdout}")
        else:
            print(f"  ❌ Apply failed: {result.stderr}")

    async def _verify_deployments(self):
        """Verify all deployments are healthy"""
        print("\n🔍 Verifying deployments...")

        # List all collections
        result = subprocess.run(
            [self.flow_cli, "collections", "list", "--prefix", "sophia/"],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            collections = json.loads(result.stdout)
            print(f"\n✅ Active Collections ({len(collections)}):")

            for collection in collections:
                print(f"  - {collection['name']}")

                # Check collection stats
                stats_result = subprocess.run(
                    [self.flow_cli, "collections", "stats", collection["name"]],
                    capture_output=True,
                    text=True,
                    check=False,
                )

                if stats_result.returncode == 0:
                    stats = json.loads(stats_result.stdout)
                    print(f"    Documents: {stats.get('documents', 0):,}")
                    print(f"    Bytes: {stats.get('bytes', 0):,}")

        # List materializations
        result = subprocess.run(
            [self.flow_cli, "materializations", "list", "--prefix", "sophia/"],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            materializations = json.loads(result.stdout)
            print(f"\n✅ Active Materializations ({len(materializations)}):")

            for mat in materializations:
                print(
                    f"  - {mat['name']} → {mat['endpoint']['connector']['config']['database']}.{mat['endpoint']['connector']['config']['schema']}"
                )

    def create_deprecation_plan(self):
        """Create plan to deprecate old ETL scripts"""
        print("\n📋 Deprecation Plan for Old ETL Scripts")
        print("=" * 60)

        scripts_to_deprecate = [
            {
                "file": "infrastructure/etl/gong/ingest_gong_data.py",
                "replacement": "config/estuary/gong-complete.flow.yaml",
                "action": "Remove after parallel validation",
            },
            {
                "file": "infrastructure/etl/gong_api_extractor_clean.py",
                "replacement": "Estuary source-gong connector",
                "action": "Archive and remove",
            },
        ]

        print("\n🗑️  Scripts to Deprecate:")
        for item in scripts_to_deprecate:
            print(f"\n  File: {item['file']}")
            print(f"  Replacement: {item['replacement']}")
            print(f"  Action: {item['action']}")

        # Create deprecation script
        deprecation_script = """#!/bin/bash
# Deprecate old ETL scripts after Estuary Flow validation
# Date: July 9, 2025

echo "🗑️  Deprecating old ETL scripts..."

# Create archive directory
mkdir -p archived_etl_scripts

# Move old scripts
mv infrastructure/etl/gong/ingest_gong_data.py archived_etl_scripts/
mv infrastructure/etl/gong_api_extractor_clean.py archived_etl_scripts/

# Update imports
echo "📝 Update any imports referencing old scripts"

echo "✅ Deprecation complete"
"""

        with open("scripts/deprecate_old_etl.sh", "w") as f:
            f.write(deprecation_script)

        os.chmod("scripts/deprecate_old_etl.sh", 0o755)
        print("\n✅ Created deprecation script: scripts/deprecate_old_etl.sh")


async def main():
    """Main deployment function"""
    deployer = EstuaryFlowDeployer()

    # Deploy all configurations
    await deployer.deploy_all()

    # Create deprecation plan
    deployer.create_deprecation_plan()

    print("\n" + "=" * 60)
    print("🎯 Next Steps:")
    print("1. Monitor Estuary Flow dashboard for data flow")
    print("2. Validate data quality in Snowflake")
    print("3. Run parallel validation for 24 hours")
    print("4. Execute deprecation script after validation")
    print("5. Update documentation")


if __name__ == "__main__":
    # Check if flowctl is installed
    if (
        subprocess.run(
            ["which", "flowctl"], capture_output=True, check=False
        ).returncode
        != 0
    ):
        print("❌ Error: flowctl CLI not found")
        print(
            "Install with: curl -L https://github.com/estuary/flow/releases/latest/download/flowctl -o /usr/local/bin/flowctl"
        )
        print("Then: chmod +x /usr/local/bin/flowctl")
        exit(1)

    asyncio.run(main())
