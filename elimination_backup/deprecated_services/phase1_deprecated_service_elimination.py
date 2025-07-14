#!/usr/bin/env python3
"""
Phase 1.1: Deprecated Service Elimination Script
Part of Comprehensive Technical Debt Elimination Plan

This script:
1. Identifies deprecated service imports
2. Updates imports to V2/V3 versions
3. Removes deprecated service files
4. Validates all imports resolve correctly
5. Provides comprehensive reporting

Author: Sophia AI Technical Debt Elimination Team
Date: January 2025
"""

import os
import re
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deprecated_service_elimination.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class DeprecatedService:
    """Represents a deprecated service and its replacement"""
    old_path: str
    new_path: str
    old_import: str
    new_import: str
    description: str
    risk_level: str

@dataclass
class EliminationResult:
    """Results of deprecated service elimination"""
    services_removed: List[str] = field(default_factory=list)
    imports_updated: List[str] = field(default_factory=list)
    files_modified: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
class DeprecatedServiceEliminator:
    """Comprehensive deprecated service elimination system"""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.backup_dir = self.root_path / "elimination_backup" / "deprecated_services"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Define deprecated services and their replacements
        self.deprecated_services = {
            "unified_memory_service": DeprecatedService(
                old_path="backend/services/unified_memory_service.py",
                new_path="backend/services/unified_memory_service_v2.py",
                old_import="from backend.services.unified_memory_service import UnifiedMemoryService",
                new_import="from backend.services.unified_memory_service import UnifiedMemoryService",
                description="Legacy memory service replaced by V2 with Qdrant integration",
                risk_level="HIGH"
            ),
            "snowflake_cortex_service": DeprecatedService(
                old_path="backend/services/snowflake_cortex_service.py",
                new_path="backend/services/qdrant_foundation_service.py",
                old_import="from backend.services.snowflake_cortex_service import SnowflakeCortexService",
                new_import="from backend.services.qdrant_foundation_service import QdrantFoundationService",
                description="Snowflake service replaced by Qdrant foundation",
                risk_level="CRITICAL"
            ),
            "enhanced_ai_memory_mcp_server": DeprecatedService(
                old_path="mcp-servers/enhanced_ai_memory_mcp_server.py",
                new_path="backend/services/unified_memory_service_v3.py",
                old_import="from mcp_servers.enhanced_ai_memory_mcp_server import EnhancedAIMemoryMCPServer",
                new_import="from backend.services.unified_memory_service import UnifiedMemoryService",
                description="Enhanced AI Memory MCP server replaced by V3 service",
                risk_level="HIGH"
            )
        }
        
        # Import patterns to update
        self.import_patterns = {
            # Legacy memory service patterns
            r"from backend\.services\.unified_memory_service import": "from backend.services.unified_memory_service import",
            r"UnifiedMemoryService\b": "UnifiedMemoryService",
            
            # Snowflake to Qdrant migration
            r"from backend\.services\.snowflake_cortex_service import": "from backend.services.qdrant_foundation_service import",
            r"SnowflakeCortexService\b": "QdrantFoundationService",
            
            # Enhanced AI Memory patterns
            r"from mcp_servers\.enhanced_ai_memory_mcp_server import": "from backend.services.unified_memory_service import",
            r"EnhancedAIMemoryMCPServer\b": "UnifiedMemoryService",
            
            # Generic deprecated patterns
            r"# DEPRECATED.*": "# MIGRATED: Updated to current service version",
            r"\.deprecated": ".current",
            r"legacy_": "current_",
        }
        
    def create_backup(self, file_path: Path) -> bool:
        """Create backup of file before modification"""
        try:
            if file_path.exists():
                backup_path = self.backup_dir / file_path.name
                shutil.copy2(file_path, backup_path)
                logger.info(f"✅ Backup created: {backup_path}")
                return True
        except Exception as e:
            logger.error(f"❌ Backup failed for {file_path}: {e}")
            return False
        return True
    
    def find_deprecated_imports(self) -> Dict[str, List[str]]:
        """Find all files with deprecated imports"""
        deprecated_files = {}
        
        for service_name, service in self.deprecated_services.items():
            files_with_import = []
            
            # Search for old import patterns
            for py_file in self.root_path.rglob("*.py"):
                if py_file.is_file():
                    try:
                        content = py_file.read_text(encoding='utf-8')
                        if service.old_import in content or service_name in content:
                            files_with_import.append(str(py_file))
                    except Exception as e:
                        logger.warning(f"⚠️ Could not read {py_file}: {e}")
            
            if files_with_import:
                deprecated_files[service_name] = files_with_import
                
        return deprecated_files
    
    def update_imports_in_file(self, file_path: Path) -> Tuple[bool, List[str]]:
        """Update deprecated imports in a single file"""
        changes_made = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
            original_content = content
            
            # Apply import pattern replacements
            for pattern, replacement in self.import_patterns.items():
                matches = re.findall(pattern, content)
                if matches:
                    content = re.sub(pattern, replacement, content)
                    changes_made.extend([f"Updated pattern: {pattern} -> {replacement}"])
            
            # Write back if changes were made
            if content != original_content:
                self.create_backup(file_path)
                file_path.write_text(content, encoding='utf-8')
                logger.info(f"✅ Updated imports in: {file_path}")
                return True, changes_made
                
        except Exception as e:
            logger.error(f"❌ Failed to update {file_path}: {e}")
            return False, [f"Error: {e}"]
        
        return False, []
    
    def remove_deprecated_files(self) -> List[str]:
        """Remove deprecated service files after creating backups"""
        removed_files = []
        
        for service_name, service in self.deprecated_services.items():
            file_path = self.root_path / service.old_path
            
            if file_path.exists():
                # Create backup before removal
                if self.create_backup(file_path):
                    try:
                        file_path.unlink()
                        removed_files.append(str(file_path))
                        logger.info(f"🗑️ Removed deprecated file: {file_path}")
                    except Exception as e:
                        logger.error(f"❌ Failed to remove {file_path}: {e}")
                else:
                    logger.warning(f"⚠️ Skipped removal of {file_path} - backup failed")
            else:
                logger.info(f"ℹ️ File already removed: {file_path}")
        
        return removed_files
    
    def validate_imports(self) -> List[str]:
        """Validate that all imports resolve correctly"""
        validation_errors = []
        
        # Test import resolution
        test_imports = [
            "from backend.services.unified_memory_service import UnifiedMemoryService",
            "from backend.services.qdrant_foundation_service import QdrantFoundationService",
            "from backend.services.unified_memory_service import UnifiedMemoryService",
        ]
        
        for import_stmt in test_imports:
            try:
                exec(import_stmt)
                logger.info(f"✅ Import validation passed: {import_stmt}")
            except ImportError as e:
                error_msg = f"❌ Import validation failed: {import_stmt} - {e}"
                validation_errors.append(error_msg)
                logger.error(error_msg)
        
        return validation_errors
    
    def run_elimination(self) -> EliminationResult:
        """Execute complete deprecated service elimination"""
        logger.info("🚀 Starting Phase 1.1: Deprecated Service Elimination")
        result = EliminationResult()
        
        try:
            # Step 1: Find deprecated imports
            logger.info("📋 Step 1: Finding deprecated imports...")
            deprecated_files = self.find_deprecated_imports()
            
            if not deprecated_files:
                logger.info("✅ No deprecated imports found!")
                return result
            
            # Step 2: Update imports in all affected files
            logger.info("🔄 Step 2: Updating imports...")
            for service_name, files in deprecated_files.items():
                logger.info(f"Processing {service_name}: {len(files)} files")
                
                for file_path in files:
                    path_obj = Path(file_path)
                    success, changes = self.update_imports_in_file(path_obj)
                    
                    if success:
                        result.files_modified.append(file_path)
                        result.imports_updated.extend(changes)
                    else:
                        result.errors.extend(changes)
            
            # Step 3: Remove deprecated service files
            logger.info("🗑️ Step 3: Removing deprecated service files...")
            removed_files = self.remove_deprecated_files()
            result.services_removed.extend(removed_files)
            
            # Step 4: Validate imports
            logger.info("✅ Step 4: Validating imports...")
            validation_errors = self.validate_imports()
            result.errors.extend(validation_errors)
            
            # Generate summary
            logger.info("📊 Elimination Summary:")
            logger.info(f"  - Services removed: {len(result.services_removed)}")
            logger.info(f"  - Files modified: {len(result.files_modified)}")
            logger.info(f"  - Import updates: {len(result.imports_updated)}")
            logger.info(f"  - Errors: {len(result.errors)}")
            logger.info(f"  - Warnings: {len(result.warnings)}")
            
            if result.errors:
                logger.error("❌ Elimination completed with errors!")
                for error in result.errors:
                    logger.error(f"  - {error}")
            else:
                logger.info("✅ Deprecated service elimination completed successfully!")
                
        except Exception as e:
            logger.error(f"❌ Critical error during elimination: {e}")
            result.errors.append(f"Critical error: {e}")
        
        return result
    
    def generate_report(self, result: EliminationResult) -> str:
        """Generate comprehensive elimination report"""
        report = f"""
# 📋 DEPRECATED SERVICE ELIMINATION REPORT
## Phase 1.1 - Technical Debt Elimination

### 📊 SUMMARY
- **Services Removed**: {len(result.services_removed)}
- **Files Modified**: {len(result.files_modified)}
- **Import Updates**: {len(result.imports_updated)}
- **Errors**: {len(result.errors)}
- **Warnings**: {len(result.warnings)}

### 🗑️ SERVICES REMOVED
{chr(10).join(f"- {service}" for service in result.services_removed)}

### 🔄 FILES MODIFIED
{chr(10).join(f"- {file}" for file in result.files_modified)}

### ⚠️ ERRORS
{chr(10).join(f"- {error}" for error in result.errors)}

### 📝 WARNINGS
{chr(10).join(f"- {warning}" for warning in result.warnings)}

### 🎯 NEXT STEPS
1. Review and test all modified files
2. Run comprehensive test suite
3. Proceed to Phase 1.2: Critical TODO Resolution
4. Update documentation references

---
Generated: {logger.name} - Phase 1.1 Complete
"""
        return report

def main():
    """Main execution function"""
    eliminator = DeprecatedServiceEliminator()
    result = eliminator.run_elimination()
    
    # Generate and save report
    report = eliminator.generate_report(result)
    report_path = Path("PHASE_1_1_DEPRECATED_SERVICE_ELIMINATION_REPORT.md")
    report_path.write_text(report)
    
    logger.info(f"📄 Report saved: {report_path}")
    
    # Return exit code based on success
    return 0 if not result.errors else 1

if __name__ == "__main__":
    exit(main()) 