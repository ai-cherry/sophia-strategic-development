#!/usr/bin/env python3
"""Comprehensive assessment of core coding infrastructure."""

import os
import sys
import json
import subprocess
import asyncio
import aiohttp
from pathlib import Path
from typing import Dict, List, Any
import logging

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InfrastructureAssessment:
    def __init__(self):
        self.results = {
            "pulumi_esc": {"status": "unknown", "details": {}},
            "github_secrets": {"status": "unknown", "details": {}},
            "docker": {"status": "unknown", "details": {}},
            "kubernetes": {"status": "unknown", "details": {}},
            "lambda_labs": {"status": "unknown", "details": {}},
            "vercel": {"status": "unknown", "details": {}},
            "snowflake": {"status": "unknown", "details": {}},
            "estuary": {"status": "unknown", "details": {}},
            "mcp_servers": {"status": "unknown", "details": {}},
            "code_protection": {"status": "unknown", "details": {}}
        }

    def assess_pulumi_esc(self):
        """Assess Pulumi ESC connectivity and secrets."""
        logger.info("Assessing Pulumi ESC...")
        try:
            from backend.core.auto_esc_config import get_config_value, config
            
            # Test critical secrets
            critical_secrets = [
                "openai_api_key", "anthropic_api_key", "github_token",
                "snowflake_account", "snowflake_user", "snowflake_password",
                "lambda_labs_api_key", "vercel_token", "estuary_access_token"
            ]
            
            available_secrets = {}
            for secret in critical_secrets:
                value = get_config_value(secret)
                available_secrets[secret] = bool(value)
            
            # Count total secrets
            total_secrets = len(config._config) if hasattr(config, '_config') and config._config else 0
            
            self.results["pulumi_esc"] = {
                "status": "connected" if total_secrets > 0 else "disconnected",
                "details": {
                    "total_secrets": total_secrets,
                    "critical_secrets": available_secrets,
                    "missing_critical": [k for k, v in available_secrets.items() if not v]
                }
            }
        except Exception as e:
            self.results["pulumi_esc"] = {
                "status": "error",
                "details": {"error": str(e)}
            }

    def assess_docker(self):
        """Assess Docker availability and functionality."""
        logger.info("Assessing Docker...")
        try:
            # Check if Docker is running
            result = subprocess.run(["docker", "version"], capture_output=True, text=True)
            if result.returncode == 0:
                # Check Docker Compose
                compose_result = subprocess.run(["docker", "compose", "version"], capture_output=True, text=True)
                
                self.results["docker"] = {
                    "status": "available",
                    "details": {
                        "docker_version": result.stdout.split('\n')[1] if result.stdout else "unknown",
                        "compose_available": compose_result.returncode == 0
                    }
                }
            else:
                self.results["docker"] = {
                    "status": "unavailable",
                    "details": {"error": result.stderr}
                }
        except Exception as e:
            self.results["docker"] = {
                "status": "error",
                "details": {"error": str(e)}
            }

    def assess_kubernetes(self):
        """Assess Kubernetes connectivity."""
        logger.info("Assessing Kubernetes...")
        try:
            # Check kubectl
            result = subprocess.run(["kubectl", "cluster-info"], capture_output=True, text=True)
            if result.returncode == 0:
                # Check nodes
                nodes_result = subprocess.run(["kubectl", "get", "nodes"], capture_output=True, text=True)
                
                self.results["kubernetes"] = {
                    "status": "connected",
                    "details": {
                        "cluster_info": result.stdout,
                        "nodes_available": nodes_result.returncode == 0
                    }
                }
            else:
                self.results["kubernetes"] = {
                    "status": "disconnected",
                    "details": {"error": result.stderr}
                }
        except Exception as e:
            self.results["kubernetes"] = {
                "status": "not_available",
                "details": {"error": str(e)}
            }

    async def assess_lambda_labs(self):
        """Assess Lambda Labs API connectivity."""
        logger.info("Assessing Lambda Labs...")
        try:
            from backend.core.auto_esc_config import get_config_value
            api_key = get_config_value("lambda_labs_api_key")
            
            if not api_key:
                self.results["lambda_labs"] = {
                    "status": "no_credentials",
                    "details": {"error": "Missing API key"}
                }
                return
            
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {api_key}"}
                async with session.get("https://cloud.lambdalabs.com/api/v1/instances", headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.results["lambda_labs"] = {
                            "status": "connected",
                            "details": {
                                "instances": len(data.get("data", [])),
                                "api_accessible": True
                            }
                        }
                    else:
                        self.results["lambda_labs"] = {
                            "status": "api_error",
                            "details": {"status_code": response.status}
                        }
        except Exception as e:
            self.results["lambda_labs"] = {
                "status": "error",
                "details": {"error": str(e)}
            }

    async def assess_vercel(self):
        """Assess Vercel API connectivity."""
        logger.info("Assessing Vercel...")
        try:
            from backend.core.auto_esc_config import get_config_value
            token = get_config_value("vercel_token")
            
            if not token:
                self.results["vercel"] = {
                    "status": "no_credentials",
                    "details": {"error": "Missing token"}
                }
                return
            
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {token}"}
                async with session.get("https://api.vercel.com/v2/user", headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.results["vercel"] = {
                            "status": "connected",
                            "details": {
                                "user": data.get("user", {}).get("username"),
                                "api_accessible": True
                            }
                        }
                    else:
                        self.results["vercel"] = {
                            "status": "api_error",
                            "details": {"status_code": response.status}
                        }
        except Exception as e:
            self.results["vercel"] = {
                "status": "error",
                "details": {"error": str(e)}
            }

    def assess_snowflake(self):
        """Assess Snowflake connectivity."""
        logger.info("Assessing Snowflake...")
        try:
            from backend.core.auto_esc_config import get_config_value
            
            snowflake_config = {
                "account": get_config_value("snowflake_account"),
                "user": get_config_value("snowflake_user"),
                "password": get_config_value("snowflake_password"),
                "warehouse": get_config_value("snowflake_warehouse"),
                "database": get_config_value("snowflake_database"),
                "role": get_config_value("snowflake_role")
            }
            
            missing = [k for k, v in snowflake_config.items() if not v]
            
            if not missing:
                # Try actual connection
                try:
                    import snowflake.connector
                    conn = snowflake.connector.connect(
                        account=snowflake_config["account"],
                        user=snowflake_config["user"],
                        password=snowflake_config["password"],
                        warehouse=snowflake_config["warehouse"],
                        database=snowflake_config["database"],
                        role=snowflake_config["role"]
                    )
                    cursor = conn.cursor()
                    cursor.execute("SELECT CURRENT_VERSION()")
                    result = cursor.fetchone()
                    version = result[0] if result else "unknown"
                    conn.close()
                    
                    self.results["snowflake"] = {
                        "status": "connected",
                        "details": {
                            "version": version,
                            "all_config_present": True
                        }
                    }
                except Exception as conn_error:
                    self.results["snowflake"] = {
                        "status": "connection_failed",
                        "details": {
                            "error": str(conn_error),
                            "all_config_present": True
                        }
                    }
            else:
                self.results["snowflake"] = {
                    "status": "missing_config",
                    "details": {"missing_fields": missing}
                }
        except Exception as e:
            self.results["snowflake"] = {
                "status": "error",
                "details": {"error": str(e)}
            }

    def assess_mcp_servers(self):
        """Assess MCP server configurations and health."""
        logger.info("Assessing MCP servers...")
        try:
            mcp_servers_dir = Path("mcp-servers")
            if not mcp_servers_dir.exists():
                self.results["mcp_servers"] = {
                    "status": "directory_missing",
                    "details": {"error": "mcp-servers directory not found"}
                }
                return
            
            # Key coding-related MCP servers
            critical_servers = [
                "ai_memory", "codacy", "github", "linear", "notion",
                "snowflake", "sophia_ai_intelligence"
            ]
            
            server_status = {}
            for server in critical_servers:
                server_dir = mcp_servers_dir / server
                if server_dir.exists():
                    # Check for main server file
                    server_files = list(server_dir.glob("*_mcp_server.py"))
                    if server_files:
                        server_status[server] = {
                            "directory_exists": True,
                            "server_file_exists": True,
                            "server_file": str(server_files[0])
                        }
                    else:
                        server_status[server] = {
                            "directory_exists": True,
                            "server_file_exists": False
                        }
                else:
                    server_status[server] = {
                        "directory_exists": False,
                        "server_file_exists": False
                    }
            
            working_servers = sum(1 for s in server_status.values() if s.get("server_file_exists"))
            
            self.results["mcp_servers"] = {
                "status": "assessed",
                "details": {
                    "total_critical_servers": len(critical_servers),
                    "working_servers": working_servers,
                    "server_status": server_status
                }
            }
        except Exception as e:
            self.results["mcp_servers"] = {
                "status": "error",
                "details": {"error": str(e)}
            }

    def assess_code_protection(self):
        """Assess code protection and automation capabilities."""
        logger.info("Assessing code protection...")
        try:
            # Check for GitHub Actions workflows
            workflows_dir = Path(".github/workflows")
            workflows = []
            if workflows_dir.exists():
                workflows = [f.name for f in workflows_dir.glob("*.yml")]
            
            # Check for pre-commit hooks
            precommit_exists = Path(".pre-commit-config.yaml").exists()
            
            # Check for code quality tools
            quality_tools = {
                "ruff": subprocess.run(["which", "ruff"], capture_output=True).returncode == 0,
                "black": subprocess.run(["which", "black"], capture_output=True).returncode == 0,
                "mypy": subprocess.run(["which", "mypy"], capture_output=True).returncode == 0
            }
            
            self.results["code_protection"] = {
                "status": "assessed",
                "details": {
                    "github_workflows": workflows,
                    "precommit_hooks": precommit_exists,
                    "quality_tools": quality_tools
                }
            }
        except Exception as e:
            self.results["code_protection"] = {
                "status": "error",
                "details": {"error": str(e)}
            }

    async def run_assessment(self):
        """Run complete infrastructure assessment."""
        logger.info("Starting comprehensive infrastructure assessment...")
        
        # Synchronous assessments
        self.assess_pulumi_esc()
        self.assess_docker()
        self.assess_kubernetes()
        self.assess_snowflake()
        self.assess_mcp_servers()
        self.assess_code_protection()
        
        # Asynchronous assessments
        await self.assess_lambda_labs()
        await self.assess_vercel()
        
        return self.results

    def generate_report(self):
        """Generate comprehensive assessment report."""
        report = {
            "assessment_summary": {
                "timestamp": "2024-01-15",
                "total_components": len(self.results),
                "healthy_components": sum(1 for r in self.results.values() if r["status"] in ["connected", "available", "assessed"]),
                "critical_issues": []
            },
            "detailed_results": self.results,
            "recommendations": []
        }
        
        # Generate recommendations based on results
        if self.results["pulumi_esc"]["status"] != "connected":
            report["recommendations"].append("CRITICAL: Fix Pulumi ESC connectivity - all secrets depend on this")
        
        if self.results["docker"]["status"] != "available":
            report["recommendations"].append("HIGH: Install/start Docker for MCP server deployment")
        
        if self.results["mcp_servers"]["details"].get("working_servers", 0) < 3:
            report["recommendations"].append("HIGH: Fix MCP server configurations for core development workflow")
        
        return report

async def main():
    """Main assessment function."""
    assessment = InfrastructureAssessment()
    results = await assessment.run_assessment()
    report = assessment.generate_report()
    
    # Save results
    with open("infrastructure_assessment_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("\n=== INFRASTRUCTURE ASSESSMENT COMPLETE ===")
    print(f"Healthy Components: {report['assessment_summary']['healthy_components']}/{report['assessment_summary']['total_components']}")
    
    if report["recommendations"]:
        print("\nCRITICAL RECOMMENDATIONS:")
        for rec in report["recommendations"]:
            print(f"  - {rec}")
    
    print(f"\nFull report saved to: infrastructure_assessment_report.json")
    
    return report

if __name__ == "__main__":
    asyncio.run(main()) 