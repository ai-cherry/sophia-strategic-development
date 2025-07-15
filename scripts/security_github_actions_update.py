#!/usr/bin/env python3
"""
GitHub Actions Security Update Script
Updates GitHub Actions workflow dependencies to secure versions
"""

import os
import re
import yaml
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitHubActionsSecurityUpdater:
    def __init__(self):
        self.workflows_dir = Path('.github/workflows')
        
        # Secure action versions (updated July 2025)
        self.secure_actions = {
            'actions/checkout': 'v4',
            'actions/setup-python': 'v5',
            'actions/setup-node': 'v4',
            'actions/cache': 'v4',
            'actions/upload-artifact': 'v4',
            'actions/download-artifact': 'v4',
            'docker/setup-buildx-action': 'v3',
            'docker/build-push-action': 'v5',
            'docker/login-action': 'v3',
            'github/super-linter': 'v5',
            'codecov/codecov-action': 'v4',
            'peaceiris/actions-gh-pages': 'v3',
            'stefanzweifel/git-auto-commit-action': 'v5',
            'tj-actions/changed-files': 'v44',  # Updated from compromised version
            'pulumi/actions': 'v5',
            'azure/login': 'v2',
            'aws-actions/configure-aws-credentials': 'v4',
            'google-github-actions/auth': 'v2',
            'hashicorp/setup-terraform': 'v3',
            'ruby/setup-ruby': 'v1',
            'actions/setup-java': 'v4',
            'actions/setup-go': 'v5',
            'actions/setup-dotnet': 'v4'
        }
        
        self.deprecated_actions = {
            'actions/checkout@v2': 'actions/checkout@v4',
            'actions/checkout@v3': 'actions/checkout@v4',
            'actions/setup-python@v2': 'actions/setup-python@v5',
            'actions/setup-python@v3': 'actions/setup-python@v5',
            'actions/setup-python@v4': 'actions/setup-python@v5',
            'actions/setup-node@v2': 'actions/setup-node@v4',
            'actions/setup-node@v3': 'actions/setup-node@v4',
            'docker/build-push-action@v2': 'docker/build-push-action@v5',
            'docker/build-push-action@v3': 'docker/build-push-action@v5',
            'docker/build-push-action@v4': 'docker/build-push-action@v5',
            'tj-actions/changed-files@v35': 'tj-actions/changed-files@v44',  # Security fix
            'tj-actions/changed-files@v36': 'tj-actions/changed-files@v44',
            'tj-actions/changed-files@v37': 'tj-actions/changed-files@v44',
            'tj-actions/changed-files@v38': 'tj-actions/changed-files@v44',
            'tj-actions/changed-files@v39': 'tj-actions/changed-files@v44',
            'tj-actions/changed-files@v40': 'tj-actions/changed-files@v44',
            'tj-actions/changed-files@v41': 'tj-actions/changed-files@v44',
            'tj-actions/changed-files@v42': 'tj-actions/changed-files@v44',
            'tj-actions/changed-files@v43': 'tj-actions/changed-files@v44',
        }
        
        self.updated_files = []
        self.security_improvements = []
        
    def find_workflow_files(self) -> List[Path]:
        """Find all GitHub Actions workflow files"""
        if not self.workflows_dir.exists():
            logger.warning("No .github/workflows directory found")
            return []
            
        workflow_files = []
        for file in self.workflows_dir.glob('*.yml'):
            workflow_files.append(file)
        for file in self.workflows_dir.glob('*.yaml'):
            workflow_files.append(file)
            
        return workflow_files
    
    def analyze_workflow(self, workflow_path: Path) -> Dict[str, Any]:
        """Analyze a workflow file for security issues"""
        try:
            with open(workflow_path, 'r') as f:
                content = f.read()
                
            # Parse YAML
            try:
                workflow_data = yaml.safe_load(content)
            except yaml.YAMLError as e:
                logger.error(f"YAML parsing error in {workflow_path}: {e}")
                return None
                
            analysis = {
                'path': workflow_path,
                'actions_used': [],
                'security_issues': [],
                'recommendations': []
            }
            
            # Find all uses: statements
            uses_pattern = r'uses:\s*([^\s]+)'
            matches = re.findall(uses_pattern, content)
            
            for match in matches:
                action = match.strip()
                analysis['actions_used'].append(action)
                
                # Check for security issues
                if action in self.deprecated_actions:
                    analysis['security_issues'].append(f"Deprecated action: {action}")
                    analysis['recommendations'].append({
                        'current': action,
                        'recommended': self.deprecated_actions[action],
                        'reason': 'Security update - deprecated version'
                    })
                    
                # Check for tj-actions/changed-files vulnerability
                if 'tj-actions/changed-files' in action and not action.endswith('@v44'):
                    analysis['security_issues'].append(f"Vulnerable tj-actions/changed-files: {action}")
                    analysis['recommendations'].append({
                        'current': action,
                        'recommended': 'tj-actions/changed-files@v44',
                        'reason': 'CRITICAL: CVE-2025-30066 supply chain attack fix'
                    })
                    
                # Check for outdated versions
                action_name = action.split('@')[0] if '@' in action else action
                if action_name in self.secure_actions:
                    current_version = action.split('@')[1] if '@' in action else 'latest'
                    recommended_version = self.secure_actions[action_name]
                    
                    if current_version != recommended_version and current_version != 'latest':
                        analysis['recommendations'].append({
                            'current': action,
                            'recommended': f"{action_name}@{recommended_version}",
                            'reason': 'Security update available'
                        })
                        
            # Check for security best practices
            if workflow_data:
                jobs = workflow_data.get('jobs', {})
                for job_name, job_data in jobs.items():
                    steps = job_data.get('steps', [])
                    
                    # Check for hardcoded secrets
                    job_str = str(job_data)
                    if 'ghp_' in job_str or 'sk-' in job_str:
                        analysis['security_issues'].append(f"Possible hardcoded secret in job: {job_name}")
                        
                    # Check for shell injection risks
                    for step in steps:
                        if 'run' in step:
                            run_command = step['run']
                            if '${{' in run_command and 'github.event' in run_command:
                                analysis['security_issues'].append(f"Potential shell injection in job: {job_name}")
                                
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing {workflow_path}: {e}")
            return None
    
    def update_workflow(self, workflow_path: Path, analysis: Dict[str, Any]) -> bool:
        """Update a workflow file with secure actions"""
        try:
            with open(workflow_path, 'r') as f:
                content = f.read()
                
            original_content = content
            updated = False
            
            # Apply recommendations
            for rec in analysis['recommendations']:
                old_action = rec['current']
                new_action = rec['recommended']
                
                # Update uses: statements
                pattern = rf'uses:\s*{re.escape(old_action)}'
                replacement = f'uses: {new_action}'
                
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    updated = True
                    
                    self.security_improvements.append({
                        'file': str(workflow_path),
                        'change': f'{old_action} → {new_action}',
                        'reason': rec['reason']
                    })
                    
            # Add security improvements
            if 'permissions:' not in content and 'jobs:' in content:
                # Add minimal permissions
                permissions_block = """
# Security: Minimal permissions
permissions:
  contents: read
  actions: read
  checks: read

"""
                content = content.replace('jobs:', permissions_block + 'jobs:')
                updated = True
                
                self.security_improvements.append({
                    'file': str(workflow_path),
                    'change': 'Added minimal permissions',
                    'reason': 'Security best practice'
                })
                
            if updated:
                # Create backup
                backup_path = workflow_path.with_suffix('.backup')
                with open(backup_path, 'w') as f:
                    f.write(original_content)
                    
                # Write updated content
                with open(workflow_path, 'w') as f:
                    f.write(content)
                    
                self.updated_files.append(workflow_path)
                logger.info(f"✅ Updated {workflow_path}")
                return True
            else:
                logger.info(f"ℹ️  No updates needed for {workflow_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating {workflow_path}: {e}")
            return False
    
    def generate_security_report(self) -> Dict[str, Any]:
        """Generate GitHub Actions security report"""
        report = {
            'timestamp': '2025-07-14T20:15:00Z',
            'workflows_analyzed': len(self.find_workflow_files()),
            'workflows_updated': len(self.updated_files),
            'security_improvements': self.security_improvements,
            'updated_files': [str(f) for f in self.updated_files],
            'critical_fixes': [
                imp for imp in self.security_improvements 
                if 'CVE-2025-30066' in imp['reason']
            ],
            'recommendations': [
                "Test all workflows after updates",
                "Monitor GitHub Security Advisories",
                "Enable Dependabot for GitHub Actions",
                "Review workflow permissions regularly"
            ]
        }
        
        # Save report
        with open('github_actions_security_report.json', 'w') as f:
            json.dump(report, f, indent=2)
            
        return report
    
    def update_all_workflows(self) -> bool:
        """Main function to update all workflows"""
        logger.info("🔧 Starting GitHub Actions security update...")
        
        # Find all workflow files
        workflows = self.find_workflow_files()
        logger.info(f"📋 Found {len(workflows)} workflow file(s)")
        
        # Analyze and update each workflow
        for workflow in workflows:
            logger.info(f"🔍 Analyzing {workflow}")
            analysis = self.analyze_workflow(workflow)
            
            if analysis and (analysis['security_issues'] or analysis['recommendations']):
                logger.info(f"⚠️  Security issues found in {workflow}")
                for issue in analysis['security_issues']:
                    logger.info(f"   - {issue}")
                    
                self.update_workflow(workflow, analysis)
            else:
                logger.info(f"✅ {workflow} is secure")
                
        # Generate report
        report = self.generate_security_report()
        
        # Summary
        logger.info(f"📊 GitHub Actions Security Update Summary:")
        logger.info(f"   📂 Workflows analyzed: {report['workflows_analyzed']}")
        logger.info(f"   ✅ Workflows updated: {report['workflows_updated']}")
        logger.info(f"   🔒 Security improvements: {len(self.security_improvements)}")
        logger.info(f"   🚨 Critical fixes: {len(report['critical_fixes'])}")
        
        if self.security_improvements:
            logger.info("🔒 Security improvements applied:")
            for improvement in self.security_improvements:
                logger.info(f"   - {improvement['change']}")
                
        return len(self.security_improvements) > 0

def main():
    """Main entry point"""
    logger.info("🛡️ GitHub Actions Security Update for Sophia AI")
    
    updater = GitHubActionsSecurityUpdater()
    success = updater.update_all_workflows()
    
    if success:
        logger.info("✅ GitHub Actions security updates completed successfully!")
        logger.info("🔄 Next steps:")
        logger.info("   1. Test all workflows after updates")
        logger.info("   2. Enable Dependabot for GitHub Actions")
        logger.info("   3. Review workflow permissions")
        logger.info("   4. Monitor for security advisories")
    else:
        logger.info("ℹ️  No GitHub Actions security updates were needed")
        
    return success

if __name__ == "__main__":
    main() 