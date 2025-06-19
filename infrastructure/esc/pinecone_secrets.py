"""
Pulumi ESC - Pinecone Secret Management
Manages Pinecone API keys and environment configuration.
"""
import pulumi
import pulumi_pulumiservice as pulumiservice
import os
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
PULUMI_ORG = os.getenv("PULUMI_ORG", "your-pulumi-org") # Replace with your Pulumi org name
PULUMI_PROJECT = "sophia-ai"
PULUMI_STACK = "dev"
ENVIRONMENT_NAME = f"{PULUMI_PROJECT}-{PULUMI_STACK}"
PINECONE_SECRET_NAME = "pineconeApiKey"

# Ensure Pulumi org is set
if PULUMI_ORG == "your-pulumi-org":
    raise ValueError("Please set the PULUMI_ORG environment variable.")

class PineconeSecretManager:
    """Manages Pinecone secrets using Pulumi ESC."""

    def __init__(self, org: str = PULUMI_ORG, project: str = PULUMI_PROJECT, stack: str = PULUMI_STACK):
        self.org = org
        self.project = project
        self.stack = stack
        self.environment_name = f"{project}-{stack}"
        self.full_secret_name = f"sophia.{PINECONE_SECRET_NAME}"

    def create_secret(self, secret_value: str):
        """
        Creates or updates the Pinecone API key in the Pulumi ESC environment.
        This function is intended to be run from an administrative script, not the main app.
        """
        try:
            # Create a Pulumi ESC environment
            environment = pulumiservice.Environment(
                self.environment_name,
                organization=self.org,
                name=self.environment_name,
                yaml=pulumi.Output.from_input(json.dumps({
                    "values": {
                        "sophia": {
                            "pineconeApiKey": {
                                "fn::secret": secret_value
                            }
                        }
                    }
                }))
            )
            logger.info(f"Successfully created/updated environment '{self.environment_name}' with Pinecone secret.")
            return environment
        except Exception as e:
            logger.error(f"Failed to create/update secret in Pulumi ESC: {e}")
            raise

    async def get_pinecone_api_key(self) -> str:
        """
        Retrieves the Pinecone API key from the Pulumi ESC environment.
        This is the method the application will call at runtime.
        """
        try:
            # Open the stack and get the secret value
            opened_env = await pulumiservice.open_environment(
                name=self.environment_name,
                organization=self.org
            )
            return opened_env.get(self.full_secret_name)
        except Exception as e:
            logger.error(f"Failed to retrieve secret '{self.full_secret_name}' from Pulumi ESC: {e}")
            # Fallback to environment variable if ESC fails
            api_key = os.getenv("PINECONE_API_KEY")
            if api_key:
                logger.warning("Falling back to PINECONE_API_KEY environment variable.")
                return api_key
            raise ConnectionError("Could not retrieve Pinecone API key from Pulumi ESC or environment variables.")

# Global instance
pinecone_secret_manager = PineconeSecretManager()

# Example of how to run this to set the secret
# This would typically be in a separate admin script.
if __name__ == '__main__':
    import os
    from dotenv import load_dotenv

    load_dotenv()

    # This script is for demonstration. In a real scenario, you would
    # have a secure way to provide the secret value.
    api_key_from_env = os.getenv("PINECONE_API_KEY_TO_SET")

    if not api_key_from_env:
        print("Please set PINECONE_API_KEY_TO_SET in your .env file to run this example.")
    else:
        print(f"Setting Pinecone API key in Pulumi ESC environment '{ENVIRONMENT_NAME}'...")
        manager = PineconeSecretManager()
        # Note: Running this with `pulumi up` would actually create the secret.
        # This python script defines the resource, but doesn't execute the creation.
        # To make this work directly, you'd use the Pulumi Automation API.
        print("Pulumi resource definition created. Run `pulumi up` in this directory to apply.")

        # For direct execution via Python (requires Pulumi Automation API setup)
        # from pulumi.automation import LocalWorkspace, Stack, create_or_select_stack
        #
        # async def run_pulumi():
        #    stack = create_or_select_stack(stack_name=PULUMI_STACK, project_name=PULUMI_PROJECT, work_dir=".")
        #    stack.set_config("pulumiservice:organization", {"value": PULUMI_ORG})
        #    await stack.up()
        #
        # asyncio.run(run_pulumi()) 