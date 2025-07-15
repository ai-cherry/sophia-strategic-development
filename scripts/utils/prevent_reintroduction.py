#!/usr/bin/env python3
"""
🚫 PREVENTION SCRIPT - Block Snowflake/Weaviate/Vercel Reintroduction
Run before any commits to ensure eliminated technologies stay eliminated
"""

import os
import sys
import re

FORBIDDEN_PATTERNS = [
    r'import\s+weaviate',
    r'from\s+weaviate',
    r'snowflake',
    r'SNOWFLAKE',
    r'qdrant_memory',
    r'vercel\s+deploy',
    r'LAMBDA_LABS_TOKEN'
]

def scan_repository():
    violations = []
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules']]
        
        for file in files:
            if file.endswith(('.py', '.js', '.ts', '.json', '.yaml', '.yml')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        for pattern in FORBIDDEN_PATTERNS:
                            if re.search(pattern, content, re.IGNORECASE):
                                violations.append(f"{file_path}: {pattern}")
                except:
                    continue
    
    return violations

if __name__ == "__main__":
    violations = scan_repository()
    if violations:
        print("❌ FORBIDDEN TECHNOLOGY DETECTED:")
        for violation in violations:
            print(f"  {violation}")
        sys.exit(1)
    else:
        print("✅ Repository clean - no forbidden technologies detected")
        sys.exit(0)
