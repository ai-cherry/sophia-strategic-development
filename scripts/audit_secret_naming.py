#!/usr/bin/env python3
"""
Sophia AI - Comprehensive Secret Naming Audit & Standardization
Analyzes GitHub secrets, Pulumi ESC mappings, and codebase references
"""

import re
import json
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class SecretReference:
    """Represents a secret reference found in code."""
    file_path: str
    line_number: int
    context: str
    secret_name: str
    usage_type: str  # 'github_action', 'pulumi_esc', 'env_var', 'code_reference'

@dataclass
class SecretAnalysis:
    """Analysis results for a secret."""
    current_name: str
    recommended_name: str
    service: str
    credential_type: str
    references: List[SecretReference]
    is_consistent: bool
    action_required: str  # 'keep', 'rename', 'delete', 'consolidate'

class SecretAuditor:
    """Audits and analyzes secret naming across the Sophia AI platform."""
    
    def __init__(self):
        self.workspace_root = Path.cwd()
        self.github_secrets: Set[str] = set()
        self.pulumi_esc_secrets: Set[str] = set()
        self.code_references: List[SecretReference] = []
        self.analysis_results: List[SecretAnalysis] = []
        
        # Standard service mapping for consistent naming
        self.service_mappings = {
            'OPENAI': 'ai.openai',
            'ANTHROPIC': 'ai.anthropic', 
            'GONG': 'business.gong',
            'HUBSPOT': 'business.hubspot',
            'LINEAR': 'business.linear',
            'NOTION': 'business.notion',
            'SLACK': 'communication.slack',
            'SNOWFLAKE': 'data.snowflake',
            'PINECONE': 'data.pinecone',
            'WEAVIATE': 'data.weaviate',
            'LAMBDA': 'infrastructure.lambda_labs',
            'VERCEL': 'infrastructure.vercel',
            'DOCKER': 'development.docker',
            'GITHUB': 'development.github',
            'PULUMI': 'infrastructure.pulumi'
        }
        
        # Standard credential types
        self.credential_types = {
            'API_KEY', 'ACCESS_TOKEN', 'CLIENT_SECRET', 'PASSWORD', 
            'USERNAME', 'ACCOUNT', 'URL', 'ENVIRONMENT', 'ORG_ID',
            'PROJECT_ID', 'SPACE_ID', 'ROLE', 'DATABASE', 'WAREHOUSE'
        }

    def extract_github_secrets(self) -> None:
        """Extract secrets from GitHub Actions workflows."""
        print("🔍 Extracting GitHub secrets from workflows...")
        
        workflow_dir = self.workspace_root / '.github' / 'workflows'
        if not workflow_dir.exists():
            print("❌ No GitHub workflows directory found")
            return
            
        for workflow_file in workflow_dir.glob('*.yml'):
            with open(workflow_file, 'r') as f:
                content = f.read()
                
            # Find secrets.SECRET_NAME patterns
            secret_pattern = r'\$\{\{\s*secrets\.([A-Z_]+)\s*\}\}'
            matches = re.finditer(secret_pattern, content)
            
            for match in matches:
                secret_name = match.group(1)
                self.github_secrets.add(secret_name)
                
                # Get line number and context
                lines = content[:match.start()].split('\n')
                line_number = len(lines)
                line_context = content.split('\n')[line_number - 1].strip()
                
                self.code_references.append(SecretReference(
                    file_path=str(workflow_file.relative_to(self.workspace_root)),
                    line_number=line_number,
                    context=line_context,
                    secret_name=secret_name,
                    usage_type='github_action'
                ))

    def extract_pulumi_esc_mappings(self) -> None:
        """Extract secrets from Pulumi ESC sync script."""
        print("🔍 Extracting Pulumi ESC mappings...")
        
        sync_script = self.workspace_root / 'scripts' / 'ci' / 'sync_from_gh_to_pulumi.py'
        if not sync_script.exists():
            print("❌ Pulumi sync script not found")
            return
            
        with open(sync_script, 'r') as f:
            content = f.read()
            
        # Extract secret mappings dictionary
        mapping_pattern = r'"([A-Z_]+)":\s*"([^"]+)"'
        matches = re.finditer(mapping_pattern, content)
        
        for match in matches:
            github_secret = match.group(1)
            match.group(2)
            self.pulumi_esc_secrets.add(github_secret)
            
            # Get line number
            lines = content[:match.start()].split('\n')
            line_number = len(lines)
            line_context = content.split('\n')[line_number - 1].strip()
            
            self.code_references.append(SecretReference(
                file_path=str(sync_script.relative_to(self.workspace_root)),
                line_number=line_number,
                context=line_context,
                secret_name=github_secret,
                usage_type='pulumi_esc'
            ))

    def extract_code_references(self) -> None:
        """Extract secret references from codebase."""
        print("🔍 Scanning codebase for secret references...")
        
        # Search patterns for environment variables and secret references
        patterns = [
            r'os\.getenv\(["\']([A-Z_]+)["\']',  # Python os.getenv
            r'process\.env\.([A-Z_]+)',  # JavaScript process.env
            r'\$\{([A-Z_]+)\}',  # Shell/Docker environment variables
            r'config\.get\(["\']([a-z_]+)["\']'  # Config get calls
        ]
        
        # File extensions to search
        extensions = ['.py', '.js', '.ts', '.yml', '.yaml', '.sh', '.md', '.json']
        
        for ext in extensions:
            for file_path in self.workspace_root.rglob(f'*{ext}'):
                # Skip certain directories
                if any(skip in str(file_path) for skip in ['.git', 'node_modules', '__pycache__', '.env']):
                    continue
                    
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    for pattern in patterns:
                        matches = re.finditer(pattern, content)
                        for match in matches:
                            secret_name = match.group(1)
                            
                            # Filter for likely secret names (all caps with underscores)
                            if re.match(r'^[A-Z][A-Z_]*[A-Z]$', secret_name) or secret_name.endswith('_KEY') or secret_name.endswith('_TOKEN'):
                                lines = content[:match.start()].split('\n')
                                line_number = len(lines)
                                line_context = content.split('\n')[line_number - 1].strip()
                                
                                self.code_references.append(SecretReference(
                                    file_path=str(file_path.relative_to(self.workspace_root)),
                                    line_number=line_number,
                                    context=line_context,
                                    secret_name=secret_name,
                                    usage_type='code_reference'
                                ))
                                
                except (UnicodeDecodeError, PermissionError):
                    continue

    def analyze_secret_consistency(self) -> None:
        """Analyze secrets for consistency and generate recommendations."""
        print("📊 Analyzing secret consistency...")
        
        # Get all unique secret names
        all_secrets = self.github_secrets | self.pulumi_esc_secrets | {ref.secret_name for ref in self.code_references}
        
        for secret_name in sorted(all_secrets):
            analysis = self._analyze_individual_secret(secret_name)
            self.analysis_results.append(analysis)

    def _analyze_individual_secret(self, secret_name: str) -> SecretAnalysis:
        """Analyze an individual secret for consistency."""
        # Get all references for this secret
        references = [ref for ref in self.code_references if ref.secret_name == secret_name]
        
        # Determine service and credential type
        service, credential_type = self._extract_service_and_type(secret_name)
        
        # Generate recommended name
        recommended_name = self._generate_recommended_name(service, credential_type, secret_name)
        
        # Determine if consistent
        is_consistent = secret_name == recommended_name
        
        # Determine action required
        action_required = self._determine_action(secret_name, references)
        
        return SecretAnalysis(
            current_name=secret_name,
            recommended_name=recommended_name,
            service=service,
            credential_type=credential_type,
            references=references,
            is_consistent=is_consistent,
            action_required=action_required
        )

    def _extract_service_and_type(self, secret_name: str) -> Tuple[str, str]:
        """Extract service and credential type from secret name."""
        # Common patterns
        if 'OPENAI' in secret_name:
            return 'openai', 'API_KEY'
        elif 'GONG' in secret_name:
            if 'SECRET' in secret_name:
                return 'gong', 'CLIENT_SECRET'
            else:
                return 'gong', 'ACCESS_KEY'
        elif 'SNOWFLAKE' in secret_name:
            if 'PASSWORD' in secret_name:
                return 'snowflake', 'PASSWORD'
            elif 'ACCOUNT' in secret_name:
                return 'snowflake', 'ACCOUNT'
            elif 'USER' in secret_name:
                return 'snowflake', 'USER'
            else:
                return 'snowflake', 'UNKNOWN'
        elif 'VERCEL' in secret_name:
            if 'PROJECT' in secret_name:
                return 'vercel', 'PROJECT_ID'
            elif 'ORG' in secret_name:
                return 'vercel', 'ORG_ID'
            else:
                return 'vercel', 'ACCESS_TOKEN'
        elif 'SLACK' in secret_name:
            if 'BOT' in secret_name:
                return 'slack', 'BOT_TOKEN'
            elif 'APP' in secret_name:
                return 'slack', 'APP_TOKEN'
            elif 'SIGNING' in secret_name:
                return 'slack', 'SIGNING_SECRET'
            else:
                return 'slack', 'UNKNOWN'
        elif 'LAMBDA' in secret_name:
            return 'lambda_labs', 'API_KEY'
        elif 'PINECONE' in secret_name:
            if 'ENVIRONMENT' in secret_name:
                return 'pinecone', 'ENVIRONMENT'
            elif 'INDEX' in secret_name:
                return 'pinecone', 'INDEX_NAME'
            else:
                return 'pinecone', 'API_KEY'
        else:
            # Try to extract from name patterns
            parts = secret_name.split('_')
            if len(parts) >= 2:
                service = parts[0].lower()
                credential_type = '_'.join(parts[1:])
                return service, credential_type
            else:
                return 'unknown', 'UNKNOWN'

    def _generate_recommended_name(self, service: str, credential_type: str, current_name: str) -> str:
        """Generate standardized secret name."""
        # Special cases for known patterns
        if current_name in ['PULUMI_ACCESS_TOKEN', 'GITHUB_TOKEN', 'DOCKER_TOKEN']:
            return current_name  # Keep these as-is
            
        # Handle service mapping
        service_upper = service.upper()
        if service == 'lambda_labs':
            service_upper = 'LAMBDA_LABS'
        elif service == 'openai':
            service_upper = 'OPENAI'
        elif service == 'gong':
            service_upper = 'GONG'
        elif service == 'snowflake':
            service_upper = 'SNOWFLAKE'
        elif service == 'vercel':
            service_upper = 'VERCEL'
        elif service == 'slack':
            service_upper = 'SLACK'
        elif service == 'pinecone':
            service_upper = 'PINECONE'
            
        # Standardize credential type
        if credential_type in ['KEY', 'API_KEY', 'ACCESS_KEY']:
            cred_type = 'API_KEY'
        elif credential_type in ['TOKEN', 'ACCESS_TOKEN', 'BOT_TOKEN', 'APP_TOKEN']:
            cred_type = credential_type
        elif credential_type in ['SECRET', 'CLIENT_SECRET', 'SIGNING_SECRET']:
            cred_type = credential_type
        else:
            cred_type = credential_type
            
        return f"{service_upper}_{cred_type}"

    def _determine_action(self, secret_name: str, references: List[SecretReference]) -> str:
        """Determine what action is required for this secret."""
        if not references:
            return 'delete'  # No references found, likely unused
        
        github_refs = [r for r in references if r.usage_type == 'github_action']
        pulumi_refs = [r for r in references if r.usage_type == 'pulumi_esc']
        code_refs = [r for r in references if r.usage_type == 'code_reference']
        
        if github_refs and not pulumi_refs:
            return 'add_to_pulumi'  # In GitHub but not Pulumi sync
        elif pulumi_refs and not github_refs:
            return 'add_to_github'  # In Pulumi but not GitHub
        elif not github_refs and not pulumi_refs and code_refs:
            return 'add_to_both'  # Only in code, needs to be added
        elif len(references) < 3:
            return 'verify_usage'  # Low usage, verify if needed
        else:
            return 'keep'  # Well-used, keep

    def generate_report(self) -> Dict:
        """Generate comprehensive analysis report."""
        print("📋 Generating analysis report...")
        
        total_secrets = len(self.analysis_results)
        consistent_secrets = len([a for a in self.analysis_results if a.is_consistent])
        
        report = {
            'summary': {
                'total_secrets': total_secrets,
                'consistent_secrets': consistent_secrets,
                'consistency_rate': f"{(consistent_secrets / total_secrets * 100):.1f}%" if total_secrets > 0 else "0%",
                'github_secrets': len(self.github_secrets),
                'pulumi_esc_secrets': len(self.pulumi_esc_secrets),
                'code_references': len(self.code_references)
            },
            'actions_required': self._summarize_actions(),
            'services': self._summarize_services(),
            'detailed_analysis': [asdict(analysis) for analysis in self.analysis_results]
        }
        
        return report

    def _summarize_actions(self) -> Dict[str, List[str]]:
        """Summarize required actions for secrets."""
        actions: Dict[str, List[str]] = {}
        for analysis in self.analysis_results:
            action = analysis.action_required
            actions.setdefault(action, []).append(analysis.current_name)
        return actions

    def _summarize_services(self) -> Dict[str, List[str]]:
        """Summarize secrets by service."""
        services: Dict[str, List[str]] = {}
        for analysis in self.analysis_results:
            service = analysis.service
            services.setdefault(service, []).append(analysis.current_name)
        return services

    def generate_migration_plan(self) -> Dict:
        """Generate specific migration plan with commands."""
        print("🔄 Generating migration plan...")
        
        migration_steps = []
        
        # Step 1: Secrets to rename
        rename_secrets = [a for a in self.analysis_results if a.current_name != a.recommended_name and a.action_required == 'keep']
        if rename_secrets:
            migration_steps.append({
                'step': 'rename_secrets',
                'description': 'Rename secrets to follow standard naming convention',
                'secrets': [(a.current_name, a.recommended_name) for a in rename_secrets],
                'commands': [
                    f"# Rename {old} to {new}" for old, new in [(a.current_name, a.recommended_name) for a in rename_secrets]
                ]
            })
        
        # Step 2: Secrets to delete
        delete_secrets = [a for a in self.analysis_results if a.action_required == 'delete']
        if delete_secrets:
            migration_steps.append({
                'step': 'delete_unused_secrets',
                'description': 'Remove unused secrets',
                'secrets': [a.current_name for a in delete_secrets],
                'commands': [f"# Delete unused secret: {a.current_name}" for a in delete_secrets]
            })
        
        # Step 3: Add missing secrets
        add_to_github = [a for a in self.analysis_results if a.action_required == 'add_to_github']
        add_to_pulumi = [a for a in self.analysis_results if a.action_required == 'add_to_pulumi']
        
        if add_to_github:
            migration_steps.append({
                'step': 'add_to_github',
                'description': 'Add missing secrets to GitHub organization',
                'secrets': [a.current_name for a in add_to_github]
            })
            
        if add_to_pulumi:
            migration_steps.append({
                'step': 'add_to_pulumi',
                'description': 'Add missing secrets to Pulumi ESC sync',
                'secrets': [a.current_name for a in add_to_pulumi]
            })
        
        return {'migration_steps': migration_steps}

def main():
    """Main execution function."""
    print("🚀 Starting Sophia AI Secret Audit & Standardization")
    print("=" * 60)
    
    auditor = SecretAuditor()
    
    # Extract all secret references
    auditor.extract_github_secrets()
    auditor.extract_pulumi_esc_mappings()
    auditor.extract_code_references()
    
    # Analyze consistency
    auditor.analyze_secret_consistency()
    
    # Generate reports
    analysis_report = auditor.generate_report()
    migration_plan = auditor.generate_migration_plan()
    
    # Save reports
    with open('secret_analysis_report.json', 'w') as f:
        json.dump(analysis_report, f, indent=2)
        
    with open('secret_migration_plan.json', 'w') as f:
        json.dump(migration_plan, f, indent=2)
    
    # Print summary
    print("\n📊 ANALYSIS SUMMARY")
    print("-" * 30)
    print(f"Total secrets found: {analysis_report['summary']['total_secrets']}")
    print(f"Consistent naming: {analysis_report['summary']['consistent_secrets']}")
    print(f"Consistency rate: {analysis_report['summary']['consistency_rate']}")
    
    print("\n🔧 ACTIONS REQUIRED")
    print("-" * 30)
    for action, secrets in analysis_report['actions_required'].items():
        print(f"{action}: {len(secrets)} secrets")
        for secret in secrets[:5]:  # Show first 5
            print(f"  - {secret}")
        if len(secrets) > 5:
            print(f"  ... and {len(secrets) - 5} more")
    
    print("\n✅ Reports generated:")
    print("  - secret_analysis_report.json")
    print("  - secret_migration_plan.json")

if __name__ == "__main__":
    main() 