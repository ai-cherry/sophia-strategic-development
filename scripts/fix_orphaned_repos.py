#!/usr/bin/env python3
"""
Quick fix for orphaned git repositories in external/
"""

import os
import subprocess
import shutil
from pathlib import Path

def log(message):
    print(f"[INFO] {message}")

def run_command(cmd, cwd=None):
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    repo_root = Path(".").resolve()
    external_dir = repo_root / "external"
    
    log("🔧 Fixing orphaned repositories in external/")
    
    # These are the orphaned repos that aren't configured as submodules
    orphaned_repos = [
        "davidamom_snowflake",
        "dynamike_snowflake", 
        "isaacwasserman_snowflake",
        "snowflake_cortex_official",
        "glips_figma_context",
        "microsoft_playwright",
        "openrouter_search",
        "portkey_admin"
    ]
    
    for repo_name in orphaned_repos:
        repo_path = external_dir / repo_name
        if repo_path.exists():
            log(f"Cleaning orphaned repo: {repo_name}")
            
            # Reset any changes in the repo
            success, stdout, stderr = run_command(
                ["git", "reset", "--hard", "HEAD"], 
                cwd=repo_path
            )
            if success:
                log(f"  ✅ Reset {repo_name}")
            else:
                log(f"  ⚠️  Failed to reset {repo_name}: {stderr}")
            
            # Clean untracked files
            success, stdout, stderr = run_command(
                ["git", "clean", "-fd"], 
                cwd=repo_path
            )
            if success:
                log(f"  ✅ Cleaned {repo_name}")
            else:
                log(f"  ⚠️  Failed to clean {repo_name}: {stderr}")
    
    log("🎉 Orphaned repository cleanup completed!")

if __name__ == "__main__":
    main()
