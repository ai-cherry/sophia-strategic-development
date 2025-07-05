#!/usr/bin/env python3
"""
Fix MCP server paths and configuration
"""

import json
import logging
import os
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MCPPathFixer:
    """Fix MCP server paths and configuration"""

    def __init__(self):
        self.server_locations = {}
        self.fixed_config = {}

    def find_all_servers(self):
        """Find all MCP server files"""
        logger.info("🔍 Finding all MCP server files...")

        # Search patterns
        patterns = ["*_mcp_server.py", "*_server.py", "server.py", "main.py"]

        # Search locations
        search_dirs = [Path("backend/mcp_servers"), Path("mcp-servers")]

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue

            # Search each subdirectory
            for subdir in search_dir.iterdir():
                if subdir.is_dir():
                    server_name = subdir.name

                    # Look for server files
                    for pattern in patterns:
                        files = list(subdir.glob(pattern))
                        if files:
                            # Take the first matching file
                            server_file = files[0]

                            # Handle relative path
                            try:
                                relative_path = str(server_file.relative_to(Path.cwd()))
                            except ValueError:
                                # If relative_to fails, construct path manually
                                relative_path = str(server_file)

                            self.server_locations[server_name] = {
                                "path": str(server_file),
                                "dir": str(subdir),
                                "relative_path": relative_path,
                            }
                            logger.info(f"  Found {server_name}: {server_file}")
                            break

    def fix_configuration(self):
        """Fix the configuration files"""
        logger.info("\n🔧 Fixing configuration...")

        # Load existing configs
        configs_to_fix = [
            "config/unified_mcp_config.json",
            "config/cursor_enhanced_mcp_config.json",
        ]

        for config_path in configs_to_fix:
            if not Path(config_path).exists():
                continue

            logger.info(f"\nFixing {config_path}...")

            with open(config_path) as f:
                config = json.load(f)

            # Fix server configurations
            servers = config.get("mcpServers", {})
            fixed_servers = {}

            for server_name, server_config in servers.items():
                # Check if we found this server
                if server_name in self.server_locations:
                    location = self.server_locations[server_name]

                    # Determine the correct command based on location
                    if location["dir"].startswith("mcp-servers"):
                        # For mcp-servers directory, run directly
                        fixed_config = {
                            "command": "python",
                            "args": [location["relative_path"]],
                            "env": server_config.get("env", {}),
                            "port": server_config.get("port", 9000),
                            "cwd": ".",
                        }
                    else:
                        # For backend directory, use module syntax
                        module_path = (
                            location["relative_path"]
                            .replace("/", ".")
                            .replace(".py", "")
                        )
                        fixed_config = {
                            "command": "python",
                            "args": [
                                "-m",
                                "uvicorn",
                                f"{module_path}:app",
                                "--host",
                                "0.0.0.0",
                                "--port",
                                str(server_config.get("port", 9000)),
                            ],
                            "env": server_config.get("env", {}),
                            "port": server_config.get("port", 9000),
                            "cwd": ".",
                        }

                    # Preserve other settings
                    fixed_config["capabilities"] = server_config.get("capabilities", [])
                    fixed_config["health_endpoint"] = server_config.get(
                        "health_endpoint", "/health"
                    )

                    fixed_servers[server_name] = fixed_config
                    logger.info(f"  ✅ Fixed {server_name}")
                else:
                    # Server not found, keep original config but log warning
                    fixed_servers[server_name] = server_config
                    logger.warning(f"  ⚠️  {server_name} not found in filesystem")

            # Update config
            config["mcpServers"] = fixed_servers

            # Save fixed config
            backup_path = config_path + ".backup"
            if Path(config_path).exists():
                os.rename(config_path, backup_path)

            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)

            logger.info(f"  ✅ Saved fixed config (backup: {backup_path})")

    def create_missing_init_files(self):
        """Create missing __init__.py files"""
        logger.info("\n📝 Creating missing __init__.py files...")

        dirs_to_check = [
            "backend/mcp_servers",
            "backend/mcp_servers/base",
            "backend/mcp_servers/ai_memory",
            "backend/mcp_servers/codacy",
            "mcp-servers",
        ]

        for dir_path in dirs_to_check:
            path = Path(dir_path)
            if path.exists() and path.is_dir():
                init_file = path / "__init__.py"
                if not init_file.exists():
                    init_file.write_text("")
                    logger.info(f"  ✅ Created {init_file}")

    def generate_server_status_report(self):
        """Generate a report of server status"""
        logger.info("\n📊 Server Status Report")
        logger.info("=" * 60)

        # Group by location
        backend_servers = []
        mcp_servers = []

        for name, location in self.server_locations.items():
            if location["dir"].startswith("backend"):
                backend_servers.append(name)
            else:
                mcp_servers.append(name)

        logger.info(f"\n📁 Backend MCP Servers ({len(backend_servers)}):")
        for server in sorted(backend_servers):
            logger.info(f"  - {server}")

        logger.info(f"\n📁 MCP-Servers Directory ({len(mcp_servers)}):")
        for server in sorted(mcp_servers):
            logger.info(f"  - {server}")

        # Save detailed mapping
        with open("mcp_server_mapping.json", "w") as f:
            json.dump(self.server_locations, f, indent=2)

        logger.info("\n📄 Detailed mapping saved to mcp_server_mapping.json")

    def run(self):
        """Run all fixes"""
        logger.info("🚀 Starting MCP Path and Configuration Fix")

        # Find all servers
        self.find_all_servers()

        # Fix configurations
        self.fix_configuration()

        # Create missing init files
        self.create_missing_init_files()

        # Generate report
        self.generate_server_status_report()

        logger.info("\n✅ Fix complete!")


def main():
    fixer = MCPPathFixer()
    fixer.run()


if __name__ == "__main__":
    main()
