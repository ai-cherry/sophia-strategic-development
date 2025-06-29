#!/usr/bin/env python3
"""
Documentation Cleanup Script
Removes obsolete, duplicate, and one-time-use documentation files
"""

import json
import shutil
from datetime import datetime
from pathlib import Path


class DocumentationCleaner:
    """Clean up junk documentation files"""

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.root_path = Path(".")
        self.docs_path = Path("docs")
        self.archive_path = Path("docs_archive")
        self.removed_files = []
        self.moved_files = []
        self.preserved_files = []

    def get_junk_patterns(self) -> dict[str, list[str]]:
        """Define patterns for junk documentation"""
        return {
            "duplicates": [
                "**/AGNO_*_SUMMARY 2.md",
                "**/AGNO_*_SUMMARY 3.md",
                "**/AGNO_*_SUMMARY 4.md",
                "**/ARCHITECTURE_REVIEW_SUMMARY 2.md",
                "**/ARCHITECTURE_REVIEW_SUMMARY 3.md",
                "**/ARCHITECTURE_REVIEW_SUMMARY 4.md",
                "**/ENHANCED_ARCHITECTURE_RECOMMENDATIONS 2.md",
                "**/ENHANCED_ARCHITECTURE_RECOMMENDATIONS 3.md",
                "**/AGNO_SOPHIA_INTEGRATION_STRATEGY 2.md",
                "**/AGNO_SOPHIA_INTEGRATION_STRATEGY 3.md",
                "**/CODEBASE_REVIEW_FINAL_SUMMARY 2.md",
                "**/*-dev 2.txt",
                "**/*-dev 3.txt",
                "**/*-dev 4.txt",
                "**/*-dev 5.txt",
            ],
            "one_time_reports": [
                "CLEANUP_REPORT.md",
                "COMPREHENSIVE_CLEANUP_IMPLEMENTATION.md",
                "GITHUB_ACTIONS_CLEANUP_SUMMARY.md",
                "OPENAI_CODEX_CLEANUP_IMPLEMENTATION.md",
                "PYTHON_SYNTAX_CLEANUP_SUMMARY.md",
                "SOPHIA_AI_PHASE1_SYNTAX_CLEANUP_SUMMARY.md",
                "SOPHIA_AI_SYNTAX_CORRUPTION_HANDOFF.md",
                "TROUBLESHOOTING_REPORT.md",
                "corrupted_files_list.txt",
                "corrupted_files.txt",
                "syntax_error_files.txt",
                "SYNTAX_FIX_CHECKLIST.md",
            ],
            "old_summaries": [
                "*_SUCCESS_SUMMARY.md",
                "*_IMPLEMENTATION_SUMMARY.md",
                "*_INTEGRATION_SUMMARY.md",
                "*_REPORT.md",
                "*_STATUS.md",
                "*_COMPLETE.md",
                "*_COMPLETION.md",
                "*_FIXES.md",
            ],
            "validation_reports": [
                "syntax_validation_report*.json",
                "syntax_validation_report*.txt",
                "current_syntax_validation_report.json",
                "optimization_report.json",
                "type_safety_audit_report.json",
                "validation_report.json",
                "venv_cleanup_report.json",
                "sophia_health_report_*.json",
            ],
            "old_deployment_scripts": [
                "deploy_advanced_sophia_2025.sh",
                "deploy_enhanced_sota_gateway.sh",
                "deploy_intelligent_ai_gateway.sh",
                "deploy_next_phase.sh",
                "deploy_sophia_conversational_interface.sh",
                "deploy_sophia_mcp_gateway.sh",
                "deploy_sophia_ux_ui_dashboard.sh",
                "deploy_sota_ai_gateway.sh",
            ],
            "old_prompts": [
                "CURSOR_AI_COMPREHENSIVE_CLEANUP_PROMPT.md",
                "CURSOR_AI_PHASE2_IMPROVEMENT_PROMPTS.md",
                "OPENAI_CODEX_IMPLEMENTATION_PROMPT.md",
                "OPENAI_CODEX_INTEGRATION_PROMPT.md",
                "CURSOR_AI_SOPHIA_REVIEW_PROMPT.md",
            ],
            "obsolete_strategies": [
                "OPTIMAL_ALIGNMENT_STRATEGY.md",
                "OPTIMAL_MCP_INTEGRATION_STRATEGY.md",
                "COMPLETE_REMEDIATION_STRATEGY_IMPLEMENTATION_GUIDE.md",
                "COMBINED_ANALYSIS_CURSOR_AI_GITHUB_ACTIONS.md",
            ],
        }

    def should_preserve(self, filepath: Path) -> bool:
        """Check if file should be preserved"""
        preserve_keywords = [
            "README",
            "API_DOCUMENTATION",
            "DEPLOYMENT_GUIDE",
            "ARCHITECTURE",
            "SECURITY",
            "SECRET_MANAGEMENT",
            "MCP_AGENT",
            "INFRASTRUCTURE",
            "quickstart",
            "guide",
        ]

        filename = filepath.name.upper()
        return any(keyword in filename for keyword in preserve_keywords)

    def find_files_to_remove(self) -> list[Path]:
        """Find all files matching junk patterns"""
        files_to_remove = []
        patterns = self.get_junk_patterns()

        for _category, pattern_list in patterns.items():
            for pattern in pattern_list:
                # Handle root directory patterns
                if not pattern.startswith("**/"):
                    matches = list(self.root_path.glob(pattern))
                else:
                    # Remove **/ prefix for proper globbing
                    clean_pattern = pattern[3:]
                    matches = list(self.root_path.glob(f"**/{clean_pattern}"))

                for match in matches:
                    if match.is_file() and not self.should_preserve(match):
                        files_to_remove.append(match)

        # Remove duplicates
        return list(set(files_to_remove))

    def create_archive(self):
        """Create archive directory for removed files"""
        if not self.dry_run:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.archive_path = Path(f"docs_archive_{timestamp}")
            self.archive_path.mkdir(exist_ok=True)

    def archive_file(self, filepath: Path) -> Path:
        """Archive a file before removal"""
        if self.dry_run:
            return filepath

        relative_path = filepath.relative_to(self.root_path)
        archive_file_path = self.archive_path / relative_path
        archive_file_path.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(filepath, archive_file_path)
        return archive_file_path

    def remove_file(self, filepath: Path):
        """Remove or archive a file"""
        try:
            if self.dry_run:
                print(f"[DRY RUN] Would remove: {filepath}")
            else:
                # Archive first
                archived = self.archive_file(filepath)
                # Then remove
                filepath.unlink()
                print(f"✓ Removed: {filepath} (archived to {archived})")

            self.removed_files.append(str(filepath))
        except Exception as e:
            print(f"✗ Failed to remove {filepath}: {e}")

    def reorganize_docs(self):
        """Move scattered docs to proper locations"""
        root_docs = [
            "LOCAL_DEVELOPMENT_GUIDE.md",
            "DEVELOPMENT_ENVIRONMENT_SETUP.md",
            "DEPLOYMENT_CONFIGURATION_GUIDE.md",
            "GITHUB_PR_TEMPLATE.md",
            "QUICK_START_SYNTAX_FIX.md",
            "MCP_SERVICE_INTEGRATION_MAPPING.md",
            "SERVICE_INTEGRATION_OPTIMIZATION_REPORT.md",
            "SOPHIA_AI_BEST_PRACTICES_GUIDE.md",
            "SOPHIA_AI_PROJECT_SUMMARY.md",
        ]

        for doc in root_docs:
            source = self.root_path / doc
            if source.exists():
                # Determine target directory
                if "DEVELOPMENT" in doc or "SETUP" in doc:
                    target_dir = self.docs_path / "getting-started"
                elif "DEPLOYMENT" in doc:
                    target_dir = self.docs_path / "deployment"
                elif "INTEGRATION" in doc or "MCP" in doc:
                    target_dir = self.docs_path / "integrations"
                else:
                    target_dir = self.docs_path

                if not self.dry_run:
                    target_dir.mkdir(parents=True, exist_ok=True)
                    target = target_dir / doc
                    shutil.move(str(source), str(target))
                    print(f"✓ Moved {doc} to {target_dir}")
                else:
                    print(f"[DRY RUN] Would move {doc} to {target_dir}")

                self.moved_files.append((str(source), str(target_dir)))

    def generate_cleanup_log(self):
        """Generate a log of all changes"""
        log = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": self.dry_run,
            "removed_files": self.removed_files,
            "moved_files": self.moved_files,
            "preserved_files": self.preserved_files,
            "archive_location": str(self.archive_path) if not self.dry_run else None,
        }

        log_path = "documentation_cleanup_log.json"
        with open(log_path, "w") as f:
            json.dump(log, f, indent=2)

        print(f"\n✓ Cleanup log saved to {log_path}")

    def run(self):
        """Execute the cleanup process"""
        print("=== Sophia AI Documentation Cleanup ===")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}\n")

        # Create archive if not dry run
        if not self.dry_run:
            self.create_archive()

        # Find and remove junk files
        print("Finding junk documentation...")
        files_to_remove = self.find_files_to_remove()

        print(f"\nFound {len(files_to_remove)} files to remove:")
        for filepath in sorted(files_to_remove):
            self.remove_file(filepath)

        # Reorganize remaining docs
        print("\nReorganizing documentation...")
        self.reorganize_docs()

        # Generate cleanup log
        self.generate_cleanup_log()

        # Summary
        print("\n=== Summary ===")
        print(f"Files removed: {len(self.removed_files)}")
        print(f"Files moved: {len(self.moved_files)}")
        if not self.dry_run:
            print(f"Archive location: {self.archive_path}")

        if self.dry_run:
            print("\nRun without --dry-run to actually perform cleanup")


def main():
    """Main function"""
    import sys

    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv

    cleaner = DocumentationCleaner(dry_run=dry_run)
    cleaner.run()


if __name__ == "__main__":
    main()
