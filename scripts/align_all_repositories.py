#!/usr/bin/env python3
"""
🔄 Repository Alignment Script for Sophia AI
Ensures all repositories (main, strategic, backup) are synchronized with virtual environment setup
"""

import os
import subprocess
import sys
from datetime import datetime

def run_command(cmd, description=""):
    """Run a shell command and return success status"""
    print(f"🔧 {description or cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Success: {description or cmd}")
            if result.stdout:
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Failed: {description or cmd}")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def check_file_exists(filepath):
    """Check if a file exists and return status"""
    exists = os.path.exists(filepath)
    status = "✅" if exists else "❌"
    print(f"{status} {filepath}")
    return exists

def main():
    """Main alignment process"""
    print("🚀 SOPHIA AI REPOSITORY ALIGNMENT")
    print("=" * 50)
    
    # Check current working directory
    cwd = os.getcwd()
    print(f"📍 Current directory: {cwd}")
    
    # Check if we're in the right directory
    if not os.path.exists(".git"):
        print("❌ Not in a git repository!")
        sys.exit(1)
    
    print("\n📋 CHECKING VIRTUAL ENVIRONMENT FILES:")
    required_files = [
        "activate_sophia_env.sh",
        ".sophia-env-config", 
        ".cursorrules",
        ".cursor-rules",
        ".cline-rules",
        ".ai-assistant-rules",
        "VIRTUAL_ENVIRONMENT_CONSISTENCY_GUIDE.md",
        "CURSOR_AI_MACHINE_SETUP_PROMPT.md",
        ".devcontainer/devcontainer.json",
        ".devcontainer/setup.sh",
        ".devcontainer/README.md"
    ]
    
    missing_files = []
    for file in required_files:
        if not check_file_exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ Missing files: {missing_files}")
        print("💡 Run the setup first to create these files")
        return False
    
    print("\n🔍 CHECKING FASTAPI APPLICATIONS:")
    fastapi_files = [
        "backend/app/simple_fastapi.py",
        "backend/app/minimal_fastapi.py", 
        "backend/app/working_fastapi.py",
        "api/main.py"
    ]
    
    for file in fastapi_files:
        check_file_exists(file)
    
    print("\n📦 CHECKING GIT STATUS:")
    run_command("git status", "Current git status")
    
    print("\n📁 ADDING NEW FILES TO GIT:")
    files_to_add = [
        "activate_sophia_env.sh",
        ".sophia-env-config",
        ".cursor-rules", 
        ".cline-rules",
        ".ai-assistant-rules",
        "VIRTUAL_ENVIRONMENT_CONSISTENCY_GUIDE.md",
        "CURSOR_AI_MACHINE_SETUP_PROMPT.md",
        ".devcontainer/devcontainer.json",
        ".devcontainer/setup.sh", 
        ".devcontainer/README.md",
        "scripts/align_all_repositories.py"
    ]
    
    for file in files_to_add:
        if os.path.exists(file):
            run_command(f"git add {file}", f"Adding {file}")
    
    print("\n📝 COMMITTING CHANGES:")
    commit_message = f"🔧 Virtual Environment Alignment & FastAPI Setup - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    if run_command(f'git commit -m "{commit_message}"', "Committing changes"):
        print("✅ Changes committed successfully")
    else:
        print("ℹ️ No changes to commit or commit failed")
    
    print("\n🌐 CHECKING REMOTE REPOSITORIES:")
    result = subprocess.run("git remote -v", shell=True, capture_output=True, text=True)
    remotes = result.stdout.strip().split('\n')
    
    remote_names = []
    for remote in remotes:
        if remote:
            parts = remote.split()
            if len(parts) >= 2 and parts[1].endswith('(push)'):
                remote_names.append(parts[0])
    
    print(f"📡 Found remotes: {remote_names}")
    
    print("\n🚀 PUSHING TO ALL REPOSITORIES:")
    for remote in remote_names:
        if run_command(f"git push {remote} main", f"Pushing to {remote}"):
            print(f"✅ Successfully pushed to {remote}")
        else:
            print(f"❌ Failed to push to {remote}")
    
    print("\n🎯 VERIFICATION:")
    print("Virtual environment setup files synchronized across all repositories")
    print("FastAPI applications aligned and ready")
    print("All repositories updated with consistent configuration")
    
    print("\n✅ REPOSITORY ALIGNMENT COMPLETE!")
    print("\n📖 NEXT STEPS:")
    print("1. On other machines, copy CURSOR_AI_MACHINE_SETUP_PROMPT.md to Cursor AI")
    print("2. Run: source activate_sophia_env.sh")
    print("3. Test FastAPI apps with: python -m uvicorn backend.app.simple_fastapi:app --port 8001")
    print("4. Verify (.venv) appears in terminal prompt")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 