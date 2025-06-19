"""
Pulumi ESC - Vercel Secret Management
Manages Vercel Access Tokens and Team IDs.
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

class VercelSecretManager:
    """Manages Vercel secrets using Pulumi ESC."""

    def __init__(self, org: str = PULUMI_ORG, project: str = PULUMI_PROJECT, stack: str = PULUMI_STACK):
        self.org = org
        self.environment_name = f"{project}-{stack}"

    async def get_vercel_secrets(self) -> dict:
        """
        Retrieves Vercel secrets from the Pulumi ESC environment.
        """
        try:
            opened_env = await pulumiservice.open_environment(
                name=self.environment_name,
                organization=self.org
            )
            return {
                "access_token": opened_env.get("sophia.vercel.accessToken"),
                "team_id": opened_env.get("sophia.vercel.teamId")
            }
        except Exception as e:
            logger.error(f"Failed to retrieve Vercel secrets from Pulumi ESC: {e}")
            # Add fallbacks if needed
            access_token = os.getenv("VERCEL_ACCESS_TOKEN")
            team_id = os.getenv("VERCEL_TEAM_ID")
            if access_token:
                logger.warning("Falling back to VERCEL_ACCESS_TOKEN environment variables.")
                return {"access_token": access_token, "team_id": team_id}
            raise ConnectionError("Could not retrieve Vercel secrets.")

vercel_secret_manager = VercelSecretManager() 