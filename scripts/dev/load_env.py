#!/usr/bin/env python3
"""Load environment variables from .env file"""

import os
import sys
from pathlib import Path


def load_env_file(env_file=".env"):
    """Load environment variables from .env file"""
    env_path = Path(env_file)
    if not env_path.exists():
        print(f"Error: {env_file} not found")
        return False

    print(f"Loading environment variables from {env_file}")
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            key, value = line.split("=", 1)
            os.environ[key] = value
            print(f"Set {key}")

    return True


if __name__ == "__main__":
    env_file = ".env"
    if len(sys.argv) > 1:
        env_file = sys.argv[1]

    if load_env_file(env_file):
        print("Environment variables loaded successfully")
    else:
        print("Failed to load environment variables")
        sys.exit(1)
