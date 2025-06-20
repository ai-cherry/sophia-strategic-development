"""Pulumi ESC Secret Manager for Estuary.
"""
from backend.core.enhanced_pulumi_esc import EnhancedPulumiESC


class EstuarySecretManager(EnhancedPulumiESC):
    def __init__(self):
        super().__init__()

    async def get_api_key(self) -> str:
        return await self.get_secret("ESTUARY_API_KEY")


estuary_secret_manager = EstuarySecretManager()
