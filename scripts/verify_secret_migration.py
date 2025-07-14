#!/usr/bin/env python3
"""
Verify that all secrets have been migrated to Pulumi ESC
and no hardcoded secrets remain in the codebase
"""

import os
import re
import subprocess
from pathlib import Path
from collections import defaultdict

# Secret patterns to check
SECRET_PATTERNS = {
    'OpenAI API Key': r'sk-[a-zA-Z0-9]{48}',
    'Anthropic API Key': r'sk-ant-[a-zA-Z0-9\-]{40,}',
    'Pulumi Token': r'pul-[a-f0-9]{40}',
    'GitHub Token': r'ghp_[a-zA-Z0-9]{36}',
    'Generic API Key': r'api[_-]?key\s*[:=]\s*["\']?[a-zA-Z0-9\-_]{20,}["\']?',
    'Bearer Token': r'Bearer\s+[a-zA-Z0-9\-_\.]{20,}',
    'AWS Access Key': r'AKIA[A-Z0-9]{16}',
    'Private Key': r'-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----',
    'Database URL': r'(?:postgresql|mysql|mongodb)://[^:]+:[^@]+@[^/]+',
}

# Files to skip
SKIP_PATTERNS = [
    '*.pyc',
    '__pycache__',
    '.git',
    'node_modules',
    'dist',
    'build',
    '.env.template',
    '.env.example',
    '*.backup',
    'cleanup_scan_report.json',
    'tests/test_enhanced_daily_cleanup.py',  # Has test patterns
]

def check_pulumi_esc_integration():
    """Verify Pulumi ESC is properly configured"""
    
    print("🔍 Checking Pulumi ESC integration...")
    
    try:
        # Check if Pulumi is logged in
        result = subprocess.run(
            ['pulumi', 'whoami'], 
            capture_output=True, 
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ Pulumi logged in as: {result.stdout.strip()}")
        else:
            print("❌ Pulumi not logged in")
            return False
        
        # Check if we can access ESC config
        from backend.core.auto_esc_config import get_config_value
        
        # Test a few common configs
        test_configs = [
            'docker_hub_username',
            'environment',
            'pulumi_org',
        ]
        
        accessible = 0
        for config in test_configs:
            try:
                value = get_config_value(config)
                if value:
                    accessible += 1
            except:
                pass
        
        if accessible > 0:
            print(f"✅ Pulumi ESC accessible ({accessible}/{len(test_configs)} test configs found)")
            return True
        else:
            print("❌ Pulumi ESC not accessible")
            return False
            
    except Exception as e:
        print(f"❌ Error checking Pulumi ESC: {e}")
        return False

def should_skip_file(filepath):
    """Check if file should be skipped"""
    
    path_str = str(filepath)
    
    for pattern in SKIP_PATTERNS:
        if pattern.startswith('*'):
            if path_str.endswith(pattern[1:]):
                return True
        elif pattern in path_str:
            return True
    
    return False

def scan_file_for_secrets(filepath):
    """Scan a single file for potential secrets"""
    
    findings = []
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        # Check each pattern
        for secret_type, pattern in SECRET_PATTERNS.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            
            # Filter out obvious placeholders
            real_matches = []
            for match in matches:
                if not any(placeholder in match.upper() for placeholder in [
                    'YOUR_', 'PLACEHOLDER', 'EXAMPLE', 'FAKE', 'TEST', 'DUMMY'
                ]):
                    real_matches.append(match)
            
            if real_matches:
                # Find line numbers
                lines = content.split('\n')
                for match in real_matches:
                    for i, line in enumerate(lines):
                        if match in line:
                            findings.append({
                                'type': secret_type,
                                'file': str(filepath),
                                'line': i + 1,
                                'preview': line.strip()[:80] + '...' if len(line.strip()) > 80 else line.strip()
                            })
                            
    except Exception as e:
        # Skip files that can't be read
        pass
    
    return findings

def scan_repository():
    """Scan entire repository for secrets"""
    
    print("\n🔍 Scanning repository for hardcoded secrets...")
    
    all_findings = []
    files_scanned = 0
    
    # Scan all files
    for filepath in Path('.').rglob('*'):
        if filepath.is_file() and not should_skip_file(filepath):
            findings = scan_file_for_secrets(filepath)
            if findings:
                all_findings.extend(findings)
            files_scanned += 1
            
            # Progress indicator
            if files_scanned % 100 == 0:
                print(f"  Scanned {files_scanned} files...")
    
    print(f"\n📊 Scanned {files_scanned} files")
    
    return all_findings

def check_env_files():
    """Check for any remaining .env files"""
    
    print("\n🔍 Checking for .env files...")
    
    env_files = []
    
    for pattern in ['*.env', '.env*']:
        for filepath in Path('.').rglob(pattern):
            if filepath.is_file():
                # Skip templates and examples
                if not any(skip in str(filepath) for skip in ['template', 'example', 'backup']):
                    env_files.append(filepath)
    
    return env_files

def generate_report(findings, env_files):
    """Generate a verification report"""
    
    print("\n" + "=" * 60)
    print("📋 SECRET MIGRATION VERIFICATION REPORT")
    print("=" * 60)
    
    # Group findings by type
    by_type = defaultdict(list)
    for finding in findings:
        by_type[finding['type']].append(finding)
    
    if findings:
        print(f"\n🚨 Found {len(findings)} potential secrets:")
        
        for secret_type, items in by_type.items():
            print(f"\n{secret_type} ({len(items)} found):")
            for item in items[:3]:  # Show first 3
                print(f"  - {item['file']}:{item['line']}")
                print(f"    {item['preview']}")
            if len(items) > 3:
                print(f"  ... and {len(items) - 3} more")
    else:
        print("\n✅ No hardcoded secrets found!")
    
    if env_files:
        print(f"\n🚨 Found {len(env_files)} .env files:")
        for filepath in env_files:
            print(f"  - {filepath}")
    else:
        print("\n✅ No .env files found (except templates)!")
    
    # Recommendations
    print("\n📋 Recommendations:")
    
    if findings:
        print("  1. Review each finding to determine if it's a real secret")
        print("  2. Migrate real secrets to Pulumi ESC using:")
        print("     python scripts/migrate_env_to_esc.py <file>")
        print("  3. Update code to use get_config_value()")
    
    if env_files:
        print("  1. Review each .env file")
        print("  2. Migrate contents to Pulumi ESC")
        print("  3. Delete the .env files")
    
    if not findings and not env_files:
        print("  ✅ Your repository appears to be clean of secrets!")
        print("  🎉 Great job on the migration!")
    
    return len(findings) == 0 and len(env_files) == 0

def main():
    """Main verification function"""
    
    print("🔐 Sophia AI Secret Migration Verification")
    print("=" * 60)
    
    # Check Pulumi ESC
    esc_ok = check_pulumi_esc_integration()
    
    # Scan for secrets
    findings = scan_repository()
    
    # Check for env files
    env_files = check_env_files()
    
    # Generate report
    all_clear = generate_report(findings, env_files)
    
    # Final status
    print("\n" + "=" * 60)
    if all_clear and esc_ok:
        print("✅ VERIFICATION PASSED - Repository is clean!")
        return 0
    else:
        print("❌ VERIFICATION FAILED - Issues found")
        return 1

if __name__ == "__main__":
    exit(main()) 