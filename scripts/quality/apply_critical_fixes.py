#!/usr/bin/env python3
"""
Apply Critical Fixes to Sophia AI Codebase

This script applies critical fixes to syntax errors and undefined names in the codebase.
"""

import os
import re
from pathlib import Path

# Define the fixes to apply
FIXES = [
    # Fix extra parentheses in snowflake_config_manager.py
    {
        'file': 'scripts/snowflake_config_manager.py',
        'find': r'table_result = self\.execute_query\("SHOW TABLES IN SCHEMA %s", \(schema,\)\)\)',
        'replace': 'table_result = self.execute_query("SHOW TABLES IN SCHEMA %s", (schema,))'
    },
    {
        'file': 'scripts/snowflake_config_manager.py',
        'find': r'count_result = self\.execute_query\("SELECT COUNT\(\*\) as count FROM %s", \(table,\)\)\s*\)',
        'replace': 'count_result = self.execute_query("SELECT COUNT(*) as count FROM %s", (table,))'
    },
    # Fix missing imports
    {
        'file': 'gemini-cli-integration/gemini_cli_provider.py',
        'find': 'def __init__(self):',
        'replace': 'def __init__(self):\n        # Import get_config_value\n        from backend.core.auto_esc_config import get_config_value',
        'before_line': True
    },
    {
        'file': 'gong-webhook-service/main.py',
        'find': 'if __name__ == "__main__":',
        'replace': 'if __name__ == "__main__":\n    from backend.core.auto_esc_config import get_config_value',
        'before_line': True
    },
    {
        'file': 'infrastructure/adapters/snowflake_adapter.py',
        'find': 'from scripts.snowflake_config_manager import SnowflakeConfigManager',
        'replace': 'import logging\nfrom scripts.snowflake_config_manager import SnowflakeConfigManager'
    },
    # Fix syntax errors in verify_and_align_snowflake.py
    {
        'file': 'scripts/verify_and_align_snowflake.py',
        'find': r'self\.cursor\.execute\("DESCRIBE TABLE SOPHIA_AI_PRODUCTION\.%s", \(table,\)\)\)',
        'replace': 'self.cursor.execute("DESCRIBE TABLE SOPHIA_AI_PRODUCTION.%s", (table,))'
    }
]

def apply_fixes():
    """Apply the defined fixes to the codebase."""
    for fix in FIXES:
        file_path = Path(fix['file'])
        
        if not file_path.exists():
            print(f"⚠️  File not found: {file_path}")
            continue
            
        try:
            # Read the file
            content = file_path.read_text()
            original_content = content
            
            # Apply the fix
            if fix.get('before_line'):
                # Insert before the matched line
                lines = content.split('\n')
                new_lines = []
                for line in lines:
                    if fix['find'] in line:
                        # Add the import before the line
                        import_line = fix['replace'].split('\n')[1].strip()
                        new_lines.append(import_line)
                    new_lines.append(line)
                content = '\n'.join(new_lines)
            else:
                # Simple find and replace
                if 'find' in fix and isinstance(fix['find'], str) and fix['find'].startswith('r'):
                    # It's a regex pattern
                    pattern = fix['find'][1:]  # Remove the 'r' prefix
                    content = re.sub(pattern, fix['replace'], content)
                else:
                    content = content.replace(fix['find'], fix['replace'])
            
            # Write back if changed
            if content != original_content:
                file_path.write_text(content)
                print(f"✅ Fixed: {file_path}")
            else:
                print(f"ℹ️  No changes needed: {file_path}")
                
        except Exception as e:
            print(f"❌ Error fixing {file_path}: {e}")

def main():
    """Main entry point."""
    print("Applying critical fixes to Sophia AI codebase...")
    print("=" * 60)
    
    apply_fixes()
    
    print("\n" + "=" * 60)
    print("Critical fixes applied!")
    print("\nNext steps:")
    print("1. Run 'ruff check . --fix' to fix remaining auto-fixable issues")
    print("2. Run 'black .' to format the code")
    print("3. Run the full test suite to ensure everything works")

if __name__ == '__main__':
    main() 