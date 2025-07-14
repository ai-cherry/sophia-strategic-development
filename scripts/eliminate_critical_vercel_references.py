#!/usr/bin/env python3
"""
Eliminate Critical Vercel References
Focus on deployment scripts and core infrastructure
"""

import os
import re
from pathlib import Path

def fix_file(file_path: Path, replacements: dict) -> bool:
    """Fix a single file with replacements"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        for pattern, replacement in replacements.items():
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.IGNORECASE)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed: {file_path}")
            return True
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
    
    return False

def main():
    print("🚀 ELIMINATING CRITICAL VERCEL REFERENCES")
    print("=" * 50)
    
    # Critical files to fix
    critical_files = [
        "scripts/unified_deployment_orchestrator.py",
        "scripts/deploy_enhanced_sophia.py", 
        "scripts/deploy_step_by_step.sh",
        "scripts/deploy_sophia_ai.sh",
        "scripts/update_github_secrets.py",
        "scripts/update_all_workflows_and_configs.py",
    ]
    
    # Replacements for Lambda Labs
    replacements = {
        r'vercel\s+deploy.*': '# Lambda Labs deployment - no Vercel needed',
        r'vercel\s+--prod.*': '# Lambda Labs deployment - no Vercel needed',
        r'VERCEL_TOKEN.*': '# Lambda Labs deployment - no Vercel tokens needed',
        r'VERCEL_ACCESS_TOKEN.*': '# Lambda Labs deployment - no Vercel tokens needed',
        r'cname\.vercel-dns\.com': '192.222.58.232',
        r'Frontend.*Vercel.*': 'Frontend (Lambda Labs)',
        r'Deploy.*Vercel.*': 'Deploy to Lambda Labs',
        r'Vercel.*deployment': 'Lambda Labs deployment',
        r'class VercelManager.*': 'class LambdaLabsManager:',
        r'self\.vercel.*': 'self.lambda_labs',
        r'vercel\.json': 'nginx.conf',
        r'https://.*\.vercel\.app': 'http://192.222.58.232',
        r'"vercel".*': '"lambda-labs"',
    }
    
    fixed_count = 0
    
    for file_path in critical_files:
        full_path = Path(file_path)
        if full_path.exists():
            if fix_file(full_path, replacements):
                fixed_count += 1
        else:
            print(f"⚠️  File not found: {file_path}")
    
    print(f"\n✅ Fixed {fixed_count} critical files")
    print("🎯 Lambda Labs deployment strategy enforced!")

if __name__ == "__main__":
    main() 