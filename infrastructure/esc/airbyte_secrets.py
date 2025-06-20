"""Pulumi ESC - Airbyte Secret Management
Manages Airbyte API keys.
"""
import logging
import os

from backend.core.enhanced_pulumi_esc import EnhancedPulumiESC

logger = logging.getLogger(__name__)

PULUMI_ORG = os.getenv("PULUMI_ORG", "your-pulumi-org")
PULUMI_PROJECT = "sophia-ai"
PULUMI_STACK = "dev"

if PULUMI_ORG == "your-pulumi-org":
    raise ValueError("Please set the PULUMI_ORG environment variable.")


class AirbyteSecretManager(EnhancedPulumiESC):
    """Handles getting and setting Airbyte secrets via Pulumi ESC."""

    def __init__(self):
        super().__init__()

    async def get_airbyte_api_key(self) -> str:
        """Retrieves the Airbyte API key."""
        return await self.get_secret("AIRBYTE_API_KEY")


airbyte_secret_manager = AirbyteSecretManager()
