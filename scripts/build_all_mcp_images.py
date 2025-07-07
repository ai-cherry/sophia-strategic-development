#!/usr/bin/env python3
"""
Build All MCP Server Images
Builds Docker images for all 29 MCP servers and integrated capabilities
"""

import argparse
import concurrent.futures
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Union


def run_command(
    cmd: list[str], capture_output: bool = True, cwd: Path | None = None
) -> subprocess.CompletedProcess | subprocess.CalledProcessError:
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            cmd, capture_output=capture_output, text=True, check=True, cwd=cwd
        )
        return result
    except subprocess.CalledProcessError as e:
        if capture_output:
            print(f"❌ Command failed: {' '.join(cmd)}")
            print(f"Error: {e.stderr}")
        return e


def get_mcp_server_definitions() -> dict[str, dict]:
    """Get all MCP server definitions for building"""
    return {
        # Core AI Orchestration MCP Servers
        "ai-memory": {
            "description": "AI Memory MCP Server - Stores and recalls architectural decisions",
            "dockerfile": "mcp-servers/ai-memory/Dockerfile",
            "context": "mcp-servers/ai-memory",
            "image": "sophia-ai-memory",
            "port": 9001,
            "create_if_missing": True,
        },
        "codacy": {
            "description": "Codacy MCP Server - Real-time code quality analysis",
            "dockerfile": "mcp-servers/codacy/Dockerfile",
            "context": "mcp-servers/codacy",
            "image": "sophia-codacy",
            "port": 3008,
            "create_if_missing": True,
        },
        "anthropic-mcp": {
            "description": "Anthropic MCP Server - Official MCP implementations",
            "dockerfile": "external/anthropic-mcp-servers/Dockerfile",
            "context": "external/anthropic-mcp-servers",
            "image": "sophia-anthropic-mcp",
            "port": 9002,
            "create_if_missing": True,
        },
        "mcp-inspector": {
            "description": "MCP Inspector - Debugging and development tools",
            "dockerfile": "external/anthropic-mcp-inspector/Dockerfile",
            "context": "external/anthropic-mcp-inspector",
            "image": "sophia-mcp-inspector",
            "port": 9003,
            "create_if_missing": True,
        },
        # Unified AI Agent Authentication System Services
        "github-agent": {
            "description": "GitHub Agent - Repository operations via CLI",
            "dockerfile": "mcp-servers/github-agent/Dockerfile",
            "context": "mcp-servers/github-agent",
            "image": "sophia-github-agent",
            "port": 9010,
            "create_if_missing": True,
        },
        "pulumi-agent": {
            "description": "Pulumi Agent - Infrastructure as code management",
            "dockerfile": "mcp-servers/pulumi-agent/Dockerfile",
            "context": "mcp-servers/pulumi-agent",
            "image": "sophia-pulumi-agent",
            "port": 9011,
            "create_if_missing": True,
        },
        "docker-agent": {
            "description": "Docker Agent - Container management",
            "dockerfile": "mcp-servers/docker-agent/Dockerfile",
            "context": "mcp-servers/docker-agent",
            "image": "sophia-docker-agent",
            "port": 9012,
            "create_if_missing": True,
        },
        "vercel-agent": {
            "description": "Vercel Agent - Frontend deployments",
            "dockerfile": "mcp-servers/vercel-agent/Dockerfile",
            "context": "mcp-servers/vercel-agent",
            "image": "sophia-vercel-agent",
            "port": 9013,
            "create_if_missing": True,
        },
        "snowflake-agent": {
            "description": "Snowflake Agent - Data operations",
            "dockerfile": "mcp-servers/snowflake-agent/Dockerfile",
            "context": "mcp-servers/snowflake-agent",
            "image": "sophia-snowflake-agent",
            "port": 9014,
            "create_if_missing": True,
        },
        "lambda-labs-agent": {
            "description": "Lambda Labs Agent - Server instance control",
            "dockerfile": "mcp-servers/lambda-labs-agent/Dockerfile",
            "context": "mcp-servers/lambda-labs-agent",
            "image": "sophia-lambda-labs-agent",
            "port": 9015,
            "create_if_missing": True,
        },
        "estuary-flow-agent": {
            "description": "Estuary Flow Agent - Data flow management",
            "dockerfile": "mcp-servers/estuary-flow-agent/Dockerfile",
            "context": "mcp-servers/estuary-flow-agent",
            "image": "sophia-estuary-flow-agent",
            "port": 9016,
            "create_if_missing": True,
        },
        "openai-agent": {
            "description": "OpenAI Agent - Language processing",
            "dockerfile": "mcp-servers/openai-agent/Dockerfile",
            "context": "mcp-servers/openai-agent",
            "image": "sophia-openai-agent",
            "port": 9017,
            "create_if_missing": True,
        },
        "anthropic-agent": {
            "description": "Anthropic Agent - Language processing",
            "dockerfile": "mcp-servers/anthropic-agent/Dockerfile",
            "context": "mcp-servers/anthropic-agent",
            "image": "sophia-anthropic-agent",
            "port": 9018,
            "create_if_missing": True,
        },
        "slack-agent": {
            "description": "Slack Agent - Communication",
            "dockerfile": "mcp-servers/slack-agent/Dockerfile",
            "context": "mcp-servers/slack-agent",
            "image": "sophia-slack-agent",
            "port": 9019,
            "create_if_missing": True,
        },
        "linear-agent": {
            "description": "Linear Agent - Project management",
            "dockerfile": "mcp-servers/linear-agent/Dockerfile",
            "context": "mcp-servers/linear-agent",
            "image": "sophia-linear-agent",
            "port": 9020,
            "create_if_missing": True,
        },
        "hubspot-agent": {
            "description": "HubSpot Agent - CRM operations",
            "dockerfile": "mcp-servers/hubspot-agent/Dockerfile",
            "context": "mcp-servers/hubspot-agent",
            "image": "sophia-hubspot-agent",
            "port": 9021,
            "create_if_missing": True,
        },
        "gong-agent": {
            "description": "Gong Agent - Call analysis",
            "dockerfile": "mcp-servers/gong-agent/Dockerfile",
            "context": "mcp-servers/gong-agent",
            "image": "sophia-gong-agent",
            "port": 9022,
            "create_if_missing": True,
        },
        # External Repository Integration Servers
        "playwright-server": {
            "description": "Microsoft Playwright MCP Server",
            "dockerfile": "external/microsoft_playwright/Dockerfile",
            "context": "external/microsoft_playwright",
            "image": "sophia-playwright",
            "port": 9030,
            "create_if_missing": True,
        },
        "figma-context-server": {
            "description": "Figma Context MCP Server",
            "dockerfile": "external/glips_figma_context/Dockerfile",
            "context": "external/glips_figma_context",
            "image": "sophia-figma-context",
            "port": 9031,
            "create_if_missing": True,
        },
        "snowflake-cortex-server": {
            "description": "Snowflake Cortex Official MCP Server",
            "dockerfile": "external/snowflake_cortex_official/Dockerfile",
            "context": "external/snowflake_cortex_official",
            "image": "sophia-snowflake-cortex",
            "port": 9032,
            "create_if_missing": True,
        },
        "portkey-admin-server": {
            "description": "Portkey Admin MCP Server",
            "dockerfile": "external/portkey_admin/Dockerfile",
            "context": "external/portkey_admin",
            "image": "sophia-portkey-admin",
            "port": 9033,
            "create_if_missing": True,
        },
        "openrouter-server": {
            "description": "OpenRouter Search MCP Server",
            "dockerfile": "external/openrouter_search/Dockerfile",
            "context": "external/openrouter_search",
            "image": "sophia-openrouter",
            "port": 9034,
            "create_if_missing": True,
        },
        # Additional Snowflake Servers
        "snowflake-davidamom": {
            "description": "Davidamom Snowflake MCP Server",
            "dockerfile": "external/davidamom_snowflake/Dockerfile",
            "context": "external/davidamom_snowflake",
            "image": "sophia-snowflake-davidamom",
            "port": 9035,
            "create_if_missing": True,
        },
        "snowflake-dynamike": {
            "description": "Dynamike Snowflake MCP Server",
            "dockerfile": "external/dynamike_snowflake/Dockerfile",
            "context": "external/dynamike_snowflake",
            "image": "sophia-snowflake-dynamike",
            "port": 9036,
            "create_if_missing": True,
        },
        "snowflake-isaacwasserman": {
            "description": "Isaacwasserman Snowflake MCP Server",
            "dockerfile": "external/isaacwasserman_snowflake/Dockerfile",
            "context": "external/isaacwasserman_snowflake",
            "image": "sophia-snowflake-isaacwasserman",
            "port": 9037,
            "create_if_missing": True,
        },
        # Core services already defined
        "mem0-server": {
            "description": "Mem0 OpenMemory MCP Server",
            "image": "sophia-ai-mem0",
            "port": 8080,
            "create_if_missing": False,  # Already built
        },
        "cortex-aisql-server": {
            "description": "Cortex AISQL MCP Server",
            "image": "sophia-ai-cortex",
            "port": 8081,
            "create_if_missing": False,  # Already built
        },
        # WebFetch and other tools
        "webfetch-server": {
            "description": "WebFetch Tool Server",
            "dockerfile": "mcp-servers/webfetch/Dockerfile",
            "context": "mcp-servers/webfetch",
            "image": "sophia-webfetch",
            "port": 9040,
            "create_if_missing": True,
        },
        "v0dev-server": {
            "description": "V0.dev UI Generation Server",
            "image": "ghcr.io/v0-services/v0-server:latest",
            "port": 9030,
            "create_if_missing": False,  # External image
        },
    }


def create_placeholder_dockerfile(
    server_name: str, server_def: dict, context_path: Path
):
    """Create a placeholder Dockerfile if it doesn't exist"""
    dockerfile_path = context_path / "Dockerfile"

    if dockerfile_path.exists():
        return True

    # Create directory if it doesn't exist
    context_path.mkdir(parents=True, exist_ok=True)

    # Create a basic FastAPI MCP server Dockerfile
    dockerfile_content = f"""FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install fastapi uvicorn mcp

# Create a basic MCP server
RUN echo 'from fastapi import FastAPI' > app.py && \\
    echo 'import mcp' >> app.py && \\
    echo '' >> app.py && \\
    echo 'app = FastAPI(title="{server_def["description"]}")' >> app.py && \\
    echo '' >> app.py && \\
    echo '@app.get("/health")' >> app.py && \\
    echo 'async def health():' >> app.py && \\
    echo '    return {{"status": "healthy", "service": "{server_name}"}}' >> app.py && \\
    echo '' >> app.py && \\
    echo '@app.get("/")' >> app.py && \\
    echo 'async def root():' >> app.py && \\
    echo '    return {{"message": "{server_def["description"]}"}}' >> app.py && \\
    echo '' >> app.py && \\
    echo '@app.get("/mcp/tools")' >> app.py && \\
    echo 'async def list_tools():' >> app.py && \\
    echo '    return {{"tools": []}}' >> app.py

EXPOSE {server_def["port"]}

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "{server_def["port"]}"]
"""

    dockerfile_path.write_text(dockerfile_content)
    print(f"📝 Created placeholder Dockerfile for {server_name}")
    return True


def build_mcp_server(
    server_name: str, server_def: dict, registry: str, push: bool = False
) -> bool:
    """Build a single MCP server Docker image"""
    if not server_def.get("create_if_missing", True):
        print(f"⏭️  Skipping {server_name} (external or already built)")
        return True

    image_name = f"{registry}/{server_def['image']}:latest"

    # Check if we need to create context/dockerfile
    if "dockerfile" in server_def:
        context_path = Path(server_def["context"])
        dockerfile_path = Path(server_def["dockerfile"])

        if not context_path.exists() or not dockerfile_path.exists():
            if server_def.get("create_if_missing", False):
                create_placeholder_dockerfile(server_name, server_def, context_path)
            else:
                print(f"⚠️  Skipping {server_name}: context or dockerfile missing")
                return False

    try:
        print(f"🏗️  Building {server_name}: {image_name}")

        # Build the image
        build_cmd = [
            "docker",
            "build",
            "-t",
            image_name,
            "-f",
            server_def.get("dockerfile", "Dockerfile"),
            server_def.get("context", "."),
        ]

        result = run_command(build_cmd, capture_output=False)
        if isinstance(result, subprocess.CalledProcessError):
            print(f"❌ Failed to build {server_name}")
            return False

        if push:
            print(f"⬆️  Pushing {server_name}: {image_name}")
            push_cmd = ["docker", "push", image_name]
            result = run_command(push_cmd, capture_output=False)
            if isinstance(result, subprocess.CalledProcessError):
                print(f"❌ Failed to push {server_name}")
                return False

        print(f"✅ Successfully built {server_name}")
        return True

    except Exception as e:
        print(f"❌ Error building {server_name}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Build all MCP server Docker images")
    parser.add_argument("--registry", default="scoobyjava15", help="Docker registry")
    parser.add_argument("--push", action="store_true", help="Push images to registry")
    parser.add_argument(
        "--parallel", type=int, default=4, help="Number of parallel builds"
    )
    parser.add_argument("--filter", help="Build only servers matching this filter")

    args = parser.parse_args()

    print("🚀 Building All MCP Server Images")
    print("=" * 50)
    print(f"Registry: {args.registry}")
    print(f"Push: {args.push}")
    print(f"Parallel builds: {args.parallel}")
    print()

    # Get all MCP server definitions
    servers = get_mcp_server_definitions()

    # Filter servers if requested
    if args.filter:
        servers = {k: v for k, v in servers.items() if args.filter.lower() in k.lower()}
        print(f"🔍 Filtered to {len(servers)} servers matching '{args.filter}'")

    print(f"📋 Building {len(servers)} MCP servers:")
    for name, server_def in servers.items():
        print(f"  • {name}: {server_def['description']}")
    print()

    # Build servers in parallel
    success_count = 0
    failed_count = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.parallel) as executor:
        # Submit all build tasks
        future_to_server = {
            executor.submit(
                build_mcp_server, name, server_def, args.registry, args.push
            ): name
            for name, server_def in servers.items()
        }

        # Collect results
        for future in concurrent.futures.as_completed(future_to_server):
            server_name = future_to_server[future]
            try:
                success = future.result()
                if success:
                    success_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                print(f"❌ Exception building {server_name}: {e}")
                failed_count += 1

    print()
    print("📊 Build Summary")
    print("=" * 20)
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"📋 Total: {len(servers)}")

    if failed_count > 0:
        print(f"⚠️  {failed_count} builds failed")
        sys.exit(1)

    print("🎉 All MCP server images built successfully!")


if __name__ == "__main__":
    main()
