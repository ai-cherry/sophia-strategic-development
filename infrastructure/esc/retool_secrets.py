"""Pulumi ESC Secret Manager for Retool
Manages Retool API tokens and other related secrets.
"""
from backend.core.enhanced_pulumi_esc import EnhancedPulumiESC


class RetoolSecretManager(EnhancedPulumiESC):
    """Handles getting and setting Retool secrets via Pulumi ESC.
    """

    def __init__(self):
        super().__init__()

    async def get_retool_api_token(self) -> str:
        """Retrieves the Retool API token from environment variables or Pulumi ESC.
        """
        return await self.get_secret("RETOOL_API_TOKEN")

    async def set_retool_api_token(self, token: str):
        """Sets the Retool API token in the environment file.
        """
        await self.set_secret("RETOOL_API_TOKEN", token)


# Global instance
retool_secret_manager = RetoolSecretManager()

if __name__ == "__main__":
    import asyncio

    async def main():
        """Manual testing for Retool Secret Manager.
        """
        print("Testing Retool Secret Manager...")

        # Set a dummy token for testing
        dummy_token = "dummy-retool-token-for-testing"
        await retool_secret_manager.set_retool_api_token(dummy_token)
        print("Set dummy token.")

        # Get the token
        retrieved_token = await retool_secret_manager.get_retool_api_token()
        print(f"Retrieved token: {retrieved_token}")

        assert retrieved_token == dummy_token
        print("✅ Retool secret management test passed!")

    asyncio.run(main())
