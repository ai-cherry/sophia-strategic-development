#!/usr/bin/env python3
"""
Deployment Environment Validator
Validates all required environment variables for deployment
"""

import logging
import os
import sys

logger = logging.getLogger(__name__)

REQUIRED_ENV_VARS = {
    "DOCKER_USER_NAME": "Docker Hub username",
    "DOCKER_PERSONAL_ACCESS_TOKEN": "Docker Hub access token",
    "PULUMI_ACCESS_TOKEN": "Pulumi access token",
    "LAMBDA_LABS_API_KEY": "Lambda Labs API key",
}

OPTIONAL_ENV_VARS = {"ENVIRONMENT": "prod", "PULUMI_ORG": "scoobyjava-org"}


def validate_environment() -> tuple[bool, list[str]]:
    """Validate deployment environment variables"""
    errors = []

    # Check required variables
    for var, description in REQUIRED_ENV_VARS.items():
        if not os.getenv(var):
            errors.append(f"Missing required variable: {var} ({description})")

    # Set optional defaults
    for var, default in OPTIONAL_ENV_VARS.items():
        if not os.getenv(var):
            os.environ[var] = default
            logger.info(f"Set default {var}={default}")

    return len(errors) == 0, errors


def main():
    """Main validation function"""
    logging.basicConfig(level=logging.INFO)

    success, errors = validate_environment()

    if success:
        logger.info("✅ All environment variables validated successfully")
        sys.exit(0)
    else:
        logger.error("❌ Environment validation failed:")
        for error in errors:
            logger.error(f"  - {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
