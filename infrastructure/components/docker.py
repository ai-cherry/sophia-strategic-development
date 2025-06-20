from pulumi import ComponentResource, ResourceOptions, Config, Output
import pulumi_docker as docker
import json
from typing import List

from .base_component import BaseComponent

class DockerComponent(BaseComponent):
    def __init__(self, name: str, mcp_images: List[docker.Image] = [], opts: ResourceOptions = None):
        super().__init__(name, opts)
        component_opts = ResourceOptions(parent=self)

        config = Config()
        env = config.require("environment")
        
        registry_url = "sophiaai.azurecr.io" # Assuming a single registry
        
        # Docker provider setup would go here if needed, but for image builds it's often not.

        # Define image configurations
        image_configs = [
            {"name": "sophia-api", "context": "../", "dockerfile": "../Dockerfile"},
            {"name": "sophia-admin", "context": "../sophia_admin_api/", "dockerfile": "../sophia_admin_api/Dockerfile"},
            # ... and so on for other images
        ]
        
        self.images = []
        for img_config in image_configs:
            image_name = f"{registry_url}/{img_config['name']}:{env}"
            image = docker.Image(img_config['name'],
                build=docker.DockerBuildArgs(
                    context=img_config["context"],
                    dockerfile=img_config["dockerfile"],
                    platform="linux/amd64"
                ),
                image_name=image_name,
                skip_push=(env != "production"),
                opts=component_opts
            )
            self.images.append(image)

        # Combine standard images with MCP images
        all_images = self.images + mcp_images

        # Create Docker network
        network_name = f"sophia-network-{env}"
        self.network = docker.Network(network_name,
            name=network_name,
            opts=component_opts
        )

        # Create Docker containers for all images
        self.containers = []
        for image in all_images:
            container_name = image.image_name.split("/")[-1].split(":")[0]
            container = docker.Container(f"{container_name}-container",
                name=f"{container_name}-{env}",
                image=image.base_image_name,
                networks_advanced=[docker.ContainerNetworksAdvancedArgs(name=self.network.name)],
                # Ports would need to be configured dynamically
                opts=ResourceOptions(depends_on=[self.network, image])
            )
            self.containers.append(container)

        # Register outputs
        self.register_outputs({
            "registry_url": registry_url,
            "image_names": [img.image_name for img in all_images],
            "network_name": self.network.name,
            "container_names": [c.name for c in self.containers]
        }) 