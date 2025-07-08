#!/usr/bin/env python3
"""Migrate MCP registry to v2 with YAML configuration."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from infrastructure.mcp_servers.mcp_registry import MCPRegistry
from infrastructure.mcp_servers.registry_v2 import get_registry


def migrate_to_yaml():
    """Migrate existing registry to YAML format."""
    print("🔄 Starting MCP Registry migration to v2...")

    # Load existing registry
    old_registry = MCPRegistry()
    old_servers = old_registry._configs

    print(f"📊 Found {len(old_servers)} servers in old registry")

    # Load new registry
    new_registry = get_registry()

    # Compare
    print("\n📋 Migration Summary:")
    print(f"  - Old registry servers: {len(old_servers)}")
    print(f"  - New registry servers: {len(new_registry._servers)}")

    # Find servers not in new registry
    old_names = set(old_servers.keys())
    new_names = set(new_registry._servers.keys())

    missing = old_names - new_names
    if missing:
        print("\n⚠️  Servers in old registry but not in YAML:")
        for name in sorted(missing):
            server = old_servers[name]
            print(f"  - {name} (port {server.port})")

    added = new_names - old_names
    if added:
        print("\n✅ New servers added in v2:")
        for name in sorted(added):
            server = new_registry.get_server(name)
            print(f"  - {name} ({server.tier.value}, port {server.port})")

    # Show tier distribution
    print("\n📊 Tier Distribution:")
    stats = new_registry.get_statistics()
    for tier, data in stats["tier_statistics"].items():
        print(f"  - {tier}: {data['total']} servers")

    # Show capability coverage
    print("\n🎯 Capability Coverage:")
    cap_stats = stats["capability_statistics"]
    for cap in sorted(cap_stats.keys()):
        data = cap_stats[cap]
        print(f"  - {cap}: {data['total']} servers")

    # Create compatibility shim
    print("\n🔧 Creating compatibility shim...")
    create_compatibility_shim()

    print("\n✅ Migration complete!")
    print("\n📝 Next steps:")
    print("  1. Review the YAML configuration at config/mcp/mcp_servers.yaml")
    print("  2. Update any code using MCPRegistry to use RegistryV2")
    print("  3. Run health checks: python scripts/check_mcp_health.py")


def create_compatibility_shim():
    """Create a compatibility shim for old registry imports."""
    shim_content = '''"""Compatibility shim for MCP Registry migration."""

import warnings
from infrastructure.mcp_servers.registry_v2 import (
    RegistryV2,
    get_registry,
    MCPServer,
    Tier,
    ServerStatus
)

warnings.warn(
    "MCPRegistry is deprecated. Please use RegistryV2 from registry_v2.py",
    DeprecationWarning,
    stacklevel=2
)


class MCPRegistry:
    """Compatibility wrapper for old MCPRegistry."""

    def __init__(self):
        self._v2_registry = get_registry()
        self._configs = {}

        # Build old-style configs
        for name, server in self._v2_registry._servers.items():
            self._configs[name] = type('MCPServerConfig', (), {
                'name': server.name,
                'port': server.port,
                'type': server.type,
                'enabled': server.status != ServerStatus.UNHEALTHY,
                'health_endpoint': server.health_endpoint,
                'capabilities': list(server.capabilities)
            })()

    def get_server_config(self, name: str):
        """Get server config (compatibility method)."""
        return self._configs.get(name)

    def get_all_configs(self):
        """Get all configs (compatibility method)."""
        return self._configs

    def get_servers_by_capability(self, capability: str):
        """Get servers by capability (compatibility method)."""
        servers = self._v2_registry.get_servers_by_capability(capability)
        return [self._configs[s.name] for s in servers if s.name in self._configs]


# Re-export v2 classes for easier migration
__all__ = ['MCPRegistry', 'RegistryV2', 'get_registry', 'MCPServer', 'Tier']
'''

    # Write shim to temporary location
    shim_path = Path("infrastructure/mcp_servers/mcp_registry_compat.py")
    shim_path.write_text(shim_content)
    print(f"  ✅ Created compatibility shim at {shim_path}")


if __name__ == "__main__":
    migrate_to_yaml()
