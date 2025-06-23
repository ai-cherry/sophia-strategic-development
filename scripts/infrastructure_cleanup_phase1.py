#!/usr/bin/env python3
"""
Sophia AI Infrastructure Cleanup - Phase 1
Removes legacy files, consolidates infrastructure, and prepares for modernization
"""

import os
import shutil
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

class InfrastructureCleanup:
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.archive_dir = Path(f"archive/infrastructure_{self.timestamp}")
        self.report = {
            "timestamp": self.timestamp,
            "actions": [],
            "errors": []
        }
        
    def run(self):
        """Execute all cleanup tasks"""
        print("🚀 Sophia AI Infrastructure Cleanup Phase 1")
        print("=" * 50)
        
        # Create archive directory
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Execute cleanup tasks
        self.cleanup_legacy_mcp_servers()
        self.cleanup_duplicate_docs()
        self.consolidate_esc_configs()
        self.cleanup_workflows()
        self.standardize_python_infrastructure()
        self.update_integration_registry()
        
        # Generate report
        self.generate_report()
        
    def cleanup_legacy_mcp_servers(self):
        """Archive legacy MCP server implementations"""
        print("\n📦 Archiving legacy MCP servers...")
        
        legacy_servers = [
            "mcp-servers/apollo_io",
            "mcp-servers/competitive_monitor",
            "mcp-servers/nmhc_targeting"
        ]
        
        archived = 0
        for server_path in legacy_servers:
            if Path(server_path).exists():
                try:
                    dest = self.archive_dir / "mcp-servers" / Path(server_path).name
                    shutil.copytree(server_path, dest)
                    shutil.rmtree(server_path)
                    archived += 1
                    print(f"   ✓ Archived: {server_path}")
                except Exception as e:
                    self.report["errors"].append(f"Failed to archive {server_path}: {e}")
                    
        self.report["actions"].append({
            "task": "archive_mcp_servers",
            "count": archived
        })
        
    def cleanup_duplicate_docs(self):
        """Remove duplicate documentation files"""
        print("\n📚 Cleaning duplicate documentation...")
        
        duplicate_patterns = [
            "docs/*SUMMARY 2.md",
            "docs/*SUMMARY 3.md",
            "docs/*SUMMARY 4.md",
            "docs/*RECOMMENDATIONS 2.md",
            "docs/*RECOMMENDATIONS 3.md",
            "docs/*STRATEGY 2.md",
            "docs/*STRATEGY 3.md"
        ]
        
        removed = 0
        for pattern in duplicate_patterns:
            for file_path in Path(".").glob(pattern):
                try:
                    dest = self.archive_dir / "docs" / file_path.name
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, dest)
                    file_path.unlink()
                    removed += 1
                    print(f"   ✓ Removed: {file_path}")
                except Exception as e:
                    self.report["errors"].append(f"Failed to remove {file_path}: {e}")
                    
        self.report["actions"].append({
            "task": "cleanup_duplicate_docs",
            "count": removed
        })
        
    def consolidate_esc_configs(self):
        """Consolidate ESC configurations to production and development only"""
        print("\n🔧 Consolidating ESC configurations...")
        
        esc_dir = Path("infrastructure/esc")
        esc_dir.mkdir(parents=True, exist_ok=True)
        
        # Create consolidated ESC config
        consolidated_config = {
            "version": "2.0",
            "environments": {
                "production": {
                    "imports": ["scoobyjava-org/default/sophia-ai-production"],
                    "values": {
                        "aws": {
                            "region": "us-east-1",
                            "account_id": "${aws.account_id}"
                        },
                        "kubernetes": {
                            "namespace": "sophia-production",
                            "cluster": "sophia-prod-cluster"
                        },
                        "services": {
                            "gong": {"enabled": True},
                            "snowflake": {"enabled": True},
                            "apollo": {"enabled": True},
                            "costar": {"enabled": True}
                        }
                    }
                },
                "development": {
                    "imports": ["scoobyjava-org/default/sophia-ai-development"],
                    "values": {
                        "aws": {
                            "region": "us-east-1",
                            "account_id": "${aws.account_id}"
                        },
                        "kubernetes": {
                            "namespace": "sophia-dev",
                            "cluster": "sophia-dev-cluster"
                        },
                        "services": {
                            "gong": {"enabled": True},
                            "snowflake": {"enabled": True},
                            "apollo": {"enabled": False},
                            "costar": {"enabled": False}
                        }
                    }
                }
            }
        }
        
        # Write consolidated config
        config_file = esc_dir / "consolidated-environments.yaml"
        with open(config_file, 'w') as f:
            import yaml
            yaml.dump(consolidated_config, f, default_flow_style=False)
            
        print(f"   ✓ Created: {config_file}")
        
        self.report["actions"].append({
            "task": "consolidate_esc",
            "created": str(config_file)
        })
        
    def cleanup_workflows(self):
        """Archive legacy GitHub workflows"""
        print("\n🔄 Cleaning up legacy workflows...")
        
        legacy_workflows = [
            ".github/workflows/deploy-sophia-dns.yml",
            ".github/workflows/deploy-sophia-platform.yml"
        ]
        
        archived = 0
        for workflow in legacy_workflows:
            if Path(workflow).exists():
                try:
                    dest = self.archive_dir / "workflows" / Path(workflow).name
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(workflow, dest)
                    Path(workflow).unlink()
                    archived += 1
                    print(f"   ✓ Archived: {workflow}")
                except Exception as e:
                    self.report["errors"].append(f"Failed to archive {workflow}: {e}")
                    
        self.report["actions"].append({
            "task": "archive_workflows",
            "count": archived
        })
        
    def standardize_python_infrastructure(self):
        """Ensure all infrastructure is Python-based"""
        print("\n🐍 Standardizing Python infrastructure...")
        
        # Check for TypeScript DNS manager
        ts_dns_path = Path("infrastructure/dns")
        if ts_dns_path.exists() and (ts_dns_path / "sophia-dns-infrastructure.ts").exists():
            # Archive TypeScript version
            dest = self.archive_dir / "typescript-dns"
            shutil.copytree(ts_dns_path, dest)
            print("   ✓ Archived TypeScript DNS manager")
            
            # Create Python wrapper
            wrapper_content = '''#!/usr/bin/env python3
"""
DNS Manager Service Wrapper
Wraps the TypeScript DNS manager as a Python service
"""

import subprocess
import json
from typing import Dict, Any

class DNSManagerService:
    def __init__(self):
        self.ts_path = str(Path(__file__).parent.parent / "archive" / f"infrastructure_{self.timestamp}" / "typescript-dns")
        
    def update_dns(self, domain: str, records: Dict[str, Any]) -> bool:
        """Update DNS records using the TypeScript implementation"""
        cmd = [
            "npm", "run", "update-dns",
            "--", 
            f"--domain={domain}",
            f"--records={json.dumps(records)}"
        ]
        
        result = subprocess.run(
            cmd,
            cwd=self.ts_path,
            capture_output=True,
            text=True
        )
        
        return result.returncode == 0
        
    def health_check(self) -> Dict[str, Any]:
        """Check DNS health"""
        cmd = ["npm", "run", "health-check"]
        
        result = subprocess.run(
            cmd,
            cwd=self.ts_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        return {"status": "error", "message": result.stderr}

# Service instance
dns_service = DNSManagerService()
'''
            
            # Write Python wrapper
            wrapper_file = Path("infrastructure/services/dns_manager.py")
            wrapper_file.parent.mkdir(parents=True, exist_ok=True)
            wrapper_file.write_text(wrapper_content.replace(f"infrastructure_{self.timestamp}", f"infrastructure_{self.timestamp}"))
            print(f"   ✓ Created Python wrapper: {wrapper_file}")
            
        self.report["actions"].append({
            "task": "standardize_python",
            "status": "completed"
        })
        
    def update_integration_registry(self):
        """Update the integration registry"""
        print("\n📋 Updating integration registry...")
        
        registry_path = Path("infrastructure/integration_registry.json")
        
        # Load existing registry or create new
        if registry_path.exists():
            with open(registry_path, 'r') as f:
                registry = json.load(f)
        else:
            registry = {}
            
        # Update registry
        registry.update({
            "version": "2.0",
            "updated": self.timestamp,
            "infrastructure": {
                "type": "python-only",
                "pulumi_ai": True,
                "esc_environments": ["production", "development"]
            },
            "agents": {
                "sophia_intelligence": {
                    "status": "active",
                    "capabilities": [
                        "competitive_intelligence",
                        "nmhc_targeting",
                        "cost_optimization",
                        "compliance_monitoring"
                    ]
                }
            },
            "workflows": {
                "consolidated": [
                    "infrastructure-orchestrator",
                    "business-intelligence",
                    "secrets-compliance",
                    "emergency-recovery"
                ]
            }
        })
        
        # Write updated registry
        with open(registry_path, 'w') as f:
            json.dump(registry, f, indent=2)
            
        print(f"   ✓ Updated: {registry_path}")
        
        self.report["actions"].append({
            "task": "update_registry",
            "path": str(registry_path)
        })
        
    def generate_report(self):
        """Generate cleanup report"""
        report_file = f"infrastructure_cleanup_report_{self.timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(self.report, f, indent=2)
            
        print("\n" + "=" * 50)
        print("✅ Infrastructure Cleanup Phase 1 Complete!")
        print(f"📊 Report: {report_file}")
        print(f"📁 Archives: {self.archive_dir}")
        
        # Summary
        total_actions = sum(
            action.get("count", 1) 
            for action in self.report["actions"]
        )
        print(f"\n📈 Summary:")
        print(f"   • Total actions: {total_actions}")
        print(f"   • Errors: {len(self.report['errors'])}")
        
        if self.report["errors"]:
            print("\n⚠️  Errors encountered:")
            for error in self.report["errors"]:
                print(f"   • {error}")

if __name__ == "__main__":
    cleanup = InfrastructureCleanup()
    cleanup.run()
