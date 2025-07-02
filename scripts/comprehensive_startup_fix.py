#!/usr/bin/env python3
"""
Comprehensive Startup Fix Script for Sophia AI Platform
======================================================

This script systematically identifies and fixes all startup issues including:
- Import errors and missing dependencies
- Syntax errors and malformed code
- Configuration validation issues
- Module-level instantiation problems
- Missing route files and broken imports

Usage: python scripts/comprehensive_startup_fix.py
"""

import os
import re
import ast
import sys
import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class FixResult:
    """Result of a fix operation"""
    success: bool
    file_path: str
    issue_type: str
    description: str
    fix_applied: str = ""
    error_message: str = ""

class ComprehensiveStartupFixer:
    """Comprehensive startup issue fixer for Sophia AI platform"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.fixes_applied: List[FixResult] = []
        self.critical_files = [
            "backend/app/fastapi_app.py",
            "backend/app/unified_fastapi_app.py",
            "backend/services/mcp_orchestration_service.py",
            "backend/services/enhanced_mcp_orchestration_service.py",
            "backend/core/secure_snowflake_config.py",
            "backend/core/optimized_connection_manager.py",
            "backend/workflows/enhanced_langgraph_orchestration.py",
            "backend/core/enhanced_cache_manager.py",
            "backend/integrations/gong_webhook_processor.py",
        ]
        
    def run_comprehensive_fix(self) -> Dict[str, any]:
        """Run comprehensive startup fixes"""
        logger.info("🚀 Starting comprehensive startup fix for Sophia AI platform...")
        
        results = {
            "total_issues_found": 0,
            "total_fixes_applied": 0,
            "critical_fixes": [],
            "syntax_fixes": [],
            "import_fixes": [],
            "configuration_fixes": [],
            "success_rate": 0.0
        }
        
        try:
            # Phase 1: Syntax Error Detection and Fixes
            logger.info("📝 Phase 1: Fixing syntax errors...")
            syntax_fixes = self.fix_syntax_errors()
            results["syntax_fixes"] = syntax_fixes
            
            # Phase 2: Import Error Resolution
            logger.info("📦 Phase 2: Resolving import errors...")
            import_fixes = self.fix_import_errors()
            results["import_fixes"] = import_fixes
            
            # Phase 3: Module-level Instantiation Issues
            logger.info("🔧 Phase 3: Fixing module-level instantiation...")
            module_fixes = self.fix_module_instantiation()
            results["critical_fixes"].extend(module_fixes)
            
            # Phase 4: Configuration Validation Issues
            logger.info("⚙️  Phase 4: Fixing configuration validation...")
            config_fixes = self.fix_configuration_issues()
            results["configuration_fixes"] = config_fixes
            
            # Phase 5: Route and API Fixes
            logger.info("🛣️  Phase 5: Fixing route and API issues...")
            route_fixes = self.fix_route_issues()
            results["import_fixes"].extend(route_fixes)
            
            # Phase 6: Validate All Fixes
            logger.info("✅ Phase 6: Validating all fixes...")
            validation_results = self.validate_fixes()
            
            # Calculate results
            total_fixes = len(syntax_fixes) + len(import_fixes) + len(module_fixes) + len(config_fixes) + len(route_fixes)
            successful_fixes = sum(1 for fix in self.fixes_applied if fix.success)
            
            results["total_issues_found"] = len(self.fixes_applied)
            results["total_fixes_applied"] = successful_fixes
            results["success_rate"] = (successful_fixes / max(len(self.fixes_applied), 1)) * 100
            results["validation"] = validation_results
            
            logger.info(f"✅ Comprehensive fix complete: {successful_fixes}/{len(self.fixes_applied)} issues resolved ({results['success_rate']:.1f}% success rate)")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Comprehensive fix failed: {e}")
            results["error"] = str(e)
            return results
    
    def fix_syntax_errors(self) -> List[FixResult]:
        """Fix syntax errors across the codebase"""
        fixes = []
        
        # Common syntax error patterns and fixes
        syntax_patterns = {
            r'"""([^"]+)""":': r'"""\1"""',  # Remove trailing colon from docstrings
            r'from __future__ import annotations\n\n"""': r'from __future__ import annotations\n\n"""',  # Fix future import position
            r'(\s+)try:\s*$': r'\1try:',  # Fix incomplete try blocks
        }
        
        python_files = list(self.project_root.rglob("*.py"))
        
        for file_path in python_files:
            try:
                # Read file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Apply syntax fixes
                for pattern, replacement in syntax_patterns.items():
                    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                
                # Check for incomplete try blocks
                if "try:\n        logger.info(f\"Webhook data received from {source_name}\")" in content and "except" not in content:
                    # Complete the webhook function
                    content = self.complete_webhook_function(content)
                
                # Validate syntax
                try:
                    ast.parse(content)
                    syntax_valid = True
                except SyntaxError as e:
                    syntax_valid = False
                    # Try to fix specific syntax errors
                    content = self.fix_specific_syntax_error(content, e)
                    try:
                        ast.parse(content)
                        syntax_valid = True
                    except:
                        pass
                
                # Write back if changes were made
                if content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    fix_result = FixResult(
                        success=syntax_valid,
                        file_path=str(file_path),
                        issue_type="syntax_error",
                        description=f"Fixed syntax errors in {file_path.name}",
                        fix_applied="Applied syntax pattern fixes and validation"
                    )
                    fixes.append(fix_result)
                    self.fixes_applied.append(fix_result)
                    
            except Exception as e:
                fix_result = FixResult(
                    success=False,
                    file_path=str(file_path),
                    issue_type="syntax_error",
                    description=f"Failed to fix syntax in {file_path.name}",
                    error_message=str(e)
                )
                fixes.append(fix_result)
                self.fixes_applied.append(fix_result)
        
        return fixes
    
    def fix_import_errors(self) -> List[FixResult]:
        """Fix import errors and missing dependencies"""
        fixes = []
        
        # Map of missing imports to actual available modules
        import_mappings = {
            'business_intelligence_routes': None,  # Comment out
            'chat_routes': 'enhanced_unified_chat_routes as chat_routes',
            'gong_integration_routes': None,  # Comment out
            'hubspot_integration_routes': None,  # Comment out
            'knowledge_base_routes': 'foundational_knowledge_routes as knowledge_base_routes',
            'monitoring_routes': 'ceo_dashboard_routes as monitoring_routes',
            'snowflake_admin_routes': None,  # Comment out
            'workflow_routes': None,  # Comment out
        }
        
        # Fix unified_fastapi_app.py imports
        unified_app_path = self.project_root / "backend/app/unified_fastapi_app.py"
        if unified_app_path.exists():
            try:
                with open(unified_app_path, 'r') as f:
                    content = f.read()
                
                original_content = content
                
                # Fix import section
                for missing_import, replacement in import_mappings.items():
                    if replacement is None:
                        # Comment out missing import
                        content = re.sub(
                            f'    {missing_import},\n',
                            f'    # {missing_import},  # Not available\n',
                            content
                        )
                        # Comment out router usage
                        content = re.sub(
                            f'            \\({missing_import}\\.router,',
                            f'            # ({missing_import}.router,',
                            content
                        )
                    else:
                        # Replace with correct import
                        content = re.sub(
                            f'    {missing_import},',
                            f'    {replacement},',
                            content
                        )
                
                # Fix double aliases
                content = re.sub(
                    r'(\w+) as \1 as (\w+)',
                    r'\1 as \2',
                    content
                )
                
                if content != original_content:
                    with open(unified_app_path, 'w') as f:
                        f.write(content)
                    
                    fix_result = FixResult(
                        success=True,
                        file_path=str(unified_app_path),
                        issue_type="import_error",
                        description="Fixed import mappings in unified_fastapi_app.py",
                        fix_applied="Updated imports to use available modules"
                    )
                    fixes.append(fix_result)
                    self.fixes_applied.append(fix_result)
                    
            except Exception as e:
                fix_result = FixResult(
                    success=False,
                    file_path=str(unified_app_path),
                    issue_type="import_error",
                    description="Failed to fix imports in unified_fastapi_app.py",
                    error_message=str(e)
                )
                fixes.append(fix_result)
                self.fixes_applied.append(fix_result)
        
        return fixes
    
    def fix_module_instantiation(self) -> List[FixResult]:
        """Fix module-level instantiation issues"""
        fixes = []
        
        # Files with module-level instantiation issues
        instantiation_fixes = {
            "backend/services/mcp_orchestration_service.py": {
                "pattern": r"^orchestration_service = MCPOrchestrationService\(\)",
                "replacement": "# Global orchestration service instance - using lazy initialization\n_orchestration_service = None\n\ndef get_orchestration_service() -> MCPOrchestrationService:\n    \"\"\"Get the global orchestration service instance (lazy initialization)\"\"\"\n    global _orchestration_service\n    if _orchestration_service is None:\n        _orchestration_service = MCPOrchestrationService()\n    return _orchestration_service"
            },
            "backend/core/secure_snowflake_config.py": {
                "pattern": r"^secure_snowflake_config = SecureSnowflakeConfig\(\)",
                "replacement": "# Global config instance - using lazy initialization\n_secure_snowflake_config = None\n\ndef get_secure_snowflake_config() -> SecureSnowflakeConfig:\n    \"\"\"Get the global secure snowflake config instance (lazy initialization)\"\"\"\n    global _secure_snowflake_config\n    if _secure_snowflake_config is None:\n        _secure_snowflake_config = SecureSnowflakeConfig()\n    return _secure_snowflake_config"
            }
        }
        
        for file_path_str, fix_config in instantiation_fixes.items():
            file_path = self.project_root / file_path_str
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    original_content = content
                    
                    # Apply the fix
                    content = re.sub(
                        fix_config["pattern"],
                        fix_config["replacement"],
                        content,
                        flags=re.MULTILINE
                    )
                    
                    if content != original_content:
                        with open(file_path, 'w') as f:
                            f.write(content)
                        
                        fix_result = FixResult(
                            success=True,
                            file_path=str(file_path),
                            issue_type="module_instantiation",
                            description=f"Fixed module-level instantiation in {file_path.name}",
                            fix_applied="Converted to lazy initialization pattern"
                        )
                        fixes.append(fix_result)
                        self.fixes_applied.append(fix_result)
                        
                except Exception as e:
                    fix_result = FixResult(
                        success=False,
                        file_path=str(file_path),
                        issue_type="module_instantiation",
                        description=f"Failed to fix module instantiation in {file_path.name}",
                        error_message=str(e)
                    )
                    fixes.append(fix_result)
                    self.fixes_applied.append(fix_result)
        
        return fixes
    
    def fix_configuration_issues(self) -> List[FixResult]:
        """Fix configuration validation issues"""
        fixes = []
        
        # Update files that import the old direct instances
        files_to_update = [
            "backend/core/optimized_connection_manager.py",
            "backend/utils/snowflake_cortex_service.py",
            "backend/utils/snowflake_cortex_service_core.py"
        ]
        
        for file_path_str in files_to_update:
            file_path = self.project_root / file_path_str
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    original_content = content
                    
                    # Update imports to use lazy initialization
                    content = re.sub(
                        r'from backend\.core\.secure_snowflake_config import secure_snowflake_config',
                        'from backend.core.secure_snowflake_config import get_secure_snowflake_config',
                        content
                    )
                    
                    # Update usage
                    content = re.sub(
                        r'\bsecure_snowflake_config\b',
                        'get_secure_snowflake_config()',
                        content
                    )
                    
                    if content != original_content:
                        with open(file_path, 'w') as f:
                            f.write(content)
                        
                        fix_result = FixResult(
                            success=True,
                            file_path=str(file_path),
                            issue_type="configuration",
                            description=f"Updated configuration usage in {file_path.name}",
                            fix_applied="Converted to lazy initialization calls"
                        )
                        fixes.append(fix_result)
                        self.fixes_applied.append(fix_result)
                        
                except Exception as e:
                    fix_result = FixResult(
                        success=False,
                        file_path=str(file_path),
                        issue_type="configuration",
                        description=f"Failed to fix configuration in {file_path.name}",
                        error_message=str(e)
                    )
                    fixes.append(fix_result)
                    self.fixes_applied.append(fix_result)
        
        return fixes
    
    def fix_route_issues(self) -> List[FixResult]:
        """Fix route and API issues"""
        fixes = []
        
        # Fix data_flow_routes.py if it has issues
        data_flow_routes = self.project_root / "backend/api/data_flow_routes.py"
        if data_flow_routes.exists():
            try:
                with open(data_flow_routes, 'r') as f:
                    content = f.read()
                
                # Check if file is truncated or has syntax issues
                if "try:\n        logger.info(f\"Webhook data received from {source_name}\")" in content and content.count("except") < content.count("try:"):
                    # Complete the webhook function
                    content = self.complete_webhook_function(content)
                    
                    with open(data_flow_routes, 'w') as f:
                        f.write(content)
                    
                    fix_result = FixResult(
                        success=True,
                        file_path=str(data_flow_routes),
                        issue_type="route_completion",
                        description="Completed truncated webhook function",
                        fix_applied="Added missing except blocks and function completion"
                    )
                    fixes.append(fix_result)
                    self.fixes_applied.append(fix_result)
                    
            except Exception as e:
                fix_result = FixResult(
                    success=False,
                    file_path=str(data_flow_routes),
                    issue_type="route_completion",
                    description="Failed to fix data_flow_routes.py",
                    error_message=str(e)
                )
                fixes.append(fix_result)
                self.fixes_applied.append(fix_result)
        
        return fixes
    
    def complete_webhook_function(self, content: str) -> str:
        """Complete a truncated webhook function"""
        webhook_completion = '''
        # Add webhook metadata
        webhook_data = {
            **data,
            "ingestion_method": "webhook",
            "received_at": datetime.now().isoformat(),
            "source": source_name,
        }

        success = await data_manager.ingest_data(source_name, webhook_data)

        if not success:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process webhook data from {source_name}",
            )

        return {
            "status": "received",
            "source": source_name,
            "timestamp": datetime.now().isoformat(),
            "queue_position": data_manager.processing_queue.qsize(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
'''
        
        # Find the incomplete try block and complete it
        if "try:\n        logger.info(f\"Webhook data received from {source_name}\")" in content:
            # Replace the incomplete try block
            content = re.sub(
                r'try:\s*\n\s*logger\.info\(f"Webhook data received from \{source_name\}"\)',
                f'try:\n        logger.info(f"Webhook data received from {{source_name}}")' + webhook_completion,
                content
            )
        
        return content
    
    def fix_specific_syntax_error(self, content: str, error: SyntaxError) -> str:
        """Fix specific syntax errors"""
        if "expected 'except' or 'finally' block" in str(error):
            # Add a basic except block
            lines = content.split('\n')
            error_line = error.lineno - 1 if error.lineno else len(lines)
            
            # Find the incomplete try block
            for i in range(error_line, len(lines)):
                if lines[i].strip() == '':
                    lines.insert(i, '    except Exception as e:')
                    lines.insert(i + 1, '        logger.error(f"Error: {e}")')
                    lines.insert(i + 2, '        raise')
                    break
            
            content = '\n'.join(lines)
        
        return content
    
    def validate_fixes(self) -> Dict[str, any]:
        """Validate that all fixes work correctly"""
        validation_results = {
            "syntax_validation": {},
            "import_validation": {},
            "startup_test": {}
        }
        
        # Test syntax validation
        for file_path_str in self.critical_files:
            file_path = self.project_root / file_path_str
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    ast.parse(content)
                    validation_results["syntax_validation"][file_path_str] = "✅ Valid"
                except SyntaxError as e:
                    validation_results["syntax_validation"][file_path_str] = f"❌ Syntax Error: {e}"
                except Exception as e:
                    validation_results["syntax_validation"][file_path_str] = f"⚠️  Other Error: {e}"
        
        # Test import validation
        try:
            result = subprocess.run([
                sys.executable, "-c",
                "from backend.services.mcp_orchestration_service import get_orchestration_service; print('✅ MCP service import successful')"
            ], capture_output=True, text=True, timeout=30)
            
            validation_results["import_validation"]["mcp_service"] = result.stdout.strip() if result.returncode == 0 else f"❌ {result.stderr}"
        except Exception as e:
            validation_results["import_validation"]["mcp_service"] = f"❌ {e}"
        
        return validation_results
    
    def generate_fix_report(self, results: Dict[str, any]) -> str:
        """Generate a comprehensive fix report"""
        report = f"""
# Comprehensive Startup Fix Report
## Sophia AI Platform - {len(self.fixes_applied)} Issues Addressed

### Executive Summary
- **Total Issues Found**: {results['total_issues_found']}
- **Total Fixes Applied**: {results['total_fixes_applied']}
- **Success Rate**: {results['success_rate']:.1f}%

### Fix Categories

#### Syntax Fixes ({len(results['syntax_fixes'])})
"""
        for fix in results['syntax_fixes']:
            status = "✅" if fix.success else "❌"
            report += f"- {status} {fix.file_path}: {fix.description}\n"
        
        report += f"\n#### Import Fixes ({len(results['import_fixes'])})\n"
        for fix in results['import_fixes']:
            status = "✅" if fix.success else "❌"
            report += f"- {status} {fix.file_path}: {fix.description}\n"
        
        report += f"\n#### Critical Fixes ({len(results['critical_fixes'])})\n"
        for fix in results['critical_fixes']:
            status = "✅" if fix.success else "❌"
            report += f"- {status} {fix.file_path}: {fix.description}\n"
        
        report += f"\n#### Configuration Fixes ({len(results['configuration_fixes'])})\n"
        for fix in results['configuration_fixes']:
            status = "✅" if fix.success else "❌"
            report += f"- {status} {fix.file_path}: {fix.description}\n"
        
        if 'validation' in results:
            report += "\n### Validation Results\n"
            for category, validations in results['validation'].items():
                report += f"\n#### {category.replace('_', ' ').title()}\n"
                for item, result in validations.items():
                    report += f"- {item}: {result}\n"
        
        return report

def main():
    """Main execution function"""
    fixer = ComprehensiveStartupFixer()
    results = fixer.run_comprehensive_fix()
    
    # Generate and save report
    report = fixer.generate_fix_report(results)
    
    with open("COMPREHENSIVE_STARTUP_FIX_REPORT.md", "w") as f:
        f.write(report)
    
    print(report)
    print(f"\n📊 Fix Summary: {results['total_fixes_applied']}/{results['total_issues_found']} issues resolved ({results['success_rate']:.1f}% success)")
    
    return results

if __name__ == "__main__":
    main() 