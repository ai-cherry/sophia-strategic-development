#!/usr/bin/env python3
"""
Sophia AI - Secret Standardization Implementation
Executes the migration plan from secret audit results
"""

import json
import re
from pathlib import Path
from typing import Dict, List

class SecretStandardizer:
    """Implements secret standardization based on audit results."""
    
    def __init__(self):
        self.workspace_root = Path.cwd()
        self.migration_plan = self._load_migration_plan()
        self.analysis_report = self._load_analysis_report()
        
    def _load_migration_plan(self) -> Dict:
        """Load the migration plan from audit results."""
        plan_file = self.workspace_root / 'secret_migration_plan.json'
        if not plan_file.exists():
            raise FileNotFoundError("Run secret audit first: python scripts/audit_secret_naming.py")
        
        with open(plan_file, 'r') as f:
            return json.load(f)
    
    def _load_analysis_report(self) -> Dict:
        """Load the analysis report from audit results."""
        report_file = self.workspace_root / 'secret_analysis_report.json'
        if not report_file.exists():
            raise FileNotFoundError("Run secret audit first: python scripts/audit_secret_naming.py")
        
        with open(report_file, 'r') as f:
            return json.load(f)

    def generate_cleanup_list(self) -> Dict:
        """Generate prioritized cleanup list based on audit results."""
        
        # Priority 1: Critical secrets that are actively used
        keep_secrets = self.analysis_report['actions_required'].get('keep', [])
        critical_secrets = [
            'OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GONG_ACCESS_KEY', 'GONG_CLIENT_SECRET',
            'SNOWFLAKE_ACCOUNT', 'SNOWFLAKE_USER', 'SNOWFLAKE_PASSWORD', 'SNOWFLAKE_ROLE',
            'SLACK_BOT_TOKEN', 'SLACK_APP_TOKEN', 'VERCEL_ACCESS_TOKEN', 'VERCEL_ORG_ID',
            'PINECONE_API_KEY', 'PINECONE_ENVIRONMENT', 'LAMBDA_LABS_API_KEY',
            'HUBSPOT_ACCESS_TOKEN', 'LINEAR_API_KEY', 'PULUMI_ACCESS_TOKEN'
        ]
        
        # Priority 2: Secrets that need Pulumi ESC integration
        add_to_pulumi = self.analysis_report['actions_required'].get('add_to_pulumi', [])
        
        # Priority 3: Secrets that need verification
        verify_usage = self.analysis_report['actions_required'].get('verify_usage', [])
        
        # Priority 4: Secrets to delete (unused)
        delete_candidates = self.analysis_report['actions_required'].get('add_to_both', [])
        
        cleanup_plan = {
            'phase_1_critical': {
                'description': 'Keep and standardize critical production secrets',
                'secrets': [s for s in critical_secrets if s in keep_secrets],
                'action': 'standardize_naming'
            },
            'phase_2_integrate': {
                'description': 'Add missing secrets to Pulumi ESC sync',
                'secrets': add_to_pulumi[:20],  # Top 20 priority
                'action': 'add_to_pulumi_esc'
            },
            'phase_3_verify': {
                'description': 'Verify usage and decide on these secrets',
                'secrets': verify_usage,
                'action': 'manual_verification'
            },
            'phase_4_cleanup': {
                'description': 'Delete unused/orphaned secrets',
                'secrets': [s for s in delete_candidates if not any(critical in s for critical in 
                          ['OPENAI', 'GONG', 'SNOWFLAKE', 'SLACK', 'VERCEL', 'PINECONE'])],
                'action': 'delete_unused'
            }
        }
        
        return cleanup_plan

    def update_pulumi_esc_sync(self, secrets_to_add: List[str]) -> None:
        """Update Pulumi ESC sync script with new secret mappings."""
        sync_script_path = self.workspace_root / 'scripts' / 'ci' / 'sync_from_gh_to_pulumi.py'
        
        if not sync_script_path.exists():
            print("❌ Pulumi sync script not found")
            return
        
        with open(sync_script_path, 'r') as f:
            content = f.read()
        
        # Find the secret_mappings dictionary
        mappings_start = content.find('self.secret_mappings = {')
        if mappings_start == -1:
            print("❌ Could not find secret_mappings in sync script")
            return
        
        # Extract existing mappings
        mappings_end = content.find('        }', mappings_start)
        content[mappings_start:mappings_end + 9]
        
        # Generate new mappings
        new_mappings = []
        for secret in secrets_to_add:
            if 'GONG' in secret and 'SECRET' in secret:
                pulumi_path = "values.sophia.business.gong.client_secret"
            elif 'GONG' in secret:
                pulumi_path = "values.sophia.business.gong.access_key"
            elif 'SNOWFLAKE' in secret and 'PASSWORD' in secret:
                pulumi_path = "values.sophia.data.snowflake.password"
            elif 'SNOWFLAKE' in secret and 'ACCOUNT' in secret:
                pulumi_path = "values.sophia.data.snowflake.account"
            elif 'VERCEL' in secret and 'PROJECT' in secret:
                pulumi_path = "values.sophia.infrastructure.vercel.project_id"
            else:
                # Default mapping pattern
                service = secret.split('_')[0].lower()
                pulumi_path = f"values.sophia.{service}.{secret.lower()}"
            
            new_mappings.append(f'            "{secret}": "{pulumi_path}",')
        
        # Insert new mappings before the closing brace
        if new_mappings:
            insertion_point = mappings_end
            new_content = (content[:insertion_point] + 
                          '\n            # Added by standardization script\n' +
                          '\n'.join(new_mappings) + '\n' +
                          content[insertion_point:])
            
            # Write back to file
            with open(sync_script_path, 'w') as f:
                f.write(new_content)
            
            print(f"✅ Added {len(new_mappings)} new secret mappings to Pulumi ESC sync")

    def generate_github_actions_cleanup(self) -> Dict:
        """Generate GitHub Actions workflow cleanup recommendations."""
        workflow_dir = self.workspace_root / '.github' / 'workflows'
        workflows = list(workflow_dir.glob('*.yml'))
        
        # Analyze workflow complexity and duplication
        workflow_analysis = {}
        secret_usage = {}
        
        for workflow_file in workflows:
            with open(workflow_file, 'r') as f:
                content = f.read()
            
            # Count secrets usage
            secret_matches = re.findall(r'secrets\.([A-Z_]+)', content)
            for secret in secret_matches:
                if secret not in secret_usage:
                    secret_usage[secret] = []
                secret_usage[secret].append(workflow_file.name)
            
            # Analyze workflow complexity
            lines = len(content.split('\n'))
            jobs = len(re.findall(r'^  [a-z-]+:', content, re.MULTILINE))
            
            workflow_analysis[workflow_file.name] = {
                'lines': lines,
                'jobs': jobs,
                'secrets_used': len(set(secret_matches)),
                'complexity_score': lines + (jobs * 50) + (len(set(secret_matches)) * 10)
            }
        
        # Generate recommendations
        cleanup_recommendations = {
            'high_complexity_workflows': [
                name for name, data in workflow_analysis.items() 
                if data['complexity_score'] > 1000
            ],
            'duplicate_secret_patterns': {
                secret: files for secret, files in secret_usage.items() 
                if len(files) > 3
            },
            'consolidation_candidates': [
                name for name, data in workflow_analysis.items()
                if data['jobs'] > 5 or data['lines'] > 500
            ]
        }
        
        return cleanup_recommendations

    def create_standardization_report(self) -> None:
        """Create comprehensive standardization report."""
        cleanup_plan = self.generate_cleanup_list()
        github_cleanup = self.generate_github_actions_cleanup()
        
        report = {
            'secret_standardization_plan': cleanup_plan,
            'github_actions_cleanup': github_cleanup,
            'implementation_steps': [
                {
                    'phase': 'Phase 1: Critical Secrets',
                    'duration': '2 days',
                    'tasks': [
                        'Verify all critical production secrets exist',
                        'Standardize naming for core secrets',
                        'Update Pulumi ESC mappings',
                        'Test secret synchronization'
                    ]
                },
                {
                    'phase': 'Phase 2: Integration',
                    'duration': '1 day',
                    'tasks': [
                        'Add missing secrets to Pulumi ESC sync',
                        'Update workflow references',
                        'Test integration pipeline'
                    ]
                },
                {
                    'phase': 'Phase 3: Verification',
                    'duration': '1 day',
                    'tasks': [
                        'Manual review of low-usage secrets',
                        'Confirm deletion candidates',
                        'Document decision rationale'
                    ]
                },
                {
                    'phase': 'Phase 4: Cleanup',
                    'duration': '1 day',
                    'tasks': [
                        'Remove unused secrets from GitHub',
                        'Clean up orphaned references',
                        'Final validation'
                    ]
                }
            ]
        }
        
        # Save report
        with open('secret_standardization_plan.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print("📋 Standardization Report Generated")
        print("=" * 40)
        
        for phase_name, phase_data in cleanup_plan.items():
            print(f"\n{phase_name.upper()}:")
            print(f"  {phase_data['description']}")
            print(f"  Secrets: {len(phase_data['secrets'])}")
            print(f"  Action: {phase_data['action']}")
        
        print("\n🔧 GITHUB ACTIONS CLEANUP:")
        print(f"  High complexity workflows: {len(github_cleanup['high_complexity_workflows'])}")
        print(f"  Consolidation candidates: {len(github_cleanup['consolidation_candidates'])}")
        
        print("\n✅ Full report saved to: secret_standardization_plan.json")

def main():
    """Main execution function."""
    print("🔧 Sophia AI Secret Standardization Implementation")
    print("=" * 50)
    
    try:
        standardizer = SecretStandardizer()
        standardizer.create_standardization_report()
        
        # Get user input for next steps
        print("\n🤔 Ready to proceed with standardization?")
        print("1. Update Pulumi ESC sync script")
        print("2. Generate GitHub Actions templates")
        print("3. Exit")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == '1':
            cleanup_plan = standardizer.generate_cleanup_list()
            secrets_to_add = cleanup_plan['phase_2_integrate']['secrets']
            standardizer.update_pulumi_esc_sync(secrets_to_add)
        elif choice == '2':
            print("🚧 GitHub Actions template generation coming in Phase 5")
        else:
            print("👋 Exiting. Run again when ready to implement changes.")
            
    except FileNotFoundError as e:
        print(f"❌ {e}")
        print("Please run secret audit first: python scripts/audit_secret_naming.py")

if __name__ == "__main__":
    main() 