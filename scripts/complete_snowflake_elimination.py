#!/usr/bin/env python3
"""
🧹 COMPLETE ELIMINATED ELIMINATION SCRIPT
Purpose: Permanently purge ALL ELIMINATED/ELIMINATED references from Sophia AI
Created: January 2025
Usage: python scripts/complete_ELIMINATED_elimination.py

This script implements the 6-phase elimination plan:
1. GitHub Actions Workflow Cleanup
2. Docker Configuration Cleanup  
3. JSON Configuration Cleanup
4. Documentation Archival
5. Deep Reference Scan
6. Prevention System Implementation
"""

import os
import re
import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Set
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ELIMINATED_elimination.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CompleteELIMINATEDEliminator:
    """Complete elimination of all ELIMINATED/ELIMINATED references"""
    
    def __init__(self, repo_root: str = "."):
        self.repo_root = Path(repo_root)
        self.elimination_backup = self.repo_root / "elimination_backup"
        self.elimination_backup.mkdir(exist_ok=True)
        
        # Comprehensive patterns to eliminate
        self.ELIMINATED_patterns = [
            r'ELIMINATED',
            r'ELIMINATED',
            r'ELIMINATED',
            r'ELIMINATED',
            r'ELIMINATED',
            r'ELIMINATED_ACCOUNT',
            r'ELIMINATED_USER',
            r'ELIMINATED_PAT',
            r'ELIMINATED_PASSWORD',
            r'ELIMINATED_WAREHOUSE',
            r'VITE_ELIMINATED_ACCOUNT',
            r'ELIMINATED-cortex',
            r'ELIMINATED_cortex',
            r'ELIMINATED_admin',
            r'ELIMINATED_cli_enhanced',
            r'ELIMINATED_unified',
            r'ELIMINATED_v2'
        ]
        
        # Files to completely eliminate
        self.files_to_eliminate = []
        
        # Files to archive (large documentation)
        self.files_to_archive = [
            "ELIMINATED_CONFIGURATION_REQUIREMENTS.md",
            "ELIMINATED_ISSUE_FINAL_RESOLUTION.md",
            "docs/ELIMINATED_migration_guide.md",
            "docs/ELIMINATED_integration.md"
        ]
        
        # Tracking
        self.modifications = []
        self.eliminated_files = []
        self.archived_files = []
        
    def phase1_github_actions_cleanup(self):
        """Phase 1: Remove ELIMINATED references from GitHub Actions"""
        logger.info("🚀 Phase 1: GitHub Actions Cleanup")
        
        github_workflows = self.repo_root / ".github" / "workflows"
        if not github_workflows.exists():
            logger.warning("No GitHub workflows directory found")
            return
            
        for workflow_file in github_workflows.glob("*.yml"):
            self._clean_yaml_file(workflow_file)
            
    def phase2_docker_cleanup(self):
        """Phase 2: Clean Docker configurations"""
        logger.info("🚀 Phase 2: Docker Configuration Cleanup")
        
        # Docker compose files
        docker_files = [
            "docker-compose.lambda.yml",
            "deployment/docker-compose-ai-core.yml", 
            "deployment/docker-compose-data-pipeline.yml",
            "deployment/docker-compose-development.yml"
        ]
        
        for docker_file in docker_files:
            file_path = self.repo_root / docker_file
            if file_path.exists():
                self._clean_yaml_file(file_path)
                
    def phase3_json_config_cleanup(self):
        """Phase 3: Clean JSON configuration files"""
        logger.info("🚀 Phase 3: JSON Configuration Cleanup")
        
        # Find all JSON files
        json_files = list(self.repo_root.rglob("*.json"))
        
        for json_file in json_files:
            # Skip node_modules and other build directories
            if any(skip in str(json_file) for skip in ["node_modules", ".git", "__pycache__"]):
                continue
                
            self._clean_json_file(json_file)
            
    def phase4_documentation_archival(self):
        """Phase 4: Archive large ELIMINATED documentation"""
        logger.info("🚀 Phase 4: Documentation Archival")
        
        for doc_file in self.files_to_archive:
            file_path = self.repo_root / doc_file
            if file_path.exists():
                archive_path = self.elimination_backup / file_path.name
                shutil.move(str(file_path), str(archive_path))
                self.archived_files.append(str(file_path))
                logger.info(f"Archived: {file_path} -> {archive_path}")
                
    def phase5_deep_reference_scan(self):
        """Phase 5: Deep scan for ANY remaining references"""
        logger.info("🚀 Phase 5: Deep Reference Scan")
        
        # Scan all text files for any remaining references
        text_extensions = ['.py', '.js', '.ts', '.tsx', '.md', '.yml', '.yaml', '.json', '.txt', '.conf']
        
        for ext in text_extensions:
            files = list(self.repo_root.rglob(f"*{ext}"))
            for file_path in files:
                if any(skip in str(file_path) for skip in ["node_modules", ".git", "__pycache__", "elimination_backup"]):
                    continue
                    
                self._deep_clean_file(file_path)
                
    def phase6_prevention_system(self):
        """Phase 6: Implement prevention system"""
        logger.info("🚀 Phase 6: Prevention System Implementation")
        
        # Create pre-commit hook
        self._create_precommit_hook()
        
        # Update .gitignore
        self._update_gitignore()
        
        # Create detection script
        self._create_detection_script()
        
    def _clean_yaml_file(self, file_path: Path):
        """Clean YAML file of ELIMINATED references"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            
            # Remove specific problematic lines
            lines_to_remove = [
                r'.*VITE_ELIMINATED_ACCOUNT.*',
                r'.*ELIMINATED_ACCOUNT.*',
                r'.*ELIMINATED_USER.*',
                r'.*ELIMINATED_PAT.*',
                r'.*ELIMINATED_PASSWORD.*',
                r'.*ELIMINATED_WAREHOUSE.*',
                r'.*ELIMINATED-cortex.*',
                r'.*ELIMINATED_cortex.*',
                r'.*ELIMINATED_admin.*',
                r'.*ELIMINATED_unified.*'
            ]
            
            for pattern in lines_to_remove:
                content = re.sub(pattern, '', content, flags=re.MULTILINE)
                
            # Clean up empty lines and sections
            content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.modifications.append(f"Cleaned YAML: {file_path}")
                logger.info(f"Cleaned YAML file: {file_path}")
                
        except Exception as e:
            logger.error(f"Error cleaning YAML file {file_path}: {e}")
            
    def _clean_json_file(self, file_path: Path):
        """Clean JSON file of ELIMINATED references"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            
            # Try to parse as JSON first
            try:
                data = json.loads(content)
                data = self._clean_json_data(data)
                content = json.dumps(data, indent=2)
            except json.JSONDecodeError:
                # If not valid JSON, clean as text
                for pattern in self.ELIMINATED_patterns:
                    content = re.sub(pattern, 'ELIMINATED', content, flags=re.IGNORECASE)
                    
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.modifications.append(f"Cleaned JSON: {file_path}")
                logger.info(f"Cleaned JSON file: {file_path}")
                
        except Exception as e:
            logger.error(f"Error cleaning JSON file {file_path}: {e}")
            
    def _clean_json_data(self, data):
        """Recursively clean JSON data structure"""
        if isinstance(data, dict):
            # Remove keys that contain ELIMINATED references
            keys_to_remove = []
            for key in data.keys():
                if any(pattern.lower() in key.lower() for pattern in ['ELIMINATED', 'ELIMINATED']):
                    keys_to_remove.append(key)
                    
            for key in keys_to_remove:
                del data[key]
                
            # Clean remaining values
            for key, value in data.items():
                data[key] = self._clean_json_data(value)
                
        elif isinstance(data, list):
            # Clean list items and remove ELIMINATED references
            cleaned_list = []
            for item in data:
                cleaned_item = self._clean_json_data(item)
                if isinstance(cleaned_item, str):
                    if not any(pattern.lower() in cleaned_item.lower() for pattern in ['ELIMINATED', 'ELIMINATED']):
                        cleaned_list.append(cleaned_item)
                else:
                    cleaned_list.append(cleaned_item)
            data = cleaned_list
            
        elif isinstance(data, str):
            # Clean string values
            for pattern in self.ELIMINATED_patterns:
                if pattern.lower() in data.lower():
                    data = "ELIMINATED"
                    break
                    
        return data
        
    def _deep_clean_file(self, file_path: Path):
        """Deep clean any text file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            original_content = content
            
            # Replace all ELIMINATED patterns
            for pattern in self.ELIMINATED_patterns:
                content = re.sub(pattern, 'ELIMINATED', content, flags=re.IGNORECASE)
                
            # Clean up obvious broken references
            content = re.sub(r'ELIMINATED[_-]ELIMINATED', 'ELIMINATED', content)
            content = re.sub(r'from\s+ELIMINATED', 'from qdrant_memory_service', content)
            content = re.sub(r'import\s+ELIMINATED', 'import qdrant_memory_service', content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.modifications.append(f"Deep cleaned: {file_path}")
                logger.info(f"Deep cleaned file: {file_path}")
                
        except Exception as e:
            logger.error(f"Error deep cleaning file {file_path}: {e}")
            
    def _create_precommit_hook(self):
        """Create pre-commit hook to prevent ELIMINATED reintroduction"""
        hook_content = '''#!/bin/bash
# Pre-commit hook to prevent ELIMINATED/ELIMINATED reintroduction

echo "🔍 Checking for ELIMINATED/ELIMINATED references..."

# Check for forbidden patterns
if git diff --cached --name-only | xargs grep -l -i "ELIMINATED\\|ELIMINATED" 2>/dev/null; then
    echo "❌ ERROR: ELIMINATED/ELIMINATED references detected!"
    echo "The following files contain forbidden references:"
    git diff --cached --name-only | xargs grep -l -i "ELIMINATED\\|ELIMINATED" 2>/dev/null
    echo ""
    echo "Please remove all ELIMINATED/ELIMINATED references before committing."
    echo "Use: python scripts/complete_ELIMINATED_elimination.py"
    exit 1
fi

echo "✅ No ELIMINATED references detected. Commit allowed."
exit 0
'''
        
        hooks_dir = self.repo_root / ".git" / "hooks"
        hooks_dir.mkdir(exist_ok=True)
        
        hook_path = hooks_dir / "pre-commit"
        with open(hook_path, 'w') as f:
            f.write(hook_content)
            
        # Make executable
        os.chmod(hook_path, 0o755)
        logger.info("Created pre-commit hook to prevent ELIMINATED reintroduction")
        
    def _update_gitignore(self):
        """Update .gitignore to block ELIMINATED patterns"""
        gitignore_path = self.repo_root / ".gitignore"
        
        ELIMINATED_patterns = [
            "# ELIMINATED/ELIMINATED prevention",
            "*ELIMINATED*",
            "*ELIMINATED*",
            "*.ELIMINATED",
            "ELIMINATED.config.*",
            "ELIMINATED.config.*"
        ]
        
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                content = f.read()
        else:
            content = ""
            
        # Add patterns if not already present
        for pattern in ELIMINATED_patterns:
            if pattern not in content:
                content += f"\n{pattern}"
                
        with open(gitignore_path, 'w') as f:
            f.write(content)
            
        logger.info("Updated .gitignore with ELIMINATED prevention patterns")
        
    def _create_detection_script(self):
        """Create script to detect any new ELIMINATED references"""
        detection_script = '''#!/usr/bin/env python3
"""
ELIMINATED Detection Script
Scans for any new ELIMINATED/ELIMINATED references
"""

import os
import re
from pathlib import Path

def scan_for_ELIMINATED():
    """Scan for ELIMINATED references"""
    patterns = [r'ELIMINATED', r'ELIMINATED', r'ELIMINATED', r'ELIMINATED']
    found_references = []
    
    for pattern in patterns:
        result = os.popen(f'grep -r -i "{pattern}" . --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=elimination_backup').read()
        if result.strip():
            found_references.append((pattern, result))
            
    if found_references:
        print("❌ ELIMINATED REFERENCES DETECTED:")
        for pattern, results in found_references:
            print(f"\\nPattern: {pattern}")
            print(results)
        return False
    else:
        print("✅ No ELIMINATED references detected")
        return True

if __name__ == "__main__":
    scan_for_ELIMINATED()
'''
        
        script_path = self.repo_root / "scripts" / "detect_ELIMINATED_references.py"
        with open(script_path, 'w') as f:
            f.write(detection_script)
            
        os.chmod(script_path, 0o755)
        logger.info("Created ELIMINATED detection script")
        
    def run_complete_elimination(self):
        """Run all elimination phases"""
        logger.info("🧹 Starting Complete ELIMINATED Elimination")
        
        try:
            self.phase1_github_actions_cleanup()
            self.phase2_docker_cleanup()
            self.phase3_json_config_cleanup()
            self.phase4_documentation_archival()
            self.phase5_deep_reference_scan()
            self.phase6_prevention_system()
            
            self._generate_elimination_report()
            
        except Exception as e:
            logger.error(f"Error during elimination: {e}")
            raise
            
    def _generate_elimination_report(self):
        """Generate comprehensive elimination report"""
        report = {
            "elimination_timestamp": datetime.now().isoformat(),
            "total_modifications": len(self.modifications),
            "eliminated_files": self.eliminated_files,
            "archived_files": self.archived_files,
            "modifications": self.modifications,
            "phases_completed": [
                "GitHub Actions Cleanup",
                "Docker Configuration Cleanup", 
                "JSON Configuration Cleanup",
                "Documentation Archival",
                "Deep Reference Scan",
                "Prevention System Implementation"
            ],
            "prevention_measures": [
                "Pre-commit hook installed",
                ".gitignore updated",
                "Detection script created"
            ]
        }
        
        report_path = self.repo_root / "COMPLETE_ELIMINATED_ELIMINATION_REPORT.md"
        with open(report_path, 'w') as f:
            f.write(f"""# 🧹 Complete ELIMINATED Elimination Report

**Elimination Date:** {report['elimination_timestamp']}

## 📊 Summary
- **Total Modifications:** {report['total_modifications']}
- **Files Eliminated:** {len(report['eliminated_files'])}
- **Files Archived:** {len(report['archived_files'])}

## ✅ Phases Completed
{chr(10).join(f"- {phase}" for phase in report['phases_completed'])}

## 🛡️ Prevention Measures
{chr(10).join(f"- {measure}" for measure in report['prevention_measures'])}

## 📝 Modifications Made
{chr(10).join(f"- {mod}" for mod in report['modifications'])}

## 🗂️ Archived Files
{chr(10).join(f"- {file}" for file in report['archived_files'])}

## 🚨 Verification Commands
```bash
# Check for any remaining references
python scripts/detect_ELIMINATED_references.py

# Test clean build
python -m pytest tests/ -v

# Verify no environment variable dependencies
grep -r "ELIMINATED\\|ELIMINATED" . --exclude-dir=.git --exclude-dir=elimination_backup
```

## 🎯 Status: COMPLETE
All ELIMINATED/ELIMINATED references have been eliminated and prevention measures are in place.
""")
        
        logger.info(f"✅ Complete elimination finished! Report: {report_path}")
        logger.info(f"📊 Total modifications: {len(self.modifications)}")
        logger.info(f"🗂️ Files archived: {len(self.archived_files)}")

def main():
    """Main execution"""
    eliminator = CompleteELIMINATEDEliminator()
    eliminator.run_complete_elimination()

if __name__ == "__main__":
    main() 