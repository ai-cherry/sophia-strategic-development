#!/usr/bin/env python3
"""Run a quick MCP server test using the infrastructure test suite."""
import subprocess
import sys
from pathlib import Path

TEST_SCRIPT = Path(__file__).parent / "dev" / "test_infrastructure.py"

if __name__ == "__main__":
    result = subprocess.run([sys.executable, str(TEST_SCRIPT)])
    sys.exit(result.returncode)
