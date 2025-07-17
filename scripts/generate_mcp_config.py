#!/usr/bin/env python3
"""
Generate MCP configuration file from Pulumi ESC
This script uses the existing EnhancedAutoESCConfig class
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.auto_esc_config import EnhancedAutoESCConfig


def main():
    """Generate MCP configuration file"""
    print("🚀 Generating MCP configuration from Pulumi ESC")
    print("=" * 60)
    
    # Initialize the enhanced config
    config = EnhancedAutoESCConfig()
    
    # Validate configurations first
    print("\n📋 Validating server configurations...")
    validation_results = config.validate_mcp_config()
    
    valid_count = sum(1 for r in validation_results.values() if r.get('valid'))
    total_count = len(validation_results)
    
    print(f"✅ {valid_count}/{total_count} servers have valid configuration")
    
    # Show which servers are configured
    print("\nConfigured servers:")
    for server, result in validation_results.items():
        if result.get('valid'):
            print(f"  ✅ {server}")
    
    # Show which servers need configuration
    if valid_count < total_count:
        print("\nServers needing configuration:")
        for server, result in validation_results.items():
            if not result.get('valid'):
                print(f"  ❌ {server}")
    
    # Generate the MCP configuration
    print("\n📄 Generating MCP JSON...")
    try:
        mcp_json = config.generate_mcp_json()
        server_count = len(mcp_json.get('mcpServers', {}))
        print(f"✅ Generated configuration for {server_count} servers")
        
        # Write to file
        output_path = ".cursor/mcp.json"
        print(f"\n💾 Writing configuration to {output_path}...")
        
        success = config.write_mcp_json(output_path)
        
        if success:
            print(f"✅ Configuration successfully written to {output_path}")
            
            # Show file size
            file_size = Path(output_path).stat().st_size
            print(f"📊 File size: {file_size:,} bytes")
            
            # Preview the configuration
            print("\n📋 Configuration preview:")
            with open(output_path, 'r') as f:
                config_data = json.load(f)
                for server_name in list(config_data.get('mcpServers', {}).keys())[:3]:
                    print(f"  - {server_name}")
                if len(config_data.get('mcpServers', {})) > 3:
                    print(f"  ... and {len(config_data['mcpServers']) - 3} more")
            
            print("\n✅ MCP configuration ready for use with Cursor AI!")
            print("🎯 Restart Cursor to load the new configuration")
            
        else:
            print("❌ Failed to write configuration file")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error generating configuration: {e}")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ Configuration generation completed successfully!")


if __name__ == "__main__":
    main()
