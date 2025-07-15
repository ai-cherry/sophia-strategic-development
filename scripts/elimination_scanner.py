#!/usr/bin/env python3
"""
Bulletproof elimination scanner
Prevents reintroduction of eliminated technologies
"""

import re
import sys
from pathlib import Path

FORBIDDEN_PATTERNS = [
    r'(?i)weaviate', r'(?i)lambda_labs', r'(?i)snowflake',
    r'import.*weaviate', r'from.*weaviate',
    r'import.*snowflake', r'from.*snowflake',
    r'WEAVIATE_', r'lambda_labs', r'SNOWFLAKE_',
    r'weaviate\.', r'lambda_labs\.', r'snowflake\.',
    r'\.lambda_labs\.app', r'lambda_labs\.json',
    r'snowflake\.com', r'weaviate\.io',
    r'semitechnologies/weaviate',
    r'snowflake/snowflake',
    r'weaviate-client', r'snowflake-connector',
    r'@lambda_labs/', r'lambda_labs-cli',
]

def scan_for_violations():
    """Scan for eliminated technology violations"""
    violations = 0
    
    for ext in ['.py', '.ts', '.js', '.json', '.yaml', '.yml', '.md']:
        files = list(Path('.').rglob(f"*{ext}"))
        
        for file_path in files:
            if any(skip in str(file_path) for skip in ['.git', 'node_modules', '.venv']):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                for pattern in FORBIDDEN_PATTERNS:
                    if re.search(pattern, content, re.IGNORECASE):
                        print(f"❌ VIOLATION: {file_path} contains eliminated technology")
                        violations += 1
                        break
                        
            except Exception:
                continue
    
    return violations

if __name__ == "__main__":
    violations = scan_for_violations()
    if violations > 0:
        print(f"❌ {violations} violations found")
        sys.exit(1)
    else:
        print("✅ No violations found")
        sys.exit(0)
