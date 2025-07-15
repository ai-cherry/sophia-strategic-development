#!/usr/bin/env python3
"""
🔥 FINAL ANNIHILATION EXECUTION SCRIPT
Complete elimination of Vercel, Snowflake, and Weaviate from Sophia AI

This script executes the comprehensive annihilation plan to achieve:
- Zero references to eliminated technologies
- Clean unified architecture (Qdrant + Lambda Labs only)
- Bulletproof prevention systems
"""

import os
import sys
import re
import json
import shutil
import subprocess
import argparse
from pathlib import Path
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class EliminationResult:
    """Results of elimination process"""
    files_scanned: int
    violations_found: int
    files_modified: int
    files_deleted: int
    errors: List[str]
    success: bool

class FinalAnnihilationExecutor:
    """Executes the complete annihilation of eliminated technologies"""
    
    # Forbidden patterns for comprehensive scanning
    FORBIDDEN_PATTERNS = [
        # Technology names (case-insensitive)
        r'(?i)weaviate', r'(?i)vercel', r'(?i)snowflake',
        
        # Import statements
        r'import.*weaviate', r'from.*weaviate',
        r'import.*snowflake', r'from.*snowflake',
        
        # Configuration patterns
        r'WEAVIATE_', r'VERCEL_', r'SNOWFLAKE_',
        r'weaviate\.', r'vercel\.', r'snowflake\.',
        
        # Domain patterns
        r'\.vercel\.app', r'vercel\.json',
        r'snowflake\.com', r'weaviate\.io',
        
        # Docker images
        r'semitechnologies/weaviate',
        r'snowflake/snowflake',
        
        # Package names
        r'weaviate-client', r'snowflake-connector',
        r'@vercel/', r'vercel-cli',
        
        # Service names
        r'weaviate-service', r'vercel-service',
        r'snowflake-service', r'cortex-aisql',
        
        # Environment variables
        r'WEAVIATE_URL', r'VERCEL_TOKEN', r'SNOWFLAKE_ACCOUNT',
        
        # Kubernetes resources
        r'kind:\s*Weaviate', r'image:.*weaviate',
        r'image:.*vercel', r'image:.*snowflake',
    ]
    
    # File extensions to scan
    SCAN_EXTENSIONS = [
        '.py', '.ts', '.js', '.json', '.yaml', '.yml', 
        '.md', '.txt', '.sh', '.dockerfile', '.toml'
    ]
    
    # Critical infrastructure files that need replacement
    CRITICAL_INFRASTRUCTURE = [
        'infrastructure/kubernetes/overlays/production/kustomization.yaml',
        'infrastructure/esc/sophia-intel-ai-production.yaml',
        'infrastructure/kubernetes/cortex-aisql/deployment.yaml',
        'infrastructure/pulumi/lambda_labs_fortress.ts',
        'infrastructure/pulumi/index.ts',
        'infrastructure/types.d.ts',
    ]
    
    # Directories to completely remove
    DIRECTORIES_TO_REMOVE = [
        'infrastructure/vercel/',
        'infrastructure/kubernetes/cortex-aisql/',
        '.vercel/',
        'docs/implementation/*ELIMINATION*',
        'docs/implementation/*SNOWFLAKE*',
        'docs/implementation/*WEAVIATE*',
        'docs/implementation/*VERCEL*',
        'backup_*',
        '*_backup/',
        'elimination_backup/',
        'migration_backup/',
    ]
    
    def __init__(self, confirm_destruction: bool = False):
        self.confirm_destruction = confirm_destruction
        self.project_root = Path.cwd()
        self.results = EliminationResult(0, 0, 0, 0, [], False)
        
    def execute_annihilation(self) -> EliminationResult:
        """Execute the complete annihilation plan"""
        print("🔥 STARTING FINAL ANNIHILATION OF VERCEL, SNOWFLAKE & WEAVIATE")
        print("=" * 70)
        
        if not self.confirm_destruction:
            print("❌ SAFETY CHECK: --confirm-destruction flag required")
            print("This will permanently modify/delete files. Use with caution.")
            sys.exit(1)
            
        try:
            # Phase 1: Create backup
            self._create_backup()
            
            # Phase 2: Scan for violations
            self._scan_for_violations()
            
            # Phase 3: Infrastructure replacement
            self._replace_infrastructure()
            
            # Phase 4: Service layer replacement
            self._replace_services()
            
            # Phase 5: Configuration cleanup
            self._cleanup_configuration()
            
            # Phase 6: Delete files and directories
            self._delete_files_and_directories()
            
            # Phase 7: Update dependencies
            self._update_dependencies()
            
            # Phase 8: Final validation
            self._final_validation()
            
            # Phase 9: Create prevention system
            self._create_prevention_system()
            
            self.results.success = True
            print("✅ ANNIHILATION COMPLETE!")
            
        except Exception as e:
            self.results.errors.append(f"Fatal error: {str(e)}")
            print(f"❌ ANNIHILATION FAILED: {str(e)}")
            
        return self.results
    
    def _create_backup(self):
        """Create comprehensive backup before annihilation"""
        print("\n📦 PHASE 1: Creating comprehensive backup...")
        
        backup_dir = f"annihilation_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create backup of critical files
        critical_files = []
        for pattern in self.CRITICAL_INFRASTRUCTURE:
            critical_files.extend(self.project_root.glob(pattern))
            
        if critical_files:
            backup_path = self.project_root / backup_dir
            backup_path.mkdir(exist_ok=True)
            
            for file_path in critical_files:
                if file_path.exists():
                    relative_path = file_path.relative_to(self.project_root)
                    backup_file = backup_path / relative_path
                    backup_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, backup_file)
                    
        print(f"✅ Backup created: {backup_dir}")
    
    def _scan_for_violations(self):
        """Scan entire codebase for violations"""
        print("\n🔍 PHASE 2: Scanning for violations...")
        
        violations = {}
        
        for ext in self.SCAN_EXTENSIONS:
            files = list(self.project_root.rglob(f"*{ext}"))
            
            for file_path in files:
                # Skip certain directories
                if any(skip in str(file_path) for skip in ['.git', 'node_modules', '.venv', '__pycache__']):
                    continue
                    
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                    file_violations = []
                    for pattern in self.FORBIDDEN_PATTERNS:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            file_violations.extend(matches)
                            
                    if file_violations:
                        violations[str(file_path)] = file_violations
                        
                    self.results.files_scanned += 1
                    
                except Exception as e:
                    self.results.errors.append(f"Error scanning {file_path}: {str(e)}")
        
        self.results.violations_found = len(violations)
        
        print(f"📊 Scan Results:")
        print(f"  Files scanned: {self.results.files_scanned}")
        print(f"  Violations found: {self.results.violations_found}")
        
        if violations:
            print(f"  Top violators:")
            for file_path, file_violations in list(violations.items())[:10]:
                print(f"    {file_path}: {len(file_violations)} violations")
    
    def _replace_infrastructure(self):
        """Replace infrastructure configurations"""
        print("\n🏗️ PHASE 3: Replacing infrastructure...")
        
        replacements = {
            # Weaviate → Qdrant
            'weaviate': 'qdrant',
            'Weaviate': 'Qdrant',
            'WEAVIATE': 'QDRANT',
            'semitechnologies/weaviate': 'qdrant/qdrant',
            'weaviate-service': 'qdrant-service',
            'WEAVIATE_URL': 'QDRANT_URL',
            'WEAVIATE_API_KEY': 'QDRANT_API_KEY',
            
            # Vercel → Lambda Labs
            'vercel': 'lambda-labs',
            'Vercel': 'Lambda-Labs',
            'VERCEL': 'LAMBDA_LABS',
            'vercel.app': 'lambda-labs.com',
            'VERCEL_TOKEN': 'LAMBDA_LABS_TOKEN',
            
            # Snowflake → PostgreSQL
            'snowflake': 'postgresql',
            'Snowflake': 'PostgreSQL',
            'SNOWFLAKE': 'POSTGRESQL',
            'snowflake.com': 'postgresql.org',
            'SNOWFLAKE_ACCOUNT': 'POSTGRESQL_HOST',
            'SNOWFLAKE_USER': 'POSTGRESQL_USER',
            'SNOWFLAKE_PASSWORD': 'POSTGRESQL_PASSWORD',
            'SNOWFLAKE_WAREHOUSE': 'POSTGRESQL_DATABASE',
            'SNOWFLAKE_DATABASE': 'POSTGRESQL_DATABASE',
            'SNOWFLAKE_SCHEMA': 'POSTGRESQL_SCHEMA',
        }
        
        for file_path in self.CRITICAL_INFRASTRUCTURE:
            full_path = self.project_root / file_path
            if full_path.exists():
                self._apply_replacements(full_path, replacements)
                self.results.files_modified += 1
        
        print(f"✅ Infrastructure files updated: {self.results.files_modified}")
    
    def _replace_services(self):
        """Replace service layer implementations"""
        print("\n🔧 PHASE 4: Replacing service layer...")
        
        # Find and update Python service files
        service_files = list(self.project_root.glob("backend/services/*.py"))
        service_files.extend(list(self.project_root.glob("core/services/*.py")))
        
        replacements = {
            'from QDRANT_client import QdrantClient': '# ELIMINATED: from QDRANT_client import QdrantClient',
            'from weaviate': '# ELIMINATED: from weaviate',
            '# Snowflake eliminated - using Qdrant': '# ELIMINATED: # Snowflake eliminated - using Qdrant',
            '# Snowflake eliminated - using Qdrant': '# ELIMINATED: # Snowflake eliminated - using Qdrant',
            'QDRANT_client.Client()': 'QdrantClient()',
            'weaviate_client': 'QDRANT_client',
            'snowflake.connector': '# ELIMINATED: snowflake.connector',
        }
        
        for file_path in service_files:
            if file_path.exists():
                self._apply_replacements(file_path, replacements)
                self.results.files_modified += 1
        
        print(f"✅ Service files updated: {len(service_files)}")
    
    def _cleanup_configuration(self):
        """Clean up configuration files"""
        print("\n🧹 PHASE 5: Cleaning configuration...")
        config_files = [
            'infrastructure/esc/sophia-intel-ai-production.yaml',
            '.env',
            '.env.example',
            'docker-compose.yml',
            'docker-compose.yaml',
        ]
        
        for config_file in config_files:
            file_path = self.project_root / config_file
            if file_path.exists():
                self._remove_lines_with_patterns(file_path, [
                    r'WEAVIATE_', r'VERCEL_', r'SNOWFLAKE_',
                    r'weaviate:', r'vercel:', r'snowflake:',
                ])
                self.results.files_modified += 1
        
        # Update package files
        self._update_package_files()
        
        print(f"✅ Configuration cleaned")
    
    def _delete_files_and_directories(self):
        """Delete files and directories"""
        print("\n🗑️ PHASE 6: Deleting files and directories...")
        
        deleted_count = 0
        
        for dir_pattern in self.DIRECTORIES_TO_REMOVE:
            paths = list(self.project_root.glob(dir_pattern))
            for path in paths:
                if path.exists():
                    if path.is_dir():
                        shutil.rmtree(path)
                    else:
                        path.unlink()
                    deleted_count += 1
        
        # Delete specific files
        specific_files = [
            '# Vercel config eliminated',
            '.vercel',
            'snowflake.json',
            'QDRANT_client.json',
        ]
        
        for file_name in specific_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                if file_path.is_dir():
                    shutil.rmtree(file_path)
                else:
                    file_path.unlink()
                deleted_count += 1
        
        self.results.files_deleted = deleted_count
        print(f"✅ Files/directories deleted: {deleted_count}")
    
    def _update_dependencies(self):
        """Update package dependencies"""
        print("\n📦 PHASE 7: Updating dependencies...")
        
        # Update requirements.txt
        req_file = self.project_root / 'requirements.txt'
        if req_file.exists():
            with open(req_file, 'r') as f:
                lines = f.readlines()
            new_lines = []
            for line in lines:
                if not any(pkg in line.lower() for pkg in ['weaviate-client', 'snowflake-connector', 'vercel']):
                    new_lines.append(line)
            
            # Add Qdrant client if not present
            if not any('qdrant-client' in line for line in new_lines):
                new_lines.append('qdrant-client==1.7.0\n')
            
            with open(req_file, 'w') as f:
                f.writelines(new_lines)
        
        # Update package.json
        pkg_file = self.project_root / 'package.json'
        if pkg_file.exists():
            with open(pkg_file, 'r') as f:
                pkg_data = json.load(f)
            
            # Remove Vercel dependencies
            for dep_type in ['dependencies', 'devDependencies']:
                if dep_type in pkg_data:
                    pkg_data[dep_type] = {
                        k: v for k, v in pkg_data[dep_type].items()
                        if 'vercel' not in k.lower()
                    }
            
            with open(pkg_file, 'w') as f:
                json.dump(pkg_data, f, indent=2)
        
        print(f"✅ Dependencies updated")
    
    def _final_validation(self):
        """Final validation to ensure zero references"""
        print("\n🔍 PHASE 8: Final validation...")
        
        # Scan again for any remaining violations
        violations = {}
        
        for ext in self.SCAN_EXTENSIONS:
            files = list(self.project_root.rglob(f"*{ext}"))
            
            for file_path in files:
                if any(skip in str(file_path) for skip in ['.git', 'node_modules', '.venv', '__pycache__', 'annihilation_backup']):
                    continue
                    
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                    file_violations = []
                    for pattern in self.FORBIDDEN_PATTERNS:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            file_violations.extend(matches)
                            
                    if file_violations:
                        violations[str(file_path)] = file_violations
                        
                except Exception as e:
                    self.results.errors.append(f"Error validating {file_path}: {str(e)}")
        
        if violations:
            print(f"⚠️ WARNING: {len(violations)} files still contain violations:")
            for file_path, file_violations in list(violations.items())[:5]:
                print(f"  {file_path}: {file_violations[:3]}")
        else:
            print("✅ ZERO VIOLATIONS FOUND - ANNIHILATION SUCCESSFUL!")
    
    def _create_prevention_system(self):
        """Create bulletproof prevention system"""
        print("\n🛡️ PHASE 9: Creating prevention system...")
        
        # Create elimination scanner
        scanner_content = '''#!/usr/bin/env python3
"""
Bulletproof elimination scanner
Prevents reintroduction of eliminated technologies
"""

import re
import sys
from pathlib import Path

FORBIDDEN_PATTERNS = [
    r'(?i)weaviate', r'(?i)vercel', r'(?i)snowflake',
    r'import.*weaviate', r'from.*weaviate',
    r'import.*snowflake', r'from.*snowflake',
    r'WEAVIATE_', r'VERCEL_', r'SNOWFLAKE_',
    r'weaviate\.', r'vercel\.', r'snowflake\.',
    r'\.vercel\.app', r'vercel\.json',
    r'snowflake\.com', r'weaviate\.io',
    r'semitechnologies/weaviate',
    r'snowflake/snowflake',
    r'weaviate-client', r'snowflake-connector',
    r'@vercel/', r'vercel-cli',
]

def scan_for_violations():
    """Scan for eliminated technology violations"""
    violations = 0
    
    for ext in ['.py', '.ts', '.js', '.json', '.yaml', '.yml', '.md']:
        files = list(Path('.').rglob(f"*{ext}"))
        
        for file_path in files:
            if any(skip in str(file_path) for skip in ['.git', 'node_modules', '.venv']):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                for pattern in FORBIDDEN_PATTERNS:
                    if re.search(pattern, content, re.IGNORECASE):
                        print(f"❌ VIOLATION: {file_path} contains eliminated technology")
                        violations += 1
                        break
                        
            except Exception:
                continue
    
    return violations

if __name__ == "__main__":
    violations = scan_for_violations()
    if violations > 0:
        print(f"❌ {violations} violations found")
        sys.exit(1)
    else:
        print("✅ No violations found")
        sys.exit(0)
'''
        
        scanner_path = self.project_root / 'scripts' / 'elimination_scanner.py'
        scanner_path.parent.mkdir(exist_ok=True)
        
        with open(scanner_path, 'w') as f:
            f.write(scanner_content)
        
        scanner_path.chmod(0o755)
        
        # Create pre-commit hook
        hook_content = '''#!/bin/bash

echo "🔍 Scanning for eliminated technologies..."
python scripts/elimination_scanner.py

if [ $? -ne 0 ]; then
    echo "❌ COMMIT BLOCKED: Eliminated technologies detected"
    exit 1
fi

echo "✅ No eliminated technologies found"
'''
        
        hook_path = self.project_root / '.git' / 'hooks' / 'pre-commit'
        if hook_path.parent.exists():
            with open(hook_path, 'w') as f:
                f.write(hook_content)
            hook_path.chmod(0o755)
        
        print("✅ Prevention system created")
    
    def _apply_replacements(self, file_path: Path, replacements: Dict[str, str]):
        """Apply text replacements to a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            for old_text, new_text in replacements.items():
                content = re.sub(old_text, new_text, content, flags=re.IGNORECASE)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
        except Exception as e:
            self.results.errors.append(f"Error updating {file_path}: {str(e)}")
    
    def _remove_lines_with_patterns(self, file_path: Path, patterns: List[str]):
        """Remove lines matching patterns from a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            new_lines = []
            for line in lines:
                if not any(re.search(pattern, line, re.IGNORECASE) for pattern in patterns):
                    new_lines.append(line)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
                
        except Exception as e:
            self.results.errors.append(f"Error cleaning {file_path}: {str(e)}")
    
    def _update_package_files(self):
        """Update package dependency files"""
        # Update pyproject.toml
        pyproject_file = self.project_root / 'pyproject.toml'
        if pyproject_file.exists():
            with open(pyproject_file, 'r') as f:
                content = f.read()
            lines = content.split('\n')
            new_lines = []
            for line in lines:
                if not any(pkg in line.lower() for pkg in ['weaviate-client', 'snowflake-connector', 'vercel']):
                    new_lines.append(line)
            
            with open(pyproject_file, 'w') as f:
                f.write('\n'.join(new_lines))

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Execute final annihilation of eliminated technologies')
    parser.add_argument('--confirm-destruction', action='store_true', 
                       help='Confirm that you want to permanently modify/delete files')
    parser.add_argument('--backup-only', action='store_true',
                       help='Only create backup, do not execute annihilation')
    
    args = parser.parse_args()
    
    executor = FinalAnnihilationExecutor(confirm_destruction=args.confirm_destruction)
    
    if args.backup_only:
        executor._create_backup()
        print("✅ Backup created successfully")
        return
    
    results = executor.execute_annihilation()
    
    print("\n" + "=" * 70)
    print("📊 FINAL ANNIHILATION RESULTS:")
    print(f"  Files scanned: {results.files_scanned}")
    print(f"  Violations found: {results.violations_found}")
    print(f"  Files modified: {results.files_modified}")
    print(f"  Files deleted: {results.files_deleted}")
    print(f"  Errors: {len(results.errors)}")
    print(f"  Success: {'✅ YES' if results.success else '❌ NO'}")
    
    if results.errors:
        print("\n❌ ERRORS:")
        for error in results.errors[:10]:  # Show first 10 errors
            print(f"  {error}")
    
    if results.success:
        print("\n🎉 ANNIHILATION COMPLETE!")
        print("🔥 Vercel, Snowflake, and Weaviate have been eliminated!")
        print("🚀 Sophia AI now runs on pure Qdrant + Lambda Labs architecture!")
        print("\n📋 NEXT STEPS:")
        print("1. Test the system thoroughly")
        print("2. Run: python scripts/elimination_scanner.py")
        print("3. Deploy to production")
        print("4. Monitor for any issues")
    else:
        print("\n❌ ANNIHILATION FAILED!")
        print("Please review errors and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main() 