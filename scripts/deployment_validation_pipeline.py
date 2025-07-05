#!/usr/bin/env python3
"""
Deployment Validation Pipeline
Pre-deployment validation for Sophia AI platform
"""

import argparse
import subprocess
import sys
from pathlib import Path


def validate_dockerfile():
    """Validate Dockerfile syntax and security."""
    print("🔍 Validating Dockerfile...")

    dockerfile = Path("Dockerfile")
    if not dockerfile.exists():
        print("❌ Dockerfile not found")
        return False

    # Check Dockerfile syntax by attempting a build
    try:
        result = subprocess.run(
            [
                "docker",
                "build",
                "--target",
                "production",
                "-t",
                "sophia-ai-validation",
                ".",
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )
        print("✅ Dockerfile builds successfully")
        # Cleanup test image
        subprocess.run(["docker", "rmi", "sophia-ai-validation"], capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Dockerfile build failed: {e.stderr if e.stderr else e}")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Dockerfile build timed out")
        return False


def validate_compose_file():
    """Validate Docker Compose configuration."""
    print("🔍 Validating Docker Compose...")

    compose_file = Path("docker-compose.cloud.yml")
    if not compose_file.exists():
        print("❌ docker-compose.cloud.yml not found")
        return False

    try:
        subprocess.run(
            ["docker-compose", "-f", "docker-compose.cloud.yml", "config"],
            check=True,
            capture_output=True,
        )
        print("✅ Docker Compose configuration valid")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Docker Compose error: {e}")
        return False


def validate_secrets():
    """Validate secrets configuration."""
    print("🔍 Validating secrets configuration...")

    # Check Pulumi ESC integration
    try:
        from backend.core.auto_esc_config import get_config_value

        test_secret = get_config_value("openai_api_key")
        if test_secret and len(test_secret) > 10:
            print("✅ Secrets integration working")
            return True
        else:
            print("⚠️ Secrets integration degraded")
            return False
    except Exception as e:
        print(f"❌ Secrets validation failed: {e}")
        return False


def main():
    """Run all validations."""
    parser = argparse.ArgumentParser(
        description="Deployment Validation Pipeline for Sophia AI"
    )
    parser.add_argument(
        "--skip-docker",
        action="store_true",
        help="Skip Docker build validation (faster, but less thorough)",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    print("🚀 Running deployment validation pipeline...")

    if args.skip_docker:
        print("⚠️  Skipping Docker build validation (--skip-docker flag)")
        validations = [validate_compose_file, validate_secrets]
    else:
        validations = [validate_dockerfile, validate_compose_file, validate_secrets]

    results = []
    for validation in validations:
        results.append(validation())

    success_rate = sum(results) / len(results) * 100
    print(f"\n📊 Validation Results: {success_rate:.1f}% passed")

    if all(results):
        print("✅ All validations passed - Ready for deployment")
        return True
    else:
        print("❌ Some validations failed - Deployment blocked")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
