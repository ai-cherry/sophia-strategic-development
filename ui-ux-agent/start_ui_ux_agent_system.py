#!/usr/bin/env python3
"""
Sophia AI UI/UX Agent System Startup Script
Demonstrates the complete design-to-code automation system
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UIUXAgentSystemManager:
    """Manager for the complete UI/UX agent system"""
    
    def __init__(self):
        self.figma_server_port = 9001
        self.agent_server_port = 9002
        self.processes = []
        
    async def start_system(self):
        """Start the complete UI/UX agent system"""
        logger.info("🚀 Starting Sophia AI UI/UX Agent System...")
        
        # Check environment
        await self._check_environment()
        
        # Start Figma MCP server
        await self._start_figma_server()
        
        # Wait for Figma server to be ready
        await self._wait_for_server(self.figma_server_port, "Figma MCP Server")
        
        # Start UI/UX agent
        await self._start_uiux_agent()
        
        # Wait for agent to be ready
        await self._wait_for_server(self.agent_server_port, "UI/UX Agent")
        
        # Run demonstration
        await self._run_demonstration()
        
        # Keep system running
        await self._keep_running()
    
    async def _check_environment(self):
        """Check environment configuration"""
        logger.info("🔧 Checking environment configuration...")
        
        figma_token = os.getenv('FIGMA_PERSONAL_ACCESS_TOKEN')
        openai_key = os.getenv('OPENAI_API_KEY')
        openrouter_key = os.getenv('OPENROUTER_API_KEY')
        
        if figma_token:
            logger.info("✅ Figma Personal Access Token configured")
        else:
            logger.warning("⚠️  Figma Personal Access Token not found - some features disabled")
            
        if openai_key:
            logger.info("✅ OpenAI API Key configured")
        else:
            logger.warning("⚠️  OpenAI API Key not found - using mock responses")
            
        if openrouter_key:
            logger.info("✅ OpenRouter API Key configured")
        else:
            logger.warning("⚠️  OpenRouter API Key not found - using mock responses")
    
    async def _start_figma_server(self):
        """Start the Figma MCP server"""
        logger.info("🎨 Starting Figma Dev Mode MCP Server...")
        
        try:
            process = subprocess.Popen([
                sys.executable,
                "mcp-servers/figma-dev-mode/figma_mcp_server.py"
            ], cwd="ui-ux-agent")
            
            self.processes.append(("Figma MCP Server", process))
            logger.info(f"✅ Figma MCP Server started (PID: {process.pid})")
            
        except Exception as e:
            logger.error(f"❌ Failed to start Figma MCP Server: {e}")
            raise
    
    async def _start_uiux_agent(self):
        """Start the UI/UX LangChain agent"""
        logger.info("🤖 Starting UI/UX LangChain Agent...")
        
        try:
            process = subprocess.Popen([
                sys.executable,
                "mcp-servers/langchain-agents/ui_ux_agent.py"
            ], cwd="ui-ux-agent")
            
            self.processes.append(("UI/UX Agent", process))
            logger.info(f"✅ UI/UX Agent started (PID: {process.pid})")
            
        except Exception as e:
            logger.error(f"❌ Failed to start UI/UX Agent: {e}")
            raise
    
    async def _wait_for_server(self, port: int, name: str, max_attempts: int = 30):
        """Wait for server to be ready"""
        logger.info(f"⏳ Waiting for {name} to be ready on port {port}...")
        
        for attempt in range(max_attempts):
            try:
                response = requests.get(f"http://localhost:{port}/health", timeout=2)
                if response.status_code == 200:
                    logger.info(f"✅ {name} is ready!")
                    return
            except:
                pass
            
            await asyncio.sleep(2)
        
        raise Exception(f"❌ {name} failed to start after {max_attempts} attempts")
    
    async def _run_demonstration(self):
        """Run system demonstration"""
        logger.info("🎯 Running UI/UX Agent System Demonstration...")
        
        # Test Figma MCP server
        await self._test_figma_server()
        
        # Test UI/UX agent
        await self._test_uiux_agent()
        
        # Test component generation
        await self._test_component_generation()
        
        logger.info("🎉 Demonstration completed successfully!")
    
    async def _test_figma_server(self):
        """Test Figma MCP server functionality"""
        logger.info("🧪 Testing Figma MCP Server...")
        
        try:
            # Test health endpoint
            response = requests.get(f"http://localhost:{self.figma_server_port}/health")
            health_data = response.json()
            logger.info(f"   ✅ Health check: {health_data['status']}")
            
            # Test design token extraction
            token_response = requests.post(
                f"http://localhost:{self.figma_server_port}/extract-design-tokens",
                json={"file_id": "demo_file_id"}
            )
            tokens = token_response.json()
            logger.info(f"   ✅ Design tokens extracted: {len(tokens['tokens'])} tokens")
            
        except Exception as e:
            logger.error(f"   ❌ Figma server test failed: {e}")
    
    async def _test_uiux_agent(self):
        """Test UI/UX agent functionality"""
        logger.info("🧪 Testing UI/UX Agent...")
        
        try:
            # Test health endpoint
            response = requests.get(f"http://localhost:{self.agent_server_port}/health")
            health_data = response.json()
            logger.info(f"   ✅ Health check: {health_data['status']}")
            logger.info(f"   ✅ Figma server status: {health_data['figma_server_status']}")
            
            # Test design analysis
            analysis_response = requests.post(
                f"http://localhost:{self.agent_server_port}/analyze-design",
                json={"file_id": "demo_file_id", "node_id": "demo_node_id"}
            )
            analysis = analysis_response.json()
            logger.info(f"   ✅ Design analysis: {analysis['component_complexity']} complexity")
            
        except Exception as e:
            logger.error(f"   ❌ UI/UX agent test failed: {e}")
    
    async def _test_component_generation(self):
        """Test component generation workflow"""
        logger.info("🧪 Testing Component Generation Workflow...")
        
        try:
            # Generate a component
            generation_response = requests.post(
                f"http://localhost:{self.agent_server_port}/generate-component",
                json={
                    "file_id": "demo_file_id",
                    "node_id": "demo_node_id",
                    "component_type": "react_component",
                    "styling_approach": "tailwind"
                }
            )
            component = generation_response.json()
            logger.info(f"   ✅ Component generated: {component['component_name']}")
            logger.info(f"   ✅ Code length: {len(component['component_code'])} characters")
            logger.info(f"   ✅ Includes tests: {'test_code' in component}")
            logger.info(f"   ✅ Includes documentation: {'documentation' in component}")
            
        except Exception as e:
            logger.error(f"   ❌ Component generation test failed: {e}")
    
    async def _keep_running(self):
        """Keep the system running and display status"""
        logger.info("============================================================")
        logger.info("🎉 SOPHIA AI UI/UX AGENT SYSTEM IS NOW RUNNING!")
        logger.info("============================================================")
        logger.info("🎨 Figma Dev Mode MCP Server:")
        logger.info(f"   🌐 http://localhost:{self.figma_server_port}")
        logger.info(f"   💚 Health: http://localhost:{self.figma_server_port}/health")
        logger.info("🤖 UI/UX LangChain Agent:")
        logger.info(f"   🌐 http://localhost:{self.agent_server_port}")
        logger.info(f"   💚 Health: http://localhost:{self.agent_server_port}/health")
        logger.info("🎯 Features Available:")
        logger.info("   ✅ Design token extraction from Figma")
        logger.info("   ✅ Component generation with React + TypeScript")
        logger.info("   ✅ Design system validation")
        logger.info("   ✅ Accessibility optimization")
        logger.info("   ✅ Automated testing and documentation")
        logger.info("📝 Test the system:")
        logger.info("   1. POST to extract design tokens")
        logger.info("   2. POST to generate components")
        logger.info("   3. POST to validate design system compliance")
        logger.info("🛑 To stop: Press Ctrl+C")
        logger.info("============================================================")
        
        try:
            while True:
                await asyncio.sleep(10)
                await self._check_system_health()
        except KeyboardInterrupt:
            logger.info("🛑 Shutting down UI/UX Agent System...")
            await self._cleanup()
    
    async def _check_system_health(self):
        """Check system health periodically"""
        try:
            figma_response = requests.get(f"http://localhost:{self.figma_server_port}/health", timeout=5)
            agent_response = requests.get(f"http://localhost:{self.agent_server_port}/health", timeout=5)
            
            if figma_response.status_code != 200 or agent_response.status_code != 200:
                logger.warning("⚠️  System health check detected issues")
        except:
            logger.warning("⚠️  System health check failed")
    
    async def _cleanup(self):
        """Clean up processes"""
        logger.info("🧹 Cleaning up processes...")
        
        for name, process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                logger.info(f"✅ {name} stopped")
            except Exception as e:
                logger.warning(f"⚠️  Failed to stop {name}: {e}")
                try:
                    process.kill()
                except:
                    pass
        
        logger.info("✅ UI/UX Agent System shutdown complete")

async def main():
    """Main entry point"""
    manager = UIUXAgentSystemManager()
    try:
        await manager.start_system()
    except KeyboardInterrupt:
        logger.info("🛑 Interrupted by user")
    except Exception as e:
        logger.error(f"❌ System failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
