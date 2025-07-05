#!/usr/bin/env python3
"""
Fix MCP Configuration Issues
Consolidates configuration files and removes phantom servers
"""

import json
import logging
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPConfigurationFixer:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.config_dir = self.project_root / "config"

        # Master configuration source
        self.unified_ports_file = self.config_dir / "unified_mcp_ports.json"

        # Files to update
        self.cursor_config_file = self.config_dir / "cursor_enhanced_mcp_config.json"
        self.consolidated_ports_file = self.config_dir / "consolidated_mcp_ports.json"

    def load_unified_ports(self) -> dict[str, Any]:
        """Load the master port configuration"""
        with open(self.unified_ports_file) as f:
            return json.load(f)

    def fix_cursor_config(self):
        """Fix cursor MCP configuration"""
        logger.info("Fixing cursor MCP configuration...")

        # Load master configuration
        unified_config = self.load_unified_ports()
        active_servers = unified_config.get("active_servers", {})

        # Load current cursor config
        with open(self.cursor_config_file) as f:
            cursor_config = json.load(f)

        # Define valid servers based on unified config
        valid_servers = {
            "ai_memory": {
                "command": "uvicorn",
                "args": [
                    "backend.mcp_servers.enhanced_ai_memory_mcp_server:app",
                    "--host",
                    "0.0.0.0",
                    "--port",
                    str(active_servers.get("ai_memory", 9000)),
                ],
                "env": {
                    "ENVIRONMENT": "prod",
                    "PULUMI_ORG": "scoobyjava-org",
                    "LAMBDA_LABS_HOST": "165.1.69.44",
                },
            },
            "snowflake_unified": {
                "command": "python",
                "args": ["mcp-servers/snowflake_unified/unified_snowflake_server.py"],
                "env": {
                    "PORT": str(active_servers.get("snowflake", 9200)),
                    "ENVIRONMENT": "prod",
                    "LAMBDA_LABS_HOST": "165.1.69.44",
                },
            },
            "codacy": {
                "command": "uvicorn",
                "args": [
                    "backend.mcp_servers.codacy.codacy_mcp_server:app",
                    "--host",
                    "0.0.0.0",
                    "--port",
                    str(active_servers.get("codacy", 9003)),
                ],
                "env": {"ENVIRONMENT": "prod", "LAMBDA_LABS_HOST": "165.1.69.44"},
            },
            "ui_ux_agent": {
                "command": "python",
                "args": ["mcp-servers/ui_ux_agent/ui_ux_agent_mcp_server.py"],
                "env": {
                    "PORT": str(active_servers.get("ui_ux_agent", 9002)),
                    "ENVIRONMENT": "prod",
                    "LAMBDA_LABS_HOST": "165.1.69.44",
                },
            },
            "portkey_admin": {
                "command": "python",
                "args": ["mcp-servers/portkey_admin/portkey_admin_mcp_server.py"],
                "env": {
                    "PORT": str(active_servers.get("portkey_admin", 9013)),
                    "ENVIRONMENT": "prod",
                    "LAMBDA_LABS_HOST": "165.1.69.44",
                },
            },
            "lambda_labs_cli": {
                "command": "python",
                "args": ["mcp-servers/lambda_labs_cli/lambda_labs_cli_mcp_server.py"],
                "env": {
                    "PORT": str(active_servers.get("lambda_labs_cli", 9020)),
                    "ENVIRONMENT": "prod",
                    "LAMBDA_LABS_HOST": "165.1.69.44",
                },
            },
        }

        # Update cursor config with valid servers only
        cursor_config["mcpServers"] = valid_servers
        cursor_config["version"] = "5.0-unified"
        cursor_config[
            "description"
        ] = "Unified MCP Configuration with Lambda Labs Integration"
        cursor_config["lambda_labs"] = {
            "host": "165.1.69.44",
            "monitoring_enabled": True,
            "health_check_interval": 30,
        }

        # Save updated config
        with open(self.cursor_config_file, "w") as f:
            json.dump(cursor_config, f, indent=2)

        logger.info(f"✅ Fixed cursor config with {len(valid_servers)} valid servers")

    def create_consolidated_ports(self):
        """Create consolidated ports configuration"""
        logger.info("Creating consolidated ports configuration...")

        # Load master configuration
        unified_config = self.load_unified_ports()

        # Create consolidated configuration
        consolidated = {
            "version": unified_config.get("version", "4.0"),
            "description": "Consolidated MCP Server Port Configuration",
            "last_updated": unified_config.get("last_updated"),
            "active_servers": unified_config.get("active_servers", {}),
            "lambda_labs": {
                "host": "165.1.69.44",
                "gateway_port": 8080,
                "monitoring_port": 9090,
            },
            "server_groups": {
                "core_intelligence": list(range(9000, 9020)),
                "strategic_enhancements": list(range(9020, 9030)),
                "business_intelligence": list(range(9100, 9120)),
                "data_integrations": list(range(9200, 9220)),
                "development_tools": list(range(9300, 9320)),
            },
        }

        # Save consolidated config
        with open(self.consolidated_ports_file, "w") as f:
            json.dump(consolidated, f, indent=2)

        logger.info("✅ Created consolidated ports configuration")

    def create_lambda_labs_config(self):
        """Create Lambda Labs specific configuration"""
        logger.info("Creating Lambda Labs configuration...")

        lambda_config = {
            "version": "1.0",
            "description": "Lambda Labs MCP Server Configuration",
            "host": "165.1.69.44",
            "services": {
                "mcp_gateway": {
                    "port": 8080,
                    "replicas": 3,
                    "health_check": "/health",
                    "load_balancer": True,
                },
                "monitoring": {
                    "prometheus_port": 9090,
                    "grafana_port": 3000,
                    "metrics_retention": "30d",
                },
                "servers": {
                    "ai_memory": {"port": 9000, "gpu_enabled": True, "memory": "16Gi"},
                    "snowflake": {"port": 9200, "gpu_enabled": False, "memory": "8Gi"},
                    "codacy": {"port": 9003, "gpu_enabled": False, "memory": "4Gi"},
                },
            },
        }

        lambda_config_file = self.config_dir / "lambda_labs_mcp_config.json"
        with open(lambda_config_file, "w") as f:
            json.dump(lambda_config, f, indent=2)

        logger.info("✅ Created Lambda Labs configuration")

    def verify_server_files(self):
        """Verify that referenced server files exist"""
        logger.info("Verifying server files...")

        with open(self.cursor_config_file) as f:
            cursor_config = json.load(f)

        missing_files = []
        for server_name, server_config in cursor_config.get("mcpServers", {}).items():
            if "command" in server_config and "args" in server_config:
                # Extract file path from args
                for arg in server_config["args"]:
                    if arg.endswith(".py"):
                        file_path = self.project_root / arg
                        if not file_path.exists():
                            missing_files.append((server_name, arg))
                            logger.warning(f"❌ Missing file for {server_name}: {arg}")
                        else:
                            logger.info(f"✅ Found file for {server_name}: {arg}")

        return missing_files

    def run(self):
        """Run all configuration fixes"""
        logger.info("Starting MCP configuration fixes...")

        # Fix configurations
        self.fix_cursor_config()
        self.create_consolidated_ports()
        self.create_lambda_labs_config()

        # Verify files
        missing_files = self.verify_server_files()

        if missing_files:
            logger.warning(f"\n⚠️  Found {len(missing_files)} missing server files:")
            for server, file in missing_files:
                logger.warning(f"   - {server}: {file}")
        else:
            logger.info("\n✅ All server files verified!")

        logger.info("\n🎉 Configuration fixes complete!")
        logger.info("   - Fixed cursor MCP configuration")
        logger.info("   - Created consolidated ports configuration")
        logger.info("   - Created Lambda Labs configuration")
        logger.info("   - All servers now configured for Lambda Labs (165.1.69.44)")


if __name__ == "__main__":
    fixer = MCPConfigurationFixer()
    fixer.run()
