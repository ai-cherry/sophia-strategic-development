#!/usr/bin/env python3
"""
🔬 Simplified Integration Testing Framework

Tests core Sophia AI platform integrations without complex dependencies:
- Business Systems (HubSpot, Gong, Slack, Linear, Asana, Notion)
- Infrastructure (Lambda Labs, Local services)
- AI Services (OpenAI, Anthropic, Portkey)
- MCP Servers (Basic connectivity tests)
- Configuration and files
"""

import asyncio
import aiohttp
import json
import time
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimplifiedIntegrationTester:
    def __init__(self):
        self.start_time = datetime.now()
        self.test_results = {}
        self.integration_inventory = {}
        
    async def test_all_integrations(self):
        """Execute simplified integration testing"""
        print("🔬 Starting Simplified Integration Testing...")
        print("=" * 70)
        
        # Test categories
        test_categories = [
            ("Configuration", self.test_configuration),
            ("Local Services", self.test_local_services),
            ("Lambda Labs", self.test_lambda_labs),
            ("Databases", self.test_databases),
            ("AI Services", self.test_ai_services),
            ("Business Systems", self.test_business_systems),
            ("MCP Servers", self.test_mcp_servers),
            ("File Structure", self.test_file_structure),
            ("CLI Tools", self.test_cli_tools)
        ]
        
        for category, test_function in test_categories:
            print(f"\n🧪 Testing {category}...")
            try:
                start = time.time()
                results = await test_function()
                duration = time.time() - start
                
                self.test_results[category] = {
                    "results": results,
                    "duration": duration,
                    "status": "completed",
                    "tested_at": datetime.now().isoformat()
                }
                
                # Print immediate results
                total = len(results)
                healthy = len([r for r in results.values() if r.get('status') in ['healthy', 'available', 'configured']])
                print(f"   Results: {healthy}/{total} integrations operational ({healthy/total*100:.1f}%)")
                
            except Exception as e:
                self.test_results[category] = {
                    "status": "failed",
                    "error": str(e),
                    "tested_at": datetime.now().isoformat()
                }
                print(f"   ❌ {category} testing failed: {str(e)}")
        
        # Generate report
        return await self.generate_report()

    async def test_configuration(self) -> Dict[str, Any]:
        """Test configuration files and environment"""
        results = {}
        
        # Test environment variables
        required_env_vars = [
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY", 
            "QDRANT_API_KEY",
            "QDRANT_URL"
        ]
        
        for env_var in required_env_vars:
            value = os.getenv(env_var)
            if value:
                # Mask the value for security
                masked_value = value[:8] + "..." if len(value) > 8 else "***"
                results[f"env_{env_var}"] = {
                    "status": "configured",
                    "value_masked": masked_value,
                    "type": "environment"
                }
            else:
                results[f"env_{env_var}"] = {
                    "status": "missing",
                    "type": "environment"
                }
        
        # Test configuration files
        config_files = [
            "config/business_intelligence.json",
            "config/mcp_server_inventory.json",
            "frontend/src/config/environment.ts",
            ".sophia/config.json"
        ]
        
        for config_file in config_files:
            path = Path(config_file)
            if path.exists():
                try:
                    if config_file.endswith('.json'):
                        with open(path) as f:
                            data = json.load(f)
                        results[f"config_{path.name}"] = {
                            "status": "valid",
                            "size_bytes": path.stat().st_size,
                            "keys": len(data) if isinstance(data, dict) else "N/A",
                            "type": "config_file"
                        }
                    else:
                        results[f"config_{path.name}"] = {
                            "status": "exists",
                            "size_bytes": path.stat().st_size,
                            "type": "config_file"
                        }
                except Exception as e:
                    results[f"config_{path.name}"] = {
                        "status": "corrupted",
                        "error": str(e),
                        "type": "config_file"
                    }
            else:
                results[f"config_{path.name}"] = {
                    "status": "missing",
                    "type": "config_file"
                }
        
        return results

    async def test_local_services(self) -> Dict[str, Any]:
        """Test local services"""
        results = {}
        
        local_services = [
            ("backend", "http://localhost:8000/health", "Backend API"),
            ("frontend", "http://localhost:3000", "Frontend React App"),
            ("nginx", "http://localhost:80", "Nginx Proxy")
        ]
        
        for service_name, url, description in local_services:
            try:
                start_time = time.time()
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=3)) as session:
                    async with session.get(url) as resp:
                        response_time = (time.time() - start_time) * 1000
                        
                        if resp.status == 200:
                            results[service_name] = {
                                "status": "healthy",
                                "response_time": response_time,
                                "http_status": resp.status,
                                "description": description,
                                "type": "local_service"
                            }
                        else:
                            results[service_name] = {
                                "status": "degraded",
                                "response_time": response_time,
                                "http_status": resp.status,
                                "description": description,
                                "type": "local_service"
                            }
            except Exception as e:
                results[service_name] = {
                    "status": "unavailable",
                    "error": str(e),
                    "description": description,
                    "type": "local_service"
                }
        
        return results

    async def test_lambda_labs(self) -> Dict[str, Any]:
        """Test Lambda Labs infrastructure"""
        results = {}
        
        lambda_labs_servers = [
            ("192.222.58.232", "AI Core (GH200)"),
            ("104.171.202.103", "Production (RTX6000)"),
            ("104.171.202.117", "Business (A6000)"),
            ("104.171.202.134", "Data (A100)"),
            ("155.248.194.183", "Development (A10)")
        ]
        
        for ip, description in lambda_labs_servers:
            try:
                # Test basic connectivity with ping
                ping_result = subprocess.run(
                    ["ping", "-c", "1", "-W", "3000", ip],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if ping_result.returncode == 0:
                    # Try HTTP if ping succeeds
                    try:
                        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                            async with session.get(f"http://{ip}:8000/health") as resp:
                                if resp.status == 200:
                                    results[f"lambda_{ip}"] = {
                                        "status": "healthy",
                                        "description": description,
                                        "http_status": resp.status,
                                        "type": "lambda_labs"
                                    }
                                else:
                                    results[f"lambda_{ip}"] = {
                                        "status": "ping_only",
                                        "description": description,
                                        "note": "Network reachable but service unavailable",
                                        "type": "lambda_labs"
                                    }
                    except:
                        results[f"lambda_{ip}"] = {
                            "status": "ping_only",
                            "description": description,
                            "note": "Network reachable but HTTP unavailable",
                            "type": "lambda_labs"
                        }
                else:
                    results[f"lambda_{ip}"] = {
                        "status": "unreachable",
                        "description": description,
                        "type": "lambda_labs"
                    }
                    
            except Exception as e:
                results[f"lambda_{ip}"] = {
                    "status": "error",
                    "description": description,
                    "error": str(e),
                    "type": "lambda_labs"
                }
        
        return results

    async def test_databases(self) -> Dict[str, Any]:
        """Test database connections"""
        results = {}
        
        # Test Qdrant
        try:
            qdrant_url = os.getenv("QDRANT_URL", "https://cloud.qdrant.io")
            qdrant_api_key = os.getenv("QDRANT_API_KEY")
            
            if qdrant_api_key:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                    headers = {"api-key": qdrant_api_key}
                    async with session.get(f"{qdrant_url}/collections", headers=headers) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            results["qdrant"] = {
                                "status": "healthy",
                                "collections_count": len(data.get("result", {}).get("collections", [])),
                                "url": qdrant_url,
                                "type": "vector_database"
                            }
                        else:
                            results["qdrant"] = {
                                "status": "degraded",
                                "http_status": resp.status,
                                "url": qdrant_url,
                                "type": "vector_database"
                            }
            else:
                results["qdrant"] = {
                    "status": "not_configured",
                    "error": "No API key found",
                    "type": "vector_database"
                }
        except Exception as e:
            results["qdrant"] = {
                "status": "error",
                "error": str(e),
                "type": "vector_database"
            }
        
        # Test Redis (simple connection check)
        redis_available = False
        try:
            # Check if Redis port is responding
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=2)) as session:
                async with session.get("http://localhost:6379") as resp:
                    redis_available = True
        except:
            pass
        
        results["redis"] = {
            "status": "available" if redis_available else "unavailable",
            "type": "cache_database",
            "port": 6379
        }
        
        # Test PostgreSQL (check if port is responding)
        postgres_available = False
        try:
            # Simple connection test
            proc = subprocess.run(
                ["nc", "-z", "localhost", "5432"],
                capture_output=True,
                timeout=2
            )
            postgres_available = proc.returncode == 0
        except:
            pass
        
        results["postgresql"] = {
            "status": "available" if postgres_available else "unavailable",
            "type": "relational_database",
            "port": 5432
        }
        
        return results

    async def test_ai_services(self) -> Dict[str, Any]:
        """Test AI service configurations"""
        results = {}
        
        # OpenAI
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and openai_key.startswith("sk-"):
            results["openai"] = {
                "status": "configured",
                "key_format": "valid",
                "key_prefix": openai_key[:10] + "...",
                "type": "ai_service"
            }
        else:
            results["openai"] = {
                "status": "not_configured",
                "type": "ai_service"
            }
        
        # Anthropic
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key and anthropic_key.startswith("sk-ant-"):
            results["anthropic"] = {
                "status": "configured",
                "key_format": "valid",
                "key_prefix": anthropic_key[:15] + "...",
                "type": "ai_service"
            }
        else:
            results["anthropic"] = {
                "status": "not_configured",
                "type": "ai_service"
            }
        
        # Portkey (check if configured)
        portkey_key = os.getenv("PORTKEY_API_KEY")
        if portkey_key:
            results["portkey"] = {
                "status": "configured",
                "type": "ai_service"
            }
        else:
            results["portkey"] = {
                "status": "not_configured",
                "type": "ai_service"
            }
        
        return results

    async def test_business_systems(self) -> Dict[str, Any]:
        """Test business system integrations via MCP servers"""
        results = {}
        
        business_systems = [
            ("hubspot", 9103, "HubSpot CRM"),
            ("gong", 9002, "Gong.io Call Intelligence"),
            ("slack", 9101, "Slack Communication"),
            ("linear", 9004, "Linear Project Management"),
            ("asana", 9006, "Asana Task Management"),
            ("notion", 9102, "Notion Knowledge Base"),
            ("github", 9003, "GitHub Code Management")
        ]
        
        for system_name, port, description in business_systems:
            try:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=2)) as session:
                    async with session.get(f"http://localhost:{port}/health") as resp:
                        if resp.status == 200:
                            results[system_name] = {
                                "status": "healthy",
                                "port": port,
                                "description": description,
                                "type": "business_system"
                            }
                        else:
                            results[system_name] = {
                                "status": "degraded",
                                "port": port,
                                "http_status": resp.status,
                                "description": description,
                                "type": "business_system"
                            }
            except Exception as e:
                results[system_name] = {
                    "status": "unavailable",
                    "port": port,
                    "error": str(e),
                    "description": description,
                    "type": "business_system"
                }
        
        return results

    async def test_mcp_servers(self) -> Dict[str, Any]:
        """Test MCP server connectivity"""
        results = {}
        
        mcp_servers = [
            ("ai_memory", 9000, "AI Memory Service"),
            ("codacy", 3008, "Code Quality Analysis"),
            ("lambda_labs_cli", 9020, "Lambda Labs CLI"),
            ("portkey_admin", 9013, "Portkey Admin")
        ]
        
        for server_name, port, description in mcp_servers:
            try:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=2)) as session:
                    async with session.get(f"http://localhost:{port}/health") as resp:
                        if resp.status == 200:
                            results[server_name] = {
                                "status": "healthy",
                                "port": port,
                                "description": description,
                                "type": "mcp_server"
                            }
                        else:
                            results[server_name] = {
                                "status": "degraded",
                                "port": port,
                                "http_status": resp.status,
                                "description": description,
                                "type": "mcp_server"
                            }
            except Exception as e:
                results[server_name] = {
                    "status": "unavailable",
                    "port": port,
                    "error": str(e),
                    "description": description,
                    "type": "mcp_server"
                }
        
        return results

    async def test_file_structure(self) -> Dict[str, Any]:
        """Test file structure and key directories"""
        results = {}
        
        key_directories = [
            ("backend", "Backend Python code"),
            ("frontend", "React frontend"),
            ("mcp-servers", "MCP server implementations"),
            ("external", "External repository collection"),
            ("config", "Configuration files"),
            ("scripts", "Utility scripts"),
            ("docs", "Documentation")
        ]
        
        for dir_name, description in key_directories:
            path = Path(dir_name)
            if path.exists() and path.is_dir():
                file_count = len(list(path.rglob("*")))
                results[dir_name] = {
                    "status": "exists",
                    "file_count": file_count,
                    "description": description,
                    "type": "directory"
                }
            else:
                results[dir_name] = {
                    "status": "missing",
                    "description": description,
                    "type": "directory"
                }
        
        # Test specific important files
        important_files = [
            ("backend/app/working_fastapi.py", "Main FastAPI application"),
            ("frontend/src/config/environment.ts", "Frontend configuration"),
            ("backend/core/auto_esc_config.py", "Secret management"),
            ("README.md", "Main documentation")
        ]
        
        for file_path, description in important_files:
            path = Path(file_path)
            if path.exists():
                results[f"file_{path.name}"] = {
                    "status": "exists",
                    "size_bytes": path.stat().st_size,
                    "description": description,
                    "type": "file"
                }
            else:
                results[f"file_{path.name}"] = {
                    "status": "missing",
                    "description": description,
                    "type": "file"
                }
        
        return results

    async def test_cli_tools(self) -> Dict[str, Any]:
        """Test CLI tool availability"""
        results = {}
        
        cli_tools = [
            ("git", ["git", "--version"], "Git version control"),
            ("python", ["python", "--version"], "Python interpreter"),
            ("node", ["node", "--version"], "Node.js runtime"),
            ("docker", ["docker", "--version"], "Docker containerization"),
            ("kubectl", ["kubectl", "version", "--client"], "Kubernetes CLI")
        ]
        
        for tool_name, command, description in cli_tools:
            try:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=3
                )
                
                if result.returncode == 0:
                    version_output = result.stdout.strip().split('\n')[0]  # First line only
                    results[tool_name] = {
                        "status": "available",
                        "version": version_output,
                        "description": description,
                        "type": "cli_tool"
                    }
                else:
                    results[tool_name] = {
                        "status": "error",
                        "error": result.stderr.strip(),
                        "description": description,
                        "type": "cli_tool"
                    }
            except FileNotFoundError:
                results[tool_name] = {
                    "status": "not_installed",
                    "description": description,
                    "type": "cli_tool"
                }
            except Exception as e:
                results[tool_name] = {
                    "status": "error",
                    "error": str(e),
                    "description": description,
                    "type": "cli_tool"
                }
        
        return results

    async def generate_report(self) -> Dict[str, Any]:
        """Generate final integration report"""
        total_duration = (datetime.now() - self.start_time).total_seconds()
        
        # Calculate statistics
        all_results = {}
        for category_data in self.test_results.values():
            if "results" in category_data:
                all_results.update(category_data["results"])
        
        total_integrations = len(all_results)
        healthy_integrations = len([r for r in all_results.values() if r.get("status") in ["healthy", "available", "configured", "exists"]])
        degraded_integrations = len([r for r in all_results.values() if r.get("status") in ["degraded", "ping_only"]])
        unavailable_integrations = len([r for r in all_results.values() if r.get("status") in ["unavailable", "error", "missing", "not_configured", "not_installed"]])
        
        # Create final report
        report = {
            "test_metadata": {
                "test_started": self.start_time.isoformat(),
                "test_completed": datetime.now().isoformat(),
                "total_duration_seconds": total_duration,
                "test_framework": "simplified_integration_tester_v1.0"
            },
            "executive_summary": {
                "total_integrations_tested": total_integrations,
                "healthy_integrations": healthy_integrations,
                "degraded_integrations": degraded_integrations,
                "unavailable_integrations": unavailable_integrations,
                "overall_health_percentage": (healthy_integrations / total_integrations * 100) if total_integrations > 0 else 0,
                "platform_status": self._determine_status(healthy_integrations, total_integrations)
            },
            "detailed_results": self.test_results,
            "integration_summary": self._generate_integration_summary(),
            "critical_issues": self._identify_critical_issues(),
            "recommendations": self._generate_recommendations()
        }
        
        # Save report
        report_filename = f"integration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 Integration Report Generated: {report_filename}")
        return report

    def _determine_status(self, healthy: int, total: int) -> str:
        """Determine overall platform status"""
        if total == 0:
            return "unknown"
        
        percentage = (healthy / total) * 100
        if percentage >= 85:
            return "excellent"
        elif percentage >= 70:
            return "good"
        elif percentage >= 50:
            return "fair"
        else:
            return "needs_attention"

    def _generate_integration_summary(self) -> Dict[str, Any]:
        """Generate integration summary by type"""
        summary = {}
        
        for category, data in self.test_results.items():
            if "results" in data:
                results = data["results"]
                by_type = {}
                
                for integration, details in results.items():
                    int_type = details.get("type", "unknown")
                    if int_type not in by_type:
                        by_type[int_type] = {"total": 0, "healthy": 0}
                    
                    by_type[int_type]["total"] += 1
                    if details.get("status") in ["healthy", "available", "configured", "exists"]:
                        by_type[int_type]["healthy"] += 1
                
                summary[category] = by_type
        
        return summary

    def _identify_critical_issues(self) -> List[Dict[str, Any]]:
        """Identify critical integration issues"""
        issues = []
        
        # Check for critical missing configurations
        if "Configuration" in self.test_results:
            config_results = self.test_results["Configuration"]["results"]
            
            critical_env_vars = ["env_OPENAI_API_KEY", "env_ANTHROPIC_API_KEY", "env_QDRANT_API_KEY"]
            for env_var in critical_env_vars:
                if env_var in config_results and config_results[env_var].get("status") == "missing":
                    issues.append({
                        "category": "Configuration",
                        "issue": f"Missing critical environment variable: {env_var}",
                        "severity": "high"
                    })
        
        # Check for infrastructure issues
        if "Lambda Labs" in self.test_results:
            lambda_results = self.test_results["Lambda Labs"]["results"]
            unreachable_count = len([r for r in lambda_results.values() if r.get("status") == "unreachable"])
            
            if unreachable_count > 2:
                issues.append({
                    "category": "Infrastructure", 
                    "issue": f"{unreachable_count} Lambda Labs servers unreachable",
                    "severity": "medium"
                })
        
        # Check for database connectivity
        if "Databases" in self.test_results:
            db_results = self.test_results["Databases"]["results"]
            if db_results.get("qdrant", {}).get("status") not in ["healthy", "available"]:
                issues.append({
                    "category": "Databases",
                    "issue": "Qdrant vector database unavailable",
                    "severity": "high"
                })
        
        return issues

    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Analyze results and provide specific recommendations
        critical_issues = self._identify_critical_issues()
        
        if any(issue["severity"] == "high" for issue in critical_issues):
            recommendations.append("Address critical configuration issues before proceeding with deployment")
        
        if "Local Services" in self.test_results:
            local_results = self.test_results["Local Services"]["results"]
            if local_results.get("backend", {}).get("status") != "healthy":
                recommendations.append("Start the backend service: python backend/app/working_fastapi.py")
        
        if "AI Services" in self.test_results:
            ai_results = self.test_results["AI Services"]["results"]
            if ai_results.get("openai", {}).get("status") != "configured":
                recommendations.append("Configure OpenAI API key for AI functionality")
            if ai_results.get("anthropic", {}).get("status") != "configured":
                recommendations.append("Configure Anthropic API key for Claude integration")
        
        recommendations.append("Review detailed results in the generated JSON report for specific issues")
        
        return recommendations

async def main():
    """Main execution function"""
    tester = SimplifiedIntegrationTester()
    
    try:
        report = await tester.test_all_integrations()
        
        # Print final summary
        print("\n" + "="*70)
        print("🎯 SOPHIA AI INTEGRATION TEST RESULTS")
        print("="*70)
        
        summary = report["executive_summary"]
        print(f"📊 Total Integrations: {summary['total_integrations_tested']}")
        print(f"✅ Healthy: {summary['healthy_integrations']}")
        print(f"⚠️  Degraded: {summary['degraded_integrations']}")
        print(f"❌ Unavailable: {summary['unavailable_integrations']}")
        print(f"📈 Health Score: {summary['overall_health_percentage']:.1f}%")
        print(f"🏆 Status: {summary['platform_status'].upper()}")
        
        # Print integration summary
        print(f"\n📋 Integration Summary:")
        for category, types in report["integration_summary"].items():
            print(f"   {category}:")
            for int_type, stats in types.items():
                print(f"     {int_type}: {stats['healthy']}/{stats['total']} healthy")
        
        # Print critical issues
        issues = report["critical_issues"]
        if issues:
            print(f"\n🚨 Critical Issues:")
            for issue in issues:
                print(f"   • {issue['issue']} (Severity: {issue['severity']})")
        
        # Print recommendations
        recommendations = report["recommendations"]
        if recommendations:
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
        
        return report
        
    except Exception as e:
        logger.error(f"Integration testing failed: {str(e)}")
        print(f"❌ Integration testing failed: {str(e)}")
        return None

if __name__ == "__main__":
    asyncio.run(main()) 