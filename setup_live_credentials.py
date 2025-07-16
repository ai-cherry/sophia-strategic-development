#!/usr/bin/env python3
"""
🔑 Setup Live Credentials for Sophia AI
=====================================
Sets up credentials from Pulumi ESC or environment variables
"""

import os
import sys

def setup_credentials():
    """Set up credentials from available sources"""
    credentials = {}
    
    print("🔑 Setting up live credentials...")
    
    # Try to load from ESC first
    try:
        sys.path.append('.')
        os.environ['ENVIRONMENT'] = 'prod'
        os.environ['PULUMI_ORG'] = 'scoobyjava-org'
        
        from backend.core.auto_esc_config import get_config_value
        
        credentials = {
            'GONG_ACCESS_KEY': get_config_value('gong_access_key', ''),
            'GONG_ACCESS_KEY_SECRET': get_config_value('gong_access_key_secret', ''),
            'SLACK_BOT_TOKEN': get_config_value('slack_bot_token', ''),
            'ASANA_API_TOKEN': get_config_value('asana_api_token', ''),
            'NOTION_API_KEY': get_config_value('notion_api_key', ''),
            'LINEAR_API_KEY': get_config_value('linear_api_key', ''),
            'OPENAI_API_KEY': get_config_value('openai_api_key', '')
        }
        
        print("✅ Loaded credentials from Pulumi ESC")
        
    except Exception as e:
        print(f"⚠️ ESC loading failed: {e}")
        print("📝 Using fallback credential sources...")
        
        # Fallback to environment
        credentials = {
            'GONG_ACCESS_KEY': os.getenv('GONG_ACCESS_KEY', ''),
            'GONG_ACCESS_KEY_SECRET': os.getenv('GONG_ACCESS_KEY_SECRET', ''),
            'SLACK_BOT_TOKEN': os.getenv('SLACK_BOT_TOKEN', ''),
            'ASANA_API_TOKEN': os.getenv('ASANA_API_TOKEN', ''),
            'NOTION_API_KEY': os.getenv('NOTION_API_KEY', ''),
            'LINEAR_API_KEY': os.getenv('LINEAR_API_KEY', ''),
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY', '')
        }
    
    # Check credential status
    print("\n📊 Credential Status:")
    for key, value in credentials.items():
        status = "FOUND" if value else "MISSING"
        length = len(value) if value else 0
        print(f"{key}: {status} ({length} chars)")
    
    # Create environment file for backend
    env_file_content = ""
    for key, value in credentials.items():
        if value:
            env_file_content += f"export {key}='{value}'\n"
    
    # Write to file
    with open('sophia_credentials.env', 'w') as f:
        f.write(env_file_content)
    
    print(f"\n✅ Created sophia_credentials.env with {len([v for v in credentials.values() if v])} credentials")
    
    return credentials

if __name__ == "__main__":
    setup_credentials() 