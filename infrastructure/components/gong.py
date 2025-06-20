from pulumi import ComponentResource, ResourceOptions, Config, Output
import pulumi_command as command
import json

from .base_component import BaseComponent

class GongComponent(BaseComponent):
    def __init__(self, name: str, opts: ResourceOptions = None):
        super().__init__(name, opts)

        config = Config()
        env = config.require("environment")
        
        gong_api_secret = config.require_secret("gong_api_secret")

        webhook_urls = {
            "development": "https://dev-api.payready.com/sophia/gong/webhook",
            "staging": "https://staging-api.payready.com/sophia/gong/webhook",
            "production": "https://api.payready.com/sophia/gong/webhook"
        }
        
        self.webhook_url = webhook_urls.get(env, webhook_urls["development"])

        # This is a custom resource that uses the Pulumi Command provider to call the Gong API
        # Note: A real implementation would need a way to get the webhook ID back from the create
        # command to use in the update and delete commands. This is a simplified example.
        self.webhook = command.local.Command("gong_webhook",
            create=Output.concat(
                "curl -X POST 'https://us-70092.api.gong.io/v2/webhooks' ",
                "-H 'Content-Type: application/json' ",
                "-H 'Authorization: Bearer ", gong_api_secret, "' ",
                f"-d '{{\"name\": \"Sophia AI Integration - {env}\", \"url\": \"{self.webhook_url}\", \"events\": [\"call.done\"]}}'"
            )
            # update and delete commands would be similar
        )
        
        # Register outputs
        self.register_outputs({
            "webhook_url": self.webhook_url,
            "environment": env
        }) 