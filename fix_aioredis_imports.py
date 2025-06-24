#!/usr/bin/env python3
"""
Script to systematically replace all aioredis imports with redis.asyncio
Fixes Python 3.11 compatibility issues
"""

import os
import re
import glob

def find_and_replace_aioredis():
    """Find and replace all aioredis imports in Python files"""
    
    # Patterns to find and replace
    replacements = [
        # Direct imports
        (r'^import redis_client$', 'import redis.asyncio as redis_client'),
        (r'^import redis_client\s+as\s+\w+$', 'import redis.asyncio as redis_client'),
        
        # From imports
        (r'^from aioredis import (.+)$', r'from redis.asyncio import \1'),
        
        # Usage patterns
        (r'\baioredis\.', 'redis_client.'),
        (r'\baioredis\b(?!\.)(?!\s*import)', 'redis_client'),
    ]
    
    # Find all Python files
    python_files = []
    for root, dirs, files in os.walk('.'):
        # Skip virtual environment and other directories
        if '/.venv/' in root or '/__pycache__/' in root or '/.git/' in root:
            continue
            
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    print(f"Found {len(python_files)} Python files to check")
    
    modified_files = []
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Apply all replacements
            for pattern, replacement in replacements:
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            
            # Check if file was modified
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                modified_files.append(file_path)
                print(f"✅ Modified: {file_path}")
        
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
    
    print(f"\n🎉 Completed! Modified {len(modified_files)} files:")
    for file_path in modified_files:
        print(f"  - {file_path}")
    
    return modified_files

def verify_no_aioredis_imports():
    """Verify no aioredis imports remain"""
    print("\n🔍 Verifying no aioredis imports remain...")
    
    remaining_files = []
    
    for root, dirs, files in os.walk('.'):
        if '/.venv/' in root or '/__pycache__/' in root or '/.git/' in root:
            continue
            
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if 'redis_client' in content:
                        remaining_files.append(file_path)
                        print(f"⚠️  Still contains 'redis_client': {file_path}")
                        
                        # Show the lines containing redis_client
                        lines = content.split('\n')
                        for i, line in enumerate(lines, 1):
                            if 'redis_client' in line:
                                print(f"    Line {i}: {line.strip()}")
                
                except Exception as e:
                    print(f"❌ Error checking {file_path}: {e}")
    
    if not remaining_files:
        print("✅ No aioredis imports found!")
    else:
        print(f"❌ Found redis_client in {len(remaining_files)} files")
    
    return remaining_files

if __name__ == "__main__":
    print("🚀 Starting redis_client cleanup...")
    
    # Step 1: Replace imports
    modified_files = find_and_replace_aioredis()
    
    # Step 2: Verify cleanup
    remaining_files = verify_no_aioredis_imports()
    
    if not remaining_files:
        print("\n🎉 SUCCESS: All aioredis imports have been replaced!")
        print("✅ Python 3.11 compatibility issues should be resolved")
    else:
        print(f"\n⚠️  WARNING: {len(remaining_files)} files still contain redis_client")
        print("Manual review may be needed for these files") 