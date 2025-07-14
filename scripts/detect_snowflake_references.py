#!/usr/bin/env python3
"""
Snowflake Detection Script
Scans for any new Snowflake/modern_stack references
"""

import os
import re
from pathlib import Path

def scan_for_snowflake():
    """Scan for Snowflake references"""
    patterns = [r'modern_stack', r'snowflake', r'SNOWFLAKE', r'ModernStack']
    found_references = []
    
    for pattern in patterns:
        result = os.popen(f'grep -r -i "{pattern}" . --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=elimination_backup').read()
        if result.strip():
            found_references.append((pattern, result))
            
    if found_references:
        print("❌ SNOWFLAKE REFERENCES DETECTED:")
        for pattern, results in found_references:
            print(f"\nPattern: {pattern}")
            print(results)
        return False
    else:
        print("✅ No Snowflake references detected")
        return True

if __name__ == "__main__":
    scan_for_snowflake()
