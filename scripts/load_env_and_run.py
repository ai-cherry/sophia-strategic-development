#!/usr/bin/env python3
"""
Environment loader utility for Sophia AI services
Ensures local.env is loaded before service startup
"""

import os
import subprocess
import sys
from pathlib import Path


def load_local_env():
    """Load environment variables from local.env file"""
    env_file = Path("local.env")

    if not env_file.exists():
        print("⚠️ Warning: local.env file not found")
        return False

    loaded_count = 0
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                # Only set if not already in environment
                if key not in os.environ:
                    os.environ[key] = value
                    loaded_count += 1

    print(f"✅ Loaded {loaded_count} environment variables from local.env")
    return True


def main():
    """Main function to load env and run command"""
    if len(sys.argv) < 2:
        print("Usage: python load_env_and_run.py <command> [args...]")
        sys.exit(1)

    # Load environment
    load_local_env()

    # Ensure critical variables are set
    critical_vars = ["QDRANT_USER", "QDRANT_ACCOUNT"]
    missing = [var for var in critical_vars if not os.getenv(var)]

    if missing:
        print(f"❌ Critical environment variables missing: {', '.join(missing)}")
        print("Please check your local.env file")
        sys.exit(1)

    # Run the command with loaded environment
    command = sys.argv[1:]
    print(f"🚀 Running: {' '.join(command)}")

    try:
        result = subprocess.run(command, env=os.environ.copy(), check=False)
        sys.exit(result.returncode)
    except Exception as e:
        print(f"❌ Error running command: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
