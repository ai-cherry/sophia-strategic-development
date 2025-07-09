import shlex

#!/usr/bin/env python3
"""Start all Cline v3.18 enhanced MCP servers."""

import asyncio
import json
import os
import signal
import subprocess
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Active processes
processes = []


def signal_handler(sig, frame):
    """Handle shutdown gracefully."""
    for proc in processes:
        proc.terminate()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


async def start_server(name: str, command: list, env: dict | None = None):
    """Start a single MCP server."""

    # Merge environment variables
    server_env = os.environ.copy()
    if env:
        server_env.update(env)

    # Add v3.18 specific environment variables
    server_env.update(
        {
            "CLINE_V3_18": "true",
            "ENABLE_WEBFETCH": "true",
            "ENABLE_SELF_KNOWLEDGE": "true",
            "ENABLE_IMPROVED_DIFF": "true",
            "ENABLE_MODEL_ROUTING": "true",
        }
    )

    try:
        proc = subprocess.Popen(
            command, env=server_env, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        processes.append(proc)
        return proc
    except Exception:
        return None


async def check_gemini_cli():
    """Check if Gemini CLI is installed."""
    result = subprocess.run(
        shlex.split("which gemini > /dev/null 2>&1"), check=True
    )  # SECURITY FIX: Replaced os.system
    return result == 0


async def main():
    """Start all Cline v3.18 enhanced servers."""

    # Check prerequisites
    gemini_available = await check_gemini_cli()

    # Load configuration
    config_path = Path(__file__).parent.parent / "config" / "cline_v3_18_config.json"
    if config_path.exists():
        with open(config_path) as f:
            json.load(f)
    else:
        pass

    # Define servers to start
    servers = [
        {
            "name": "Enhanced AI Memory Server",
            "command": [
                "python",
                "-m",
                "mcp_servers.ai_memory.enhanced_ai_memory_server",
            ],
            "env": {
                "PORT": "9000",
                "ENABLE_AUTO_DISCOVERY": "true",
                "ENABLE_CONTEXT_AWARE_RECALL": "true",
                "ENABLE_WEBFETCH_INTEGRATION": "true",
                "ENABLE_PATTERN_MATCHING": "true",
            },
        },
        {
            "name": "Enhanced Codacy Server",
            "command": ["python", "-m", "mcp_servers.codacy.enhanced_codacy_server"],
            "env": {
                "PORT": "3008",
                "ENABLE_REAL_TIME_ANALYSIS": "true",
                "ENABLE_SECURITY_SCANNING": "true",
                "ENABLE_PERFORMANCE_INSIGHTS": "true",
                "ENABLE_AI_SUGGESTIONS": "true",
            },
        },
        {
            "name": "Standardized MCP Server (v3.18)",
            "command": ["python", "-m", "backend.mcp.base.standardized_mcp_server"],
            "env": {
                "PORT": "9001",
                "ENABLE_GEMINI_CLI": str(gemini_available).lower(),
                "GEMINI_CLI_PATH": "/usr/local/bin/gemini",
            },
        },
    ]

    # Start all servers
    for server in servers:
        await start_server(server["name"], server["command"], server["env"])
        await asyncio.sleep(1)  # Give each server time to start

    if not processes:
        return

    # Keep running
    try:
        while True:
            await asyncio.sleep(1)
            # Check if any process has died
            for _i, proc in enumerate(processes):
                if proc.poll() is not None:
                    pass
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    asyncio.run(main())
