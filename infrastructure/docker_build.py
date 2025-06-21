"""Pulumi script for building and publishing Sophia AI's Docker images."""

import pulumi
import pulumi_docker as docker

# --- Configuration ---
config = pulumi.Config()
# E.g., "docker.io/my-username", "gcr.io/my-project", or an ECR URL
registry_url = config.require("docker_registry_url")
image_version = config.get("image_version", "latest")

# Get registry info from the URL for authentication
registry_info = docker.get_registry_info(server=registry_url)

# --- Image Definitions ---

# 1. Sophia API Image
# This image contains the main FastAPI backend.
sophia_api_image = docker.Image(
    "sophia-api-image",
    build=docker.DockerBuildArgs(
        context="..",  # Build from the root of the project
        dockerfile="../Dockerfile",  # The main Dockerfile
        target="production",  # Specify the production stage
    ),
    image_name=f"{registry_url}/sophia-api:{image_version}",
    registry=registry_info,
)

# 2. IAC Toolkit Image
# This image is used for running infrastructure tasks in CI/CD.
iac_toolkit_image = docker.Image(
    "iac-toolkit-image",
    build=docker.DockerBuildArgs(
        context="..",
        dockerfile="../Dockerfile.iac",
    ),
    image_name=f"{registry_url}/iac-toolkit:{image_version}",
    registry=registry_info,
)

# 3. MCP Gateway Image
# The gateway for routing MCP requests.
mcp_gateway_image = docker.Image(
    "mcp-gateway-image",
    build=docker.DockerBuildArgs(
        context="../mcp-gateway",
        dockerfile="../mcp-gateway/Dockerfile",
    ),
    image_name=f"{registry_url}/mcp-gateway:{image_version}",
    registry=registry_info,
)


# --- Outputs ---
pulumi.export("sophia_api_image_name", sophia_api_image.image_name)
pulumi.export("iac_toolkit_image_name", iac_toolkit_image.image_name)
pulumi.export("mcp_gateway_image_name", mcp_gateway_image.image_name)
