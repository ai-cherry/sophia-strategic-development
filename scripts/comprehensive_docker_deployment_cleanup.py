#!/usr/bin/env python3
"""
🔬 COMPREHENSIVE DOCKER/DEPLOYMENT ECOSYSTEM CLEANUP
Complete analysis, verification, and cleanup of Docker/deployment files

This script implements the comprehensive cleanup strategy for the Docker/deployment chaos.
"""

import os
import shutil
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple
import yaml
import re

class DockerDeploymentAnalyzer:
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.analysis_results = {
            "dockerfiles": {},
            "compose_files": {},
            "deployment_scripts": {},
            "backup_files": {},
            "github_workflows": {},
            "config_files": {}
        }
        self.cleanup_actions = []
        self.files_to_keep = []
        self.files_to_delete = []
        
    def analyze_dockerfiles(self) -> Dict:
        """Analyze all Dockerfiles and categorize them"""
        print("🔍 Analyzing Dockerfiles...")
        
        dockerfiles = list(self.base_path.rglob("Dockerfile*"))
        
        working_dockerfiles = []
        broken_dockerfiles = []
        backup_dockerfiles = []
        
        for dockerfile in dockerfiles:
            if ".backup" in str(dockerfile) or "backup" in str(dockerfile):
                backup_dockerfiles.append(str(dockerfile))
            elif self._is_dockerfile_valid(dockerfile):
                working_dockerfiles.append(str(dockerfile))
            else:
                broken_dockerfiles.append(str(dockerfile))
        
        self.analysis_results["dockerfiles"] = {
            "total": len(dockerfiles),
            "working": working_dockerfiles,
            "broken": broken_dockerfiles,
            "backup": backup_dockerfiles
        }
        
        print(f"  📊 Found {len(dockerfiles)} Dockerfiles:")
        print(f"    ✅ Working: {len(working_dockerfiles)}")
        print(f"    ❌ Broken: {len(broken_dockerfiles)}")
        print(f"    🗑️  Backup: {len(backup_dockerfiles)}")
        
        return self.analysis_results["dockerfiles"]
    
    def analyze_compose_files(self) -> Dict:
        """Analyze all docker-compose files"""
        print("🔍 Analyzing docker-compose files...")
        
        compose_files = list(self.base_path.rglob("docker-compose*.yml")) + \
                       list(self.base_path.rglob("docker-compose*.yaml"))
        
        working_compose = []
        broken_compose = []
        redundant_compose = []
        
        for compose_file in compose_files:
            if self._is_compose_valid(compose_file):
                if self._is_compose_redundant(compose_file):
                    redundant_compose.append(str(compose_file))
                else:
                    working_compose.append(str(compose_file))
            else:
                broken_compose.append(str(compose_file))
        
        self.analysis_results["compose_files"] = {
            "total": len(compose_files),
            "working": working_compose,
            "broken": broken_compose,
            "redundant": redundant_compose
        }
        
        print(f"  📊 Found {len(compose_files)} docker-compose files:")
        print(f"    ✅ Working: {len(working_compose)}")
        print(f"    ❌ Broken: {len(broken_compose)}")
        print(f"    🔄 Redundant: {len(redundant_compose)}")
        
        return self.analysis_results["compose_files"]
    
    def analyze_deployment_scripts(self) -> Dict:
        """Analyze all deployment scripts"""
        print("🔍 Analyzing deployment scripts...")
        
        script_patterns = ["*deploy*", "*deployment*"]
        deployment_scripts = []
        
        for pattern in script_patterns:
            deployment_scripts.extend(list(self.base_path.rglob(pattern)))
        
        # Filter to only include actual script files
        deployment_scripts = [f for f in deployment_scripts if f.is_file() and 
                            (f.suffix in ['.sh', '.py', '.yml', '.yaml'] or f.name.startswith('deploy'))]
        
        working_scripts = []
        broken_scripts = []
        backup_scripts = []
        
        for script in deployment_scripts:
            if ".backup" in str(script) or "backup" in str(script):
                backup_scripts.append(str(script))
            elif self._is_script_working(script):
                working_scripts.append(str(script))
            else:
                broken_scripts.append(str(script))
        
        self.analysis_results["deployment_scripts"] = {
            "total": len(deployment_scripts),
            "working": working_scripts,
            "broken": broken_scripts,
            "backup": backup_scripts
        }
        
        print(f"  📊 Found {len(deployment_scripts)} deployment scripts:")
        print(f"    ✅ Working: {len(working_scripts)}")
        print(f"    ❌ Broken: {len(broken_scripts)}")
        print(f"    🗑️  Backup: {len(backup_scripts)}")
        
        return self.analysis_results["deployment_scripts"]
    
    def analyze_backup_files(self) -> Dict:
        """Analyze all backup files"""
        print("🔍 Analyzing backup files...")
        
        backup_patterns = ["*.backup", "*.ssh_backup", "*backup*", "*.bak"]
        backup_files = []
        
        for pattern in backup_patterns:
            backup_files.extend(list(self.base_path.rglob(pattern)))
        
        ssh_backups = [f for f in backup_files if ".ssh_backup" in str(f)]
        general_backups = [f for f in backup_files if ".ssh_backup" not in str(f)]
        
        self.analysis_results["backup_files"] = {
            "total": len(backup_files),
            "ssh_backups": [str(f) for f in ssh_backups],
            "general_backups": [str(f) for f in general_backups]
        }
        
        print(f"  📊 Found {len(backup_files)} backup files:")
        print(f"    🔑 SSH backups: {len(ssh_backups)}")
        print(f"    📄 General backups: {len(general_backups)}")
        
        return self.analysis_results["backup_files"]
    
    def analyze_github_workflows(self) -> Dict:
        """Analyze GitHub workflows"""
        print("🔍 Analyzing GitHub workflows...")
        
        workflow_dir = self.base_path / ".github" / "workflows"
        if not workflow_dir.exists():
            self.analysis_results["github_workflows"] = {"total": 0, "files": []}
            return self.analysis_results["github_workflows"]
        
        workflows = list(workflow_dir.glob("*.yml")) + list(workflow_dir.glob("*.yaml"))
        
        deployment_workflows = []
        other_workflows = []
        
        for workflow in workflows:
            if "deploy" in workflow.name.lower() or "build" in workflow.name.lower():
                deployment_workflows.append(str(workflow))
            else:
                other_workflows.append(str(workflow))
        
        self.analysis_results["github_workflows"] = {
            "total": len(workflows),
            "deployment": deployment_workflows,
            "other": other_workflows
        }
        
        print(f"  📊 Found {len(workflows)} GitHub workflows:")
        print(f"    🚀 Deployment: {len(deployment_workflows)}")
        print(f"    🔧 Other: {len(other_workflows)}")
        
        return self.analysis_results["github_workflows"]
    
    def _is_dockerfile_valid(self, dockerfile: Path) -> bool:
        """Check if a Dockerfile is valid and references existing files"""
        try:
            with open(dockerfile, 'r') as f:
                content = f.read()
                
            # Check for basic Dockerfile structure
            if not content.strip().startswith('FROM'):
                return False
                
            # Check for references to missing files
            copy_lines = re.findall(r'COPY\s+(\S+)', content)
            for copy_ref in copy_lines:
                if copy_ref.startswith('.') or copy_ref.startswith('/'):
                    ref_path = dockerfile.parent / copy_ref
                    if not ref_path.exists() and not any(ref_path.parent.glob(copy_ref.split('/')[-1])):
                        return False
            
            return True
        except Exception:
            return False
    
    def _is_compose_valid(self, compose_file: Path) -> bool:
        """Check if a docker-compose file is valid"""
        try:
            with open(compose_file, 'r') as f:
                compose_data = yaml.safe_load(f)
                
            # Check for basic compose structure
            if not isinstance(compose_data, dict) or 'services' not in compose_data:
                return False
                
            # Check for references to missing Dockerfiles
            for service_name, service_config in compose_data['services'].items():
                if 'build' in service_config:
                    build_config = service_config['build']
                    if isinstance(build_config, dict) and 'dockerfile' in build_config:
                        dockerfile_path = compose_file.parent / build_config['dockerfile']
                        if not dockerfile_path.exists():
                            return False
                    elif isinstance(build_config, str):
                        dockerfile_path = compose_file.parent / build_config / 'Dockerfile'
                        if not dockerfile_path.exists():
                            return False
            
            return True
        except Exception:
            return False
    
    def _is_compose_redundant(self, compose_file: Path) -> bool:
        """Check if a compose file is redundant"""
        redundant_patterns = [
            'docker-compose.override.yml',
            'docker-compose.dev.yml',
            'docker-compose.local.yml',
            'docker-compose.backup',
            'docker-compose.old'
        ]
        
        return any(pattern in str(compose_file) for pattern in redundant_patterns)
    
    def _is_script_working(self, script: Path) -> bool:
        """Check if a deployment script is working"""
        try:
            with open(script, 'r') as f:
                content = f.read()
            
            # Check for references to missing files
            if 'docker-compose' in content:
                compose_refs = re.findall(r'docker-compose\s+.*?-f\s+(\S+)', content)
                for ref in compose_refs:
                    ref_path = script.parent / ref
                    if not ref_path.exists():
                        return False
            
            # Check for references to missing Dockerfiles
            if 'docker build' in content:
                dockerfile_refs = re.findall(r'docker build.*?-f\s+(\S+)', content)
                for ref in dockerfile_refs:
                    ref_path = script.parent / ref
                    if not ref_path.exists():
                        return False
            
            return True
        except Exception:
            return False
    
    def generate_cleanup_plan(self) -> List[Dict]:
        """Generate a comprehensive cleanup plan"""
        print("📋 Generating cleanup plan...")
        
        cleanup_plan = []
        
        # 1. Delete all backup files
        for backup_file in self.analysis_results["backup_files"]["ssh_backups"] + \
                          self.analysis_results["backup_files"]["general_backups"]:
            cleanup_plan.append({
                "action": "delete",
                "file": backup_file,
                "reason": "Backup file cleanup",
                "safe": True
            })
        
        # 2. Delete broken Dockerfiles
        for dockerfile in self.analysis_results["dockerfiles"]["broken"]:
            cleanup_plan.append({
                "action": "delete",
                "file": dockerfile,
                "reason": "Broken Dockerfile",
                "safe": True
            })
        
        # 3. Delete backup Dockerfiles
        for dockerfile in self.analysis_results["dockerfiles"]["backup"]:
            cleanup_plan.append({
                "action": "delete",
                "file": dockerfile,
                "reason": "Backup Dockerfile",
                "safe": True
            })
        
        # 4. Delete broken compose files
        for compose_file in self.analysis_results["compose_files"]["broken"]:
            cleanup_plan.append({
                "action": "delete",
                "file": compose_file,
                "reason": "Broken docker-compose file",
                "safe": True
            })
        
        # 5. Delete redundant compose files
        for compose_file in self.analysis_results["compose_files"]["redundant"]:
            cleanup_plan.append({
                "action": "delete",
                "file": compose_file,
                "reason": "Redundant docker-compose file",
                "safe": True
            })
        
        # 6. Delete broken deployment scripts
        for script in self.analysis_results["deployment_scripts"]["broken"]:
            cleanup_plan.append({
                "action": "delete",
                "file": script,
                "reason": "Broken deployment script",
                "safe": True
            })
        
        # 7. Delete backup deployment scripts
        for script in self.analysis_results["deployment_scripts"]["backup"]:
            cleanup_plan.append({
                "action": "delete",
                "file": script,
                "reason": "Backup deployment script",
                "safe": True
            })
        
        self.cleanup_actions = cleanup_plan
        
        print(f"  📋 Generated {len(cleanup_plan)} cleanup actions")
        
        return cleanup_plan
    
    def execute_cleanup(self, dry_run: bool = True) -> Dict:
        """Execute the cleanup plan"""
        print(f"🧹 {'DRY RUN: ' if dry_run else ''}Executing cleanup plan...")
        
        results = {
            "deleted": [],
            "errors": [],
            "skipped": []
        }
        
        for action in self.cleanup_actions:
            try:
                file_path = Path(action["file"])
                
                if not file_path.exists():
                    results["skipped"].append(f"File not found: {action['file']}")
                    continue
                
                if dry_run:
                    print(f"  [DRY RUN] Would delete: {action['file']} ({action['reason']})")
                    results["deleted"].append(action["file"])
                else:
                    if file_path.is_file():
                        file_path.unlink()
                    elif file_path.is_dir():
                        shutil.rmtree(file_path)
                    
                    print(f"  ✅ Deleted: {action['file']} ({action['reason']})")
                    results["deleted"].append(action["file"])
                    
            except Exception as e:
                error_msg = f"Error deleting {action['file']}: {str(e)}"
                print(f"  ❌ {error_msg}")
                results["errors"].append(error_msg)
        
        return results
    
    def verify_working_files(self) -> Dict:
        """Verify that working files are actually functional"""
        print("🔍 Verifying working files...")
        
        verification_results = {
            "dockerfiles": {},
            "compose_files": {},
            "scripts": {}
        }
        
        # Test working Dockerfiles
        for dockerfile in self.analysis_results["dockerfiles"]["working"]:
            dockerfile_path = Path(dockerfile)
            try:
                # Try to parse the Dockerfile
                result = subprocess.run(
                    ["docker", "build", "--dry-run", "-f", str(dockerfile_path), "."],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                verification_results["dockerfiles"][dockerfile] = {
                    "status": "working" if result.returncode == 0 else "broken",
                    "error": result.stderr if result.returncode != 0 else None
                }
            except Exception as e:
                verification_results["dockerfiles"][dockerfile] = {
                    "status": "error",
                    "error": str(e)
                }
        
        # Test working compose files
        for compose_file in self.analysis_results["compose_files"]["working"]:
            compose_path = Path(compose_file)
            try:
                result = subprocess.run(
                    ["docker-compose", "-f", str(compose_path), "config"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                verification_results["compose_files"][compose_file] = {
                    "status": "working" if result.returncode == 0 else "broken",
                    "error": result.stderr if result.returncode != 0 else None
                }
            except Exception as e:
                verification_results["compose_files"][compose_file] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return verification_results
    
    def generate_report(self) -> Dict:
        """Generate a comprehensive analysis report"""
        total_files = sum([
            self.analysis_results["dockerfiles"]["total"],
            self.analysis_results["compose_files"]["total"],
            self.analysis_results["deployment_scripts"]["total"],
            self.analysis_results["backup_files"]["total"],
            self.analysis_results["github_workflows"]["total"]
        ])
        
        files_to_delete = len(self.cleanup_actions)
        files_to_keep = total_files - files_to_delete
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_files_analyzed": total_files,
                "files_to_delete": files_to_delete,
                "files_to_keep": files_to_keep,
                "cleanup_reduction": f"{(files_to_delete/total_files)*100:.1f}%" if total_files > 0 else "0%"
            },
            "analysis_results": self.analysis_results,
            "cleanup_actions": self.cleanup_actions,
            "recommended_final_structure": {
                "dockerfiles": [
                    "Dockerfile.production",
                    "frontend/Dockerfile",
                    "mcp-servers/Dockerfile.base"
                ],
                "compose_files": [
                    "docker-compose.unified.yml"
                ],
                "deployment_scripts": [
                    "scripts/deploy_production.sh",
                    "scripts/deploy_k3s.sh",
                    "scripts/build_images.sh"
                ]
            }
        }
        
        return report
    
    def run_comprehensive_analysis(self, dry_run: bool = True) -> Dict:
        """Run the complete analysis and cleanup process"""
        print("🚀 Starting comprehensive Docker/deployment analysis...")
        print("=" * 60)
        
        # Run all analyses
        self.analyze_dockerfiles()
        self.analyze_compose_files()
        self.analyze_deployment_scripts()
        self.analyze_backup_files()
        self.analyze_github_workflows()
        
        # Generate cleanup plan
        self.generate_cleanup_plan()
        
        # Execute cleanup
        cleanup_results = self.execute_cleanup(dry_run=dry_run)
        
        # Verify working files
        verification_results = self.verify_working_files()
        
        # Generate final report
        report = self.generate_report()
        report["cleanup_results"] = cleanup_results
        report["verification_results"] = verification_results
        
        print("=" * 60)
        print("📊 ANALYSIS COMPLETE")
        print(f"Total files analyzed: {report['summary']['total_files_analyzed']}")
        print(f"Files to delete: {report['summary']['files_to_delete']}")
        print(f"Files to keep: {report['summary']['files_to_keep']}")
        print(f"Cleanup reduction: {report['summary']['cleanup_reduction']}")
        
        return report

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Comprehensive Docker/deployment cleanup")
    parser.add_argument("--execute", action="store_true", help="Execute cleanup (default is dry run)")
    parser.add_argument("--output", default="deployment_cleanup_report.json", help="Output report file")
    
    args = parser.parse_args()
    
    # Run analysis
    analyzer = DockerDeploymentAnalyzer()
    report = analyzer.run_comprehensive_analysis(dry_run=not args.execute)
    
    # Save report
    with open(args.output, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📄 Report saved to: {args.output}")
    
    if not args.execute:
        print("\n💡 This was a DRY RUN. Use --execute to actually delete files.")

if __name__ == "__main__":
    main() 