#!/usr/bin/env python3
"""
Test script for Enhanced Auto ESC Config with MCP server integration

This demonstrates how to use the EnhancedAutoESCConfig class to:
1. Get MCP server configurations from Pulumi ESC
2. Generate MCP JSON configuration
3. Validate configurations
"""

import json
import logging
from backend.core.auto_esc_config import EnhancedAutoESCConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_enhanced_esc_config():
    """Test the enhanced ESC configuration for MCP servers"""
    print("\n🚀 Testing Enhanced Auto ESC Config")
    print("="*60)
    
    # Create enhanced config instance
    enhanced_config = EnhancedAutoESCConfig()
    
    # Test 1: Get individual server configurations
    print("\n📊 Testing Individual Server Configurations:")
    test_servers = ['gong', 'lambda-labs', 'qdrant', 'slack']
    
    for server in test_servers:
        print(f"\n🔧 {server}:")
        try:
            config = enhanced_config.get_mcp_config(server)
            print(f"   API Key: {'✅ Present' if config.get('api_key') else '❌ Missing'}")
            print(f"   Endpoint: {config.get('endpoint', 'Not specified')}")
            if config.get('config'):
                print(f"   Additional config: {list(config['config'].keys())}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Test 2: Generate MCP JSON configuration
    print("\n\n📄 Generating MCP JSON Configuration:")
    try:
        mcp_json = enhanced_config.generate_mcp_json()
        print(f"✅ Generated configuration for {len(mcp_json['mcpServers'])} servers")
        
        # Display the configuration
        print("\n📋 MCP Configuration:")
        for server_name, server_config in mcp_json['mcpServers'].items():
            print(f"\n   {server_name}:")
            print(f"     Command: {server_config['command']}")
            print(f"     Args: {server_config['args']}")
            if 'env' in server_config:
                print(f"     Environment variables: {len(server_config['env'])}")
                # Show first few env vars (hiding sensitive values)
                for key in list(server_config['env'].keys())[:3]:
                    value = server_config['env'][key]
                    if 'KEY' in key or 'TOKEN' in key or 'SECRET' in key:
                        value = '***REDACTED***'
                    print(f"       - {key}: {value}")
    
    except Exception as e:
        print(f"❌ Failed to generate MCP JSON: {e}")
    
    # Test 3: Validate configurations
    print("\n\n✅ Validating MCP Configurations:")
    validation_results = enhanced_config.validate_mcp_config()
    
    valid_count = sum(1 for r in validation_results.values() if r['valid'])
    print(f"\n📊 Validation Summary: {valid_count}/{len(validation_results)} servers configured")
    
    print("\n📋 Detailed Results:")
    for server, result in validation_results.items():
        status = "✅" if result['valid'] else "❌"
        print(f"   {status} {server}:")
        if result['valid']:
            print(f"      - Has auth: {result['has_auth']}")
            print(f"      - Has endpoint: {result['has_endpoint']}")
        else:
            print(f"      - Error: {result.get('error', 'Missing configuration')}")
    
    # Test 4: Write MCP configuration to file
    print("\n\n💾 Writing MCP Configuration:")
    output_path = "test_mcp_config.json"
    try:
        # Generate and write directly
        mcp_json = enhanced_config.generate_mcp_json()
        with open(output_path, 'w') as f:
            json.dump(mcp_json, f, indent=2)
        print(f"✅ Configuration written to {output_path}")
        
        # Show file content preview
        print("\n📄 File Preview:")
        with open(output_path, 'r') as f:
            content = f.read()
            lines = content.split('\n')[:20]  # Show first 20 lines
            for line in lines:
                print(f"   {line}")
        if len(content.split('\n')) > 20:
            print("   ... (truncated)")
            
    except Exception as e:
        print(f"❌ Failed to write configuration: {e}")
    
    # Clean up test file
    import os
    if os.path.exists(output_path):
        os.remove(output_path)
        print(f"\n🧹 Cleaned up test file: {output_path}")


def test_specific_server_config():
    """Test configuration for a specific server in detail"""
    print("\n\n🔍 Detailed Server Configuration Test")
    print("="*60)
    
    enhanced_config = EnhancedAutoESCConfig()
    server_name = 'lambda-labs'
    
    print(f"\n📊 Detailed configuration for {server_name}:")
    
    # Get raw configuration
    config = enhanced_config.get_mcp_config(server_name)
    print("\n1️⃣ Raw Configuration:")
    for key, value in config.items():
        if key == 'api_key' and value:
            value = '***REDACTED***'
        elif key == 'ssh_private_key' and value:
            value = '***REDACTED***'
        print(f"   {key}: {value}")
    
    # Build server configuration
    server_config = enhanced_config.build_server_config(server_name, config)
    print("\n2️⃣ Built Server Configuration:")
    print(f"   Command: {server_config['command']} {' '.join(server_config['args'])}")
    if 'env' in server_config:
        print("   Environment Variables:")
        for key, value in server_config['env'].items():
            if 'KEY' in key or 'TOKEN' in key:
                value = '***REDACTED***'
            print(f"     {key}: {value}")


def main():
    """Main test function"""
    print("\n🎯 Enhanced Auto ESC Config Test Suite")
    print("="*60)
    
    # Run main tests
    test_enhanced_esc_config()
    
    # Run detailed server test
    test_specific_server_config()
    
    print("\n\n✅ All tests completed!")


if __name__ == "__main__":
    main()
