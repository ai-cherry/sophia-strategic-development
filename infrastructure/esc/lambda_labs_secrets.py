#!/usr/bin/env python3
"""Lambda Labs Secrets Management for Pulumi ESC."""

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


def setup_lambda_labs_secrets():
    """Set up Lambda Labs secrets in Pulumi ESC."""
    # Check if PULUMI_ORG is set
    pulumi_org = os.getenv("PULUMI_ORG")
    if not pulumi_org:
        raise ValueError("Please set the PULUMI_ORG environment variable.")

    logger.info("🔐 Setting up Lambda Labs secrets...")

    # Lambda Labs secrets configuration
    secrets = {
        "api_key": {
            "description": "Lambda Labs API Key",
            "env_var": "LAMBDA_LABS_API_KEY",
            "required": True,
        },
        "ssh_public_key": {
            "description": "SSH Public Key for Lambda Labs instances",
            "env_var": "LAMBDA_LABS_SSH_PUBLIC_KEY",
            "required": False,
        },
        "ssh_private_key": {
            "description": "SSH Private Key for Lambda Labs instances",
            "env_var": "LAMBDA_LABS_SSH_PRIVATE_KEY",
            "required": False,
        },
        "jupyter_password": {
            "description": "Jupyter Notebook Password",
            "env_var": "LAMBDA_LABS_JUPYTER_PASSWORD",
            "required": False,
        },
    }

    # Configuration values
    config = {
        "instance_type": "gpu_1x_a10",
        "region": "us-west-2",
        "api_url": "https://cloud.lambdalabs.com/api/v1",
    }

    try:
        # Set up secrets
        for secret_name, secret_config in secrets.items():
            env_var = secret_config["env_var"]
            value = os.getenv(env_var)

            if value:
                logger.info(f"✅ Setting {secret_name} from {env_var}")
                set_secret(f"lambda_labs:{secret_name}", value)
            elif secret_config["required"]:
                logger.error(f"❌ Required secret {secret_name} not found in {env_var}")
                return False
            else:
                logger.info(f"ℹ️  Optional secret {secret_name} not provided")

        # Set up configuration
        for config_name, config_value in config.items():
            logger.info(f"✅ Setting config {config_name}")
            set_secret(f"lambda_labs:{config_name}", config_value)

        logger.info("✅ Lambda Labs secrets configured successfully")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to set up Lambda Labs secrets: {e}")
        return False


if __name__ == "__main__":
    success = setup_lambda_labs_secrets()
    sys.exit(0 if success else 1)
