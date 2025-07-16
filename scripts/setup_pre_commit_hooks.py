#!/usr/bin/env python3
"""
Setup Pre-Commit Hooks for Technical Debt Prevention
Installs and configures pre-commit hooks to prevent technical debt accumulation
"""

import stat
import subprocess
import sys
from pathlib import Path

def setup_pre_commit_hook():
    """Set up pre-commit hook for technical debt prevention"""
    
    # Get git hooks directory
    git_dir = Path(".git")
    if not git_dir.exists():
        print("❌ Not a git repository")
        sys.exit(1)
    
    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(exist_ok=True)
    
    pre_commit_hook = hooks_dir / "pre-commit"
    
    # Pre-commit hook script
    hook_script = '''#!/bin/bash
# Technical Debt Prevention Pre-Commit Hook
# Automatically prevents technical debt accumulation

echo "🔍 Running technical debt prevention checks..."

# Run technical debt validation
python scripts/technical_debt_prevention.py --mode=validate

if [ $? -ne 0 ]; then
    echo "❌ Pre-commit blocked: Technical debt detected"
    echo "💡 Run 'python scripts/technical_debt_prevention.py --mode=validate' for details"
    exit 1
fi

# Check for archive directories
if git diff --cached --name-only | grep -E "(archive/|backup/|_archived/)" > /dev/null; then
    echo "❌ Pre-commit blocked: Archive directories detected"
    echo "💡 Remove archive directories and use git history instead"
    exit 1
fi

# Check for backup files
if git diff --cached --name-only | grep -E "\\.(backup|bak|old|tmp|temp)$" > /dev/null; then
    echo "❌ Pre-commit blocked: Backup files detected"
    echo "💡 Remove backup files and use git history instead"
    exit 1
fi

# Check for one-time scripts in wrong location
if git diff --cached --name-only | grep -E "scripts/(?!one_time/|utils/|monitoring/).*(?:deploy_|setup_|fix_|test_|migrate_|cleanup_)" > /dev/null; then
    echo "❌ Pre-commit blocked: One-time scripts in wrong location"
    echo "💡 Move one-time scripts to scripts/one_time/ directory"
    exit 1
fi

# Check file count
file_count=$(find . -type f -not -path "./.git/*" -not -path "./.venv/*" -not -path "./node_modules/*" | wc -l)
if [ $file_count -gt 250 ]; then
    echo "❌ Pre-commit blocked: File count exceeds limit ($file_count > 250)"
    echo "💡 Remove unnecessary files before committing"
    exit 1
fi

# Check repository size
repo_size=$(du -sm . 2>/dev/null | cut -f1 || echo "0")
if [ $repo_size -gt 500 ]; then
    echo "❌ Pre-commit blocked: Repository size exceeds limit (${repo_size}MB > 500MB)"
    echo "💡 Remove large files before committing"
    exit 1
fi

echo "✅ Technical debt prevention checks passed"
exit 0
'''
    
    # Write hook script
    with open(pre_commit_hook, 'w') as f:
        f.write(hook_script)
    
    # Make executable
    pre_commit_hook.chmod(pre_commit_hook.stat().st_mode | stat.S_IEXEC)
    
    print(f"✅ Pre-commit hook installed: {pre_commit_hook}")
    
    # Test the hook
    print("🔍 Testing pre-commit hook...")
    result = subprocess.run([str(pre_commit_hook)], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Pre-commit hook test passed")
    else:
        print("⚠️  Pre-commit hook test failed:")
        print(result.stdout)
        print(result.stderr)

def setup_commit_msg_hook():
    """Set up commit message hook for technical debt prevention"""
    
    hooks_dir = Path(".git/hooks")
    commit_msg_hook = hooks_dir / "commit-msg"
    
    # Commit message hook script
    hook_script = '''#!/bin/bash
# Technical Debt Prevention Commit Message Hook
# Ensures commit messages follow standards

commit_msg_file="$1"
commit_msg=$(cat "$commit_msg_file")

# Check for technical debt keywords in commit message
if echo "$commit_msg" | grep -iE "(TODO|FIXME|HACK|XXX|temporary|quick fix)" > /dev/null; then
    echo "⚠️  Commit message contains technical debt keywords"
    echo "💡 Consider resolving the technical debt before committing"
fi

# Check for proper commit message format
if ! echo "$commit_msg" | grep -E "^(feat|fix|docs|style|refactor|test|chore|perf|ci|build):" > /dev/null; then
    echo "⚠️  Commit message doesn't follow conventional commit format"
    echo "💡 Use format: type: description (e.g., feat: add new feature)"
fi

exit 0
'''
    
    # Write hook script
    with open(commit_msg_hook, 'w') as f:
        f.write(hook_script)
    
    # Make executable
    commit_msg_hook.chmod(commit_msg_hook.stat().st_mode | stat.S_IEXEC)
    
    print(f"✅ Commit message hook installed: {commit_msg_hook}")

def main():
    """Main function"""
    print("🔧 Setting up technical debt prevention hooks...")
    
    try:
        setup_pre_commit_hook()
        setup_commit_msg_hook()
        
        print("\n🎉 Pre-commit hooks setup complete!")
        print("\n📋 What was installed:")
        print("  • Pre-commit hook: Validates technical debt before commits")
        print("  • Commit message hook: Ensures proper commit message format")
        print("\n💡 To test manually:")
        print("  python scripts/technical_debt_prevention.py --mode=validate")
        
    except Exception as e:
        print(f"❌ Error setting up hooks: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 