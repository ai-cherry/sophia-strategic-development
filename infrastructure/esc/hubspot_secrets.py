"""Pulumi ESC - HubSpot Secret Management
Manages HubSpot API keys.
"""
import logging
import os

import pulumi_pulumiservice as pulumiservice

logger = logging.getLogger(__name__)

PULUMI_ORG = os.getenv("PULUMI_ORG", "your-pulumi-org")


class HubSpotSecretManager:
    """Manages HubSpot secrets using Pulumi ESC."""

    def __init__(
        self, org: str = PULUMI_ORG, project: str = "sophia-ai", stack: str = "dev"
    ):
        self.org = org
        self.environment_name = f"{project}-{stack}"

    async def get_api_key(self) -> str:
        try:
            opened_env = await pulumiservice.open_environment(
                name=self.environment_name, organization=self.org
            )
            return opened_env.get("sophia.hubspot.apiKey")
        except Exception as e:
            logger.error(f"Failed to retrieve HubSpot API key from Pulumi ESC: {e}")
            api_key = os.getenv("HUBSPOT_API_KEY")
            if api_key:
                logger.warning("Falling back to HUBSPOT_API_KEY environment variable.")
                return api_key
            raise ConnectionError("Could not retrieve HubSpot API key.")


hubspot_secret_manager = HubSpotSecretManager()
