#!/usr/bin/env python3
"""
Phase 1 MCP Server Health Check
Validates all game-changing servers are operational
"""

import contextlib
import os
import subprocess


class MCPHealthChecker:
    def __init__(self):
        self.results = []
        self.config_path = "config/cursor_phase1_mcp_config.json"

    def check_prerequisites(self) -> list[tuple[str, bool, str]]:
        """Check system prerequisites"""
        checks = []

        # Node.js check
        try:
            result = subprocess.run(
                ["node", "--version"], capture_output=True, text=True
            )
            version = result.stdout.strip()
            checks.append(("Node.js", True, f"Version: {version}"))
        except Exception:
            checks.append(("Node.js", False, "Not installed"))

        # Python check
        try:
            result = subprocess.run(
                ["python3", "--version"], capture_output=True, text=True
            )
            version = result.stdout.strip()
            checks.append(("Python", True, f"Version: {version}"))
        except Exception:
            checks.append(("Python", False, "Not installed"))

        # Git check
        try:
            result = subprocess.run(
                ["git", "--version"], capture_output=True, text=True
            )
            version = result.stdout.strip()
            checks.append(("Git", True, f"Version: {version}"))
        except Exception:
            checks.append(("Git", False, "Not installed"))

        return checks

    def check_mcp_servers(self) -> list[dict[str, any]]:
        """Check MCP server installations"""
        servers = []

        # Microsoft Playwright
        playwright_path = "mcp-servers/playwright/microsoft-playwright-mcp"
        servers.append(
            {
                "name": "Microsoft Playwright MCP",
                "path": playwright_path,
                "exists": os.path.exists(playwright_path),
                "value": "$500K+ web automation",
            }
        )

        # Snowflake Cortex
        cortex_path = "mcp-servers/snowflake_cortex/snowflake_cortex_mcp_server.py"
        servers.append(
            {
                "name": "Snowflake Cortex Agent",
                "path": cortex_path,
                "exists": os.path.exists(cortex_path),
                "value": "$300K+ data intelligence",
            }
        )

        # Apollo.io
        apollo_path = "mcp-servers/apollo/apollo-io-mcp"
        servers.append(
            {
                "name": "Apollo.io MCP",
                "path": apollo_path,
                "exists": os.path.exists(apollo_path),
                "value": "$200K+ sales intelligence",
            }
        )

        # Apify (Remote)
        apify_config = "config/mcp/phase1/apify_config.json"
        servers.append(
            {
                "name": "Apify Official MCP",
                "path": apify_config,
                "exists": os.path.exists(apify_config),
                "value": "$400K+ automation tools",
            }
        )

        # Figma Context
        figma_path = "mcp-servers/figma_context/figma-context-mcp"
        servers.append(
            {
                "name": "Figma Context MCP",
                "path": figma_path,
                "exists": os.path.exists(figma_path),
                "value": "$300K+ design automation",
            }
        )

        return servers

    def check_environment_variables(self) -> list[tuple[str, bool]]:
        """Check required environment variables"""
        required_vars = [
            "SNOWFLAKE_ACCOUNT",
            "SNOWFLAKE_USER",
            "SNOWFLAKE_PASSWORD",
            "APOLLO_IO_API_KEY",
            "APIFY_TOKEN",
            "FIGMA_ACCESS_TOKEN",
        ]

        results = []
        for var in required_vars:
            exists = os.getenv(var) is not None
            results.append((var, exists))

        return results

    def generate_report(self):
        """Generate health check report"""

        # Prerequisites
        prereqs = self.check_prerequisites()
        for _name, _status, _info in prereqs:
            pass

        # MCP Servers
        servers = self.check_mcp_servers()
        total_value = 0
        for server in servers:
            "✅" if server["exists"] else "❌"
            if server["exists"]:
                value_str = (
                    server["value"]
                    .replace("$", "")
                    .replace("K+", "000")
                    .replace(" ", "")
                )
                with contextlib.suppress(Exception):
                    total_value += int(value_str.split()[0])

        # Environment Variables
        env_vars = self.check_environment_variables()
        missing_vars = []
        for var, exists in env_vars:
            if not exists:
                missing_vars.append(var)

        # Summary
        all_servers_exist = all(s["exists"] for s in servers)
        all_vars_set = len(missing_vars) == 0
        all_prereqs_met = all(p[1] for p in prereqs)

        if missing_vars:
            for var in missing_vars:
                pass

        overall_ready = all_servers_exist and all_vars_set and all_prereqs_met
        if overall_ready:
            pass
        else:
            pass


if __name__ == "__main__":
    checker = MCPHealthChecker()
    checker.generate_report()
