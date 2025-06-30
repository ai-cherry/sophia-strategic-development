#!/usr/bin/env python3
"""
Enhanced MCP Orchestration Service for Sophia AI CLI/SDK Integration
Builds upon existing MCP orchestration to include new CLI/SDK enhanced servers
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import httpx
from pydantic import BaseModel

# Import existing orchestration service as base
from backend.services.mcp_orchestration_service import MCPOrchestrationService, MCPServerConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CLISDKEnhancement(BaseModel):
    """Configuration for CLI/SDK enhanced servers"""
    name: str
    cli_command: Optional[str] = None
    sdk_package: Optional[str] = None
    installation_method: str = "pip"  # pip, npm, homebrew, etc.
    required_env_vars: List[str] = []
    capabilities: List[str] = []
    business_value: str = ""
    implementation_phase: str = "phase_1"

class EnhancedMCPOrchestrationService(MCPOrchestrationService):
    """Enhanced MCP orchestration service with CLI/SDK integration"""
    
    def __init__(self):
        super().__init__()
        self.cli_sdk_enhancements = {}
        self.enhanced_config_path = Path("config/enhanced_mcp_ports.json")
        self.phase_1_servers = []
        self.phase_2_servers = []
        
        # Load enhanced configuration
        self._load_enhanced_configuration()
        
    def _load_enhanced_configuration(self):
        """Load enhanced MCP configuration with CLI/SDK servers"""
        try:
            if self.enhanced_config_path.exists():
                with open(self.enhanced_config_path, 'r') as f:
                    enhanced_config = json.load(f)
                
                # Load phase information
                deployment_req = enhanced_config.get("deployment_requirements", {})
                self.phase_1_servers = deployment_req.get("phase_1_servers", [])
                self.phase_2_servers = deployment_req.get("phase_2_servers", [])
                
                # Load CLI/SDK enhanced servers
                servers = enhanced_config.get("servers", {})
                for name, config in servers.items():
                    if isinstance(config, dict) and "port" in config:
                        # This is an enhanced server configuration
                        self._register_enhanced_server(name, config)
                        
                logger.info(f"✅ Loaded enhanced configuration with {len(self.cli_sdk_enhancements)} CLI/SDK servers")
                
            else:
                logger.warning(f"Enhanced configuration not found: {self.enhanced_config_path}")
                
        except Exception as e:
            logger.error(f"❌ Failed to load enhanced configuration: {e}")

    def _register_enhanced_server(self, name: str, config: Dict[str, Any]):
        """Register a CLI/SDK enhanced server"""
        try:
            # Create enhanced server configuration
            enhancement = CLISDKEnhancement(
                name=name,
                required_env_vars=self._get_required_env_vars(name),
                capabilities=config.get("capabilities", []),
                business_value=config.get("business_value", ""),
                implementation_phase=config.get("implementation_phase", "phase_1")
            )
            
            # Create standard MCP server config
            server_config = MCPServerConfig(
                name=name,
                port=config["port"],
                command="uv",
                args=["run", "python", f"mcp-servers/{name}/{name}_mcp_server.py"],
                env={
                    "ENVIRONMENT": "prod",
                    "PULUMI_ORG": "scoobyjava-org",
                    "MCP_SERVER_PORT": str(config["port"])
                },
                capabilities=config.get("capabilities", []),
                auto_start=True
            )
            
            # Add environment variables
            for env_var in enhancement.required_env_vars:
                server_config.env[env_var] = f"${{{env_var}}}"
            
            # Register both configurations
            self.cli_sdk_enhancements[name] = enhancement
            self.servers[name] = server_config
            
            logger.info(f"✅ Registered enhanced server: {name} (Port: {config['port']})")
            
        except Exception as e:
            logger.error(f"❌ Failed to register enhanced server {name}: {e}")

    def _get_required_env_vars(self, server_name: str) -> List[str]:
        """Get required environment variables for a server"""
        env_var_mapping = {
            "apify_intelligence": ["APIFY_API_TOKEN"],
            "huggingface_ai": ["HF_TOKEN"],
            "weaviate_primary": ["WEAVIATE_URL", "WEAVIATE_API_KEY"],
            "arize_phoenix": ["PHOENIX_API_KEY"],
            "n8n_workflow_cli": ["N8N_URL", "N8N_USER", "N8N_PASSWORD"]
        }
        
        return env_var_mapping.get(server_name, [])

    async def initialize_enhanced_servers(self) -> Dict[str, Any]:
        """Initialize CLI/SDK enhanced servers"""
        logger.info("🚀 Initializing CLI/SDK enhanced servers...")
        
        results = {
            "phase_1_results": {},
            "phase_2_results": {},
            "overall_success": True,
            "timestamp": datetime.now().isoformat()
        }
        
        # Initialize Phase 1 servers first
        logger.info("📦 Initializing Phase 1 servers...")
        for server_name in self.phase_1_servers:
            if server_name in self.cli_sdk_enhancements:
                result = await self._initialize_enhanced_server(server_name)
                results["phase_1_results"][server_name] = result
                
                if not result["success"]:
                    results["overall_success"] = False
        
        # Initialize Phase 2 servers if Phase 1 successful
        if results["overall_success"]:
            logger.info("📦 Initializing Phase 2 servers...")
            for server_name in self.phase_2_servers:
                if server_name in self.cli_sdk_enhancements:
                    result = await self._initialize_enhanced_server(server_name)
                    results["phase_2_results"][server_name] = result
                    
                    if not result["success"]:
                        results["overall_success"] = False
        else:
            logger.warning("⚠️ Skipping Phase 2 due to Phase 1 failures")
        
        # Summary
        total_servers = len(self.phase_1_servers) + len(self.phase_2_servers)
        successful_servers = sum(1 for phase_results in [results["phase_1_results"], results["phase_2_results"]] 
                               for result in phase_results.values() if result["success"])
        
        logger.info(f"📊 Enhanced server initialization complete: {successful_servers}/{total_servers} successful")
        
        return results

    async def _initialize_enhanced_server(self, server_name: str) -> Dict[str, Any]:
        """Initialize a single enhanced server"""
        logger.info(f"🚀 Initializing enhanced server: {server_name}")
        
        try:
            enhancement = self.cli_sdk_enhancements[server_name]
            server_config = self.servers[server_name]
            
            # Check environment variables
            missing_env_vars = []
            for env_var in enhancement.required_env_vars:
                if not os.getenv(env_var):
                    missing_env_vars.append(env_var)
            
            if missing_env_vars:
                logger.warning(f"⚠️ Missing environment variables for {server_name}: {missing_env_vars}")
            
            # Attempt to start server
            start_result = await self._start_enhanced_server(server_name, server_config)
            
            if start_result["success"]:
                # Verify server health
                health_result = await self._check_enhanced_server_health(server_name, server_config.port)
                
                return {
                    "success": health_result["healthy"],
                    "server_name": server_name,
                    "port": server_config.port,
                    "capabilities": enhancement.capabilities,
                    "business_value": enhancement.business_value,
                    "health_status": health_result,
                    "missing_env_vars": missing_env_vars,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "server_name": server_name,
                    "error": start_result.get("error", "Unknown error"),
                    "missing_env_vars": missing_env_vars,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize {server_name}: {e}")
            return {
                "success": False,
                "server_name": server_name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def _start_enhanced_server(self, server_name: str, config: MCPServerConfig) -> Dict[str, Any]:
        """Start an enhanced server with CLI/SDK capabilities"""
        try:
            # Use existing server starting logic from parent class
            # This would call the actual server startup process
            
            # For now, simulate server startup
            logger.info(f"🚀 Starting {server_name} on port {config.port}")
            
            # In a real implementation, this would:
            # 1. Check if server script exists
            # 2. Start the server process
            # 3. Wait for startup confirmation
            
            return {
                "success": True,
                "server_name": server_name,
                "port": config.port,
                "process_id": f"simulated_pid_{config.port}"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to start {server_name}: {e}")
            return {
                "success": False,
                "server_name": server_name,
                "error": str(e)
            }

    async def _check_enhanced_server_health(self, server_name: str, port: int) -> Dict[str, Any]:
        """Check health of an enhanced server"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"http://localhost:{port}/health")
                
                if response.status_code == 200:
                    health_data = response.json()
                    return {
                        "healthy": True,
                        "server_name": server_name,
                        "port": port,
                        "response_time_ms": response.elapsed.total_seconds() * 1000,
                        "health_data": health_data,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {
                        "healthy": False,
                        "server_name": server_name,
                        "port": port,
                        "error": f"HTTP {response.status_code}",
                        "timestamp": datetime.now().isoformat()
                    }
                    
        except Exception as e:
            return {
                "healthy": False,
                "server_name": server_name,
                "port": port,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def route_enhanced_request(self, 
                                   server_type: str, 
                                   request_data: Dict[str, Any], 
                                   priority: str = "standard") -> Dict[str, Any]:
        """Route request through enhanced MCP servers with CLI/SDK capabilities"""
        
        try:
            # Check if this is an enhanced server
            if server_type in self.cli_sdk_enhancements:
                enhancement = self.cli_sdk_enhancements[server_type]
                
                logger.info(f"🎯 Routing enhanced request to {server_type}")
                
                # Add enhancement context to request
                enhanced_request = {
                    **request_data,
                    "enhancement_info": {
                        "capabilities": enhancement.capabilities,
                        "business_value": enhancement.business_value,
                        "implementation_phase": enhancement.implementation_phase
                    }
                }
                
                # Route through existing orchestration with enhancements
                result = await super().route_request(server_type, enhanced_request, priority)
                
                # Add enhancement metadata to response
                if "enhancement_applied" not in result:
                    result["enhancement_applied"] = {
                        "server": server_type,
                        "capabilities_used": enhancement.capabilities,
                        "business_value": enhancement.business_value
                    }
                
                return result
            else:
                # Route through standard orchestration
                return await super().route_request(server_type, request_data, priority)
                
        except Exception as e:
            logger.error(f"❌ Enhanced routing failed for {server_type}: {e}")
            return {
                "success": False,
                "error": str(e),
                "server_type": server_type,
                "timestamp": datetime.now().isoformat()
            }

    async def get_enhanced_server_status(self) -> Dict[str, Any]:
        """Get comprehensive status of all enhanced servers"""
        
        status = {
            "enhanced_servers": {},
            "phase_1_servers": [],
            "phase_2_servers": [],
            "overall_health": "unknown",
            "timestamp": datetime.now().isoformat()
        }
        
        healthy_servers = 0
        total_enhanced_servers = len(self.cli_sdk_enhancements)
        
        # Check each enhanced server
        for server_name, enhancement in self.cli_sdk_enhancements.items():
            if server_name in self.servers:
                server_config = self.servers[server_name]
                health_result = await self._check_enhanced_server_health(server_name, server_config.port)
                
                status["enhanced_servers"][server_name] = {
                    "health": health_result,
                    "capabilities": enhancement.capabilities,
                    "business_value": enhancement.business_value,
                    "implementation_phase": enhancement.implementation_phase,
                    "port": server_config.port
                }
                
                if health_result["healthy"]:
                    healthy_servers += 1
                    
                # Categorize by phase
                if enhancement.implementation_phase == "phase_1":
                    status["phase_1_servers"].append(server_name)
                else:
                    status["phase_2_servers"].append(server_name)
        
        # Determine overall health
        if healthy_servers == total_enhanced_servers:
            status["overall_health"] = "healthy"
        elif healthy_servers > 0:
            status["overall_health"] = "degraded"
        else:
            status["overall_health"] = "unhealthy"
        
        status["health_summary"] = {
            "healthy_servers": healthy_servers,
            "total_enhanced_servers": total_enhanced_servers,
            "health_percentage": (healthy_servers / total_enhanced_servers * 100) if total_enhanced_servers > 0 else 0
        }
        
        return status

    async def validate_cli_sdk_requirements(self) -> Dict[str, Any]:
        """Validate CLI/SDK requirements for enhanced servers"""
        
        validation_results = {
            "requirements_met": {},
            "missing_requirements": {},
            "installation_commands": {},
            "overall_ready": True,
            "timestamp": datetime.now().isoformat()
        }
        
        for server_name, enhancement in self.cli_sdk_enhancements.items():
            server_validation = {
                "env_vars_present": [],
                "env_vars_missing": [],
                "cli_available": False,
                "sdk_available": False
            }
            
            # Check environment variables
            for env_var in enhancement.required_env_vars:
                if os.getenv(env_var):
                    server_validation["env_vars_present"].append(env_var)
                else:
                    server_validation["env_vars_missing"].append(env_var)
                    validation_results["overall_ready"] = False
            
            # Check CLI availability (simplified check)
            if enhancement.cli_command:
                cli_check = await self._check_cli_availability(enhancement.cli_command)
                server_validation["cli_available"] = cli_check
                
                if not cli_check:
                    validation_results["overall_ready"] = False
            
            # Store results
            validation_results["requirements_met"][server_name] = server_validation
            
            # Generate installation commands if needed
            if server_validation["env_vars_missing"] or not server_validation.get("cli_available", True):
                validation_results["installation_commands"][server_name] = self._generate_installation_commands(server_name, enhancement)
        
        return validation_results

    async def _check_cli_availability(self, cli_command: str) -> bool:
        """Check if a CLI command is available"""
        try:
            process = await asyncio.create_subprocess_exec(
                "which", cli_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.wait()
            return process.returncode == 0
            
        except Exception:
            return False

    def _generate_installation_commands(self, server_name: str, enhancement: CLISDKEnhancement) -> List[str]:
        """Generate installation commands for a server's requirements"""
        commands = []
        
        # CLI installation commands
        cli_installations = {
            "apify_intelligence": ["npm install -g apify-cli"],
            "huggingface_ai": ["pip install transformers sentence-transformers"],
            "weaviate_primary": ["brew install weaviate-cli", "pip install weaviate-client"],
            "arize_phoenix": ["pip install arize-phoenix"],
            "n8n_workflow_cli": ["npm install -g n8n"]
        }
        
        if server_name in cli_installations:
            commands.extend(cli_installations[server_name])
        
        # Environment variable setup
        if enhancement.required_env_vars:
            commands.append(f"# Set environment variables: {', '.join(enhancement.required_env_vars)}")
        
        return commands

# Convenience functions for integration
async def initialize_enhanced_mcp_system() -> Dict[str, Any]:
    """Initialize the complete enhanced MCP system"""
    logger.info("🚀 Initializing Enhanced MCP System with CLI/SDK integrations...")
    
    orchestrator = EnhancedMCPOrchestrationService()
    
    # Validate requirements first
    validation = await orchestrator.validate_cli_sdk_requirements()
    
    if not validation["overall_ready"]:
        logger.warning("⚠️ Some CLI/SDK requirements not met")
        return {
            "success": False,
            "error": "Requirements validation failed",
            "validation_results": validation
        }
    
    # Initialize enhanced servers
    initialization_results = await orchestrator.initialize_enhanced_servers()
    
    return {
        "success": initialization_results["overall_success"],
        "initialization_results": initialization_results,
        "validation_results": validation,
        "timestamp": datetime.now().isoformat()
    }

async def get_enhanced_system_status() -> Dict[str, Any]:
    """Get comprehensive status of enhanced MCP system"""
    orchestrator = EnhancedMCPOrchestrationService()
    return await orchestrator.get_enhanced_server_status()

# Main execution for testing
async def main():
    """Main function for testing enhanced orchestration"""
    
    # Initialize system
    init_result = await initialize_enhanced_mcp_system()
    print(f"Initialization result: {json.dumps(init_result, indent=2)}")
    
    # Get status
    status_result = await get_enhanced_system_status()
    print(f"System status: {json.dumps(status_result, indent=2)}")

if __name__ == "__main__":
    asyncio.run(main()) 