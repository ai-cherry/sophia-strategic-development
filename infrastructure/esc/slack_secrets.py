"""
Pulumi ESC Secret Manager for Slack.
"""
from backend.core.enhanced_pulumi_esc import EnhancedPulumiESC

class SlackSecretManager(EnhancedPulumiESC):
    def __init__(self):
        super().__init__()
    async def get_bot_token(self) -> str:
        return await self.get_secret("SLACK_BOT_TOKEN")

slack_secret_manager = SlackSecretManager() 