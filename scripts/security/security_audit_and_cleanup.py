#!/usr/bin/env python3
"""
Comprehensive Security Audit and Cleanup Script for Sophia AI
Scans the entire codebase for exposed secrets, hardcoded credentials, and security issues
"""

import os
import re
import sys
import json
import logging
import subprocess
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class SecurityIssue:
    """Represents a security issue found in the codebase"""
    file_path: str
    line_number: int
    issue_type: str
    description: str
    severity: str
    line_content: str
    suggested_fix: Optional[str] = None

class SecurityAuditor:
    """Comprehensive security auditor for Sophia AI codebase"""
    
    # Patterns for detecting various types of secrets
    SECRET_PATTERNS = {
        'openai_api_key': [
            r'sk-[a-zA-Z0-9]{48}',
            r'sk-proj-[a-zA-Z0-9]{48}',
            r'sk-svcacct-[a-zA-Z0-9-_]{48,}'
        ],
        'anthropic_api_key': [
            r'sk-ant-api[0-9]{2}-[a-zA-Z0-9-_]{95}'
        ],
        'gong_api_key': [
            r'[A-Z0-9]{26}',  # Gong access keys are typically 26 characters
        ],
        'pinecone_api_key': [
            r'pcsk_[a-zA-Z0-9-_]{32,}'
        ],
        'snowflake_password': [
            r'eyJ[a-zA-Z0-9-_]+\.[a-zA-Z0-9-_]+\.[a-zA-Z0-9-_]+',  # JWT format
        ],
        'github_token': [
            r'ghp_[a-zA-Z0-9]{36}',
            r'gho_[a-zA-Z0-9]{36}',
            r'ghu_[a-zA-Z0-9]{36}',
            r'ghs_[a-zA-Z0-9]{36}',
            r'ghr_[a-zA-Z0-9]{36}'
        ],
        'pulumi_token': [
            r'pul-[a-f0-9]{40}'
        ],
        'generic_secret': [
            r'(?i)(password|secret|key|token)\s*[:=]\s*["\'][^"\']{20,}["\']',
            r'(?i)(api_key|access_key|secret_key)\s*[:=]\s*["\'][^"\']{20,}["\']'
        ]
    }
    
    # File patterns to exclude from scanning
    EXCLUDE_PATTERNS = [
        r'\.git/',
        r'__pycache__/',
        r'\.pyc$',
        r'node_modules/',
        r'\.venv/',
        r'venv/',
        r'\.env\.example$',
        r'\.env\.template$',
        r'\.md$',  # Markdown files (documentation)
        r'\.log$',
        r'\.backup$',
        r'\.bak$',
        r'/logs/',
        r'test_.*\.py$',  # Test files might have mock secrets
    ]
    
    # Files that should never contain secrets
    SENSITIVE_FILE_TYPES = [
        '.py', '.js', '.ts', '.jsx', '.tsx', '.json', '.yaml', '.yml', 
        '.env', '.conf', '.config', '.ini', '.toml'
    ]
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.issues: List[SecurityIssue] = []
        
    def scan_codebase(self) -> List[SecurityIssue]:
        """Scan the entire codebase for security issues"""
        logger.info("🔍 Starting comprehensive security audit...")
        
        # Get all files to scan
        files_to_scan = self._get_files_to_scan()
        logger.info(f"Scanning {len(files_to_scan)} files...")
        
        for file_path in files_to_scan:
            self._scan_file(file_path)
        
        # Additional checks
        self._check_git_history()
        self._check_environment_files()
        self._check_configuration_files()
        
        logger.info(f"🔍 Security audit complete. Found {len(self.issues)} issues.")
        return self.issues
    
    def _get_files_to_scan(self) -> List[Path]:
        """Get list of files to scan, excluding patterns"""
        files = []
        
        for root, dirs, filenames in os.walk(self.project_root):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not any(
                re.search(pattern, str(Path(root) / d))
                for pattern in self.EXCLUDE_PATTERNS
            )]
            
            for filename in filenames:
                file_path = Path(root) / filename
                relative_path = file_path.relative_to(self.project_root)
                
                # Skip excluded files
                if any(re.search(pattern, str(relative_path)) for pattern in self.EXCLUDE_PATTERNS):
                    continue
                
                # Only scan certain file types
                if file_path.suffix in self.SENSITIVE_FILE_TYPES:
                    files.append(file_path)
        
        return files
    
    def _scan_file(self, file_path: Path) -> None:
        """Scan a single file for security issues"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                self._check_line_for_secrets(file_path, line_num, line)
                self._check_line_for_patterns(file_path, line_num, line)
                
        except Exception as e:
            logger.warning(f"Failed to scan {file_path}: {e}")
    
    def _check_line_for_secrets(self, file_path: Path, line_num: int, line: str) -> None:
        """Check a line for potential secrets"""
        line_stripped = line.strip()
        
        for secret_type, patterns in self.SECRET_PATTERNS.items():
            for pattern in patterns:
                matches = re.finditer(pattern, line)
                for match in matches:
                    # Additional validation to avoid false positives
                    if self._is_likely_secret(secret_type, match.group()):
                        self.issues.append(SecurityIssue(
                            file_path=str(file_path.relative_to(self.project_root)),
                            line_number=line_num,
                            issue_type="exposed_secret",
                            description=f"Potential {secret_type} found",
                            severity="CRITICAL",
                            line_content=line_stripped,
                            suggested_fix=f"Replace with get_config_value('{secret_type}')"
                        ))
    
    def _check_line_for_patterns(self, file_path: Path, line_num: int, line: str) -> None:
        """Check line for other security patterns"""
        line_lower = line.lower()
        
        # Check for hardcoded URLs with credentials
        url_pattern = r'https?://[^:]+:[^@]+@[^/]+'
        if re.search(url_pattern, line):
            self.issues.append(SecurityIssue(
                file_path=str(file_path.relative_to(self.project_root)),
                line_number=line_num,
                issue_type="hardcoded_credentials",
                description="URL with embedded credentials",
                severity="HIGH",
                line_content=line.strip()
            ))
        
        # Check for hardcoded database connections
        if any(keyword in line_lower for keyword in ['password=', 'pwd=', 'passwd=']):
            if not line.strip().startswith('#'):  # Not a comment
                self.issues.append(SecurityIssue(
                    file_path=str(file_path.relative_to(self.project_root)),
                    line_number=line_num,
                    issue_type="hardcoded_password",
                    description="Hardcoded password in connection string",
                    severity="HIGH",
                    line_content=line.strip()
                ))
        
        # Check for insecure practices
        if 'verify=false' in line_lower or 'ssl_verify=false' in line_lower:
            self.issues.append(SecurityIssue(
                file_path=str(file_path.relative_to(self.project_root)),
                line_number=line_num,
                issue_type="insecure_ssl",
                description="SSL verification disabled",
                severity="MEDIUM",
                line_content=line.strip()
            ))
    
    def _is_likely_secret(self, secret_type: str, value: str) -> bool:
        """Additional validation to determine if a value is likely a real secret"""
        # Skip obvious test/placeholder values
        test_indicators = [
            'test', 'fake', 'mock', 'example', 'placeholder', 'dummy',
            'xxx', 'yyy', 'zzz', '123', 'abc', 'sample'
        ]
        
        value_lower = value.lower()
        if any(indicator in value_lower for indicator in test_indicators):
            return False
        
        # Check for patterns that indicate real secrets
        if secret_type == 'openai_api_key':
            return len(value) >= 48 and value.startswith('sk-')
        elif secret_type == 'anthropic_api_key':
            return len(value) >= 95 and value.startswith('sk-ant-')
        elif secret_type == 'gong_api_key':
            return len(value) == 26 and value.isupper()
        elif secret_type == 'pinecone_api_key':
            return len(value) >= 32 and value.startswith('pcsk_')
        elif secret_type == 'snowflake_password':
            return len(value) > 100 and '.' in value  # JWT format
        
        return True
    
    def _check_git_history(self) -> None:
        """Check git history for accidentally committed secrets"""
        logger.info("🔍 Checking git history for leaked secrets...")
        
        try:
            # Use git log to search for potential secrets in commit history
            result = subprocess.run([
                'git', 'log', '--all', '--full-history', '--grep=password',
                '--grep=secret', '--grep=key', '--grep=token', '--oneline'
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.stdout:
                commits = result.stdout.strip().split('\n')
                for commit in commits[:10]:  # Check last 10 matching commits
                    self.issues.append(SecurityIssue(
                        file_path="git_history",
                        line_number=0,
                        issue_type="git_history_leak",
                        description=f"Commit message contains sensitive keywords: {commit}",
                        severity="MEDIUM",
                        line_content=commit
                    ))
        except Exception as e:
            logger.warning(f"Failed to check git history: {e}")
    
    def _check_environment_files(self) -> None:
        """Check for problematic environment files"""
        env_files = [
            '.env', '.env.local', '.env.production', '.env.development',
            '.env.staging', '.env.test'
        ]
        
        for env_file in env_files:
            env_path = self.project_root / env_file
            if env_path.exists():
                self.issues.append(SecurityIssue(
                    file_path=env_file,
                    line_number=0,
                    issue_type="environment_file",
                    description=f"Environment file {env_file} found - should not be committed",
                    severity="HIGH",
                    line_content="",
                    suggested_fix=f"Add {env_file} to .gitignore and remove from git"
                ))
    
    def _check_configuration_files(self) -> None:
        """Check configuration files for security issues"""
        config_files = [
            'config.json', 'config.yaml', 'config.yml', 'secrets.json',
            'credentials.json', 'auth.json'
        ]
        
        for config_file in config_files:
            for config_path in self.project_root.rglob(config_file):
                if not any(exclude in str(config_path) for exclude in ['.git', 'node_modules', '__pycache__']):
                    self.issues.append(SecurityIssue(
                        file_path=str(config_path.relative_to(self.project_root)),
                        line_number=0,
                        issue_type="config_file",
                        description=f"Configuration file {config_file} may contain secrets",
                        severity="MEDIUM",
                        line_content=""
                    ))
    
    def generate_report(self) -> str:
        """Generate a comprehensive security report"""
        if not self.issues:
            return "✅ No security issues found!"
        
        # Group issues by severity
        critical_issues = [i for i in self.issues if i.severity == "CRITICAL"]
        high_issues = [i for i in self.issues if i.severity == "HIGH"]
        medium_issues = [i for i in self.issues if i.severity == "MEDIUM"]
        
        report = f"""
🔐 SOPHIA AI SECURITY AUDIT REPORT
{'='*60}

📊 SUMMARY:
   🔴 Critical Issues: {len(critical_issues)}
   🟠 High Issues: {len(high_issues)}
   🟡 Medium Issues: {len(medium_issues)}
   📋 Total Issues: {len(self.issues)}

"""
        
        if critical_issues:
            report += "\n🔴 CRITICAL ISSUES (IMMEDIATE ACTION REQUIRED):\n"
            report += "="*50 + "\n"
            for issue in critical_issues:
                report += f"File: {issue.file_path}:{issue.line_number}\n"
                report += f"Issue: {issue.description}\n"
                report += f"Content: {issue.line_content[:100]}...\n"
                if issue.suggested_fix:
                    report += f"Fix: {issue.suggested_fix}\n"
                report += "-" * 40 + "\n"
        
        if high_issues:
            report += "\n🟠 HIGH PRIORITY ISSUES:\n"
            report += "="*30 + "\n"
            for issue in high_issues:
                report += f"File: {issue.file_path}:{issue.line_number}\n"
                report += f"Issue: {issue.description}\n"
                report += f"Content: {issue.line_content[:100]}...\n"
                report += "-" * 40 + "\n"
        
        if medium_issues:
            report += "\n🟡 MEDIUM PRIORITY ISSUES:\n"
            report += "="*30 + "\n"
            for issue in medium_issues[:10]:  # Show first 10 medium issues
                report += f"File: {issue.file_path}:{issue.line_number}\n"
                report += f"Issue: {issue.description}\n"
                report += "-" * 40 + "\n"
            if len(medium_issues) > 10:
                report += f"... and {len(medium_issues) - 10} more medium issues\n"
        
        return report
    
    def fix_issues_automatically(self) -> int:
        """Automatically fix issues where possible"""
        fixed_count = 0
        
        for issue in self.issues:
            if issue.issue_type == "exposed_secret" and issue.suggested_fix:
                # This would require more sophisticated parsing to safely replace
                # For now, just log what should be fixed
                logger.warning(f"MANUAL FIX REQUIRED: {issue.file_path}:{issue.line_number}")
                logger.warning(f"  Replace: {issue.line_content.strip()}")
                logger.warning(f"  With: {issue.suggested_fix}")
        
        return fixed_count

def main():
    """Main function"""
    project_root = Path(__file__).parent.parent.parent
    
    logger.info("🚀 Starting Sophia AI Security Audit")
    logger.info("="*60)
    
    # Create auditor and scan
    auditor = SecurityAuditor(project_root)
    issues = auditor.scan_codebase()
    
    # Generate and display report
    report = auditor.generate_report()
    print(report)
    
    # Save report to file
    report_file = project_root / "SECURITY_AUDIT_REPORT.md"
    with open(report_file, 'w') as f:
        f.write(report)
    
    logger.info(f"📄 Security report saved to: {report_file}")
    
    # Check for critical issues
    critical_issues = [i for i in issues if i.severity == "CRITICAL"]
    if critical_issues:
        logger.error("🚨 CRITICAL SECURITY ISSUES FOUND!")
        logger.error("These must be fixed before deploying to production.")
        sys.exit(1)
    else:
        logger.info("✅ No critical security issues found.")
        
    # Check for high priority issues
    high_issues = [i for i in issues if i.severity == "HIGH"]
    if high_issues:
        logger.warning("⚠️  High priority security issues found.")
        logger.warning("These should be addressed soon.")
    
    return len(issues)

if __name__ == "__main__":
    issues_found = main() 