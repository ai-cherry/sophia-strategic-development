#!/usr/bin/env python3
"""
Enhanced Dead Code Scanner for Sophia AI
Builds on existing AI infrastructure to implement dead code audit recommendations gracefully.

Leverages:
- Existing AI Junk Prevention Service patterns
- AI Code Quality MCP Server capabilities
- Current pre-commit hook infrastructure
- AI Memory System for decision storage
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add backend to path to use existing infrastructure
sys.path.append(str(Path(__file__).parent.parent / "backend"))

try:
    from core.auto_esc_config import get_config_value
    from services.ai_junk_prevention_service import AiJunkPreventionService

    SOPHIA_INFRASTRUCTURE_AVAILABLE = True
except ImportError:
    print("⚠️ Sophia AI infrastructure not available. Running in standalone mode.")
    SOPHIA_INFRASTRUCTURE_AVAILABLE = False


class EnhancedDeadCodeScanner:
    """
    Enhanced dead code scanner implementing audit recommendations.
    Builds on existing Sophia AI automation infrastructure.
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self.scan_results = {
            "timestamp": datetime.now().isoformat(),
            "categories": {},
            "recommendations": [],
            "auto_fixable": [],
            "requires_manual_review": [],
        }

        # Dead code patterns from audit report
        self.dead_code_patterns = {
            "monorepo_artifacts": {
                "pattern": r"^(apps|libs)/(?!README\.md$|\.FUTURE_USE_ONLY$).*",
                "description": "Monorepo transition artifacts",
                "action": "mark_future_use",
                "risk": "low",
            },
            "one_time_reports": {
                "pattern": r".*(_REPORT|_SUMMARY|_PLAN|_STATUS|_COMPLETE|_SUCCESS|_ANALYSIS|_PROMPT)\.md$",
                "description": "One-time reports and temporary documentation",
                "action": "archive_and_delete",
                "risk": "low",
            },
            "deprecated_dockerfiles": {
                "pattern": r"^Dockerfile\.(?!production$).*",
                "description": "Non-production Dockerfiles",
                "action": "archive_non_production",
                "risk": "medium",
            },
            "backup_files": {
                "pattern": r".*\.backup(\.[\d_]+)?$",
                "description": "Backup files from previous operations",
                "action": "cleanup_aged_backups",
                "risk": "low",
            },
            "legacy_fastapi_apps": {
                "pattern": r"backend/app/(?!fastapi_main\.py$|__init__\.py$).*\.py$",
                "description": "Legacy FastAPI application files",
                "action": "verify_unused_then_remove",
                "risk": "high",
            },
        }

        # Initialize existing infrastructure if available
        self.ai_junk_service = None
        if SOPHIA_INFRASTRUCTURE_AVAILABLE:
            try:
                self.ai_junk_service = AiJunkPreventionService()
            except Exception as e:
                print(f"⚠️ Could not initialize AI Junk Prevention Service: {e}")

    def scan_codebase(self) -> dict[str, Any]:
        """
        Comprehensive dead code scan using existing infrastructure patterns.
        """
        print("🔍 Starting Enhanced Dead Code Scan...")
        print(f"📁 Scanning: {self.project_root}")

        for category, config in self.dead_code_patterns.items():
            print(f"\n📊 Scanning category: {category}")
            matches = self._scan_pattern(config["pattern"], config["description"])

            self.scan_results["categories"][category] = {
                "pattern": config["pattern"],
                "description": config["description"],
                "matches": matches,
                "count": len(matches),
                "action": config["action"],
                "risk": config["risk"],
            }

            if matches:
                print(f"   Found {len(matches)} matches")
                self._categorize_recommendations(category, matches, config)
            else:
                print("   ✅ No issues found")

        # Generate summary
        self._generate_summary()
        return self.scan_results

    def _scan_pattern(self, pattern: str, description: str) -> list[str]:
        """Scan for files matching the dead code pattern."""
        matches = []

        try:
            # Use git ls-files for better performance and respect .gitignore
            result = subprocess.run(
                ["git", "ls-files"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                files = result.stdout.strip().split("\n")
                for file_path in files:
                    if file_path and re.match(pattern, file_path):
                        full_path = self.project_root / file_path
                        if full_path.exists():
                            matches.append(file_path)
            else:
                print(f"⚠️ Git command failed: {result.stderr}")

        except Exception as e:
            print(f"⚠️ Error scanning pattern {pattern}: {e}")

        return matches

    def _categorize_recommendations(
        self, category: str, matches: list[str], config: dict[str, Any]
    ):
        """Categorize findings into actionable recommendations."""

        if config["risk"] == "low" and config["action"] in [
            "mark_future_use",
            "archive_and_delete",
        ]:
            # Auto-fixable low risk items
            self.scan_results["auto_fixable"].append(
                {
                    "category": category,
                    "files": matches,
                    "action": config["action"],
                    "description": config["description"],
                }
            )
        else:
            # Items requiring manual review
            self.scan_results["requires_manual_review"].append(
                {
                    "category": category,
                    "files": matches,
                    "action": config["action"],
                    "description": config["description"],
                    "risk": config["risk"],
                }
            )

    def _generate_summary(self):
        """Generate comprehensive summary and recommendations."""
        total_files = sum(
            cat["count"] for cat in self.scan_results["categories"].values()
        )
        auto_fixable_count = sum(
            len(item["files"]) for item in self.scan_results["auto_fixable"]
        )
        manual_review_count = sum(
            len(item["files"]) for item in self.scan_results["requires_manual_review"]
        )

        self.scan_results["summary"] = {
            "total_dead_code_files": total_files,
            "auto_fixable": auto_fixable_count,
            "requires_manual_review": manual_review_count,
            "completion_percentage": round(
                (auto_fixable_count / total_files * 100) if total_files > 0 else 100, 1
            ),
        }

        # Generate specific recommendations
        self._generate_specific_recommendations()

    def _generate_specific_recommendations(self):
        """Generate specific recommendations based on audit findings."""
        recommendations = []

        # Monorepo artifacts recommendation
        monorepo_files = (
            self.scan_results["categories"]
            .get("monorepo_artifacts", {})
            .get("count", 0)
        )
        if monorepo_files > 0:
            recommendations.append(
                {
                    "priority": "high",
                    "action": "Create .FUTURE_USE_ONLY markers in apps/ and libs/ directories",
                    "rationale": "Clearly mark these as reserved for February 2025 monorepo transition",
                    "command": "python scripts/enhanced_dead_code_scanner.py --fix-monorepo-artifacts",
                }
            )

        # One-time reports recommendation
        report_files = (
            self.scan_results["categories"].get("one_time_reports", {}).get("count", 0)
        )
        if report_files > 0:
            recommendations.append(
                {
                    "priority": "medium",
                    "action": f"Archive and cleanup {report_files} temporary report files",
                    "rationale": "These are one-time documents that should be deleted after use",
                    "command": "python scripts/enhanced_dead_code_scanner.py --cleanup-reports",
                }
            )

        # Dockerfile consolidation
        dockerfile_count = (
            self.scan_results["categories"]
            .get("deprecated_dockerfiles", {})
            .get("count", 0)
        )
        if dockerfile_count > 0:
            recommendations.append(
                {
                    "priority": "medium",
                    "action": "Consolidate to single production Dockerfile",
                    "rationale": "Multiple Dockerfiles create confusion and maintenance burden",
                    "command": "python scripts/enhanced_dead_code_scanner.py --consolidate-dockerfiles",
                }
            )

        self.scan_results["recommendations"] = recommendations

    def execute_auto_fixes(self, category: Optional[str] = None) -> dict[str, Any]:
        """
        Execute automatic fixes for low-risk dead code issues.
        Builds on existing AI Junk Prevention Service patterns.
        """
        results = {"fixed": [], "errors": []}

        auto_fixable = self.scan_results.get("auto_fixable", [])
        if category:
            auto_fixable = [
                item for item in auto_fixable if item["category"] == category
            ]

        for item in auto_fixable:
            try:
                if item["action"] == "mark_future_use":
                    self._mark_monorepo_future_use(item["files"])
                    results["fixed"].append(
                        f"Marked {len(item['files'])} monorepo artifacts as future-use"
                    )

                elif item["action"] == "archive_and_delete":
                    archived = self._archive_temporary_files(item["files"])
                    results["fixed"].append(f"Archived {archived} temporary files")

            except Exception as e:
                results["errors"].append(f"Error fixing {item['category']}: {e}")

        return results

    def _mark_monorepo_future_use(self, files: list[str]):
        """Mark monorepo directories with clear future-use indicators."""

        # Create .FUTURE_USE_ONLY marker for apps/
        apps_marker = self.project_root / "apps" / ".FUTURE_USE_ONLY"
        if not apps_marker.exists():
            apps_marker.parent.mkdir(exist_ok=True)
            apps_marker.write_text(
                """# Monorepo Future Structure - DO NOT USE YET

This directory is reserved for monorepo transition (target: February 2025).
Continue using backend/ and frontend/ for all current development.
See docs/monorepo/MONOREPO_TRANSITION_GUIDE.md for timeline.

Created by Enhanced Dead Code Scanner to prevent accidental usage.
"""
            )

        # Create .FUTURE_USE_ONLY marker for libs/
        libs_marker = self.project_root / "libs" / ".FUTURE_USE_ONLY"
        if not libs_marker.exists():
            libs_marker.parent.mkdir(exist_ok=True)
            libs_marker.write_text(
                """# Shared Libraries - DO NOT USE YET

This directory is reserved for monorepo shared libraries.
Current shared code should remain in backend/core/ and backend/utils/.
See docs/monorepo/MONOREPO_TRANSITION_GUIDE.md for migration plan.

Created by Enhanced Dead Code Scanner to prevent accidental usage.
"""
            )

    def _archive_temporary_files(self, files: list[str]) -> int:
        """Archive temporary files before deletion."""
        archived_count = 0
        archive_dir = (
            self.project_root
            / "archive"
            / f"dead_code_cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

        for file_path in files:
            try:
                source = self.project_root / file_path
                if source.exists():
                    # Create archive directory structure
                    target = archive_dir / file_path
                    target.parent.mkdir(parents=True, exist_ok=True)

                    # Move file to archive
                    source.rename(target)
                    archived_count += 1

            except Exception as e:
                print(f"⚠️ Error archiving {file_path}: {e}")

        if archived_count > 0:
            # Create archive manifest
            manifest = archive_dir / "ARCHIVE_MANIFEST.md"
            manifest.write_text(
                f"""# Dead Code Archive Manifest

**Created**: {datetime.now().isoformat()}
**Reason**: Automated cleanup of temporary files and reports
**Files Archived**: {archived_count}

## Files in this archive:
{chr(10).join(f"- {f}" for f in files)}

These files were identified as temporary/one-time files that should be deleted after use.
They have been archived for safety but can likely be permanently deleted.

To restore a file: Copy it back from this archive to its original location.
To permanently delete: Remove this entire archive directory.
"""
            )

        return archived_count

    def generate_report(self, format: str = "markdown") -> str:
        """Generate comprehensive dead code analysis report."""

        if format == "json":
            return json.dumps(self.scan_results, indent=2)

        # Markdown report
        report = f"""# Enhanced Dead Code Analysis Report

**Generated**: {self.scan_results['timestamp']}
**Project**: {self.project_root.name}

## 📊 Summary

- **Total dead code files found**: {self.scan_results['summary']['total_dead_code_files']}
- **Auto-fixable**: {self.scan_results['summary']['auto_fixable']}
- **Requires manual review**: {self.scan_results['summary']['requires_manual_review']}
- **Automation coverage**: {self.scan_results['summary']['completion_percentage']}%

## 🔍 Categories Analyzed

"""

        for category, data in self.scan_results["categories"].items():
            report += f"""### {category.replace('_', ' ').title()}
- **Pattern**: `{data['pattern']}`
- **Description**: {data['description']}
- **Files found**: {data['count']}
- **Risk level**: {data['risk']}
- **Recommended action**: {data['action']}

"""
            if data["matches"]:
                report += "**Files:**\n"
                for file_path in data["matches"][:10]:  # Limit to first 10
                    report += f"- `{file_path}`\n"
                if len(data["matches"]) > 10:
                    report += f"- ... and {len(data['matches']) - 10} more\n"
                report += "\n"

        # Add recommendations
        report += "## 🎯 Recommended Actions\n\n"
        for i, rec in enumerate(self.scan_results["recommendations"], 1):
            report += f"{i}. **{rec['action']}** (Priority: {rec['priority']})\n"
            report += f"   - Rationale: {rec['rationale']}\n"
            report += f"   - Command: `{rec['command']}`\n\n"

        # Add implementation guidance
        report += """## 🚀 Implementation Guidance

### Immediate Actions (Low Risk)
```bash
# Fix monorepo artifacts
python scripts/enhanced_dead_code_scanner.py --fix-monorepo-artifacts

# Cleanup temporary reports
python scripts/enhanced_dead_code_scanner.py --cleanup-reports
```

### Manual Review Required (Medium/High Risk)
- Review Dockerfile consolidation strategy
- Verify FastAPI application unification
- Analyze any deprecated system remnants

### Prevention (Ongoing)
- Enhanced pre-commit hooks will prevent future dead code accumulation
- AI Junk Prevention Service will block creation of identified patterns
- Weekly automated scans will catch new issues early

This report was generated by the Enhanced Dead Code Scanner, building on Sophia AI's existing automation infrastructure for graceful technical debt reduction.
"""

        return report


def main():
    """Main execution function with command-line interface."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Enhanced Dead Code Scanner for Sophia AI"
    )
    parser.add_argument("--scan", action="store_true", help="Perform dead code scan")
    parser.add_argument(
        "--fix-monorepo-artifacts",
        action="store_true",
        help="Fix monorepo transition artifacts",
    )
    parser.add_argument(
        "--cleanup-reports",
        action="store_true",
        help="Cleanup temporary reports and documentation",
    )
    parser.add_argument(
        "--consolidate-dockerfiles",
        action="store_true",
        help="Analyze Dockerfile consolidation opportunities",
    )
    parser.add_argument(
        "--report",
        choices=["markdown", "json"],
        default="markdown",
        help="Report format",
    )
    parser.add_argument("--output", help="Output file (default: stdout)")

    args = parser.parse_args()

    scanner = EnhancedDeadCodeScanner()

    # Always perform scan first
    print("🔍 Enhanced Dead Code Scanner - Building on Sophia AI Infrastructure")
    print("=" * 80)

    results = scanner.scan_codebase()

    # Execute requested fixes
    if args.fix_monorepo_artifacts:
        print("\n🔧 Fixing monorepo artifacts...")
        fix_results = scanner.execute_auto_fixes("monorepo_artifacts")
        print(f"✅ Fixed: {fix_results}")

    if args.cleanup_reports:
        print("\n🧹 Cleaning up temporary reports...")
        fix_results = scanner.execute_auto_fixes("one_time_reports")
        print(f"✅ Cleaned: {fix_results}")

    # Generate and output report
    print(f"\n📋 Generating {args.report} report...")
    report = scanner.generate_report(args.report)

    if args.output:
        with open(args.output, "w") as f:
            f.write(report)
        print(f"📄 Report saved to: {args.output}")
    else:
        print("\n" + "=" * 80)
        print(report)

    # Summary
    summary = results["summary"]
    print("\n🎯 SUMMARY:")
    print(f"   Found {summary['total_dead_code_files']} dead code files")
    print(
        f"   {summary['auto_fixable']} auto-fixable, {summary['requires_manual_review']} need manual review"
    )
    print(f"   {summary['completion_percentage']}% can be automated")

    if summary["total_dead_code_files"] > 0:
        print("\n💡 Next steps:")
        print("   1. Review the report above")
        print("   2. Run auto-fixes for low-risk items")
        print("   3. Manually review medium/high-risk items")
        print("   4. Update pre-commit hooks to prevent future accumulation")


if __name__ == "__main__":
    main()
