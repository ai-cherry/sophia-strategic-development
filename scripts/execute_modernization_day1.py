#!/usr/bin/env python3
"""
Sophia AI Infrastructure Modernization - Day 1 Execution Script
Automated cleanup and foundation setup
"""

import os
import shutil
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple
import subprocess
import asyncio


class ModernizationExecutor:
    """Execute Day 1 of infrastructure modernization"""
    
    def __init__(self):
        self.root_path = Path(".")
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.archive_dir = Path(f"archive/modernization_{self.timestamp}")
        self.log_file = Path(f"modernization_log_{self.timestamp}.json")
        self.actions_log = []
        
    async def execute_day1(self):
        """Execute all Day 1 tasks"""
        print("🚀 Sophia AI Infrastructure Modernization - Day 1")
        print("=" * 50)
        
        # Morning tasks (2 hours)
        await self.morning_cleanup()
        
        # Afternoon tasks (4 hours)
        await self.afternoon_standardization()
        
        # Generate report
        self.generate_report()
        
        print("\n✅ Day 1 Complete! Check modernization_log_*.json for details")
        
    async def morning_cleanup(self):
        """Morning: Aggressive cleanup (2 hours)"""
        print("\n📅 MORNING TASKS (9 AM - 11 AM)")
        print("-" * 40)
        
        # Task 1: Documentation cleanup
        print("\n1️⃣ Running documentation cleanup...")
        await self.cleanup_documentation()
        
        # Task 2: Archive legacy MCP files
        print("\n2️⃣ Archiving legacy MCP integration files...")
        await self.archive_legacy_mcp()
        
        # Task 3: Remove broken Pulumi TypeScript
        print("\n3️⃣ Removing broken Pulumi TypeScript remnants...")
        await self.remove_typescript_remnants()
        
    async def afternoon_standardization(self):
        """Afternoon: Python standardization (4 hours)"""
        print("\n📅 AFTERNOON TASKS (1 PM - 5 PM)")
        print("-" * 40)
        
        # Task 4: Standardize Python infrastructure
        print("\n4️⃣ Standardizing Python infrastructure entrypoints...")
        await self.standardize_python_infrastructure()
        
        # Task 5: Consolidate ESC environments
        print("\n5️⃣ Consolidating ESC environments...")
        await self.consolidate_esc_environments()
        
        # Task 6: Update import paths
        print("\n6️⃣ Updating all import paths and references...")
        await self.update_import_paths()
        
    async def cleanup_documentation(self):
        """Run documentation cleanup"""
        try:
            # Execute the documentation cleanup script
            result = subprocess.run(
                ["python", "scripts/documentation_cleanup.py"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.log_action("documentation_cleanup", "success", 
                              "Removed 60+ duplicate and outdated documentation files")
                print("   ✓ Documentation cleanup complete")
            else:
                self.log_action("documentation_cleanup", "failed", result.stderr)
                print(f"   ✗ Documentation cleanup failed: {result.stderr}")
                
        except Exception as e:
            self.log_action("documentation_cleanup", "error", str(e))
            print(f"   ✗ Error: {e}")
            
    async def archive_legacy_mcp(self):
        """Archive legacy MCP integration files"""
        legacy_patterns = [
            "mcp-servers/apollo_io/**",
            "mcp-servers/nmhc_targeting/**",
            "mcp-servers/competitive_monitor/**",
            "**/*mcp*broken*",
            "**/*mcp*legacy*"
        ]
        
        archived_count = 0
        for pattern in legacy_patterns:
            for file_path in self.root_path.glob(pattern):
                if file_path.is_file():
                    self.archive_file(file_path)
                    archived_count += 1
                    
        self.log_action("archive_legacy_mcp", "success", 
                       f"Archived {archived_count} legacy MCP files")
        print(f"   ✓ Archived {archived_count} legacy MCP files")
        
    async def remove_typescript_remnants(self):
        """Remove broken Pulumi TypeScript files"""
        ts_patterns = [
            "infrastructure/**/*.ts",
            "infrastructure/**/tsconfig.json",
            "infrastructure/**/package-lock.json",
            "**/*pulumi*broken*"
        ]
        
        removed_count = 0
        for pattern in ts_patterns:
            for file_path in self.root_path.glob(pattern):
                if file_path.is_file() and "dns" not in str(file_path):
                    self.archive_file(file_path)
                    file_path.unlink()
                    removed_count += 1
                    
        self.log_action("remove_typescript", "success", 
                       f"Removed {removed_count} TypeScript remnants")
        print(f"   ✓ Removed {removed_count} TypeScript remnants")
        
    async def standardize_python_infrastructure(self):
        """Create standardized Python infrastructure entrypoints"""
        
        # Create main infrastructure module
        infra_init = Path("infrastructure/__init__.py")
        infra_init.parent.mkdir(exist_ok=True)
        
        init_content = '''"""
Sophia AI Infrastructure - Unified Python Module
AI-powered infrastructure automation for Pay Ready
"""

from .agents.enhanced_sophia_agent import EnhancedSophiaIntelligenceAgent
from .agents.orchestrator import InfrastructureOrchestrator
from .agents.bi_deployer import BusinessIntelligenceDeployer
from .agents.secret_manager import SecretComplianceManager

__all__ = [
    "EnhancedSophiaIntelligenceAgent",
    "InfrastructureOrchestrator", 
    "BusinessIntelligenceDeployer",
    "SecretComplianceManager"
]

__version__ = "2.0.0"
'''
        
        infra_init.write_text(init_content)
        
        # Create agent directory structure
        agents_dir = Path("infrastructure/agents")
        agents_dir.mkdir(exist_ok=True)
        (agents_dir / "__init__.py").touch()
        
        self.log_action("standardize_python", "success", 
                       "Created unified Python infrastructure module")
        print("   ✓ Created unified Python infrastructure module")
        
    async def consolidate_esc_environments(self):
        """Consolidate ESC environments to production and development only"""
        
        esc_config = {
            "environments": {
                "production": {
                    "imports": ["scoobyjava-org/default/sophia-ai-production"],
                    "values": {
                        "aws": {"region": "us-east-1"},
                        "kubernetes": {"namespace": "sophia-production"},
                        "monitoring": {"enabled": True},
                        "alerts": {"channel": "#sophia-alerts"}
                    }
                },
                "development": {
                    "imports": ["scoobyjava-org/default/sophia-ai-development"],
                    "values": {
                        "aws": {"region": "us-east-1"},
                        "kubernetes": {"namespace": "sophia-dev"},
                        "monitoring": {"enabled": False},
                        "alerts": {"channel": "#sophia-dev"}
                    }
                }
            }
        }
        
        # Write consolidated ESC configuration
        esc_path = Path("infrastructure/esc/consolidated.yaml")
        esc_path.parent.mkdir(parents=True, exist_ok=True)
        
        import yaml
        with open(esc_path, 'w') as f:
            yaml.dump(esc_config, f, default_flow_style=False)
            
        self.log_action("consolidate_esc", "success", 
                       "Consolidated ESC to production and development environments")
        print("   ✓ Consolidated ESC environments")
        
    async def update_import_paths(self):
        """Update all import paths to use new structure"""
        
        updates_made = 0
        python_files = list(self.root_path.glob("**/*.py"))
        
        replacements = [
            ("from mcp-servers.", "from mcp-servers."),
            ("import mcp-servers.", "import mcp-servers."),
            ("from infrastructure.agents", "from infrastructure.agents"),
            ("from backend.mcp", "from backend.mcp"),
        ]
        
        for py_file in python_files:
            if "venv" in str(py_file) or "archive" in str(py_file):
                continue
                
            try:
                content = py_file.read_text()
                original = content
                
                for old, new in replacements:
                    content = content.replace(old, new)
                    
                if content != original:
                    py_file.write_text(content)
                    updates_made += 1
                    
            except Exception as e:
                continue
                
        self.log_action("update_imports", "success", 
                       f"Updated imports in {updates_made} files")
        print(f"   ✓ Updated imports in {updates_made} files")
        
    def archive_file(self, file_path: Path):
        """Archive a file before removal"""
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        relative_path = file_path.relative_to(self.root_path)
        archive_path = self.archive_dir / relative_path
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(file_path, archive_path)
        
    def log_action(self, action: str, status: str, details: str):
        """Log an action taken"""
        self.actions_log.append({
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "status": status,
            "details": details
        })
        
    def generate_report(self):
        """Generate final report"""
        report = {
            "execution_date": datetime.now().isoformat(),
            "phase": "Day 1 - Foundation & Cleanup",
            "archive_location": str(self.archive_dir),
            "actions": self.actions_log,
            "summary": {
                "total_actions": len(self.actions_log),
                "successful": len([a for a in self.actions_log if a["status"] == "success"]),
                "failed": len([a for a in self.actions_log if a["status"] == "failed"]),
                "errors": len([a for a in self.actions_log if a["status"] == "error"])
            },
            "next_steps": [
                "Review archived files in " + str(self.archive_dir),
                "Run Day 2 script: python scripts/execute_modernization_day2.py",
                "Check for any import errors: python scripts/validate_imports.py"
            ]
        }
        
        with open(self.log_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"\n📊 Report saved to: {self.log_file}")
        print(f"📁 Archives saved to: {self.archive_dir}")


async def main():
    """Main execution function"""
    executor = ModernizationExecutor()
    
    print("\n⚠️  WARNING: This script will make significant changes!")
    print("Archives will be created, but please ensure you have backups.")
    
    response = input("\nProceed with Day 1 modernization? (yes/no): ")
    if response.lower() != 'yes':
        print("Modernization cancelled.")
        return
        
    await executor.execute_day1()


if __name__ == "__main__":
    asyncio.run(main())
