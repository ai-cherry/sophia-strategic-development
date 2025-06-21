"""Pulumi ESC - Intercom Secret Management.

Manages Intercom API keys.
"""

import logging
import os

import pulumi_pulumiservice as pulumiservice

logger = logging.getLogger(__name__)

PULUMI_ORG = os.getenv("PULUMI_ORG", "your-pulumi-org")


class IntercomSecretManager:
    """Manages Intercom secrets using Pulumi ESC."""

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
            return opened_env.get("sophia.intercom.apiKey")
        except Exception as e:
            logger.error(f"Failed to retrieve Intercom API key from Pulumi ESC: {e}")
            api_key = os.getenv("INTERCOM_API_KEY")
            if api_key:
                logger.warning("Falling back to INTERCOM_API_KEY environment variable.")
                return api_key
            raise ConnectionError("Could not retrieve Intercom API key.")


intercom_secret_manager = IntercomSecretManager()
