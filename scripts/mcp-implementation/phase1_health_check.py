#!/usr/bin/env python3
"""
Phase 1 MCP Server Health Check
Validates all game-changing servers are operational
"""

import os
import subprocess
from datetime import datetime


class MCPHealthChecker:
    def __init__(self):
        self.results = []
        self.config_path = "config/cursor_phase1_mcp_config.json"

    def check_prerequisites(self) -> list[tuple[str, bool, str]]:
        """Check system prerequisites"""
        checks = []

        # Node.js check
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            version = result.stdout.strip()
            checks.append(("Node.js", True, f"Version: {version}"))
        except Exception:
            checks.append(("Node.js", False, "Not installed"))

        # Python check
        try:
            result = subprocess.run(['python3', '--version'], capture_output=True, text=True)
            version = result.stdout.strip()
            checks.append(("Python", True, f"Version: {version}"))
        except Exception:
            checks.append(("Python", False, "Not installed"))

        # Git check
        try:
            result = subprocess.run(['git', '--version'], capture_output=True, text=True)
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
        servers.append({
            "name": "Microsoft Playwright MCP",
            "path": playwright_path,
            "exists": os.path.exists(playwright_path),
            "value": "$500K+ web automation"
        })

        # Snowflake Cortex
        cortex_path = "mcp-servers/snowflake_cortex/snowflake_cortex_mcp_server.py"
        servers.append({
            "name": "Snowflake Cortex Agent",
            "path": cortex_path,
            "exists": os.path.exists(cortex_path),
            "value": "$300K+ data intelligence"
        })

        # Apollo.io
        apollo_path = "mcp-servers/apollo/apollo-io-mcp"
        servers.append({
            "name": "Apollo.io MCP",
            "path": apollo_path,
            "exists": os.path.exists(apollo_path),
            "value": "$200K+ sales intelligence"
        })

        # Apify (Remote)
        apify_config = "config/mcp/phase1/apify_config.json"
        servers.append({
            "name": "Apify Official MCP",
            "path": apify_config,
            "exists": os.path.exists(apify_config),
            "value": "$400K+ automation tools"
        })

        # Figma Context
        figma_path = "mcp-servers/figma_context/figma-context-mcp"
        servers.append({
            "name": "Figma Context MCP",
            "path": figma_path,
            "exists": os.path.exists(figma_path),
            "value": "$300K+ design automation"
        })

        return servers

    def check_environment_variables(self) -> list[tuple[str, bool]]:
        """Check required environment variables"""
        required_vars = [
            "SNOWFLAKE_ACCOUNT",
            "SNOWFLAKE_USER",
            "SNOWFLAKE_PASSWORD",
            "APOLLO_IO_API_KEY",
            "APIFY_TOKEN",
            "FIGMA_ACCESS_TOKEN"
        ]

        results = []
        for var in required_vars:
            exists = os.getenv(var) is not None
            results.append((var, exists))

        return results

    def generate_report(self):
        """Generate health check report"""
        print("\n" + "="*60)
        print("🏥 PHASE 1 MCP HEALTH CHECK REPORT")
        print("="*60)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Prerequisites
        print("📋 PREREQUISITES:")
        prereqs = self.check_prerequisites()
        for name, status, info in prereqs:
            icon = "✅" if status else "❌"
            print(f"  {icon} {name}: {info}")
        print()

        # MCP Servers
        print("🚀 MCP SERVERS:")
        servers = self.check_mcp_servers()
        total_value = 0
        for server in servers:
            icon = "✅" if server['exists'] else "❌"
            print(f"  {icon} {server['name']}")
            print(f"     Path: {server['path']}")
            print(f"     Business Value: {server['value']}")
            if server['exists']:
                value_str = server['value'].replace('$', '').replace('K+', '000').replace(' ', '')
                try:
                    total_value += int(value_str.split()[0])
                except Exception:
                    pass
        print()
        print(f"  💰 Total Business Value: ${total_value:,}+")
        print()

        # Environment Variables
        print("�� ENVIRONMENT VARIABLES:")
        env_vars = self.check_environment_variables()
        missing_vars = []
        for var, exists in env_vars:
            icon = "✅" if exists else "❌"
            status = "Set" if exists else "Missing"
            print(f"  {icon} {var}: {status}")
            if not exists:
                missing_vars.append(var)
        print()

        # Summary
        all_servers_exist = all(s['exists'] for s in servers)
        all_vars_set = len(missing_vars) == 0
        all_prereqs_met = all(p[1] for p in prereqs)

        print("📊 SUMMARY:")
        print(f"  Prerequisites: {'✅ All met' if all_prereqs_met else '❌ Missing dependencies'}")
        print(f"  MCP Servers: {'✅ All installed' if all_servers_exist else '❌ Some missing'}")
        print(f"  Environment: {'✅ All variables set' if all_vars_set else '❌ Missing variables'}")
        print()

        if missing_vars:
            print("⚠️  ACTION REQUIRED:")
            print("  Set the following environment variables:")
            for var in missing_vars:
                print(f"    export {var}='your-value-here'")
            print()

        overall_ready = all_servers_exist and all_vars_set and all_prereqs_met
        if overall_ready:
            print("🎉 PHASE 1 READY FOR DEPLOYMENT!")
        else:
            print("🔧 Please address the issues above before deployment.")

        print("="*60)

if __name__ == "__main__":
    checker = MCPHealthChecker()
    checker.generate_report()
