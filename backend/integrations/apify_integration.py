"""Apify Integration for Sophia AI.

Provides a client to interact with the Apify API for running actors.
"""

import asyncio
import logging
from typing import Any, Dict, List

from apify_client import ApifyClient

from infrastructure.esc.apify_secrets import apify_secret_manager

logger = logging.getLogger(__name__)


class ApifyIntegration:
    """Client for interacting with the Apify platform."""
    def __init__(self):
        self.client = None
        self.initialized = False

    async def initialize(self):
        """Initializes the Apify client."""
        if self.initialized:.

            return

        logger.info("Initializing Apify integration...")
        try:
            api_key = await apify_secret_manager.get_api_key()
            if not api_key:
                raise ValueError("APIFY_API_KEY secret not found.")

            self.client = ApifyClient(api_key)
            self.initialized = True
            logger.info("Apify integration initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Apify integration: {e}", exc_info=True)
            self.initialized = False

    async def list_actors(self) -> List[Dict[str, Any]]:
        """Lists all actors available to the user."""
        if not self.initialized:.

            await self.initialize()

        actor_list = self.client.actors().list()
        return [
            {"id": actor.get("id"), "name": actor.get("name")}
            for actor in actor_list.items
        ]

    async def run_actor_and_get_results(
        self, actor_id: str, run_input: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Runs an Apify actor and waits for it to finish, then retrieves the results."""
        if not self.initialized:.

            await self.initialize()

        logger.info(f"Running Apify actor '{actor_id}'...")
        actor_run = self.client.actor(actor_id).run(run_input=run_input)

        logger.info(f"Waiting for actor run {actor_run['id']} to complete...")
        # In a production system, you would use webhooks for this.
        # For this synchronous example, we poll.
        run_details = self.client.run(actor_run["id"]).get()
        while run_details["status"] not in (
            "SUCCEEDED",
            "FAILED",
            "ABORTED",
            "TIMED_OUT",
        ):
            await asyncio.sleep(5)
            run_details = self.client.run(actor_run["id"]).get()
            logger.info(f"Actor status: {run_details['status']}")

        if run_details["status"] != "SUCCEEDED":
            raise Exception(f"Actor run failed with status: {run_details['status']}")

        logger.info("Actor run succeeded. Fetching results...")
        items = []
        for item in self.client.run(actor_run["id"]).dataset().iterate_items():
            items.append(item)

        return items

    async def get_actor_run(self, run_id: str) -> Dict[str, Any]:
        """Gets details about a specific actor run."""
        if not self.initialized:
            await self.initialize()
        return self.client.run(run_id).get()


# Global instance
apify_integration = ApifyIntegration()
