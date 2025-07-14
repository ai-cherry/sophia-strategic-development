#!/usr/bin/env python3
"""
Qdrant Alignment Validation Script
Validates that GitHub workflows are properly aligned with Qdrant architecture
"""

import os
import json
import yaml
import subprocess
from pathlib import Path
from typing import List, Dict, Any

class QdrantAlignmentValidator:
    """Validates Qdrant alignment across the codebase"""
    
    def __init__(self):
        self.repo_root = Path(__file__).parent.parent
        self.issues = []
        self.successes = []
    
    def validate_workflows(self) -> bool:
        """Validate GitHub workflows for Qdrant alignment"""
        print("🔍 Validating GitHub workflows...")
        
        workflow_dir = self.repo_root / ".github" / "workflows"
        if not workflow_dir.exists():
            self.issues.append("GitHub workflows directory not found")
            return False
        
        workflows_valid = True
        
        for workflow_file in workflow_dir.glob("*.yml"):
            if workflow_file.name in ["contamination_check.yml", "qdrant_production_deploy.yml"]:
                continue  # Skip our new workflows
            
            try:
                with open(workflow_file, 'r') as f:
                    content = f.read()
                
                # Check if workflow is disabled
                if 'if: false' in content:
                    self.successes.append(f"Workflow properly disabled: {workflow_file.name}")
                    continue
                
                # Check for Weaviate contamination
                if 'weaviate' in content.lower():
                    self.issues.append(f"Weaviate contamination in active workflow: {workflow_file.name}")
                    workflows_valid = False
                else:
                    self.successes.append(f"Workflow clean: {workflow_file.name}")
                    
            except Exception as e:
                self.issues.append(f"Error reading workflow {workflow_file.name}: {e}")
                workflows_valid = False
        
        return workflows_valid
    
    def validate_k8s_manifests(self) -> bool:
        """Validate Kubernetes manifests for Qdrant alignment"""
        print("☸️ Validating Kubernetes manifests...")
        
        k8s_dir = self.repo_root / "k8s"
        if not k8s_dir.exists():
            self.issues.append("Kubernetes directory not found")
            return False
        
        manifests_valid = True
        
        for manifest_file in k8s_dir.rglob("*.yaml"):
            try:
                with open(manifest_file, 'r') as f:
                    content = f.read()
                
                # Check for Weaviate references
                if 'weaviate' in content.lower():
                    self.issues.append(f"Weaviate reference in manifest: {manifest_file.relative_to(self.repo_root)}")
                    manifests_valid = False
                
                # Check for Qdrant references
                if 'qdrant' in content.lower():
                    self.successes.append(f"Qdrant configured in: {manifest_file.relative_to(self.repo_root)}")
                    
            except Exception as e:
                self.issues.append(f"Error reading manifest {manifest_file.relative_to(self.repo_root)}: {e}")
                manifests_valid = False
        
        return manifests_valid
    
    def validate_docker_compose(self) -> bool:
        """Validate Docker Compose files for Qdrant alignment"""
        print("🐳 Validating Docker Compose files...")
        
        compose_files = [
            "docker-compose.yml",
            "docker-compose.development.yml"
        ]
        
        compose_valid = True
        
        for compose_file in compose_files:
            compose_path = self.repo_root / compose_file
            
            if not compose_path.exists():
                continue
            
            try:
                with open(compose_path, 'r') as f:
                    content = f.read()
                
                # Check for Weaviate services
                if 'weaviate:' in content:
                    self.issues.append(f"Weaviate service found in: {compose_file}")
                    compose_valid = False
                else:
                    self.successes.append(f"No Weaviate service in: {compose_file}")
                    
            except Exception as e:
                self.issues.append(f"Error reading compose file {compose_file}: {e}")
                compose_valid = False
        
        return compose_valid
    
    def validate_qdrant_connectivity(self) -> bool:
        """Validate Qdrant connectivity (if credentials available)"""
        print("🔗 Validating Qdrant connectivity...")
        
        qdrant_url = os.getenv("QDRANT_URL", "https://cloud.qdrant.io")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        
        if not qdrant_api_key:
            self.issues.append("QDRANT_API_KEY not provided - skipping connectivity test")
            return False
        
        try:
            import requests
            
            response = requests.get(
                f"{qdrant_url}/collections",
                headers={"Authorization": f"Bearer {qdrant_api_key}"},
                timeout=10
            )
            
            if response.status_code == 200:
                self.successes.append("Qdrant connectivity successful")
                return True
            else:
                self.issues.append(f"Qdrant connectivity failed: {response.status_code}")
                return False
                
        except ImportError:
            self.issues.append("requests library not available - skipping connectivity test")
            return False
        except Exception as e:
            self.issues.append(f"Qdrant connectivity error: {e}")
            return False
    
    def generate_report(self):
        """Generate validation report"""
        print("\n" + "="*60)
        print("📊 QDRANT ALIGNMENT VALIDATION REPORT")
        print("="*60)
        
        if self.successes:
            print("\n✅ SUCCESSES:")
            for success in self.successes:
                print(f"  ✅ {success}")
        
        if self.issues:
            print("\n❌ ISSUES:")
            for issue in self.issues:
                print(f"  ❌ {issue}")
        
        print(f"\n📊 SUMMARY:")
        print(f"  ✅ Successes: {len(self.successes)}")
        print(f"  ❌ Issues: {len(self.issues)}")
        
        if self.issues:
            print("\n🔧 NEXT STEPS:")
            print("  1. Review and fix the issues listed above")
            print("  2. Re-run the validation script")
            print("  3. Ensure all workflows use Qdrant instead of Weaviate")
            
        return len(self.issues) == 0
    
    def run_validation(self) -> bool:
        """Run complete validation"""
        print("🚀 Starting Qdrant Alignment Validation")
        print("="*50)
        
        validations = [
            self.validate_workflows(),
            self.validate_k8s_manifests(),
            self.validate_docker_compose(),
            self.validate_qdrant_connectivity()
        ]
        
        all_valid = all(validations)
        self.generate_report()
        
        if all_valid:
            print("\n🎉 ALL VALIDATIONS PASSED!")
            print("✅ GitHub workflows are properly aligned with Qdrant architecture")
        else:
            print("\n⚠️ VALIDATION ISSUES FOUND")
            print("❌ Please address the issues above before proceeding")
        
        return all_valid

def main():
    """Main validation function"""
    validator = QdrantAlignmentValidator()
    success = validator.run_validation()
    
    exit(0 if success else 1)

if __name__ == "__main__":
    main()
