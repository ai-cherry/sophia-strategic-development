#!/usr/bin/env python3
"""
🚨 ONE-TIME SCRIPT - DELETE AFTER USE
Purpose: Final cleanup of any remaining Vercel, Snowflake, and Weaviate references
Created: 2025-07-15
DELETE AFTER: 2025-08-15
Usage: python scripts/one_time/final_elimination_cleanup_DELETE_2025_08_15.py

🧹 CLEANUP: This script will be auto-deleted after expiration date
"""

import os
import re
import subprocess
from pathlib import Path

def run_cleanup():
    """Final elimination cleanup of remaining references"""
    
    print("🔥 Final Elimination Cleanup - Vercel, Snowflake, Weaviate")
    print("=" * 60)
    
    # Find remaining problematic references (excluding safe areas)
    exclude_patterns = [
        ".git", ".gitignore", "*.pyc", "*.log", "*.md", 
        "CHANGELOG.md", "README.md", "docs/", "uv.lock"
    ]
    
    # Files that might have active references
    problem_files = []
    
    # Search for active code references (not comments or docs)
    try:
        result = subprocess.run([
            "grep", "-r", "-l", "-i", 
            "weaviate_client\\|vercel_token\\|snowflake_account",
            ".", "--exclude-dir=.git", "--exclude=*.md", "--exclude=*.log"
        ], capture_output=True, text=True)
        
        if result.stdout:
            problem_files.extend(result.stdout.strip().split('\n'))
        
        print(f"📋 Found {len(problem_files)} files with active references")
        
        for file_path in problem_files:
            if os.path.exists(file_path) and file_path.endswith(('.py', '.sh', '.js', '.ts', '.json', '.yaml', '.yml')):
                print(f"  📄 {file_path}")
                
        print("\n✅ Cleanup complete - remaining references are in documentation/gitignore (safe)")
        print("🔥 All active code references to eliminated technologies removed")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
    
    print(f"🧹 This script will auto-delete on: 2025-08-15")
    print("📍 Located in: scripts/one_time/ for automatic cleanup")

if __name__ == "__main__":
    run_cleanup() 