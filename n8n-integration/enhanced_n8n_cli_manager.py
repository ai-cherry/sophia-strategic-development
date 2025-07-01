#!/usr/bin/env python3
"""
Enhanced N8N CLI Manager for Sophia AI
Leverages N8N CLI capabilities for workflow automation and management
Integrates with existing N8N Docker infrastructure
"""

import asyncio
import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkflowDefinition(BaseModel):
    name: str
    description: str
    workflow_id: str | None = None
    nodes: list[dict[str, Any]]
    connections: dict[str, Any]
    active: bool = True
    tags: list[str] = []


class N8NCliManager:
    """Enhanced N8N CLI manager leveraging CLI capabilities for Sophia AI"""

    def __init__(
        self,
        n8n_url: str = "http://localhost:5678",
        n8n_user: str = "sophia_admin",
        n8n_password: str = "sophia_secure_password",
    ):
        self.n8n_url = n8n_url
        self.n8n_user = n8n_user
        self.n8n_password = n8n_password
        self.workflows_dir = Path(__file__).parent / "workflows"
        self.custom_nodes_dir = Path(__file__).parent / "custom-nodes"

        # Ensure directories exist
        self.workflows_dir.mkdir(exist_ok=True)
        self.custom_nodes_dir.mkdir(exist_ok=True)

        # Initialize HTTP client for API calls
        self.client = httpx.AsyncClient(timeout=30.0)

    async def __aenter__(self):
        """Async context manager entry"""
        await self.authenticate()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.client.aclose()

    async def authenticate(self):
        """Authenticate with N8N instance"""
        try:
            # Login to N8N instance
            login_response = await self.client.post(
                f"{self.n8n_url}/rest/login",
                json={"email": self.n8n_user, "password": self.n8n_password},
            )

            if login_response.status_code == 200:
                logger.info("✅ Successfully authenticated with N8N")
                return True
            else:
                logger.error(
                    f"❌ N8N authentication failed: {login_response.status_code}"
                )
                return False

        except Exception as e:
            logger.error(f"❌ N8N authentication error: {e}")
            return False

    def run_cli_command(
        self, command: list[str], cwd: Path | None = None
    ) -> dict[str, Any]:
        """Execute N8N CLI command and return result"""
        try:
            # Ensure n8n is available globally (should be installed via npm)
            full_command = ["n8n"] + command

            result = subprocess.run(
                full_command,
                cwd=cwd or self.workflows_dir,
                capture_output=True,
                text=True,
                timeout=60,
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
            }

        except subprocess.TimeoutExpired:
            logger.error("❌ N8N CLI command timed out")
            return {"success": False, "error": "Command timed out"}
        except Exception as e:
            logger.error(f"❌ N8N CLI command failed: {e}")
            return {"success": False, "error": str(e)}

    async def export_workflows(self, output_dir: Path | None = None) -> dict[str, Any]:
        """Export all workflows using N8N CLI"""
        export_dir = output_dir or self.workflows_dir / "exports"
        export_dir.mkdir(exist_ok=True)

        logger.info("📤 Exporting workflows via N8N CLI...")

        # Export workflows
        result = self.run_cli_command(
            ["export:workflow", "--output", str(export_dir), "--all"]
        )

        if result["success"]:
            logger.info("✅ Workflows exported successfully")
            return {
                "success": True,
                "export_path": str(export_dir),
                "timestamp": datetime.now().isoformat(),
            }
        else:
            logger.error(
                f"❌ Workflow export failed: {result.get('stderr', 'Unknown error')}"
            )
            return {"success": False, "error": result.get("stderr", "Export failed")}

    async def import_workflows(self, import_dir: Path) -> dict[str, Any]:
        """Import workflows using N8N CLI"""
        if not import_dir.exists():
            return {
                "success": False,
                "error": f"Import directory {import_dir} does not exist",
            }

        logger.info(f"📥 Importing workflows from {import_dir}...")

        # Import workflows
        result = self.run_cli_command(
            ["import:workflow", "--input", str(import_dir), "--separate"]
        )

        if result["success"]:
            logger.info("✅ Workflows imported successfully")
            return {
                "success": True,
                "import_path": str(import_dir),
                "timestamp": datetime.now().isoformat(),
            }
        else:
            logger.error(
                f"❌ Workflow import failed: {result.get('stderr', 'Unknown error')}"
            )
            return {"success": False, "error": result.get("stderr", "Import failed")}

    async def manage_credentials(
        self, action: str, credential_data: dict | None = None
    ) -> dict[str, Any]:
        """Manage credentials using N8N CLI"""
        logger.info(f"🔐 Managing credentials: {action}")

        if action == "export":
            # Export credentials
            result = self.run_cli_command(
                [
                    "export:credentials",
                    "--output",
                    str(self.workflows_dir / "credentials"),
                    "--decrypt",
                ]
            )
        elif action == "import" and credential_data:
            # Import credentials
            cred_file = self.workflows_dir / "temp_credentials.json"
            with open(cred_file, "w") as f:
                json.dump(credential_data, f)

            result = self.run_cli_command(
                ["import:credentials", "--input", str(cred_file)]
            )

            # Clean up temp file
            cred_file.unlink(missing_ok=True)
        else:
            return {"success": False, "error": f"Invalid credential action: {action}"}

        return {"success": result["success"], "result": result}

    async def install_community_nodes(self, node_packages: list[str]) -> dict[str, Any]:
        """Install community nodes using N8N CLI"""
        results = []

        for package in node_packages:
            logger.info(f"📦 Installing community node: {package}")

            result = self.run_cli_command(["community-install", package])

            results.append(
                {
                    "package": package,
                    "success": result["success"],
                    "output": result.get("stdout", ""),
                    "error": result.get("stderr", ""),
                }
            )

        successful_installs = [r for r in results if r["success"]]

        return {
            "success": len(successful_installs) == len(node_packages),
            "total_packages": len(node_packages),
            "successful_installs": len(successful_installs),
            "results": results,
        }

    async def create_sophia_ai_workflows(self) -> dict[str, Any]:
        """Create predefined Sophia AI workflow templates"""
        workflows = []

        # Executive Intelligence Workflow
        executive_workflow = {
            "name": "Sophia AI - Executive Intelligence Pipeline",
            "description": "Automated executive intelligence gathering and analysis",
            "nodes": [
                {
                    "name": "Trigger",
                    "type": "n8n-nodes-base.cron",
                    "position": [200, 200],
                    "parameters": {
                        "rule": {"interval": [{"field": "hours", "value": 4}]}
                    },
                },
                {
                    "name": "Apify Intelligence",
                    "type": "n8n-nodes-base.httpRequest",
                    "position": [400, 200],
                    "parameters": {
                        "url": "http://localhost:9015/api/competitive-analysis",
                        "method": "POST",
                    },
                },
                {
                    "name": "Sophia AI Enhancement",
                    "type": "n8n-nodes-base.httpRequest",
                    "position": [600, 200],
                    "parameters": {
                        "url": "http://localhost:9099/api/v1/n8n/process",
                        "method": "POST",
                    },
                },
                {
                    "name": "Executive Notification",
                    "type": "n8n-nodes-base.slack",
                    "position": [800, 200],
                    "parameters": {"channel": "#executive-insights"},
                },
            ],
            "connections": {
                "Trigger": {"main": [["Apify Intelligence"]]},
                "Apify Intelligence": {"main": [["Sophia AI Enhancement"]]},
                "Sophia AI Enhancement": {"main": [["Executive Notification"]]},
            },
        }

        # Business Intelligence Workflow
        business_workflow = {
            "name": "Sophia AI - Business Intelligence Automation",
            "description": "Automated business data processing and insights",
            "nodes": [
                {
                    "name": "Webhook Trigger",
                    "type": "n8n-nodes-base.webhook",
                    "position": [200, 200],
                    "parameters": {"path": "sophia-business-data"},
                },
                {
                    "name": "Hugging Face Processing",
                    "type": "n8n-nodes-base.httpRequest",
                    "position": [400, 200],
                    "parameters": {
                        "url": "http://localhost:9016/api/process-business-data",
                        "method": "POST",
                    },
                },
                {
                    "name": "Vector Storage",
                    "type": "n8n-nodes-base.httpRequest",
                    "position": [600, 200],
                    "parameters": {
                        "url": "http://localhost:9017/api/store-vectors",
                        "method": "POST",
                    },
                },
                {
                    "name": "Dashboard Update",
                    "type": "n8n-nodes-base.httpRequest",
                    "position": [800, 200],
                    "parameters": {
                        "url": "http://localhost:3000/api/dashboard/update",
                        "method": "POST",
                    },
                },
            ],
            "connections": {
                "Webhook Trigger": {"main": [["Hugging Face Processing"]]},
                "Hugging Face Processing": {"main": [["Vector Storage"]]},
                "Vector Storage": {"main": [["Dashboard Update"]]},
            },
        }

        workflows.extend([executive_workflow, business_workflow])

        # Save workflows to files
        for workflow in workflows:
            workflow_file = (
                self.workflows_dir
                / f"{workflow['name'].lower().replace(' ', '_')}.json"
            )
            with open(workflow_file, "w") as f:
                json.dump(workflow, f, indent=2)

            logger.info(f"✅ Created workflow template: {workflow['name']}")

        return {
            "success": True,
            "workflows_created": len(workflows),
            "workflow_files": [w["name"] for w in workflows],
        }

    async def monitor_workflows(self) -> dict[str, Any]:
        """Monitor workflow execution status"""
        try:
            # Get workflow executions
            response = await self.client.get(f"{self.n8n_url}/rest/executions")

            if response.status_code == 200:
                executions = response.json()

                # Analyze execution status
                total_executions = len(executions.get("data", []))
                successful_executions = len(
                    [
                        e
                        for e in executions.get("data", [])
                        if e.get("finished") and not e.get("stoppedAt")
                    ]
                )
                failed_executions = total_executions - successful_executions

                return {
                    "success": True,
                    "total_executions": total_executions,
                    "successful_executions": successful_executions,
                    "failed_executions": failed_executions,
                    "success_rate": (
                        (successful_executions / total_executions * 100)
                        if total_executions > 0
                        else 0
                    ),
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                return {
                    "success": False,
                    "error": f"API call failed: {response.status_code}",
                }

        except Exception as e:
            logger.error(f"❌ Workflow monitoring failed: {e}")
            return {"success": False, "error": str(e)}

    async def backup_n8n_data(self) -> dict[str, Any]:
        """Create comprehensive backup of N8N data"""
        backup_dir = (
            self.workflows_dir / "backups" / datetime.now().strftime("%Y%m%d_%H%M%S")
        )
        backup_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"💾 Creating N8N backup in {backup_dir}...")

        backup_results = {}

        # Export workflows
        workflow_backup = await self.export_workflows(backup_dir / "workflows")
        backup_results["workflows"] = workflow_backup

        # Export credentials
        cred_result = self.run_cli_command(
            [
                "export:credentials",
                "--output",
                str(backup_dir / "credentials"),
                "--decrypt",
            ]
        )
        backup_results["credentials"] = {"success": cred_result["success"]}

        # Create backup manifest
        manifest = {
            "backup_timestamp": datetime.now().isoformat(),
            "backup_dir": str(backup_dir),
            "components": backup_results,
            "sophia_ai_version": "enhanced_cli_v1.0",
        }

        with open(backup_dir / "backup_manifest.json", "w") as f:
            json.dump(manifest, f, indent=2)

        return {
            "success": True,
            "backup_path": str(backup_dir),
            "components_backed_up": len(backup_results),
            "manifest": manifest,
        }


# CLI Commands for easy management
async def main():
    """Main CLI interface for enhanced N8N management"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python enhanced_n8n_cli_manager.py <command>")
        print(
            "Commands: export, import, backup, monitor, create-workflows, install-nodes"
        )
        return

    command = sys.argv[1]

    async with N8NCliManager() as n8n_manager:
        if command == "export":
            result = await n8n_manager.export_workflows()
            print(f"Export result: {result}")

        elif command == "backup":
            result = await n8n_manager.backup_n8n_data()
            print(f"Backup result: {result}")

        elif command == "monitor":
            result = await n8n_manager.monitor_workflows()
            print(f"Monitoring result: {result}")

        elif command == "create-workflows":
            result = await n8n_manager.create_sophia_ai_workflows()
            print(f"Workflow creation result: {result}")

        elif command == "install-nodes":
            # Install common Sophia AI community nodes
            nodes = [
                "n8n-nodes-slack-enhanced",
                "n8n-nodes-hubspot-enhanced",
                "n8n-nodes-snowflake",
            ]
            result = await n8n_manager.install_community_nodes(nodes)
            print(f"Node installation result: {result}")

        else:
            print(f"Unknown command: {command}")


if __name__ == "__main__":
    asyncio.run(main())
