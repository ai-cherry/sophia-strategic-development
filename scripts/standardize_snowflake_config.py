#!/usr/bin/env python3
"""
Standardize Snowflake Configuration for Sophia AI Platform
This script identifies and fixes Snowflake configuration inconsistencies
"""

import json
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SnowflakeConfigStandardizer:
    def __init__(self):
        # The SINGLE source of truth for Snowflake configuration
        self.standard_config = {
            "account": "ZNB04675.us-east-1",  # Primary account
            "user": "SCOOBYJAVA15",
            "database": "SOPHIA_AI",
            "warehouse": "SOPHIA_AI_WH",
            "role": "SOPHIA_AI_PROD_ROLE",
            "schema": "PUBLIC",
            "auth_method": "PAT",  # Personal Access Token
        }

        # Known variations to fix
        self.account_variations = {
            "UHDECNO-CVB64222": self.standard_config["account"],
            "scoobyjava-vw02766": self.standard_config["account"],
            "ZNB04675": self.standard_config["account"],  # Missing region
        }

        self.user_variations = {
            "PROGRAMMATIC_SERVICE_USER": self.standard_config["user"],
            "scoobyjava15": self.standard_config["user"],  # Lowercase
        }

        self.database_variations = {
            "SOPHIA_AI_PROD": self.standard_config["database"],
            "SOPHIA_AI_DEV": self.standard_config["database"],
        }

        self.warehouse_variations = {
            "COMPUTE_WH": self.standard_config["warehouse"],
            "AI_COMPUTE_WH": self.standard_config["warehouse"],
        }

        # Files to check and fix
        self.config_files = [
            "backend/core/auto_esc_config.py",
            "backend/core/aligned_snowflake_config.py",
            "backend/core/config.py",
            "backend/utils/snowflake_connector.py",
            "backend/utils/snowflake_cortex_service.py",
            "backend/services/snowflake_service.py",
            "infrastructure/esc/sophia-ai-production.yaml",
            "config/services/snowflake.yaml",
        ]

        self.findings = []

    def scan_file(self, file_path: Path) -> list[dict]:
        """Scan a file for Snowflake configuration issues"""
        if not file_path.exists():
            return []

        issues = []
        with open(file_path) as f:
            content = f.read()
            lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            # Check for account variations
            for variation, standard in self.account_variations.items():
                if variation in line and variation != standard:
                    issues.append(
                        {
                            "file": str(file_path),
                            "line": i,
                            "type": "account",
                            "found": variation,
                            "should_be": standard,
                            "content": line.strip(),
                        }
                    )

            # Check for user variations
            for variation, standard in self.user_variations.items():
                if variation in line:
                    issues.append(
                        {
                            "file": str(file_path),
                            "line": i,
                            "type": "user",
                            "found": variation,
                            "should_be": standard,
                            "content": line.strip(),
                        }
                    )

            # Check for database variations
            for variation, standard in self.database_variations.items():
                if variation in line and variation != standard:
                    issues.append(
                        {
                            "file": str(file_path),
                            "line": i,
                            "type": "database",
                            "found": variation,
                            "should_be": standard,
                            "content": line.strip(),
                        }
                    )

            # Check for warehouse variations
            for variation, standard in self.warehouse_variations.items():
                if variation in line and variation != standard:
                    issues.append(
                        {
                            "file": str(file_path),
                            "line": i,
                            "type": "warehouse",
                            "found": variation,
                            "should_be": standard,
                            "content": line.strip(),
                        }
                    )

        return issues

    def fix_file(self, file_path: Path, issues: list[dict]) -> bool:
        """Fix Snowflake configuration issues in a file"""
        if not issues:
            return True

        try:
            with open(file_path) as f:
                content = f.read()

            # Apply fixes
            for issue in issues:
                content = content.replace(issue["found"], issue["should_be"])

            # Write back
            with open(file_path, "w") as f:
                f.write(content)

            logger.info(f"✅ Fixed {len(issues)} issues in {file_path}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to fix {file_path}: {e}")
            return False

    def create_standard_config_file(self):
        """Create a standard Snowflake configuration file"""
        config_content = f'''"""
Snowflake Configuration - SINGLE SOURCE OF TRUTH
Generated by standardize_snowflake_config.py
DO NOT MODIFY - This is the authoritative configuration
"""

SNOWFLAKE_CONFIG = {{
    "account": "{self.standard_config['account']}",
    "user": "{self.standard_config['user']}",
    "database": "{self.standard_config['database']}",
    "warehouse": "{self.standard_config['warehouse']}",
    "role": "{self.standard_config['role']}",
    "schema": "{self.standard_config['schema']}",
    "auth_method": "{self.standard_config['auth_method']}",
}}

# Environment-specific overrides (if needed)
SNOWFLAKE_ENV_CONFIG = {{
    "production": {{
        "database": "{self.standard_config['database']}",
        "warehouse": "{self.standard_config['warehouse']}",
        "role": "{self.standard_config['role']}",
    }},
    "staging": {{
        "database": "{self.standard_config['database']}_STAGING",
        "warehouse": "{self.standard_config['warehouse']}_STAGING",
        "role": "{self.standard_config['role']}_STAGING",
    }},
    "development": {{
        "database": "{self.standard_config['database']}_DEV",
        "warehouse": "{self.standard_config['warehouse']}_DEV",
        "role": "{self.standard_config['role']}_DEV",
    }}
}}

def get_snowflake_config(environment: str = "production") -> dict:
    """Get Snowflake configuration for the specified environment"""
    config = SNOWFLAKE_CONFIG.copy()

    if environment in SNOWFLAKE_ENV_CONFIG:
        config.update(SNOWFLAKE_ENV_CONFIG[environment])

    return config
'''

        config_path = Path("backend/core/snowflake_standard_config.py")
        with open(config_path, "w") as f:
            f.write(config_content)

        logger.info(f"✅ Created standard config file: {config_path}")

    def scan_all_python_files(self) -> list[dict]:
        """Scan all Python files for Snowflake configuration issues"""
        all_issues = []

        # Scan backend directory
        backend_path = Path("backend")
        for py_file in backend_path.rglob("*.py"):
            issues = self.scan_file(py_file)
            if issues:
                all_issues.extend(issues)

        # Scan config files
        for config_file in ["*.yaml", "*.yml", "*.json"]:
            for file_path in Path(".").rglob(config_file):
                if "node_modules" not in str(file_path) and ".git" not in str(
                    file_path
                ):
                    issues = self.scan_file(file_path)
                    if issues:
                        all_issues.extend(issues)

        return all_issues

    def generate_report(self, all_issues: list[dict], fixed_files: list[str]):
        """Generate a comprehensive report"""
        report = {
            "standard_configuration": self.standard_config,
            "total_issues": len(all_issues),
            "issues_by_type": {},
            "issues_by_file": {},
            "fixed_files": fixed_files,
            "recommendations": [],
        }

        # Group by type
        for issue in all_issues:
            issue_type = issue["type"]
            if issue_type not in report["issues_by_type"]:
                report["issues_by_type"][issue_type] = []
            report["issues_by_type"][issue_type].append(issue)

        # Group by file
        for issue in all_issues:
            file_name = issue["file"]
            if file_name not in report["issues_by_file"]:
                report["issues_by_file"][file_name] = []
            report["issues_by_file"][file_name].append(issue)

        # Add recommendations
        if all_issues:
            report["recommendations"].append(
                "Update all Snowflake references to use standard configuration"
            )
            report["recommendations"].append(
                "Use backend/core/snowflake_standard_config.py as single source"
            )

        # Save report
        with open("snowflake_standardization_report.json", "w") as f:
            json.dump(report, f, indent=2)

        # Print summary
        logger.info("\n📊 Snowflake Configuration Report:")
        logger.info(f"Standard Account: {self.standard_config['account']}")
        logger.info(f"Standard User: {self.standard_config['user']}")
        logger.info(f"Standard Database: {self.standard_config['database']}")
        logger.info(f"Standard Warehouse: {self.standard_config['warehouse']}")
        logger.info(f"\nTotal Issues Found: {len(all_issues)}")

        for issue_type, issues in report["issues_by_type"].items():
            logger.info(f"  {issue_type}: {len(issues)} issues")

        return report

    def run(self, fix=False):
        """Run the Snowflake configuration standardizer"""
        logger.info("🚀 Snowflake Configuration Standardizer")
        logger.info("=" * 60)

        # Create standard config file
        self.create_standard_config_file()

        # Scan for issues
        logger.info("\n🔍 Scanning for configuration issues...")
        all_issues = self.scan_all_python_files()

        # Fix issues if requested
        fixed_files = []
        if fix and all_issues:
            logger.info("\n🔧 Fixing configuration issues...")

            # Group issues by file
            issues_by_file = {}
            for issue in all_issues:
                file_path = issue["file"]
                if file_path not in issues_by_file:
                    issues_by_file[file_path] = []
                issues_by_file[file_path].append(issue)

            # Fix each file
            for file_path, issues in issues_by_file.items():
                if self.fix_file(Path(file_path), issues):
                    fixed_files.append(file_path)

        # Generate report
        self.generate_report(all_issues, fixed_files)

        if not all_issues:
            logger.info("\n✅ No Snowflake configuration issues found!")
        else:
            logger.info(f"\n⚠️  Found {len(all_issues)} configuration issues")
            if not fix:
                logger.info("Run with --fix flag to automatically fix issues")

        return len(all_issues) == 0


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Standardize Snowflake configuration")
    parser.add_argument("--fix", action="store_true", help="Fix issues automatically")
    args = parser.parse_args()

    standardizer = SnowflakeConfigStandardizer()
    success = standardizer.run(fix=args.fix)
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
