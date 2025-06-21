#!/usr/bin/env python3
"""Deploy All Sophia AI Retool Dashboards
Ensures consistent design, proper integrations, and live deployment
"""

import asyncio
import json
import os
import subprocess
import sys
from datetime import datetime
from typing import Any, Dict

import aiohttp

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
RESET = "\033[0m"

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
ADMIN_KEY = os.getenv("SOPHIA_ADMIN_KEY", "sophia_admin_2024")


class ComprehensiveDashboardDeployer:
    """Deploy all Sophia AI dashboards with consistent design"""

    def __init__(self):
        self.backend_url = BACKEND_URL
        self.admin_key = ADMIN_KEY
        self.deployment_results = {}
        self.mcp_servers = []
        self.integration_status = {}

    async def check_prerequisites(self) -> bool:
        """Check all prerequisites before deployment"""
        print(f"\n{BLUE}=== Checking Prerequisites ==={RESET}")

        checks = {
            "Backend API": await self._check_backend(),
            "Docker": self._check_docker(),
            "Docker Compose": self._check_docker_compose(),
            "Environment Variables": self._check_env_vars(),
            "Python Dependencies": self._check_python_deps(),
        }

        all_passed = True
        for check, result in checks.items():
            if result:
                print(f"{GREEN}✓ {check}{RESET}")
            else:
                print(f"{RED}✗ {check}{RESET}")
                all_passed = False

        return all_passed

    async def _check_backend(self) -> bool:
        """Check if backend is running"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.backend_url}/health") as response:
                    return response.status == 200
        except:
            return False

    def _check_docker(self) -> bool:
        """Check if Docker is installed"""
        try:
            result = subprocess.run(["docker", "--version"], capture_output=True)
            return result.returncode == 0
        except:
            return False

    def _check_docker_compose(self) -> bool:
        """Check if Docker Compose is installed"""
        try:
            result = subprocess.run(
                ["docker-compose", "--version"], capture_output=True
            )
            return result.returncode == 0
        except:
            return False

    def _check_env_vars(self) -> bool:
        """Check required environment variables"""
        required = ["OPENAI_API_KEY", "PINECONE_API_KEY", "SNOWFLAKE_ACCOUNT"]
        missing = [var for var in required if not os.getenv(var)]
        if missing:
            print(
                f"{YELLOW}  Missing environment variables: {', '.join(missing)}{RESET}"
            )
        return len(missing) == 0

    def _check_python_deps(self) -> bool:
        """Check if required Python packages are installed"""
        try:
            import asyncio
            import json

            import aiohttp

            return True
        except ImportError:
            return False

    async def start_backend_if_needed(self) -> bool:
        """Start backend if not running"""
        if not await self._check_backend():
            print(f"\n{YELLOW}Backend not running. Starting...{RESET}")

            # Start backend
            backend_process = subprocess.Popen(
                ["python", "backend/main.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Wait for backend to start
            for i in range(30):
                await asyncio.sleep(1)
                if await self._check_backend():
                    print(f"{GREEN}✓ Backend started successfully{RESET}")
                    return True

            print(f"{RED}✗ Failed to start backend{RESET}")
            return False

        return True

    async def start_mcp_servers(self) -> Dict[str, bool]:
        """Start all required MCP servers"""
        print(f"\n{BLUE}=== Starting MCP Servers ==={RESET}")

        mcp_servers = [
            "gong-mcp",
            "slack-mcp",
            "snowflake-mcp",
            "pinecone-mcp",
            "retool-mcp",
            "linear-mcp",
            "claude-mcp",
            "ai-memory-mcp",
            "knowledge-mcp",
            "apollo-mcp",
        ]

        # Check which servers are already running
        running_servers = {}
        try:
            result = subprocess.run(
                ["docker-compose", "ps", "--format", "json"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                containers = json.loads(result.stdout) if result.stdout else []
                for container in containers:
                    if container.get("State") == "running":
                        running_servers[container["Service"]] = True
        except:
            pass

        # Start servers that aren't running
        servers_to_start = [s for s in mcp_servers if s not in running_servers]

        if servers_to_start:
            print(f"Starting {len(servers_to_start)} MCP servers...")
            result = subprocess.run(
                ["docker-compose", "up", "-d"] + servers_to_start,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                print(f"{RED}Error starting MCP servers: {result.stderr}{RESET}")
                return {}

        # Wait for servers to be ready
        await asyncio.sleep(5)

        # Check server status
        server_status = {}
        for server in mcp_servers:
            server_status[server] = (
                server in running_servers or server in servers_to_start
            )
            status_icon = "✓" if server_status[server] else "✗"
            color = GREEN if server_status[server] else RED
            print(f"{color}{status_icon} {server}{RESET}")

        return server_status

    async def check_integrations(self) -> Dict[str, Dict[str, Any]]:
        """Check all integration connections"""
        print(f"\n{BLUE}=== Checking Integrations ==={RESET}")

        integrations = {
            "Snowflake": await self._check_snowflake(),
            "Gong": await self._check_gong(),
            "Slack": await self._check_slack(),
            "Pinecone": await self._check_pinecone(),
            "Linear": await self._check_linear(),
            "OpenAI": await self._check_openai(),
        }

        for name, status in integrations.items():
            if status["connected"]:
                print(f"{GREEN}✓ {name}: Connected{RESET}")
                if "details" in status:
                    print(f"  {status['details']}")
            else:
                print(f"{RED}✗ {name}: {status.get('error', 'Not connected')}{RESET}")

        return integrations

    async def _check_snowflake(self) -> Dict[str, Any]:
        """Check Snowflake connection"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"X-Admin-Key": self.admin_key}
                async with session.get(
                    f"{self.backend_url}/api/integrations/snowflake/test",
                    headers=headers,
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "connected": True,
                            "details": f"Database: {data.get('database', 'N/A')}",
                        }
                    else:
                        return {
                            "connected": False,
                            "error": f"Status {response.status}",
                        }
        except Exception as e:
            return {"connected": False, "error": str(e)}

    async def _check_gong(self) -> Dict[str, Any]:
        """Check Gong connection"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"X-Admin-Key": self.admin_key}
                async with session.get(
                    f"{self.backend_url}/api/integrations/gong/test", headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "connected": True,
                            "details": f"Calls available: {data.get('call_count', 0)}",
                        }
                    else:
                        return {
                            "connected": False,
                            "error": f"Status {response.status}",
                        }
        except Exception as e:
            return {"connected": False, "error": str(e)}

    async def _check_slack(self) -> Dict[str, Any]:
        """Check Slack connection"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"X-Admin-Key": self.admin_key}
                async with session.get(
                    f"{self.backend_url}/api/integrations/slack/test", headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "connected": True,
                            "details": f"Workspace: {data.get('workspace', 'N/A')}",
                        }
                    else:
                        return {
                            "connected": False,
                            "error": f"Status {response.status}",
                        }
        except Exception as e:
            return {"connected": False, "error": str(e)}

    async def _check_pinecone(self) -> Dict[str, Any]:
        """Check Pinecone connection"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"X-Admin-Key": self.admin_key}
                async with session.get(
                    f"{self.backend_url}/api/integrations/pinecone/test",
                    headers=headers,
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "connected": True,
                            "details": f"Index: {data.get('index', 'N/A')}",
                        }
                    else:
                        return {
                            "connected": False,
                            "error": f"Status {response.status}",
                        }
        except Exception as e:
            return {"connected": False, "error": str(e)}

    async def _check_linear(self) -> Dict[str, Any]:
        """Check Linear connection"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"X-Admin-Key": self.admin_key}
                async with session.get(
                    f"{self.backend_url}/api/integrations/linear/test", headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "connected": True,
                            "details": f"Workspace: {data.get('workspace', 'N/A')}",
                        }
                    else:
                        return {
                            "connected": False,
                            "error": f"Status {response.status}",
                        }
        except Exception as e:
            return {"connected": False, "error": str(e)}

    async def _check_openai(self) -> Dict[str, Any]:
        """Check OpenAI connection"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"X-Admin-Key": self.admin_key}
                async with session.get(
                    f"{self.backend_url}/api/integrations/openai/test", headers=headers
                ) as response:
                    if response.status == 200:
                        return {"connected": True}
                    else:
                        return {
                            "connected": False,
                            "error": f"Status {response.status}",
                        }
        except Exception as e:
            return {"connected": False, "error": str(e)}

    def generate_retool_configs(self) -> Dict[str, Dict[str, Any]]:
        """Generate consistent Retool configurations for all dashboards"""
        print(f"\n{BLUE}=== Generating Retool Configurations ==={RESET}")

        # Shared design system
        design_system = {
            "colors": {
                "primary": "#5E6AD2",  # Linear purple
                "secondary": "#238636",  # GitHub green
                "accent": "#F59E0B",  # Warning yellow
                "danger": "#EF4444",  # Error red
                "success": "#10B981",  # Success green
                "background": "#1a1a1a",  # Dark background
                "surface": "#2a2a2a",  # Card background
                "text": "#ffffff",  # Primary text
                "textSecondary": "#a0a0a0",  # Secondary text
            },
            "fonts": {
                "heading": "Inter, system-ui, sans-serif",
                "body": "Inter, system-ui, sans-serif",
                "mono": "JetBrains Mono, monospace",
            },
            "spacing": {"xs": 4, "sm": 8, "md": 16, "lg": 24, "xl": 32},
            "borderRadius": 8,
            "shadow": "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
        }

        # Shared components
        shared_components = {
            "header": {
                "type": "container",
                "backgroundColor": design_system["colors"]["background"],
                "padding": design_system["spacing"]["md"],
                "borderBottom": f"1px solid {design_system['colors']['surface']}",
            },
            "statCard": {
                "backgroundColor": design_system["colors"]["surface"],
                "borderRadius": design_system["borderRadius"],
                "padding": design_system["spacing"]["md"],
                "boxShadow": design_system["shadow"],
            },
        }

        # CEO Dashboard Configuration
        ceo_config = {
            "name": "Sophia CEO Dashboard",
            "description": "Executive command center for Pay Ready AI",
            "theme": design_system,
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
                    },
                }
            ],
            "tabs": [
                {
                    "name": "Strategic Intelligence",
                    "icon": "fas fa-brain",
                    "color": design_system["colors"]["primary"],
                },
                {
                    "name": "Client Health",
                    "icon": "fas fa-heartbeat",
                    "color": design_system["colors"]["success"],
                },
                {
                    "name": "AI System Status",
                    "icon": "fas fa-robot",
                    "color": design_system["colors"]["accent"],
                },
            ],
        }

        # Knowledge Admin Dashboard Configuration
        knowledge_config = {
            "name": "Sophia Knowledge Admin",
            "description": "Knowledge base management and curation",
            "theme": design_system,
            "resources": [
                {
                    "name": "KnowledgeAPI",
                    "type": "restapi",
                    "config": {
                        "baseURL": f"{self.backend_url}/api/knowledge",
                        "headers": [
                            {
                                "key": "Authorization",
                                "value": "Bearer {{ current_user.authToken }}",
                            },
                            {"key": "Content-Type", "value": "application/json"},
                        ],
                    },
                }
            ],
            "tabs": [
                {
                    "name": "Document Upload",
                    "icon": "fas fa-upload",
                    "color": design_system["colors"]["primary"],
                },
                {
                    "name": "Knowledge Curation",
                    "icon": "fas fa-edit",
                    "color": design_system["colors"]["secondary"],
                },
                {
                    "name": "Discovery Queue",
                    "icon": "fas fa-lightbulb",
                    "color": design_system["colors"]["accent"],
                },
            ],
        }

        # Project Management Dashboard Configuration
        project_config = {
            "name": "Sophia Project Intelligence",
            "description": "Unified project management across all tools",
            "theme": design_system,
            "resources": [
                {
                    "name": "ProjectAPI",
                    "type": "restapi",
                    "config": {
                        "baseURL": f"{self.backend_url}/api/project-management",
                        "headers": [
                            {
                                "key": "Authorization",
                                "value": "Bearer {{ environment.SOPHIA_API_KEY }}",
                            },
                            {"key": "Content-Type", "value": "application/json"},
                        ],
                    },
                }
            ],
            "tabs": [
                {
                    "name": "Portfolio Overview",
                    "icon": "fas fa-th-large",
                    "color": design_system["colors"]["primary"],
                },
                {
                    "name": "OKR Alignment",
                    "icon": "fas fa-bullseye",
                    "color": design_system["colors"]["success"],
                },
                {
                    "name": "Team Performance",
                    "icon": "fas fa-users",
                    "color": design_system["colors"]["secondary"],
                },
            ],
        }

        # Save configurations
        configs = {
            "ceo": ceo_config,
            "knowledge": knowledge_config,
            "project": project_config,
        }

        for name, config in configs.items():
            filename = f"retool_{name}_dashboard_config.json"
            with open(filename, "w") as f:
                json.dump(config, f, indent=2)
            print(f"{GREEN}✓ Generated {filename}{RESET}")

        return configs

    def generate_deployment_guide(self) -> str:
        """Generate comprehensive deployment guide"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        guide = f"""
# Sophia AI Dashboard Deployment Guide
Generated: {timestamp}

## 🚀 Quick Start

### Prerequisites Status:
"""
        # Add prerequisite status
        for check, result in self.deployment_results.get("prerequisites", {}).items():
            status = "✅" if result else "❌"
            guide += f"- {status} {check}\n"

        guide += """

### MCP Server Status:
"""
        # Add MCP server status
        for server, running in self.deployment_results.get("mcp_servers", {}).items():
            status = "✅" if running else "❌"
            guide += f"- {status} {server}\n"

        guide += """

### Integration Status:
"""
        # Add integration status
        for integration, status in self.deployment_results.get(
            "integrations", {}
        ).items():
            icon = "✅" if status.get("connected") else "❌"
            details = (
                status.get("details", "")
                if status.get("connected")
                else status.get("error", "Not connected")
            )
            guide += f"- {icon} {integration}: {details}\n"

        guide += f"""

## 📊 Dashboard URLs

### 1. CEO Dashboard
- **Purpose**: Executive command center with strategic intelligence
- **Backend URL**: {self.backend_url}
- **Key Features**:
  - Strategic Intelligence Chat
  - Client Health Portfolio
  - AI System Monitoring

### 2. Knowledge Admin Dashboard
- **Purpose**: Knowledge base management and curation
- **API Endpoint**: {self.backend_url}/api/knowledge
- **Key Features**:
  - Document Upload & Processing
  - Knowledge Curation Chat
  - Discovery Queue for insights

### 3. Project Intelligence Dashboard
- **Purpose**: Unified project management across Linear, GitHub, Asana, Slack
- **API Endpoint**: {self.backend_url}/api/project-management
- **Key Features**:
  - Portfolio Overview
  - OKR Alignment Tracking
  - Team Performance Analytics

## 🛠️ Retool Setup Instructions

### Step 1: Create Retool Apps

1. Log into Retool (https://retool.com)
2. Create three new apps:
   - "Sophia CEO Dashboard"
   - "Sophia Knowledge Admin"
   - "Sophia Project Intelligence"

### Step 2: Import Configurations

For each dashboard:
1. Open the app in Retool
2. Go to Settings → App JSON
3. Copy the contents from the respective config file:
   - CEO: `retool_ceo_dashboard_config.json`
   - Knowledge: `retool_knowledge_dashboard_config.json`
   - Project: `retool_project_dashboard_config.json`
4. Paste and save

### Step 3: Configure Resources

Each dashboard needs its API resource configured:

**CEO Dashboard:**
- Resource Name: SophiaAPI
- Base URL: {self.backend_url}
- Headers: X-Admin-Key = {self.admin_key}

**Knowledge Admin:**
- Resource Name: KnowledgeAPI
- Base URL: {self.backend_url}/api/knowledge
- Headers: Authorization = Bearer {{{{ current_user.authToken }}}}

**Project Intelligence:**
- Resource Name: ProjectAPI
- Base URL: {self.backend_url}/api/project-management
- Headers: Authorization = Bearer {{{{ environment.SOPHIA_API_KEY }}}}

### Step 4: Environment Variables

Set these in Retool's environment settings:
- SOPHIA_API_URL = {self.backend_url}
- SOPHIA_API_KEY = {self.admin_key}
- SOPHIA_ADMIN_KEY = {self.admin_key}

## 🔧 Test Commands

### Test CEO Dashboard API:
```bash
# Dashboard Summary
curl -H "X-Admin-Key: {self.admin_key}" \\
     {self.backend_url}/api/retool/executive/dashboard-summary

# Strategic Chat
curl -X POST -H "X-Admin-Key: {self.admin_key}" \\
     -H "Content-Type: application/json" \\
     -d '{{"message": "What is our client health status?", "mode": "internal"}}' \\
     {self.backend_url}/api/retool/executive/strategic-chat
```

### Test Knowledge Admin API:
```bash
# Get Knowledge Stats
curl -H "Authorization: Bearer {self.admin_key}" \\
     {self.backend_url}/api/knowledge/stats

# Search Knowledge
curl -H "Authorization: Bearer {self.admin_key}" \\
     {self.backend_url}/api/knowledge/search?q=sales
```

### Test Project Management API:
```bash
# Dashboard Summary
curl -H "Authorization: Bearer {self.admin_key}" \\
     {self.backend_url}/api/project-management/dashboard/summary

# OKR Alignment
curl -H "Authorization: Bearer {self.admin_key}" \\
     {self.backend_url}/api/project-management/okr/alignment?quarter=Q1_2024
```

## 🎨 Design System

All dashboards use a consistent design system:
- **Primary Color**: #5E6AD2 (Linear purple)
- **Secondary Color**: #238636 (GitHub green)
- **Background**: #1a1a1a (Dark theme)
- **Surface**: #2a2a2a (Card backgrounds)
- **Font**: Inter, system-ui, sans-serif
- **Border Radius**: 8px
- **Spacing**: 4px, 8px, 16px, 24px, 32px

## 🚨 Troubleshooting

### Backend Connection Issues:
1. Ensure backend is running: `ps aux | grep "python.*main.py"`
2. Check backend logs: `tail -f backend/backend.log`
3. Verify port availability: `lsof -i :8000`

### MCP Server Issues:
1. Check Docker status: `docker ps`
2. View MCP logs: `docker-compose logs [server-name]`
3. Restart specific server: `docker-compose restart [server-name]`

### Integration Issues:
1. Verify environment variables are set
2. Check API keys are valid
3. Test connections individually using curl commands above

## 📈 Next Steps

1. **Customize Dashboards**: Add specific visualizations for your use case
2. **Set Up Alerts**: Configure notifications for critical metrics
3. **Add User Permissions**: Set up role-based access in Retool
4. **Enable Real-time Updates**: Configure WebSocket connections
5. **Create Custom Reports**: Build report generation capabilities

## 🔗 Useful Links

- Retool Documentation: https://docs.retool.com
- Sophia AI Docs: /docs/
- API Documentation: {self.backend_url}/docs
- Support: support@payready.com

---

**Deployment Status**: {"✅ Complete" if all(self.deployment_results.get("prerequisites", {}).values()) else "⚠️ Partial"}
**Generated by**: Sophia AI Deployment System
"""

        return guide

    async def deploy_all(self):
        """Main deployment orchestration"""
        print(f"\n{MAGENTA}{'=' * 60}{RESET}")
        print(f"{MAGENTA}Sophia AI Complete Dashboard Deployment{RESET}")
        print(f"{MAGENTA}{'=' * 60}{RESET}")

        # Check prerequisites
        prereq_status = await self.check_prerequisites()
        self.deployment_results["prerequisites"] = {
            "Backend API": await self._check_backend(),
            "Docker": self._check_docker(),
            "Docker Compose": self._check_docker_compose(),
            "Environment Variables": self._check_env_vars(),
            "Python Dependencies": self._check_python_deps(),
        }

        if not prereq_status:
            print(
                f"\n{RED}Some prerequisites are missing. Please fix them before continuing.{RESET}"
            )
            if not await self._check_backend():
                await self.start_backend_if_needed()

        # Start MCP servers
        self.deployment_results["mcp_servers"] = await self.start_mcp_servers()

        # Check integrations
        self.deployment_results["integrations"] = await self.check_integrations()

        # Generate Retool configurations
        self.deployment_results["configs"] = self.generate_retool_configs()

        # Generate deployment guide
        guide = self.generate_deployment_guide()

        # Save deployment guide
        with open("COMPLETE_DASHBOARD_DEPLOYMENT_GUIDE.md", "w") as f:
            f.write(guide)

        print(
            f"\n{GREEN}✓ Deployment guide saved to: COMPLETE_DASHBOARD_DEPLOYMENT_GUIDE.md{RESET}"
        )

        # Print summary
        print(f"\n{BLUE}{'=' * 60}{RESET}")
        print(f"{BLUE}Deployment Summary{RESET}")
        print(f"{BLUE}{'=' * 60}{RESET}")

        # Prerequisites
        prereq_count = sum(
            1 for v in self.deployment_results["prerequisites"].values() if v
        )
        total_prereq = len(self.deployment_results["prerequisites"])
        print(f"\nPrerequisites: {prereq_count}/{total_prereq} passed")

        # MCP Servers
        mcp_count = sum(1 for v in self.deployment_results["mcp_servers"].values() if v)
        total_mcp = len(self.deployment_results["mcp_servers"])
        print(f"MCP Servers: {mcp_count}/{total_mcp} running")

        # Integrations
        int_count = sum(
            1
            for v in self.deployment_results["integrations"].values()
            if v.get("connected")
        )
        total_int = len(self.deployment_results["integrations"])
        print(f"Integrations: {int_count}/{total_int} connected")

        # Dashboards
        print("Dashboards: 3/3 configurations generated")

        if prereq_count == total_prereq and mcp_count > 0:
            print(
                f"\n{GREEN}✅ Deployment successful! Your dashboards are ready to be created in Retool.{RESET}"
            )
            print(f"\n{CYAN}Next steps:{RESET}")
            print("1. Open Retool and create the three dashboard apps")
            print("2. Import the generated configurations")
            print("3. Configure the API resources as specified in the guide")
            print("4. Start using your Sophia AI dashboards!")
        else:
            print(
                f"\n{YELLOW}⚠️ Deployment completed with warnings. Check the guide for details.{RESET}"
            )


async def main():
    """Main entry point"""
    deployer = ComprehensiveDashboardDeployer()
    await deployer.deploy_all()


if __name__ == "__main__":
    asyncio.run(main())
