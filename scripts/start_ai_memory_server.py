#!/usr/bin/env python3
"""
Start AI Memory MCP Server with debugging
"""

import subprocess
import sys
import os
from pathlib import Path
from backend.core.auto_esc_config import get_config_value

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set environment variables
get_config_value("PYTHONPATH") = str(project_root)
get_config_value("MCP_SERVER_PORT") = "9001"

# Start the server directly
server_path = project_root / "mcp-servers" / "ai_memory" / "server.py"

print("Starting AI Memory MCP Server...")
print(f"Server path: {server_path}")
print(f"Python path: {sys.executable}")
print(f"Project root: {project_root}")

# Run the server
try:
    subprocess.run([sys.executable, str(server_path)], check=True)
except subprocess.CalledProcessError as e:
    print(f"Server failed with error: {e}")
except KeyboardInterrupt:
    print("\nServer stopped by user")
