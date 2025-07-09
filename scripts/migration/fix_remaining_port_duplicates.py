#!/usr/bin/env python3
"""
Fix remaining port duplicates in mcp_servers nested structure
"""

import json
from pathlib import Path


def fix_remaining_duplicates():
    """Fix remaining port duplicates"""
    ports_file = Path("config/consolidated_mcp_ports.json")

    # Load current config
    with open(ports_file) as f:
        data = json.load(f)

    # Get all ports from active_servers
    used_ports = set(data["active_servers"].values())

    # Fix conflicts in mcp_servers section
    if "mcp_servers" in data:
        # Fix specific known conflicts
        fixes = {
            ("core_intelligence", "linear"): 9040,  # Was conflicting with asana at 9004
            ("core_intelligence", "asana"): 9041,  # Was conflicting with linear at 9006
            (
                "core_intelligence",
                "ui_ux_agent",
            ): 9042,  # Was conflicting with slack at 9008
            (
                "infrastructure",
                "lambda_labs_cli",
            ): 9043,  # Was conflicting with snowflake at 9200
            ("infrastructure", "snowflake_cortex"): 9044,  # Was conflicting at 9201
            (
                "infrastructure",
                "snowflake_admin",
            ): 9045,  # Was conflicting with estuary at 9202
        }

        for (category, server), new_port in fixes.items():
            if (
                category in data["mcp_servers"]
                and server in data["mcp_servers"][category]
            ):
                data["mcp_servers"][category][server]["port"] = new_port
                print(f"Fixed {category}.{server} -> port {new_port}")

    # Save fixed config
    with open(ports_file, "w") as f:
        json.dump(data, f, indent=2)

    print("\nFixed remaining port conflicts")
    print(f"Saved to: {ports_file}")


if __name__ == "__main__":
    fix_remaining_duplicates()
