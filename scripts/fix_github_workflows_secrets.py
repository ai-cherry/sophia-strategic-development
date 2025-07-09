#!/usr/bin/env python3
"""
Fix ALL GitHub workflows to use consistent Docker secret names.
This ensures DOCKER_USERNAME and DOCKER_TOKEN are used everywhere.
"""

import os
import re
from pathlib import Path

# Mapping of old names to new names
SECRET_REPLACEMENTS = {
    # Docker Hub
    "DOCKER_HUB_USERNAME": "DOCKER_USERNAME",
    "DOCKER_HUB_TOKEN": "DOCKER_TOKEN",
    "DOCKER_HUB_ACCESS_TOKEN": "DOCKER_TOKEN",
    "DOCKER_PERSONAL_ACCESS_TOKEN": "DOCKER_TOKEN",
    "DOCKER_PASSWORD": "DOCKER_TOKEN",
    
    # Keep these for reference but don't change them
    # These are other secrets that should remain as-is
}

def fix_workflow_file(filepath: Path) -> bool:
    """Fix secret names in a workflow file"""
    print(f"📄 Checking {filepath.name}...")
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    original_content = content
    changes_made = False
    
    # Fix Docker Hub secret references
    for old_name, new_name in SECRET_REPLACEMENTS.items():
        # Pattern 1: ${{ secrets.OLD_NAME }}
        pattern1 = rf'\$\{{\{{\s*secrets\.{old_name}\s*\}}\}}'
        if re.search(pattern1, content):
            content = re.sub(pattern1, f'${{{{ secrets.{new_name} }}}}', content)
            print(f"  ✅ Replaced secrets.{old_name} → secrets.{new_name}")
            changes_made = True
        
        # Pattern 2: env.OLD_NAME in some cases
        pattern2 = rf'\benv\.{old_name}\b'
        if re.search(pattern2, content):
            content = re.sub(pattern2, f'env.{new_name}', content)
            print(f"  ✅ Replaced env.{old_name} → env.{new_name}")
            changes_made = True
    
    # Special case: username field in docker/login-action
    # Find patterns like:
    # username: ${{ env.DOCKER_REGISTRY }}
    # and replace with:
    # username: ${{ secrets.DOCKERHUB_USERNAME }}
    docker_login_pattern = r'(username:\s*\$\{{\s*env\.DOCKER_REGISTRY\s*\}\})'
    if re.search(docker_login_pattern, content):
        content = re.sub(docker_login_pattern, 'username: ${{ secrets.DOCKERHUB_USERNAME }}', content)
        print(f"  ✅ Fixed docker/login-action username to use secrets.DOCKERHUB_USERNAME")
        changes_made = True
    
    # Write back if changes were made
    if changes_made:
        with open(filepath, 'w') as f:
            f.write(content)
        return True
    else:
        print(f"  ✔️  No changes needed")
        return False

def fix_all_workflows():
    """Fix all GitHub workflow files"""
    workflows_dir = Path(".github/workflows")
    
    if not workflows_dir.exists():
        print("❌ .github/workflows directory not found!")
        return
    
    print("🔧 Fixing GitHub workflow files...")
    print("=" * 50)
    
    workflow_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
    print(f"Found {len(workflow_files)} workflow files\n")
    
    fixed_count = 0
    for workflow_file in sorted(workflow_files):
        if fix_workflow_file(workflow_file):
            fixed_count += 1
    
    print("\n" + "=" * 50)
    print(f"✅ Fixed {fixed_count} workflow files")
    print(f"📋 Total workflows checked: {len(workflow_files)}")

def generate_summary():
    """Generate a summary of what needs to be done"""
    print("\n📝 Summary of Changes:")
    print("\nDocker Hub Credentials:")
    print("  OLD → NEW")
    print("  DOCKER_HUB_USERNAME → DOCKER_USERNAME")
    print("  DOCKER_HUB_TOKEN → DOCKER_TOKEN")
    print("  DOCKER_HUB_ACCESS_TOKEN → DOCKER_TOKEN")
    print("  DOCKER_PERSONAL_ACCESS_TOKEN → DOCKER_TOKEN")
    print("  DOCKER_PASSWORD → DOCKER_TOKEN")
    
    print("\n⚠️  IMPORTANT:")
    print("1. Make sure these secrets exist in GitHub Organization:")
    print("   - DOCKER_USERNAME (value: scoobyjava15)")
    print("   - DOCKER_TOKEN (your Docker Hub access token)")
    print("\n2. After running this script, commit and push the changes")
    print("3. All workflows will use consistent secret names")

def main():
    print("🚀 GitHub Workflows Secret Name Fixer")
    print("This will standardize all Docker secret references")
    print("=" * 50 + "\n")
    
    # Fix all workflows
    fix_all_workflows()
    
    # Generate summary
    generate_summary()

if __name__ == "__main__":
    main() 