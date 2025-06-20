"""Pulumi ESC Secret Manager for Pulumi itself.
"""
from backend.core.enhanced_pulumi_esc import EnhancedPulumiESC


class PulumiSecretManager(EnhancedPulumiESC):
    def __init__(self):
        super().__init__()

    async def get_access_token(self) -> str:
        return await self.get_secret("PULUMI_ACCESS_TOKEN")


pulumi_secret_manager = PulumiSecretManager()
