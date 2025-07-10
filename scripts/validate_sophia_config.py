#!/usr/bin/env python3
"""
Validate Sophia AI configuration for conflicts and issues

Checks:
1. Port conflicts across all servers
2. Required capabilities coverage
3. Server ownership assignment
4. Resource allocation validity

Date: July 9, 2025
"""

import sys
from collections import defaultdict
from pathlib import Path

import yaml


def load_config() -> dict:
    """Load the unified configuration file"""
    config_path = Path("config/sophia_mcp_unified.yaml")

    if not config_path.exists():
        print(f"❌ Configuration file not found: {config_path}")
        sys.exit(1)

    with open(config_path) as f:
        return yaml.safe_load(f)


def validate_mcp_ports(config: dict) -> bool:
    """Check for port conflicts across all configurations"""

    port_usage = defaultdict(list)
    valid = True

    # Check all server tiers
    for tier, servers in config.get("mcp_servers", {}).items():
        for server_name, server_config in servers.items():
            if isinstance(server_config, dict):
                port = server_config.get("port")
                if port:
                    port_usage[port].append(f"{server_name} ({tier})")

    # Check central services
    for service_name, service_config in config.get("central_services", {}).items():
        if isinstance(service_config, dict):
            port = service_config.get("port")
            if port:
                port_usage[port].append(f"{service_name} (central_service)")

    # Find conflicts
    conflicts = []
    for port, servers in port_usage.items():
        if len(servers) > 1:
            conflicts.append(f"Port {port} conflict: {', '.join(servers)}")

    if conflicts:
        print("❌ Port conflicts found:")
        for conflict in conflicts:
            print(f"  - {conflict}")
        valid = False
    else:
        print("✅ No port conflicts found")

    # Report port allocation summary
    print("\n📊 Port allocation summary:")
    print(f"  - Total ports allocated: {len(port_usage)}")
    print(f"  - Port range used: {min(port_usage.keys())} - {max(port_usage.keys())}")

    return valid


def validate_capabilities(config: dict) -> bool:
    """Ensure all required capabilities are covered"""

    required_capabilities = [
        "MEMORY",
        "EMBEDDING",
        "SEARCH",
        "ANALYTICS",
        "CRM",
        "CALLS",
        "MESSAGING",
        "CODE_ANALYSIS",
        "INFRASTRUCTURE",
        "WORKFLOW",
    ]

    available_capabilities = set()
    capability_providers = defaultdict(list)

    # Collect capabilities from all active servers
    for tier, servers in config.get("mcp_servers", {}).items():
        for server_name, server_config in servers.items():
            if (
                isinstance(server_config, dict)
                and server_config.get("status") == "active"
            ):
                capabilities = server_config.get("capabilities", [])
                for cap in capabilities:
                    available_capabilities.add(cap)
                    capability_providers[cap].append(server_name)

    missing = set(required_capabilities) - available_capabilities
    valid = True

    if missing:
        print(f"\n❌ Missing required capabilities: {missing}")
        valid = False
    else:
        print("\n✅ All required capabilities are covered")

    # Report capability coverage
    print("\n📊 Capability coverage:")
    for cap in sorted(required_capabilities):
        providers = capability_providers.get(cap, [])
        status = "✅" if providers else "❌"
        print(f"  {status} {cap}: {', '.join(providers) if providers else 'MISSING'}")

    return valid


def validate_ownership(config: dict) -> bool:
    """Check that all servers have assigned owners"""

    servers_without_owners = []
    owner_distribution = defaultdict(int)
    valid = True

    # Check all servers
    for tier, servers in config.get("mcp_servers", {}).items():
        for server_name, server_config in servers.items():
            if isinstance(server_config, dict):
                owner = server_config.get("owner")
                if not owner:
                    servers_without_owners.append(f"{server_name} ({tier})")
                else:
                    owner_distribution[owner] += 1

    if servers_without_owners:
        print("\n❌ Servers without owners:")
        for server in servers_without_owners:
            print(f"  - {server}")
        valid = False
    else:
        print("\n✅ All servers have assigned owners")

    # Report ownership distribution
    print("\n📊 Ownership distribution:")
    for owner, count in sorted(owner_distribution.items()):
        print(f"  - {owner}: {count} servers")

    return valid


def validate_resources(config: dict) -> bool:
    """Validate resource allocations"""

    total_memory = 0
    total_cpu = 0
    total_replicas = 0
    valid = True
    issues = []

    # Check all servers
    for tier, servers in config.get("mcp_servers", {}).items():
        for server_name, server_config in servers.items():
            if isinstance(server_config, dict):
                resources = server_config.get("resources", {})

                # Parse memory
                memory_str = resources.get("memory", "0Gi")
                memory_gb = 0
                try:
                    memory_gb = int(memory_str.replace("Gi", ""))
                    total_memory += memory_gb * resources.get("replicas", 1)
                except ValueError:
                    issues.append(
                        f"{server_name}: Invalid memory format '{memory_str}'"
                    )

                # Parse CPU
                cpu_str = resources.get("cpu", "0m")
                cpu_millicores = 0
                try:
                    cpu_millicores = int(cpu_str.replace("m", ""))
                    total_cpu += cpu_millicores * resources.get("replicas", 1)
                except ValueError:
                    issues.append(f"{server_name}: Invalid CPU format '{cpu_str}'")

                # Count replicas
                replicas = resources.get("replicas", 1)
                total_replicas += replicas

                # Validate minimum resources
                if memory_gb < 1:
                    issues.append(f"{server_name}: Memory too low ({memory_str})")
                if cpu_millicores < 500:
                    issues.append(f"{server_name}: CPU too low ({cpu_str})")

    if issues:
        print("\n❌ Resource allocation issues:")
        for issue in issues:
            print(f"  - {issue}")
        valid = False
    else:
        print("\n✅ Resource allocations are valid")

    # Report resource summary
    print("\n📊 Resource allocation summary:")
    print(f"  - Total memory: {total_memory} GB")
    print(f"  - Total CPU: {total_cpu / 1000:.1f} cores")
    print(f"  - Total replicas: {total_replicas}")

    # Resource recommendations
    recommended_memory = total_replicas * 2  # 2GB per replica average
    recommended_cpu = total_replicas * 1000  # 1 core per replica average

    if total_memory > recommended_memory * 1.5:
        print(
            f"  ⚠️  Memory allocation seems high (recommended: ~{recommended_memory} GB)"
        )
    if total_cpu > recommended_cpu * 1.5:
        print(
            f"  ⚠️  CPU allocation seems high (recommended: ~{recommended_cpu / 1000:.1f} cores)"
        )

    return valid


def validate_versions(config: dict) -> bool:
    """Check for version consistency and updates needed"""

    servers_without_versions = []
    version_distribution = defaultdict(list)
    valid = True

    # Check all servers
    for tier, servers in config.get("mcp_servers", {}).items():
        for server_name, server_config in servers.items():
            if isinstance(server_config, dict):
                version = server_config.get("version")
                if not version:
                    servers_without_versions.append(f"{server_name} ({tier})")
                else:
                    # Group by major version
                    major_version = version.split(".")[0]
                    version_distribution[major_version].append(
                        f"{server_name} ({version})"
                    )

    if servers_without_versions:
        print("\n⚠️  Servers without version information:")
        for server in servers_without_versions:
            print(f"  - {server}")
    else:
        print("\n✅ All servers have version information")

    # Report version distribution
    print("\n📊 Version distribution:")
    for major, servers in sorted(version_distribution.items()):
        print(f"  - v{major}.x: {len(servers)} servers")

    return valid


def validate_deprecated(config: dict) -> bool:
    """Check deprecated servers configuration"""

    deprecated = config.get("deprecated_servers", [])

    if not deprecated:
        print("\n⚠️  No deprecated servers listed")
        return True

    print("\n📊 Deprecated servers:")
    for server in deprecated:
        print(f"  - {server['name']}: {server['reason']}")
        print(f"    Removal date: {server.get('removal_date', 'Not specified')}")

    return True


def main():
    """Run all validation checks"""

    print("🔍 Sophia AI Configuration Validator")
    print("=" * 50)

    # Load configuration
    config = load_config()
    print(f"✅ Loaded configuration version {config.get('version', 'unknown')}")
    print(f"   Last updated: {config.get('last_updated', 'unknown')}")
    print(f"   Environment: {config.get('environment', 'unknown')}")

    # Run all validations
    results = []
    results.append(validate_mcp_ports(config))
    results.append(validate_capabilities(config))
    results.append(validate_ownership(config))
    results.append(validate_resources(config))
    results.append(validate_versions(config))
    results.append(validate_deprecated(config))

    # Final summary
    print("\n" + "=" * 50)
    total_checks = len(results)
    passed_checks = sum(results)

    if all(results):
        print(f"✅ All {total_checks} validation checks passed!")
        sys.exit(0)
    else:
        print(
            f"❌ {total_checks - passed_checks} of {total_checks} validation checks failed"
        )
        print("\n🔧 Next steps:")
        print("  1. Fix port conflicts by updating port assignments")
        print("  2. Ensure all required capabilities are covered")
        print("  3. Assign owners to all servers")
        print("  4. Review resource allocations")
        sys.exit(1)


if __name__ == "__main__":
    main()
