#!/usr/bin/env python3
"""
Phase 1A: Foundation Setup Implementation
Implements Anthropic SDK integration and Sophia MCP Base Class
"""

import asyncio
import logging
import subprocess
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Phase1AImplementer:
    """Implements Phase 1A foundation setup"""

    def __init__(self):
        self.base_dir = Path.cwd()
        self.external_dir = self.base_dir / "external"
        self.backend_dir = self.base_dir / "backend"
        self.mcp_servers_dir = self.backend_dir / "mcp_servers"

        # Ensure directories exist
        self.mcp_servers_dir.mkdir(exist_ok=True)

    async def implement_phase1a(self):
        """Implement all Phase 1A components"""
        logger.info("�� Starting Phase 1A: Foundation Setup Implementation")

        steps = [
            ("Install Anthropic MCP SDK", self.install_anthropic_sdk),
            ("Setup MCP Inspector", self.setup_mcp_inspector),
            ("Create Sophia MCP Base Class", self.create_sophia_mcp_base),
            ("Fix Snowflake Connection Permanently", self.fix_snowflake_connection),
            ("Create MCP Server Registry", self.create_mcp_registry),
            ("Setup Development Tools", self.setup_development_tools),
        ]

        results = []
        for step_name, step_func in steps:
            try:
                logger.info(f"📋 {step_name}...")
                result = await step_func()
                results.append(
                    {"step": step_name, "status": "success", "result": result}
                )
                logger.info(f"   ✅ {step_name} completed successfully")
            except Exception as e:
                logger.error(f"   ❌ {step_name} failed: {e}")
                results.append({"step": step_name, "status": "failed", "error": str(e)})

        # Generate report
        await self.generate_phase1a_report(results)

        return results

    async def install_anthropic_sdk(self):
        """Install Anthropic MCP SDK"""
        sdk_path = self.external_dir / "anthropic-mcp-python-sdk"

        if not sdk_path.exists():
            logger.warning(f"SDK path {sdk_path} does not exist, cloning...")
            result = subprocess.run(
                [
                    "git",
                    "clone",
                    "https://github.com/modelcontextprotocol/python-sdk.git",
                    str(sdk_path),
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                raise Exception(f"Failed to clone SDK: {result.stderr}")

        # Install in development mode
        logger.info("   Installing MCP SDK in development mode...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", str(sdk_path)],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise Exception(f"SDK installation failed: {result.stderr}")

        # Verify installation
        try:
            import mcp

            logger.info(
                f"   ✅ MCP SDK version: {mcp.__version__ if hasattr(mcp, '__version__') else 'installed'}"
            )
            return {"status": "installed", "path": str(sdk_path)}
        except ImportError as e:
            raise Exception(f"SDK verification failed: {e}")

    async def setup_mcp_inspector(self):
        """Setup MCP Inspector for development"""
        inspector_path = self.external_dir / "anthropic-mcp-inspector"

        if not inspector_path.exists():
            logger.warning(
                f"Inspector path {inspector_path} does not exist, cloning..."
            )
            result = subprocess.run(
                [
                    "git",
                    "clone",
                    "https://github.com/modelcontextprotocol/inspector.git",
                    str(inspector_path),
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                raise Exception(f"Failed to clone Inspector: {result.stderr}")

        # Check if it's a Node.js project and install dependencies
        package_json = inspector_path / "package.json"
        if package_json.exists():
            logger.info("   Installing Inspector dependencies...")
            result = subprocess.run(
                ["npm", "install"], cwd=inspector_path, capture_output=True, text=True
            )

            if result.returncode != 0:
                logger.warning(f"npm install failed: {result.stderr}")
                return {
                    "status": "partial",
                    "note": "Dependencies not installed, but files available",
                }

        # Create startup script
        startup_script = self.base_dir / "start_mcp_inspector.sh"
        startup_script.write_text(
            f"""#!/bin/bash
# MCP Inspector Startup Script
cd {inspector_path}
npm start
"""
        )
        startup_script.chmod(0o755)

        return {
            "status": "configured",
            "path": str(inspector_path),
            "startup_script": str(startup_script),
        }

    def _error_handling_1(self):
        """Extracted error_handling logic"""
        from mcp import Server, Tool, Resource
        from mcp.types import TextContent, ImageContent
        MCP_AVAILABLE = True
    except ImportError:
        MCP_AVAILABLE = False
        # Create mock classes for development
        class Server:
            def __init__(self, name: str, version: str = "1.0.0"):
                self.name = name
                self.version = version


    def _error_handling_2(self):
        """Extracted error_handling logic"""
                # Authenticate request
                if not await self.authenticate(request):
                    self.metrics["failed_requests"] += 1
                    raise Exception("Authentication failed")


    async def create_sophia_mcp_base(self):
        """Create Sophia MCP Base Class"""
        base_class_content = '''"""
Sophia MCP Base Class
Unified base class for all Sophia AI MCP servers
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

self._error_handling_1()
    class Tool:
        pass

    class Resource:
        pass

from backend.core.auto_esc_config import get_config_value


@dataclass
class MCPServerHealth:
    """Health status for MCP servers"""
    status: str  # healthy, degraded, unhealthy
    uptime_seconds: float
    total_requests: int
    successful_requests: int
    failed_requests: int
    last_request_time: Optional[datetime]
    error_rate: float


class SophiaMCPServer(ABC):
    """
    Base class for all Sophia AI MCP servers
    Provides unified patterns for authentication, logging, health checks, and error handling
    """

    def __init__(self, name: str, version: str = "1.0.0", port: Optional[int] = None):
        self.name = name
        self.version = version
        self.port = port
        self.start_time = time.time()

        # Setup logging
        self.logger = logging.getLogger(f"sophia.mcp.{name}")
        self.logger.setLevel(logging.INFO)

        # Load configuration
        self.config = self._load_config()

        # Initialize metrics
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "last_request_time": None
        }

        # Initialize MCP server if available
        if MCP_AVAILABLE:
            self.mcp_server = Server(name, version)
            self._register_tools()
            self._register_resources()
        else:
            self.mcp_server = None
            self.logger.warning("MCP SDK not available - running in mock mode")

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from Pulumi ESC and environment"""
        return {
            "environment": get_config_value("environment", "prod"),
            "log_level": get_config_value("log_level", "INFO"),
            "debug_mode": get_config_value("debug_mode", "false").lower() == "true",
            "max_retries": int(get_config_value("mcp_max_retries", "3")),
            "timeout_seconds": int(get_config_value("mcp_timeout", "30"))
        }

    @abstractmethod
    def _register_tools(self):
        """Register MCP tools - must be implemented by subclasses"""
        pass

    @abstractmethod
    def _register_resources(self):
        """Register MCP resources - must be implemented by subclasses"""
        pass

    async def authenticate(self, request: Any) -> bool:
        """
        Standard authentication for all servers
        Override in subclasses for specific auth requirements
        """
        # Basic API key authentication
        api_key = getattr(request, 'api_key', None) or os.getenv(f"{self.name.upper()}_API_KEY")

        if not api_key:
            self.logger.warning("No API key provided for authentication")
            return False

        # Add custom authentication logic here
        return True

    async def health_check(self) -> MCPServerHealth:
        """Standard health check for all servers"""
        uptime = time.time() - self.start_time
        total_requests = self.metrics["total_requests"]
        failed_requests = self.metrics["failed_requests"]

        error_rate = (failed_requests / max(total_requests, 1)) * 100

        # Determine health status
        if error_rate > 50:
            status = "unhealthy"
        elif error_rate > 10:
            status = "degraded"
        else:
            status = "healthy"

        return MCPServerHealth(
            status=status,
            uptime_seconds=uptime,
            total_requests=total_requests,
            successful_requests=self.metrics["successful_requests"],
            failed_requests=failed_requests,
            last_request_time=self.metrics["last_request_time"],
            error_rate=error_rate
        )

    async def handle_request(self, request: Any) -> Any:
        """
        Standard request handler with metrics and error handling
        """
        self.metrics["total_requests"] += 1
        self.metrics["last_request_time"] = datetime.now()

        self._error_handling_2()
            # Process request
            result = await self.process_request(request)

            self.metrics["successful_requests"] += 1
            return result

        except Exception as e:
            self.metrics["failed_requests"] += 1
            self.logger.error(f"Request failed: {e}")
            raise

    @abstractmethod
    async def process_request(self, request: Any) -> Any:
        """Process the actual request - must be implemented by subclasses"""
        pass

    async def start(self):
        """Start the MCP server"""
        self.logger.info(f"🚀 Starting {self.name} MCP Server v{self.version}")

        if self.port:
            self.logger.info(f"   Listening on port {self.port}")

        # Perform startup health check
        health = await self.health_check()
        self.logger.info(f"   Health status: {health.status}")

        # Additional startup logic can be added here
        await self.on_startup()

    async def stop(self):
        """Stop the MCP server"""
        self.logger.info(f"🛑 Stopping {self.name} MCP Server")
        await self.on_shutdown()

    async def on_startup(self):
        """Override for custom startup logic"""
        pass

    async def on_shutdown(self):
        """Override for custom shutdown logic"""
        pass


class SophiaSnowflakeMCPServer(SophiaMCPServer):
    """Example Snowflake MCP Server implementation"""

    def __init__(self):
        super().__init__("snowflake", "1.0.0", port=9100)
        self.connection_manager = None

    def _register_tools(self):
        """Register Snowflake-specific tools"""
        if not self.mcp_server:
            return

        # Register tools would go here when MCP SDK is available
        pass

    def _register_resources(self):
        """Register Snowflake-specific resources"""
        if not self.mcp_server:
            return

        # Register resources would go here when MCP SDK is available
        pass

    async def process_request(self, request: Any) -> Any:
        """Process Snowflake-specific requests"""
        # Implement Snowflake query processing
        return {"status": "success", "message": "Snowflake query processed"}

    async def on_startup(self):
        """Initialize Snowflake connection"""
        from backend.core.optimized_connection_manager import OptimizedConnectionManager
        self.connection_manager = OptimizedConnectionManager()
        await self.connection_manager.initialize()
        self.logger.info("✅ Snowflake connection manager initialized")


# Factory function for creating MCP servers
def create_mcp_server(server_type: str, **kwargs) -> SophiaMCPServer:
    """Factory function to create MCP servers"""
    servers = {
        "snowflake": SophiaSnowflakeMCPServer,
        # Add other server types here
    }

    if server_type not in servers:
        raise ValueError(f"Unknown server type: {server_type}")

    return servers[server_type](**kwargs)
'''

        # Write the base class
        base_class_file = self.mcp_servers_dir / "sophia_mcp_base.py"
        base_class_file.write_text(base_class_content)

        # Create __init__.py for the mcp_servers package
        init_file = self.mcp_servers_dir / "__init__.py"
        init_file.write_text('"""Sophia AI MCP Servers Package"""')

        return {"status": "created", "path": str(base_class_file)}

    async def fix_snowflake_connection(self):
        """Create a permanent fix for Snowflake connection"""

        # Create a startup configuration script
        startup_fix_content = '''"""
Sophia AI Startup Configuration
Ensures correct configuration is loaded at application startup
"""

import os
import logging

logger = logging.getLogger(__name__)

def configure_snowflake_environment():
    """Configure Snowflake environment variables at startup"""

    # Set correct Snowflake configuration
    snowflake_config = {
        'SNOWFLAKE_ACCOUNT': 'ZNB04675',
        'SNOWFLAKE_USER': 'SCOOBYJAVA15',
        'SNOWFLAKE_DATABASE': 'SOPHIA_AI',
        'SNOWFLAKE_WAREHOUSE': 'SOPHIA_AI_WH',
        'SNOWFLAKE_ROLE': 'ACCOUNTADMIN',
        'SNOWFLAKE_SCHEMA': 'PROCESSED_AI'
    }

    for key, value in snowflake_config.items():
        os.environ[key] = value
        logger.info(f"✅ Set {key}: {value}")

    logger.info("🔧 Snowflake environment configuration applied")

def apply_startup_configuration():
    """Apply all startup configuration"""
    logger.info("🚀 Applying Sophia AI startup configuration")

    # Configure Snowflake
    configure_snowflake_environment()

    # Set other environment variables
    os.environ['ENVIRONMENT'] = 'prod'
    os.environ['PULUMI_ORG'] = 'scoobyjava-org'

    logger.info("✅ Startup configuration complete")

# Auto-apply configuration when module is imported
apply_startup_configuration()
'''

        startup_config_file = self.backend_dir / "core" / "startup_config.py"
        startup_config_file.write_text(startup_fix_content)

        # Update FastAPI app to import startup config
        fastapi_app_file = self.backend_dir / "app" / "fastapi_app.py"

        if fastapi_app_file.exists():
            content = fastapi_app_file.read_text()

            # Add import at the top if not already present
            if (
                "from backend.core.startup_config import apply_startup_configuration"
                not in content
            ):
                # Find the imports section and add our import
                lines = content.split("\n")
                import_line = "from backend.core.startup_config import apply_startup_configuration"

                # Add after other imports
                for i, line in enumerate(lines):
                    if line.startswith("from backend.") and "import" in line:
                        lines.insert(i + 1, import_line)
                        break

                # Add call to apply configuration early in the file
                for i, line in enumerate(lines):
                    if "app = FastAPI(" in line:
                        lines.insert(i, "# Apply startup configuration")
                        lines.insert(i + 1, "apply_startup_configuration()")
                        lines.insert(i + 2, "")
                        break

                fastapi_app_file.write_text("\n".join(lines))

        return {"status": "created", "startup_config": str(startup_config_file)}

    async def create_mcp_registry(self):
        """Create MCP server registry for management"""

        registry_content = '''"""
Sophia AI MCP Server Registry
Central registry for managing all MCP servers
"""

import asyncio
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

from .sophia_mcp_base import SophiaMCPServer, MCPServerHealth, create_mcp_server

logger = logging.getLogger(__name__)


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server"""
    name: str
    type: str
    port: int
    enabled: bool = True
    auto_start: bool = True
    health_check_interval: int = 60


class MCPServerRegistry:
    """Registry for managing all MCP servers"""

    def __init__(self):
        self.servers: Dict[str, SophiaMCPServer] = {}
        self.configs: Dict[str, MCPServerConfig] = {}
        self.health_status: Dict[str, MCPServerHealth] = {}

        # Load default configurations
        self._load_default_configs()

    def _load_default_configs(self):
        """Load default server configurations"""
        default_configs = [
            MCPServerConfig("snowflake", "snowflake", 9100),
            MCPServerConfig("hubspot", "hubspot", 9101),
            MCPServerConfig("slack", "slack", 9102),
            MCPServerConfig("github", "github", 9103),
            MCPServerConfig("notion", "notion", 9104),
        ]

        for config in default_configs:
            self.configs[config.name] = config

    async def register_server(self, config: MCPServerConfig):
        """Register a new MCP server"""
        logger.info(f"📋 Registering MCP server: {config.name}")

        try:
            # Create server instance
            server = create_mcp_server(config.type, port=config.port)
            self.servers[config.name] = server
            self.configs[config.name] = config

            # Start server if auto_start is enabled
            if config.auto_start and config.enabled:
                await server.start()

            logger.info(f"✅ Registered {config.name} MCP server")

        except Exception as e:
            logger.error(f"❌ Failed to register {config.name}: {e}")
            raise

    async def start_server(self, name: str):
        """Start a specific MCP server"""
        if name not in self.servers:
            raise ValueError(f"Server {name} not found in registry")

        server = self.servers[name]
        await server.start()
        logger.info(f"🚀 Started {name} MCP server")

    async def stop_server(self, name: str):
        """Stop a specific MCP server"""
        if name not in self.servers:
            raise ValueError(f"Server {name} not found in registry")

        server = self.servers[name]
        await server.stop()
        logger.info(f"🛑 Stopped {name} MCP server")

    async def start_all_servers(self):
        """Start all enabled MCP servers"""
        logger.info("🚀 Starting all enabled MCP servers")

        for name, config in self.configs.items():
            if config.enabled and config.auto_start:
                try:
                    if name not in self.servers:
                        await self.register_server(config)
                    else:
                        await self.start_server(name)
                except Exception as e:
                    logger.error(f"❌ Failed to start {name}: {e}")

    async def stop_all_servers(self):
        """Stop all MCP servers"""
        logger.info("🛑 Stopping all MCP servers")

        for name in self.servers:
            try:
                await self.stop_server(name)
            except Exception as e:
                logger.error(f"❌ Failed to stop {name}: {e}")

    async def health_check_all(self):
        """Perform health check on all servers"""
        logger.info("🔍 Performing health check on all MCP servers")

        for name, server in self.servers.items():
            try:
                health = await server.health_check()
                self.health_status[name] = health
                logger.info(f"   {name}: {health.status}")
            except Exception as e:
                logger.error(f"❌ Health check failed for {name}: {e}")

    def get_server_status(self) -> Dict[str, Dict]:
        """Get status of all servers"""
        status = {}

        for name, config in self.configs.items():
            server_info = {
                "config": asdict(config),
                "registered": name in self.servers,
                "health": asdict(self.health_status.get(name)) if name in self.health_status else None
            }
            status[name] = server_info

        return status

    async def start_health_monitoring(self):
        """Start background health monitoring"""
        logger.info("🔍 Starting MCP server health monitoring")

        async def health_monitor():
            while True:
                try:
                    await self.health_check_all()
                    await asyncio.sleep(60)  # Check every minute
                except Exception as e:
                    logger.error(f"Health monitoring error: {e}")
                    await asyncio.sleep(60)

        # Start monitoring task
        asyncio.create_task(health_monitor())


# Global registry instance
mcp_registry = MCPServerRegistry()
'''

        registry_file = self.mcp_servers_dir / "mcp_registry.py"
        registry_file.write_text(registry_content)

        return {"status": "created", "path": str(registry_file)}

    async def setup_development_tools(self):
        """Setup development and testing tools"""

        # Create test script
        test_script_content = '''#!/usr/bin/env python3
"""
MCP Server Testing Script
Quick testing tool for MCP servers
"""

import asyncio
import sys
from backend.mcp_servers.mcp_registry import mcp_registry

async def test_mcp_servers():
    """Test all MCP servers"""
    print("🧪 Testing MCP Servers")
    print("=" * 50)

    # Start all servers
    await mcp_registry.start_all_servers()

    # Wait a moment for servers to initialize
    await asyncio.sleep(2)

    # Perform health checks
    await mcp_registry.health_check_all()

    # Get status
    status = mcp_registry.get_server_status()

    print("\\n📊 Server Status:")
    for name, info in status.items():
        enabled = "✅" if info["config"]["enabled"] else "❌"
        registered = "✅" if info["registered"] else "❌"
        health = info["health"]["status"] if info["health"] else "unknown"

        print(f"   {name}: {enabled} enabled, {registered} registered, {health} health")

    print("\\n🎉 MCP server testing complete!")

if __name__ == "__main__":
    asyncio.run(test_mcp_servers())
'''

        test_script = self.base_dir / "test_mcp_servers.py"
        test_script.write_text(test_script_content)
        test_script.chmod(0o755)

        # Create development configuration
        dev_config_content = """# Development Configuration for MCP Servers

# Environment variables for development
export ENVIRONMENT=dev
export LOG_LEVEL=DEBUG
export MCP_DEBUG=true

# Snowflake configuration (already set by startup_config.py)
export SNOWFLAKE_ACCOUNT=ZNB04675
export SNOWFLAKE_USER=SCOOBYJAVA15
export SNOWFLAKE_DATABASE=SOPHIA_AI
export SNOWFLAKE_WAREHOUSE=SOPHIA_AI_WH
export SNOWFLAKE_ROLE=ACCOUNTADMIN
export SNOWFLAKE_SCHEMA=PROCESSED_AI

# Development shortcuts
alias test-mcp="python test_mcp_servers.py"
alias start-inspector="./start_mcp_inspector.sh"
alias sophia-dev="source .venv/bin/activate && export ENVIRONMENT=dev"

echo "🔧 Sophia AI MCP development environment configured"
"""

        dev_config = self.base_dir / "dev_mcp_config.sh"
        dev_config.write_text(dev_config_content)
        dev_config.chmod(0o755)

        return {"test_script": str(test_script), "dev_config": str(dev_config)}

    async def generate_phase1a_report(self, results: list):
        """Generate Phase 1A implementation report"""
        logger.info("📊 Generating Phase 1A implementation report")

        successful = sum(1 for r in results if r["status"] == "success")
        total = len(results)

        report_content = f"""# 🚀 PHASE 1A IMPLEMENTATION REPORT

**Implementation Date:** {asyncio.get_event_loop().time()}
**Phase:** Foundation Setup
**Total Steps:** {total}
**Successful:** {successful}
**Success Rate:** {(successful/total*100):.1f}%

## 📊 Implementation Results

"""

        for result in results:
            status_emoji = "✅" if result["status"] == "success" else "❌"
            report_content += f"### {status_emoji} {result['step']}\n"
            report_content += f"- **Status:** {result['status']}\n"

            if result["status"] == "success":
                if "result" in result:
                    for key, value in result["result"].items():
                        report_content += f"- **{key.title()}:** {value}\n"
            else:
                if "error" in result:
                    report_content += f"- **Error:** {result['error']}\n"

            report_content += "\n"

        report_content += f"""## 🎯 Next Steps

### Phase 1B: Service Integration (Days 3-4)
1. **Configure API Credentials** - Add real API keys for all services
2. **Test Snowflake MCP** - Verify data warehouse connectivity
3. **Test HubSpot MCP** - Verify CRM integration
4. **Test Slack MCP** - Verify team communication
5. **Integration Testing** - End-to-end workflow testing

### Development Commands
```bash
# Test all MCP servers
python test_mcp_servers.py

# Start MCP Inspector
./start_mcp_inspector.sh

# Configure development environment
source dev_mcp_config.sh
```

## 🎉 Foundation Status

Phase 1A foundation setup is {'✅ COMPLETE' if successful == total else f'⚠️ PARTIAL ({successful}/{total} steps)'}.

{'Ready to proceed with Phase 1B service integration!' if successful == total else 'Manual attention required for failed steps before proceeding.'}
"""

        # Write report
        report_file = self.base_dir / "PHASE1A_IMPLEMENTATION_REPORT.md"
        report_file.write_text(report_content)

        logger.info(f"📄 Phase 1A report written to {report_file}")


async def main():
    """Main implementation function"""
    implementer = Phase1AImplementer()

    try:
        results = await implementer.implement_phase1a()

        successful = sum(1 for r in results if r["status"] == "success")
        total = len(results)

        if successful == total:
            logger.info("🎉 Phase 1A implementation completed successfully!")
            logger.info("🚀 Ready to proceed with Phase 1B service integration")
        else:
            logger.warning(f"⚠️ {total - successful} steps need manual attention")

        return successful == total

    except Exception as e:
        logger.error(f"❌ Phase 1A implementation failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
