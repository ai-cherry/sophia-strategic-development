#!/usr/bin/env python3
"""
Sophia AI - Enhanced Secret Standardization with Environment-Aware Naming
Implements SOPHIA_{SERVICE}_{TYPE}_{ENV} pattern with advanced Pulumi ESC integration
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class Environment(Enum):
    """Supported deployment environments."""

    PRODUCTION = "PROD"
    STAGING = "STG"
    DEVELOPMENT = "DEV"


class ServiceCategory(Enum):
    """Service categories for organized secret management."""

    PLATFORM = "platform"
    INFRASTRUCTURE = "infrastructure"
    DATA = "data"
    INTEGRATION = "integration"
    AI = "ai"
    COMMUNICATION = "communication"


@dataclass
class SecretMapping:
    """Enhanced secret mapping with environment awareness."""

    old_name: str
    new_name: str
    service: str
    category: ServiceCategory
    environment: Environment
    pulumi_esc_path: str
    description: str
    required: bool = True


@dataclass
class ESCEnvironmentConfig:
    """Pulumi ESC environment configuration."""

    name: str
    environment: Environment
    values_structure: Dict
    imports: List[str]


class EnhancedSecretStandardizer:
    """Advanced secret standardization with environment-specific naming."""

    def __init__(self):
        self.workspace_root = Path.cwd()
        self.current_secrets = self._discover_current_secrets()
        self.secret_mappings: List[SecretMapping] = []
        self.esc_configs: List[ESCEnvironmentConfig] = []

    def _discover_current_secrets(self) -> Set[str]:
        """Discover all current secrets from workflows and code."""
        secrets = set()

        # Scan GitHub Actions workflows
        workflows_dir = self.workspace_root / ".github" / "workflows"
        if workflows_dir.exists():
            for workflow_file in workflows_dir.glob("*.yml"):
                with open(workflow_file, "r") as f:
                    content = f.read()
                    secrets.update(re.findall(r"secrets\.([A-Z_]+)", content))

        # Scan backend code for environment variables
        backend_dir = self.workspace_root / "backend"
        if backend_dir.exists():
            for py_file in backend_dir.rglob("*.py"):
                try:
                    with open(py_file, "r") as f:
                        content = f.read()
                        secrets.update(
                            re.findall(r'os\.getenv\(["\']([A-Z_]+)["\']', content)
                        )
                        secrets.update(
                            re.findall(r'config\.get\(["\']([a-z_]+)["\']', content)
                        )
                except (UnicodeDecodeError, PermissionError):
                    continue

        print(f"🔍 Discovered {len(secrets)} unique secrets")
        return secrets

    def generate_enhanced_secret_mappings(self) -> List[SecretMapping]:
        """Generate enhanced secret mappings with SOPHIA_ prefix and environment awareness."""

        # Define enhanced service mappings

        mappings = []

        for secret in sorted(self.current_secrets):
            # Skip if already follows SOPHIA_ pattern
            if secret.startswith("SOPHIA_"):
                continue

            # Generate mappings for each environment
            for env in Environment:
                service_info = self._extract_service_info(secret)
                if service_info:
                    service, category, credential_type = service_info

                    new_name = f"SOPHIA_{service}_{credential_type}_{env.value}"
                    esc_path = f"values.sophia.{category.value}.{service.lower()}.{credential_type.lower()}"

                    mapping = SecretMapping(
                        old_name=secret,
                        new_name=new_name,
                        service=service,
                        category=category,
                        environment=env,
                        pulumi_esc_path=esc_path,
                        description=f"{service} {credential_type} for {env.value} environment",
                        required=env
                        == Environment.PRODUCTION,  # Only PROD is required initially
                    )
                    mappings.append(mapping)

        self.secret_mappings = mappings
        return mappings

    def _extract_service_info(
        self, secret_name: str
    ) -> Optional[Tuple[str, ServiceCategory, str]]:
        """Extract service, category, and credential type from secret name."""

        service_patterns = {
            # Platform
            ("PULUMI", "GITHUB", "DOCKER"): (ServiceCategory.PLATFORM, "TOKEN"),
            # Infrastructure
            ("VERCEL", "NAMECHEAP", "LAMBDA"): (
                ServiceCategory.INFRASTRUCTURE,
                "TOKEN",
            ),
            # Data
            ("SNOWFLAKE", "PINECONE", "WEAVIATE"): (ServiceCategory.DATA, "PASSWORD"),
            # Integration
            ("LINEAR", "ASANA", "GONG", "APOLLO", "HUBSPOT"): (
                ServiceCategory.INTEGRATION,
                "API_KEY",
            ),
            # AI
            ("OPENAI", "ANTHROPIC", "PORTKEY"): (ServiceCategory.AI, "API_KEY"),
            # Communication
            ("SLACK", "DISCORD"): (ServiceCategory.COMMUNICATION, "BOT_TOKEN"),
        }

        secret_upper = secret_name.upper()

        for services, (category, default_type) in service_patterns.items():
            for service in services:
                if service in secret_upper:
                    # Determine credential type
                    if "PASSWORD" in secret_upper or "PAT" in secret_upper:
                        cred_type = "PASSWORD"
                    elif "SECRET" in secret_upper:
                        cred_type = "CLIENT_SECRET"
                    elif "KEY" in secret_upper:
                        cred_type = "API_KEY"
                    elif "TOKEN" in secret_upper:
                        cred_type = "TOKEN"
                    else:
                        cred_type = default_type

                    return service, category, cred_type

        return None

    def generate_esc_environments(self) -> List[ESCEnvironmentConfig]:
        """Generate Pulumi ESC environment configurations."""

        esc_configs = []

        for env in Environment:
            # Group mappings by category for this environment
            env_mappings = [m for m in self.secret_mappings if m.environment == env]

            values_structure = {
                "sophia": {
                    "platform": {
                        "name": "sophia-ai-platform",
                        "version": "v2.0.0",
                        "environment": env.value.lower(),
                    }
                }
            }

            # Build nested structure by category
            for mapping in env_mappings:
                category_key = mapping.category.value
                service_key = mapping.service.lower()
                cred_key = mapping.pulumi_esc_path.split(".")[-1]

                if category_key not in values_structure["sophia"]:
                    values_structure["sophia"][category_key] = {}

                if service_key not in values_structure["sophia"][category_key]:
                    values_structure["sophia"][category_key][service_key] = {}

                values_structure["sophia"][category_key][service_key][cred_key] = (
                    f"${{{mapping.new_name}}}"
                )

            esc_config = ESCEnvironmentConfig(
                name=f"scoobyjava-org/sophia-ai-{env.value.lower()}",
                environment=env,
                values_structure=values_structure,
                imports=["scoobyjava-org/default/common"],  # Common configuration
            )

            esc_configs.append(esc_config)

        self.esc_configs = esc_configs
        return esc_configs

    def create_migration_scripts(self) -> Dict[str, str]:
        """Create migration scripts for different phases."""

        scripts = {}

        # Phase 1: Critical production secrets
        critical_services = {"OPENAI", "SNOWFLAKE", "VERCEL", "PULUMI", "GONG"}
        critical_mappings = [
            m
            for m in self.secret_mappings
            if m.environment == Environment.PRODUCTION
            and m.service in critical_services
        ]

        scripts["phase1_critical.sh"] = self._generate_migration_script(
            critical_mappings, "Phase 1: Critical Production Secrets"
        )

        # Phase 2: All production secrets
        prod_mappings = [
            m for m in self.secret_mappings if m.environment == Environment.PRODUCTION
        ]
        scripts["phase2_production.sh"] = self._generate_migration_script(
            prod_mappings, "Phase 2: All Production Secrets"
        )

        # Phase 3: Staging and development
        non_prod_mappings = [
            m for m in self.secret_mappings if m.environment != Environment.PRODUCTION
        ]
        scripts["phase3_environments.sh"] = self._generate_migration_script(
            non_prod_mappings, "Phase 3: Staging and Development Secrets"
        )

        return scripts

    def _generate_migration_script(
        self, mappings: List[SecretMapping], description: str
    ) -> str:
        """Generate shell script for secret migration."""

        script_lines = [
            "#!/bin/bash",
            f"# {description}",
            "set -e",
            "",
            "echo '🔐 Starting secret migration...'",
            "",
        ]

        # GitHub CLI commands to create new secrets
        for mapping in mappings:
            script_lines.extend(
                [
                    f"# Migrate {mapping.old_name} -> {mapping.new_name}",
                    f"if gh secret list --org ai-cherry | grep -q '{mapping.old_name}'; then",
                    f"  OLD_VALUE=$(gh secret list --org ai-cherry --json name,value | jq -r '.[] | select(.name==\"{mapping.old_name}\") | .value')",
                    f'  gh secret set {mapping.new_name} --body "$OLD_VALUE" --org ai-cherry',
                    f"  echo '✅ Migrated {mapping.old_name} -> {mapping.new_name}'",
                    "else",
                    f"  echo '⚠️  {mapping.old_name} not found'",
                    "fi",
                    "",
                ]
            )

        # Pulumi ESC update commands
        script_lines.extend(
            [
                "# Update Pulumi ESC environments",
                "echo '📝 Updating Pulumi ESC configurations...'",
            ]
        )

        for esc_config in self.esc_configs:
            if any(m.environment == esc_config.environment for m in mappings):
                script_lines.extend(
                    [
                        f"# Update {esc_config.name}",
                        f"pulumi env init {esc_config.name} --yes || true",
                        f"echo '{json.dumps(esc_config.values_structure)}' | pulumi env set {esc_config.name} --",
                        f"echo '✅ Updated {esc_config.name}'",
                        "",
                    ]
                )

        script_lines.append("echo '🎉 Migration completed successfully!'")

        return "\n".join(script_lines)

    def update_auto_esc_config(self) -> str:
        """Generate enhanced auto_esc_config.py with new structure."""

        config_code = '''"""
Enhanced Sophia AI Configuration with Environment-Aware Secret Management
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
import os
import json
import subprocess

class Environment(Enum):
    """Deployment environments."""
    PRODUCTION = "prod"
    STAGING = "stg"  
    DEVELOPMENT = "dev"

class SophiaPlatformSettings(BaseModel):
    """Platform-level settings."""
    name: str = "sophia-ai-platform"
    version: str = "v2.0.0"
    environment: str

class SophiaInfrastructureSettings(BaseModel):
    """Infrastructure service settings."""
    vercel_token: Optional[str] = None
    vercel_team_id: Optional[str] = None
    namecheap_api_key: Optional[str] = None
    namecheap_api_user: Optional[str] = None
    lambda_labs_api_key: Optional[str] = None

class SophiaDataSettings(BaseModel):
    """Data platform settings."""
    snowflake_account: Optional[str] = None
    snowflake_user: Optional[str] = None
    snowflake_password: Optional[str] = None
    snowflake_role: str = "ACCOUNTADMIN"
    snowflake_warehouse: str = "SOPHIA_AI_WH"
    snowflake_database: str = "SOPHIA_AI"
    pinecone_api_key: Optional[str] = None
    pinecone_environment: Optional[str] = None
    weaviate_api_key: Optional[str] = None

class SophiaIntegrationSettings(BaseModel):
    """Integration platform settings."""
    linear_api_key: Optional[str] = None
    asana_api_key: Optional[str] = None
    gong_access_key: Optional[str] = None
    gong_client_secret: Optional[str] = None
    apollo_api_key: Optional[str] = None
    hubspot_access_token: Optional[str] = None

class SophiaAISettings(BaseModel):
    """AI service settings."""
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    portkey_api_key: Optional[str] = None

class SophiaCommunicationSettings(BaseModel):
    """Communication service settings."""
    slack_bot_token: Optional[str] = None
    slack_webhook_url: Optional[str] = None
    discord_bot_token: Optional[str] = None

class SophiaSettings(BaseModel):
    """Complete Sophia AI configuration."""
    platform: SophiaPlatformSettings
    infrastructure: SophiaInfrastructureSettings = Field(default_factory=SophiaInfrastructureSettings)
    data: SophiaDataSettings = Field(default_factory=SophiaDataSettings)
    integration: SophiaIntegrationSettings = Field(default_factory=SophiaIntegrationSettings)
    ai: SophiaAISettings = Field(default_factory=SophiaAISettings)
    communication: SophiaCommunicationSettings = Field(default_factory=SophiaCommunicationSettings)

def load_environment_settings(environment: Environment) -> SophiaSettings:
    """Load settings for specific environment from Pulumi ESC."""
    esc_env = f"scoobyjava-org/sophia-ai-{environment.value}"
    
    try:
        result = subprocess.run([
            "pulumi", "env", "open", esc_env, "--format", "json"
        ], capture_output=True, text=True, check=True)
        
        config_data = json.loads(result.stdout)
        sophia_config = config_data.get("values", {}).get("sophia", {})
        
        return SophiaSettings(
            platform=SophiaPlatformSettings(**sophia_config.get("platform", {})),
            infrastructure=SophiaInfrastructureSettings(**sophia_config.get("infrastructure", {})),
            data=SophiaDataSettings(**sophia_config.get("data", {})),
            integration=SophiaIntegrationSettings(**sophia_config.get("integration", {})),
            ai=SophiaAISettings(**sophia_config.get("ai", {})),
            communication=SophiaCommunicationSettings(**sophia_config.get("communication", {}))
        )
    
    except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as e:
        print(f"Failed to load from Pulumi ESC: {e}")
        return load_fallback_settings()

def load_fallback_settings() -> SophiaSettings:
    """Load settings from environment variables as fallback."""
    return SophiaSettings(
        platform=SophiaPlatformSettings(
            environment=os.getenv("ENVIRONMENT", "development")
        ),
        infrastructure=SophiaInfrastructureSettings(
            vercel_token=os.getenv("SOPHIA_VERCEL_TOKEN_PROD"),
            vercel_team_id=os.getenv("SOPHIA_VERCEL_TEAM_ID_PROD"),
            namecheap_api_key=os.getenv("SOPHIA_NAMECHEAP_API_KEY_PROD"),
            lambda_labs_api_key=os.getenv("SOPHIA_LAMBDA_LABS_API_KEY_PROD")
        ),
        data=SophiaDataSettings(
            snowflake_account=os.getenv("SOPHIA_SNOWFLAKE_ACCOUNT_PROD"),
            snowflake_user=os.getenv("SOPHIA_SNOWFLAKE_USER_PROD"),
            snowflake_password=os.getenv("SOPHIA_SNOWFLAKE_PASSWORD_PROD"),
            pinecone_api_key=os.getenv("SOPHIA_PINECONE_API_KEY_PROD")
        ),
        integration=SophiaIntegrationSettings(
            linear_api_key=os.getenv("SOPHIA_LINEAR_API_KEY_PROD"),
            asana_api_key=os.getenv("SOPHIA_ASANA_API_KEY_PROD"),
            gong_access_key=os.getenv("SOPHIA_GONG_ACCESS_KEY_PROD"),
            gong_client_secret=os.getenv("SOPHIA_GONG_CLIENT_SECRET_PROD"),
            hubspot_access_token=os.getenv("SOPHIA_HUBSPOT_ACCESS_TOKEN_PROD")
        ),
        ai=SophiaAISettings(
            openai_api_key=os.getenv("SOPHIA_OPENAI_API_KEY_PROD"),
            anthropic_api_key=os.getenv("SOPHIA_ANTHROPIC_API_KEY_PROD"),
            portkey_api_key=os.getenv("SOPHIA_PORTKEY_API_KEY_PROD")
        ),
        communication=SophiaCommunicationSettings(
            slack_bot_token=os.getenv("SOPHIA_SLACK_BOT_TOKEN_PROD"),
            slack_webhook_url=os.getenv("SOPHIA_SLACK_WEBHOOK_PROD")
        )
    )

# Default configuration
current_env = Environment(os.getenv("ENVIRONMENT", "development"))
config = load_environment_settings(current_env)
'''

        return config_code

    def generate_comprehensive_report(self) -> Dict:
        """Generate comprehensive migration report."""

        # Generate all components
        self.generate_enhanced_secret_mappings()
        self.generate_esc_environments()
        migration_scripts = self.create_migration_scripts()
        updated_config = self.update_auto_esc_config()

        report = {
            "enhanced_standardization_summary": {
                "total_secrets_discovered": len(self.current_secrets),
                "total_mappings_generated": len(self.secret_mappings),
                "environments_configured": len(self.esc_configs),
                "migration_phases": len(migration_scripts),
                "naming_pattern": "SOPHIA_{SERVICE}_{TYPE}_{ENV}",
                "esc_structure": "values.sophia.{category}.{service}.{credential}",
            },
            "secret_mappings": [asdict(mapping) for mapping in self.secret_mappings],
            "esc_environments": [asdict(config) for config in self.esc_configs],
            "migration_scripts": migration_scripts,
            "implementation_plan": {
                "phase_1": "Critical production secrets (OPENAI, SNOWFLAKE, VERCEL, PULUMI, GONG)",
                "phase_2": "All production environment secrets",
                "phase_3": "Staging and development environment secrets",
                "phase_4": "Cleanup and validation",
            },
            "next_steps": [
                "Review generated migration scripts",
                "Execute Phase 1 migration for critical secrets",
                "Update backend/core/auto_esc_config.py with enhanced structure",
                "Test Pulumi ESC integration",
                "Execute remaining migration phases",
                "Clean up old secret references",
            ],
        }

        # Save migration scripts
        scripts_dir = Path("migration_scripts")
        scripts_dir.mkdir(exist_ok=True)

        for script_name, script_content in migration_scripts.items():
            script_path = scripts_dir / script_name
            with open(script_path, "w") as f:
                f.write(script_content)
            os.chmod(script_path, 0o755)  # Make executable

        # Save enhanced config
        config_path = Path("enhanced_auto_esc_config.py")
        with open(config_path, "w") as f:
            f.write(updated_config)

        # Save report with custom JSON encoder
        with open("enhanced_secret_standardization_report.json", "w") as f:
            json.dump(report, f, indent=2, default=self._json_serializer)

        return report

    def _json_serializer(self, obj):
        """Custom JSON serializer for enum objects."""
        if isinstance(obj, (ServiceCategory, Environment)):
            return obj.value
        elif isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(
            f"Object of type {obj.__class__.__name__} is not JSON serializable"
        )


def main():
    """Main execution function."""
    print("🚀 Sophia AI - Enhanced Secret Standardization")
    print("=" * 60)

    standardizer = EnhancedSecretStandardizer()
    report = standardizer.generate_comprehensive_report()

    print("\n📊 ENHANCED STANDARDIZATION SUMMARY")
    print("-" * 40)
    summary = report["enhanced_standardization_summary"]
    print(f"Secrets discovered: {summary['total_secrets_discovered']}")
    print(f"Mappings generated: {summary['total_mappings_generated']}")
    print(f"ESC environments: {summary['environments_configured']}")
    print(f"Migration phases: {summary['migration_phases']}")
    print(f"Naming pattern: {summary['naming_pattern']}")

    print("\n📁 FILES GENERATED:")
    print("- enhanced_secret_standardization_report.json")
    print("- enhanced_auto_esc_config.py")
    print("- migration_scripts/phase1_critical.sh")
    print("- migration_scripts/phase2_production.sh")
    print("- migration_scripts/phase3_environments.sh")

    print("\n🎯 NEXT STEPS:")
    print("1. Review generated migration scripts")
    print("2. Execute: ./migration_scripts/phase1_critical.sh")
    print("3. Update backend/core/auto_esc_config.py")
    print("4. Test Pulumi ESC integration")
    print("5. Continue with remaining phases")


if __name__ == "__main__":
    main()
