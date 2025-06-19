#!/usr/bin/env python3
"""
Claude as Code Launcher
Launches Claude MCP server and integration functionality
"""

import asyncio
import sys
import os
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.mcp.claude_mcp_server import claude_mcp_server
from backend.integrations.claude_integration import claude_integration
from infrastructure.esc.claude_secrets import claude_secret_manager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def setup_claude_environment():
    """Setup Claude environment and credentials"""
    print("🔐 Setting up Claude environment...")
    
    # Setup secrets in Pulumi ESC
    setup_success = await claude_secret_manager.setup_claude_secrets()
    if not setup_success:
        print("❌ Failed to setup Claude secrets")
        return False
    
    # Validate configuration
    validation = await claude_secret_manager.validate_claude_config()
    if not validation['valid']:
        print(f"❌ Configuration validation failed: {validation.get('error', 'Unknown error')}")
        return False
    
    # Get environment variables
    env_vars = await claude_secret_manager.get_environment_variables()
    
    # Set environment variables for current session
    for key, value in env_vars.items():
        os.environ[key] = value
    
    print("✅ Claude environment setup completed")
    return True

async def test_claude_integration():
    """Test Claude integration functionality"""
    print("🧪 Testing Claude integration...")
    
    # Initialize Claude integration
    success = await claude_integration.initialize()
    if not success:
        print("❌ Failed to initialize Claude integration")
        return False
    
    # Test basic functionality
    try:
        response = await claude_integration.send_message("Hello, Claude! Please respond with 'Integration test successful.'")
        if response and "successful" in response.content.lower():
            print("✅ Claude integration test passed")
            return True
        else:
            print("❌ Claude integration test failed")
            return False
    except Exception as e:
        print(f"❌ Claude integration test error: {e}")
        return False

async def start_claude_mcp_server():
    """Start the Claude MCP server"""
    print("🚀 Starting Claude MCP Server...")
    
    try:
        # Run the MCP server
        async with claude_mcp_server.server.stdio_server() as (read_stream, write_stream):
            await claude_mcp_server.server.run(
                read_stream, write_stream, claude_mcp_server.server.create_initialization_options()
            )
    except Exception as e:
        logger.error(f"Failed to start Claude MCP server: {e}")
        sys.exit(1)

async def main():
    """Main launcher function"""
    print("🎯 Claude as Code Launcher")
    print("=" * 40)
    
    # Setup environment
    env_success = await setup_claude_environment()
    if not env_success:
        print("❌ Environment setup failed")
        sys.exit(1)
    
    # Test integration
    test_success = await test_claude_integration()
    if not test_success:
        print("❌ Integration test failed")
        sys.exit(1)
    
    # Start MCP server
    print("🚀 Claude as Code is ready!")
    print("📋 Available capabilities:")
    print("  • Code generation and analysis")
    print("  • Code refactoring and optimization")
    print("  • Documentation generation")
    print("  • Test generation")
    print("  • Debugging assistance")
    print("  • Concept explanation")
    print("  • Natural language programming")
    
    await start_claude_mcp_server()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Claude as Code launcher stopped")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Launcher error: {e}")
        sys.exit(1)

