#!/usr/bin/env python3
"""
Safe Cleanup Script for Sophia AI
Phase 1B: Remove deprecated code and legacy artifacts with backup
"""

import shutil
import json
import re
from pathlib import Path
from datetime import datetime
import argparse


class SafeCleanup:
    """Safe cleanup with backup and stakeholder approval"""

    def __init__(self, dry_run: bool = True, backup: bool = True):
        self.dry_run = dry_run
        self.backup = backup
        self.root_path = Path(".")
        self.cleanup_targets = []
        self.approval_required = []
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = f"cleanup_backup_{self.timestamp}"

    def identify_cleanup_targets(self):
        """Identify files and directories for cleanup"""

        # Legacy patterns to remove
        legacy_patterns = {
            "retool": r"retool|RETOOL",
            "jump": r"jump|JUMP",
            "deprecated": r"DEPRECATED|UNUSED|OLD|LEGACY",
            "temp": r"\.tmp$|\.temp$|_temp\.|temp_",
            "backup": r"\.bak$|\.backup$|_backup\.|backup_",
        }

        # Scan for cleanup targets
        for file_path in self.root_path.rglob("*"):
            if any(
                skip in str(file_path)
                for skip in [".git", ".venv", "node_modules", self.backup_dir]
            ):
                continue

            # Check file name patterns
            file_name = file_path.name
            for pattern_type, pattern in legacy_patterns.items():
                if re.search(pattern, file_name, re.IGNORECASE):
                    self.cleanup_targets.append(
                        {
                            "path": file_path,
                            "type": pattern_type,
                            "reason": f"Matches {pattern_type} pattern",
                        }
                    )
                    break

            # Check file content for deprecated markers
            if file_path.is_file() and file_path.suffix in [".py", ".js", ".ts", ".md"]:
                try:
                    with open(file_path, "r") as f:
                        content = f.read()
                        if "# DEPRECATED" in content or "// DEPRECATED" in content:
                            self.cleanup_targets.append(
                                {
                                    "path": file_path,
                                    "type": "deprecated",
                                    "reason": "Contains DEPRECATED marker",
                                }
                            )
                except Exception:
                    pass

        # Identify unused MCP servers and agents
        self._identify_unused_agents()

    def _identify_unused_agents(self):
        """Identify potentially unused agents and MCP servers"""
        agent_dirs = [
            self.root_path / "mcp-servers",
            self.root_path / "backend" / "agents",
        ]

        for agent_dir in agent_dirs:
            if not agent_dir.exists():
                continue

            for agent_path in agent_dir.iterdir():
                if agent_path.is_dir():
                    # Check if agent has recent activity
                    last_modified = max(
                        (
                            f.stat().st_mtime
                            for f in agent_path.rglob("*")
                            if f.is_file()
                        ),
                        default=0,
                    )

                    days_old = (datetime.now().timestamp() - last_modified) / (
                        24 * 3600
                    )

                    if days_old > 90:  # Not modified in 90 days
                        self.approval_required.append(
                            {
                                "path": agent_path,
                                "type": "unused_agent",
                                "reason": f"Not modified in {int(days_old)} days",
                                "requires_approval": True,
                            }
                        )

    def create_backup(self):
        """Create backup of files before removal"""
        if not self.backup or self.dry_run:
            return

        backup_path = Path(self.backup_dir)
        backup_path.mkdir(exist_ok=True)

        print(f"\nCreating backup in {self.backup_dir}/")

        for target in self.cleanup_targets + self.approval_required:
            source_path = target["path"]

            # Calculate relative path for backup
            try:
                relative_path = source_path.relative_to(self.root_path)
                dest_path = backup_path / relative_path

                # Create parent directories
                dest_path.parent.mkdir(parents=True, exist_ok=True)

                # Copy file or directory
                if source_path.is_file():
                    shutil.copy2(source_path, dest_path)
                else:
                    shutil.copytree(source_path, dest_path)

                print(f"  Backed up: {relative_path}")
            except Exception as e:
                print(f"  Failed to backup {source_path}: {e}")

    def execute_cleanup(self):
        """Execute the cleanup (or preview in dry-run mode)"""

        print("\n=== Cleanup Targets ===")

        # Auto-cleanup targets
        print("\nAuto-cleanup (no approval needed):")
        for target in self.cleanup_targets:
            path = target["path"]
            print(
                f"  {target['type']}: {path.relative_to(self.root_path)} - {target['reason']}"
            )

            if not self.dry_run:
                try:
                    if path.is_file():
                        path.unlink()
                    else:
                        shutil.rmtree(path)
                    print("    ✓ Removed")
                except Exception as e:
                    print(f"    ✗ Failed: {e}")

        # Approval required targets
        if self.approval_required:
            print("\n\nApproval Required:")
            for target in self.approval_required:
                path = target["path"]
                print(
                    f"  {target['type']}: {path.relative_to(self.root_path)} - {target['reason']}"
                )
                print("    → Requires stakeholder approval before removal")

        if self.dry_run:
            print(
                "\n[DRY RUN] No files were actually removed. Run without --dry-run to execute."
            )

    def generate_cleanup_report(self):
        """Generate a cleanup report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": self.dry_run,
            "backup_created": self.backup and not self.dry_run,
            "backup_location": self.backup_dir if self.backup else None,
            "auto_cleanup": [
                {
                    "path": str(t["path"].relative_to(self.root_path)),
                    "type": t["type"],
                    "reason": t["reason"],
                }
                for t in self.cleanup_targets
            ],
            "approval_required": [
                {
                    "path": str(t["path"].relative_to(self.root_path)),
                    "type": t["type"],
                    "reason": t["reason"],
                }
                for t in self.approval_required
            ],
            "summary": {
                "total_auto_cleanup": len(self.cleanup_targets),
                "total_approval_required": len(self.approval_required),
            },
        }

        report_file = f"cleanup_report_{self.timestamp}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\nCleanup report saved to: {report_file}")
        return report

    def create_approval_checklist(self):
        """Create a checklist for stakeholder approval"""
        if not self.approval_required:
            return

        checklist_file = f"cleanup_approval_checklist_{self.timestamp}.md"

        with open(checklist_file, "w") as f:
            f.write("# Cleanup Approval Checklist\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            f.write("Please review and approve the following items for removal:\n\n")

            for item in self.approval_required:
                path = item["path"].relative_to(self.root_path)
                f.write(f"- [ ] **{path}**\n")
                f.write(f"  - Type: {item['type']}\n")
                f.write(f"  - Reason: {item['reason']}\n")
                f.write("  - Approved by: ____________\n")
                f.write("  - Date: ____________\n\n")

            f.write("\n## Approval Process\n\n")
            f.write("1. Review each item with relevant stakeholders\n")
            f.write("2. Check the box for approved items\n")
            f.write("3. Add approver name and date\n")
            f.write("4. Run cleanup script with --approved-list flag\n")

        print(f"Approval checklist created: {checklist_file}")

    def run(self):
        """Execute the safe cleanup process"""
        print("=== Sophia AI Safe Cleanup ===\n")

        # Step 1: Identify targets
        print("1. Identifying cleanup targets...")
        self.identify_cleanup_targets()
        print(f"   Found {len(self.cleanup_targets)} auto-cleanup targets")
        print(f"   Found {len(self.approval_required)} items requiring approval")

        # Step 2: Create backup
        if self.backup and not self.dry_run:
            print("\n2. Creating backup...")
            self.create_backup()

        # Step 3: Execute cleanup
        print("\n3. Executing cleanup...")
        self.execute_cleanup()

        # Step 4: Generate reports
        print("\n4. Generating reports...")
        self.generate_cleanup_report()
        self.create_approval_checklist()

        # Summary
        print("\n=== Summary ===")
        print(f"Auto-cleanup targets: {len(self.cleanup_targets)}")
        print(f"Approval required: {len(self.approval_required)}")
        if self.backup and not self.dry_run:
            print(f"Backup location: {self.backup_dir}/")


def main():
    """Main function with CLI arguments"""
    parser = argparse.ArgumentParser(description="Safe cleanup for Sophia AI codebase")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Preview cleanup without removing files (default: True)",
    )
    parser.add_argument(
        "--execute", action="store_true", help="Actually execute the cleanup"
    )
    parser.add_argument("--no-backup", action="store_true", help="Skip creating backup")
    parser.add_argument("--approved-list", type=str, help="Path to approved items list")

    args = parser.parse_args()

    # Override dry-run if execute is specified
    dry_run = not args.execute
    backup = not args.no_backup

    cleanup = SafeCleanup(dry_run=dry_run, backup=backup)
    cleanup.run()


if __name__ == "__main__":
    main()
