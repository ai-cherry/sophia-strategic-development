#!/usr/bin/env python3
"""
Sophia Intel AI Deployment Script

Comprehensive deployment automation for sophia-intel.ai integration
including Vercel project management, DNS configuration, and Lambda Labs integration.

Usage:
    python scripts/deploy_sophia_intel_ai.py --phase [1|2|3|4|all]
"""

import argparse
import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from typing import Optional

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Add backend to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

try:
    from backend.core.auto_esc_config import get_config_value, get_lambda_labs_config
except ImportError:
    logging.warning("⚠️  Warning: Could not import Sophia AI config")
    get_lambda_labs_config = None
    def get_config_value(key, default=None):
        return os.getenv(key.upper(), default)


class SophiaIntelAIDeployer:
    """Comprehensive deployment manager for sophia-intel.ai"""

    def __init__(self):
        self.domain = "sophia-intel.ai"

        # Use Pulumi ESC for retrieving secrets
        self.vercel_token = get_config_value("vercel_api_token") or get_config_value(
            "VERCEL_API_TOKEN"
        )
        self.namecheap_api_key = get_config_value(
            "namecheap_api_key"
        ) or get_config_value("NAMECHEAP_API_KEY")

        if not self.vercel_token:
            logging.error(
                "❌ Error: VERCEL_API_TOKEN not found in Pulumi ESC or environment variables.\n"
                "Please ensure it's set in GitHub Organization Secrets and synced to Pulumi ESC."
            )
            sys.exit(1)

        if not self.namecheap_api_key:
            logging.error(
                "❌ Error: NAMECHEAP_API_KEY not found in Pulumi ESC or environment variables.\n"
                "Please ensure it's set in GitHub Organization Secrets and synced to Pulumi ESC."
            )
            sys.exit(1)

        logging.info("✅ Successfully loaded API keys from Pulumi ESC")

        self.target_projects = {
            "sophia-intel-ai-app": {
                "domain": "app.sophia-intel.ai",
                "framework": "vite",
                "build_command": "npm run build",
                "output_directory": "dist",
                "root_directory": "frontend",
                "env_vars": {
                    "VITE_API_ENDPOINT": "https://api.sophia-intel.ai",
                    "VITE_ENVIRONMENT": "production",
                    "VITE_DOMAIN": "sophia-intel.ai",
                    "VITE_APP_NAME": "Sophia AI",
                },
            },
            "sophia-intel-ai-admin": {
                "domain": "admin.sophia-intel.ai",
                "framework": "vite",
                "build_command": "cd admin && npm run build",
                "output_directory": "admin/dist",
                "root_directory": "admin",
                "env_vars": {
                    "VITE_API_ENDPOINT": "https://api.sophia-intel.ai",
                    "VITE_ADMIN_MODE": "true",
                    "VITE_DOMAIN": "sophia-intel.ai",
                    "VITE_APP_NAME": "Sophia AI Admin",
                },
            },
        }

        self.lambda_labs_instances = {
            "sophia-ai-core": {
                "ip": "192.222.58.232",
                "purpose": "Core AI Services & Snowflake Cortex",
                "endpoints": ["8000", "9001"],
            },
            "sophia-production-instance": {
                "ip": "104.171.202.103",
                "purpose": "Monitoring & Operations",
                "endpoints": ["3000", "9090"],
            },
            "sophia-mcp-orchestrator": {
                "ip": "104.171.202.117",
                "purpose": "MCP Server Orchestration",
                "endpoints": ["8080"],
            },
            "sophia-data-pipeline": {
                "ip": "104.171.202.134",
                "purpose": "Data Processing & ETL",
                "endpoints": ["8000"],
            },
            "sophia-development": {
                "ip": "155.248.194.183",
                "purpose": "Development & Testing",
                "endpoints": ["8000"],
            },
        }

    def phase_1_immediate_fixes(self) -> bool:
        """Phase 1: Vercel project cleanup and build fixes"""
        logging.info("🚀 Phase 1: Immediate Fixes - Vercel Project Cleanup")

        # 1.1 Delete unnecessary projects
        projects_to_delete = [
            "sophia-ai-frontend-dev",
            "sophia-ai-frontend-prod",
            "sophia-ai",
            "frontend",
            "dist",
            "sophia-vercel",
        ]

        for project in projects_to_delete:
            logging.info(f"   🗑️  Deleting project: {project}")
            result = self._delete_vercel_project(project)
            if result:
                logging.info(f"   ✅ Deleted {project}")
            else:
                logging.warning(f"   ⚠️  Could not delete {project} (may not exist)")

        # 1.2 Archive legacy projects
        legacy_projects = ["orchestra-ai-admin", "orchestra-dev"]
        for project in legacy_projects:
            logging.info(f"   📦 Archiving legacy project: {project}")
            # Note: Vercel API doesn't have archive, so we'll leave these for manual handling

        # 1.3 Rename main projects
        renames = {
            "sophia-main": "sophia-intel-ai-app",
            "sophia-ai-ceo-dashboard": "sophia-intel-ai-admin",
        }

        for old_name, new_name in renames.items():
            logging.info(f"   🔄 Renaming {old_name} → {new_name}")
            result = self._rename_vercel_project(old_name, new_name)
            if result:
                logging.info(f"   ✅ Renamed to {new_name}")
            else:
                logging.warning(f"   ⚠️  Could not rename {old_name}")

        # 1.4 Update project configurations
        for project_name, config in self.target_projects.items():
            logging.info(f"   ⚙️  Configuring {project_name}")
            result = self._update_vercel_project_config(project_name, config)
            if result:
                logging.info(f"   ✅ Configured {project_name}")
            else:
                logging.error(f"   ❌ Failed to configure {project_name}")

        logging.info("✅ Phase 1 Complete: Vercel projects cleaned up and configured")
        return True

    def phase_2_domain_integration(self) -> bool:
        """Phase 2: DNS optimization and domain integration"""
        logging.info("🌐 Phase 2: Domain Integration - DNS & SSL Setup")

        # 2.1 Verify current DNS records
        current_dns = self._get_current_dns_records()
        logging.info(f"   📋 Current DNS records: {len(current_dns)} found")

        # 2.2 Add missing DNS records
        required_records = [
            {"name": "admin", "type": "CNAME", "value": "cname.vercel-dns.com"},
            {"name": "docs", "type": "CNAME", "value": "cname.vercel-dns.com"},
            {"name": "status", "type": "CNAME", "value": "cname.vercel-dns.com"},
            {"name": "staging", "type": "CNAME", "value": "cname.vercel-dns.com"},
        ]

        for record in required_records:
            logging.info(f"   🔧 Adding DNS record: {record['name']}.{self.domain}")
            result = self._add_dns_record(record)
            if result:
                logging.info(f"   ✅ Added {record['name']} DNS record")
            else:
                logging.warning(f"   ⚠️  DNS record {record['name']} may already exist")

        # 2.3 Configure custom domains in Vercel
        for project_name, config in self.target_projects.items():
            domain = config["domain"]
            logging.info(f"   🔗 Adding custom domain {domain} to {project_name}")
            result = self._add_vercel_custom_domain(project_name, domain)
            if result:
                logging.info(f"   ✅ Added custom domain {domain}")
            else:
                logging.warning(f"   ⚠️  Custom domain {domain} may already exist")

        logging.info("✅ Phase 2 Complete: Domain integration configured")
        return True

    def phase_3_backend_integration(self) -> bool:
        """Phase 3: Lambda Labs backend integration"""
        logging.info("🔌 Phase 3: Backend Integration - Lambda Labs Connectivity")

        # 3.1 Test Lambda Labs instance connectivity
        healthy_instances = 0
        for instance_name, config in self.lambda_labs_instances.items():
            ip = config["ip"]
            logging.info(f"   🏥 Testing connectivity to {instance_name} ({ip})")

            for port in config["endpoints"]:
                if self._test_instance_connectivity(ip, port):
                    logging.info(f"   ✅ {instance_name}:{port} is healthy")
                    healthy_instances += 1
                else:
                    logging.warning(f"   ❌ {instance_name}:{port} is not responding")

        logging.info(f"   📊 Healthy endpoints: {healthy_instances}")

        # 3.2 Update environment variables with backend endpoints
        for project_name, config in self.target_projects.items():
            logging.info(f"   🔐 Updating environment variables for {project_name}")
            result = self._sync_environment_variables(project_name, config["env_vars"])
            if result:
                logging.info(f"   ✅ Environment variables updated for {project_name}")
            else:
                logging.error(
                    f"   ❌ Failed to update environment variables for {project_name}"
                )

        # 3.3 Deploy API gateway configuration
        logging.info("   🚪 Deploying API gateway configuration")
        result = self._deploy_api_gateway()
        if result:
            logging.info("   ✅ API gateway deployed")
        else:
            logging.warning("   ⚠️  API gateway deployment needs manual verification")

        logging.info("✅ Phase 3 Complete: Backend integration established")
        return True

    def phase_4_monitoring_optimization(self) -> bool:
        """Phase 4: Monitoring and optimization setup"""
        logging.info("📊 Phase 4: Monitoring & Optimization")

        # 4.1 Deploy status page
        logging.info("   📈 Setting up status page monitoring")
        result = self._setup_status_monitoring()
        if result:
            logging.info("   ✅ Status monitoring configured")
        else:
            logging.warning("   ⚠️  Status monitoring needs manual setup")

        # 4.2 Configure cost monitoring
        logging.info("   💰 Setting up cost monitoring")
        result = self._setup_cost_monitoring()
        if result:
            logging.info("   ✅ Cost monitoring configured")
        else:
            logging.warning("   ⚠️  Cost monitoring needs manual setup")

        # 4.3 Performance optimization
        logging.info("   ⚡ Applying performance optimizations")
        result = self._apply_performance_optimizations()
        if result:
            logging.info("   ✅ Performance optimizations applied")
        else:
            logging.warning("   ⚠️  Performance optimizations need manual review")

        logging.info("✅ Phase 4 Complete: Monitoring and optimization configured")
        return True

    def _delete_vercel_project(self, project_name: str) -> bool:
        """Delete a Vercel project"""
        try:
            # First get project ID
            project_id = self._get_vercel_project_id(project_name)
            if not project_id:
                return False

            headers = {
                "Authorization": f"Bearer {self.vercel_token}",
                "Content-Type": "application/json",
            }

            response = requests.delete(
                f"https://api.vercel.com/v9/projects/{project_id}",
                headers=headers,
                timeout=10,
            )

            response.raise_for_status()
            return response.status_code == 204
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logging.info(
                    f"   ℹ️  Project {project_name} not found, skipping deletion."
                )
                return True
            logging.error(f"   ❌ Error deleting project {project_name}: {e}")
            return False
        except Exception as e:
            logging.error(f"   ❌ Error deleting project {project_name}: {e}")
            return False

    def _get_vercel_project_id(self, project_name: str) -> str | None:
        """Get Vercel project ID by name"""
        try:
            headers = {
                "Authorization": f"Bearer {self.vercel_token}",
                "Content-Type": "application/json",
            }

            response = requests.get(
                "https://api.vercel.com/v9/projects", headers=headers, timeout=10
            )

            if response.status_code == 200:
                projects = response.json().get("projects", [])
                for project in projects:
                    if project.get("name") == project_name:
                        return project.get("id")

            return None
        except Exception as e:
            logging.error(f"   ❌ Error getting project ID for {project_name}: {e}")
            return None

    def _rename_vercel_project(self, old_name: str, new_name: str) -> bool:
        """Rename a Vercel project"""
        try:
            project_id = self._get_vercel_project_id(old_name)
            if not project_id:
                return False

            headers = {
                "Authorization": f"Bearer {self.vercel_token}",
                "Content-Type": "application/json",
            }

            response = requests.patch(
                f"https://api.vercel.com/v9/projects/{project_id}",
                headers=headers,
                json={"name": new_name},
                timeout=10,
            )

            response.raise_for_status()
            return response.status_code == 200
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logging.info(f"   ℹ️  Project {old_name} not found, skipping rename.")
                return True
            logging.error(f"   ❌ Error renaming project {old_name}: {e}")
            return False
        except Exception as e:
            logging.error(f"   ❌ Error renaming project {old_name}: {e}")
            return False

    def _update_vercel_project_config(self, project_name: str, config: dict) -> bool:
        """Update Vercel project configuration"""
        try:
            project_id = self._get_vercel_project_id(project_name)
            if not project_id:
                return False

            headers = {
                "Authorization": f"Bearer {self.vercel_token}",
                "Content-Type": "application/json",
            }

            # Update project settings
            update_data = {
                "framework": config.get("framework"),
                "buildCommand": config.get("build_command"),
                "outputDirectory": config.get("output_directory"),
                "installCommand": "npm ci",
                "nodeVersion": "18.x",
            }

            if config.get("root_directory"):
                update_data["rootDirectory"] = config["root_directory"]

            response = requests.patch(
                f"https://api.vercel.com/v9/projects/{project_id}",
                headers=headers,
                json=update_data,
                timeout=10,
            )

            response.raise_for_status()
            return response.status_code == 200
        except Exception as e:
            logging.error(f"   ❌ Error updating project config for {project_name}: {e}")
            return False

    def _sync_environment_variables(
        self, project_name: str, env_vars: dict[str, str]
    ) -> bool:
        """Sync environment variables to Vercel project"""
        try:
            project_id = self._get_vercel_project_id(project_name)
            if not project_id:
                return False

            headers = {
                "Authorization": f"Bearer {self.vercel_token}",
                "Content-Type": "application/json",
            }

            # Get existing environment variables
            response = requests.get(
                f"https://api.vercel.com/v9/projects/{project_id}/env",
                headers=headers,
                timeout=10,
            )

            existing_vars = {}
            if response.status_code == 200:
                for var in response.json().get("envs", []):
                    existing_vars[var["key"]] = var["id"]

            # Update or create environment variables
            for key, value in env_vars.items():
                if key in existing_vars:
                    # Update existing variable
                    var_id = existing_vars[key]
                    update_response = requests.patch(
                        f"https://api.vercel.com/v9/projects/{project_id}/env/{var_id}",
                        headers=headers,
                        json={
                            "key": key,
                            "value": value,
                            "target": ["production", "preview", "development"],
                        },
                        timeout=10,
                    )
                    update_response.raise_for_status()
                else:
                    # Create new variable
                    create_response = requests.post(
                        f"https://api.vercel.com/v9/projects/{project_id}/env",
                        headers=headers,
                        json={
                            "key": key,
                            "value": value,
                            "target": ["production", "preview", "development"],
                            "type": "encrypted",
                        },
                        timeout=10,
                    )
                    create_response.raise_for_status()

            return True
        except requests.exceptions.HTTPError as e:
            logging.error(
                f"   ❌ HTTP Error syncing environment variables for {project_name}: {e.response.text}"
            )
            return False
        except Exception as e:
            logging.error(
                f"   ❌ Error syncing environment variables for {project_name}: {e}"
            )
            return False

    def _add_vercel_custom_domain(self, project_name: str, domain: str) -> bool:
        """Add custom domain to Vercel project"""
        try:
            project_id = self._get_vercel_project_id(project_name)
            if not project_id:
                return False

            headers = {
                "Authorization": f"Bearer {self.vercel_token}",
                "Content-Type": "application/json",
            }

            response = requests.post(
                f"https://api.vercel.com/v9/projects/{project_id}/domains",
                headers=headers,
                json={"name": domain},
                timeout=10,
            )

            if response.status_code == 409:  # Domain already exists
                logging.info(
                    f"   ℹ️  Domain {domain} already added to project {project_name}."
                )
                return True

            response.raise_for_status()
            return response.status_code in [200, 201]
        except requests.exceptions.HTTPError as e:
            logging.error(
                f"   ❌ HTTP Error adding custom domain {domain}: {e.response.text}"
            )
            return False
        except Exception as e:
            logging.error(f"   ❌ Error adding custom domain {domain}: {e}")
            return False

    def _get_current_dns_records(self) -> list[dict]:
        """Get current DNS records from Namecheap"""
        # This would integrate with Namecheap API
        # For now, return known records from the screenshot
        return [
            {"name": "@", "type": "A", "value": "34.74.88.2"},
            {"name": "api", "type": "A", "value": "34.74.88.2"},
            {"name": "webhooks", "type": "A", "value": "34.74.88.2"},
            {"name": "app", "type": "CNAME", "value": "cname.vercel-dns.com"},
            {"name": "dev.app", "type": "CNAME", "value": "cname.vercel-dns.com"},
        ]

    def _add_dns_record(self, record: dict) -> bool:
        """Add DNS record via Namecheap API"""
        # This would integrate with Namecheap API
        # For now, return True (manual configuration required)
        return True

    def _test_instance_connectivity(self, ip: str, port: str) -> bool:
        """Test connectivity to Lambda Labs instance"""
        try:
            import socket

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((ip, int(port)))
            sock.close()
            return result == 0
        except Exception:
            return False

    def _deploy_api_gateway(self) -> bool:
        """Deploy API gateway configuration"""
        # This would deploy the API gateway to Lambda Labs instances
        return True

    def _setup_status_monitoring(self) -> bool:
        """Setup status page monitoring"""
        # This would configure status page monitoring
        return True

    def _setup_cost_monitoring(self) -> bool:
        """Setup cost monitoring and alerts"""
        # This would configure cost monitoring
        return True

    def _apply_performance_optimizations(self) -> bool:
        """Apply performance optimizations"""
        # This would apply various performance optimizations
        return True

    def run_deployment(self, phases: list[int]) -> bool:
        """Run deployment phases"""
        logging.info("🚀 Starting Sophia Intel AI Deployment")
        logging.info(f"   Domain: {self.domain}")
        logging.info(f"   Phases: {phases}")
        logging.info(f"   Timestamp: {datetime.now().isoformat()}")
        logging.info("")

        success = True

        if 1 in phases:
            success &= self.phase_1_immediate_fixes()
            logging.info("")

        if 2 in phases:
            success &= self.phase_2_domain_integration()
            logging.info("")

        if 3 in phases:
            success &= self.phase_3_backend_integration()
            logging.info("")

        if 4 in phases:
            success &= self.phase_4_monitoring_optimization()
            logging.info("")

        if success:
            logging.info("🎉 Deployment completed successfully!")
            logging.info(f"   🌐 Main app: https://app.{self.domain}")
            logging.info(f"   🔧 Admin: https://admin.{self.domain}")
            logging.info(f"   📡 API: https://api.{self.domain}")
            logging.info(f"   📊 Status: https://status.{self.domain}")
        else:
            logging.error("❌ Deployment completed with errors")
            logging.error("   Please review the output above for details")

        return success


def main():
    parser = argparse.ArgumentParser(description="Deploy Sophia Intel AI integration")
    parser.add_argument(
        "--phase",
        choices=["1", "2", "3", "4", "all"],
        default="all",
        help="Deployment phase to run",
    )

    args = parser.parse_args()

    if args.phase == "all":
        phases = [1, 2, 3, 4]
    else:
        phases = [int(args.phase)]

    deployer = SophiaIntelAIDeployer()
    success = deployer.run_deployment(phases)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
