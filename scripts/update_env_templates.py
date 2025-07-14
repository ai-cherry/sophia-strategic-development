#!/usr/bin/env python3
"""
Update .env template files to use proper placeholders
Ensures no real secrets are in template files
"""

import re
import os
from pathlib import Path

# Define patterns and their placeholder replacements
SECRET_PATTERNS = {
    # API Keys
    r'sk-[a-zA-Z0-9]{48}': 'sk-YOUR_OPENAI_API_KEY_HERE',
    r'sk-ant-[a-zA-Z0-9\-]{40,}': 'sk-ant-YOUR_ANTHROPIC_API_KEY_HERE',
    r'pul-[a-f0-9]{40}': 'pul-YOUR_PULUMI_ACCESS_TOKEN_HERE',
    r'ghp_[a-zA-Z0-9]{36}': 'ghp_YOUR_GITHUB_PERSONAL_ACCESS_TOKEN_HERE',
    
    # Bearer tokens
    r'Bearer [a-zA-Z0-9\-_\.]+': 'Bearer YOUR_AUTH_TOKEN_HERE',
    
    # URLs with embedded tokens
    r'https://[a-zA-Z0-9\-_]+:[a-zA-Z0-9\-_]+@': 'https://username:password@',
    r'https://api\.[a-z]+\.com/v[0-9]/[a-zA-Z0-9\-_]+': 'https://api.service.com/v1/YOUR_ENDPOINT',
    
    # Database URLs
    r'postgresql://[^:]+:[^@]+@[^/]+/[^?]+': 'postgresql://user:password@host:5432/database',
    r'redis://:[^@]+@[^:]+:[0-9]+': 'redis://:password@host:6379',
    
    # AWS/Cloud credentials
    r'AKIA[A-Z0-9]{16}': 'AKIAIOSFODNN7EXAMPLE',
    r'[a-zA-Z0-9/+=]{40}': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
    
    # Generic patterns
    r'[a-f0-9]{32}': 'YOUR_32_CHAR_HEX_TOKEN_HERE',
    r'[a-f0-9]{40}': 'YOUR_40_CHAR_HEX_TOKEN_HERE',
    r'[a-f0-9]{64}': 'YOUR_64_CHAR_HEX_TOKEN_HERE',
}

# Template files to update
TEMPLATE_FILES = [
    '.env.template',
    '.env.example',
    'frontend/.env.local.template',
    'config/estuary/estuary.env.template',
    '**/*.env.template',
    '**/*.env.example',
]

def update_template_file(filepath):
    """Update a single template file with placeholders"""
    
    print(f"\n📄 Processing {filepath}...")
    
    # Read the file
    with open(filepath, 'r') as f:
        content = f.read()
    
    original_content = content
    replacements = 0
    
    # Apply each pattern
    for pattern, placeholder in SECRET_PATTERNS.items():
        # Count replacements
        matches = re.findall(pattern, content)
        if matches:
            content = re.sub(pattern, placeholder, content)
            replacements += len(matches)
            print(f"  ✅ Replaced {len(matches)} instances of pattern: {pattern[:30]}...")
    
    # Additional specific replacements for common keys
    common_replacements = {
        'OPENAI_API_KEY=.*': 'OPENAI_API_KEY=sk-YOUR_OPENAI_API_KEY_HERE',
        'ANTHROPIC_API_KEY=.*': 'ANTHROPIC_API_KEY=sk-ant-YOUR_ANTHROPIC_API_KEY_HERE',
        'GITHUB_TOKEN=.*': 'GITHUB_TOKEN=ghp_YOUR_GITHUB_PERSONAL_ACCESS_TOKEN_HERE',
        'PULUMI_ACCESS_TOKEN=.*': 'PULUMI_ACCESS_TOKEN=pul-YOUR_PULUMI_ACCESS_TOKEN_HERE',
        'DATABASE_URL=.*': 'DATABASE_URL=postgresql://user:password@host:5432/database',
        'REDIS_URL=.*': 'REDIS_URL=redis://:password@host:6379',
        'API_KEY=.*': 'API_KEY=YOUR_API_KEY_HERE',
        'SECRET_KEY=.*': 'SECRET_KEY=YOUR_SECRET_KEY_HERE',
        'AUTH_TOKEN=.*': 'AUTH_TOKEN=YOUR_AUTH_TOKEN_HERE',
    }
    
    for pattern, replacement in common_replacements.items():
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            replacements += 1
    
    # Write back if changes were made
    if content != original_content:
        # Create backup
        backup_path = f"{filepath}.backup"
        with open(backup_path, 'w') as f:
            f.write(original_content)
        
        # Write updated content
        with open(filepath, 'w') as f:
            f.write(content)
        
        print(f"  ✅ Updated {filepath} ({replacements} replacements)")
        print(f"  📦 Backup saved to {backup_path}")
    else:
        print(f"  ✓ No secrets found in {filepath}")
    
    return replacements

def add_template_header(filepath):
    """Add a header comment to template files"""
    
    header = """# Sophia AI Environment Variables Template
# 
# This is a template file. Copy to .env and fill in your actual values.
# NEVER commit real secrets to version control!
# 
# All secrets should be managed through Pulumi ESC:
# https://github.com/ai-cherry/sophia-main/docs/PULUMI_ESC_GUIDE.md
#
# To get a secret value:
# python -c "from backend.core.auto_esc_config import get_config_value; print(get_config_value('key_name'))"

"""
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Only add header if it doesn't already have one
    if 'template file' not in content.lower()[:200]:
        with open(filepath, 'w') as f:
            f.write(header + content)
        print(f"  📝 Added template header to {filepath}")

def main():
    """Main function to update all template files"""
    
    print("🔍 Updating environment template files...")
    print("=" * 60)
    
    total_files = 0
    total_replacements = 0
    
    # Process each template pattern
    for pattern in TEMPLATE_FILES:
        if '**' in pattern:
            # Glob pattern
            for filepath in Path('.').glob(pattern):
                if '.backup' not in str(filepath):
                    replacements = update_template_file(filepath)
                    add_template_header(filepath)
                    total_files += 1
                    total_replacements += replacements
        else:
            # Direct file
            if os.path.exists(pattern):
                replacements = update_template_file(pattern)
                add_template_header(pattern)
                total_files += 1
                total_replacements += replacements
    
    print("\n" + "=" * 60)
    print(f"✅ Summary:")
    print(f"  - Files processed: {total_files}")
    print(f"  - Total replacements: {total_replacements}")
    print(f"\n📋 Next steps:")
    print(f"  1. Review the changes: git diff *.template")
    print(f"  2. Remove backup files after verification: rm *.template.backup")
    print(f"  3. Commit the changes: git add *.template && git commit -m 'Update templates with placeholders'")

if __name__ == "__main__":
    main() 