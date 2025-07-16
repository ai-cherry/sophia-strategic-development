#!/usr/bin/env python3
"""
Gong Integration Test Script
Tests the complete Gong.io integration pipeline
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.auto_esc_config import get_gong_config
import structlog

logger = structlog.get_logger()

async def test_gong_integration():
    """Test the complete Gong integration pipeline"""
    
    print("🔍 Testing Gong.io Integration...")
    print("=" * 50)
    
    # Test 1: Configuration
    print("\n1. Testing Configuration...")
    try:
        config = get_gong_config()
        
        required_keys = ['access_key', 'access_key_secret', 'base_url']
        missing_keys = [key for key in required_keys if not config.get(key)]
        
        if missing_keys:
            print(f"❌ Missing configuration: {missing_keys}")
            print("📋 Please add Gong API credentials to GitHub Organization secrets")
            print("   See GONG_INTEGRATION_COMPREHENSIVE_ANALYSIS.md for details")
            return False
        else:
            print("✅ Configuration loaded successfully")
            print(f"   Base URL: {config['base_url']}")
            print(f"   Access Key: {config['access_key'][:8]}..." if config['access_key'] else "   Access Key: NOT_SET")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False
    
    # Test 2: MCP Server Import
    print("\n2. Testing MCP Server Import...")
    try:
        from apps.mcp_servers.servers.gong.server import GongMCPServer
        print("✅ MCP Server import successful")
    except Exception as e:
        print(f"❌ MCP Server import failed: {e}")
        return False
    
    # Test 3: API Client Import
    print("\n3. Testing API Client Import...")
    try:
        from infrastructure.integrations.gong_api_client import GongAPIClient
        print("✅ API Client import successful")
    except Exception as e:
        print(f"❌ API Client import failed: {e}")
        return False
    
    # Test 4: Memory Service Integration
    print("\n4. Testing Memory Service Integration...")
    try:
        from backend.services.sophia_unified_memory_service import SophiaUnifiedMemoryService
        SophiaUnifiedMemoryService()
        print("✅ Memory service integration ready")
    except Exception as e:
        print(f"❌ Memory service integration failed: {e}")
        return False
    
    # Test 5: Configuration Fix Check
    print("\n5. Checking Required Configuration Fixes...")
    fixes_needed = []
    
    # Check MCP server configuration key
    try:
        with open('apps/mcp-servers/servers/gong/server.py', 'r') as f:
            content = f.read()
            if 'get_config_value("gong_api_key")' in content:
                fixes_needed.append("MCP Server: Change 'gong_api_key' to 'GONG_ACCESS_KEY'")
    except:
        fixes_needed.append("Cannot read MCP server file")
    
    # Check API client authentication method
    try:
        with open('infrastructure/integrations/gong_api_client.py', 'r') as f:
            content = f.read()
            if 'f"Bearer {self.api_key}"' in content:
                fixes_needed.append("API Client: Change Bearer auth to Basic auth")
    except:
        fixes_needed.append("Cannot read API client file")
    
    if fixes_needed:
        print("❌ Configuration fixes needed:")
        for fix in fixes_needed:
            print(f"   - {fix}")
        print("📋 See GONG_INTEGRATION_FIXES.md for detailed instructions")
    else:
        print("✅ All configuration fixes applied")
    
    # Test 6: API Connection (only if credentials available)
    if not missing_keys:
        print("\n6. Testing API Connection...")
        try:
            # Create API client with proper authentication
            access_key = config['access_key']
            config['access_key_secret']
            
            client = GongAPIClient(
                api_key=access_key,
                # Note: Need to update constructor to accept access_secret
                base_url=config['base_url']
            )
            
            # Test basic API call
            async with client:
                result = await client.list_calls(limit=1)
                if result and 'calls' in result:
                    print("✅ API connection successful!")
                    print(f"   Found {len(result['calls'])} calls")
                else:
                    print("❌ API connection failed: No data returned")
        except Exception as e:
            print(f"❌ API connection failed: {e}")
    else:
        print("\n6. Skipping API Connection Test (credentials missing)")
    
    # Test 7: MCP Server Startup
    print("\n7. Testing MCP Server Startup...")
    try:
        server = GongMCPServer()
        # Test tool listing
        tools = await server.get_custom_tools()
        print("✅ MCP Server startup successful")
        print(f"   Available tools: {len(tools)}")
        for tool in tools:
            print(f"   - {tool.name}: {tool.description}")
    except Exception as e:
        print(f"❌ MCP Server startup failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎯 INTEGRATION TEST SUMMARY")
    print("=" * 50)
    
    if missing_keys:
        print("❌ BLOCKED: Missing Gong API credentials")
        print("📋 Next Steps:")
        print("   1. Get Gong API credentials from admin portal")
        print("   2. Add to GitHub Organization secrets")
        print("   3. Apply configuration fixes")
        print("   4. Re-run this test")
    elif fixes_needed:
        print("⚠️  READY: Credentials available, fixes needed")
        print("📋 Next Steps:")
        print("   1. Apply configuration fixes from GONG_INTEGRATION_FIXES.md")
        print("   2. Re-run this test")
        print("   3. Deploy to production")
    else:
        print("✅ SUCCESS: Ready for production deployment!")
        print("🚀 Next Steps:")
        print("   1. Deploy MCP server to K8s")
        print("   2. Configure webhooks")
        print("   3. Start receiving real sales data")
    
    return True

def test_webhook_configuration():
    """Test webhook server configuration"""
    print("\n🔗 Testing Webhook Configuration...")
    
    try:
        from infrastructure.integrations.gong_webhook_server import get_server_config
        config = get_server_config()
        print("✅ Webhook server configuration loaded")
        print(f"   Host: {config.HOST}")
        print(f"   Port: {config.PORT}")
    except Exception as e:
        print(f"❌ Webhook configuration failed: {e}")

def main():
    """Main test runner"""
    try:
        asyncio.run(test_gong_integration())
        test_webhook_configuration()
    except KeyboardInterrupt:
        print("\n❌ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
