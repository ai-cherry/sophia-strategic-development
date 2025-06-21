"""Pulumi ESC - Snowflake Secret Management.

Manages Snowflake connection credentials.
"""

import logging
import os
from dataclasses import dataclass

import pulumi_pulumiservice as pulumiservice

logger = logging.getLogger(__name__)

PULUMI_ORG = os.getenv("PULUMI_ORG", "your-pulumi-org")
PULUMI_PROJECT = "sophia-ai"
PULUMI_STACK = "dev"

if PULUMI_ORG == "your-pulumi-org":
    raise ValueError("Please set the PULUMI_ORG environment variable.")


@dataclass
class SnowflakeCredentials:
    user: str
    password: str
    account: str
    warehouse: str
    database: str
    schema: str
    role: str


class SnowflakeSecretManager:
    """Manages Snowflake secrets using Pulumi ESC."""

    def __init__(
        self,
        org: str = PULUMI_ORG,
        project: str = PULUMI_PROJECT,
        stack: str = PULUMI_STACK,
    ):
        self.org = org
        self.environment_name = f"{project}-{stack}"

    async def get_snowflake_credentials(self) -> SnowflakeCredentials:
        """Retrieves Snowflake credentials from the Pulumi ESC environment."""
        try:
            opened_env = await pulumiservice.open_environment(
                name=self.environment_name, organization=self.org
            )
            return SnowflakeCredentials(
                user=opened_env.get("sophia.snowflake.user"),
                password=opened_env.get("sophia.snowflake.password"),
                account=opened_env.get("sophia.snowflake.account"),
                warehouse=opened_env.get("sophia.snowflake.warehouse"),
                database=opened_env.get("sophia.snowflake.database"),
                schema=opened_env.get("sophia.snowflake.schema"),
                role=opened_env.get("sophia.snowflake.role"),
            )
        except Exception as e:
            logger.error(
                f"Failed to retrieve Snowflake credentials from Pulumi ESC: {e}"
            )
            # Add fallback to individual environment variables if needed
            raise ConnectionError("Could not retrieve Snowflake credentials.")


snowflake_secret_manager = SnowflakeSecretManager()
