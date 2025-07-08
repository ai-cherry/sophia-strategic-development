#!/usr/bin/env python3
"""
Fix Secret Management System Script
Comprehensive infrastructure fixes for Sophia AI secret management
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class SecretManagementFixer:
    def __init__(self, workspace_root: str = "/Users/lynnmusil/sophia-main"):
        self.workspace_root = Path(workspace_root)
        self.fixes_applied = []
        self.errors_found = []
        self.pulumi_installed = False

    def check_pulumi_cli(self) -> bool:
        """Check if Pulumi CLI is installed"""
        try:
            result = subprocess.run(
                ["pulumi", "version"], capture_output=True, text=True
            )
            if result.returncode == 0:
                self.fixes_applied.append(
                    f"Pulumi CLI already installed: {result.stdout.strip()}"
                )
                return True
        except FileNotFoundError:
            pass
        return False

    def install_pulumi_cli(self) -> bool:
        """Install Pulumi CLI"""
        try:
            # Download and install Pulumi
            install_cmd = "curl -fsSL https://get.pulumi.com | sh"
            result = subprocess.run(
                install_cmd, shell=True, capture_output=True, text=True
            )

            if result.returncode == 0:
                # Add to PATH
                home = os.path.expanduser("~")
                pulumi_path = f"{home}/.pulumi/bin"

                # Update PATH for current session
                os.environ["PATH"] = f"{pulumi_path}:{os.environ.get('PATH', '')}"

                # Add to shell configs
                shell_configs = [".bashrc", ".zshrc", ".profile"]
                export_line = f"export PATH=$PATH:{pulumi_path}"

                for config in shell_configs:
                    config_path = Path(home) / config
                    if config_path.exists():
                        with open(config_path) as f:
                            content = f.read()
                        if export_line not in content:
                            with open(config_path, "a") as f:
                                f.write(
                                    "\n# Added by Sophia AI secret management fix\n"
                                )
                                f.write(f"{export_line}\n")

                # Set PULUMI_ORG
                org_line = "export PULUMI_ORG=scoobyjava-org"
                for config in shell_configs:
                    config_path = Path(home) / config
                    if config_path.exists():
                        with open(config_path) as f:
                            content = f.read()
                        if org_line not in content:
                            with open(config_path, "a") as f:
                                f.write(f"{org_line}\n")

                os.environ["PULUMI_ORG"] = "scoobyjava-org"

                self.fixes_applied.append("Pulumi CLI installed successfully")
                self.pulumi_installed = True
                return True
            else:
                self.errors_found.append(f"Failed to install Pulumi: {result.stderr}")
                return False

        except Exception as e:
            self.errors_found.append(f"Error installing Pulumi: {e}")
            return False

    def create_backend_structure(self) -> bool:
        """Create backend directory structure"""
        try:
            backend_dirs = [
                "backend",
                "backend/core",
                "backend/services",
                "backend/agents",
                "backend/integrations",
                "backend/api",
                "backend/middleware",
                "backend/utils",
                "backend/tests",
            ]

            for dir_path in backend_dirs:
                full_path = self.workspace_root / dir_path
                full_path.mkdir(parents=True, exist_ok=True)

                # Create __init__.py
                init_file = full_path / "__init__.py"
                if not init_file.exists():
                    init_file.touch()

            # Create main backend __init__.py with imports
            backend_init = self.workspace_root / "backend" / "__init__.py"
            init_content = '''"""
Sophia AI Backend Package
Centralized backend services with secure secret management
"""

from .core.auto_esc_config import get_config_value, get_snowflake_config
from .core.auto_esc_config import get_integration_config, get_lambda_labs_config

__version__ = "1.0.0"
__all__ = [
    "get_config_value",
    "get_snowflake_config",
    "get_integration_config",
    "get_lambda_labs_config"
]
'''
            with open(backend_init, "w") as f:
                f.write(init_content)

            # Move auto_esc_config.py to backend/core
            source_file = self.workspace_root / "shared" / "auto_esc_config.py"
            dest_file = self.workspace_root / "backend" / "core" / "auto_esc_config.py"

            if source_file.exists() and not dest_file.exists():
                shutil.copy2(source_file, dest_file)
                self.fixes_applied.append("Moved auto_esc_config.py to backend/core")
            elif dest_file.exists():
                self.fixes_applied.append("auto_esc_config.py already in backend/core")

            self.fixes_applied.append("Backend directory structure created")
            return True

        except Exception as e:
            self.errors_found.append(f"Error creating backend structure: {e}")
            return False

    def fix_esc_configuration(self) -> bool:
        """Fix ESC configuration file"""
        try:
            esc_dir = self.workspace_root / "infrastructure" / "esc"
            esc_dir.mkdir(parents=True, exist_ok=True)

            # Create fixed ESC configuration
            esc_config = {
                "values": {
                    "ai_services": {
                        "openai": {"api_key": {"fn::secret": "${OPENAI_API_KEY}"}},
                        "anthropic": {
                            "api_key": {"fn::secret": "${ANTHROPIC_API_KEY}"}
                        },
                        "portkey": {"api_key": {"fn::secret": "${PORTKEY_API_KEY}"}},
                        "openrouter": {
                            "api_key": {"fn::secret": "${OPENROUTER_API_KEY}"}
                        },
                    },
                    "data_infrastructure": {
                        "snowflake": {
                            "account": {"fn::secret": "${SNOWFLAKE_ACCOUNT}"},
                            "user": {"fn::secret": "${SNOWFLAKE_USERNAME}"},
                            "password": {"fn::secret": "${SNOWFLAKE_PASSWORD}"},
                            "warehouse": {"fn::secret": "${SNOWFLAKE_WAREHOUSE}"},
                            "database": {"fn::secret": "${SNOWFLAKE_DATABASE}"},
                            "role": {"fn::secret": "${SNOWFLAKE_ROLE}"},
                        },
                        "pinecone": {
                            "api_key": {"fn::secret": "${PINECONE_API_KEY}"},
                            "environment": {"fn::secret": "${PINECONE_ENVIRONMENT}"},
                        },
                    },
                    "business_intelligence": {
                        "gong": {
                            "access_key": {"fn::secret": "${GONG_ACCESS_KEY}"},
                            "access_key_secret": {
                                "fn::secret": "${GONG_ACCESS_KEY_SECRET}"
                            },
                        },
                        "hubspot": {
                            "access_token": {"fn::secret": "${HUBSPOT_ACCESS_TOKEN}"}
                        },
                        "linear": {"api_key": {"fn::secret": "${LINEAR_API_KEY}"}},
                    },
                    "infrastructure": {
                        "lambda_labs": {
                            "api_key": {"fn::secret": "${LAMBDA_LABS_API_KEY}"},
                            "ssh_key": {"fn::secret": "${LAMBDA_LABS_SSH_PRIVATE_KEY}"},
                        },
                        "docker": {
                            "token": {"fn::secret": "${DOCKER_TOKEN}"},
                            "hub_access_token": {
                                "fn::secret": "${DOCKER_HUB_ACCESS_TOKEN}"
                            },
                        },
                    },
                },
                "environmentVariables": {
                    "OPENAI_API_KEY": "${ai_services.openai.api_key}",
                    "ANTHROPIC_API_KEY": "${ai_services.anthropic.api_key}",
                    "SNOWFLAKE_ACCOUNT": "${data_infrastructure.snowflake.account}",
                    "SNOWFLAKE_USERNAME": "${data_infrastructure.snowflake.user}",
                    "SNOWFLAKE_PASSWORD": "${data_infrastructure.snowflake.password}",
                    "GONG_ACCESS_KEY": "${business_intelligence.gong.access_key}",
                    "HUBSPOT_ACCESS_TOKEN": "${business_intelligence.hubspot.access_token}",
                    "LAMBDA_LABS_API_KEY": "${infrastructure.lambda_labs.api_key}",
                },
            }

            # Convert to YAML format
            import yaml

            esc_file = esc_dir / "sophia-ai-production.yaml"

            # Backup existing file if it exists
            if esc_file.exists():
                backup_file = esc_file.with_suffix(".yaml.backup")
                shutil.copy2(esc_file, backup_file)
                self.fixes_applied.append(
                    f"Backed up existing ESC config to {backup_file}"
                )

            # Write fixed configuration
            with open(esc_file, "w") as f:
                yaml.dump(esc_config, f, default_flow_style=False, sort_keys=False)

            self.fixes_applied.append("Fixed ESC configuration structure")
            return True

        except Exception as e:
            self.errors_found.append(f"Error fixing ESC configuration: {e}")
            return False

    def create_secret_mappings(self) -> bool:
        """Create centralized secret mapping configuration"""
        try:
            mappings_content = '''"""
Centralized secret mapping configuration
Maps GitHub Organization Secrets to internal key names
"""

GITHUB_TO_INTERNAL_MAPPING = {
    # AI Services
    "OPENAI_API_KEY": "openai_api_key",
    "ANTHROPIC_API_KEY": "anthropic_api_key",
    "PORTKEY_API_KEY": "portkey_api_key",
    "OPENROUTER_API_KEY": "openrouter_api_key",
    "MEM0_API_KEY": "mem0_api_key",

    # Data Infrastructure
    "SNOWFLAKE_ACCOUNT": "snowflake_account",
    "SNOWFLAKE_USERNAME": "snowflake_user",
    "SNOWFLAKE_PASSWORD": "snowflake_password",
    "SNOWFLAKE_WAREHOUSE": "snowflake_warehouse",
    "SNOWFLAKE_DATABASE": "snowflake_database",
    "SNOWFLAKE_ROLE": "snowflake_role",
    "PINECONE_API_KEY": "pinecone_api_key",
    "PINECONE_ENVIRONMENT": "pinecone_environment",

    # Business Intelligence
    "GONG_ACCESS_KEY": "gong_access_key",
    "GONG_ACCESS_KEY_SECRET": "gong_access_key_secret",
    "HUBSPOT_ACCESS_TOKEN": "hubspot_access_token",
    "LINEAR_API_KEY": "linear_api_key",
    "NOTION_API_TOKEN": "notion_api_token",

    # Infrastructure
    "LAMBDA_LABS_API_KEY": "lambda_api_key",
    "LAMBDA_IP_ADDRESS": "lambda_ip_address",
    "LAMBDA_SSH_PRIVATE_KEY": "lambda_ssh_private_key",
    "DOCKER_TOKEN": "docker_token",
    "DOCKER_HUB_ACCESS_TOKEN": "docker_hub_access_token",

    # Communication
    "SLACK_BOT_TOKEN": "slack_bot_token",
    "SLACK_APP_TOKEN": "slack_app_token",
    "SLACK_SIGNING_SECRET": "slack_signing_secret",
}

def get_internal_key(github_key: str) -> str:
    """Convert GitHub secret name to internal key name"""
    return GITHUB_TO_INTERNAL_MAPPING.get(github_key, github_key.lower())

def get_github_key(internal_key: str) -> str:
    """Convert internal key name to GitHub secret name"""
    for github_key, internal in GITHUB_TO_INTERNAL_MAPPING.items():
        if internal == internal_key:
            return github_key
    return internal_key.upper()
'''

            mappings_file = (
                self.workspace_root / "backend" / "core" / "secret_mappings.py"
            )
            with open(mappings_file, "w") as f:
                f.write(mappings_content)

            self.fixes_applied.append("Created secret mapping configuration")
            return True

        except Exception as e:
            self.errors_found.append(f"Error creating secret mappings: {e}")
            return False

    def remove_legacy_env_files(self) -> bool:
        """Remove legacy .env files"""
        try:
            env_files = [
                ".env.lambda-labs",
                "infrastructure/.env.sophia",
                ".env",
                ".env.local",
                ".env.production",
            ]

            for env_file in env_files:
                file_path = self.workspace_root / env_file
                if file_path.exists():
                    # Backup first
                    backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
                    shutil.copy2(file_path, backup_path)

                    # Remove file
                    file_path.unlink()
                    self.fixes_applied.append(
                        f"Removed {env_file} (backed up to {backup_path})"
                    )

            # Update .gitignore
            gitignore_path = self.workspace_root / ".gitignore"
            gitignore_lines = [
                "\n# Environment files",
                "*.env",
                "!*.env.example",
                "!*.env.template",
            ]

            if gitignore_path.exists():
                with open(gitignore_path) as f:
                    content = f.read()

                # Add lines if not present
                for line in gitignore_lines:
                    if line.strip() and line not in content:
                        with open(gitignore_path, "a") as f:
                            f.write(f"{line}\n")

            self.fixes_applied.append("Updated .gitignore for environment files")
            return True

        except Exception as e:
            self.errors_found.append(f"Error removing legacy files: {e}")
            return False

    def create_validation_scripts(self) -> bool:
        """Create validation and test scripts"""
        try:
            # Create test script
            test_script_content = '''#!/usr/bin/env python3
"""
Test script for validating secret access after remediation
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from backend.core.auto_esc_config import get_config_value
    from backend.core.service_configs import ai_config, data_config, business_config

    def test_secret_access():
        """Test secret access through centralized configuration"""
        print("🔍 Testing secret access...")

        # Test individual secrets
        tests = [
            ("OpenAI API Key", get_config_value("openai_api_key")),
            ("Anthropic API Key", get_config_value("anthropic_api_key")),
            ("Snowflake Account", get_config_value("snowflake_account")),
            ("Gong Access Key", get_config_value("gong_access_key")),
            ("HubSpot Token", get_config_value("hubspot_access_token")),
        ]

        passed = 0
        total = len(tests)

        for name, value in tests:
            if value and len(str(value)) > 5:
                print(f"✅ {name}: Available")
                passed += 1
            else:
                print(f"❌ {name}: Missing or invalid")

        print(f"\\n📊 Results: {passed}/{total} secrets accessible")

        # Test service configurations
        print("\\n🔍 Testing service configurations...")

        service_tests = [
            ("AI Services", ai_config.validate()),
            ("Data Services", data_config.validate()),
            ("Business Services", business_config.validate()),
        ]

        service_passed = 0
        for name, valid in service_tests:
            if valid:
                print(f"✅ {name}: Valid configuration")
                service_passed += 1
            else:
                print(f"❌ {name}: Invalid configuration")

        print(f"\\n📊 Service Results: {service_passed}/{len(service_tests)} configurations valid")

        return passed == total and service_passed == len(service_tests)

    if __name__ == "__main__":
        success = test_secret_access()
        sys.exit(0 if success else 1)

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure backend directory structure is created and auto_esc_config is available")
    sys.exit(1)
'''

            test_file = self.workspace_root / "scripts" / "test_secret_access.py"
            with open(test_file, "w") as f:
                f.write(test_script_content)
            test_file.chmod(0o755)

            self.fixes_applied.append("Created test validation script")
            return True

        except Exception as e:
            self.errors_found.append(f"Error creating validation scripts: {e}")
            return False

    def apply_all_fixes(self) -> dict[str, bool]:
        """Apply all infrastructure fixes"""

        results = {}

        # 1. Check/Install Pulumi CLI
        if self.check_pulumi_cli():
            results["pulumi_cli"] = True
        else:
            results["pulumi_cli"] = self.install_pulumi_cli()

        # 2. Create backend structure
        results["backend_structure"] = self.create_backend_structure()

        # 3. Fix ESC configuration
        results["esc_config"] = self.fix_esc_configuration()

        # 4. Create secret mappings
        results["secret_mappings"] = self.create_secret_mappings()

        # 5. Remove legacy files
        results["legacy_cleanup"] = self.remove_legacy_env_files()

        # 6. Create validation scripts
        results["validation_scripts"] = self.create_validation_scripts()

        return results

    def generate_report(self, results: dict[str, bool]) -> str:
        """Generate fix report"""
        report = f"""
# Secret Management Infrastructure Fix Report

**Date:** {subprocess.run(['date'], capture_output=True, text=True).stdout.strip()}
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

1. **Apply code fixes**: `python scripts/apply_remediation_fixes.py`
2. **Test secret access**: `python scripts/test_secret_access.py`
3. **Validate system**: `python scripts/validate_secret_system.py`

## Environment Setup

Make sure to reload your shell or run:
```bash
export PATH=$PATH:~/.pulumi/bin
export PULUMI_ORG=scoobyjava-org
```

"""

        return report


def main():
    """Main function"""
    fixer = SecretManagementFixer()

    # Apply all fixes
    results = fixer.apply_all_fixes()

    # Generate report
    report = fixer.generate_report(results)

    # Save report
    report_path = Path("/Users/lynnmusil/sophia-main/SECRET_MANAGEMENT_FIX_REPORT.md")
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
