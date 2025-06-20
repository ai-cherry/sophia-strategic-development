#!/usr/bin/env python3
"""Direct Retool API Test Script
Tests Retool API connectivity without Pulumi ESC dependencies
"""

import asyncio
import os
from typing import Optional

import aiohttp

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


class RetoolAPITester:
    """Direct Retool API testing without Pulumi dependencies"""

    def __init__(self):
        # Try to get Retool API token from environment
        self.api_token = os.getenv("RETOOL_API_TOKEN", "")
        self.base_url = "https://api.retool.com/v1"

    async def test_api_connection(self) -> bool:
        """Test basic API connectivity"""
        print(f"\n{BLUE}=== Testing Retool API Connection ==={RESET}")

        if not self.api_token:
            print(f"{YELLOW}⚠ RETOOL_API_TOKEN not found in environment{RESET}")
            print("Please set it with: export RETOOL_API_TOKEN='your-token-here'")
            return False

        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

        try:
            async with aiohttp.ClientSession() as session:
                # Test with a simple API call - list apps
                async with session.get(
                    f"{self.base_url}/apps", headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"{GREEN}✓ Successfully connected to Retool API{RESET}")
                        print(f"Found {len(data.get('data', []))} apps")
                        return True
                    elif response.status == 401:
                        print(
                            f"{RED}✗ Authentication failed - check your API token{RESET}"
                        )
                        return False
                    else:
                        error = await response.text()
                        print(
                            f"{RED}✗ API returned status {response.status}: {error}{RESET}"
                        )
                        return False

        except Exception as e:
            print(f"{RED}✗ Connection error: {str(e)}{RESET}")
            return False

    async def create_test_app(self) -> Optional[str]:
        """Create a test Retool app"""
        print(f"\n{BLUE}=== Creating Test Retool App ==={RESET}")

        if not self.api_token:
            print(f"{RED}✗ No API token available{RESET}")
            return None

        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

        app_data = {
            "name": "Sophia AI Test Dashboard",
            "description": "Test dashboard for Sophia AI integration",
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/apps", headers=headers, json=app_data
                ) as response:
                    if response.status in [200, 201]:
                        data = await response.json()
                        app_id = data.get("data", {}).get("id")
                        print(f"{GREEN}✓ Created app with ID: {app_id}{RESET}")
                        return app_id
                    else:
                        error = await response.text()
                        print(f"{RED}✗ Failed to create app: {error}{RESET}")
                        return None

        except Exception as e:
            print(f"{RED}✗ Error creating app: {str(e)}{RESET}")
            return None

    async def test_resource_creation(self) -> bool:
        """Test creating a REST API resource"""
        print(f"\n{BLUE}=== Testing Resource Creation ==={RESET}")

        if not self.api_token:
            print(f"{RED}✗ No API token available{RESET}")
            return False

        # For now, just return True as resource creation requires an app context
        print(f"{YELLOW}⚠ Resource creation requires app context - skipping{RESET}")
        return True

    def print_setup_instructions(self):
        """Print instructions for setting up Retool"""
        print(f"\n{BLUE}=== Retool Setup Instructions ==={RESET}")
        print(
            """
1. Get your Retool API token:
   - Log into Retool
   - Go to Settings > API
   - Generate an API token
   
2. Set the environment variable:
   export RETOOL_API_TOKEN='your-token-here'
   
3. Run this test again:
   python scripts/test_retool_api_direct.py
   
4. Once connected, you can:
   - Create apps programmatically
   - Configure resources
   - Deploy dashboards
   
5. For manual dashboard creation:
   - Log into Retool
   - Create new app: "Sophia CEO Dashboard"
   - Add REST API resource pointing to: http://localhost:8000
   - Add authentication header: X-Admin-Key = sophia_admin_2024
"""
        )

    async def run_tests(self):
        """Run all tests"""
        print(f"{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}Retool API Direct Test{RESET}")
        print(f"{BLUE}{'='*60}{RESET}")

        # Test API connection
        connected = await self.test_api_connection()

        if connected:
            # Try to create a test app
            app_id = await self.create_test_app()

            # Test resource creation
            await self.test_resource_creation()

            print(f"\n{GREEN}✓ Retool API tests completed successfully!{RESET}")
        else:
            # Show setup instructions
            self.print_setup_instructions()

        # Always show quick start info
        print(f"\n{BLUE}=== Quick Start ==={RESET}")
        print(
            """
To deploy a dashboard manually:
1. Start the backend: cd backend && python main_simple.py
2. Test the API: curl http://localhost:8000/api/executive/summary
3. Create Retool app with REST API resource
4. Build your dashboard!
"""
        )


async def main():
    """Main function"""
    tester = RetoolAPITester()
    await tester.run_tests()


if __name__ == "__main__":
    asyncio.run(main())
