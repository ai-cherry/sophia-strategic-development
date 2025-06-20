"""
Sophia AI - Main Infrastructure as Code
This module brings together all infrastructure resources for the Sophia AI platform
"""

import pulumi
from pulumi import Config
import os
import sys

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import component-based infrastructure
from components.snowflake import SnowflakeComponent
from components.gong import GongComponent
from components.vercel import VercelComponent
from components.estuary import EstuaryComponent
from components import portkey, openrouter
from components.lambda_labs import LambdaLabsComponent
from components.airbyte import AirbyteComponent
from components.github import GitHubComponent
from components.docker import DockerComponent
from components.mcp import McpComponent
from components.pulumi_esc import PulumiEscComponent
from components.pinecone import PineconeComponent

# Import legacy infrastructure modules
import vercel
import estuary
import lambda_labs
import airbyte
import github
import pulumi_esc
import docker
import mcp

# Load configuration
config = Config()
env = config.require("environment")  # development, staging, or production

# --- Component-based Infrastructure ---
snowflake_component = SnowflakeComponent("snowflake")
gong_component = GongComponent("gong")
vercel_component = VercelComponent("vercel")
estuary_component = EstuaryComponent("estuary")
# lambda_labs_component = LambdaLabsComponent("lambda_labs")
# airbyte_component = AirbyteComponent("airbyte",
#     snowflake_config=snowflake_component.outputs
# )
github_component = GitHubComponent("github")
mcp_component = McpComponent("mcp")
docker_component = DockerComponent("docker", mcp_images=mcp_component.images)
pinecone_component = PineconeComponent("pinecone")
pulumi_esc_component = PulumiEscComponent("pulumi_esc")

# --- Legacy Infrastructure ---

# Create a stack output with all the exported values
pulumi.export("environment", env)

# Snowflake outputs (now from the component)
pulumi.export("snowflake", snowflake_component.outputs)

# Gong outputs (now from the component)
pulumi.export("gong", gong_component.outputs)

# Vercel outputs (now from the component)
pulumi.export("vercel", vercel_component.outputs)

# Estuary outputs (now from the component)
pulumi.export("estuary", estuary_component.outputs)

# Portkey outputs
pulumi.export("portkey", {
    "base_url": portkey.api_base_urls.get(env, portkey.api_base_urls["development"]),
    "virtual_key_name": portkey.virtual_key_config["name"],
    "environment": env
})

# OpenRouter outputs
pulumi.export("openrouter", {
    "base_url": openrouter.api_base_urls.get(env, openrouter.api_base_urls["development"]),
    "default_model": openrouter.openrouter_provider["default_model"],
    "route_prefix": openrouter.openrouter_provider["default_route_prefix"],
    "environment": env
})

# Lambda Labs outputs (now from the component)
# pulumi.export("lambda_labs", lambda_labs_component.outputs)

# Airbyte outputs (now from the component)
# pulumi.export("airbyte", airbyte_component.outputs)

# GitHub outputs (now from the component)
pulumi.export("github", github_component.outputs)

# Pinecone outputs (now from the component)
pulumi.export("pinecone", pinecone_component.outputs)

# Pulumi ESC outputs (now from the component)
pulumi.export("pulumi_esc", pulumi_esc_component.outputs)

# Docker outputs (now from the component)
pulumi.export("docker", docker_component.outputs)

# MCP outputs (now from the component)
pulumi.export("mcp", mcp_component.outputs)

# Create a combined configuration output
pulumi.export("sophia_config", {
    "environment": env,
    "snowflake": {
        "warehouse": snowflake_component.outputs["warehouse_name"],
        "database": snowflake_component.outputs["database_name"],
        "schema": snowflake_component.outputs["schema_name"],
        "role": snowflake_component.outputs["role_name"]
    },
    "gong": {
        "webhook_url": gong_component.outputs["webhook_url"]
    },
    "vercel": {
        "project": vercel_component.outputs["project_name"],
        "domain": vercel_component.outputs["domain"],
        "url": vercel_component.outputs["deployment_url"]
    },
    "estuary": {
        "collection": estuary.collection_names.get(env, estuary.collection_names["development"]),
        "api_url": estuary.estuary_api_url
    },
    "portkey": {
        "base_url": portkey.api_base_urls.get(env, portkey.api_base_urls["development"]),
        "virtual_key_name": portkey.virtual_key_config["name"]
    },
    "openrouter": {
        "base_url": openrouter.api_base_urls.get(env, openrouter.api_base_urls["development"]),
        "default_model": openrouter.openrouter_provider["default_model"],
        "route_prefix": openrouter.openrouter_provider["default_route_prefix"]
    },
    "lambda_labs": {
        "instance_type": lambda_labs_component.outputs["instance_type"],
        "region": lambda_labs_component.outputs["region"],
        "data_bucket": lambda_labs_component.outputs["data_bucket"]
    },
    "airbyte": {
        "base_url": airbyte.airbyte_urls.get(env, airbyte.airbyte_urls["development"]),
        "workspace_name": airbyte.workspace_config["name"]
    },
    "github": {
        "repository_name": github_component.outputs["repository_name"],
        "repository_url": github_component.outputs["repository_url"]
    },
    "pinecone": {
        "knowledge_base_index": pinecone_component.outputs["knowledge_base_index"],
        "ai_memory_index": pinecone_component.outputs["ai_memory_index"]
    },
    "docker": {
        "registry": docker.registry_urls.get(env, docker.registry_urls["development"]),
        "network": docker.network.name
    },
    "mcp": {
        "server_names": [server["name"] for server in mcp.mcp_server_configs],
        "config_file_url_placeholder": "Access mcp_config.json from stack outputs"
    }
})

# Print a success message
pulumi.export("message", f"Sophia AI infrastructure for {env} environment has been successfully deployed!")
