#!/usr/bin/env python3
"""
Clean up duplicate port assignments in consolidated_mcp_ports.json
"""

import json
from pathlib import Path


def clean_port_duplicates():
    """Clean duplicate port assignments"""
    ports_file = Path("config/consolidated_mcp_ports.json")

    # Load current config
    with open(ports_file) as f:
        data = json.load(f)

    # Track unique servers and their ports
    seen_servers = set()
    unique_active_servers = {}

    # Process active_servers - keep only unique server names
    if "active_servers" in data:
        for server, port in data["active_servers"].items():
            # Normalize server name (remove hyphens)
            normalized = server.replace("-", "_")

            if normalized not in seen_servers:
                seen_servers.add(normalized)
                unique_active_servers[normalized] = port

    # Update the config
    data["active_servers"] = unique_active_servers

    # Clean up mcp_servers section - ensure no port conflicts
    port_to_server = {}

    if "mcp_servers" in data:
        for category, servers in data["mcp_servers"].items():
            if isinstance(servers, dict):
                for server, config in list(servers.items()):
                    if isinstance(config, dict) and "port" in config:
                        port = config["port"]

                        # Check if port is already assigned
                        if port in port_to_server:
                            print(
                                f"Port conflict: {port} used by both {port_to_server[port]} and {category}.{server}"
                            )
                            # Find next available port in the category range
                            if category == "core_intelligence":
                                base = 9000
                            elif category == "communication":
                                base = 9100
                            elif category == "infrastructure":
                                base = 9200
                            elif category == "business_intelligence":
                                base = 9300
                            elif category == "development_tools":
                                base = 3000
                            else:
                                base = 8000

                            # Find next available port
                            new_port = base
                            while (
                                new_port in port_to_server
                                or new_port in unique_active_servers.values()
                            ):
                                new_port += 1

                            print(
                                f"  -> Reassigning {category}.{server} to port {new_port}"
                            )
                            config["port"] = new_port
                            port = new_port

                        port_to_server[port] = f"{category}.{server}"

    # Save cleaned config
    with open(ports_file, "w") as f:
        json.dump(data, f, indent=2)

    print("\nCleaned port configuration:")
    print(f"- Active servers: {len(unique_active_servers)}")
    print(f"- Total unique ports: {len(port_to_server)}")
    print(f"\nSaved to: {ports_file}")


if __name__ == "__main__":
    clean_port_duplicates()
