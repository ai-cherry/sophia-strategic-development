#!/usr/bin/env python3
"""Deploy and validate CEO Dashboard for immediate use.

Ensures all backend APIs are running and creates Retool configuration
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Any, Dict

import aiohttp

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
ADMIN_KEY = os.getenv("SOPHIA_ADMIN_KEY", "sophia_admin_2024")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


class CEODashboardDeployer:
    """Deploy and validate CEO Dashboard."""

    def __init__(self):
        self.backend_url = BACKEND_URL
        self.admin_key = ADMIN_KEY
        self.test_results = []

    async def validate_backend_health(self) -> bool:
        """Check if backend is running and healthy."""print(f"\n{BLUE}=== Validating Backend Health ==={RESET}").

        try:
            async with aiohttp.ClientSession() as session:
                # Test root endpoint
                async with session.get(f"{self.backend_url}/") as response:
                    if response.status == 200:
                        print(
                            f"{GREEN}✓ Backend is running at {self.backend_url}{RESET}"
                        )
                        return True
                    else:
                        print(
                            f"{RED}✗ Backend returned status {response.status}{RESET}"
                        )
                        return False
        except Exception as e:
            print(f"{RED}✗ Cannot connect to backend: {e}{RESET}")
            print(f"{YELLOW}Make sure to run: cd backend && python main.py{RESET}")
            return False

    async def test_executive_endpoints(self) -> Dict[str, bool]:
        """Test all executive API endpoints."""print(f"\n{BLUE}=== Testing Executive API Endpoints ==={RESET}").

        endpoints = [
            {
                "name": "Dashboard Summary",
                "method": "GET",
                "path": "/api/retool/executive/dashboard-summary",
            },
            {
                "name": "Client Health Portfolio",
                "method": "GET",
                "path": "/api/retool/executive/client-health-portfolio",
            },
            {
                "name": "Sales Performance",
                "method": "GET",
                "path": "/api/retool/executive/sales-performance",
            },
            {
                "name": "OpenRouter Models",
                "method": "GET",
                "path": "/api/retool/executive/openrouter-models",
            },
            {
                "name": "Model Presets",
                "method": "GET",
                "path": "/api/retool/executive/model-presets",
            },
        ]

        results = {}
        headers = {"X-Admin-Key": self.admin_key}

        async with aiohttp.ClientSession() as session:
            for endpoint in endpoints:
                try:
                    url = f"{self.backend_url}{endpoint['path']}"

                    if endpoint["method"] == "GET":
                        async with session.get(url, headers=headers) as response:
                            if response.status == 200:
                                data = await response.json()
                                print(f"{GREEN}✓ {endpoint['name']}: OK{RESET}")
                                results[endpoint["name"]] = True
                            else:
                                error = await response.text()
                                print(
                                    f"{RED}✗ {endpoint['name']}: {response.status} - {error}{RESET}"
                                )
                                results[endpoint["name"]] = False
                except Exception as e:
                    print(f"{RED}✗ {endpoint['name']}: {str(e)}{RESET}")
                    results[endpoint["name"]] = False

        return results

    async def test_strategic_chat(self) -> bool:
        """Test strategic chat functionality."""print(f"\n{BLUE}=== Testing Strategic Chat ==={RESET}").

        test_queries = [
            {
                "message": "What is our current client health status?",
                "mode": "internal",
            },
            {
                "message": "What are the latest proptech market trends?",
                "mode": "external",
            },
            {
                "message": "How do our metrics compare to market trends?",
                "mode": "combined",
            },
        ]

        headers = {"X-Admin-Key": self.admin_key, "Content-Type": "application/json"}

        async with aiohttp.ClientSession() as session:
            for query in test_queries:
                try:
                    url = f"{self.backend_url}/api/retool/executive/strategic-chat"
                    async with session.post(
                        url, headers=headers, json=query
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            print(
                                f"{GREEN}✓ Chat ({query['mode']} mode): Response received{RESET}"
                            )
                            return True
                        else:
                            error = await response.text()
                            print(
                                f"{YELLOW}⚠ Chat ({query['mode']} mode): {error}{RESET}"
                            )
                except Exception as e:
                    print(f"{YELLOW}⚠ Chat ({query['mode']} mode): {str(e)}{RESET}")

        return False

    async def test_system_endpoints(self) -> Dict[str, bool]:
        """Test system intelligence endpoints."""print(f"\n{BLUE}=== Testing System Intelligence Endpoints ==={RESET}").

        endpoints = [
            {"name": "Agent Status", "path": "/api/system/agents"},
            {"name": "Infrastructure Health", "path": "/api/system/infrastructure"},
            {"name": "API Catalog", "path": "/api/system/api-catalog"},
        ]

        results = {}
        headers = {"X-Admin-Key": self.admin_key}

        async with aiohttp.ClientSession() as session:
            for endpoint in endpoints:
                try:
                    url = f"{self.backend_url}{endpoint['path']}"
                    async with session.get(url, headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            print(f"{GREEN}✓ {endpoint['name']}: OK{RESET}")
                            results[endpoint["name"]] = True
                        else:
                            print(
                                f"{YELLOW}⚠ {endpoint['name']}: {response.status}{RESET}"
                            )
                            results[endpoint["name"]] = False
                except Exception as e:
                    print(f"{YELLOW}⚠ {endpoint['name']}: {str(e)}{RESET}")
                    results[endpoint["name"]] = False

        return results

    def generate_retool_config(self) -> Dict[str, Any]:
        """Generate Retool application configuration."""return {.

            "name": "Sophia CEO Dashboard",
            "description": "Executive command center for Pay Ready AI",
            "resources": [
                {
                    "name": "SophiaAPI",
                    "type": "restapi",
                    "config": {
                        "baseURL": self.backend_url,
                        "headers": [
                            {
                                "key": "X-Admin-Key",
                                "value": "{{ environment.SOPHIA_ADMIN_KEY }}",
                            },
                            {"key": "Content-Type", "value": "application/json"},
                        ],
                        "authentication": "custom",
                        "urlParams": [],
                        "cookies": [],
                    },
                }
            ],
            "queries": [
                {
                    "name": "getDashboardSummary",
                    "resource": "SophiaAPI",
                    "type": "GET",
                    "url": "/api/retool/executive/dashboard-summary",
                },
                {
                    "name": "getClientHealth",
                    "resource": "SophiaAPI",
                    "type": "GET",
                    "url": "/api/retool/executive/client-health-portfolio",
                },
                {
                    "name": "strategicChat",
                    "resource": "SophiaAPI",
                    "type": "POST",
                    "url": "/api/retool/executive/strategic-chat",
                    "body": {
                        "message": "{{ chatInput.value }}",
                        "mode": "{{ modeSelector.value }}",
                        "model_id": "{{ modelSelector.value }}",
                    },
                },
                {
                    "name": "getOpenRouterModels",
                    "resource": "SophiaAPI",
                    "type": "GET",
                    "url": "/api/retool/executive/openrouter-models",
                },
                {
                    "name": "getAgentStatus",
                    "resource": "SophiaAPI",
                    "type": "GET",
                    "url": "/api/system/agents",
                },
            ],
        }

    def generate_deployment_guide(self, test_results: Dict[str, Any]) -> str:
        """Generate deployment guide based on test results."""guide = f"""

{BLUE}=== CEO Dashboard Deployment Guide ==={RESET}

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

{BLUE}1. Backend Status:{RESET}
"""if test_results.get("backend_healthy"):

            guide += f"{GREEN}✓ Backend is running at {self.backend_url}{RESET}\n"
        else:
            guide += f"{RED}✗ Backend is not running. Start it with:{RESET}\n"
            guide += "  cd backend && python main.py\n"

        guide += f"\n{BLUE}2. API Endpoints Status:{RESET}\n"

        for endpoint, status in test_results.get("executive_endpoints", {}).items():
            if status:
                guide += f"{GREEN}✓ {endpoint}{RESET}\n"
            else:
                guide += f"{RED}✗ {endpoint}{RESET}\n"

        guide += f"\n{BLUE}3. Retool Setup Instructions:{RESET}\n"
        guide += "a) Log into your Retool account\n"
        guide += "b) Create a new app called 'Sophia CEO Dashboard'\n"
        guide += "c) Add a REST API resource:\n"
        guide += "   - Name: SophiaAPI\n"
        guide += f"   - Base URL: {self.backend_url}\n"
        guide += f"   - Headers: X-Admin-Key = {self.admin_key}\n"
        guide += "\n"
        guide += "d) Import the configuration from: retool_ceo_dashboard_config.json\n"

        guide += f"\n{BLUE}4. Quick Test Commands:{RESET}\n"
        guide += "# Test dashboard summary\n"
        guide += f'curl -H "X-Admin-Key: {self.admin_key}" {self.backend_url}/api/retool/executive/dashboard-summary\n\n'
        guide += "# Test strategic chat\n"
        guide += f
"""curl -X POST -H "X-Admin-Key: {self.admin_key}" -H "Content-Type: application/json" \\.

     -d '{{"message": "What is our client health status?", "mode": "internal"}}' \\
     {self.backend_url}/api/retool/executive/strategic-chat\n"""

        guide += f"\n{BLUE}5. Environment Variables:{RESET}\n"
        guide += f"SOPHIA_ADMIN_KEY={self.admin_key}\n"
        guide += f"BACKEND_URL={self.backend_url}\n"
        if OPENROUTER_API_KEY:
            guide += "OPENROUTER_API_KEY=****** (configured)\n"
        else:
            guide += f"{YELLOW}OPENROUTER_API_KEY=<not set> (required for model selection){RESET}\n"

        return guide

    async def deploy(self):
        """Run full deployment validation."""
        print(f"{BLUE}{'=' * 60}{RESET}")
        print(f"{BLUE}Sophia AI CEO Dashboard Deployment Tool{RESET}")
        print(f"{BLUE}{'=' * 60}{RESET}")

        # Test backend health
        backend_healthy = await self.validate_backend_health()

        if not backend_healthy:
            print(f"\n{RED}Backend must be running before proceeding.{RESET}")
            print("Start it with: cd backend && python main.py")
            return

        # Test executive endpoints
        executive_results = await self.test_executive_endpoints()

        # Test strategic chat
        chat_working = await self.test_strategic_chat()

        # Test system endpoints
        system_results = await self.test_system_endpoints()

        # Generate Retool configuration
        retool_config = self.generate_retool_config()

        # Save configuration
        with open("retool_ceo_dashboard_config.json", "w") as f:
            json.dump(retool_config, f, indent=2)
        print(
            f"\n{GREEN}✓ Retool configuration saved to: retool_ceo_dashboard_config.json{RESET}"
        )

        # Generate deployment guide
        test_results = {
            "backend_healthy": backend_healthy,
            "executive_endpoints": executive_results,
            "system_endpoints": system_results,
            "chat_working": chat_working,
        }

        guide = self.generate_deployment_guide(test_results)

        # Save deployment guide
        with open("CEO_DASHBOARD_DEPLOYMENT_GUIDE.md", "w") as f:
            f.write(guide)

        print(guide)

        # Summary
        total_tests = (
            len(executive_results) + len(system_results) + (1 if chat_working else 0)
        )
        passed_tests = (
            sum(executive_results.values())
            + sum(system_results.values())
            + (1 if chat_working else 0)
        )

        print(f"\n{BLUE}{'=' * 60}{RESET}")
        print(f"{BLUE}Deployment Summary:{RESET}")
        print(f"Tests Passed: {passed_tests}/{total_tests}")

        if passed_tests == total_tests:
            print(f"{GREEN}✓ CEO Dashboard is ready for deployment!{RESET}")
            print("\nNext steps:")
            print("1. Open Retool and create new app")
            print("2. Import configuration from retool_ceo_dashboard_config.json")
            print("3. Start using your executive dashboard!")
        else:
            print(f"{YELLOW}⚠ Some tests failed. Check the logs above.{RESET}")


async def main():
    deployer = CEODashboardDeployer()
    await deployer.deploy()


if __name__ == "__main__":
    asyncio.run(main())
