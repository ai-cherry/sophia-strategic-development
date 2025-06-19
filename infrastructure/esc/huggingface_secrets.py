"""
Pulumi ESC - Hugging Face Secret Management
Manages Hugging Face API keys.
"""
import pulumi
import pulumi_pulumiservice as pulumiservice
import os
import json
import logging

logger = logging.getLogger(__name__)

PULUMI_ORG = os.getenv("PULUMI_ORG", "your-pulumi-org")
PULUMI_PROJECT = "sophia-ai"
PULUMI_STACK = "dev"
ENVIRONMENT_NAME = f"{PULUMI_PROJECT}-{PULUMI_STACK}"
HF_SECRET_NAME = "huggingFaceApiKey"

if PULUMI_ORG == "your-pulumi-org":
    raise ValueError("Please set the PULUMI_ORG environment variable.")

class HuggingFaceSecretManager:
    """Manages Hugging Face secrets using Pulumi ESC."""

    def __init__(self, org: str = PULUMI_ORG, project: str = PULUMI_PROJECT, stack: str = PULUMI_STACK):
        self.org = org
        self.project = project
        self.stack = stack
        self.environment_name = f"{project}-{stack}"
        self.full_secret_name = f"sophia.{HF_SECRET_NAME}"

    async def get_huggingface_api_key(self) -> str:
        """
        Retrieves the Hugging Face API key from the Pulumi ESC environment.
        """
        try:
            opened_env = await pulumiservice.open_environment(
                name=self.environment_name,
                organization=self.org
            )
            return opened_env.get(self.full_secret_name)
        except Exception as e:
            logger.error(f"Failed to retrieve secret '{self.full_secret_name}' from Pulumi ESC: {e}")
            api_key = os.getenv("HUGGING_FACE_API_KEY")
            if api_key:
                logger.warning("Falling back to HUGGING_FACE_API_KEY environment variable.")
                return api_key
            raise ConnectionError("Could not retrieve Hugging Face API key from Pulumi ESC or environment variables.")

huggingface_secret_manager = HuggingFaceSecretManager() 