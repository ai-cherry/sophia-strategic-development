"""
Pulumi ESC Secret Manager for Apify.
"""
from backend.core.enhanced_pulumi_esc import EnhancedPulumiESC

class ApifySecretManager(EnhancedPulumiESC):
    def __init__(self):
        super().__init__(env_file_name="apify.env")
    async def get_api_key(self) -> str:
        return await self.get_secret("APIFY_API_KEY")

apify_secret_manager = ApifySecretManager() 