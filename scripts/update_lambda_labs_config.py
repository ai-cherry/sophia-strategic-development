#!/usr/bin/env python3
"""
Lambda Labs Configuration Update Script

Updates all references to outdated Lambda Labs IP addresses and configurations
based on the current running instances from the Lambda Labs dashboard.

Current Active Instances:
- sophia-platform-prod: 146.235.200.1 (gpu_1x_a10) - Main Platform
- sophia-mcp-prod: 165.1.69.44 (gpu_1x_a10) - MCP Servers  
- sophia-ai-prod: 137.131.6.213 (gpu_1x_a100_sxm4) - AI Processing
"""

import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple


class LambdaLabsConfigUpdater:
    """Updates Lambda Labs configurations across the entire codebase"""
    
    def __init__(self):
        # Old IP that needs to be replaced
        self.old_ip = "104.171.202.64"
        
        # Current Lambda Labs instances from dashboard
        self.instances = {
            "platform": {
                "name": "sophia-platform-prod",
                "ip": "146.235.200.1",
                "type": "gpu_1x_a10",
                "purpose": "Main Platform Services"
            },
            "mcp": {
                "name": "sophia-mcp-prod", 
                "ip": "165.1.69.44",
                "type": "gpu_1x_a10",
                "purpose": "MCP Servers (Codacy, etc.)"
            },
            "ai": {
                "name": "sophia-ai-prod",
                "ip": "137.131.6.213", 
                "type": "gpu_1x_a100_sxm4",
                "purpose": "AI Processing & ML Workloads"
            }
        }
        
        # Service to instance mapping
        self.service_mapping = {
            "codacy": "mcp",           # Codacy MCP Server
            "mcp": "mcp",              # General MCP services
            "main": "platform",       # Main API
            "api": "platform",        # API services
            "platform": "platform",   # Platform services
            "ai": "ai",               # AI processing
            "ml": "ai",               # Machine learning
            "cortex": "ai",           # Snowflake Cortex
        }
        
        # Files that need updates
        self.update_targets = []
        
    def scan_for_old_references(self) -> List[Tuple[str, int, str]]:
        """Scan codebase for old IP references"""
        print("🔍 Scanning for old Lambda Labs IP references...")
        
        try:
            # Use git grep to find all references
            result = subprocess.run(
                ["git", "grep", "-n", self.old_ip],
                capture_output=True,
                text=True,
                cwd="."
            )
            
            references = []
            for line in result.stdout.split('\n'):
                if line.strip():
                    parts = line.split(':', 2)
                    if len(parts) >= 3:
                        file_path = parts[0]
                        line_num = int(parts[1])
                        content = parts[2]
                        references.append((file_path, line_num, content))
            
            print(f"   Found {len(references)} references to old IP {self.old_ip}")
            return references
            
        except subprocess.CalledProcessError:
            print("   No references found or git grep failed")
            return []
    
    def determine_target_instance(self, file_path: str, content: str) -> str:
        """Determine which instance a service should target"""
        file_lower = file_path.lower()
        content_lower = content.lower()
        
        # Check for specific service indicators
        for service, instance_key in self.service_mapping.items():
            if service in file_lower or service in content_lower:
                return instance_key
        
        # Default assignments based on file patterns
        if any(pattern in file_lower for pattern in ['codacy', 'mcp']):
            return "mcp"
        elif any(pattern in file_lower for pattern in ['ai', 'cortex', 'ml']):
            return "ai"
        else:
            return "platform"  # Default to platform
    
    def update_file_content(self, file_path: str, target_instance: str) -> bool:
        """Update a file with the correct IP address"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_ip = self.instances[target_instance]["ip"]
            new_content = content.replace(self.old_ip, new_ip)
            
            if new_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                return True
            
            return False
            
        except Exception as e:
            print(f"   ❌ Error updating {file_path}: {e}")
            return False
    
    def update_github_workflow(self) -> bool:
        """Update the GitHub Actions workflow for Codacy deployment"""
        workflow_path = ".github/workflows/deploy-codacy-to-lambda.yml"
        
        try:
            with open(workflow_path, 'r') as f:
                content = f.read()
            
            # Update SSH keyscan and SSH commands to use MCP instance
            mcp_ip = self.instances["mcp"]["ip"]
            
            # Replace IP in SSH keyscan
            content = re.sub(
                r'ssh-keyscan -t rsa \d+\.\d+\.\d+\.\d+',
                f'ssh-keyscan -t rsa {mcp_ip}',
                content
            )
            
            # Replace IP in SSH connection
            content = re.sub(
                r'ssh ubuntu@\d+\.\d+\.\d+\.\d+',
                f'ssh ubuntu@{mcp_ip}',
                content
            )
            
            # Update old IP references
            content = content.replace(self.old_ip, mcp_ip)
            
            with open(workflow_path, 'w') as f:
                f.write(content)
            
            print(f"   ✅ Updated GitHub workflow to target {mcp_ip} (sophia-mcp-prod)")
            return True
            
        except Exception as e:
            print(f"   ❌ Error updating GitHub workflow: {e}")
            return False
    
    def create_instance_mapping_docs(self) -> None:
        """Create documentation for the new instance mapping"""
        docs_content = f"""# Lambda Labs Instance Mapping

**Updated**: {subprocess.run(['date'], capture_output=True, text=True).stdout.strip()}

## Current Active Instances

"""
        
        for key, instance in self.instances.items():
            docs_content += f"""### {instance['name']}
- **IP Address**: `{instance['ip']}`
- **Instance Type**: `{instance['type']}`
- **Purpose**: {instance['purpose']}

"""
        
        docs_content += f"""## Service Deployment Mapping

| Service Type | Target Instance | IP Address | Purpose |
|--------------|----------------|------------|---------|
"""
        
        for service, instance_key in self.service_mapping.items():
            instance = self.instances[instance_key]
            docs_content += f"| {service.title()} | {instance['name']} | `{instance['ip']}` | {instance['purpose']} |\n"
        
        docs_content += f"""
## Migration Summary

- **Old IP**: `{self.old_ip}` (deprecated)
- **Codacy MCP Server**: Now deploys to `{self.instances['mcp']['ip']}` (sophia-mcp-prod)
- **Main Platform**: Now targets `{self.instances['platform']['ip']}` (sophia-platform-prod)  
- **AI Processing**: Now targets `{self.instances['ai']['ip']}` (sophia-ai-prod)

## Access URLs

### MCP Services (sophia-mcp-prod: {self.instances['mcp']['ip']})
- Codacy MCP: `http://{self.instances['mcp']['ip']}:3008`
- AI Memory: `http://{self.instances['mcp']['ip']}:9001`
- Other MCP Servers: `http://{self.instances['mcp']['ip']}:<port>`

### Platform Services (sophia-platform-prod: {self.instances['platform']['ip']})
- Main API: `http://{self.instances['platform']['ip']}:8000`
- Frontend: `http://{self.instances['platform']['ip']}:3000`
- API Docs: `http://{self.instances['platform']['ip']}:8000/docs`

### AI Services (sophia-ai-prod: {self.instances['ai']['ip']})
- Snowflake Cortex: `http://{self.instances['ai']['ip']}:9030`
- AI Processing: `http://{self.instances['ai']['ip']}:<port>`

## Monitoring Commands

```bash
# Test Codacy MCP Server
python scripts/monitor_codacy_mcp_server.py

# Test all connectivity  
python scripts/test_lambda_labs_connectivity.py

# Check deployment status
python scripts/check_deployment_status.py
```
"""
        
        # Save documentation
        with open("docs/LAMBDA_LABS_INSTANCE_MAPPING.md", 'w') as f:
            f.write(docs_content)
        
        print("   ✅ Created instance mapping documentation")
    
    def run_comprehensive_update(self) -> Dict[str, int]:
        """Run comprehensive update of all Lambda Labs configurations"""
        print("🚀 Lambda Labs Configuration Update")
        print("="*60)
        
        # Scan for references
        references = self.scan_for_old_references()
        
        if not references:
            print("✅ No old IP references found - everything is up to date!")
            return {"total": 0, "updated": 0, "errors": 0}
        
        print(f"\n📋 Processing {len(references)} files...")
        
        # Group by file for batch processing
        files_to_update = {}
        for file_path, line_num, content in references:
            if file_path not in files_to_update:
                files_to_update[file_path] = []
            files_to_update[file_path].append((line_num, content))
        
        # Update files
        stats = {"total": len(files_to_update), "updated": 0, "errors": 0}
        
        for file_path, lines in files_to_update.items():
            print(f"\n📝 Processing: {file_path}")
            
            # Determine target instance
            sample_content = " ".join([line[1] for line in lines[:3]])  # Use first few lines as sample
            target_instance = self.determine_target_instance(file_path, sample_content)
            target_ip = self.instances[target_instance]["ip"]
            target_name = self.instances[target_instance]["name"]
            
            print(f"   🎯 Target: {target_name} ({target_ip})")
            
            # Update file
            if self.update_file_content(file_path, target_instance):
                stats["updated"] += 1
                print(f"   ✅ Updated {len(lines)} references")
            else:
                stats["errors"] += 1
                print(f"   ❌ Failed to update")
        
        # Update GitHub workflow specifically
        print(f"\n🔧 Updating GitHub Actions workflow...")
        if self.update_github_workflow():
            print("   ✅ GitHub workflow updated for Codacy MCP deployment")
        else:
            print("   ❌ Failed to update GitHub workflow")
        
        # Create documentation
        print(f"\n📚 Creating instance mapping documentation...")
        self.create_instance_mapping_docs()
        
        return stats
    
    def verify_updates(self) -> bool:
        """Verify that updates were successful"""
        print(f"\n🔍 Verifying updates...")
        
        # Check if old IP still exists
        try:
            result = subprocess.run(
                ["git", "grep", self.old_ip],
                capture_output=True,
                text=True,
                cwd="."
            )
            
            remaining_refs = result.stdout.strip()
            if remaining_refs:
                print(f"   ⚠️ Found remaining references to old IP:")
                for line in remaining_refs.split('\n')[:5]:  # Show first 5
                    print(f"      {line}")
                return False
            else:
                print("   ✅ No remaining references to old IP found")
                return True
                
        except subprocess.CalledProcessError:
            print("   ✅ No remaining references to old IP found")
            return True


def main():
    """Main execution function"""
    updater = LambdaLabsConfigUpdater()
    
    print("🔄 Updating Lambda Labs configurations based on current dashboard...")
    print("📊 Current Active Instances:")
    for key, instance in updater.instances.items():
        print(f"   • {instance['name']}: {instance['ip']} ({instance['purpose']})")
    
    print(f"\n🎯 Migration Plan:")
    print(f"   • OLD IP: {updater.old_ip} (deprecated)")
    print(f"   • Codacy MCP → {updater.instances['mcp']['ip']} (sophia-mcp-prod)")
    print(f"   • Platform → {updater.instances['platform']['ip']} (sophia-platform-prod)")
    print(f"   • AI Services → {updater.instances['ai']['ip']} (sophia-ai-prod)")
    
    # Run update
    stats = updater.run_comprehensive_update()
    
    # Show results
    print(f"\n📊 UPDATE RESULTS:")
    print(f"   📁 Total files processed: {stats['total']}")
    print(f"   ✅ Successfully updated: {stats['updated']}")
    print(f"   ❌ Errors: {stats['errors']}")
    
    # Verify
    if updater.verify_updates():
        print(f"\n🎉 All Lambda Labs configurations updated successfully!")
        print(f"\n🔗 Next Steps:")
        print(f"   1. Commit the changes: git add -A && git commit -m 'Update Lambda Labs instance IPs'")
        print(f"   2. Push to trigger new deployment: git push origin main")
        print(f"   3. Monitor deployment: python scripts/monitor_codacy_mcp_server.py")
        print(f"   4. Test Codacy MCP: http://{updater.instances['mcp']['ip']}:3008/health")
    else:
        print(f"\n⚠️ Some references may need manual review")
    
    print(f"\n📚 Documentation created: docs/LAMBDA_LABS_INSTANCE_MAPPING.md")


if __name__ == "__main__":
    main() 