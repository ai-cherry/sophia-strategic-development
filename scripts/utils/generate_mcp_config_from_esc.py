#!/usr/bin/env python3
"""
Generate MCP Configuration from Pulumi ESC

This script uses the EnhancedAutoESCConfig class to generate
the .cursor/mcp.json file from Pulumi ESC secrets.
"""

import json
import os
import sys
from pathlib import Path

# Add parent directory to path to import from backend
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.core.auto_esc_config import EnhancedAutoESCConfig


def main():
    """Generate MCP configuration from Pulumi ESC"""
    print("🚀 MCP Configuration Generator from Pulumi ESC")
    print("="*50)
    
    # Create enhanced config instance
    enhanced_config = EnhancedAutoESCConfig()
    
    # Validate configurations first
    print("\n📊 Validating MCP server configurations...")
    validation_results = enhanced_config.validate_mcp_config()
    
    valid_count = sum(1 for r in validation_results.values() if r['valid'])
    print(f"✅ {valid_count}/{len(validation_results)} servers have valid configuration")
    
    # Show validation details
    print("\n📋 Validation Details:")
    for server, result in validation_results.items():
        if result['valid']:
            print(f"  ✅ {server}")
        else:
            print(f"  ❌ {server} - Missing configuration")
    
    # Generate MCP JSON
    print("\n📄 Generating MCP configuration...")
    try:
        mcp_json = enhanced_config.generate_mcp_json()
        
        # Show summary
        print(f"\n✅ Generated configuration for {len(mcp_json['mcpServers'])} servers:")
        for server_name in mcp_json['mcpServers']:
            print(f"  - {server_name}")
        
        # Write to file
        output_path = ".cursor/mcp.json"
        
        # Ask for confirmation
        print(f"\n💾 Ready to write configuration to: {output_path}")
        response = input("Proceed? (y/n): ")
        
        if response.lower() == 'y':
            # Create directory if needed
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Write configuration
            with open(output_path, 'w') as f:
                json.dump(mcp_json, f, indent=2)
            
            print(f"\n✅ Configuration written to {output_path}")
            
            # Show file size
            file_size = os.path.getsize(output_path)
            print(f"📊 File size: {file_size} bytes")
            
            # Verify the file
            with open(output_path, 'r') as f:
                loaded = json.load(f)
                print(f"✅ Verification: File contains {len(loaded['mcpServers'])} server configurations")
        else:
            print("\n❌ Operation cancelled")
            
            # Optionally show what would have been written
            print("\n📋 Configuration that would have been written:")
            print(json.dumps(mcp_json, indent=2)[:500] + "..." if len(json.dumps(mcp_json)) > 500 else json.dumps(mcp_json, indent=2))
    
    except Exception as e:
        print(f"\n❌ Failed to generate MCP configuration: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
