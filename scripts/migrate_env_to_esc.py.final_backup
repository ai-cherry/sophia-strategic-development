#!/usr/bin/env python3
"""
Migrate .env file contents to Pulumi ESC
Usage: python migrate_env_to_esc.py <env_file>
"""

import sys
import os
import re
import subprocess
from pathlib import Path

def parse_env_file(filepath):
    """Parse .env file and return key-value pairs"""
    env_vars = {}
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Parse KEY=VALUE
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                env_vars[key] = value
    
    return env_vars

def migrate_to_pulumi_esc(env_vars, prefix=''):
    """Migrate environment variables to Pulumi ESC"""
    
    print("🚀 Migrating to Pulumi ESC...")
    
    for key, value in env_vars.items():
        # Skip if already looks like a placeholder
        if 'YOUR_' in value or 'PLACEHOLDER' in value:
            print(f"⏭️  Skipping {key} (looks like placeholder)")
            continue
        
        # Determine if it's a secret
        is_secret = any(pattern in value.lower() for pattern in [
            'key', 'token', 'secret', 'password', 'auth'
        ]) or any(pattern in value for pattern in [
            'sk-', 'ghp_', 'pul-', 'Bearer'
        ])
        
        # Construct the Pulumi config key
        config_key = f"{prefix}{key.lower()}" if prefix else key.lower()
        
        # Set in Pulumi ESC
        cmd = ['pulumi', 'config', 'set', config_key, value]
        if is_secret:
            cmd.append('--secret')
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"✅ Migrated {key} -> {config_key} {'(secret)' if is_secret else ''}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to migrate {key}: {e.stderr}")

def update_code_references(key_mappings):
    """Generate code to update references to use get_config_value"""
    
    print("\n📝 Update your code with these changes:")
    print("```python")
    print("from backend.core.auto_esc_config import get_config_value")
    print()
    
    for old_key, new_key in key_mappings.items():
        print(f"# Replace: os.getenv('{old_key}')")
        print(f"# With:    get_config_value('{new_key}')")
        print()
    print("```")

def main():
    if len(sys.argv) != 2:
        print("Usage: python migrate_env_to_esc.py <env_file>")
        sys.exit(1)
    
    env_file = sys.argv[1]
    
    if not os.path.exists(env_file):
        print(f"❌ File not found: {env_file}")
        sys.exit(1)
    
    print(f"📄 Parsing {env_file}...")
    env_vars = parse_env_file(env_file)
    
    print(f"Found {len(env_vars)} environment variables")
    
    # Determine prefix based on filename
    prefix = ''
    if 'lambda' in env_file.lower():
        prefix = 'lambda_labs.'
    elif 'vercel' in env_file.lower():
        prefix = 'vercel.'
    elif 'modern_stack' in env_file.lower():
        prefix = 'modern_stack.'
    
    # Migrate to Pulumi ESC
    migrate_to_pulumi_esc(env_vars, prefix)
    
    # Generate key mappings
    key_mappings = {
        key: f"{prefix}{key.lower()}" if prefix else key.lower()
        for key in env_vars.keys()
    }
    
    # Show code update suggestions
    update_code_references(key_mappings)
    
    print(f"\n✅ Migration complete! Remember to:")
    print(f"1. Test the migrated values: python -c \"from backend.core.auto_esc_config import get_config_value; print(get_config_value('{list(key_mappings.values())[0]}'))\"")
    print(f"2. Delete the original file: rm {env_file}")
    print(f"3. Update all code references to use get_config_value()")

if __name__ == "__main__":
    main() 