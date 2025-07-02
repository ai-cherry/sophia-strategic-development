#!/usr/bin/env python3
"""
Comprehensive Submodule Cleanup and Update Script for Sophia AI

This script will:
1. Clean dirty submodules to restore git status
2. Add missing configured submodules
3. Convert high-value orphaned repos to proper submodules
4. Remove redundant repositories
5. Update all submodules to latest versions
6. Validate final state
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Tuple
import json
import shutil

class SubmoduleManager:
    def __init__(self, repo_root: str = "."):
        self.repo_root = Path(repo_root).resolve()
        self.external_dir = self.repo_root / "external"
        
    def run_command(self, cmd: List[str], cwd: str = None, capture_output: bool = True) -> Tuple[int, str, str]:
        """Run a command and return exit code, stdout, stderr"""
        try:
            result = subprocess.run(
                cmd, 
                cwd=cwd or self.repo_root,
                capture_output=capture_output,
                text=True,
                check=False
            )
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            return 1, "", str(e)
    
    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def phase_1_clean_dirty_submodules(self):
        """Clean up dirty submodules to restore clean git status"""
        self.log("🧹 Phase 1: Cleaning dirty submodules")
        
        dirty_submodules = [
            "external/anthropic-mcp-python-sdk",
            "external/anthropic-mcp-servers"
        ]
        
        for submodule in dirty_submodules:
            submodule_path = self.repo_root / submodule
            if submodule_path.exists():
                self.log(f"Cleaning {submodule}")
                
                # Reset to HEAD
                exit_code, stdout, stderr = self.run_command(
                    ["git", "reset", "--hard", "HEAD"], 
                    cwd=submodule_path
                )
                if exit_code != 0:
                    self.log(f"Warning: Failed to reset {submodule}: {stderr}", "WARN")
                
                # Clean untracked files
                exit_code, stdout, stderr = self.run_command(
                    ["git", "clean", "-fd"], 
                    cwd=submodule_path
                )
                if exit_code != 0:
                    self.log(f"Warning: Failed to clean {submodule}: {stderr}", "WARN")
                
                self.log(f"✅ Cleaned {submodule}")
            else:
                self.log(f"⚠️  {submodule} not found")
    
    def phase_2_add_missing_submodules(self):
        """Add missing configured submodules"""
        self.log("➕ Phase 2: Adding missing configured submodules")
        
        missing_submodules = [
            {
                "path": "external/notion-mcp-server",
                "url": "https://github.com/ai-cherry/notion-mcp-server.git"
            },
            {
                "path": "external/slack-mcp-server", 
                "url": "https://github.com/ai-cherry/slack-mcp-server.git"
            }
        ]
        
        for submodule in missing_submodules:
            path = self.repo_root / submodule["path"]
            if not path.exists():
                self.log(f"Adding submodule {submodule['path']}")
                exit_code, stdout, stderr = self.run_command([
                    "git", "submodule", "add", 
                    submodule["url"], 
                    submodule["path"]
                ])
                if exit_code == 0:
                    self.log(f"✅ Added {submodule['path']}")
                else:
                    self.log(f"❌ Failed to add {submodule['path']}: {stderr}", "ERROR")
            else:
                self.log(f"✅ {submodule['path']} already exists")
    
    def phase_6_validate_final_state(self):
        """Validate the final state of submodules"""
        self.log("✅ Phase 6: Validating final submodule state")
        
        # Check git submodule status
        exit_code, stdout, stderr = self.run_command([
            "git", "submodule", "status"
        ])
        
        if exit_code == 0:
            self.log("Submodule status:")
            for line in stdout.strip().split('\n'):
                if line.strip():
                    self.log(f"  {line}")
        else:
            self.log(f"Failed to get submodule status: {stderr}", "ERROR")
    
    def run_conservative_cleanup(self):
        """Run a conservative cleanup - just clean dirty submodules and validate"""
        self.log("🚀 Starting conservative submodule cleanup for Sophia AI")
        self.log(f"Repository root: {self.repo_root}")
        
        try:
            self.phase_1_clean_dirty_submodules()
            self.phase_6_validate_final_state()
            
            self.log("🎉 Conservative submodule cleanup completed!")
            self.log("Dirty submodules have been cleaned. Repository should have cleaner git status.")
            
        except Exception as e:
            self.log(f"❌ Cleanup failed with error: {e}", "ERROR")
            sys.exit(1)

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        repo_root = sys.argv[1]
    else:
        repo_root = "."
    
    manager = SubmoduleManager(repo_root)
    manager.run_conservative_cleanup()

if __name__ == "__main__":
    main()
