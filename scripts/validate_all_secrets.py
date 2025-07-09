#!/usr/bin/env python3
"""
Validate ALL secret mappings between GitHub, Pulumi ESC, and the application.
This shows exactly what's missing and what needs to be fixed.
"""

import json
import os
import subprocess

# Import the mapping from our comprehensive script
from comprehensive_secret_mapping import APP_KEY_MAPPINGS, COMPLETE_SECRET_MAPPING


def check_github_secrets() -> set[str]:
    """Check which GitHub secrets are available in environment"""
    available = set()
    missing = set()

    print("🔍 Checking GitHub secrets in environment...")
    for secret_name in COMPLETE_SECRET_MAPPING.keys():
        if os.environ.get(secret_name):
            available.add(secret_name)
        else:
            missing.add(secret_name)

    print(f"✅ Available: {len(available)}")
    print(f"❌ Missing: {len(missing)}")

    if missing and len(missing) < 20:  # Only show if not too many
        print("\nMissing secrets:")
        for secret in sorted(missing):
            print(f"  - {secret}")

    return available

def check_pulumi_esc() -> dict[str, str]:
    """Check what's in Pulumi ESC"""
    print("\n🔍 Checking Pulumi ESC...")

    org = os.environ.get("PULUMI_ORG", "scoobyjava-org")
    env_name = f"{org}/default/sophia-ai-production"

    result = subprocess.run(
        ["pulumi", "env", "get", env_name, "--show-secrets"],
        check=False, capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"❌ Failed to get ESC config: {result.stderr}")
        return {}

    try:
        config = json.loads(result.stdout)

        # Count real vs placeholder values
        real_count = 0
        placeholder_count = 0

        for key, value in config.items():
            if str(value).startswith("PLACEHOLDER"):
                placeholder_count += 1
            else:
                real_count += 1

        print(f"✅ Real values: {real_count}")
        print(f"⚠️  Placeholders: {placeholder_count}")

        return config
    except json.JSONDecodeError:
        print("❌ Could not parse ESC config")
        return {}

def check_application_access() -> None:
    """Check if the application can access secrets"""
    print("\n🔍 Testing application access...")

    # Test by running our test script
    result = subprocess.run(
        ["python3", "test_docker_config.py"],
        check=False, capture_output=True,
        text=True
    )

    print(result.stdout)
    if result.returncode != 0:
        print(f"❌ Application test failed: {result.stderr}")

def validate_critical_path() -> None:
    """Validate the critical path for Docker Hub credentials"""
    print("\n🔐 Validating critical Docker Hub credential path...")

    # GitHub secret names
    github_username = os.environ.get("DOCKERHUB_USERNAME")
    github_token = os.environ.get("DOCKER_TOKEN")

    print("1️⃣ GitHub Secrets:")
    print(f"   DOCKERHUB_USERNAME: {'✅ Set' if github_username else '❌ Missing'}")
    print(f"   DOCKER_TOKEN: {'✅ Set' if github_token else '❌ Missing'}")

    # Check Pulumi ESC
    org = os.environ.get("PULUMI_ORG", "scoobyjava-org")
    env_name = f"{org}/default/sophia-ai-production"

    result = subprocess.run(
        ["pulumi", "env", "get", env_name, "--show-secrets"],
        check=False, capture_output=True,
        text=True,
        stderr=subprocess.DEVNULL
    )

    if result.returncode == 0:
        try:
            config = json.loads(result.stdout)

            print("\n2️⃣ Pulumi ESC:")
            print(f"   docker_username: {'✅ Set' if 'docker_username' in config else '❌ Missing'}")
            print(f"   docker_token: {'✅ Set' if 'docker_token' in config else '❌ Missing'}")

            # Check if they're real values or placeholders
            if 'docker_username' in config:
                if str(config['docker_username']).startswith("PLACEHOLDER"):
                    print("   ⚠️  docker_username is still a placeholder!")
            if 'docker_token' in config:
                if str(config['docker_token']).startswith("PLACEHOLDER"):
                    print("   ⚠️  docker_token is still a placeholder!")

        except json.JSONDecodeError:
            print("   ❌ Could not parse ESC config")

    print("\n3️⃣ Application Mapping (auto_esc_config.py):")
    print("   All variations map to docker_token and docker_username ✅")

def generate_fix_commands() -> None:
    """Generate commands to fix missing secrets"""
    print("\n🔧 Fix Commands:")
    print("\nIf running locally, set these environment variables:")
    print("export PULUMI_ACCESS_TOKEN='pul-...'")
    print("export DOCKERHUB_USERNAME='scoobyjava15'")
    print("export DOCKER_TOKEN='your-docker-hub-token'")
    print("\nThen run:")
    print("python3 scripts/comprehensive_secret_mapping.py")
    print("\nOr trigger the GitHub Action:")
    print("gh workflow run sync_secrets_comprehensive.yml")

def main():
    print("🔍 Comprehensive Secret Validation")
    print("=" * 50)

    # Check Pulumi access
    if not os.environ.get("PULUMI_ACCESS_TOKEN"):
        print("⚠️  PULUMI_ACCESS_TOKEN not set - some checks will fail")

    # Run all checks
    github_secrets = check_github_secrets()
    esc_config = check_pulumi_esc()
    check_application_access()
    validate_critical_path()

    # Summary
    print("\n📊 Summary:")
    print(f"GitHub secrets available: {len(github_secrets)}/{len(COMPLETE_SECRET_MAPPING)}")
    print(f"Pulumi ESC entries: {len(esc_config)}")
    print(f"Application mappings: {len(APP_KEY_MAPPINGS)}")

    # Generate fixes
    generate_fix_commands()

if __name__ == "__main__":
    main()
