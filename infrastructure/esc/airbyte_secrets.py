"""
Pulumi ESC - Airbyte Secret Management
Manages Airbyte API keys.
"""
import pulumi_pulumiservice as pulumiservice
import os
import logging

logger = logging.getLogger(__name__)

PULUMI_ORG = os.getenv("PULUMI_ORG", "your-pulumi-org")
PULUMI_PROJECT = "sophia-ai"
PULUMI_STACK = "dev"

if PULUMI_ORG == "your-pulumi-org":
    raise ValueError("Please set the PULUMI_ORG environment variable.")

class AirbyteSecretManager:
    """Manages Airbyte secrets using Pulumi ESC."""

    def __init__(self, org: str = PULUMI_ORG, project: str = PULUMI_PROJECT, stack: str = PULUMI_STACK):
        self.org = org
        self.environment_name = f"{project}-{stack}"

    async def get_airbyte_api_key(self) -> str:
        """
        Retrieves the Airbyte API key from the Pulumi ESC environment.
        """
        try:
            opened_env = await pulumiservice.open_environment(
                name=self.environment_name,
                organization=self.org
            )
            return opened_env.get("sophia.airbyte.apiKey")
        except Exception as e:
            logger.error(f"Failed to retrieve Airbyte API key from Pulumi ESC: {e}")
            api_key = os.getenv("AIRBYTE_API_KEY")
            if api_key:
                logger.warning("Falling back to AIRBYTE_API_KEY environment variable.")
                return api_key
            raise ConnectionError("Could not retrieve Airbyte API key.")

airbyte_secret_manager = AirbyteSecretManager() 