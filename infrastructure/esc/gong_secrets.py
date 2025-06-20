"""
Pulumi ESC Secret Manager for Gong.
"""
from backend.core.enhanced_pulumi_esc import EnhancedPulumiESC

class GongSecretManager(EnhancedPulumiESC):
    def __init__(self):
        super().__init__(env_file_name="gong.env")
    async def get_api_key(self) -> str:
        return await self.get_secret("GONG_API_KEY")

gong_secret_manager = GongSecretManager() 