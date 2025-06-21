import json

import pulumi_docker as docker
from pulumi import Config, ResourceOptions, asset

from .base_component import BaseComponent


class McpComponent(BaseComponent):
    def __init__(self, name: str, opts: ResourceOptions = None):
        super().__init__(name, opts)
        component_opts = ResourceOptions(parent=self)

        config = Config()
        env = config.require("environment")
        registry_url = "sophiaai.azurecr.io"

        mcp_server_configs = [
            {"name": "claude-mcp", "context": "../backend/mcp/claude/", "port": 8010},
            {"name": "openai-mcp", "context": "../backend/mcp/openai/", "port": 8011},
            # ... and so on for other MCP servers
        ]

        self.images = []
        for server_config in mcp_server_configs:
            image_name = f"{registry_url}/{server_config['name']}:{env}"
            image = docker.Image(
                f"{server_config['name']}-image",
                build=docker.DockerBuildArgs(
                    context=server_config["context"],
                    dockerfile=f"{server_config['context']}/Dockerfile",
                    platform="linux/amd64",
                ),
                image_name=image_name,
                skip_push=(env != "production"),
                opts=component_opts,
            )
            self.images.append(image)

        mcp_config_data = {
            "version": "1.0.0",
            "environment": env,
            "servers": [
                {"name": s["name"], "url": f"http://{s['name']}:{s['port']}"}
                for s in mcp_server_configs
            ],
        }

        self.config_file = asset.StringAsset(json.dumps(mcp_config_data, indent=2))

        self.register_outputs(
            {
                "image_names": [img.image_name for img in self.images],
                "config_json": self.config_file,
            }
        )
