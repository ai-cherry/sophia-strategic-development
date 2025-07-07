#!/usr/bin/env python3
"""
Dead Code Cleanup Script for Sophia AI
Safely removes identified dead code files with backup and logging
"""

import argparse
import json
import logging
import os
import shutil
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("dead_code_cleanup.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class DeadCodeCleaner:
    """Handles safe removal of dead code files"""

    def __init__(self, report_file="codebase_audit_report.json", dry_run=False):
        self.report_file = report_file
        self.dry_run = dry_run
        self.backup_dir = None
        self.dead_files = []
        self.categories = defaultdict(list)

    def load_report(self):
        """Load the dead code audit report"""
        try:
            with open(self.report_file) as f:
                data = json.load(f)
                self.dead_files = data.get("dead_code", [])
                logger.info(
                    f"Loaded {len(self.dead_files)} dead code files from report"
                )
                return True
        except Exception as e:
            logger.error(f"Failed to load report: {e}")
            return False

    def categorize_files(self):
        """Categorize dead code files by type"""
        for f in self.dead_files:
            if "fix_" in f or "final_" in f or "patch_" in f:
                self.categories["Fix/Patch Scripts"].append(f)
            elif "test_" in f:
                self.categories["Test Files"].append(f)
            elif "example_" in f or "demo_" in f:
                self.categories["Example/Demo Files"].append(f)
            elif "implement_" in f or "deploy_" in f:
                self.categories["Implementation/Deploy Scripts"].append(f)
            elif "startup" in f or "start_" in f:
                self.categories["Startup Scripts"].append(f)
            elif "backup" in f or "old" in f or "deprecated" in f:
                self.categories["Backup/Old Files"].append(f)
            elif "integration" in f:
                self.categories["Integration Scripts"].append(f)
            elif "analysis" in f or "audit" in f or "diagnostic" in f:
                self.categories["Analysis/Diagnostic Scripts"].append(f)
            elif "setup_" in f or "configure_" in f:
                self.categories["Setup/Configuration Scripts"].append(f)
            elif "validate_" in f or "verify_" in f or "check_" in f:
                self.categories["Validation/Verification Scripts"].append(f)
            else:
                self.categories["Other"].append(f)

    def create_backup_dir(self):
        """Create timestamped backup directory"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = Path(f"dead_code_backup_{timestamp}")
        if not self.dry_run:
            self.backup_dir.mkdir(exist_ok=True)
            logger.info(f"Created backup directory: {self.backup_dir}")

    def show_summary(self):
        """Display summary of files to be removed"""
        print("\n" + "=" * 60)
        print("DEAD CODE CLEANUP SUMMARY")
        print("=" * 60)
        print(f"Total files identified: {len(self.dead_files)}")
        print(f"Dry run mode: {'ON' if self.dry_run else 'OFF'}")
        if self.backup_dir:
            print(f"Backup directory: {self.backup_dir}")

        print("\nCategories:")
        for cat, files in sorted(self.categories.items(), key=lambda x: -len(x[1])):
            print(f"\n{cat}: {len(files)} files")
            # Show first 3 files in each category
            for f in files[:3]:
                print(f"  - {f}")
            if len(files) > 3:
                print(f"  ... and {len(files) - 3} more")

    def backup_file(self, filepath):
        """Backup a file before deletion"""
        if self.dry_run:
            return True

        try:
            source = Path(filepath)
            if not source.exists():
                logger.warning(f"File not found, skipping: {filepath}")
                return False

            # Create subdirectory structure in backup
            relative_path = source.relative_to(".")
            if self.backup_dir is None:
                logger.error("Backup directory not created")
                return False
            backup_path = self.backup_dir / relative_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)

            # Copy file to backup
            shutil.copy2(source, backup_path)
            logger.debug(f"Backed up: {filepath} -> {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to backup {filepath}: {e}")
            return False

    def remove_file(self, filepath):
        """Remove a single file"""
        try:
            if self.backup_file(filepath):
                if not self.dry_run:
                    Path(filepath).unlink()
                logger.info(
                    f"{'Would remove' if self.dry_run else 'Removed'}: {filepath}"
                )
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to remove {filepath}: {e}")
            return False

    def remove_category(self, category):
        """Remove all files in a category"""
        if category not in self.categories:
            logger.error(f"Unknown category: {category}")
            return 0

        files = self.categories[category]
        removed = 0

        print(f"\nRemoving {len(files)} files from category: {category}")
        for f in files:
            if self.remove_file(f):
                removed += 1

        return removed

    def remove_all(self):
        """Remove all dead code files"""
        removed = 0
        for f in self.dead_files:
            if self.remove_file(f):
                removed += 1
        return removed

    def interactive_cleanup(self):
        """Interactive mode for selective cleanup"""
        print("\nInteractive Cleanup Mode")
        print("Select categories to remove (comma-separated numbers) or 'all':")

        # Display categories with numbers
        cat_list = sorted(self.categories.items(), key=lambda x: -len(x[1]))
        for i, (cat, files) in enumerate(cat_list, 1):
            print(f"{i}. {cat} ({len(files)} files)")

        choice = input("\nYour choice: ").strip().lower()

        if choice == "all":
            confirm = input(f"\nRemove ALL {len(self.dead_files)} files? (yes/no): ")
            if confirm.lower() == "yes":
                return self.remove_all()
        else:
            try:
                indices = [int(x.strip()) - 1 for x in choice.split(",")]
                total_removed = 0
                for idx in indices:
                    if 0 <= idx < len(cat_list):
                        category = cat_list[idx][0]
                        total_removed += self.remove_category(category)
                return total_removed
            except ValueError:
                logger.error("Invalid input")
                return 0

        return 0

    def generate_report(self, removed_count):
        """Generate cleanup report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_identified": len(self.dead_files),
            "total_removed": removed_count,
            "dry_run": self.dry_run,
            "backup_dir": str(self.backup_dir) if self.backup_dir else None,
            "categories": {cat: len(files) for cat, files in self.categories.items()},
        }

        report_file = "dead_code_cleanup_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Cleanup report saved to: {report_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Clean up dead code from Sophia AI codebase"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be removed without actually removing",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Remove all dead code files without prompting",
    )
    parser.add_argument("--category", help="Remove specific category of files")
    parser.add_argument(
        "--report",
        default="codebase_audit_report.json",
        help="Path to audit report file",
    )

    args = parser.parse_args()

    # Initialize cleaner
    cleaner = DeadCodeCleaner(report_file=args.report, dry_run=args.dry_run)

    # Load report
    if not cleaner.load_report():
        return 1

    # Categorize files
    cleaner.categorize_files()

    # Create backup directory
    cleaner.create_backup_dir()

    # Show summary
    cleaner.show_summary()

    # Perform cleanup based on arguments
    if args.all:
        confirm = input(f"\nRemove ALL {len(cleaner.dead_files)} files? (yes/no): ")
        if confirm.lower() == "yes":
            removed = cleaner.remove_all()
        else:
            logger.info("Cleanup cancelled")
            return 0
    elif args.category:
        removed = cleaner.remove_category(args.category)
    else:
        removed = cleaner.interactive_cleanup()

    # Generate report
    cleaner.generate_report(removed)

    print("\nCleanup complete!")
    print(f"Files {'would be' if args.dry_run else ''} removed: {removed}")
    if cleaner.backup_dir and not args.dry_run:
        print(f"Backups saved to: {cleaner.backup_dir}")

    return 0


if __name__ == "__main__":
    exit(main())
