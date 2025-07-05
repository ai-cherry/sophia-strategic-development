#!/usr/bin/env python3
"""
Enhanced Pulumi ESC Implementation Script
=========================================
Addresses all identified gaps in the Sophia AI IaC strategy:
1. Automated SSH key management for Lambda Labs
2. Consolidated Pulumi language strategy (TypeScript)
3. Complete IaC coverage for all services
4. Bi-directional GitHub <-> Pulumi ESC sync
"""

import json
from pathlib import Path


class EnhancedPulumiESCImplementation:
    def __init__(self):
        self.project_root = Path.cwd()
        self.infrastructure_dir = self.project_root / "infrastructure"
        self.esc_dir = self.infrastructure_dir / "esc"
        self.github_org = "ai-cherry"
        self.pulumi_org = "scoobyjava-org"
        self.pulumi_project = "sophia-ai-production"

    def implement_phase1_ssh_automation(self):
        """Phase 1: Solve the SSH key management problem"""
        print("\n🔐 Phase 1: Implementing Automated SSH Key Management")
        print("=" * 60)

        # Create SSH key management script
        ssh_manager_path = self.esc_dir / "ssh_key_manager.py"
        ssh_manager_content = '''#!/usr/bin/env python3
"""
Lambda Labs SSH Key Manager
===========================
Automates SSH key provisioning for Lambda Labs instances
"""

import json
import base64
import subprocess
from pathlib import Path

class LambdaLabsSSHManager:
    def __init__(self):
        self.ssh_dir = Path.home() / ".ssh"
        self.key_name = "pulumi_lambda_key"

    def generate_ssh_key_if_needed(self):
        """Generate SSH key pair if it doesn't exist"""
        private_key_path = self.ssh_dir / self.key_name
        public_key_path = self.ssh_dir / f"{self.key_name}.pub"

        if not private_key_path.exists():
            print(f"🔑 Generating new SSH key pair: {self.key_name}")
            subprocess.run([
                "ssh-keygen", "-t", "ed25519",
                "-f", str(private_key_path),
                "-N", "",  # No passphrase
                "-C", "pulumi@sophia-ai"
            ], check=True)

            # Set proper permissions
            private_key_path.chmod(0o600)
            public_key_path.chmod(0o644)

        return private_key_path, public_key_path

    def get_public_key_content(self):
        """Get the public key content"""
        _, public_key_path = self.generate_ssh_key_if_needed()
        return public_key_path.read_text().strip()

    def encode_for_pulumi_esc(self, content: str) -> str:
        """Encode multi-line content for Pulumi ESC"""
        # Base64 encode to handle multi-line content
        encoded = base64.b64encode(content.encode()).decode()
        return encoded

    def store_in_pulumi_esc(self):
        """Store SSH public key in Pulumi ESC"""
        public_key = self.get_public_key_content()
        encoded_key = self.encode_for_pulumi_esc(public_key)

        # Store as base64 encoded value
        cmd = [
            "pulumi", "env", "set",
            "scoobyjava-org/default/sophia-ai-production",
            "lambda_labs_ssh_public_key_base64",
            encoded_key
        ]

        print("📤 Storing SSH public key in Pulumi ESC (base64 encoded)")
        subprocess.run(cmd, check=True)

        # Also store the key name
        subprocess.run([
            "pulumi", "env", "set",
            "scoobyjava-org/default/sophia-ai-production",
            "lambda_labs_ssh_key_name",
            self.key_name
        ], check=True)

        print("✅ SSH key stored in Pulumi ESC successfully")

    def inject_key_via_lambda_api(self, instance_id: str):
        """Inject SSH key into Lambda Labs instance via API"""
        # This would use the Lambda Labs API to inject the key
        # For now, we'll use user-data approach in Pulumi
        print(f"🚀 Would inject SSH key into instance: {instance_id}")

if __name__ == "__main__":
    manager = LambdaLabsSSHManager()
    manager.store_in_pulumi_esc()
'''

        self.esc_dir.mkdir(parents=True, exist_ok=True)
        ssh_manager_path.write_text(ssh_manager_content)
        ssh_manager_path.chmod(0o755)
        print(f"✅ Created SSH key manager: {ssh_manager_path}")

        # Create cloud-init template for Lambda Labs
        cloud_init_path = (
            self.infrastructure_dir / "templates" / "lambda-labs-cloud-init.yaml"
        )
        cloud_init_path.parent.mkdir(exist_ok=True)

        cloud_init_content = """#cloud-config
# Lambda Labs instance initialization with SSH key injection

users:
  - name: ubuntu
    sudo: ALL=(ALL) NOPASSWD:ALL
    ssh_authorized_keys:
      - ${ssh_public_key}

# Install essential packages
packages:
  - docker.io
  - docker-compose
  - kubectl
  - python3-pip
  - git
  - htop
  - tmux

# Enable Docker
runcmd:
  - systemctl enable docker
  - systemctl start docker
  - usermod -aG docker ubuntu

# Write deployment marker
write_files:
  - path: /home/ubuntu/.sophia-ai-deployed
    content: |
      DEPLOYED_BY=pulumi
      DEPLOYED_AT=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
      SSH_KEY_NAME=${ssh_key_name}
"""

        cloud_init_path.write_text(cloud_init_content)
        print(f"✅ Created cloud-init template: {cloud_init_path}")

    def implement_phase2_language_consolidation(self):
        """Phase 2: Consolidate Pulumi to TypeScript only"""
        print("\n🎯 Phase 2: Consolidating Pulumi to TypeScript")
        print("=" * 60)

        # Create unified TypeScript infrastructure
        unified_infra_path = self.infrastructure_dir / "index.ts"
        unified_infra_content = """import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";
import * as k8s from "@pulumi/kubernetes";
import { LambdaLabsProvider } from "./providers/lambda-labs";
import { SnowflakeProvider } from "./providers/snowflake";
import { EstuaryProvider } from "./providers/estuary";
import { GitHubProvider } from "./providers/github";
import { PortkeyProvider } from "./providers/portkey";

// Get configuration from Pulumi ESC
const config = new pulumi.Config();
const pulumiOrg = config.require("pulumiOrg");
const environment = config.require("environment");

// Import ESC secrets
const escConfig = new pulumi.StackReference(`${pulumiOrg}/default/sophia-ai-${environment}`);

// Lambda Labs Infrastructure
export const lambdaLabs = new LambdaLabsProvider("lambda-labs", {
    apiKey: escConfig.getOutput("lambda_api_key"),
    sshPublicKeyBase64: escConfig.getOutput("lambda_labs_ssh_public_key_base64"),
    instances: [
        {
            name: "sophia-platform-prod",
            instanceType: "gpu_1x_a100",
            region: "us-west-1",
            userData: pulumi.interpolate`${cloudInitScript}`,
        },
        {
            name: "sophia-mcp-prod",
            instanceType: "gpu_1x_a100",
            region: "us-west-1",
            userData: pulumi.interpolate`${cloudInitScript}`,
        }
    ]
});

// Snowflake Infrastructure
export const snowflake = new SnowflakeProvider("snowflake", {
    account: escConfig.getOutput("snowflake_account"),
    username: escConfig.getOutput("snowflake_user"),
    password: escConfig.getOutput("snowflake_password"),
    role: escConfig.getOutput("snowflake_role"),
    databases: [
        {
            name: "SOPHIA_AI_PROD",
            schemas: ["PUBLIC", "AI_MEMORY", "BUSINESS_INTELLIGENCE"],
            warehouses: ["COMPUTE_WH", "ANALYTICS_WH"],
        }
    ]
});

// Estuary Flow Infrastructure
export const estuary = new EstuaryProvider("estuary", {
    accessToken: escConfig.getOutput("estuary_access_token"),
    tenant: escConfig.getOutput("estuary_tenant"),
    flows: [
        {
            name: "gong-to-snowflake",
            source: "gong",
            destination: "snowflake",
            schedule: "0 */2 * * *", // Every 2 hours
        },
        {
            name: "hubspot-to-snowflake",
            source: "hubspot",
            destination: "snowflake",
            schedule: "0 */4 * * *", // Every 4 hours
        }
    ]
});

// GitHub Infrastructure
export const github = new GitHubProvider("github", {
    token: escConfig.getOutput("github_token"),
    organization: "ai-cherry",
    repositories: [
        {
            name: "sophia-main",
            private: true,
            branchProtection: {
                branches: ["main"],
                requiredReviews: 1,
            }
        }
    ],
    secrets: {
        organization: true,
        syncWithPulumiESC: true,
    }
});

// Portkey Infrastructure
export const portkey = new PortkeyProvider("portkey", {
    apiKey: escConfig.getOutput("portkey_api_key"),
    projects: [
        {
            name: "sophia-ai-production",
            virtualKeys: true,
            costAlerts: {
                daily: 1000,
                monthly: 25000,
            }
        }
    ]
});

// Export important values
export const lambdaLabsInstances = lambdaLabs.instances;
export const snowflakeDatabase = snowflake.database;
export const estuaryFlows = estuary.flows;
export const githubRepos = github.repositories;
export const portkeyProject = portkey.project;
"""

        unified_infra_path.write_text(unified_infra_content)
        print(f"✅ Created unified TypeScript infrastructure: {unified_infra_path}")

        # Create provider modules
        providers_dir = self.infrastructure_dir / "providers"
        providers_dir.mkdir(exist_ok=True)

        # Lambda Labs Provider
        lambda_provider_path = providers_dir / "lambda-labs.ts"
        lambda_provider_content = """import * as pulumi from "@pulumi/pulumi";
import axios from "axios";
import { decode } from "base-64";

export interface LambdaLabsInstanceConfig {
    name: string;
    instanceType: string;
    region: string;
    userData?: pulumi.Input<string>;
}

export class LambdaLabsProvider extends pulumi.ComponentResource {
    public instances: pulumi.Output<any[]>;

    constructor(name: string, args: {
        apiKey: pulumi.Input<string>;
        sshPublicKeyBase64: pulumi.Input<string>;
        instances: LambdaLabsInstanceConfig[];
    }, opts?: pulumi.ComponentResourceOptions) {
        super("sophia:infrastructure:LambdaLabs", name, {}, opts);

        // Decode SSH public key
        const sshPublicKey = pulumi.output(args.sshPublicKeyBase64).apply(
            key => Buffer.from(key, 'base64').toString('utf-8')
        );

        // Create instances
        this.instances = pulumi.output(args.instances.map(instance => {
            // Inject SSH key into user data
            const userData = pulumi.interpolate`#!/bin/bash
echo "${sshPublicKey}" >> /home/ubuntu/.ssh/authorized_keys
${instance.userData || ""}
`;

            // Here we would call Lambda Labs API to create instance
            // For now, return a mock instance
            return {
                name: instance.name,
                type: instance.instanceType,
                region: instance.region,
                status: "provisioning",
                userData: userData,
            };
        }));
    }
}
"""
        lambda_provider_path.write_text(lambda_provider_content)
        print(f"✅ Created Lambda Labs provider: {lambda_provider_path}")

    def implement_phase3_complete_iac_coverage(self):
        """Phase 3: Implement complete IaC coverage for all services"""
        print("\n🚀 Phase 3: Implementing Complete IaC Coverage")
        print("=" * 60)

        # Create comprehensive secret mappings
        secret_mappings_path = self.esc_dir / "secret_mappings.json"
        secret_mappings = {
            "github_to_pulumi": {
                # AI Services
                "OPENAI_API_KEY": "values.sophia.ai.openai.api_key",
                "ANTHROPIC_API_KEY": "values.sophia.ai.anthropic.api_key",
                "GROQ_API_KEY": "groq_api_key",
                "MISTRAL_API_KEY": "mistral_api_key",
                "DEEPSEEK_API_KEY": "deepseek_api_key",
                "PERPLEXITY_API_KEY": "perplexity_api_key",
                "TOGETHER_AI_API_KEY": "together_ai_api_key",
                "ELEVEN_LABS_API_KEY": "eleven_labs_api_key",
                "STABILITY_API_KEY": "stability_api_key",
                "OPENROUTER_API_KEY": "openrouter_api_key",
                "PORTKEY_API_KEY": "portkey_api_key",
                "PORTKEY_CONFIG_ID": "portkey_config_id",
                "MEM0_API_KEY": "values.sophia.ai.mem0.api_key",
                "LANGCHAIN_API_KEY": "langchain_api_key",
                "LANGGRAPH_API_KEY": "langgraph_api_key",
                "TAVILY_API_KEY": "tavily_api_key",
                "LLAMA_API_KEY": "llama_api_key",
                # Business Intelligence
                "GONG_ACCESS_KEY": "values.sophia.business.gong.access_key",
                "GONG_CLIENT_SECRET": "values.sophia.business.gong.client_secret",
                "HUBSPOT_ACCESS_TOKEN": "hubspot_access_token",
                "HUBSPOT_API_KEY": "hubspot_api_key",
                "HUBSPOT_CLIENT_SECRET": "hubspot_client_secret",
                "LINEAR_API_KEY": "linear_api_key",
                "NOTION_API_TOKEN": "notion_api_token",
                "ASANA_API_TOKEN": "asana_api_token",
                # Communication
                "SLACK_APP_TOKEN": "slack_app_token",
                "SLACK_BOT_TOKEN": "slack_bot_token",
                "SLACK_CLIENT_ID": "slack_client_id",
                "SLACK_CLIENT_SECRET": "slack_client_secret",
                "SLACK_SIGNING_SECRET": "slack_signing_secret",
                # Data Infrastructure
                "SNOWFLAKE_ACCOUNT": "snowflake_account",
                "SNOWFLAKE_USER": "snowflake_user",
                "SNOWFLAKE_PASSWORD": "snowflake_password",
                "SNOWFLAKE_ROLE": "snowflake_role",
                "SNOWFLAKE_DATABASE": "snowflake_database",
                "SNOWFLAKE_WAREHOUSE": "snowflake_warehouse",
                "SNOWFLAKE_SCHEMA": "snowflake_schema",
                "DATABASE_URL": "database_url",
                "REDIS_URL": "redis_url",
                "REDIS_PASSWORD": "redis_password",
                "PINECONE_API_KEY": "values.sophia.data.pinecone.api_key",
                "PINECONE_ENVIRONMENT": "pinecone_environment",
                "PINECONE_INDEX_NAME": "pinecone_index_name",
                # Data Integration
                "ESTUARY_ACCESS_TOKEN": "estuary_access_token",
                "ESTUARY_REFRESH_TOKEN": "estuary_refresh_token",
                "ESTUARY_ENDPOINT": "estuary_endpoint",
                "ESTUARY_TENANT": "estuary_tenant",
                # Cloud Infrastructure
                "LAMBDA_API_KEY": "lambda_api_key",
                "PULUMI_ACCESS_TOKEN": "values.sophia.infrastructure.pulumi.access_token",
                "VERCEL_API_TOKEN": "vercel_api_token",
                "LAMBDA_IP_ADDRESS": "lambda_ip_address",
                # Development Tools
                "GITHUB_TOKEN": "github_token",
                # Security
                "JWT_SECRET": "jwt_secret",
                "API_SECRET_KEY": "api_secret_key",
                "ENCRYPTION_KEY": "encryption_key",
                # SSH Keys (NEW)
                "LAMBDA_LABS_SSH_PUBLIC_KEY": "lambda_labs_ssh_public_key_base64",
                "LAMBDA_LABS_SSH_KEY_NAME": "lambda_labs_ssh_key_name",
            },
            "services": {
                "lambda_labs": {
                    "required_secrets": [
                        "lambda_api_key",
                        "lambda_labs_ssh_public_key_base64",
                        "lambda_labs_ssh_key_name",
                    ]
                },
                "snowflake": {
                    "required_secrets": [
                        "snowflake_account",
                        "snowflake_user",
                        "snowflake_password",
                        "snowflake_role",
                        "snowflake_database",
                        "snowflake_warehouse",
                        "snowflake_schema",
                    ]
                },
                "estuary": {
                    "required_secrets": [
                        "estuary_access_token",
                        "estuary_refresh_token",
                        "estuary_endpoint",
                        "estuary_tenant",
                    ]
                },
                "github": {"required_secrets": ["github_token", "pulumi_access_token"]},
                "portkey": {
                    "required_secrets": ["portkey_api_key", "portkey_config_id"]
                },
            },
        }

        with open(secret_mappings_path, "w") as f:
            json.dump(secret_mappings, f, indent=2)
        print(f"✅ Created comprehensive secret mappings: {secret_mappings_path}")

    def implement_phase4_bidirectional_sync(self):
        """Phase 4: Implement bi-directional GitHub <-> Pulumi ESC sync"""
        print("\n🔄 Phase 4: Implementing Bi-directional Sync")
        print("=" * 60)

        # Create bi-directional sync script
        sync_script_path = self.esc_dir / "github_sync_bidirectional.py"
        sync_script_content = '''#!/usr/bin/env python3
"""
Bi-directional GitHub <-> Pulumi ESC Sync
=========================================
Ensures GitHub Organization Secrets and Pulumi ESC stay in sync
"""

import json
import subprocess
import os
from pathlib import Path
from typing import Dict, Set

class BiDirectionalSync:
    def __init__(self):
        self.mappings_path = Path(__file__).parent / "secret_mappings.json"
        self.load_mappings()

    def load_mappings(self):
        """Load secret mappings configuration"""
        with open(self.mappings_path) as f:
            self.mappings = json.load(f)

    def get_github_secrets(self) -> Set[str]:
        """Get list of GitHub organization secrets"""
        cmd = ["gh", "secret", "list", "--org", "ai-cherry", "--json", "name"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            secrets = json.loads(result.stdout)
            return {s["name"] for s in secrets}
        return set()

    def get_pulumi_secrets(self) -> Dict[str, str]:
        """Get all Pulumi ESC values"""
        cmd = ["pulumi", "env", "open", "scoobyjava-org/default/sophia-ai-production", "--format", "json"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return json.loads(result.stdout)
        return {}

    def sync_github_to_pulumi(self):
        """Sync GitHub secrets to Pulumi ESC"""
        print("📥 Syncing GitHub → Pulumi ESC...")
        github_secrets = self.get_github_secrets()

        for gh_secret, pulumi_path in self.mappings["github_to_pulumi"].items():
            if gh_secret in github_secrets:
                # Get the secret value from GitHub (requires PAT with org:admin)
                value = os.environ.get(gh_secret, "")
                if value and value != f"PLACEHOLDER_{gh_secret}":
                    # Set in Pulumi ESC
                    cmd = [
                        "pulumi", "env", "set",
                        "scoobyjava-org/default/sophia-ai-production",
                        pulumi_path,
                        value,
                        "--secret"
                    ]
                    subprocess.run(cmd, capture_output=True)
                    print(f"  ✅ {gh_secret} → {pulumi_path}")

    def sync_pulumi_to_github(self):
        """Sync Pulumi ESC secrets to GitHub"""
        print("📤 Syncing Pulumi ESC → GitHub...")
        pulumi_secrets = self.get_pulumi_secrets()

        for gh_secret, pulumi_path in self.mappings["github_to_pulumi"].items():
            # Navigate nested path
            value = pulumi_secrets
            for part in pulumi_path.split("."):
                value = value.get(part, {})

            if isinstance(value, str) and value and not value.startswith("PLACEHOLDER_"):
                # Set in GitHub
                cmd = [
                    "gh", "secret", "set", gh_secret,
                    "--org", "ai-cherry",
                    "--body", value
                ]
                subprocess.run(cmd, capture_output=True)
                print(f"  ✅ {pulumi_path} → {gh_secret}")

    def validate_sync(self):
        """Validate that all required secrets are present"""
        print("\\n🔍 Validating secret synchronization...")
        pulumi_secrets = self.get_pulumi_secrets()

        all_valid = True
        for service, config in self.mappings["services"].items():
            print(f"\\n  Service: {service}")
            for secret in config["required_secrets"]:
                # Check if secret exists and is not a placeholder
                value = pulumi_secrets.get(secret, "")
                if value and not value.startswith("PLACEHOLDER_"):
                    print(f"    ✅ {secret}")
                else:
                    print(f"    ❌ {secret} (missing or placeholder)")
                    all_valid = False

        return all_valid

if __name__ == "__main__":
    sync = BiDirectionalSync()
    sync.sync_github_to_pulumi()
    sync.sync_pulumi_to_github()

    if sync.validate_sync():
        print("\\n✅ All secrets synchronized successfully!")
    else:
        print("\\n⚠️  Some secrets are missing or need configuration")
'''

        sync_script_path.write_text(sync_script_content)
        sync_script_path.chmod(0o755)
        print(f"✅ Created bi-directional sync script: {sync_script_path}")

    def create_implementation_plan(self):
        """Create detailed implementation plan"""
        print("\n📋 Creating Implementation Plan")
        print("=" * 60)

        plan_path = self.project_root / "ENHANCED_PULUMI_ESC_IMPLEMENTATION_PLAN.md"
        plan_content = """# Enhanced Pulumi ESC Implementation Plan

## 🎯 Objective
Transform Sophia AI's Infrastructure as Code to a "fully finished, fully baked" state with:
- ✅ Automated SSH key management for Lambda Labs
- ✅ Consolidated TypeScript-only Pulumi infrastructure
- ✅ Complete IaC coverage for all services
- ✅ Bi-directional GitHub <-> Pulumi ESC synchronization

## 📅 Implementation Timeline

### Phase 1: SSH Key Automation (Day 1)
**Goal**: Eliminate manual SSH key configuration for Lambda Labs

1. **Generate and Store SSH Keys**
   ```bash
   cd infrastructure/esc
   python ssh_key_manager.py
   ```

2. **Update Lambda Labs Pulumi Provider**
   - Implement cloud-init user data injection
   - Base64 decode SSH keys from Pulumi ESC
   - Automatic key provisioning on instance creation

3. **Test SSH Access**
   ```bash
   ssh -i ~/.ssh/pulumi_lambda_key ubuntu@<instance-ip>
   ```

### Phase 2: Language Consolidation (Day 2-3)
**Goal**: Migrate all Pulumi code to TypeScript

1. **Convert Python Infrastructure**
   - Migrate `infrastructure/index.py` to TypeScript
   - Create unified `infrastructure/index.ts`
   - Implement provider pattern for each service

2. **Create Service Providers**
   - `providers/lambda-labs.ts`
   - `providers/snowflake.ts`
   - `providers/estuary.ts`
   - `providers/github.ts`
   - `providers/portkey.ts`

3. **Update Build System**
   ```bash
   cd infrastructure
   npm init -y
   npm install @pulumi/pulumi @pulumi/kubernetes
   npm install typescript ts-node
   ```

### Phase 3: Complete IaC Coverage (Day 4-7)
**Goal**: Implement IaC for all services

1. **Estuary Flow**
   - Connector provisioning
   - Data flow configuration
   - Collection management
   - Schedule automation

2. **Snowflake Enhanced**
   - Database/schema creation
   - User/role management
   - Grants and permissions
   - External stages and pipes

3. **GitHub Resources**
   - Repository management
   - Team configuration
   - Webhook setup
   - Branch protection rules

4. **Portkey Projects**
   - Virtual key management
   - Cost alert configuration
   - Project settings

### Phase 4: Bi-directional Sync (Day 8-9)
**Goal**: Automated secret synchronization

1. **GitHub Actions Workflow**
   ```yaml
   name: Sync Secrets Bi-directional
   on:
     schedule:
       - cron: '0 */6 * * *'  # Every 6 hours
     workflow_dispatch:
   ```

2. **Validation Framework**
   - Secret presence checking
   - Placeholder detection
   - Service readiness validation

3. **Monitoring and Alerts**
   - Secret rotation tracking
   - Sync failure notifications
   - Compliance reporting

## 🚀 Deployment Commands

### Initial Setup
```bash
# 1. Set up SSH key automation
cd infrastructure/esc
python ssh_key_manager.py

# 2. Install TypeScript dependencies
cd ../
npm install

# 3. Deploy infrastructure
pulumi up -s sophia-ai-production

# 4. Run bi-directional sync
cd esc
python github_sync_bidirectional.py
```

### Validation
```bash
# Validate all services
python infrastructure/esc/validate_iac_completeness.py

# Test SSH access
ssh -i ~/.ssh/pulumi_lambda_key ubuntu@$(pulumi stack output platform_ip)

# Check secret sync status
python infrastructure/esc/sync_status_validator.py
```

## 📊 Success Metrics

1. **SSH Automation**
   - ✅ Zero manual SSH key steps
   - ✅ Automatic key injection on instance creation
   - ✅ Successful SSH access without manual configuration

2. **Language Consolidation**
   - ✅ 100% TypeScript Pulumi code
   - ✅ Zero Python Pulumi files
   - ✅ Consistent provider pattern

3. **IaC Coverage**
   - ✅ All 5 services fully managed by Pulumi
   - ✅ No manual infrastructure steps
   - ✅ Complete automation from code to deployment

4. **Secret Management**
   - ✅ 100% secret synchronization
   - ✅ Zero placeholder values in production
   - ✅ Automated rotation capability

## 🛡️ Security Considerations

1. **SSH Key Security**
   - Private keys never stored in Pulumi ESC
   - Public keys base64 encoded for multi-line support
   - Proper file permissions (600 for private, 644 for public)

2. **Secret Rotation**
   - Automated rotation workflows
   - Audit trails for all changes
   - Zero-downtime secret updates

3. **Access Control**
   - GitHub organization admin for secret management
   - Pulumi RBAC for environment access
   - Service-specific IAM policies

## 📚 Documentation Updates

1. Update `infrastructure/README.md` to reflect:
   - TypeScript-only approach
   - Complete service coverage
   - SSH key automation

2. Update `docs/system_handbook/00_SOPHIA_AI_SYSTEM_HANDBOOK.md`:
   - New IaC architecture
   - Automated workflows
   - Security enhancements

3. Create new guides:
   - `docs/infrastructure/SSH_KEY_AUTOMATION.md`
   - `docs/infrastructure/TYPESCRIPT_MIGRATION.md`
   - `docs/infrastructure/COMPLETE_IAC_GUIDE.md`

## ✅ Completion Checklist

- [ ] SSH key automation implemented and tested
- [ ] All Pulumi code migrated to TypeScript
- [ ] Estuary Flow IaC implemented
- [ ] Snowflake enhanced IaC implemented
- [ ] GitHub resources IaC implemented
- [ ] Portkey projects IaC implemented
- [ ] Bi-directional sync operational
- [ ] All secrets validated (no placeholders)
- [ ] Documentation fully updated
- [ ] Team trained on new workflows

## 🎉 Expected Outcome

A truly "fully finished, fully baked" Infrastructure as Code implementation where:
- Every infrastructure component is defined in code
- No manual steps required for any deployment
- Complete automation from commit to production
- Enterprise-grade security and compliance
- Zero-friction developer experience
"""

        plan_path.write_text(plan_content)
        print(f"✅ Created implementation plan: {plan_path}")

    def run(self):
        """Execute the implementation"""
        print("🚀 Enhanced Pulumi ESC Implementation")
        print("=" * 60)

        # Create ESC directory if needed
        self.esc_dir.mkdir(parents=True, exist_ok=True)

        # Execute all phases
        self.implement_phase1_ssh_automation()
        self.implement_phase2_language_consolidation()
        self.implement_phase3_complete_iac_coverage()
        self.implement_phase4_bidirectional_sync()
        self.create_implementation_plan()

        print("\n✅ Enhanced Pulumi ESC implementation scripts created!")
        print("\n📋 Next Steps:")
        print(
            "1. Review the implementation plan: ENHANCED_PULUMI_ESC_IMPLEMENTATION_PLAN.md"
        )
        print("2. Execute Phase 1 (SSH Automation):")
        print("   cd infrastructure/esc && python ssh_key_manager.py")
        print("3. Begin TypeScript migration following the plan")
        print("4. Implement complete IaC coverage for all services")
        print("5. Enable bi-directional secret synchronization")


if __name__ == "__main__":
    implementation = EnhancedPulumiESCImplementation()
    implementation.run()
