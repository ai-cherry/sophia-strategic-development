"""Pulumi ESC Secret Manager for Apollo.io."""

from backend.core.enhanced_pulumi_esc import EnhancedPulumiESC


class ApolloSecretManager(EnhancedPulumiESC):
    def __init__(self):
        super().__init__()

    async def get_api_key(self) -> str:
        return await self.get_secret("APOLLO_API_KEY")


apollo_secret_manager = ApolloSecretManager()
