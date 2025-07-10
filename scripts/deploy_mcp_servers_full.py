#!/usr/bin/env python3
"""
🚀 MCP Server Full Deployment Script
Deploy all MCP servers with monitoring and verification
Date: July 10, 2025

PERMANENT SCRIPT - DO NOT DELETE
This is a reusable deployment tool for MCP servers
"""

import asyncio
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

import httpx

# Configure logging
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# MCP Server Configuration
MCP_SERVERS = [
    {
        "name": "ai_memory",
        "path": "mcp-servers/ai_memory/server.py",
        "port": 9001,
        "display_name": "AI Memory",
        "critical": True,
    },
    {
        "name": "codacy",
        "path": "mcp-servers/codacy/server.py",
        "port": 3008,
        "display_name": "Codacy",
        "critical": False,
    },
    {
        "name": "github",
        "path": "mcp-servers/github/server.py",
        "port": 9003,
        "display_name": "GitHub",
        "critical": True,
    },
    {
        "name": "linear",
        "path": "mcp-servers/linear/server.py",
        "port": 9004,
        "display_name": "Linear",
        "critical": False,
    },
    {
        "name": "asana",
        "path": "mcp-servers/asana/server.py",
        "port": 9006,
        "display_name": "Asana",
        "critical": False,
    },
    {
        "name": "notion",
        "path": "mcp-servers/notion/server.py",
        "port": 9102,
        "display_name": "Notion",
        "critical": False,
    },
    {
        "name": "slack",
        "path": "mcp-servers/slack/server.py",
        "port": 9101,
        "display_name": "Slack",
        "critical": True,
    },
    {
        "name": "snowflake_unified",
        "path": "mcp-servers/snowflake_unified/server.py",
        "port": 9001,
        "display_name": "Snowflake Unified",
        "critical": True,
    },
    {
        "name": "gong",
        "path": "mcp-servers/gong/server.py",
        "port": 9100,
        "display_name": "Gong",
        "critical": True,
    },
    {
        "name": "hubspot_unified",
        "path": "mcp-servers/hubspot_unified/server.py",
        "port": 9105,
        "display_name": "HubSpot",
        "critical": True,
    },
]


class MCPDeploymentManager:
    """Manage MCP server deployments"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.processes = {}
        self.kubectl_configured = False
        self.lambda_labs_ip = "192.222.58.232"

    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met"""
        logger.info("Checking prerequisites...")

        # Check Python
        if sys.version_info < (3, 10):
            logger.error("Python 3.10+ required")
            return False

        # Check environment
        env_file = self.project_root / "local.env"
        if not env_file.exists():
            logger.warning("local.env not found, using environment variables")

        # Check kubectl
        try:
            result = subprocess.run(
                ["kubectl", "version", "--client"], capture_output=True, text=True
            )
            logger.info(f"kubectl available: {result.returncode == 0}")
        except FileNotFoundError:
            logger.warning("kubectl not installed - K8s deployment will be skipped")

        return True

    def kill_port(self, port: int):
        """Kill any process using the specified port"""
        try:
            # Find process using the port
            result = subprocess.run(
                ["lsof", "-t", f"-i:{port}"], capture_output=True, text=True
            )
            if result.stdout.strip():
                pid = result.stdout.strip()
                subprocess.run(["kill", "-9", pid])
                logger.info(f"Killed process {pid} on port {port}")
                time.sleep(0.5)
        except Exception as e:
            logger.debug(f"No process to kill on port {port}: {e}")

    def start_mcp_server(self, server_config: dict) -> Optional[subprocess.Popen]:
        """Start a single MCP server"""
        name = server_config["name"]
        path = self.project_root / server_config["path"]
        port = server_config["port"]

        if not path.exists():
            logger.error(f"Server file not found: {path}")
            return None

        # Kill any existing process on the port
        self.kill_port(port)

        # Set environment variables
        env = os.environ.copy()
        env["MCP_SERVER_PORT"] = str(port)
        env["PYTHONUNBUFFERED"] = "1"

        # Start the server
        try:
            logger.info(f"Starting {server_config['display_name']} on port {port}...")
            process = subprocess.Popen(
                [sys.executable, str(path)],
                cwd=str(self.project_root),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # Give it time to start
            time.sleep(2)

            # Check if it's still running
            if process.poll() is None:
                logger.info(f"✅ {server_config['display_name']} started successfully")
                return process
            else:
                stdout, stderr = process.communicate()
                logger.error(f"❌ {server_config['display_name']} failed to start")
                logger.error(f"stderr: {stderr.decode()}")
                return None

        except Exception as e:
            logger.error(f"Failed to start {name}: {e}")
            return None

    async def check_server_health(self, server_config: dict) -> bool:
        """Check if a server is healthy"""
        port = server_config["port"]
        url = f"http://localhost:{port}/health"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=5)
                return response.status_code == 200
        except:
            return False

    def configure_kubectl(self) -> bool:
        """Configure kubectl for Lambda Labs K3s"""
        logger.info("Configuring kubectl for Lambda Labs K3s...")

        kubeconfig_path = Path.home() / ".kube" / "lambda-labs-k3s"

        # Check if we have the kubeconfig
        if not kubeconfig_path.exists():
            logger.warning(
                """
⚠️  Lambda Labs K3s kubeconfig not found!

To configure kubectl:
1. SSH into Lambda Labs: ssh ubuntu@192.222.58.232
2. Get kubeconfig: sudo cat /etc/rancher/k3s/k3s.yaml
3. Save it locally to: ~/.kube/lambda-labs-k3s
4. Update the server address to: https://192.222.58.232:6443
5. Export: export KUBECONFIG=~/.kube/lambda-labs-k3s
"""
            )
            return False

        # Set KUBECONFIG environment variable
        os.environ["KUBECONFIG"] = str(kubeconfig_path)

        # Test connection
        try:
            result = subprocess.run(
                ["kubectl", "get", "nodes"], capture_output=True, text=True
            )
            if result.returncode == 0:
                logger.info("✅ kubectl configured successfully")
                self.kubectl_configured = True
                return True
            else:
                logger.error(f"kubectl test failed: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"kubectl configuration failed: {e}")
            return False

    def deploy_to_k8s(self):
        """Deploy MCP servers to K8s"""
        if not self.kubectl_configured:
            logger.warning("kubectl not configured, skipping K8s deployment")
            return

        logger.info("Deploying to K8s...")

        # Apply namespace
        namespace_yaml = self.project_root / "k8s" / "namespace.yaml"
        if namespace_yaml.exists():
            subprocess.run(["kubectl", "apply", "-f", str(namespace_yaml)])

        # Apply kustomization
        kustomization_path = self.project_root / "k8s" / "overlays" / "production"
        if kustomization_path.exists():
            subprocess.run(["kubectl", "apply", "-k", str(kustomization_path)])
            logger.info("✅ K8s deployment initiated")

    async def monitor_deployments(self):
        """Monitor all deployments"""
        logger.info("\n" + "=" * 60)
        logger.info("DEPLOYMENT STATUS")
        logger.info("=" * 60)

        # Local deployments
        logger.info("\n📍 LOCAL DEPLOYMENTS:")
        for server in MCP_SERVERS:
            process = self.processes.get(server["name"])
            if process and process.poll() is None:
                health = await self.check_server_health(server)
                status = "✅ Healthy" if health else "⚠️  Running (no health endpoint)"
            else:
                status = "❌ Not running"

            logger.info(
                f"  {server['display_name']:20} Port {server['port']:5} {status}"
            )

        # K8s deployments
        if self.kubectl_configured:
            logger.info("\n☸️  K8S DEPLOYMENTS:")
            try:
                result = subprocess.run(
                    ["kubectl", "get", "pods", "-n", "sophia-ai-prod"],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    logger.info(result.stdout)
            except:
                pass

    async def verify_snowflake_data(self):
        """Verify data is flowing to Snowflake"""
        logger.info("\n❄️  SNOWFLAKE DATA VERIFICATION:")

        try:
            # Import Snowflake connector
            import snowflake.connector
            from backend.core.unified_config import UnifiedConfig

            config = UnifiedConfig()

            # Connect to Snowflake
            conn = snowflake.connector.connect(
                account=config.snowflake_account,
                user=config.snowflake_user,
                password=config.snowflake_password,
                warehouse=config.snowflake_warehouse,
                database=config.snowflake_database,
                schema=config.snowflake_schema,
            )

            cursor = conn.cursor()

            # Check AI Memory table
            cursor.execute(
                """
                SELECT COUNT(*) as record_count,
                       MAX(created_at) as latest_record
                FROM AI_MEMORY.SOPHIA_MEMORY_RECORDS
            """
            )
            result = cursor.fetchone()

            if result:
                logger.info(f"  AI Memory Records: {result[0]}")
                logger.info(f"  Latest Record: {result[1]}")

            # Check other tables
            tables_to_check = [
                "STG_GONG_CALLS",
                "STG_HUBSPOT_CONTACTS",
                "STG_SLACK_MESSAGES",
            ]

            for table in tables_to_check:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    logger.info(f"  {table}: {count} records")
                except:
                    logger.info(f"  {table}: Not available")

            cursor.close()
            conn.close()

        except Exception as e:
            logger.error(f"Snowflake verification failed: {e}")

    async def run_deployment(self):
        """Run the full deployment"""
        logger.info("🚀 Starting MCP Server Full Deployment")

        if not self.check_prerequisites():
            return

        # Configure kubectl
        self.configure_kubectl()

        # Start all MCP servers
        logger.info("\n Starting MCP servers...")
        for server in MCP_SERVERS:
            process = self.start_mcp_server(server)
            if process:
                self.processes[server["name"]] = process

        # Wait for servers to stabilize
        logger.info("\nWaiting for servers to stabilize...")
        await asyncio.sleep(5)

        # Monitor deployments
        await self.monitor_deployments()

        # Deploy to K8s
        self.deploy_to_k8s()

        # Verify Snowflake data
        await self.verify_snowflake_data()

        # Create GitHub secrets documentation
        self.create_github_secrets_doc()

        logger.info("\n" + "=" * 60)
        logger.info("DEPLOYMENT COMPLETE")
        logger.info("=" * 60)
        logger.info("\nNext steps:")
        logger.info(
            "1. Add GitHub secrets (see docs/deployment/GITHUB_SECRETS_SETUP.md)"
        )
        logger.info(
            "2. Configure kubectl (see docs/deployment/KUBECTL_LAMBDA_LABS_SETUP.md)"
        )
        logger.info("3. Push to main to trigger K8s deployment")
        logger.info("\nMonitoring URLs:")
        logger.info("  Backend API: http://localhost:8001")
        logger.info("  API Docs: http://localhost:8001/docs")
        logger.info("  AI Memory: http://localhost:9001/health")

    def create_github_secrets_doc(self):
        """Create GitHub secrets documentation"""
        doc_path = self.project_root / "docs" / "deployment" / "GITHUB_SECRETS_SETUP.md"

        content = """# GitHub Secrets Setup for Sophia AI

## Required Secrets

Add these secrets to your GitHub repository settings:

### 1. Docker Hub Credentials
- **DOCKER_HUB_USERNAME**: Your Docker Hub username
- **DOCKER_HUB_ACCESS_TOKEN**: Docker Hub access token (not password)

### 2. Lambda Labs Kubeconfig
- **LAMBDA_LABS_KUBECONFIG**: Base64 encoded kubeconfig

To encode your kubeconfig:
```bash
cat ~/.kube/lambda-labs-k3s | base64 -w 0
```

## Adding Secrets

1. Go to your GitHub repository
2. Navigate to Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add each secret with the exact names above

## Verification

After adding secrets, the deployment workflow will trigger automatically on push to main.

Monitor the deployment:
- GitHub Actions tab in your repository
- Lambda Labs K3s cluster: `kubectl get pods -n sophia-ai-prod`
"""

        doc_path.parent.mkdir(parents=True, exist_ok=True)
        doc_path.write_text(content)
        logger.info(f"Created GitHub secrets documentation at {doc_path}")


async def main():
    """Main entry point"""
    manager = MCPDeploymentManager()
    await manager.run_deployment()


if __name__ == "__main__":
    asyncio.run(main())
