#!/usr/bin/env python3
"""
Generate MCP configuration from Pulumi ESC secrets

This script uses the EnhancedAutoESCConfig to generate .cursor/mcp.json
from secrets stored in Pulumi ESC / GitHub Organization Secrets.

Usage:
    python scripts/utils/generate_mcp_config.py [--validate] [--output PATH]
"""

import argparse
import json
import logging
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.core.auto_esc_config import EnhancedAutoESCConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main function to generate MCP configuration"""
    parser = argparse.ArgumentParser(
        description='Generate MCP configuration from Pulumi ESC'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate configuration without writing file'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='.cursor/mcp.json',
        help='Output path for MCP configuration (default: .cursor/mcp.json)'
    )
    parser.add_argument(
        '--show-config',
        action='store_true',
        help='Show the generated configuration'
    )
    
    args = parser.parse_args()
    
    # Initialize the enhanced config
    logger.info("🚀 Initializing Enhanced Auto ESC Config...")
    config_manager = EnhancedAutoESCConfig()
    
    if args.validate:
        # Validate configuration
        logger.info("🔍 Validating MCP server configurations...")
        validation_results = config_manager.validate_mcp_config()
        
        # Print validation results
        print("\n📋 MCP Server Configuration Validation Results:\n")
        print(f"{'Server':<15} {'Valid':<8} {'Has Auth':<10} {'Has Endpoint':<15} {'Notes'}")
        print("-" * 60)
        
        for server, result in validation_results.items():
            valid = "✅" if result.get('valid') else "❌"
            has_auth = "✅" if result.get('has_auth') else "❌"
            has_endpoint = "✅" if result.get('has_endpoint') else "N/A"
            error = result.get('error', '')
            
            print(f"{server:<15} {valid:<8} {has_auth:<10} {has_endpoint:<15} {error}")
        
        # Summary
        valid_count = sum(1 for r in validation_results.values() if r.get('valid'))
        total_count = len(validation_results)
        print(f"\n✅ Valid configurations: {valid_count}/{total_count}")
        
        if valid_count < total_count:
            print("\n⚠️  Some servers are missing configuration.")
            print("   Add the required secrets to Pulumi ESC or GitHub Organization Secrets.")
            return 1
    
    else:
        # Generate configuration
        logger.info("🔧 Generating MCP configuration...")
        mcp_config = config_manager.generate_mcp_json()
        
        if args.show_config:
            print("\n📄 Generated MCP Configuration:\n")
            print(json.dumps(mcp_config, indent=2))
        
        # Write configuration
        if config_manager.write_mcp_json(args.output):
            print(f"\n✅ MCP configuration successfully written to: {args.output}")
            print(f"   Configured {len(mcp_config.get('mcpServers', {}))} MCP servers")
            
            # List configured servers
            if mcp_config.get('mcpServers'):
                print("\n📦 Configured MCP Servers:")
                for server in mcp_config['mcpServers']:
                    print(f"   - {server}")
        else:
            print(f"\n❌ Failed to write MCP configuration to: {args.output}")
            return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
