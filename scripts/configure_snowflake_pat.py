#!/usr/bin/env python3
"""
Configure Snowflake PAT for Sophia AI
Sets up the Snowflake Programmatic Access Token in the environment
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.core.auto_esc_config import set_config_value, get_config_value


def configure_snowflake_pat():
    """Configure Snowflake PAT token for authentication"""

    # PAT token provided by user
    pat_token = "eyJraWQiOiI1MDg3NDc2OTQxMyIsImFsZyI6IkVTMjU2In0.eyJwIjoiMTk4NzI5NDc2OjUwODc0NzQ1NDc3IiwiaXNzIjoiU0Y6MTA0OSIsImV4cCI6MTc4MjI4MDQ3OH0.8m-fWI5rvCs6b8bvw1quiM-UzW9uPRxMUmE6VAgOFFylAhRkCzch7ojh7CRLeMdii6DD1Owqap0KoOmyxsW77A"

    # Set in environment immediately
    os.environ["SNOWFLAKE_PAT"] = pat_token
    os.environ["SNOWFLAKE_ACCOUNT"] = "UHDECNO-CVB64222"
    os.environ["SNOWFLAKE_USER"] = "SCOOBYJAVA15"
    os.environ["SNOWFLAKE_WAREHOUSE"] = "SOPHIA_AI_COMPUTE_WH"
    os.environ["SNOWFLAKE_DATABASE"] = "AI_MEMORY"
    os.environ["SNOWFLAKE_SCHEMA"] = "VECTORS"
    os.environ["SNOWFLAKE_ROLE"] = "ACCOUNTADMIN"

    # Also set through config system
    set_config_value("snowflake_pat", pat_token)
    set_config_value("snowflake_account", "UHDECNO-CVB64222")
    set_config_value("snowflake_user", "SCOOBYJAVA15")
    set_config_value("snowflake_warehouse", "SOPHIA_AI_COMPUTE_WH")
    set_config_value("snowflake_database", "AI_MEMORY")
    set_config_value("snowflake_schema", "VECTORS")
    set_config_value("snowflake_role", "ACCOUNTADMIN")

    print("✅ Snowflake PAT configured successfully!")
    print(f"   Account: {get_config_value('snowflake_account')}")
    print(f"   User: {get_config_value('snowflake_user')}")
    print(f"   Database: {get_config_value('snowflake_database')}")
    print(f"   PAT Token: {pat_token[:20]}...{pat_token[-20:]}")

    # Update local.env file
    env_file = project_root / "local.env"
    env_lines = []

    # Read existing lines
    if env_file.exists():
        with open(env_file, "r") as f:
            env_lines = f.readlines()

    # Update or add Snowflake variables
    snowflake_vars = {
        "SNOWFLAKE_PAT": pat_token,
        "SNOWFLAKE_ACCOUNT": "UHDECNO-CVB64222",
        "SNOWFLAKE_USER": "SCOOBYJAVA15",
        "SNOWFLAKE_WAREHOUSE": "SOPHIA_AI_COMPUTE_WH",
        "SNOWFLAKE_DATABASE": "AI_MEMORY",
        "SNOWFLAKE_SCHEMA": "VECTORS",
        "SNOWFLAKE_ROLE": "ACCOUNTADMIN",
    }

    # Update existing or add new
    updated_vars = set()
    new_lines = []

    for line in env_lines:
        stripped = line.strip()
        if "=" in stripped:
            key = stripped.split("=")[0]
            if key in snowflake_vars:
                new_lines.append(f"{key}={snowflake_vars[key]}\n")
                updated_vars.add(key)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    # Add any missing variables
    for key, value in snowflake_vars.items():
        if key not in updated_vars:
            new_lines.append(f"{key}={value}\n")

    # Write back
    with open(env_file, "w") as f:
        f.writelines(new_lines)

    print("\n✅ Updated local.env with Snowflake credentials")
    print("\n🚀 Next: Restart backend to use new credentials")


if __name__ == "__main__":
    configure_snowflake_pat()
