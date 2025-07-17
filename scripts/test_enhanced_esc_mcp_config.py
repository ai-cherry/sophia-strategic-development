#!/usr/bin/env python3
"""
Test script for EnhancedAutoESCConfig MCP configuration generation
"""

import sys
import os
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.auto_esc_config import EnhancedAutoESCConfig


def test_mcp_config_generation():
    """Test MCP configuration generation from Pulumi ESC"""
    print("🚀 Testing EnhancedAutoESCConfig MCP generation")
    print("=" * 60)
    
    # Initialize the enhanced config
    config = EnhancedAutoESCConfig()
    
    # Test 1: List available MCP servers
    print("\n📋 Available MCP servers:")
    for server in config.mcp_servers:
        print(f"  - {server}")
    
    # Test 2: Validate configurations
    print("\n🔍 Validating MCP server configurations:")
    validation_results = config.validate_mcp_config()
    
    for server, result in validation_results.items():
        if result.get('valid'):
            print(f"  ✅ {server}: Valid (has_auth: {result['has_auth']}, has_endpoint: {result['has_endpoint']})")
        else:
            error = result.get('error', 'Invalid configuration')
            print(f"  ❌ {server}: {error}")
    
    # Test 3: Get specific server configs
    print("\n🔧 Sample server configurations:")
    test_servers = ['gong', 'lambda-labs', 'qdrant', 'redis']
    
    for server in test_servers:
        if server in config.mcp_servers:
            try:
                server_config = config.get_mcp_config(server)
                print(f"\n  {server}:")
                for key, value in server_config.items():
                    if key == 'api_key' and value:
                        # Mask sensitive data
                        display_value = value[:10] + "..." if len(value) > 10 else "[HIDDEN]"
                    else:
                        display_value = value
                    print(f"    {key}: {display_value}")
            except Exception as e:
                print(f"  ❌ Error getting {server} config: {e}")
    
    # Test 4: Generate MCP JSON
    print("\n📄 Generating MCP JSON configuration:")
    try:
        mcp_json = config.generate_mcp_json()
        
        # Count configured servers
        configured_count = len(mcp_json.get('mcpServers', {}))
        print(f"  ✅ Generated configuration for {configured_count} servers")
        
        # Show a sample server configuration
        if configured_count > 0:
            sample_server = list(mcp_json['mcpServers'].keys())[0]
            print(f"\n  Sample configuration ({sample_server}):")
            sample_config = mcp_json['mcpServers'][sample_server]
            print(f"    command: {sample_config.get('command')}")
            print(f"    args: {sample_config.get('args')}")
            if 'env' in sample_config:
                print(f"    env vars: {len(sample_config['env'])} configured")
        
    except Exception as e:
        print(f"  ❌ Error generating MCP JSON: {e}")
    
    # Test 5: Write MCP JSON to file
    print("\n💾 Writing MCP configuration to file:")
    output_path = ".cursor/mcp_test.json"
    
    try:
        success = config.write_mcp_json(output_path)
        if success:
            print(f"  ✅ Configuration written to {output_path}")
            
            # Verify file contents
            with open(output_path, 'r') as f:
                written_config = json.load(f)
                print(f"  📊 File contains {len(written_config.get('mcpServers', {}))} server configurations")
        else:
            print("  ❌ Failed to write configuration")
            
    except Exception as e:
        print(f"  ❌ Error writing configuration: {e}")
    
    # Test 6: Get Perplexity configuration
    print("\n🤖 Testing Perplexity configuration:")
    try:
        perplexity_config = config.get_perplexity_config()
        print(f"  Endpoint: {perplexity_config.get('endpoint')}")
        print(f"  Models configured: {len(perplexity_config.get('model_preferences', {}))}")
        print(f"  Temperature: {perplexity_config.get('settings', {}).get('temperature')}")
        print(f"  Max tokens: {perplexity_config.get('settings', {}).get('max_tokens')}")
    except Exception as e:
        print(f"  ❌ Error getting Perplexity config: {e}")
    
    print("\n" + "=" * 60)
    print("✅ EnhancedAutoESCConfig test completed")


def test_individual_server_config(server_name: str):
    """Test configuration for a specific MCP server"""
    print(f"\n🔍 Testing {server_name} configuration:")
    print("-" * 40)
    
    config = EnhancedAutoESCConfig()
    
    try:
        # Get the configuration
        server_config = config.get_mcp_config(server_name)
        
        print(f"Raw configuration:")
        for key, value in server_config.items():
            if key == 'api_key' and value:
                print(f"  {key}: [CONFIGURED]")
            else:
                print(f"  {key}: {value}")
        
        # Build the MCP server config
        mcp_server_config = config.build_server_config(server_name, server_config)
        
        print(f"\nMCP server configuration:")
        print(f"  command: {mcp_server_config.get('command')}")
        print(f"  args: {mcp_server_config.get('args')}")
        
        if 'env' in mcp_server_config:
            print(f"  environment variables:")
            for env_var, value in mcp_server_config['env'].items():
                if 'KEY' in env_var or 'TOKEN' in env_var:
                    print(f"    {env_var}: [CONFIGURED]")
                else:
                    print(f"    {env_var}: {value}")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")


if __name__ == "__main__":
    # Run main test
    test_mcp_config_generation()
    
    # Test specific servers if requested
    if len(sys.argv) > 1:
        for server in sys.argv[1:]:
            test_individual_server_config(server)
