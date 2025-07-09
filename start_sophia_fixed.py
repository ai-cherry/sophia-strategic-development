#!/usr/bin/env python3
"""
Sophia AI Startup Script with PERMANENT Snowflake Fix
Run this before starting any Sophia AI services
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def apply_permanent_snowflake_fix():
    """Apply permanent Snowflake configuration fix"""

    # Force correct environment variables
    correct_config = {
        "SNOWFLAKE_ACCOUNT": "ZNB04675",
        "SNOWFLAKE_USER": "SCOOBYJAVA15",
        "SNOWFLAKE_DATABASE": "SOPHIA_AI",
        "SNOWFLAKE_WAREHOUSE": "SOPHIA_AI_WH",
        "SNOWFLAKE_ROLE": "ACCOUNTADMIN",
        "SNOWFLAKE_SCHEMA": "PROCESSED_AI",
    }

    for key, value in correct_config.items():
        os.environ[key] = value

    # Clear any Python cache that might have old values
    import subprocess

    try:
        # TODO: Validate input before subprocess execution
        subprocess.run(
            ["find", ".", "-name", "*.pyc", "-delete"], capture_output=True, check=False
        )
        # TODO: Validate input before subprocess execution
        subprocess.run(
            [
                "find",
                ".",
                "-name",
                "__pycache__",
                "-type",
                "d",
                "-exec",
                "rm",
                "-rf",
                "{}",
                "+",
            ],
            capture_output=True,
            check=False,
        )
    except Exception:
        pass

    return correct_config


if __name__ == "__main__":
    apply_permanent_snowflake_fix()

    # Test the fix
    try:
        from backend.core.snowflake_override import get_snowflake_connection_params

        params = get_snowflake_connection_params()

        if params["account"] == "ZNB04675":
            pass
        else:
            sys.exit(1)

    except Exception:
        sys.exit(1)
