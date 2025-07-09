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

    dockerfile = Path("Dockerfile")
    if not dockerfile.exists():
        return False

    # Check Dockerfile syntax by attempting a build
    try:
        subprocess.run(
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
        # Cleanup test image
        subprocess.run(
            ["docker", "rmi", "sophia-ai-validation"], check=False, capture_output=True
        )
        return True
    except subprocess.CalledProcessError:
        return False
    except subprocess.TimeoutExpired:
        return False


def validate_compose_file():
    """Validate Docker Compose configuration."""

    compose_file = Path("docker-compose.cloud.yml")
    if not compose_file.exists():
        return False

    try:
        subprocess.run(
            ["docker-compose", "-f", "docker-compose.cloud.yml", "config"],
            check=True,
            capture_output=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def validate_secrets():
    """Validate secrets configuration."""

    # Check Pulumi ESC integration
    try:
        from backend.core.auto_esc_config import get_config_value

        test_secret = get_config_value("openai_api_key")
        return bool(test_secret and len(test_secret) > 10)
    except Exception:
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

    if args.skip_docker:
        validations = [validate_compose_file, validate_secrets]
    else:
        validations = [validate_dockerfile, validate_compose_file, validate_secrets]

    results = []
    for validation in validations:
        results.append(validation())

    sum(results) / len(results) * 100

    return bool(all(results))


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
