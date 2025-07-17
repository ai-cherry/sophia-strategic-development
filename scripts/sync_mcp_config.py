#!/usr/bin/env python3
"""
Simple MCP configuration sync from Pulumi ESC
"""

import json
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.auto_esc_config import EnhancedAutoESCConfig


def sync_mcp_configuration():
    """Sync MCP configuration from Pulumi ESC"""
    try:
        config = EnhancedAutoESCConfig()
        
        # Generate MCP configuration
        mcp_config = config.generate_mcp_json()
        
        # Ensure .cursor directory exists
        os.makedirs('.cursor', exist_ok=True)
        
        # Write to .cursor/mcp.json
        with open('.cursor/mcp.json', 'w') as f:
            json.dump(mcp_config, f, indent=2)
        
        print("✅ MCP configuration synced from Pulumi ESC")
        
    except Exception as e:
        print(f"❌ Failed to sync MCP configuration: {e}")
        sys.exit(1)


if __name__ == "__main__":
    sync_mcp_configuration()
