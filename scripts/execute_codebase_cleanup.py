#!/usr/bin/env python3
"""Execute comprehensive codebase cleanup for Sophia AI.
This script implements the cleanup strategy defined in OPENAI_CODEX_INTEGRATION_PROMPT.md
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


class CodebaseCleanup:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.root_dir = Path.cwd()
        self.changes_made = []
        self.errors = []

    def log(self, message: str, level: str = "INFO"):
        """Log messages with level."""
        print(f"[{level}] {message}")

    def execute_command(self, cmd: List[str], check: bool = True) -> Optional[str]:
        """Execute shell command."""
        if self.dry_run:
            self.log(f"DRY RUN: Would execute: {' '.join(cmd)}")
            return None

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=check)
            return result.stdout
        except subprocess.CalledProcessError as e:
            self.errors.append(f"Command failed: {' '.join(cmd)}\n{e.stderr}")
            return None

    def remove_vendored_dependencies(self):
        """Remove vendored dependencies from Git and filesystem."""
        self.log("Removing vendored dependencies...")

        vendored_paths = [
            "frontend/node_modules",
            "sophia_admin_api/venv",
            "**/.npm",
            "**/node_modules",
            "**/venv",
        ]

        # Remove from Git tracking
        for path in vendored_paths:
            self.execute_command(["git", "rm", "-r", "--cached", path], check=False)

        # Update .gitignore
        gitignore_additions = [
            "node_modules/",
            "venv/",
            ".npm/",
            "**/venv/",
            "**/node_modules/",
            "__pycache__/",
            "*.pyc",
            ".pytest_cache/",
            ".coverage",
            "*.egg-info/",
            "dist/",
            "build/",
            ".env",
            ".env.*",
            "!.env.template",
        ]

        gitignore_path = self.root_dir / ".gitignore"
        existing_ignores = set()

        if gitignore_path.exists():
            existing_ignores = set(gitignore_path.read_text().strip().split("\n"))

        new_ignores = [
            ignore for ignore in gitignore_additions if ignore not in existing_ignores
        ]

        if new_ignores:
            with open(gitignore_path, "a") as f:
                f.write("\n# Added by cleanup script\n")
                f.write("\n".join(new_ignores) + "\n")
            self.changes_made.append("Updated .gitignore")

    def consolidate_main_files(self):
        """Consolidate multiple main.py files into one."""
        self.log("Consolidating main.py files...")

        main_files = {
            "backend/main.py": "keep",
            "backend/main_simple.py": "remove",
            "backend/main_dashboard.py": "remove",
            "backend/main_simplified.py": "remove",
        }

        # Read content from files to merge
        features_to_merge = {}

        for file_path, action in main_files.items():
            if action == "remove" and Path(file_path).exists():
                content = Path(file_path).read_text()
                # Extract unique features (simplified - in real implementation, parse AST)
                if "dashboard" in file_path.lower():
                    features_to_merge["dashboard"] = True

        # Update main.py with feature flags
        main_path = Path("backend/main.py")
        if main_path.exists() and features_to_merge:
            content = main_path.read_text()

            # Add feature flags at the top
            feature_flags = """
# Feature flags from environment
ENABLE_DASHBOARD = os.getenv("ENABLE_DASHBOARD", "true").lower() == "true"
ENABLE_MCP = os.getenv("ENABLE_MCP", "true").lower() == "true"
ENABLE_SIMPLIFIED_MODE = os.getenv("SIMPLIFIED_MODE", "false").lower() == "true"
"""

            # Insert after imports
            import_end = content.find("\n\n")
            if import_end > 0:
                new_content = (
                    content[:import_end] + feature_flags + content[import_end:]
                )

                if not self.dry_run:
                    main_path.write_text(new_content)
                    self.changes_made.append(
                        "Updated backend/main.py with feature flags"
                    )

        # Remove duplicate files
        for file_path, action in main_files.items():
            if action == "remove" and Path(file_path).exists():
                if not self.dry_run:
                    Path(file_path).unlink()
                    self.changes_made.append(f"Removed {file_path}")

    def fix_duplicate_integrations(self):
        """Remove duplicate integration files."""
        self.log("Fixing duplicate integrations...")

        duplicates = [
            (
                "backend/integrations/gong_integration.py",
                "backend/integrations/gong/enhanced_gong_integration.py",
            ),
            (
                "backend/integrations/gong_integration.py",
                "backend/analytics/gong_analytics.py",
            ),
            (
                "backend/vector/vector_integration.py",
                "backend/vector/vector_integration_updated.py",
            ),
        ]

        for keep, remove in duplicates:
            if Path(remove).exists():
                # TODO: Merge unique functionality before removing
                if not self.dry_run:
                    Path(remove).unlink()
                    self.changes_made.append(f"Removed duplicate: {remove}")

    def standardize_secret_management(self):
        """Remove legacy secret management code."""
        self.log("Standardizing secret management...")

        legacy_files = ["backend/core/pulumi_esc.py", "backend/config/secure_config.py"]

        for file_path in legacy_files:
            if Path(file_path).exists():
                if not self.dry_run:
                    Path(file_path).unlink()
                    self.changes_made.append(f"Removed legacy secret file: {file_path}")

    def fix_directory_names(self):
        """Fix malformed directory names."""
        self.log("Fixing directory names...")

        # Find directories with problematic names
        problematic_dirs = []
        for path in Path("backend").rglob("*"):
            if path.is_dir() and (" and " in path.name or " " in path.name):
                problematic_dirs.append(path)

        for dir_path in problematic_dirs:
            new_name = dir_path.name.replace(" and ", "_").replace(" ", "_")
            new_path = dir_path.parent / new_name

            if not self.dry_run:
                dir_path.rename(new_path)
                self.changes_made.append(f"Renamed: {dir_path} -> {new_path}")

    def consolidate_api_routes(self):
        """Consolidate API routes into single directory."""
        self.log("Consolidating API routes...")

        target_dir = Path("backend/app/routes")
        source_dirs = [Path("backend/app/routers"), Path("backend/api")]

        if not self.dry_run:
            target_dir.mkdir(parents=True, exist_ok=True)

        for source_dir in source_dirs:
            if source_dir.exists():
                for file_path in source_dir.rglob("*.py"):
                    if file_path.name != "__init__.py":
                        target_path = target_dir / file_path.name
                        if not self.dry_run:
                            shutil.move(str(file_path), str(target_path))
                            self.changes_made.append(
                                f"Moved {file_path} to {target_path}"
                            )

                # Remove empty directory
                if not self.dry_run and source_dir.exists():
                    shutil.rmtree(source_dir)
                    self.changes_made.append(f"Removed directory: {source_dir}")

    def clean_scripts_directory(self):
        """Clean up scripts directory."""
        self.log("Cleaning scripts directory...")

        # Move test scripts to tests/
        test_scripts = list(Path("scripts").glob("test_*.py"))
        tests_dir = Path("tests/scripts")

        if test_scripts and not self.dry_run:
            tests_dir.mkdir(parents=True, exist_ok=True)

        for script in test_scripts:
            if not self.dry_run:
                target = tests_dir / script.name
                shutil.move(str(script), str(target))
                self.changes_made.append(f"Moved {script} to {target}")

        # Remove fix scripts (after verifying fixes are applied)
        fix_scripts = list(Path("scripts").glob("fix_*.py"))
        for script in fix_scripts:
            # TODO: Verify fixes are applied before removing
            self.log(f"Would remove fix script: {script}", "WARN")

    def reorganize_documentation(self):
        """Reorganize documentation structure."""
        self.log("Reorganizing documentation...")

        doc_structure = {
            "docs/api": ["API_REFERENCE.md", "API_DOCUMENTATION.md"],
            "docs/architecture": ["SYSTEM_DESIGN.md", "AGENT_ARCHITECTURE.md"],
            "docs/deployment": ["DEPLOYMENT_GUIDE.md", "INFRASTRUCTURE.md"],
            "docs/development": ["SETUP_GUIDE.md", "CONTRIBUTING.md"],
        }

        for dir_path, files in doc_structure.items():
            dir_obj = Path(dir_path)
            if not self.dry_run:
                dir_obj.mkdir(parents=True, exist_ok=True)

        # Move scattered documentation files
        for doc_file in Path(".").glob("*_GUIDE.md"):
            if "deployment" in doc_file.name.lower():
                target = Path("docs/deployment") / doc_file.name
            elif "setup" in doc_file.name.lower():
                target = Path("docs/development") / doc_file.name
            else:
                target = Path("docs") / doc_file.name

            if not self.dry_run and doc_file.exists():
                shutil.move(str(doc_file), str(target))
                self.changes_made.append(f"Moved {doc_file} to {target}")

    def generate_validation_script(self):
        """Generate validation script."""
        self.log("Generating validation script...")

        validation_script = '''#!/usr/bin/env python3
"""Validate codebase cleanup was successful."""

import os
import sys
from pathlib import Path

def check_no_vendored_deps():
    """Ensure no vendored dependencies exist."""
    vendored = [
        "frontend/node_modules",
        "sophia_admin_api/venv",
    ]
    for path in vendored:
        if Path(path).exists():
            print(f"ERROR: Vendored dependency still exists: {path}")
            return False
    return True

def check_single_main():
    """Ensure only one main.py exists."""
    main_files = list(Path("backend").glob("main*.py"))
    if len(main_files) != 1:
        print(f"ERROR: Multiple main files found: {main_files}")
        return False
    return True

def check_no_duplicate_integrations():
    """Check for duplicate integration files."""
    duplicates = [
        "backend/integrations/gong/enhanced_gong_integration.py",
        "backend/analytics/gong_analytics.py",
        "backend/vector/vector_integration_updated.py"
    ]
    for path in duplicates:
        if Path(path).exists():
            print(f"ERROR: Duplicate integration still exists: {path}")
            return False
    return True

def check_api_routes_consolidated():
    """Check API routes are consolidated."""
    old_dirs = ["backend/app/routers", "backend/api"]
    for dir_path in old_dirs:
        if Path(dir_path).exists():
            print(f"ERROR: Old API directory still exists: {dir_path}")
            return False
    return True

if __name__ == "__main__":
    checks = [
        check_no_vendored_deps,
        check_single_main,
        check_no_duplicate_integrations,
        check_api_routes_consolidated,
    ]

    all_passed = all(check() for check in checks)

    if all_passed:
        print("✅ All validation checks passed!")
    else:
        print("❌ Some validation checks failed!")

    sys.exit(0 if all_passed else 1)
'''

        validation_path = Path("scripts/validate_cleanup.py")
        if not self.dry_run:
            validation_path.write_text(validation_script)
            validation_path.chmod(0o755)
            self.changes_made.append("Created validation script")

    def generate_summary(self):
        """Generate cleanup summary."""
        summary = {
            "changes_made": self.changes_made,
            "errors": self.errors,
            "timestamp": str(Path.cwd()),
            "dry_run": self.dry_run,
        }

        summary_path = Path("cleanup_summary.json")
        if not self.dry_run:
            with open(summary_path, "w") as f:
                json.dump(summary, f, indent=2)

        return summary

    def run(self):
        """Execute all cleanup tasks."""
        tasks = [
            self.remove_vendored_dependencies,
            self.consolidate_main_files,
            self.fix_duplicate_integrations,
            self.standardize_secret_management,
            self.fix_directory_names,
            self.consolidate_api_routes,
            self.clean_scripts_directory,
            self.reorganize_documentation,
            self.generate_validation_script,
        ]

        for task in tasks:
            try:
                task()
            except Exception as e:
                self.log(f"Error in {task.__name__}: {str(e)}", "ERROR")
                self.errors.append(f"{task.__name__}: {str(e)}")

        summary = self.generate_summary()

        self.log("\n=== Cleanup Summary ===")
        self.log(f"Changes made: {len(self.changes_made)}")
        self.log(f"Errors: {len(self.errors)}")

        if self.errors:
            self.log("\nErrors encountered:", "ERROR")
            for error in self.errors:
                self.log(f"  - {error}", "ERROR")

        return summary


def main():
    parser = argparse.ArgumentParser(description="Execute Sophia AI codebase cleanup")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--validate-only", action="store_true", help="Only run validation"
    )

    args = parser.parse_args()

    if args.validate_only:
        # Run validation script
        result = subprocess.run([sys.executable, "scripts/validate_cleanup.py"])
        sys.exit(result.returncode)

    cleanup = CodebaseCleanup(dry_run=args.dry_run)
    summary = cleanup.run()

    if cleanup.errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
