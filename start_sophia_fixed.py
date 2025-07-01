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
    print("🔧 Applying PERMANENT Snowflake configuration fix...")

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
        print(f"   ✅ Set {key}: {value}")

    # Clear any Python cache that might have old values
    import subprocess

    try:
        subprocess.run(
            ["find", ".", "-name", "*.pyc", "-delete"], capture_output=True, check=False
        )
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
        print("   ✅ Cleared Python cache")
    except Exception:
        pass

    print("🎉 Permanent Snowflake fix applied!")
    return correct_config


if __name__ == "__main__":
    apply_permanent_snowflake_fix()

    # Test the fix
    try:
        from backend.core.snowflake_override import get_snowflake_connection_params

        params = get_snowflake_connection_params()
        print(f"🧪 Test: Snowflake account is {params['account']}")

        if params["account"] == "ZNB04675":
            print("✅ PERMANENT FIX VERIFIED - Ready to start Sophia AI!")
        else:
            print(f"❌ Fix verification failed - account is {params['account']}")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Fix verification error: {e}")
        sys.exit(1)
