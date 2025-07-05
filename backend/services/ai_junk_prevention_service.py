"""
AI Junk File Prevention Service
Prevents AI agents from creating unnecessary files and cleans up existing junk
"""

import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from backend.utils.custom_logger import setup_logger

logger = setup_logger("ai_junk_prevention")


class AIJunkPreventionService:
    """Service to prevent and clean up AI-generated junk files"""

    def __init__(self):
        self.forbidden_patterns = {
            # Analysis and report files
            r".*_analysis_report\.md$",
            r".*_comprehensive_report\.md$",
            r".*_implementation_report\.md$",
            r".*_success_report\.md$",
            r".*_status_report\.md$",
            r".*_final_report\.md$",
            # One-time scripts
            r"^scripts/one_time_.*\.py$",
            r"^scripts/temp_.*\.py$",
            r"^scripts/test_.*\.py$",  # Unless in tests/
            r"^scripts/fix_.*\.py$",  # Unless permanent
            # Backup files
            r".*\.backup$",
            r".*\.bak$",
            r".*\.tmp$",
            r".*\.temp$",
            # Duplicate documentation
            r"^docs/.*_PLAN\.md$",
            r"^docs/.*_CHECKLIST\.md$",
            r"^docs/.*_TODO\.md$",
            r"^docs/.*_NOTES\.md$",
        }

        self.allowed_exceptions = {
            # Permanent fix scripts
            "scripts/fix_all_syntax_errors.py",
            "scripts/fix_critical_syntax_errors.py",
            # Important documentation
            "docs/system_handbook/",
            "docs/architecture/",
            # Test files in proper location
            "tests/",
        }

        self.cleanup_rules = {
            "analysis_reports": {
                "pattern": r".*_analysis.*\.md$",
                "max_age_days": 7,
                "keep_latest": 3,
            },
            "one_time_scripts": {
                "pattern": r"^scripts/(one_time|temp|fix)_.*\.py$",
                "max_age_days": 1,
                "keep_latest": 0,
            },
            "backup_files": {
                "pattern": r".*\.(backup|bak|tmp|temp)$",
                "max_age_days": 3,
                "keep_latest": 1,
            },
        }

    def should_prevent_file_creation(
        self, file_path: str
    ) -> tuple[bool, Optional[str]]:
        """Check if a file should be prevented from being created"""
        path = Path(file_path)

        # Check if in allowed exceptions
        for exception in self.allowed_exceptions:
            if str(path).startswith(exception) or str(path) == exception:
                return False, None

        # Check forbidden patterns
        for pattern in self.forbidden_patterns:
            if re.match(pattern, str(path)):
                return True, f"File matches forbidden pattern: {pattern}"

        # Check for duplicate functionality
        if self._is_duplicate_functionality(path):
            return True, "File appears to duplicate existing functionality"

        return False, None

    def _is_duplicate_functionality(self, path: Path) -> bool:
        """Check if file duplicates existing functionality"""
        if path.suffix == ".py" and path.parent == Path("scripts"):
            # Check if similar script already exists
            base_name = path.stem.lower()

            # Remove common prefixes
            for prefix in ["fix_", "check_", "analyze_", "test_", "validate_"]:
                if base_name.startswith(prefix):
                    base_name = base_name[len(prefix) :]

            # Look for similar scripts
            scripts_dir = Path("scripts")
            if scripts_dir.exists():
                for existing in scripts_dir.glob("*.py"):
                    existing_base = existing.stem.lower()
                    for prefix in ["fix_", "check_", "analyze_", "test_", "validate_"]:
                        if existing_base.startswith(prefix):
                            existing_base = existing_base[len(prefix) :]

                    if (
                        base_name == existing_base
                        or base_name in existing_base
                        or existing_base in base_name
                    ):
                        return True

        return False

    async def clean_junk_files(self, dry_run: bool = True) -> dict[str, list[str]]:
        """Clean up junk files based on rules"""
        results = {"deleted": [], "kept": [], "errors": []}

        for category, rule in self.cleanup_rules.items():
            try:
                cleaned = await self._clean_by_rule(rule, dry_run)
                results["deleted"].extend(cleaned["deleted"])
                results["kept"].extend(cleaned["kept"])
            except Exception as e:
                results["errors"].append(f"Error cleaning {category}: {e}")

        # Log results
        logger.info(
            f"Cleanup complete: {len(results['deleted'])} files deleted, {len(results['kept'])} kept"
        )

        return results

    async def _clean_by_rule(self, rule: dict, dry_run: bool) -> dict[str, list[str]]:
        """Clean files based on a specific rule"""
        pattern = rule["pattern"]
        max_age_days = rule["max_age_days"]
        keep_latest = rule["keep_latest"]

        results = {"deleted": [], "kept": []}

        # Find matching files
        matching_files = []
        for root, dirs, files in os.walk("."):
            for file in files:
                file_path = Path(root) / file
                if re.match(pattern, str(file_path)):
                    matching_files.append(file_path)

        # Sort by modification time
        matching_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

        # Keep latest N files
        files_to_keep = matching_files[:keep_latest] if keep_latest > 0 else []

        # Check age and delete
        cutoff_time = datetime.now() - timedelta(days=max_age_days)

        for file_path in matching_files:
            if file_path in files_to_keep:
                results["kept"].append(str(file_path))
                continue

            # Check age
            file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            if file_time < cutoff_time:
                if dry_run:
                    logger.info(f"Would delete: {file_path}")
                else:
                    file_path.unlink()
                    logger.info(f"Deleted: {file_path}")
                results["deleted"].append(str(file_path))
            else:
                results["kept"].append(str(file_path))

        return results

    def get_cleanup_recommendations(self) -> list[str]:
        """Get recommendations for manual cleanup"""
        recommendations = []

        # Check for large directories
        for dir_path in ["docs", "scripts", "backups"]:
            path = Path(dir_path)
            if path.exists():
                file_count = len(list(path.rglob("*")))
                if file_count > 50:
                    recommendations.append(
                        f"Directory '{dir_path}' has {file_count} files - consider organizing"
                    )

        # Check for old analysis files
        analysis_files = list(Path(".").rglob("*analysis*.md"))
        if len(analysis_files) > 10:
            recommendations.append(
                f"Found {len(analysis_files)} analysis files - consider archiving old ones"
            )

        # Check for duplicate scripts
        scripts = list(Path("scripts").glob("*.py")) if Path("scripts").exists() else []
        script_purposes = {}
        for script in scripts:
            base = script.stem.lower()
            for prefix in ["fix_", "check_", "analyze_", "test_"]:
                if base.startswith(prefix):
                    purpose = base[len(prefix) :]
                    if purpose in script_purposes:
                        script_purposes[purpose].append(script)
                    else:
                        script_purposes[purpose] = [script]

        for purpose, scripts in script_purposes.items():
            if len(scripts) > 1:
                recommendations.append(
                    f"Multiple scripts for '{purpose}': {[s.name for s in scripts]}"
                )

        return recommendations

    def create_file_creation_hook(self):
        """Create a hook that can be integrated into file creation workflows"""

        def hook(file_path: str, content: str = "") -> bool:
            """Hook to check if file creation should proceed"""
            should_prevent, reason = self.should_prevent_file_creation(file_path)

            if should_prevent:
                logger.warning(f"Prevented creation of {file_path}: {reason}")

                # Suggest alternative
                alternative = self._suggest_alternative(file_path, content)
                if alternative:
                    logger.info(f"Suggestion: {alternative}")

                return False

            return True

        return hook

    def _suggest_alternative(self, file_path: str, content: str) -> Optional[str]:
        """Suggest alternative to creating a junk file"""
        path = Path(file_path)

        if "_report.md" in file_path:
            return "Add information to existing documentation in docs/system_handbook/"

        if path.parent == Path("scripts") and "fix_" in path.name:
            return "Consider adding functionality to scripts/fix_all_syntax_errors.py"

        if ".backup" in file_path or ".bak" in file_path:
            return "Use git for version control instead of backup files"

        return None

    async def setup_automated_cleanup(self):
        """Setup automated cleanup tasks"""
        # This would integrate with a scheduler like APScheduler
        # For now, just document the approach
        logger.info("Automated cleanup would run:")
        logger.info("- Hourly: Check for forbidden file creation")
        logger.info("- Daily: Clean up old temporary files")
        logger.info("- Weekly: Full junk file cleanup")
        logger.info("- Post-deployment: Remove one-time scripts")

        return {
            "hourly": "check_forbidden_files",
            "daily": "clean_temp_files",
            "weekly": "full_cleanup",
            "post_deployment": "remove_one_time_scripts",
        }


# Singleton instance
junk_prevention_service = AIJunkPreventionService()


# Integration with file operations
def ai_safe_create_file(file_path: str, content: str = "") -> bool:
    """Safe file creation that prevents junk files"""
    hook = junk_prevention_service.create_file_creation_hook()

    if hook(file_path, content):
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        Path(file_path).write_text(content)
        return True

    return False


async def run_cleanup(dry_run: bool = True):
    """Run junk file cleanup"""
    results = await junk_prevention_service.clean_junk_files(dry_run)

    print("\n=== AI Junk File Cleanup Report ===")
    print(f"Files to delete: {len(results['deleted'])}")
    for file in results["deleted"][:10]:  # Show first 10
        print(f"  - {file}")
    if len(results["deleted"]) > 10:
        print(f"  ... and {len(results['deleted']) - 10} more")

    print(f"\nFiles kept: {len(results['kept'])}")

    if results["errors"]:
        print(f"\nErrors: {len(results['errors'])}")
        for error in results["errors"]:
            print(f"  - {error}")

    # Get recommendations
    recommendations = junk_prevention_service.get_cleanup_recommendations()
    if recommendations:
        print("\n=== Cleanup Recommendations ===")
        for rec in recommendations:
            print(f"  - {rec}")

    return results
