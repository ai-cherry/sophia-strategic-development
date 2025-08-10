#!/usr/bin/env python3
"""
Setup script for MCP-Notion Sync Service
"""

import os
import sys
import json
from pathlib import Path

def setup_environment():
    """Set up the environment for the sync service"""
    print("🚀 Setting up MCP-Notion Sync Service for Sophia")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        sys.exit(1)
    
    print("✅ Python version check passed")
    
    # Create necessary directories
    dirs_to_create = [
        'logs',
        'data',
        'cache',
        'backups'
    ]
    
    for dir_name in dirs_to_create:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"✅ Created directory: {dir_name}")
    
    # Check for .env file
    if not os.path.exists('.env'):
        print("⚠️  No .env file found. Creating from template...")
        if os.path.exists('.env.example'):
            with open('.env.example', 'r') as src, open('.env', 'w') as dst:
                dst.write(src.read())
            print("✅ Created .env file. Please update with your API keys.")
        else:
            print("❌ .env.example not found")
    else:
        print("✅ .env file exists")
    
    # Initialize sync state
    sync_state_file = 'sync_state.json'
    if not os.path.exists(sync_state_file):
        initial_state = {
            'version': '1.0.0',
            'last_sync': None,
            'content_hashes': {},
            'notion_mappings': {},
            'github_mappings': {},
            'statistics': {
                'total_syncs': 0,
                'successful_syncs': 0,
                'failed_syncs': 0,
                'duplicates_prevented': 0
            }
        }
        with open(sync_state_file, 'w') as f:
            json.dump(initial_state, f, indent=2)
        print(f"✅ Initialized sync state: {sync_state_file}")
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Update .env with your API keys")
    print("2. Run: pip install -r requirements.txt")
    print("3. Run: python sync_manager.py")

if __name__ == '__main__':
    setup_environment()
