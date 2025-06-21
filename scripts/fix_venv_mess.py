#!/usr/bin/env python3
"""
Emergency script to fix the virtual environment mess in Sophia AI repository.
This script will:
1. Scan venv directories for any custom project code
2. Move legitimate files to correct locations
3. Remove venv directories from Git
4. Update .gitignore
5. Fix any other structural issues
"""

import os
import shutil
import subprocess
from pathlib import Path
import re
import json

class VenvCleanup:
    def __init__(self):
        self.project_root = Path.cwd()
        self.venv_dirs = []
        self.custom_files = []
        self.moved_files = []
        self.standard_packages = {
            'pip', 'setuptools', 'wheel', 'pkg_resources', 'distutils',
            'asyncpg', 'greenlet', 'werkzeug', 'urllib3', 'chardet',
            'html5lib', 'resolvelib', 'certifi', 'idna', 'requests'
        }
        
    def find_venv_directories(self):
        """Find all virtual environment directories."""
        print("🔍 Searching for virtual environment directories...")
        
        patterns = ['venv', '*_venv', '.venv', 'env', 'ENV', '.env', 'virtualenv']
        
        for pattern in patterns:
            for path in self.project_root.rglob(pattern):
                if path.is_dir() and 'site-packages' in [p.name for p in path.rglob('*')]:
                    self.venv_dirs.append(path)
                    print(f"  Found venv: {path}")
        
        # Also check specific known locations
        known_venvs = [
            'sophia_admin_api/venv',
            'sophia_venv',
            'frontend/node_modules'  # Also check for node_modules
        ]
        
        for venv in known_venvs:
            path = self.project_root / venv
            if path.exists():
                self.venv_dirs.append(path)
                print(f"  Found known venv: {path}")
                
    def scan_for_custom_code(self):
        """Scan venv directories for any custom project code."""
        print("\n🔍 Scanning for custom code in venv directories...")
        
        for venv_dir in self.venv_dirs:
            for file_path in venv_dir.rglob('*.py'):
                # Skip standard library and third-party packages
                relative_path = str(file_path.relative_to(venv_dir))
                
                # Check if this might be custom code
                if self._is_likely_custom_code(file_path, relative_path):
                    self.custom_files.append(file_path)
                    print(f"  ⚠️  Found potential custom code: {file_path}")
                    
    def _is_likely_custom_code(self, file_path, relative_path):
        """Determine if a file is likely custom project code."""
        # Skip if in site-packages of known packages
        for pkg in self.standard_packages:
            if pkg in relative_path:
                return False
                
        # Skip __pycache__ and .pyc files
        if '__pycache__' in relative_path or file_path.suffix == '.pyc':
            return False
            
        # Skip standard venv structure files
        if any(x in relative_path for x in ['site-packages', 'lib/python', 'bin/', 'Scripts/']):
            # But check for sophia/backend/agents etc in the path
            if any(x in relative_path.lower() for x in ['sophia', 'backend', 'agents', 'mcp']):
                return True
            return False
            
        # Check file content for project-specific imports or code
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(1000)  # Read first 1000 chars
                
                # Look for project-specific imports or references
                project_indicators = [
                    'from backend', 'import backend',
                    'from agents', 'import agents',
                    'sophia', 'pay_ready', 'PayReady',
                    'from infrastructure', 'import infrastructure'
                ]
                
                for indicator in project_indicators:
                    if indicator in content:
                        return True
                        
        except Exception:
            pass
            
        return False
        
    def move_custom_files(self):
        """Move any found custom files to appropriate locations."""
        if not self.custom_files:
            print("\n✅ No custom code found in venv directories!")
            return
            
        print(f"\n📦 Found {len(self.custom_files)} custom files to move...")
        
        for file_path in self.custom_files:
            # Try to determine the correct location
            new_location = self._determine_correct_location(file_path)
            
            if new_location:
                # Create directory if it doesn't exist
                new_location.parent.mkdir(parents=True, exist_ok=True)
                
                # Move the file
                print(f"  Moving: {file_path}")
                print(f"      To: {new_location}")
                
                try:
                    shutil.copy2(file_path, new_location)
                    self.moved_files.append((file_path, new_location))
                except Exception as e:
                    print(f"  ❌ Error moving file: {e}")
                    
    def _determine_correct_location(self, file_path):
        """Determine the correct location for a misplaced file."""
        file_name = file_path.name
        file_content = ""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
        except:
            pass
            
        # Check for specific patterns in filename or content
        if 'agent' in file_name.lower() or 'from backend.agents' in file_content:
            # Likely an agent file
            if 'specialized' in file_content:
                return self.project_root / 'backend' / 'agents' / 'specialized' / file_name
            elif 'core' in file_content:
                return self.project_root / 'backend' / 'agents' / 'core' / file_name
            else:
                return self.project_root / 'backend' / 'agents' / file_name
                
        elif 'mcp' in file_name.lower() or 'mcp_server' in file_content:
            return self.project_root / 'backend' / 'mcp' / file_name
            
        elif 'integration' in file_name.lower():
            return self.project_root / 'backend' / 'integrations' / file_name
            
        elif 'test_' in file_name:
            return self.project_root / 'tests' / file_name
            
        elif 'script' in file_name.lower() or file_path.parent.name == 'scripts':
            return self.project_root / 'scripts' / file_name
            
        # Default: put in a recovery folder
        return self.project_root / 'recovered_files' / file_name
        
    def update_gitignore(self):
        """Update .gitignore with proper entries."""
        print("\n📝 Updating .gitignore...")
        
        gitignore_content = """# Virtual Environments
venv/
*venv/
*/venv/
**/venv/
**/*_venv/
.venv/
env/
ENV/
.env/
virtualenv/
.virtualenv/
pipenv/
.pipenv/

# Node modules
node_modules/
**/node_modules/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# IDE
.idea/
.vscode/
*.swp
*.swo
*~
.DS_Store

# Logs
logs/
*.log

# Environment variables
.env
.env.local
.env.*.local

# Temporary files
*.tmp
*.temp
*.bak
*.swp
*~

# OS
.DS_Store
Thumbs.db
desktop.ini

# Coverage
htmlcov/
.coverage
.coverage.*
coverage.xml
*.cover

# pytest
.pytest_cache/

# mypy
.mypy_cache/
.dmypy.json
dmypy.json
"""
        
        gitignore_path = self.project_root / '.gitignore'
        
        # Read existing .gitignore if it exists
        existing_content = ""
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                existing_content = f.read()
                
        # Merge content (avoid duplicates)
        if 'venv/' not in existing_content:
            with open(gitignore_path, 'w') as f:
                f.write(gitignore_content)
            print("  ✅ Updated .gitignore")
        else:
            print("  ℹ️  .gitignore already contains venv entries")
            
    def remove_venv_from_git(self):
        """Remove venv directories from Git tracking."""
        print("\n🗑️  Removing venv directories from Git...")
        
        for venv_dir in self.venv_dirs:
            if venv_dir.exists():
                try:
                    # Remove from git tracking but keep locally
                    cmd = f'git rm -r --cached "{venv_dir}"'
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        print(f"  ✅ Removed from Git: {venv_dir}")
                    else:
                        print(f"  ℹ️  Not in Git or already removed: {venv_dir}")
                        
                except Exception as e:
                    print(f"  ❌ Error removing {venv_dir}: {e}")
                    
    def fix_malformed_filenames(self):
        """Fix files with malformed names."""
        print("\n🔧 Fixing malformed filenames...")
        
        malformed_patterns = [
            ('backend/agents/core/agent_framework.py and infrastructure', 
             'backend/agents/core/agent_framework_infrastructure.py'),
            ('infrastructure/kubernetes/components/lambda_labs_instance.py and backend/mcp/mcp_client.py',
             'infrastructure/kubernetes/components/lambda_labs_instance_mcp_client.py'),
            ('backend/agents/core/agent_framework.py and infrastructure/kubernetes/developer_tools_mcp_stack.py',
             'backend/agents/core/agent_framework_developer_tools.py')
        ]
        
        for old_name, new_name in malformed_patterns:
            old_path = self.project_root / old_name
            new_path = self.project_root / new_name
            
            if old_path.exists():
                try:
                    old_path.rename(new_path)
                    print(f"  ✅ Renamed: {old_name}")
                    print(f"        To: {new_name}")
                except Exception as e:
                    print(f"  ❌ Error renaming {old_name}: {e}")
                    
    def create_summary_report(self):
        """Create a summary report of the cleanup."""
        print("\n📊 Creating cleanup summary report...")
        
        report = {
            "venv_directories_found": len(self.venv_dirs),
            "custom_files_found": len(self.custom_files),
            "files_moved": len(self.moved_files),
            "venv_dirs": [str(d) for d in self.venv_dirs],
            "moved_files": [
                {
                    "from": str(src),
                    "to": str(dst)
                } for src, dst in self.moved_files
            ]
        }
        
        report_path = self.project_root / 'venv_cleanup_report.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"  ✅ Report saved to: {report_path}")
        
    def run_cleanup(self):
        """Run the complete cleanup process."""
        print("🚀 Starting Sophia AI Virtual Environment Cleanup")
        print("=" * 60)
        
        # Step 1: Find venv directories
        self.find_venv_directories()
        
        if not self.venv_dirs:
            print("\n✅ No virtual environment directories found!")
            return
            
        # Step 2: Scan for custom code
        self.scan_for_custom_code()
        
        # Step 3: Move custom files
        self.move_custom_files()
        
        # Step 4: Update .gitignore
        self.update_gitignore()
        
        # Step 5: Remove venv from Git
        self.remove_venv_from_git()
        
        # Step 6: Fix malformed filenames
        self.fix_malformed_filenames()
        
        # Step 7: Create summary report
        self.create_summary_report()
        
        print("\n" + "=" * 60)
        print("✅ Cleanup Complete!")
        print(f"  - Found {len(self.venv_dirs)} venv directories")
        print(f"  - Found {len(self.custom_files)} custom files")
        print(f"  - Moved {len(self.moved_files)} files")
        
        print("\n📋 Next Steps:")
        print("1. Review the moved files in their new locations")
        print("2. Delete the venv directories: rm -rf sophia_admin_api/venv sophia_venv")
        print("3. Run: git add .")
        print("4. Run: git commit -m 'Fix: Remove venv from Git and recover misplaced files'")
        print("5. Run: git push")
        print("\n⚠️  Remember to recreate your virtual environments properly!")


if __name__ == "__main__":
    cleanup = VenvCleanup()
    cleanup.run_cleanup()
