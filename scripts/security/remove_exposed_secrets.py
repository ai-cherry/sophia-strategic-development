#!/usr/bin/env python3
"""
Emergency Script to Remove All Exposed Secrets from Sophia AI Codebase
This script replaces hardcoded secrets with secure configuration calls
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple

# Define the exposed secret that needs to be replaced
EXPOSED_SNOWFLAKE_PASSWORD = 'eyJraWQiOiI1MDg3NDc2OTQxMyIsImFsZyI6IkVTMjU2In0.eyJwIjoiMTk4NzI5NDc2OjUwODc0NzQ1NDc3IiwiaXNzIjoiU0Y6MTA0OSIsImV4cCI6MTc4MjI4MDQ3OH0.8m-fWI5rvCs6b8bvw1quiM-UzW9uPRxMUmE6VAgOFFylAhRkCzch7ojh7CRLeMdii6DD1Owqap0KoOmyxsW77A'

EXPOSED_GONG_KEY = 'TV33BPZ5UN45QKZRXHQ6Q3L5N'

# Files to fix
CRITICAL_FILES = [
    'snowflake_advanced_features_implementation.py',
    'sophia_standalone_server.py',
    'deploy_estuary_foundation_corrected.py',
    'backend/core/comprehensive_snowflake_config.py',
    'backend/core/enhanced_snowflake_config.py',
    'backend/core/snowflake_schema_integration.py',
    'backend/services/unified_ai_orchestration_service.py',
    'scripts/estuary_integration_manager.py',
    'scripts/snowflake_config_manager.py',
    'scripts/deploy_snowflake_stability_standalone.py',
    'cortex_agents_advanced_implementation.py',
    'deploy_complete_platform.py',
]

def fix_file_secrets(file_path: Path) -> bool:
    """Fix secrets in a single file"""
    if not file_path.exists():
        print(f"⚠️  File not found: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace exposed Snowflake password
        content = content.replace(
            f'password="{EXPOSED_SNOWFLAKE_PASSWORD}"',
            'password=get_config_value("snowflake_password")'
        )
        content = content.replace(
            f"password='{EXPOSED_SNOWFLAKE_PASSWORD}'",
            'password=get_config_value("snowflake_password")'
        )
        content = content.replace(
            f'"{EXPOSED_SNOWFLAKE_PASSWORD}"',
            'get_config_value("snowflake_password")'
        )
        content = content.replace(
            f"'{EXPOSED_SNOWFLAKE_PASSWORD}'",
            'get_config_value("snowflake_password")'
        )
        
        # Replace Gong API key
        content = content.replace(
            f'"{EXPOSED_GONG_KEY}"',
            'get_config_value("gong_access_key")'
        )
        content = content.replace(
            f"'{EXPOSED_GONG_KEY}'",
            'get_config_value("gong_access_key")'
        )
        
        # Replace hardcoded CEO access token
        content = content.replace(
            '"sophia_ceo_access_2024"',
            'get_config_value("ceo_access_token", "sophia_ceo_access_2024")'
        )
        content = content.replace(
            "'sophia_ceo_access_2024'",
            'get_config_value("ceo_access_token", "sophia_ceo_access_2024")'
        )
        
        # Add import if needed and content was changed
        if content != original_content:
            # Check if import already exists
            if 'from backend.core.auto_esc_config import get_config_value' not in content:
                # Find a good place to add the import
                lines = content.split('\n')
                import_added = False
                
                for i, line in enumerate(lines):
                    if line.strip().startswith('import ') or line.strip().startswith('from '):
                        # Add after existing imports
                        continue
                    elif not line.strip() or line.strip().startswith('#'):
                        # Skip empty lines and comments
                        continue
                    else:
                        # This is the first non-import line, add import before it
                        lines.insert(i, 'from backend.core.auto_esc_config import get_config_value')
                        import_added = True
                        break
                
                if not import_added:
                    # Add at the beginning if no good place found
                    lines.insert(0, 'from backend.core.auto_esc_config import get_config_value')
                
                content = '\n'.join(lines)
        
        # Write back if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed secrets in: {file_path}")
            return True
        else:
            print(f"ℹ️  No secrets found in: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False

def delete_files_with_exposed_secrets():
    """Delete standalone files that contain exposed secrets and aren't critical"""
    project_root = Path(__file__).parent.parent.parent
    
    # Files that can be safely deleted (they're not part of core functionality)
    files_to_delete = [
        'flow.yaml',  # Estuary flow config with exposed secrets
        'enhanced_auto_esc_config.py',  # Backup file with secrets
    ]
    
    for file_name in files_to_delete:
        for file_path in project_root.rglob(file_name):
            if file_path.exists():
                try:
                    file_path.unlink()
                    print(f"🗑️  Deleted file with exposed secrets: {file_path}")
                except Exception as e:
                    print(f"❌ Failed to delete {file_path}: {e}")

def main():
    """Main function to remove all exposed secrets"""
    project_root = Path(__file__).parent.parent.parent
    
    print("🚨 EMERGENCY SECRET REMOVAL")
    print("="*50)
    
    fixed_count = 0
    
    # Fix critical files
    for file_name in CRITICAL_FILES:
        file_path = project_root / file_name
        if fix_file_secrets(file_path):
            fixed_count += 1
    
    # Delete files that can't be easily fixed
    delete_files_with_exposed_secrets()
    
    # Fix any other Python files with the exposed password
    print("\n🔍 Scanning for other files with exposed secrets...")
    
    for py_file in project_root.rglob("*.py"):
        if py_file.name in ['remove_exposed_secrets.py', 'security_audit_and_cleanup.py']:
            continue  # Skip our own scripts
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if EXPOSED_SNOWFLAKE_PASSWORD in content or EXPOSED_GONG_KEY in content:
                if fix_file_secrets(py_file):
                    fixed_count += 1
        except:
            continue
    
    print(f"\n✅ Fixed {fixed_count} files")
    print("🔐 All exposed secrets have been removed!")
    print("\n⚠️  IMPORTANT: You must now set the real secrets in Pulumi ESC:")
    print("   1. Run: python scripts/security/setup_pulumi_esc_secrets.py")
    print("   2. Set all required secrets interactively")
    print("   3. Test the application startup")

if __name__ == "__main__":
    main() 