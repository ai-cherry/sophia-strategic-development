
import pulumi_command as command
from pulumi import Config, Output, ResourceOptions

from .base_component import BaseComponent


class EstuaryComponent(BaseComponent):
    def __init__(self, name: str, opts: ResourceOptions = None):
        super().__init__(name, opts)

        config = Config()
        env = config.require("environment")

        estuary_api_key = config.require_secret("estuary_api_key")
        self.estuary_api_url = (
            config.get("estuary_api_url") or "https://api.estuary.tech"
        )

        collection_names = {
            "development": "sophia_dev",
            "staging": "sophia_staging",
            "production": "sophia_prod",
        }
        self.collection_name = collection_names.get(
            env, collection_names["development"]
        )

        # This is a custom resource that uses the Pulumi Command provider to call the Estuary API
        self.collection = command.local.Command(
            "estuary_collection",
            create=Output.concat(
                "curl -X POST '",
                self.estuary_api_url,
                "/collections' ",
                "-H 'Content-Type: application/json' ",
                "-H 'Authorization: Bearer ",
                estuary_api_key,
                "' ",
                f'-d \'{{"name": "{self.collection_name}", "description": "Sophia AI data collection for {env}"}}\'',
            )
            # update and delete commands would be similar
        )

        # Register outputs
        self.register_outputs(
            {
                "collection_name": self.collection_name,
                "api_url": self.estuary_api_url,
                "environment": env,
            }
        )
