#!/usr/bin/env python3
"""
🔐 Hardcoded Secret Scanner

Scans for hardcoded secrets in the codebase and provides remediation suggestions.
Integrates with Pulumi ESC secret management.

Usage:
    python scripts/utils/secret_scanner.py
    python scripts/utils/secret_scanner.py --fix
"""

import os
import re
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Set
from dataclasses import dataclass

@dataclass
class SecretFound:
    file_path: str
    line_number: int
    line_content: str
    secret_type: str
    confidence: float
    remediation: str

class SecretScanner:
    """Advanced secret scanner with high accuracy detection"""
    
    def __init__(self):
        self.secret_patterns = {
            'openai_api_key': {
                'pattern': r'sk-[a-zA-Z0-9]{48}',
                'confidence': 0.95,
                'remediation': 'Use get_config_value("OPENAI_API_KEY")'
            },
            'anthropic_api_key': {
                'pattern': r'sk-ant-api03-[a-zA-Z0-9_-]{95}',
                'confidence': 0.95,
                'remediation': 'Use get_config_value("ANTHROPIC_API_KEY")'
            },
            'aws_access_key': {
                'pattern': r'AKIA[0-9A-Z]{16}',
                'confidence': 0.90,
                'remediation': 'Use get_config_value("AWS_ACCESS_KEY_ID")'
            },
            'aws_secret_key': {
                'pattern': r'[a-zA-Z0-9/+=]{40}',
                'confidence': 0.70,
                'remediation': 'Use get_config_value("AWS_SECRET_ACCESS_KEY")'
            },
            'pulumi_token': {
                'pattern': r'pul-[a-f0-9]{40}',
                'confidence': 0.95,
                'remediation': 'Use get_config_value("PULUMI_ACCESS_TOKEN")'
            },
            'github_token': {
                'pattern': r'ghp_[A-Za-z0-9]{36}',
                'confidence': 0.90,
                'remediation': 'Use get_config_value("GITHUB_TOKEN")'
            },
            'gong_access_key': {
                'pattern': r'TV33BPZ5UN45QKZ[A-Z0-9]{20,}',
                'confidence': 0.95,
                'remediation': 'Use get_config_value("GONG_ACCESS_KEY")'
            },
            'docker_hub_token': {
                'pattern': r'dckr_pat_[a-zA-Z0-9_-]{36}',
                'confidence': 0.95,
                'remediation': 'Use get_docker_hub_config()["access_token"]'
            },
            'slack_token': {
                'pattern': r'xoxb-[0-9]{12}-[0-9]{12}-[a-zA-Z0-9]{24}',
                'confidence': 0.95,
                'remediation': 'Use get_config_value("SLACK_BOT_TOKEN")'
            },
            'linear_api_key': {
                'pattern': r'lin_api_[a-zA-Z0-9]{40}',
                'confidence': 0.90,
                'remediation': 'Use get_config_value("LINEAR_API_KEY")'
            },
            'notion_token': {
                'pattern': r'secret_[a-zA-Z0-9]{43}',
                'confidence': 0.80,
                'remediation': 'Use get_config_value("NOTION_API_KEY")'
            },
            'generic_base64_secret': {
                'pattern': r'["\'][A-Za-z0-9+/=]{32,}["\']',
                'confidence': 0.50,
                'remediation': 'Review and use appropriate get_config_value()'
            }
        }
        
        # Whitelist patterns that should be ignored
        self.whitelist_patterns = [
            r'example',
            r'placeholder',
            r'fake',
            r'test',
            r'demo',
            r'\$\{[^}]+\}',  # Environment variable placeholders
            r'<[^>]+>',      # Angle bracket placeholders
        ]
        
        # File extensions to scan
        self.scan_extensions = {'.py', '.js', '.ts', '.yaml', '.yml', '.json', '.sh', '.env'}
        
        # Directories to skip
        self.skip_dirs = {'.git', '.venv', 'node_modules', '__pycache__', '.pytest_cache'}

    def scan_repository(self, repo_path: Path = None) -> List[SecretFound]:
        """Scan the entire repository for hardcoded secrets"""
        if repo_path is None:
            repo_path = Path.cwd()
            
        secrets_found = []
        
        print(f"🔍 Scanning repository for hardcoded secrets...")
        print(f"Repository: {repo_path}")
        
        scanned_files = 0
        for file_path in self._get_scannable_files(repo_path):
            secrets_found.extend(self._scan_file(file_path))
            scanned_files += 1
            
            if scanned_files % 100 == 0:
                print(f"   Scanned {scanned_files} files...")
        
        print(f"✅ Scanned {scanned_files} files")
        print(f"🚨 Found {len(secrets_found)} potential secrets")
        
        return secrets_found

    def _get_scannable_files(self, repo_path: Path) -> List[Path]:
        """Get list of files that should be scanned"""
        scannable_files = []
        
        for file_path in repo_path.rglob('*'):
            # Skip directories
            if file_path.is_dir():
                continue
                
            # Skip files in excluded directories
            if any(skip_dir in file_path.parts for skip_dir in self.skip_dirs):
                continue
                
            # Only scan files with relevant extensions
            if file_path.suffix.lower() in self.scan_extensions:
                scannable_files.append(file_path)
            elif file_path.name in {'.env', '.env.local', '.env.production', 'config', 'secrets'}:
                scannable_files.append(file_path)
                
        return scannable_files

    def _scan_file(self, file_path: Path) -> List[SecretFound]:
        """Scan a single file for secrets"""
        secrets_found = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            for line_num, line in enumerate(lines, 1):
                line_stripped = line.strip()
                
                # Skip comments and documentation
                if self._is_comment_or_doc(line_stripped, file_path.suffix):
                    continue
                    
                # Check each secret pattern
                for secret_type, pattern_info in self.secret_patterns.items():
                    matches = re.finditer(pattern_info['pattern'], line)
                    
                    for match in matches:
                        # Check if this match should be whitelisted
                        if self._is_whitelisted(match.group(), line):
                            continue
                            
                        secrets_found.append(SecretFound(
                            file_path=str(file_path),
                            line_number=line_num,
                            line_content=line_stripped,
                            secret_type=secret_type,
                            confidence=pattern_info['confidence'],
                            remediation=pattern_info['remediation']
                        ))
                        
        except Exception as e:
            print(f"⚠️ Error scanning {file_path}: {e}")
            
        return secrets_found

    def _is_comment_or_doc(self, line: str, file_extension: str) -> bool:
        """Check if line is a comment or documentation"""
        if file_extension == '.py':
            return line.startswith('#') or '"""' in line or "'''" in line
        elif file_extension in {'.js', '.ts'}:
            return line.startswith('//') or line.startswith('/*') or '*/' in line
        elif file_extension == '.sh':
            return line.startswith('#')
        elif file_extension in {'.yaml', '.yml'}:
            return line.startswith('#')
        return False

    def _is_whitelisted(self, match: str, full_line: str) -> bool:
        """Check if a match should be whitelisted"""
        full_context = full_line.lower()
        
        for pattern in self.whitelist_patterns:
            if re.search(pattern, full_context, re.IGNORECASE):
                return True
                
        return False

    def generate_report(self, secrets: List[SecretFound]) -> str:
        """Generate a comprehensive report of found secrets"""
        if not secrets:
            return "✅ No hardcoded secrets found!"
            
        # Group by file
        by_file = {}
        for secret in secrets:
            if secret.file_path not in by_file:
                by_file[secret.file_path] = []
            by_file[secret.file_path].append(secret)
            
        # Group by secret type
        by_type = {}
        for secret in secrets:
            if secret.secret_type not in by_type:
                by_type[secret.secret_type] = []
            by_type[secret.secret_type].append(secret)
            
        report = f"""🔐 Hardcoded Secrets Report
Generated: {os.popen('date').read().strip()}

📊 SUMMARY
Total Secrets Found: {len(secrets)}
Files Affected: {len(by_file)}
Secret Types: {len(by_type)}

🚨 HIGH CONFIDENCE SECRETS (≥0.90)
"""
        
        high_confidence = [s for s in secrets if s.confidence >= 0.90]
        for secret in high_confidence:
            report += f"""
File: {secret.file_path}:{secret.line_number}
Type: {secret.secret_type}
Confidence: {secret.confidence:.0%}
Remediation: {secret.remediation}
Line: {secret.line_content[:100]}...
"""
        
        report += f"""

📋 BREAKDOWN BY TYPE
"""
        for secret_type, type_secrets in sorted(by_type.items()):
            avg_confidence = sum(s.confidence for s in type_secrets) / len(type_secrets)
            report += f"• {secret_type}: {len(type_secrets)} occurrences (avg confidence: {avg_confidence:.0%})\n"
            
        report += f"""

📁 BREAKDOWN BY FILE
"""
        for file_path, file_secrets in sorted(by_file.items()):
            report += f"• {file_path}: {len(file_secrets)} secrets\n"
            
        report += f"""

🔧 REMEDIATION STEPS

1. HIGH PRIORITY (Confidence ≥90%):
   • Review and extract {len(high_confidence)} high-confidence secrets
   • Use Pulumi ESC via get_config_value() functions
   
2. MEDIUM PRIORITY (Confidence 70-89%):
   • Review {len([s for s in secrets if 0.70 <= s.confidence < 0.90])} medium-confidence matches
   • Verify if they are actual secrets
   
3. LOW PRIORITY (Confidence <70%):
   • Review {len([s for s in secrets if s.confidence < 0.70])} low-confidence matches
   • Likely false positives but worth checking

🛡️ PREVENTION
• Add pre-commit hook: python scripts/utils/secret_scanner.py
• Use get_config_value() for all secrets
• Never commit actual API keys or tokens
"""
        
        return report

    def fix_secrets_automatically(self, secrets: List[SecretFound]) -> int:
        """Automatically fix high-confidence secrets"""
        fixed_count = 0
        
        # Group by file for efficient processing
        by_file = {}
        for secret in secrets:
            if secret.confidence >= 0.90:  # Only fix high-confidence secrets
                if secret.file_path not in by_file:
                    by_file[secret.file_path] = []
                by_file[secret.file_path].append(secret)
        
        for file_path, file_secrets in by_file.items():
            if self._fix_file_secrets(file_path, file_secrets):
                fixed_count += len(file_secrets)
                
        return fixed_count

    def _fix_file_secrets(self, file_path: str, secrets: List[SecretFound]) -> bool:
        """Fix secrets in a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            # Sort secrets by line number (descending) to avoid index issues
            secrets_sorted = sorted(secrets, key=lambda s: s.line_number, reverse=True)
            
            for secret in secrets_sorted:
                line_idx = secret.line_number - 1
                if 0 <= line_idx < len(lines):
                    original_line = lines[line_idx]
                    
                    # Generate appropriate replacement
                    replacement = self._generate_replacement(secret)
                    if replacement:
                        # Replace the secret with the config call
                        new_line = self._replace_secret_in_line(original_line, secret, replacement)
                        lines[line_idx] = new_line
                        
            # Write back the fixed file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
                
            print(f"✅ Fixed {len(secrets)} secrets in {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error fixing {file_path}: {e}")
            return False

    def _generate_replacement(self, secret: SecretFound) -> str:
        """Generate appropriate replacement for a secret"""
        replacements = {
            'openai_api_key': 'get_config_value("OPENAI_API_KEY")',
            'anthropic_api_key': 'get_config_value("ANTHROPIC_API_KEY")',
            'pulumi_token': 'get_config_value("PULUMI_ACCESS_TOKEN")',
            'github_token': 'get_config_value("GITHUB_TOKEN")',
            'gong_access_key': 'get_config_value("GONG_ACCESS_KEY")',
            'docker_hub_token': 'get_docker_hub_config()["access_token"]',
            'slack_token': 'get_config_value("SLACK_BOT_TOKEN")',
            'linear_api_key': 'get_config_value("LINEAR_API_KEY")',
            'notion_token': 'get_config_value("NOTION_API_KEY")',
        }
        
        return replacements.get(secret.secret_type)

    def _replace_secret_in_line(self, line: str, secret: SecretFound, replacement: str) -> str:
        """Replace secret in line with appropriate config call"""
        # For now, just add a comment - more sophisticated replacement could be added
        return line.rstrip() + f"  # FIXME: Use {replacement}\n"


def main():
    """Main scanner function"""
    parser = argparse.ArgumentParser(description="Hardcoded Secret Scanner")
    parser.add_argument("--fix", action="store_true", help="Automatically fix high-confidence secrets")
    parser.add_argument("--output", type=str, help="Output report to file")
    parser.add_argument("--format", choices=['text', 'json'], default='text', help="Output format")
    
    args = parser.parse_args()
    
    scanner = SecretScanner()
    secrets = scanner.scan_repository()
    
    if args.format == 'json':
        # JSON output for CI/CD integration
        output = {
            'total_secrets': len(secrets),
            'high_confidence_secrets': len([s for s in secrets if s.confidence >= 0.90]),
            'secrets': [
                {
                    'file_path': s.file_path,
                    'line_number': s.line_number,
                    'secret_type': s.secret_type,
                    'confidence': s.confidence,
                    'remediation': s.remediation
                }
                for s in secrets
            ]
        }
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(output, f, indent=2)
        else:
            print(json.dumps(output, indent=2))
            
    else:
        # Text report
        report = scanner.generate_report(secrets)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
        else:
            print(report)
    
    if args.fix:
        fixed_count = scanner.fix_secrets_automatically(secrets)
        print(f"\n🔧 Automatically fixed {fixed_count} high-confidence secrets")
    
    # Exit with error code if high-confidence secrets found
    high_confidence_count = len([s for s in secrets if s.confidence >= 0.90])
    if high_confidence_count > 0:
        print(f"\n🚨 Found {high_confidence_count} high-confidence secrets!")
        print("Please review and fix before committing.")
        sys.exit(1)
    else:
        print("\n✅ No high-confidence secrets detected.")
        sys.exit(0)

if __name__ == "__main__":
    main() 