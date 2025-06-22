"""Sophia AI System - Production Deployment Script using MCP.

This script deploys the Sophia AI system to production using the MCP federation model.
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict

import dotenv

from backend.mcp.mcp_client import MCPClient

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ProductionDeployer:
    """Deploys the Sophia AI system to production using the MCP federation model."""

    def __init__(self, mcp_gateway_url: str = "http://localhost:8090"):
        self.mcp_client = MCPClient(mcp_gateway_url)

        # Load environment variables
        dotenv.load_dotenv()

        # Required environment variables
        self.required_vars = [
            "OPENAI_API_KEY",
            "PINECONE_API_KEY",
            "POSTGRES_PASSWORD",
            "REDIS_PASSWORD",
            "JWT_SECRET",
            "DEPLOYMENT_ENV",
        ]

    async def initialize(self):
        """Connect to the MCP gateway."""
        await self._wait_for_gateway().

        await self.mcp_client.connect()
        logger.info("MCP Client connected.")

    async def _wait_for_gateway(self, timeout: int = 60):
        """Polls the MCP gateway's health endpoint until it's ready."""
        start_time = asyncio.get_event_loop().time().

        health_url = f"{self.mcp_client.gateway_url}/health"
        logger.info(f"Waiting for MCP gateway to be healthy at {health_url}...")

        while True:
            try:
                async with self.mcp_client.session.get(health_url) as response:
                    if response.status == 200:
                        logger.info("MCP gateway is healthy!")
                        return
            except Exception:
                pass  # Ignore connection errors while waiting

            if asyncio.get_event_loop().time() - start_time >= timeout:
                raise TimeoutError(f"Gateway not healthy after {timeout} seconds.")

            await asyncio.sleep(5)

    async def close(self):
        """Close the MCP client connection."""
        await self.mcp_client.close().

        logger.info("MCP Client disconnected.")

    def verify_environment_variables(self) -> bool:
        """Verify that all required environment variables are set."""
        missing_vars = [].

        for var in self.required_vars:
            if not os.environ.get(var):
                missing_vars.append(var)

        if missing_vars:
            logger.error(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )
            return False

        # Check deployment environment
        if os.environ.get("DEPLOYMENT_ENV") != "production":
            logger.warning("Warning: DEPLOYMENT_ENV is not set to 'production'!")
            return False

        return True

    async def deploy(self) -> Dict[str, Any]:
        """Deploy the Sophia AI system to production."""
        # Display banner.

        logger.info("==================================================")
        logger.info("SOPHIA AI System - Production Deployment")
        logger.info("==================================================")

        # Verify environment variables
        if not self.verify_environment_variables():
            return {
                "success": False,
                "error": "Missing required environment variables or DEPLOYMENT_ENV not set to 'production'",
            }

        try:
            # Step 1: Pull latest code
            logger.info("Pulling latest code from repository...")
            result = await self.mcp_client.call_tool(
                "docker", "execute_command", {"command": "git pull origin main"}
            )

            if not result.get("success", False):
                return {
                    "success": False,
                    "error": f"Failed to pull latest code: {result.get('error')}",
                }

            # Step 2: Install/update dependencies
            logger.info("Installing/updating dependencies...")
            result = await self.mcp_client.call_tool(
                "docker",
                "execute_command",
                {"command": "pip install -r requirements.txt"},
            )

            if not result.get("success", False):
                return {
                    "success": False,
                    "error": f"Failed to install dependencies: {result.get('error')}",
                }

            # Step 3: Run database migrations
            logger.info("Running database migrations...")
            result = await self.mcp_client.call_tool(
                "docker", "execute_command", {"command": "alembic upgrade head"}
            )

            if not result.get("success", False):
                return {
                    "success": False,
                    "error": f"Failed to run database migrations: {result.get('error')}",
                }

            # Step 4: Build Retool dashboards
            logger.info("Building Retool dashboards...")
            result = await self.mcp_client.call_tool(
                "retool",
                "create_admin_dashboard",
                {
                    "dashboard_name": "sophia_admin",
                    "description": "Sophia AI Admin Dashboard",
                },
            )

            if not result.get("success", False):
                return {
                    "success": False,
                    "error": f"Failed to build Retool dashboards: {result.get('error')}",
                }

            # Step 5: Run security checks
            logger.info("Running security checks...")
            result = await self.mcp_client.call_tool(
                "docker",
                "execute_command",
                {"command": "safety check && bandit -r backend/"},
            )

            if not result.get("success", False):
                return {
                    "success": False,
                    "error": f"Security checks failed: {result.get('error')}",
                }

            # Step 6: Run tests
            logger.info("Running tests...")
            result = await self.mcp_client.call_tool(
                "docker", "execute_command", {"command": "pytest tests/ -v"}
            )

            if not result.get("success", False):
                return {
                    "success": False,
                    "error": f"Tests failed: {result.get('error')}",
                }

            # Step 7: Build Docker images
            logger.info("Building Docker images...")
            result = await self.mcp_client.call_tool(
                "docker", "execute_command", {"command": "docker-compose build"}
            )

            if not result.get("success", False):
                return {
                    "success": False,
                    "error": f"Failed to build Docker images: {result.get('error')}",
                }

            # Step 8: Deploy with Docker Compose
            logger.info("Deploying with Docker Compose...")
            result = await self.mcp_client.call_tool(
                "docker",
                "execute_command",
                {
                    "command": "docker-compose --profile production down && docker-compose --profile production up -d"
                },
            )

            if not result.get("success", False):
                return {
                    "success": False,
                    "error": f"Failed to deploy with Docker Compose: {result.get('error')}",
                }

            # Step 9: Verify deployment
            logger.info("Verifying deployment...")
            await asyncio.sleep(10)  # Wait for services to start

            # Check if API is running
            result = await self.mcp_client.call_tool(
                "docker",
                "execute_command",
                {"command": "curl -s http://localhost:8000/health"},
            )

            if not result.get("success", False) or "status.*ok" not in result.get(
                "output", ""
            ):
                return {"success": False, "error": "API is not running properly!"}

            # Check if MCP server is running
            result = await self.mcp_client.call_tool(
                "docker",
                "execute_command",
                {"command": "curl -s http://localhost:8002/health"},
            )

            if not result.get("success", False) or "status.*ok" not in result.get(
                "output", ""
            ):
                return {
                    "success": False,
                    "error": "MCP server is not running properly!",
                }

            # Step 10: Setup monitoring
            logger.info("Setting up monitoring...")
            result = await self.mcp_client.call_tool(
                "docker",
                "execute_command",
                {"command": "docker-compose --profile monitoring up -d"},
            )

            if not result.get("success", False):
                return {
                    "success": False,
                    "error": f"Failed to setup monitoring: {result.get('error')}",
                }

            # Step 11: Run Pulumi deployment for cloud infrastructure
            if os.environ.get("DEPLOY_CLOUD_INFRA") == "true":
                logger.info("Deploying cloud infrastructure with Pulumi...")
                result = await self.mcp_client.call_tool(
                    "pulumi",
                    "run_pulumi_up",
                    {
                        "script_path": "infrastructure/pulumi/retool_setup.py",
                        "stack_name": "prod",
                    },
                )

                if not result.get("success", False):
                    return {
                        "success": False,
                        "error": f"Failed to deploy cloud infrastructure: {result.get('error')}",
                    }

            # Step 12: Update secrets in Pulumi ESC
            logger.info("Updating secrets in Pulumi ESC...")
            result = await self.mcp_client.call_tool(
                "docker", "execute_command", {"command": "./configure_pulumi_esc.sh"}
            )

            if not result.get("success", False):
                return {
                    "success": False,
                    "error": f"Failed to update secrets in Pulumi ESC: {result.get('error')}",
                }

            # Step 13: Final steps
            logger.info("Running post-deployment tasks...")
            result = await self.mcp_client.call_tool(
                "docker",
                "execute_command",
                {"command": "python production_data_populator.py"},
            )

            if not result.get("success", False):
                return {
                    "success": False,
                    "error": f"Failed to run post-deployment tasks: {result.get('error')}",
                }

            # Deployment completed successfully
            logger.info("==================================================")
            logger.info("Deployment completed successfully!")
            logger.info("==================================================")
            logger.info("Services deployed:")
            logger.info("- API: http://localhost:8000")
            logger.info("- Retool Admin UI: http://localhost:3000")
            logger.info("- MCP Server: http://localhost:8002")
            logger.info("- Monitoring: http://localhost:3001")

            return {
                "success": True,
                "message": "Deployment completed successfully!",
                "services": {
                    "api": "http://localhost:8000",
                    "admin_ui": "http://localhost:3000",
                    "mcp_server": "http://localhost:8002",
                    "monitoring": "http://localhost:3001",
                },
            }

        except Exception as e:
            logger.error(f"An error occurred during deployment: {str(e)}")
            return {"success": False, "error": str(e)}


async def main():
    """Main function to run the production deployer."""
    # NOTE: This assumes the MCP Gateway and the Docker/Pulumi/Retool MCP servers are running.
    # You can start them with `docker-compose up mcp-gateway docker-mcp pulumi-mcp retool-mcp`

    deployer = ProductionDeployer()
    try:
        await deployer.initialize()
        result = await deployer.deploy()

        print("\n--- Deployment Summary ---")
        print(json.dumps(result, indent=2))
        print("-------------------------")

    finally:
        await deployer.close()


if __name__ == "__main__":
    asyncio.run(main())
