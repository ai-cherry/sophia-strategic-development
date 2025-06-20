"""
Pulumi ESC Secret Manager for Arie.
"""
from backend.core.enhanced_pulumi_esc import EnhancedPulumiESC

class ArieSecretManager(EnhancedPulumiESC):
    def __init__(self):
        super().__init__()
    async def get_api_key(self) -> str:
        return await self.get_secret("ARIE_API_KEY")

arie_secret_manager = ArieSecretManager() 