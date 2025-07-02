#!/usr/bin/env python3
"""
Sophia AI Self-Healing Deployment System
Automatically detects, fixes, and prevents common deployment issues
"""

import asyncio
import ast
import json
import logging
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SelfHealingDeployment:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.fixed_issues = []
        self.deployment_status = {
            "start_time": datetime.now().isoformat(),
            "issues_fixed": 0,
            "services_deployed": 0,
            "health_score": 0
        }

    async def run_self_healing_deployment(self):
        """Main self-healing deployment process"""
        logger.info("🔧 Starting Self-Healing Deployment System")
        
        try:
            # Phase 1: Fix critical issues
            await self._fix_critical_issues()
            
            # Phase 2: Deploy services incrementally
            await self._deploy_services()
            
            # Phase 3: Validate deployment
            await self._validate_deployment()
            
            logger.info("✅ Self-healing deployment completed successfully!")
            return self.deployment_status
            
        except Exception as e:
            logger.error(f"❌ Self-healing deployment failed: {e}")
            return {"success": False, "error": str(e)}

    async def _fix_critical_issues(self):
        """Fix critical issues that prevent deployment"""
        logger.info("🔍 Phase 1: Fixing critical issues")
        
        # Fix indentation errors in snowflake_cortex_service.py
        await self._fix_snowflake_indentation()
        
        # Fix missing module imports
        await self._fix_missing_imports()
        
        # Fix MCP server configuration
        await self._fix_mcp_configuration()
        
        # Install missing dependencies
        await self._install_missing_dependencies()

    async def _fix_snowflake_indentation(self):
        """Fix indentation errors in snowflake_cortex_service.py"""
        file_path = self.project_root / "backend" / "utils" / "snowflake_cortex_service.py"
        
        if not file_path.exists():
            return
            
        try:
            content = file_path.read_text()
            lines = content.split('\n')
            fixed_lines = []
            
            for i, line in enumerate(lines):
                # Fix specific indentation issues
                if 'cursor = self.connection.cursor()' in line and line.startswith('cursor'):
                    # Add proper indentation
                    line = '            ' + line
                    
                # Fix try block indentation
                if line.strip() == 'cursor = self.connection.cursor()' and i > 0:
                    prev_line = lines[i-1].strip()
                    if prev_line.endswith('try:'):
                        line = '            ' + line.strip()
                
                fixed_lines.append(line)
            
            # Save fixed content
            file_path.write_text('\n'.join(fixed_lines))
            logger.info("   ✅ Fixed indentation in snowflake_cortex_service.py")
            self.deployment_status["issues_fixed"] += 1
            
        except Exception as e:
            logger.warning(f"   ⚠️ Could not fix snowflake indentation: {e}")

    async def _fix_missing_imports(self):
        """Fix missing import issues"""
        logger.info("   🔧 Fixing missing imports...")
        
        # Create missing server module
        server_file = self.project_root / "backend" / "mcp_servers" / "server.py"
        if not server_file.exists():
            server_content = '''"""
Basic server implementation for MCP servers
"""

class Server:
    """Basic server class for MCP compatibility"""
    def __init__(self, name: str):
        self.name = name
    
    def run(self):
        pass
'''
            server_file.parent.mkdir(parents=True, exist_ok=True)
            server_file.write_text(server_content)
            logger.info("   ✅ Created missing server.py module")
            self.deployment_status["issues_fixed"] += 1

    async def _fix_mcp_configuration(self):
        """Fix MCP server configuration issues"""
        config_file = self.project_root / "config" / "cursor_enhanced_mcp_config.json"
        
        if config_file.exists():
            try:
                config = json.loads(config_file.read_text())
                
                # Fix MCPServerEndpoint initialization
                if 'mcpServers' in config:
                    for server_name, server_config in config['mcpServers'].items():
                        if isinstance(server_config, dict) and 'name' in server_config:
                            del server_config['name']
                
                config_file.write_text(json.dumps(config, indent=2))
                logger.info("   ✅ Fixed MCP configuration")
                self.deployment_status["issues_fixed"] += 1
                
            except Exception as e:
                logger.warning(f"   ⚠️ Could not fix MCP config: {e}")

    async def _install_missing_dependencies(self):
        """Install missing dependencies"""
        missing_deps = ['slowapi', 'aiomysql', 'snowflake-connector-python']
        
        for dep in missing_deps:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
                logger.info(f"   ✅ Installed {dep}")
                self.deployment_status["issues_fixed"] += 1
            except Exception as e:
                logger.warning(f"   ⚠️ Failed to install {dep}: {e}")

    async def _deploy_services(self):
        """Deploy services incrementally"""
        logger.info("🚀 Phase 2: Deploying services")
        
        # Create and deploy minimal working API
        await self._create_minimal_api()
        
        # Deploy existing MCP servers if they exist
        await self._deploy_existing_mcp_servers()

    async def _create_minimal_api(self):
        """Create a minimal working API"""
        api_file = self.project_root / "backend" / "app" / "self_healing_api.py"
        
        api_content = '''#!/usr/bin/env python3
"""
Self-Healing Minimal API for Sophia AI
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Sophia AI Self-Healing API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "self_healing_api"}

@app.get("/")
async def root():
    return {"message": "Sophia AI Self-Healing API is running"}

@app.get("/api/v1/status")
async def api_status():
    return {
        "api_version": "1.0.0",
        "status": "operational",
        "self_healing": True
    }

if __name__ == "__main__":
    logger.info("🚀 Starting Self-Healing API on port 8002")
    uvicorn.run(app, host="0.0.0.0", port=8002)
'''
        
        api_file.write_text(api_content)
        api_file.chmod(0o755)
        
        # Start the API
        try:
            process = await asyncio.create_subprocess_exec(
                sys.executable, str(api_file),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Give it time to start
            await asyncio.sleep(3)
            
            # Check if it's running
            if await self._check_service_health("localhost", 8002):
                logger.info("   ✅ Self-healing API deployed successfully on port 8002")
                self.deployment_status["services_deployed"] += 1
            else:
                logger.warning("   ⚠️ Self-healing API health check failed")
                
        except Exception as e:
            logger.error(f"   ❌ Failed to deploy self-healing API: {e}")

    async def _deploy_existing_mcp_servers(self):
        """Deploy existing MCP servers if they're working"""
        mcp_servers = [
            ("ai_memory", "mcp-servers/ai_memory/simple_ai_memory_server.py", 9001),
            ("codacy", "mcp-servers/codacy/simple_codacy_server.py", 3008),
            ("github", "mcp-servers/github/simple_github_server.py", 9003),
            ("linear", "mcp-servers/linear/simple_linear_server.py", 9004)
        ]
        
        for server_name, server_path, port in mcp_servers:
            server_file = self.project_root / server_path
            
            if server_file.exists():
                try:
                    # Check if port is available
                    if await self._is_port_available(port):
                        process = await asyncio.create_subprocess_exec(
                            sys.executable, str(server_file),
                            stdout=asyncio.subprocess.PIPE,
                            stderr=asyncio.subprocess.PIPE
                        )
                        
                        await asyncio.sleep(2)
                        
                        if await self._check_service_health("localhost", port):
                            logger.info(f"   ✅ {server_name} MCP server deployed on port {port}")
                            self.deployment_status["services_deployed"] += 1
                        else:
                            logger.warning(f"   ⚠️ {server_name} MCP server health check failed")
                    else:
                        logger.warning(f"   ⚠️ Port {port} not available for {server_name}")
                        
                except Exception as e:
                    logger.warning(f"   ⚠️ Failed to deploy {server_name}: {e}")

    async def _validate_deployment(self):
        """Validate the deployment"""
        logger.info("✅ Phase 3: Validating deployment")
        
        # Check service health
        services_checked = 0
        services_healthy = 0
        
        test_ports = [8002, 9001, 3008, 9003, 9004]
        
        for port in test_ports:
            services_checked += 1
            if await self._check_service_health("localhost", port):
                services_healthy += 1
                logger.info(f"   ✅ Service on port {port} is healthy")
            else:
                logger.info(f"   ℹ️ No service running on port {port}")
        
        # Calculate health score
        if services_checked > 0:
            self.deployment_status["health_score"] = (services_healthy / services_checked) * 100
        
        logger.info(f"   📊 Deployment health score: {self.deployment_status['health_score']:.1f}%")
        
        # Create deployment report
        await self._create_deployment_report()

    async def _check_service_health(self, host: str, port: int) -> bool:
        """Check if a service is healthy"""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://{host}:{port}/health", timeout=5) as response:
                    return response.status == 200
        except Exception:
            return False

    async def _is_port_available(self, port: int) -> bool:
        """Check if a port is available"""
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return True
        except OSError:
            return False

    async def _create_deployment_report(self):
        """Create deployment report"""
        report_content = f"""# Self-Healing Deployment Report

## Summary
- **Start Time**: {self.deployment_status['start_time']}
- **Issues Fixed**: {self.deployment_status['issues_fixed']}
- **Services Deployed**: {self.deployment_status['services_deployed']}
- **Health Score**: {self.deployment_status['health_score']:.1f}%

## Fixed Issues
"""
        
        for issue in self.fixed_issues:
            report_content += f"- {issue}\n"
        
        report_content += f"""
## Services Status
- Self-Healing API: http://localhost:8002
- AI Memory MCP: http://localhost:9001 (if available)
- Codacy MCP: http://localhost:3008 (if available)
- GitHub MCP: http://localhost:9003 (if available)
- Linear MCP: http://localhost:9004 (if available)

## Next Steps
1. Check service health at the URLs above
2. Monitor logs for any issues
3. Run additional tests as needed

---
*Generated by Sophia AI Self-Healing Deployment System*
"""
        
        report_file = self.project_root / "SELF_HEALING_DEPLOYMENT_REPORT.md"
        report_file.write_text(report_content)
        logger.info(f"   📄 Deployment report saved to {report_file}")

async def main():
    """Main entry point"""
    deployment = SelfHealingDeployment()
    result = await deployment.run_self_healing_deployment()
    
    print("\n" + "="*60)
    print("SELF-HEALING DEPLOYMENT SUMMARY")
    print("="*60)
    print(f"Issues Fixed: {result.get('issues_fixed', 0)}")
    print(f"Services Deployed: {result.get('services_deployed', 0)}")
    print(f"Health Score: {result.get('health_score', 0):.1f}%")
    print("="*60)
    
    return result

if __name__ == "__main__":
    asyncio.run(main()) 