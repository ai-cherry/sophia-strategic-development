#!/usr/bin/env python3
"""
Examples of using the EnhancedAutoESCConfig class
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.core.auto_esc_config import EnhancedAutoESCConfig


def example_generate_mcp_config():
    """Example: Generate MCP configuration for Cursor AI"""
    print("📄 Example 1: Generate MCP configuration")
    print("-" * 40)
    
    config = EnhancedAutoESCConfig()
    
    # Generate the configuration
    mcp_json = config.generate_mcp_json()
    
    # Write to file
    success = config.write_mcp_json(".cursor/mcp.json")
    
    if success:
        print("✅ MCP configuration generated successfully")
        print(f"   Configured servers: {len(mcp_json['mcpServers'])}")
    else:
        print("❌ Failed to generate MCP configuration")


def example_get_specific_server_config():
    """Example: Get configuration for a specific MCP server"""
    print("\n🔧 Example 2: Get specific server configuration")
    print("-" * 40)
    
    config = EnhancedAutoESCConfig()
    
    # Get Gong configuration
    gong_config = config.get_mcp_config('gong')
    print("Gong configuration:")
    print(f"  API Key: {'✅ Configured' if gong_config.get('api_key') else '❌ Not configured'}")
    print(f"  Endpoint: {gong_config.get('endpoint', 'Not set')}")
    
    # Get Lambda Labs configuration
    lambda_config = config.get_mcp_config('lambda-labs')
    print("\nLambda Labs configuration:")
    print(f"  API Key: {'✅ Configured' if lambda_config.get('api_key') else '❌ Not configured'}")
    print(f"  SSH Key Path: {lambda_config.get('ssh_private_key_path', 'Not set')}")


def example_validate_all_servers():
    """Example: Validate all MCP server configurations"""
    print("\n✅ Example 3: Validate all server configurations")
    print("-" * 40)
    
    config = EnhancedAutoESCConfig()
    validation_results = config.validate_mcp_config()
    
    valid_count = sum(1 for r in validation_results.values() if r.get('valid'))
    total_count = len(validation_results)
    
    print(f"Validation summary: {valid_count}/{total_count} servers configured")
    
    # Show problematic servers
    print("\nServers needing configuration:")
    for server, result in validation_results.items():
        if not result.get('valid'):
            print(f"  - {server}: Missing authentication")


def example_get_perplexity_config():
    """Example: Get Perplexity API configuration"""
    print("\n🤖 Example 4: Get Perplexity configuration")
    print("-" * 40)
    
    config = EnhancedAutoESCConfig()
    perplexity = config.get_perplexity_config()
    
    print("Perplexity configuration:")
    print(f"  API Key: {'✅ Configured' if perplexity.get('api_key') else '❌ Not configured'}")
    print(f"  Default model: {perplexity['model_preferences']['default']}")
    print(f"  Coding model: {perplexity['model_preferences']['coding']}")
    print(f"  Temperature: {perplexity['settings']['temperature']}")
    print(f"  Max tokens: {perplexity['settings']['max_tokens']}")


def example_build_server_config():
    """Example: Build configuration for a specific server"""
    print("\n🏗️ Example 5: Build server-specific configuration")
    print("-" * 40)
    
    config = EnhancedAutoESCConfig()
    
    # Get raw configuration
    qdrant_raw = config.get_mcp_config('qdrant')
    
    # Build MCP server configuration
    qdrant_mcp = config.build_server_config('qdrant', qdrant_raw)
    
    print("Qdrant MCP configuration:")
    print(f"  Command: {qdrant_mcp['command']}")
    print(f"  Args: {qdrant_mcp['args']}")
    if 'env' in qdrant_mcp:
        print(f"  Environment variables: {len(qdrant_mcp['env'])} configured")


def example_custom_server_list():
    """Example: Generate configuration for custom server list"""
    print("\n🎯 Example 6: Custom server selection")
    print("-" * 40)
    
    config = EnhancedAutoESCConfig()
    
    # Override the default server list
    custom_servers = ['gong', 'hubspot', 'slack', 'qdrant']
    config.mcp_servers = custom_servers
    
    # Generate configuration
    mcp_json = config.generate_mcp_json()
    
    print(f"Generated configuration for {len(mcp_json['mcpServers'])} servers:")
    for server in mcp_json['mcpServers']:
        print(f"  - {server}")


def example_programmatic_usage():
    """Example: Using configuration programmatically in code"""
    print("\n💻 Example 7: Programmatic usage in application")
    print("-" * 40)
    
    from backend.core.auto_esc_config import get_gong_config, get_redis_config, get_qdrant_config
    
    # Use specific configuration getters
    gong = get_gong_config()
    print(f"Gong access key configured: {'✅' if gong['access_key'] else '❌'}")
    
    redis = get_redis_config()
    print(f"Redis host: {redis['host']}:{redis['port']}")
    
    qdrant = get_qdrant_config()
    print(f"Qdrant URL: {qdrant['url']}")


if __name__ == "__main__":
    print("🚀 EnhancedAutoESCConfig Usage Examples")
    print("=" * 60)
    
    # Run all examples
    example_generate_mcp_config()
    example_get_specific_server_config()
    example_validate_all_servers()
    example_get_perplexity_config()
    example_build_server_config()
    example_custom_server_list()
    example_programmatic_usage()
    
    print("\n" + "=" * 60)
    print("✅ All examples completed")
