#!/usr/bin/env python3
"""Wrapper to start MCP servers using the development script."""
import os
import sys
from pathlib import Path

# Ensure dev scripts are on path
DEV_DIR = Path(__file__).parent / "dev"
sys.path.insert(0, str(DEV_DIR))

try:
    from start_mcp_servers import main as start_mcp
except Exception as exc:  # fallback to subprocess
    import subprocess
    def main():
        result = subprocess.run([sys.executable, str(DEV_DIR / "start_mcp_servers.py")])
        return result.returncode
else:
    def main():  # type: ignore
        return start_mcp()

if __name__ == "__main__":
    sys.exit(main() or 0)
