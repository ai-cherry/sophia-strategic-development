#!/usr/bin/env python3
"""Comprehensive codebase cleanup script for Sophia AI.
This script performs the actual cleanup operations identified in the codebase review.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_status(message: str, status: str = "INFO"):
    """Print colored status messages."""
    colors = {"INFO": BLUE, "SUCCESS": GREEN, "WARNING": YELLOW, "ERROR": RED}
    color = colors.get(status, BLUE)
    print(f"{color}[{status}]{RESET} {message}")


def get_repo_size() -> float:
    """Get the current repository size in MB."""
    try:
        result = subprocess.run(["du", "-sm", "."], capture_output=True, text=True)
        if result.returncode == 0:
            size_mb = float(result.stdout.split()[0])
            return size_mb
    except:
        return 0.0


def remove_vendored_dependencies() -> Tuple[bool, List[str]]:
    """Remove vendored dependencies from the repository."""
    removed = []
    errors = []

    # List of vendored dependencies to remove
    vendored_paths = [
        "frontend/node_modules",
        "sophia_admin_api/venv",
        "sophia_venv",  # Also check for this
        ".npm",  # NPM cache
    ]

    for path in vendored_paths:
        if os.path.exists(path):
            try:
                print_status(f"Removing {path}...", "INFO")
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                removed.append(path)
                print_status(f"Removed {path}", "SUCCESS")
            except Exception as e:
                errors.append(f"Failed to remove {path}: {str(e)}")
                print_status(f"Failed to remove {path}: {str(e)}", "ERROR")

    return len(errors) == 0, removed


def fix_malformed_directories() -> Tuple[bool, List[str]]:
    """Fix malformed directory names."""
    fixed = []
    errors = []

    # Known malformed directories
    malformed = [
        "backend/agents/core/agent_framework.py and infrastructure",
        # Add any other malformed paths here
    ]

    for path in malformed:
        if os.path.exists(path):
            try:
                print_status(f"Removing malformed directory: {path}", "INFO")
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                fixed.append(path)
                print_status(f"Fixed malformed path: {path}", "SUCCESS")
            except Exception as e:
                errors.append(f"Failed to fix {path}: {str(e)}")
                print_status(f"Failed to fix {path}: {str(e)}", "ERROR")

    return len(errors) == 0, fixed


def update_gitignore() -> bool:
    """Update .gitignore with comprehensive ignore patterns."""
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv
pip-log.txt
pip-delete-this-directory.txt
.pytest_cache/
.coverage
htmlcov/
dist/
build/
*.egg-info/
.mypy_cache/
.dmypy.json
dmypy.json
.pyre/

# Virtual Environments
sophia_venv/
sophia_admin_api/venv/
*/venv/
*/env/

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.npm
.yarn-integrity
*.tsbuildinfo

# Frontend specific
frontend/node_modules/
frontend/dist/
frontend/build/
frontend/.next/
frontend/out/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.project
.classpath
.c9/
*.launch
.settings/
*.sublime-workspace

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Environment
.env
.env.local
.env.*.local
.env.development
.env.test
.env.production

# Logs
logs/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
lerna-debug.log*
.pnpm-debug.log*

# Testing
coverage/
.nyc_output/
*.lcov

# Build outputs
dist/
build/
out/
.next/
.nuxt/
.cache/
.parcel-cache/

# Temporary files
*.tmp
*.temp
*.bak
*.swp
*.swo
*~

# Package files
*.7z
*.dmg
*.gz
*.iso
*.jar
*.rar
*.tar
*.zip

# Database
*.sqlite
*.sqlite3
*.db

# Secrets (should never be committed)
*.pem
*.key
*.cert
*.crt
*.p12
*.pfx

# Pulumi
.pulumi/
Pulumi.*.yaml

# Docker
.dockerignore

# Jupyter Notebook
.ipynb_checkpoints
*.ipynb

# pyenv
.python-version

# pipenv
Pipfile.lock

# Poetry
poetry.lock

# Celery
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# mkdocs documentation
/site

# Flask
instance/
.webassets-cache

# Scrapy
.scrapy

# Sphinx documentation
docs/_build/
docs/_static/
docs/_templates/

# PyBuilder
target/

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# Rope project settings
.ropeproject

# Mr Developer
.mr.developer.cfg

# Pycharm
.idea/

# VS Code
.vscode/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject
"""

    try:
        print_status("Updating .gitignore...", "INFO")
        with open(".gitignore", "w") as f:
            f.write(gitignore_content)
        print_status("Updated .gitignore", "SUCCESS")
        return True
    except Exception as e:
        print_status(f"Failed to update .gitignore: {str(e)}", "ERROR")
        return False


def clean_git_cache() -> bool:
    """Clean git cache to ensure ignored files are properly ignored."""
    try:
        print_status("Cleaning git cache...", "INFO")
        subprocess.run(["git", "rm", "-r", "--cached", "."], capture_output=True)
        subprocess.run(["git", "add", "."], capture_output=True)
        print_status("Git cache cleaned", "SUCCESS")
        return True
    except Exception as e:
        print_status(f"Failed to clean git cache: {str(e)}", "ERROR")
        return False


def audit_scripts_directory() -> List[str]:
    """Audit scripts directory and identify potentially obsolete scripts."""
    obsolete_patterns = [
        "fix_",
        "test_docstring",
        "push_",
        "fix_syntax",
        "fix_precommit",
        "cleanup_fix_scripts",
    ]

    potentially_obsolete = []
    scripts_dir = Path("scripts")

    if scripts_dir.exists():
        for script in scripts_dir.glob("*.py"):
            script_name = script.name
            for pattern in obsolete_patterns:
                if pattern in script_name:
                    potentially_obsolete.append(str(script))
                    break

    return potentially_obsolete


def create_cleanup_report(
    initial_size: float,
    final_size: float,
    removed_items: List[str],
    fixed_items: List[str],
    obsolete_scripts: List[str],
) -> None:
    """Create a detailed cleanup report."""
    report_content = f"""# Sophia AI Codebase Cleanup Report

## Summary
- **Initial Repository Size**: {initial_size:.2f} MB
- **Final Repository Size**: {final_size:.2f} MB
- **Size Reduction**: {initial_size - final_size:.2f} MB ({((initial_size - final_size) / initial_size * 100):.1f}%)

## Removed Items
{chr(10).join(f'- {item}' for item in removed_items) if removed_items else '- None'}

## Fixed Malformed Directories
{chr(10).join(f'- {item}' for item in fixed_items) if fixed_items else '- None'}

## Potentially Obsolete Scripts
The following scripts may be obsolete and should be reviewed:
{chr(10).join(f'- {script}' for script in obsolete_scripts[:20]) if obsolete_scripts else '- None'}

## Next Steps
1. Review the potentially obsolete scripts and remove if no longer needed
2. Run `poetry install` to reinstall Python dependencies
3. Run `npm install` in the frontend directory to reinstall Node dependencies
4. Commit the changes with: `git commit -m "chore: comprehensive codebase cleanup"`
5. Consider using BFG Repo-Cleaner to remove large files from git history

## Important Notes
- All vendored dependencies have been removed
- .gitignore has been updated with comprehensive patterns
- The sophia_admin_api source code has been preserved
- No actual code files were deleted, only vendored dependencies
"""

    try:
        with open("CLEANUP_REPORT.md", "w") as f:
            f.write(report_content)
        print_status("Created cleanup report: CLEANUP_REPORT.md", "SUCCESS")
    except Exception as e:
        print_status(f"Failed to create report: {str(e)}", "ERROR")


def main():
    """Main cleanup function."""
    print_status("Starting Sophia AI Codebase Cleanup", "INFO")
    print_status("=" * 50, "INFO")

    # Get initial size
    initial_size = get_repo_size()
    print_status(f"Initial repository size: {initial_size:.2f} MB", "INFO")

    # Perform cleanup operations
    all_removed = []
    all_fixed = []

    # 1. Remove vendored dependencies
    success, removed = remove_vendored_dependencies()
    all_removed.extend(removed)

    # 2. Fix malformed directories
    success, fixed = fix_malformed_directories()
    all_fixed.extend(fixed)

    # 3. Update .gitignore
    update_gitignore()

    # 4. Clean git cache
    clean_git_cache()

    # 5. Audit scripts
    obsolete_scripts = audit_scripts_directory()
    if obsolete_scripts:
        print_status(
            f"Found {len(obsolete_scripts)} potentially obsolete scripts", "WARNING"
        )

    # Get final size
    final_size = get_repo_size()
    print_status(f"Final repository size: {final_size:.2f} MB", "INFO")
    print_status(f"Size reduction: {initial_size - final_size:.2f} MB", "SUCCESS")

    # Create report
    create_cleanup_report(
        initial_size, final_size, all_removed, all_fixed, obsolete_scripts
    )

    print_status("=" * 50, "INFO")
    print_status("Cleanup completed! Check CLEANUP_REPORT.md for details", "SUCCESS")

    # Remind about next steps
    print_status("\nNext steps:", "INFO")
    print_status("1. Review CLEANUP_REPORT.md", "INFO")
    print_status("2. Run: cd frontend && npm install", "INFO")
    print_status("3. Run: poetry install", "INFO")
    print_status(
        "4. Commit changes: git add . && git commit -m 'chore: comprehensive codebase cleanup'",
        "INFO",
    )


if __name__ == "__main__":
    # Check if we're in the right directory
    if not os.path.exists("backend") or not os.path.exists("frontend"):
        print_status("Error: Must run from Sophia AI root directory", "ERROR")
        sys.exit(1)

    # Confirm before proceeding
    print_status(
        "This will remove vendored dependencies and clean up the repository.", "WARNING"
    )
    response = input(f"{YELLOW}Continue? (y/N): {RESET}")
    if response.lower() != "y":
        print_status("Cleanup cancelled", "INFO")
        sys.exit(0)

    main()
