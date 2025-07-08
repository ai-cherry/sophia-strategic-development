#!/usr/bin/env python3
"""
Apply Remediation Fixes Script
Implements specific code fixes from the detailed remediation plan
Focuses on replacing direct environment access with centralized configuration
"""

import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Tuple


class RemediationFixer:
    def __init__(self, workspace_root: str = "/Users/lynnmusil/sophia-main"):
        self.workspace_root = Path(workspace_root)
        self.fixes_applied = []
        self.errors_found = []

        # Mapping of os.getenv patterns to auto_esc_config patterns
        self.secret_mappings = {
            # AI Services
            'get_config_value("openai_api_key")': 'get_config_value("openai_api_key")',
            'get_config_value("anthropic_api_key")': 'get_config_value("anthropic_api_key")',
            # Data Infrastructure
            'get_config_value("snowflake_account")': 'get_config_value("snowflake_account")',
            'get_config_value("snowflake_user")': 'get_config_value("snowflake_user")',
            'get_config_value("snowflake_password")': 'get_config_value("snowflake_password")',
            'get_config_value("snowflake_warehouse")': 'get_config_value("snowflake_warehouse")',
            'get_config_value("snowflake_database")': 'get_config_value("snowflake_database")',
            'get_config_value("snowflake_role")': 'get_config_value("snowflake_role")',
            # Business Intelligence
            'get_config_value("gong_access_key")': 'get_config_value("gong_access_key")',
            'get_config_value("gong_access_key_secret")': 'get_config_value("gong_access_key_secret")',
            'get_config_value("hubspot_access_token")': 'get_config_value("hubspot_access_token")',
            'get_config_value("linear_api_key")': 'get_config_value("linear_api_key")',
            'get_config_value("notion_api_token")': 'get_config_value("notion_api_token")',
            # Infrastructure
            'get_config_value("lambda_api_key")': 'get_config_value("lambda_api_key")',
            'get_config_value("lambda_ip_address")': 'get_config_value("lambda_ip_address")',
            'get_config_value("docker_token")': 'get_config_value("docker_token")',
            # Communication
            'get_config_value("slack_bot_token")': 'get_config_value("slack_bot_token")',
            'get_config_value("slack_app_token")': 'get_config_value("slack_app_token")',
            # Data Services
            'get_config_value("estuary_access_token")': 'get_config_value("estuary_access_token")',
            'get_config_value("estuary_refresh_token")': 'get_config_value("estuary_refresh_token")',
            'get_config_value("pinecone_api_key")': 'get_config_value("pinecone_api_key")',
        }

    def find_python_files_with_env_access(self) -> list[Path]:
        """Find Python files that use direct environment access"""
        python_files = []

        # Search in infrastructure directory
        for file_path in self.workspace_root.rglob("*.py"):
            if "backend" in str(file_path) or "__pycache__" in str(file_path):
                continue

            try:
                with open(file_path) as f:
                    content = f.read()
                    if "os.getenv(" in content or "os.environ.get(" in content:
                        python_files.append(file_path)
            except Exception as e:
                self.errors_found.append(f"Error reading {file_path}: {e}")

        return python_files

    def fix_file_env_access(self, file_path: Path) -> bool:
        """Fix direct environment access in a single file"""
        try:
            with open(file_path) as f:
                original_content = f.read()

            modified_content = original_content
            changes_made = 0

            # Add import if needed and env access found
            needs_import = False
            for old_pattern in self.secret_mappings.keys():
                if old_pattern in modified_content:
                    needs_import = True
                    break

            # Add import at the top if needed
            if (
                needs_import
                and "from backend.core.auto_esc_config import get_config_value"
                not in modified_content
            ):
                import_line = (
                    "from backend.core.auto_esc_config import get_config_value\n"
                )

                # Find the best place to add the import
                lines = modified_content.split("\n")
                import_index = 0

                # Skip shebang and docstrings
                for i, line in enumerate(lines):
                    if (
                        line.startswith("#")
                        or line.startswith('"""')
                        or line.startswith("'''")
                    ):
                        continue
                    if line.startswith("import ") or line.startswith("from "):
                        import_index = i
                        break
                    if line.strip():  # First non-empty line
                        import_index = i
                        break

                lines.insert(import_index, import_line.strip())
                modified_content = "\n".join(lines)

            # Apply all secret mappings
            for old_pattern, new_pattern in self.secret_mappings.items():
                if old_pattern in modified_content:
                    modified_content = modified_content.replace(
                        old_pattern, new_pattern
                    )
                    changes_made += 1

            # Handle default values in os.getenv calls
            modified_content = self._fix_env_with_defaults(modified_content)

            # Only write if changes were made
            if modified_content != original_content:
                # Backup original file
                backup_path = file_path.with_suffix(file_path.suffix + ".backup")
                shutil.copy2(file_path, backup_path)

                # Write modified content
                with open(file_path, "w") as f:
                    f.write(modified_content)

                self.fixes_applied.append(
                    f"Fixed {file_path}: {changes_made} replacements"
                )
                return True

            return False

        except Exception as e:
            self.errors_found.append(f"Error fixing {file_path}: {e}")
            return False

    def _fix_env_with_defaults(self, content: str) -> str:
        """Fix os.getenv calls that have default values"""

        # Pattern: get_config_value("key", "default_value")
        pattern = r'os\.getenv\("([^"]+)",\s*"([^"]*)"\)'

        def replace_with_default(match):
            env_key = match.group(1)
            default_value = match.group(2)

            # Map to internal key name
            internal_key = self._get_internal_key_name(env_key)
            return f'get_config_value("{internal_key}", "{default_value}")'

        content = re.sub(pattern, replace_with_default, content)

        # Pattern: get_config_value("key")
        pattern_none = r'os\.getenv\("([^"]+)",\s*None\)'

        def replace_with_none(match):
            env_key = match.group(1)
            internal_key = self._get_internal_key_name(env_key)
            return f'get_config_value("{internal_key}")'

        content = re.sub(pattern_none, replace_with_none, content)

        return content

    def _get_internal_key_name(self, env_key: str) -> str:
        """Convert environment variable name to internal key name"""
        key_mappings = {
            "OPENAI_API_KEY": "openai_api_key",
            "ANTHROPIC_API_KEY": "anthropic_api_key",
            "SNOWFLAKE_ACCOUNT": "snowflake_account",
            "SNOWFLAKE_USER": "snowflake_user",
            "SNOWFLAKE_PASSWORD": "snowflake_password",
            "GONG_ACCESS_KEY": "gong_access_key",
            "HUBSPOT_ACCESS_TOKEN": "hubspot_access_token",
            "LAMBDA_API_KEY": "lambda_api_key",
            "SLACK_BOT_TOKEN": "slack_bot_token",
            "NOTION_API_KEY": "notion_api_token",
            "ESTUARY_ACCESS_TOKEN": "estuary_access_token",
            "PINECONE_API_KEY": "pinecone_api_key",
        }

        return key_mappings.get(env_key, env_key.lower())

    def create_service_config_classes(self) -> bool:
        """Create centralized service configuration classes"""
        try:
            backend_core = self.workspace_root / "backend" / "core"
            backend_core.mkdir(parents=True, exist_ok=True)

            # Create service_configs.py
            service_config_content = '''"""
Centralized service configuration classes
Uses auto_esc_config for secure secret management
"""

from typing import Dict, Optional
from .auto_esc_config import get_config_value

class AIServiceConfig:
    """Configuration for AI services"""

    def __init__(self):
        self.openai_api_key = get_config_value("openai_api_key")
        self.anthropic_api_key = get_config_value("anthropic_api_key")
        self.portkey_api_key = get_config_value("portkey_api_key")
        self.openrouter_api_key = get_config_value("openrouter_api_key")

    def validate(self) -> bool:
        """Validate that required secrets are available"""
        required = [self.openai_api_key, self.anthropic_api_key]
        return all(secret is not None for secret in required)

class DataServiceConfig:
    """Configuration for data services"""

    def __init__(self):
        self.snowflake_account = get_config_value("snowflake_account")
        self.snowflake_user = get_config_value("snowflake_user")
        self.snowflake_password = get_config_value("snowflake_password")
        self.snowflake_warehouse = get_config_value("snowflake_warehouse")
        self.snowflake_database = get_config_value("snowflake_database")
        self.snowflake_role = get_config_value("snowflake_role")
        self.pinecone_api_key = get_config_value("pinecone_api_key")

    def get_snowflake_url(self) -> str:
        """Generate Snowflake connection URL"""
        if not all([self.snowflake_account, self.snowflake_user, self.snowflake_password]):
            raise ValueError("Missing required Snowflake configuration")
        return f"snowflake://{self.snowflake_user}:{self.snowflake_password}@{self.snowflake_account}"

    def validate(self) -> bool:
        """Validate Snowflake configuration"""
        required = [self.snowflake_account, self.snowflake_user, self.snowflake_password]
        return all(config is not None for config in required)

class BusinessServiceConfig:
    """Configuration for business intelligence services"""

    def __init__(self):
        self.gong_access_key = get_config_value("gong_access_key")
        self.gong_access_key_secret = get_config_value("gong_access_key_secret")
        self.hubspot_access_token = get_config_value("hubspot_access_token")
        self.linear_api_key = get_config_value("linear_api_key")
        self.notion_api_token = get_config_value("notion_api_token")

    def validate(self) -> bool:
        """Validate business service configuration"""
        return any([
            self.gong_access_key,
            self.hubspot_access_token,
            self.linear_api_key
        ])

class InfrastructureConfig:
    """Configuration for infrastructure services"""

    def __init__(self):
        self.lambda_api_key = get_config_value("lambda_api_key")
        self.lambda_ip_address = get_config_value("lambda_ip_address")
        self.docker_token = get_config_value("docker_token")
        self.slack_bot_token = get_config_value("slack_bot_token")

# Global configuration instances
ai_config = AIServiceConfig()
data_config = DataServiceConfig()
business_config = BusinessServiceConfig()
infrastructure_config = InfrastructureConfig()
'''

            service_config_file = backend_core / "service_configs.py"
            with open(service_config_file, "w") as f:
                f.write(service_config_content)

            self.fixes_applied.append("Created service configuration classes")
            return True

        except Exception as e:
            self.errors_found.append(f"Error creating service configs: {e}")
            return False

    def apply_all_fixes(self) -> dict[str, bool]:
        """Apply all remediation fixes"""

        results = {}

        # 1. Create service configuration classes
        results["service_configs"] = self.create_service_config_classes()

        # 2. Find and fix Python files with direct env access
        files_to_fix = self.find_python_files_with_env_access()

        # 3. Fix each file
        fixed_files = 0
        for file_path in files_to_fix:
            if self.fix_file_env_access(file_path):
                fixed_files += 1

        results["file_fixes"] = fixed_files > 0

        return results

    def generate_report(self, results: dict[str, bool]) -> str:
        """Generate remediation report"""
        report = f"""
# Remediation Fixes Applied

**Date:** {os.popen('date').read().strip()}
**Status:** {'✅ Success' if all(results.values()) else '⚠️ Partial Success'}

## Results Summary

"""

        for fix_name, success in results.items():
            status = "✅ Success" if success else "❌ Failed"
            report += f"- **{fix_name.replace('_', ' ').title()}**: {status}\n"

        report += """

## Fixes Applied

"""
        for fix in self.fixes_applied:
            report += f"- {fix}\n"

        if self.errors_found:
            report += """

## Errors Found

"""
            for error in self.errors_found:
                report += f"- {error}\n"

        report += """

## Next Steps

1. **Run test script**: `python scripts/test_secret_access.py`
2. **Validate system**: `python scripts/validate_secret_system.py`
3. **Test integrations**: Verify all services work with new configuration
4. **Monitor performance**: Check for any performance impacts

## Manual Actions Still Required

1. **Review backup files**: Check .backup files for any missed patterns
2. **Update documentation**: Update any documentation referencing old patterns
3. **Test MCP servers**: Verify all MCP servers work with new configuration
4. **Remove backups**: Once validated, remove .backup files

"""

        return report


def main():
    """Main function"""
    fixer = RemediationFixer()

    # Apply all fixes
    results = fixer.apply_all_fixes()

    # Generate report
    report = fixer.generate_report(results)

    # Save report
    report_path = Path("/Users/lynnmusil/sophia-main/REMEDIATION_FIXES_APPLIED.md")
    with open(report_path, "w") as f:
        f.write(report)


    # Print summary
    successful_fixes = sum(1 for result in results.values() if result)
    total_fixes = len(results)


    if successful_fixes == total_fixes:
        pass
    else:
        pass

    return 0 if successful_fixes == total_fixes else 1


if __name__ == "__main__":
    exit(main())
