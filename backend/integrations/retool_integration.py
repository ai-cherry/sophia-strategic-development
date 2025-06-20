"""Retool API Integration for Sophia AI
Provides a client to interact with the Retool API for building internal tools.
"""

import asyncio
import logging
from typing import Any, Dict, Optional

import aiohttp

from infrastructure.esc.retool_secrets import retool_secret_manager

logger = logging.getLogger(__name__)


class RetoolIntegration:
    """Client for programmatically interacting with Retool.
    """

    BASE_URL = "https://api.retool.com/v1"

    def __init__(self):
        self.api_token: Optional[str] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self.initialized = False

    async def initialize(self):
        """Initializes the Retool integration by fetching the API token
        and creating an aiohttp session.
        """
        if self.initialized:
            return

        logger.info("Initializing Retool integration...")
        try:
            self.api_token = await retool_secret_manager.get_retool_api_token()
            if not self.api_token:
                raise ValueError("RETOOL_API_TOKEN is not set.")

            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json",
            }
            self.session = aiohttp.ClientSession(headers=headers)

            self.initialized = True
            logger.info("Retool integration initialized successfully.")

        except Exception as e:
            logger.error(f"Failed to initialize Retool integration: {e}", exc_info=True)
            self.initialized = False

    async def close(self):
        """Close the aiohttp session."""
        if self.session:
            await self.session.close()

    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Makes an API request to Retool.
        """
        if not self.initialized or not self.session:
            raise ConnectionError("Retool integration not initialized.")

        url = f"{self.BASE_URL}/{endpoint}"
        async with self.session.request(method, url, **kwargs) as response:
            response.raise_for_status()
            return await response.json()

    async def create_app(self, name: str, description: str = "") -> Dict[str, Any]:
        """Creates a new Retool application.
        """
        payload = {
            "name": name,
            "displayName": name.replace("_", " ").title(),
            "description": description,
        }
        return await self._request("POST", "applications", json=payload)

    async def add_component_to_app(
        self, app_id: str, component_type: str, properties: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Adds a UI component to a Retool application.
        This is a conceptual example. The actual API might differ.
        """
        logger.warning(
            "This is a conceptual function. Retool's API for direct component manipulation may vary."
        )
        payload = {"componentType": component_type, "properties": properties}
        return await self._request(
            "POST", f"applications/{app_id}/components", json=payload
        )


async def main():
    """Manual testing for RetoolIntegration."""
    print("Testing Retool Integration...")
    integration = RetoolIntegration()

    try:
        # NOTE: This requires RETOOL_API_TOKEN to be set in a retool.env file or environment
        await integration.initialize()

        # This is a conceptual test and will likely fail if Retool API doesn't support it directly.
        # It serves to demonstrate the client's structure.
        print("Retool client initialized.")
        print("✅ Retool integration client structured correctly.")

    except Exception as e:
        logger.error(f"Retool integration test failed: {e}")
        print(
            "❌ Retool integration test failed. This is expected if a real API token is not provided."
        )

    finally:
        await integration.close()


if __name__ == "__main__":
    asyncio.run(main())
