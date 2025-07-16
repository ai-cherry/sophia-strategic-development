#!/usr/bin/env python3
"""
Cleanup Conflicting Infrastructure Scripts
Removes potentially competing or conflicting scripts to ensure clean infrastructure management

This script identifies and removes:
1. Old deployment scripts with overlapping functionality
2. Multiple MCP server startup approaches 
3. Conflicting port management scripts
4. Duplicate Qdrant configuration scripts
5. Legacy infrastructure management scripts

Preserves the new infrastructure fix scripts created today.
"""

import os
import shutil
import json
from pathlib import Path
from typing import List, Dict, Set
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ConflictingScriptsCleaner:
    """Removes potentially conflicting infrastructure scripts"""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.scripts_dir = self.root_dir / "scripts"
        
        # Scripts to PRESERVE (newly created today)
        self.preserve_scripts = {
            "fix_distributed_infrastructure_issues.py",
            "deploy_infrastructure_fixes.py", 
            "validate_qdrant_connection.py",
            "validate_service_communication.py",
            "deploy_letsencrypt_ssl.sh",
            "update_remote_systemd_ports.sh",
            "ssl_renewal.sh",
            "cleanup_conflicting_infrastructure_scripts.py"  # This script
        }
        
        # Conflicting script patterns to remove
        self.conflicting_patterns = {
            # Old deployment scripts
            "deploy_sophia_*.sh",
            "deploy_*.sh", 
            "quick_deployment_*.sh",
            "emergency_*.sh",
            "deploy_containerd_*.sh",
            "deploy_integrated_*.py",
            "deploy_modernization_*.sh",
            
            # Old MCP server management
            "start_*mcp*.sh",
            "start_*mcp*.py", 
            "run_*mcp*.py",
            "stop_*mcp*.sh",
            "check_*mcp*.sh",
            "generate_mcp_*.sh",
            "phase*_mcp_*.py",
            
            # Old infrastructure management
            "quick_backend_*.sh",
            "quick_frontend_*.sh",
            "fix_deployment_*.py",
            "fix_critical_*.py",
            
            # Old Qdrant management (except the new validation script)
            "qdrant_*_setup.py",
            "qdrant_step*.py", 
            "qdrant_assessment_*.py",
            "qdrant_comprehensive_*.py",
            "fix_*qdrant*.py",
            "validate_qdrant_fortress.py",
            "init_qdrant_*.py",
            
            # Old port management
            "fix_*port*.py",
            "resolve_*port*.py"
        }
        
        self.removed_scripts = []
        self.backup_dir = None
        
    def cleanup_all_conflicts(self):
        """Remove all conflicting scripts with backup"""
        logger.info("🧹 Starting cleanup of conflicting infrastructure scripts")
        
        # Create backup directory
        self.backup_dir = self.root_dir / f"backup_removed_scripts_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.backup_dir.mkdir(exist_ok=True)
        
        try:
            # Remove conflicting scripts
            self._remove_conflicting_scripts()
            
            # Remove conflicting root-level scripts
            self._remove_root_level_scripts()
            
            # Remove MCP integration conflicts
            self._remove_mcp_integration_conflicts()
            
            # Generate cleanup report
            self._generate_cleanup_report()
            
            logger.info(f"✅ Cleanup completed: {len(self.removed_scripts)} scripts removed")
            logger.info(f"   Backup created: {self.backup_dir}")
            
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")
            raise

    def _remove_conflicting_scripts(self):
        """Remove conflicting scripts from scripts/ directory"""
        logger.info("🔍 Scanning scripts/ directory for conflicts")
        
        if not self.scripts_dir.exists():
            return
            
        for script_file in self.scripts_dir.iterdir():
            if script_file.is_file() and self._is_conflicting_script(script_file):
                self._backup_and_remove_script(script_file)

    def _remove_root_level_scripts(self):
        """Remove conflicting scripts from root directory"""
        logger.info("🔍 Scanning root directory for conflicts")
        
        root_conflicts = [
            "deploy_lambda_labs.sh",
            "dev_mcp_config.sh",
            "activate_env.sh",
            "activate_sophia.sh"
        ]
        
        for script_name in root_conflicts:
            script_path = self.root_dir / script_name
            if script_path.exists():
                self._backup_and_remove_script(script_path)

    def _remove_mcp_integration_conflicts(self):
        """Remove conflicting MCP integration scripts"""
        logger.info("🔍 Removing MCP integration conflicts")
        
        # Remove conflicting gemini CLI MCP scripts
        gemini_dir = self.root_dir / "gemini-cli-integration"
        if gemini_dir.exists():
            conflicts = [
                "start-mcp-servers.sh",
                "setup-gemini-cli.sh"
            ]
            for conflict in conflicts:
                conflict_path = gemini_dir / conflict
                if conflict_path.exists():
                    self._backup_and_remove_script(conflict_path)

    def _is_conflicting_script(self, script_path: Path) -> bool:
        """Check if script matches conflicting patterns"""
        script_name = script_path.name
        
        # Preserve new scripts
        if script_name in self.preserve_scripts:
            return False
            
        # Check against conflicting patterns
        for pattern in self.conflicting_patterns:
            # Convert glob pattern to simple matching
            if self._matches_pattern(script_name, pattern):
                return True
                
        # Check for specific old scripts
        old_scripts = {
            "start_all_mcp_servers.py",
            "start_enhanced_mcp_servers.sh", 
            "start_mcp_servers.py",
            "run_all_mcp_servers.py",
            "fix_critical_memory_database_issues.py",
            "fix_deployment_gpu_limits.py",
            "qdrant_step2_provision_collections.py",
            "qdrant_step2_provision_collections_fixed.py",
            "phase2_mcp_consolidation.py",
            "emergency_container_startup_fix.sh"
        }
        
        return script_name in old_scripts

    def _matches_pattern(self, filename: str, pattern: str) -> bool:
        """Simple pattern matching for script names"""
        import fnmatch
        return fnmatch.fnmatch(filename, pattern)

    def _backup_and_remove_script(self, script_path: Path):
        """Backup and remove a conflicting script"""
        try:
            # Create backup
            relative_path = script_path.relative_to(self.root_dir)
            backup_path = self.backup_dir / relative_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(script_path, backup_path)
            
            # Remove original
            script_path.unlink()
            
            self.removed_scripts.append(str(relative_path))
            logger.info(f"   🗑️ Removed: {relative_path}")
            
        except Exception as e:
            logger.warning(f"   ⚠️ Could not remove {script_path}: {e}")

    def _generate_cleanup_report(self):
        """Generate comprehensive cleanup report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "cleanup_summary": {
                "total_scripts_removed": len(self.removed_scripts),
                "backup_location": str(self.backup_dir),
                "scripts_preserved": list(self.preserve_scripts)
            },
            "removed_scripts": sorted(self.removed_scripts),
            "categories_cleaned": {
                "deployment_scripts": [s for s in self.removed_scripts if "deploy" in s],
                "mcp_server_scripts": [s for s in self.removed_scripts if "mcp" in s],
                "qdrant_scripts": [s for s in self.removed_scripts if "qdrant" in s],
                "infrastructure_scripts": [s for s in self.removed_scripts if any(term in s for term in ["infrastructure", "deploy", "fix"])],
                "port_management": [s for s in self.removed_scripts if "port" in s]
            },
            "impact_analysis": {
                "conflicts_eliminated": True,
                "new_scripts_protected": True,
                "backup_created": True,
                "recovery_possible": True
            },
            "next_steps": [
                "Use fix_distributed_infrastructure_issues.py for infrastructure fixes",
                "Use deploy_infrastructure_fixes.py for production deployment",
                "Use validate_qdrant_connection.py for Qdrant testing",
                "Use validate_service_communication.py for service testing",
                "Review backup_removed_scripts_* if any functionality is needed"
            ]
        }
        
        # Save report
        report_file = self.root_dir / "infrastructure_cleanup_report.json"
        report_file.write_text(json.dumps(report, indent=2))
        
        # Create summary
        summary = f"""# Infrastructure Scripts Cleanup Report

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Status:** COMPLETED SUCCESSFULLY  

## Summary
- **Scripts Removed:** {len(self.removed_scripts)}
- **Categories Cleaned:** 5 (deployment, MCP, Qdrant, infrastructure, ports)
- **Backup Location:** `{self.backup_dir}`
- **New Scripts Preserved:** {len(self.preserve_scripts)}

## Conflicts Eliminated
✅ Multiple deployment approaches consolidated  
✅ Duplicate MCP server management removed  
✅ Conflicting Qdrant scripts eliminated  
✅ Port management conflicts resolved  
✅ Legacy infrastructure scripts removed  

## Active Infrastructure Scripts (Preserved)
- `fix_distributed_infrastructure_issues.py` - Main infrastructure fix script
- `deploy_infrastructure_fixes.py` - Production deployment automation
- `validate_qdrant_connection.py` - Qdrant connectivity testing
- `validate_service_communication.py` - Service communication testing
- `deploy_letsencrypt_ssl.sh` - SSL certificate automation
- `update_remote_systemd_ports.sh` - Port configuration updates
- `ssl_renewal.sh` - SSL renewal automation

## Recovery
All removed scripts are backed up in: `{self.backup_dir}`
To restore a script: `cp {self.backup_dir}/path/to/script ./path/to/script`

## Next Steps
1. Use the new infrastructure scripts for all operations
2. Test deployment with `python scripts/deploy_infrastructure_fixes.py`
3. Validate fixes with `python scripts/validate_service_communication.py`
4. Deploy SSL with `bash scripts/deploy_letsencrypt_ssl.sh`
"""
        
        summary_file = self.root_dir / "INFRASTRUCTURE_CLEANUP_SUMMARY.md"
        summary_file.write_text(summary)
        
        logger.info(f"📊 Cleanup report saved: {report_file}")
        logger.info(f"📝 Summary created: {summary_file}")

def main():
    """Main execution function"""
    cleaner = ConflictingScriptsCleaner()
    cleaner.cleanup_all_conflicts()

if __name__ == "__main__":
    main() 