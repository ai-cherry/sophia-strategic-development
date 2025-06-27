#!/usr/bin/env python3
"""Start all Cline v3.18 enhanced MCP servers."""

import asyncio
import subprocess
import sys
import os
import json
from pathlib import Path
import signal

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Active processes
processes = []

def signal_handler(sig, frame):
    """Handle shutdown gracefully."""
    print("\n🛑 Shutting down Cline v3.18 servers...")
    for proc in processes:
        proc.terminate()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

async def start_server(name: str, command: list, env: dict = None):
    """Start a single MCP server."""
    print(f"🚀 Starting {name}...")
    
    # Merge environment variables
    server_env = os.environ.copy()
    if env:
        server_env.update(env)
    
    # Add v3.18 specific environment variables
    server_env.update({
        "CLINE_V3_18": "true",
        "ENABLE_WEBFETCH": "true",
        "ENABLE_SELF_KNOWLEDGE": "true",
        "ENABLE_IMPROVED_DIFF": "true",
        "ENABLE_MODEL_ROUTING": "true"
    })
    
    try:
        proc = subprocess.Popen(
            command,
            env=server_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        processes.append(proc)
        print(f"✅ {name} started (PID: {proc.pid})")
        return proc
    except Exception as e:
        print(f"❌ Failed to start {name}: {e}")
        return None

async def check_gemini_cli():
    """Check if Gemini CLI is installed."""
    result = os.system("which gemini > /dev/null 2>&1")
    if result != 0:
        print("⚠️  Gemini CLI not found. Install with: npm install -g @google/generative-ai-cli")
        print("   Continuing without Gemini CLI support...")
        return False
    print("✅ Gemini CLI detected")
    return True

async def main():
    """Start all Cline v3.18 enhanced servers."""
    print("🎯 Cline v3.18 Enhanced MCP Server Launcher")
    print("==========================================")
    
    # Check prerequisites
    gemini_available = await check_gemini_cli()
    
    # Load configuration
    config_path = Path(__file__).parent.parent / "config" / "cline_v3_18_config.json"
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
        print("✅ Loaded Cline v3.18 configuration")
    else:
        print("⚠️  No configuration found, using defaults")
        config = {}
    
    # Define servers to start
    servers = [
        {
            "name": "Enhanced AI Memory Server",
            "command": ["python", "-m", "mcp_servers.ai_memory.enhanced_ai_memory_server"],
            "env": {
                "PORT": "9000",
                "ENABLE_AUTO_DISCOVERY": "true",
                "ENABLE_CONTEXT_AWARE_RECALL": "true",
                "ENABLE_WEBFETCH_INTEGRATION": "true",
                "ENABLE_PATTERN_MATCHING": "true"
            }
        },
        {
            "name": "Enhanced Codacy Server",
            "command": ["python", "-m", "mcp_servers.codacy.enhanced_codacy_server"],
            "env": {
                "PORT": "3008",
                "ENABLE_REAL_TIME_ANALYSIS": "true",
                "ENABLE_SECURITY_SCANNING": "true",
                "ENABLE_PERFORMANCE_INSIGHTS": "true",
                "ENABLE_AI_SUGGESTIONS": "true"
            }
        },
        {
            "name": "Standardized MCP Server (v3.18)",
            "command": ["python", "-m", "backend.mcp.base.standardized_mcp_server"],
            "env": {
                "PORT": "9001",
                "ENABLE_GEMINI_CLI": str(gemini_available).lower(),
                "GEMINI_CLI_PATH": "/usr/local/bin/gemini"
            }
        }
    ]
    
    # Start all servers
    print("\n🚀 Starting Cline v3.18 servers...")
    for server in servers:
        await start_server(server["name"], server["command"], server["env"])
        await asyncio.sleep(1)  # Give each server time to start
    
    if not processes:
        print("\n❌ No servers started successfully!")
        return
    
    print("\n✅ All Cline v3.18 servers started!")
    print("\n📊 Server Status:")
    print("================")
    print(f"• Enhanced AI Memory: http://localhost:9000")
    print(f"• Enhanced Codacy: http://localhost:3008")
    print(f"• Standardized MCP: http://localhost:9001")
    
    print("\n🎯 Cline v3.18 Features Enabled:")
    print("================================")
    print("✅ Gemini CLI Integration" if gemini_available else "❌ Gemini CLI (not installed)")
    print("✅ WebFetch with Caching")
    print("✅ Self-Knowledge Capabilities")
    print("✅ Improved Diff Editing")
    print("✅ AI Memory Auto-Discovery")
    print("✅ Real-time Code Analysis")
    print("✅ Model Routing (Claude 4, Gemini, GPT-4, Cortex)")
    
    print("\n💡 Natural Language Commands:")
    print("============================")
    print('• "Process this large file with Gemini" → Free Gemini CLI')
    print('• "Fetch docs from [url]" → WebFetch with caching')
    print('• "Remember this decision" → AI Memory auto-discovery')
    print('• "Analyze code quality" → Real-time Codacy analysis')
    print('• "What can you do?" → Self-knowledge capabilities')
    
    print("\n🛑 Press Ctrl+C to stop all servers")
    
    # Keep running
    try:
        while True:
            await asyncio.sleep(1)
            # Check if any process has died
            for i, proc in enumerate(processes):
                if proc.poll() is not None:
                    print(f"\n⚠️  Server {i} died unexpectedly!")
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    asyncio.run(main())
