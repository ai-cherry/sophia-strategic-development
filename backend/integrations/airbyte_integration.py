"""Airbyte Integration for Sophia AI
Provides a client to interact with the Airbyte API to manage and trigger data syncs.
"""
import logging
from typing import Any, Dict, Optional

import aiohttp

from infrastructure.esc.airbyte_secrets import airbyte_secret_manager

logger = logging.getLogger(__name__)


class AirbyteIntegration:
    """Handles communication with the Airbyte API.
    """

    def __init__(self, api_base_url: str = "https://api.airbyte.com/v1/"):
        self.api_base_url = api_base_url
        self.session = None
        self.headers = {}

    async def initialize(self):
        """Initializes the aiohttp session and retrieves the API key.
        """
        if self.session:
            return

        logger.info("Initializing Airbyte integration...")
        try:
            api_key = await airbyte_secret_manager.get_airbyte_api_key()
            self.headers = {
                "Authorization": f"Bearer {api_key}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
            self.session = aiohttp.ClientSession(headers=self.headers)
            logger.info("Airbyte integration initialized successfully.")
        except Exception as e:
            logger.error(
                f"Failed to initialize Airbyte integration: {e}", exc_info=True
            )
            raise

    async def close(self):
        """Closes the aiohttp session."""
        if self.session:
            await self.session.close()

    async def trigger_sync(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """Triggers a new synchronization job for a given Airbyte connection.

        Args:
            connection_id: The ID of the Airbyte connection to sync.

        Returns:
            A dictionary containing the job information, or None on failure.
        """
        if not self.session:
            await self.initialize()

        url = f"{self.api_base_url}jobs"
        payload = {"jobType": "sync", "connectionId": connection_id}

        logger.info(f"Triggering Airbyte sync for connection_id: {connection_id}")
        try:
            async with self.session.post(url, json=payload) as response:
                response.raise_for_status()
                job_info = await response.json()
                logger.info(
                    f"Successfully triggered Airbyte job: {job_info.get('job', {}).get('id')}"
                )
                return job_info
        except aiohttp.ClientError as e:
            logger.error(
                f"Error triggering Airbyte sync for connection {connection_id}: {e}"
            )
            return None

    async def get_job_status(self, job_id: int) -> Optional[Dict[str, Any]]:
        """Checks the status of a specific Airbyte job.

        Args:
            job_id: The ID of the job to check.

        Returns:
            A dictionary containing the job status information, or None on failure.
        """
        if not self.session:
            await self.initialize()

        url = f"{self.api_base_url}jobs/{job_id}"
        logger.info(f"Checking status for Airbyte job_id: {job_id}")
        try:
            async with self.session.get(url) as response:
                response.raise_for_status()
                job_status = await response.json()
                return job_status
        except aiohttp.ClientError as e:
            logger.error(f"Error checking status for Airbyte job {job_id}: {e}")
            return None


# Global instance
airbyte_integration = AirbyteIntegration()
