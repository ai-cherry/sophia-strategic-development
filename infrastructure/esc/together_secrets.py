"""
Pulumi ESC Secret Manager for Together AI.
"""
from backend.core.enhanced_pulumi_esc import EnhancedPulumiESC

class TogetherSecretManager(EnhancedPulumiESC):
    def __init__(self):
        super().__init__(env_file_name="together.env")
    async def get_api_key(self) -> str:
        return await self.get_secret("TOGETHER_API_KEY")

together_secret_manager = TogetherSecretManager() 