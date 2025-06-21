"""Pulumi ESC Secret Manager for n8n."""

from backend.core.enhanced_pulumi_esc import EnhancedPulumiESC


class N8nSecretManager(EnhancedPulumiESC):
    def __init__(self):
        super().__init__()

    async def get_api_key(self) -> str:
        return await self.get_secret("N8N_API_KEY")


n8n_secret_manager = N8nSecretManager()
