#!/usr/bin/env python3
"""
🔬 Comprehensive Integration Testing Framework

Tests all Sophia AI platform integrations and generates detailed report:
- Business Systems (HubSpot, Gong, Slack, Linear, Asana, Notion)
- Infrastructure (Lambda Labs, PostgreSQL, Redis, Qdrant)
- AI Services (Portkey, OpenRouter, Anthropic, OpenAI)
- Development Tools (GitHub, Figma, Codacy)
- MCP Servers (40+ servers across multiple categories)
- External repositories and CLI tools
"""

import asyncio
import aiohttp
import json
import time
import os
import subprocess
import psutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveIntegrationTester:
    def __init__(self):
        self.start_time = datetime.now()
        self.test_results = {}
        self.integration_inventory = {}
        self.performance_metrics = {}
        self.error_log = []
        
    async def test_all_integrations(self):
        """Execute comprehensive integration testing"""
        print("🔬 Starting Comprehensive Integration Testing...")
        print("=" * 70)
        
        # Initialize inventory
        await self.discover_all_integrations()
        
        # Test categories in order of dependency
        test_categories = [
            ("Infrastructure", self.test_infrastructure_integrations),
            ("Database", self.test_database_integrations),
            ("Business Systems", self.test_business_integrations),
            ("AI Services", self.test_ai_service_integrations),
            ("MCP Servers", self.test_mcp_integrations),
            ("Development Tools", self.test_development_integrations),
            ("External Repositories", self.test_external_integrations),
            ("CLI Tools", self.test_cli_integrations),
            ("API Endpoints", self.test_api_integrations),
            ("Real-time Services", self.test_realtime_integrations)
        ]
        
        for category, test_function in test_categories:
            print(f"\n🧪 Testing {category} Integrations...")
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
                passed = len([r for r in results.values() if r.get('status') == 'healthy'])
                print(f"   Results: {passed}/{total} integrations healthy ({passed/total*100:.1f}%)")
                
            except Exception as e:
                self.test_results[category] = {
                    "status": "failed",
                    "error": str(e),
                    "tested_at": datetime.now().isoformat()
                }
                self.error_log.append(f"{category}: {str(e)}")
                print(f"   ❌ {category} testing failed: {str(e)}")
        
        # Generate comprehensive report
        return await self.generate_final_report()

    async def discover_all_integrations(self):
        """Discover all integrations from configuration files and codebase"""
        print("🔍 Discovering all platform integrations...")
        
        # Load MCP server inventory
        mcp_config_file = Path("config/mcp_server_inventory.json")
        if mcp_config_file.exists():
            with open(mcp_config_file) as f:
                mcp_data = json.load(f)
                self.integration_inventory["mcp_servers"] = mcp_data
        
        # Load business intelligence config
        bi_config_file = Path("config/business_intelligence.json")
        if bi_config_file.exists():
            with open(bi_config_file) as f:
                bi_data = json.load(f)
                self.integration_inventory["business_intelligence"] = bi_data
        
        # Load platform integration matrix
        platform_config_file = Path("docs/PLATFORM_INTEGRATION_MATRIX.json")
        if platform_config_file.exists():
            with open(platform_config_file) as f:
                platform_data = json.load(f)
                self.integration_inventory["platform_matrix"] = platform_data
        
        # Discover from environment configuration
        try:
            from backend.core.auto_esc_config import get_config_value
            self.integration_inventory["esc_config"] = "available"
        except:
            self.integration_inventory["esc_config"] = "unavailable"
        
        # Count external repositories
        external_dir = Path("external")
        if external_dir.exists():
            external_repos = [d.name for d in external_dir.iterdir() if d.is_dir()]
            self.integration_inventory["external_repositories"] = external_repos
        
        print(f"   Discovered: {len(self.integration_inventory)} integration categories")

    async def test_infrastructure_integrations(self) -> Dict[str, Any]:
        """Test core infrastructure integrations"""
        results = {}
        
        # Lambda Labs Infrastructure
        lambda_labs_ips = [
            "192.222.58.232",  # AI Core (GH200)
            "104.171.202.103", # Production (RTX6000)
            "104.171.202.117", # Business (A6000)
            "104.171.202.134", # Data (A100)
            "155.248.194.183"  # Development (A10)
        ]
        
        for ip in lambda_labs_ips:
            try:
                # Test basic connectivity
                start_time = time.time()
                
                # Try to ping the server
                ping_result = subprocess.run(
                    ["ping", "-c", "1", "-W", "3000", ip],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                response_time = (time.time() - start_time) * 1000
                
                if ping_result.returncode == 0:
                    # Try HTTP connection
                    try:
                        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                            async with session.get(f"http://{ip}:8000/health") as resp:
                                if resp.status == 200:
                                    data = await resp.json()
                                    results[f"lambda_labs_{ip}"] = {
                                        "status": "healthy",
                                        "response_time": response_time,
                                        "http_status": resp.status,
                                        "services": data.get("services", {}),
                                        "type": "infrastructure"
                                    }
                                else:
                                    results[f"lambda_labs_{ip}"] = {
                                        "status": "degraded",
                                        "response_time": response_time,
                                        "http_status": resp.status,
                                        "type": "infrastructure"
                                    }
                    except:
                        results[f"lambda_labs_{ip}"] = {
                            "status": "ping_only",
                            "response_time": response_time,
                            "note": "Network accessible but HTTP service unavailable",
                            "type": "infrastructure"
                        }
                else:
                    results[f"lambda_labs_{ip}"] = {
                        "status": "unreachable",
                        "response_time": None,
                        "type": "infrastructure"
                    }
                    
            except Exception as e:
                results[f"lambda_labs_{ip}"] = {
                    "status": "error",
                    "error": str(e),
                    "type": "infrastructure"
                }
        
        # Test local services
        local_services = [
            ("backend", "http://localhost:8000/health"),
            ("frontend", "http://localhost:3000"),
            ("nginx", "http://localhost:80"),
        ]
        
        for service_name, url in local_services:
            try:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=3)) as session:
                    start_time = time.time()
                    async with session.get(url) as resp:
                        response_time = (time.time() - start_time) * 1000
                        results[f"local_{service_name}"] = {
                            "status": "healthy" if resp.status == 200 else "degraded",
                            "response_time": response_time,
                            "http_status": resp.status,
                            "type": "local_service"
                        }
            except Exception as e:
                results[f"local_{service_name}"] = {
                    "status": "unavailable",
                    "error": str(e),
                    "type": "local_service"
                }
        
        return results

    async def test_database_integrations(self) -> Dict[str, Any]:
        """Test database and storage integrations"""
        results = {}
        
        # PostgreSQL
        try:
            import psycopg2
            
            # Test connection
            conn_params = {
                "host": os.getenv("POSTGRES_HOST", "localhost"),
                "port": os.getenv("POSTGRES_PORT", "5432"),
                "database": os.getenv("POSTGRES_DB", "sophia_ai"),
                "user": os.getenv("POSTGRES_USER", "postgres"),
                "password": os.getenv("POSTGRES_PASSWORD", "")
            }
            
            start_time = time.time()
            conn = psycopg2.connect(**conn_params)
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            response_time = (time.time() - start_time) * 1000
            
            cursor.close()
            conn.close()
            
            results["postgresql"] = {
                "status": "healthy",
                "response_time": response_time,
                "version": version[0] if version else None,
                "type": "database"
            }
            
        except Exception as e:
            results["postgresql"] = {
                "status": "unavailable",
                "error": str(e),
                "type": "database"
            }
        
        # Redis
        try:
            import redis
            
            start_time = time.time()
            r = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", "6379")),
                decode_responses=True
            )
            
            # Test basic operations
            r.ping()
            info = r.info()
            response_time = (time.time() - start_time) * 1000
            
            results["redis"] = {
                "status": "healthy",
                "response_time": response_time,
                "version": info.get("redis_version"),
                "memory_usage": info.get("used_memory_human"),
                "type": "cache"
            }
            
        except Exception as e:
            results["redis"] = {
                "status": "unavailable",
                "error": str(e),
                "type": "cache"
            }
        
        # Qdrant Vector Database
        try:
            from qdrant_client import QdrantClient
            
            qdrant_url = os.getenv("QDRANT_URL", "https://cloud.qdrant.io")
            qdrant_api_key = os.getenv("QDRANT_API_KEY")
            
            if qdrant_api_key:
                start_time = time.time()
                client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
                
                # Test connection and get collections
                collections = client.get_collections()
                response_time = (time.time() - start_time) * 1000
                
                results["qdrant"] = {
                    "status": "healthy",
                    "response_time": response_time,
                    "collections_count": len(collections.collections),
                    "collections": [c.name for c in collections.collections],
                    "type": "vector_database"
                }
            else:
                results["qdrant"] = {
                    "status": "misconfigured",
                    "error": "No API key configured",
                    "type": "vector_database"
                }
                
        except Exception as e:
            results["qdrant"] = {
                "status": "unavailable",
                "error": str(e),
                "type": "vector_database"
            }
        
        return results

    async def test_business_integrations(self) -> Dict[str, Any]:
        """Test business system integrations"""
        results = {}
        
        business_systems = [
            ("hubspot", "HubSpot CRM"),
            ("gong", "Gong.io Call Intelligence"),
            ("slack", "Slack Communication"),
            ("linear", "Linear Project Management"),
            ("asana", "Asana Task Management"),
            ("notion", "Notion Knowledge Base"),
            ("github", "GitHub Code Management")
        ]
        
        for system_id, system_name in business_systems:
            try:
                # Test via backend API if available
                url = f"http://localhost:8000/api/v1/integrations/{system_id}/status"
                
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                    start_time = time.time()
                    async with session.get(url) as resp:
                        response_time = (time.time() - start_time) * 1000
                        
                        if resp.status == 200:
                            data = await resp.json()
                            results[system_id] = {
                                "status": "healthy",
                                "response_time": response_time,
                                "integration_data": data,
                                "name": system_name,
                                "type": "business_system"
                            }
                        else:
                            results[system_id] = {
                                "status": "degraded",
                                "response_time": response_time,
                                "http_status": resp.status,
                                "name": system_name,
                                "type": "business_system"
                            }
                            
            except Exception as e:
                # Test direct MCP server if backend unavailable
                try:
                    mcp_port = self.get_mcp_port(system_id)
                    if mcp_port:
                        url = f"http://localhost:{mcp_port}/health"
                        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=3)) as session:
                            async with session.get(url) as resp:
                                if resp.status == 200:
                                    results[system_id] = {
                                        "status": "mcp_only",
                                        "mcp_port": mcp_port,
                                        "name": system_name,
                                        "type": "business_system"
                                    }
                                else:
                                    raise Exception("MCP server unhealthy")
                    else:
                        raise Exception("No MCP port found")
                        
                except:
                    results[system_id] = {
                        "status": "unavailable",
                        "error": str(e),
                        "name": system_name,
                        "type": "business_system"
                    }
        
        return results

    async def test_ai_service_integrations(self) -> Dict[str, Any]:
        """Test AI service integrations"""
        results = {}
        
        ai_services = [
            ("openai", "OpenAI API"),
            ("anthropic", "Anthropic Claude API"),
            ("portkey", "Portkey LLM Gateway"),
            ("openrouter", "OpenRouter Model Access"),
            ("lambda_labs_gpu", "Lambda Labs GPU Services")
        ]
        
        for service_id, service_name in ai_services:
            try:
                # Test via configuration
                if service_id == "openai":
                    api_key = os.getenv("OPENAI_API_KEY")
                    if api_key and api_key.startswith("sk-"):
                        results[service_id] = {
                            "status": "configured",
                            "key_format": "valid",
                            "name": service_name,
                            "type": "ai_service"
                        }
                    else:
                        results[service_id] = {
                            "status": "misconfigured",
                            "error": "Invalid or missing API key",
                            "name": service_name,
                            "type": "ai_service"
                        }
                
                elif service_id == "anthropic":
                    api_key = os.getenv("ANTHROPIC_API_KEY")
                    if api_key and api_key.startswith("sk-ant-"):
                        results[service_id] = {
                            "status": "configured",
                            "key_format": "valid",
                            "name": service_name,
                            "type": "ai_service"
                        }
                    else:
                        results[service_id] = {
                            "status": "misconfigured",
                            "error": "Invalid or missing API key",
                            "name": service_name,
                            "type": "ai_service"
                        }
                
                elif service_id == "portkey":
                    # Test Portkey gateway
                    try:
                        url = "http://localhost:8000/api/v1/portkey/status"
                        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=3)) as session:
                            async with session.get(url) as resp:
                                if resp.status == 200:
                                    results[service_id] = {
                                        "status": "healthy",
                                        "name": service_name,
                                        "type": "ai_service"
                                    }
                                else:
                                    results[service_id] = {
                                        "status": "degraded",
                                        "name": service_name,
                                        "type": "ai_service"
                                    }
                    except:
                        results[service_id] = {
                            "status": "unavailable",
                            "name": service_name,
                            "type": "ai_service"
                        }
                
                else:
                    # Generic test
                    results[service_id] = {
                        "status": "unknown",
                        "name": service_name,
                        "type": "ai_service"
                    }
                    
            except Exception as e:
                results[service_id] = {
                    "status": "error",
                    "error": str(e),
                    "name": service_name,
                    "type": "ai_service"
                }
        
        return results

    async def test_mcp_integrations(self) -> Dict[str, Any]:
        """Test MCP server integrations"""
        results = {}
        
        # Standard MCP ports
        mcp_servers = {
            "ai_memory": 9000,
            "figma": 9001,
            "ui_ux_agent": 9002,
            "codacy": 3008,
            "asana": 9006,
            "notion": 9102,
            "linear": 9004,
            "github": 9003,
            "slack": 9101,
            "postgres": 9012,
            "lambda_labs_cli": 9020,
            "portkey_admin": 9013,
            "hubspot": 9103
        }
        
        for server_name, port in mcp_servers.items():
            try:
                # Test MCP server health
                url = f"http://localhost:{port}/health"
                start_time = time.time()
                
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=2)) as session:
                    async with session.get(url) as resp:
                        response_time = (time.time() - start_time) * 1000
                        
                        if resp.status == 200:
                            try:
                                data = await resp.json()
                                results[server_name] = {
                                    "status": "healthy",
                                    "port": port,
                                    "response_time": response_time,
                                    "health_data": data,
                                    "type": "mcp_server"
                                }
                            except:
                                results[server_name] = {
                                    "status": "healthy",
                                    "port": port,
                                    "response_time": response_time,
                                    "type": "mcp_server"
                                }
                        else:
                            results[server_name] = {
                                "status": "degraded",
                                "port": port,
                                "response_time": response_time,
                                "http_status": resp.status,
                                "type": "mcp_server"
                            }
                            
            except Exception as e:
                # Check if process is running on port
                try:
                    for proc in psutil.process_iter(['pid', 'name', 'connections']):
                        connections = proc.info['connections'] or []
                        for conn in connections:
                            if conn.laddr.port == port:
                                results[server_name] = {
                                    "status": "process_running",
                                    "port": port,
                                    "process_name": proc.info['name'],
                                    "note": "Process running but HTTP endpoint unavailable",
                                    "type": "mcp_server"
                                }
                                break
                        if server_name in results:
                            break
                    
                    if server_name not in results:
                        results[server_name] = {
                            "status": "stopped",
                            "port": port,
                            "error": str(e),
                            "type": "mcp_server"
                        }
                except:
                    results[server_name] = {
                        "status": "error",
                        "port": port,
                        "error": str(e),
                        "type": "mcp_server"
                    }
        
        return results

    async def test_development_integrations(self) -> Dict[str, Any]:
        """Test development tool integrations"""
        results = {}
        
        # VS Code Extension
        vscode_ext_dir = Path("sophia-vscode-extension")
        if vscode_ext_dir.exists():
            package_json = vscode_ext_dir / "package.json"
            if package_json.exists():
                try:
                    with open(package_json) as f:
                        package_data = json.load(f)
                    
                    results["vscode_extension"] = {
                        "status": "installed",
                        "version": package_data.get("version"),
                        "name": package_data.get("displayName"),
                        "type": "development_tool"
                    }
                except:
                    results["vscode_extension"] = {
                        "status": "corrupted",
                        "type": "development_tool"
                    }
            else:
                results["vscode_extension"] = {
                    "status": "incomplete",
                    "type": "development_tool"
                }
        else:
            results["vscode_extension"] = {
                "status": "not_found",
                "type": "development_tool"
            }
        
        # Chrome Extension
        chrome_ext_dir = Path("sophia-chrome-extension")
        if chrome_ext_dir.exists():
            manifest_file = chrome_ext_dir / "manifest.json"
            if manifest_file.exists():
                try:
                    with open(manifest_file) as f:
                        manifest_data = json.load(f)
                    
                    results["chrome_extension"] = {
                        "status": "installed",
                        "version": manifest_data.get("version"),
                        "name": manifest_data.get("name"),
                        "type": "development_tool"
                    }
                except:
                    results["chrome_extension"] = {
                        "status": "corrupted",
                        "type": "development_tool"
                    }
            else:
                results["chrome_extension"] = {
                    "status": "incomplete",
                    "type": "development_tool"
                }
        else:
            results["chrome_extension"] = {
                "status": "not_found",
                "type": "development_tool"
            }
        
        # Figma Integration
        try:
            figma_token = os.getenv("FIGMA_PAT") or os.getenv("FIGMA_ACCESS_TOKEN")
            if figma_token:
                results["figma"] = {
                    "status": "configured",
                    "type": "development_tool"
                }
            else:
                results["figma"] = {
                    "status": "not_configured",
                    "type": "development_tool"
                }
        except:
            results["figma"] = {
                "status": "error",
                "type": "development_tool"
            }
        
        return results

    async def test_external_integrations(self) -> Dict[str, Any]:
        """Test external repository integrations"""
        results = {}
        
        external_dir = Path("external")
        if external_dir.exists():
            for repo_dir in external_dir.iterdir():
                if repo_dir.is_dir() and repo_dir.name != "__pycache__":
                    # Check if it's a proper git repository
                    git_dir = repo_dir / ".git"
                    readme_file = None
                    
                    # Look for README files
                    for readme_name in ["README.md", "README.txt", "README"]:
                        readme_path = repo_dir / readme_name
                        if readme_path.exists():
                            readme_file = readme_name
                            break
                    
                    if git_dir.exists():
                        try:
                            # Get git status
                            result = subprocess.run(
                                ["git", "status", "--porcelain"],
                                cwd=repo_dir,
                                capture_output=True,
                                text=True,
                                timeout=5
                            )
                            
                            is_clean = len(result.stdout.strip()) == 0
                            
                            results[repo_dir.name] = {
                                "status": "healthy",
                                "type": "external_repository",
                                "has_readme": readme_file is not None,
                                "git_clean": is_clean,
                                "file_count": len(list(repo_dir.rglob("*")))
                            }
                            
                        except Exception as e:
                            results[repo_dir.name] = {
                                "status": "git_error",
                                "type": "external_repository",
                                "error": str(e)
                            }
                    else:
                        results[repo_dir.name] = {
                            "status": "not_git_repo",
                            "type": "external_repository",
                            "has_readme": readme_file is not None,
                            "file_count": len(list(repo_dir.rglob("*")))
                        }
        else:
            results["external_directory"] = {
                "status": "not_found",
                "type": "external_repository"
            }
        
        return results

    async def test_cli_integrations(self) -> Dict[str, Any]:
        """Test CLI tool integrations"""
        results = {}
        
        cli_tools = [
            ("docker", ["docker", "--version"]),
            ("git", ["git", "--version"]),
            ("python", ["python", "--version"]),
            ("node", ["node", "--version"]),
            ("npm", ["npm", "--version"]),
            ("kubectl", ["kubectl", "version", "--client"]),
            ("pulumi", ["pulumi", "version"])
        ]
        
        for tool_name, command in cli_tools:
            try:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    version_output = result.stdout.strip()
                    results[tool_name] = {
                        "status": "available",
                        "version_output": version_output,
                        "type": "cli_tool"
                    }
                else:
                    results[tool_name] = {
                        "status": "error",
                        "error": result.stderr.strip(),
                        "type": "cli_tool"
                    }
                    
            except subprocess.TimeoutExpired:
                results[tool_name] = {
                    "status": "timeout",
                    "type": "cli_tool"
                }
            except FileNotFoundError:
                results[tool_name] = {
                    "status": "not_installed",
                    "type": "cli_tool"
                }
            except Exception as e:
                results[tool_name] = {
                    "status": "error",
                    "error": str(e),
                    "type": "cli_tool"
                }
        
        # Test specialized CLI integrations
        claude_cli = Path("claude-cli-integration/claude")
        if claude_cli.exists() and claude_cli.is_file():
            results["claude_cli"] = {
                "status": "installed",
                "executable": str(claude_cli),
                "type": "cli_tool"
            }
        else:
            results["claude_cli"] = {
                "status": "not_found",
                "type": "cli_tool"
            }
        
        gemini_cli = Path("gemini-cli-integration/gemini_cli_provider.py")
        if gemini_cli.exists():
            results["gemini_cli"] = {
                "status": "installed",
                "file": str(gemini_cli),
                "type": "cli_tool"
            }
        else:
            results["gemini_cli"] = {
                "status": "not_found",
                "type": "cli_tool"
            }
        
        return results

    async def test_api_integrations(self) -> Dict[str, Any]:
        """Test API endpoint integrations"""
        results = {}
        
        api_endpoints = [
            ("health", "/health"),
            ("dashboard_data", "/api/v3/dashboard/data"),
            ("chat", "/api/v3/chat"),
            ("ai_memory", "/api/v3/ai-memory/health"),
            ("knowledge", "/api/v3/knowledge/status"),
            ("system_status", "/system/status")
        ]
        
        base_url = "http://localhost:8000"
        
        for endpoint_name, path in api_endpoints:
            try:
                url = f"{base_url}{path}"
                start_time = time.time()
                
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                    async with session.get(url) as resp:
                        response_time = (time.time() - start_time) * 1000
                        
                        if resp.status == 200:
                            try:
                                data = await resp.json()
                                results[endpoint_name] = {
                                    "status": "healthy",
                                    "response_time": response_time,
                                    "response_size": len(str(data)),
                                    "type": "api_endpoint"
                                }
                            except:
                                results[endpoint_name] = {
                                    "status": "healthy",
                                    "response_time": response_time,
                                    "content_type": "non_json",
                                    "type": "api_endpoint"
                                }
                        else:
                            results[endpoint_name] = {
                                "status": "degraded",
                                "response_time": response_time,
                                "http_status": resp.status,
                                "type": "api_endpoint"
                            }
                            
            except Exception as e:
                results[endpoint_name] = {
                    "status": "unavailable",
                    "error": str(e),
                    "type": "api_endpoint"
                }
        
        return results

    async def test_realtime_integrations(self) -> Dict[str, Any]:
        """Test real-time service integrations"""
        results = {}
        
        # WebSocket connections
        websocket_endpoints = [
            ("chat_websocket", "ws://localhost:8000/ws"),
            ("agents_websocket", "ws://localhost:8000/ws/agents"),
            ("system_websocket", "ws://localhost:8000/ws/system")
        ]
        
        for ws_name, ws_url in websocket_endpoints:
            try:
                # Simple WebSocket connection test
                import websockets
                
                async with websockets.connect(ws_url, timeout=3) as websocket:
                    # Send ping
                    await websocket.send('{"type": "ping"}')
                    
                    # Wait for response
                    response = await asyncio.wait_for(websocket.recv(), timeout=2)
                    
                    results[ws_name] = {
                        "status": "healthy",
                        "response": response,
                        "type": "websocket"
                    }
                    
            except ImportError:
                results[ws_name] = {
                    "status": "websockets_not_installed",
                    "type": "websocket"
                }
            except Exception as e:
                results[ws_name] = {
                    "status": "unavailable",
                    "error": str(e),
                    "type": "websocket"
                }
        
        # Server-Sent Events
        sse_endpoints = [
            ("system_events", "/api/v1/events/stream"),
            ("monitoring_events", "/api/v1/monitoring/stream")
        ]
        
        for sse_name, sse_path in sse_endpoints:
            try:
                url = f"http://localhost:8000{sse_path}"
                
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=3)) as session:
                    async with session.get(url, headers={"Accept": "text/event-stream"}) as resp:
                        if resp.status == 200:
                            results[sse_name] = {
                                "status": "healthy",
                                "content_type": resp.headers.get("content-type"),
                                "type": "server_sent_events"
                            }
                        else:
                            results[sse_name] = {
                                "status": "degraded",
                                "http_status": resp.status,
                                "type": "server_sent_events"
                            }
                            
            except Exception as e:
                results[sse_name] = {
                    "status": "unavailable",
                    "error": str(e),
                    "type": "server_sent_events"
                }
        
        return results

    def get_mcp_port(self, service_name: str) -> Optional[int]:
        """Get MCP server port for a service"""
        mcp_ports = {
            "ai_memory": 9000,
            "figma": 9001,
            "ui_ux_agent": 9002,
            "github": 9003,
            "linear": 9004,
            "slack": 9101,
            "asana": 9006,
            "notion": 9102,
            "codacy": 3008,
            "postgres": 9012,
            "hubspot": 9103,
            "lambda_labs_cli": 9020,
            "portkey_admin": 9013
        }
        return mcp_ports.get(service_name)

    async def generate_final_report(self) -> Dict[str, Any]:
        """Generate comprehensive final report"""
        total_duration = (datetime.now() - self.start_time).total_seconds()
        
        # Calculate summary statistics
        total_integrations = 0
        healthy_integrations = 0
        degraded_integrations = 0
        unavailable_integrations = 0
        
        category_stats = {}
        
        for category, data in self.test_results.items():
            if "results" in data:
                results = data["results"]
                category_total = len(results)
                category_healthy = len([r for r in results.values() if r.get("status") == "healthy"])
                category_degraded = len([r for r in results.values() if r.get("status") in ["degraded", "configured", "mcp_only"]])
                category_unavailable = len([r for r in results.values() if r.get("status") in ["unavailable", "error", "not_found"]])
                
                total_integrations += category_total
                healthy_integrations += category_healthy
                degraded_integrations += category_degraded
                unavailable_integrations += category_unavailable
                
                category_stats[category] = {
                    "total": category_total,
                    "healthy": category_healthy,
                    "degraded": category_degraded,
                    "unavailable": category_unavailable,
                    "health_percentage": (category_healthy / category_total * 100) if category_total > 0 else 0
                }
        
        # Generate final report
        report = {
            "test_metadata": {
                "test_started": self.start_time.isoformat(),
                "test_completed": datetime.now().isoformat(),
                "total_duration_seconds": total_duration,
                "test_framework_version": "1.0.0"
            },
            "executive_summary": {
                "total_integrations_tested": total_integrations,
                "healthy_integrations": healthy_integrations,
                "degraded_integrations": degraded_integrations,
                "unavailable_integrations": unavailable_integrations,
                "overall_health_percentage": (healthy_integrations / total_integrations * 100) if total_integrations > 0 else 0,
                "platform_status": self._determine_platform_status(healthy_integrations, total_integrations)
            },
            "category_breakdown": category_stats,
            "detailed_results": self.test_results,
            "integration_inventory": self.integration_inventory,
            "critical_issues": self._identify_critical_issues(),
            "recommendations": self._generate_recommendations(),
            "performance_metrics": self._calculate_performance_metrics(),
            "error_log": self.error_log
        }
        
        # Save report to file
        report_filename = f"comprehensive_integration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 Comprehensive Integration Report Generated: {report_filename}")
        return report

    def _determine_platform_status(self, healthy: int, total: int) -> str:
        """Determine overall platform status"""
        if total == 0:
            return "unknown"
        
        health_percentage = (healthy / total) * 100
        
        if health_percentage >= 90:
            return "excellent"
        elif health_percentage >= 75:
            return "good"
        elif health_percentage >= 50:
            return "fair"
        elif health_percentage >= 25:
            return "poor"
        else:
            return "critical"

    def _identify_critical_issues(self) -> List[Dict[str, Any]]:
        """Identify critical integration issues"""
        issues = []
        
        for category, data in self.test_results.items():
            if "results" in data:
                for integration, result in data["results"].items():
                    if result.get("status") in ["unavailable", "error"]:
                        issues.append({
                            "category": category,
                            "integration": integration,
                            "status": result.get("status"),
                            "error": result.get("error"),
                            "criticality": self._assess_criticality(category, integration)
                        })
        
        return sorted(issues, key=lambda x: x["criticality"], reverse=True)

    def _assess_criticality(self, category: str, integration: str) -> int:
        """Assess criticality of an integration (1-10 scale)"""
        critical_integrations = {
            "postgresql": 10,
            "redis": 9,
            "qdrant": 9,
            "backend": 10,
            "openai": 8,
            "anthropic": 8,
            "hubspot": 7,
            "gong": 7,
            "slack": 6,
            "linear": 5,
            "asana": 5,
            "notion": 4
        }
        
        return critical_integrations.get(integration, 3)

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Analyze results and generate specific recommendations
        if "Infrastructure" in self.test_results:
            infra_results = self.test_results["Infrastructure"]["results"]
            lambda_labs_healthy = len([r for k, r in infra_results.items() if k.startswith("lambda_labs") and r.get("status") == "healthy"])
            lambda_labs_total = len([r for k, r in infra_results.items() if k.startswith("lambda_labs")])
            
            if lambda_labs_healthy < lambda_labs_total:
                recommendations.append(f"Lambda Labs Infrastructure: {lambda_labs_healthy}/{lambda_labs_total} servers healthy - investigate network connectivity")
        
        if "Database" in self.test_results:
            db_results = self.test_results["Database"]["results"]
            if db_results.get("postgresql", {}).get("status") != "healthy":
                recommendations.append("PostgreSQL database unavailable - critical for data persistence")
            if db_results.get("redis", {}).get("status") != "healthy":
                recommendations.append("Redis cache unavailable - impacts performance")
            if db_results.get("qdrant", {}).get("status") != "healthy":
                recommendations.append("Qdrant vector database unavailable - impacts AI capabilities")
        
        if "MCP Servers" in self.test_results:
            mcp_results = self.test_results["MCP Servers"]["results"]
            unhealthy_mcp = [k for k, v in mcp_results.items() if v.get("status") not in ["healthy", "configured"]]
            if len(unhealthy_mcp) > 5:
                recommendations.append(f"Multiple MCP servers unhealthy ({len(unhealthy_mcp)} servers) - review MCP orchestration")
        
        if len(self.error_log) > 0:
            recommendations.append(f"Multiple integration errors detected ({len(self.error_log)} errors) - review error log for details")
        
        return recommendations

    def _calculate_performance_metrics(self) -> Dict[str, Any]:
        """Calculate performance metrics"""
        response_times = []
        
        for category, data in self.test_results.items():
            if "results" in data:
                for integration, result in data["results"].items():
                    if "response_time" in result:
                        response_times.append(result["response_time"])
        
        if response_times:
            return {
                "average_response_time_ms": sum(response_times) / len(response_times),
                "max_response_time_ms": max(response_times),
                "min_response_time_ms": min(response_times),
                "total_tests_with_timing": len(response_times)
            }
        else:
            return {
                "average_response_time_ms": None,
                "max_response_time_ms": None,
                "min_response_time_ms": None,
                "total_tests_with_timing": 0
            }

async def main():
    """Main execution function"""
    tester = ComprehensiveIntegrationTester()
    
    try:
        report = await tester.test_all_integrations()
        
        # Print executive summary
        print("\n" + "="*70)
        print("🎯 COMPREHENSIVE INTEGRATION TEST RESULTS")
        print("="*70)
        
        summary = report["executive_summary"]
        print(f"📊 Total Integrations Tested: {summary['total_integrations_tested']}")
        print(f"✅ Healthy: {summary['healthy_integrations']}")
        print(f"⚠️  Degraded: {summary['degraded_integrations']}")
        print(f"❌ Unavailable: {summary['unavailable_integrations']}")
        print(f"📈 Overall Health: {summary['overall_health_percentage']:.1f}%")
        print(f"🏆 Platform Status: {summary['platform_status'].upper()}")
        
        # Print category breakdown
        print(f"\n📋 Category Breakdown:")
        for category, stats in report["category_breakdown"].items():
            print(f"   {category}: {stats['healthy']}/{stats['total']} healthy ({stats['health_percentage']:.1f}%)")
        
        # Print critical issues
        critical_issues = report["critical_issues"]
        if critical_issues:
            print(f"\n🚨 Critical Issues ({len(critical_issues)}):")
            for issue in critical_issues[:5]:  # Top 5
                print(f"   • {issue['category']}/{issue['integration']}: {issue['status']}")
                if issue.get('error'):
                    print(f"     Error: {issue['error'][:100]}...")
        
        # Print recommendations
        recommendations = report["recommendations"]
        if recommendations:
            print(f"\n💡 Recommendations ({len(recommendations)}):")
            for i, rec in enumerate(recommendations[:5], 1):  # Top 5
                print(f"   {i}. {rec}")
        
        print(f"\n📄 Detailed report saved to: comprehensive_integration_report_*.json")
        
        return report
        
    except Exception as e:
        logger.error(f"Integration testing failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 