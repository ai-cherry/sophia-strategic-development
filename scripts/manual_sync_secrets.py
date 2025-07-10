#!/usr/bin/env python3
"""
Manual Secret Sync Script

This script allows manual syncing of secrets from GitHub to Pulumi ESC.
Use this when the CI/CD pipeline is not available or for local development.

Usage:
    1. Set environment variables:
       export GITHUB_TOKEN=<your-github-token>
       export PULUMI_ACCESS_TOKEN=<your-pulumi-token>

    2. Run the script:
       python scripts/manual_sync_secrets.py
"""

import os
import subprocess
import sys
from datetime import datetime


def check_prerequisites():
    """Check if required tools and tokens are available"""
    print("🔍 Checking prerequisites...")

    # Check GitHub CLI
    if (
        subprocess.run(["which", "gh"], capture_output=True, check=False).returncode
        != 0
    ):
        print("❌ GitHub CLI not found. Install with: brew install gh")
        return False

    # Check Pulumi CLI
    if (
        subprocess.run(["which", "pulumi"], capture_output=True, check=False).returncode
        != 0
    ):
        print("❌ Pulumi CLI not found. Install with: brew install pulumi")
        return False

    # Check tokens
    if not os.environ.get("GITHUB_TOKEN"):
        print("❌ GITHUB_TOKEN not set")
        return False

    if not os.environ.get("PULUMI_ACCESS_TOKEN"):
        print("❌ PULUMI_ACCESS_TOKEN not set")
        return False

    print("✅ All prerequisites met")
    return True


def get_github_secrets():
    """Fetch all secrets from GitHub organization"""
    print("\n📥 Fetching secrets from GitHub...")

    try:
        # List all secrets
        result = subprocess.run(
            ["gh", "secret", "list", "--repo", "ai-cherry/sophia-main"],
            capture_output=True,
            text=True,
            check=True,
        )

        secret_names = []
        for line in result.stdout.strip().split("\n"):
            if line:
                secret_name = line.split("\t")[0]
                secret_names.append(secret_name)

        print(f"Found {len(secret_names)} secrets in GitHub")
        return secret_names

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to fetch GitHub secrets: {e}")
        return []


def sync_to_pulumi():
    """Run the sync script"""
    print("\n🔄 Syncing to Pulumi ESC...")

    # Set up environment
    env = os.environ.copy()
    env["PULUMI_SKIP_UPDATE_CHECK"] = "true"

    # Run the sync script
    try:
        result = subprocess.run(
            [sys.executable, "scripts/ci/sync_secrets_to_esc.py"], env=env, check=True
        )
        print("✅ Sync completed successfully")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Sync failed: {e}")
        return False


def verify_pulumi_secrets():
    """Verify secrets in Pulumi ESC"""
    print("\n🔍 Verifying Pulumi ESC...")

    try:
        # Check a few critical secrets
        critical_secrets = [
            "values.sophia.data.snowflake.user",
            "values.sophia.ai.openai_api_key",
            "values.sophia.ai.anthropic_api_key",
        ]

        for secret_path in critical_secrets:
            result = subprocess.run(
                [
                    "pulumi",
                    "env",
                    "get",
                    "scoobyjava-org/default/sophia-ai-production",
                    secret_path,
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode == 0:
                value = result.stdout.strip()
                if value and not value.startswith("FROM_GITHUB"):
                    print(f"✅ {secret_path}: Available")
                else:
                    print(f"❌ {secret_path}: Not synced (placeholder)")
            else:
                print(f"❌ {secret_path}: Not found")

    except Exception as e:
        print(f"❌ Verification failed: {e}")


def main():
    """Main function"""
    print("=" * 60)
    print("🔐 Manual Secret Sync Tool")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    if not check_prerequisites():
        print("\n❌ Prerequisites check failed. Please fix the issues above.")
        sys.exit(1)

    # Get GitHub secrets
    secrets = get_github_secrets()
    if not secrets:
        print("\n❌ No secrets found in GitHub. Please check your access.")
        sys.exit(1)

    # Sync to Pulumi
    if not sync_to_pulumi():
        print("\n❌ Sync failed. Please check the errors above.")
        sys.exit(1)

    # Verify
    verify_pulumi_secrets()

    print("\n" + "=" * 60)
    print("✅ Manual sync complete!")
    print("\nNext steps:")
    print("1. Set environment variables:")
    print("   export PULUMI_ORG=scoobyjava-org")
    print("   export ENVIRONMENT=prod")
    print("2. Test the backend:")
    print("   python backend/app/unified_chat_backend.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
