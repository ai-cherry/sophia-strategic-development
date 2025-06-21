#!/usr/bin/env python3
"""Run a quick MCP health check using the simple check script."""

import subprocess
import sys
from pathlib import Path

DEV_DIR = Path(__file__).parent / "dev"
SCRIPT = DEV_DIR / "simple_mcp_check.py"

if __name__ == "__main__":
    result = subprocess.run([sys.executable, str(SCRIPT)])
    sys.exit(result.returncode)
