"""
Pulumi ESC Secret Manager for GitHub.
"""
from backend.core.enhanced_pulumi_esc import EnhancedPulumiESC

class GitHubSecretManager(EnhancedPulumiESC):
    def __init__(self):
        super().__init__()
    async def get_pat(self) -> str:
        return await self.get_secret("GITHUB_PAT")

github_secret_manager = GitHubSecretManager() 