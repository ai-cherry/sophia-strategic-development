#!/usr/bin/env python3
"""OpenAI Secrets Management for Pulumi ESC."""

import logging
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from infrastructure.esc.get_secret import set_secret

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_openai_secrets():
    """Set up OpenAI secrets in Pulumi ESC."""
    # Check if PULUMI_ORG is set
    pulumi_org = os.getenv("PULUMI_ORG")
    if not pulumi_org:
        raise ValueError("Please set the PULUMI_ORG environment variable.")

    logger.info("🔐 Setting up OpenAI secrets...")

    # OpenAI secrets configuration
    secrets = {
        "api_key": {
            "description": "OpenAI API Key",
            "env_var": "OPENAI_API_KEY",
            "required": True,
        },
        "organization": {
            "description": "OpenAI Organization ID",
            "env_var": "OPENAI_ORGANIZATION",
            "required": False,
        },
    }

    # Configuration values
    config = {
        "api_url": "https://api.openai.com/v1",
        "model": "gpt-4",
        "max_tokens": 4096,
        "temperature": 0.7,
    }

    try:
        # Set up secrets
        for secret_name, secret_config in secrets.items():
            env_var = secret_config["env_var"]
            value = os.getenv(env_var)

            if value:
                logger.info(f"✅ Setting {secret_name} from {env_var}")
                set_secret(f"openai:{secret_name}", value)
            elif secret_config["required"]:
                logger.error(f"❌ Required secret {secret_name} not found in {env_var}")
                return False
            else:
                logger.info(f"ℹ️  Optional secret {secret_name} not provided")

        # Set up configuration
        for config_name, config_value in config.items():
            logger.info(f"✅ Setting config {config_name}")
            set_secret(f"openai:{config_name}", config_value)

        logger.info("✅ OpenAI secrets configured successfully")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to set up OpenAI secrets: {e}")
        return False


if __name__ == "__main__":
    success = setup_openai_secrets()
    sys.exit(0 if success else 1)
