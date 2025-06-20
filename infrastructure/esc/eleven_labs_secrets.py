"""
Pulumi ESC Secret Manager for Eleven Labs.
"""
from backend.core.enhanced_pulumi_esc import EnhancedPulumiESC

class ElevenLabsSecretManager(EnhancedPulumiESC):
    def __init__(self):
        super().__init__()
    async def get_api_key(self) -> str:
        return await self.get_secret("ELEVEN_LABS_API_KEY")

eleven_labs_secret_manager = ElevenLabsSecretManager() 