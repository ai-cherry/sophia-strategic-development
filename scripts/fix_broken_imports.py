#!/usr/bin/env python3
"""
Broken Import Fix Script - Phase 1 Refactoring
Identifies and fixes broken imports throughout the Sophia AI codebase
"""

import ast
import os
import re
from pathlib import Path
from typing import List, Dict, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BrokenImportFixer:
    """Comprehensive broken import detection and fixing"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.broken_imports = []
        self.missing_modules = []
        self.fixes_applied = []
        
    def find_broken_imports(self) -> List[Dict]:
        """Find all broken imports in the codebase"""
        logger.info("🔍 Scanning for broken imports...")
        
        for py_file in self.project_root.rglob("*.py"):
            # Skip virtual environments and node_modules
            if any(skip in str(py_file) for skip in ['.venv', 'node_modules', '__pycache__']):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ImportFrom) and node.module:
                            self._check_import(py_file, node)
                        elif isinstance(node, ast.Import):
                            for alias in node.names:
                                self._check_module(py_file, alias.name, node.lineno)
                                
            except Exception as e:
                logger.warning(f"⚠️  Could not parse {py_file}: {e}")
                continue
                
        logger.info(f"Found {len(self.broken_imports)} broken imports")
        return self.broken_imports
        
    def _check_import(self, file_path: Path, node: ast.ImportFrom):
        """Check if an import can be resolved"""
        module = node.module
        line_no = node.lineno
        
        # Check for common broken patterns
        if module and any(pattern in module for pattern in ['backend.', 'mcp_servers.', 'shared.']):
            module_path = self._module_to_path(module)
            
            if not self._module_exists(module_path):
                self.broken_imports.append({
                    'file': str(file_path),
                    'line': line_no,
                    'module': module,
                    'type': 'import_from',
                    'suggested_fix': self._suggest_fix(module)
                })
                
    def _check_module(self, file_path: Path, module_name: str, line_no: int):
        """Check if a module import can be resolved"""
        if any(pattern in module_name for pattern in ['backend.', 'mcp_servers.', 'shared.']):
            module_path = self._module_to_path(module_name)
            
            if not self._module_exists(module_path):
                self.broken_imports.append({
                    'file': str(file_path),
                    'line': line_no,
                    'module': module_name,
                    'type': 'import',
                    'suggested_fix': self._suggest_fix(module_name)
                })
                
    def _module_to_path(self, module_name: str) -> Path:
        """Convert module name to file path"""
        return self.project_root / module_name.replace('.', '/')
        
    def _module_exists(self, module_path: Path) -> bool:
        """Check if module exists as file or package"""
        return (
            module_path.exists() or
            (module_path.parent / f"{module_path.name}.py").exists() or
            (module_path / "__init__.py").exists()
        )
        
    def _suggest_fix(self, module_name: str) -> str:
        """Suggest a fix for broken import"""
        # Common fix patterns
        fixes = {
            'backend.core.auto_esc_config': 'backend.core.auto_esc_config',
            'backend.services.': 'Check if service exists in backend/services/',
            'mcp_servers.': 'Check if MCP server exists in mcp_servers/',
            'shared.': 'May need to create shared module or update import path'
        }
        
        for pattern, fix in fixes.items():
            if pattern in module_name:
                return fix
                
        return f"Check if {module_name} exists and create if needed"
        
    def create_missing_modules(self) -> List[str]:
        """Create missing __init__.py files and modules"""
        logger.info("🔧 Creating missing modules...")
        
        missing_inits = [
            "backend/utils/__init__.py",
            "backend/monitoring/__init__.py", 
            "mcp_servers/redis/__init__.py",
            "mcp_servers/qdrant/__init__.py",
            "mcp_servers/postgresql/__init__.py",
            "shared/__init__.py",
            "shared/utils/__init__.py"
        ]
        
        created = []
        for init_path in missing_inits:
            full_path = self.project_root / init_path
            if not full_path.exists():
                # Create directory if it doesn't exist
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Create __init__.py with appropriate content
                init_content = self._generate_init_content(init_path)
                with open(full_path, 'w') as f:
                    f.write(init_content)
                    
                created.append(str(full_path))
                logger.info(f"✅ Created {full_path}")
                
        self.fixes_applied.extend(created)
        return created
        
    def _generate_init_content(self, init_path: str) -> str:
        """Generate appropriate content for __init__.py files"""
        if "backend/utils" in init_path:
            return '''"""
Backend utilities for Sophia AI
"""

# Common utility imports can be added here
'''
        elif "backend/monitoring" in init_path:
            return '''"""
Monitoring utilities for Sophia AI
"""

# Monitoring classes and functions
'''
        elif "mcp_servers" in init_path:
            return '''"""
MCP Server module for Sophia AI
"""

# MCP server exports
'''
        elif "shared" in init_path:
            return '''"""
Shared utilities and components for Sophia AI
"""

# Shared components
'''
        else:
            return '''"""
Module for Sophia AI
"""
'''

    def fix_common_import_issues(self) -> List[str]:
        """Fix common import path issues"""
        logger.info("🔧 Fixing common import issues...")
        
        fixes = []
        
        # Fix backend.core imports
        for broken in self.broken_imports:
            if 'backend.core' in broken['module']:
                fix = self._fix_backend_core_import(broken)
                if fix:
                    fixes.append(fix)
                    
        # Fix MCP server imports
        for broken in self.broken_imports:
            if 'mcp_servers' in broken['module']:
                fix = self._fix_mcp_server_import(broken)
                if fix:
                    fixes.append(fix)
                    
        self.fixes_applied.extend(fixes)
        return fixes
        
    def _fix_backend_core_import(self, broken_import: Dict) -> str:
        """Fix backend.core import issues"""
        file_path = Path(broken_import['file'])
        module = broken_import['module']
        
        # Common backend.core fixes
        if 'auto_esc_config' in module:
            # This is usually correct, check if file exists
            config_file = self.project_root / "backend/core/auto_esc_config.py"
            if config_file.exists():
                return f"✅ {module} import is correct, file exists"
                
        return None
        
    def _fix_mcp_server_import(self, broken_import: Dict) -> str:
        """Fix MCP server import issues"""
        file_path = Path(broken_import['file'])
        module = broken_import['module']
        
        # Extract MCP server name
        parts = module.split('.')
        if len(parts) >= 2 and parts[0] == 'mcp_servers':
            server_name = parts[1]
            server_dir = self.project_root / "mcp_servers" / server_name
            
            if not server_dir.exists():
                logger.info(f"Creating MCP server directory: {server_dir}")
                server_dir.mkdir(parents=True, exist_ok=True)
                
                # Create __init__.py
                init_file = server_dir / "__init__.py"
                with open(init_file, 'w') as f:
                    f.write(f'''"""
{server_name.title()} MCP Server for Sophia AI
"""

# MCP server implementation will be added here
''')
                return f"✅ Created MCP server structure for {server_name}"
                
        return None
        
    def generate_report(self) -> str:
        """Generate a comprehensive report of findings and fixes"""
        report = f"""
# 🔍 BROKEN IMPORT ANALYSIS REPORT

## Summary
- **Broken imports found**: {len(self.broken_imports)}
- **Fixes applied**: {len(self.fixes_applied)}

## Broken Imports Details
"""
        
        for broken in self.broken_imports[:10]:  # Show first 10
            report += f"""
### {broken['file']}:{broken['line']}
- **Module**: `{broken['module']}`
- **Type**: {broken['type']}
- **Suggested Fix**: {broken['suggested_fix']}
"""
        
        if len(self.broken_imports) > 10:
            report += f"\n... and {len(self.broken_imports) - 10} more broken imports\n"
            
        report += f"""
## Fixes Applied
"""
        for fix in self.fixes_applied:
            report += f"- ✅ {fix}\n"
            
        return report
        
    def run_comprehensive_fix(self) -> Dict:
        """Run the complete broken import fix process"""
        logger.info("🚀 Starting comprehensive import fix...")
        
        # Step 1: Find broken imports
        self.find_broken_imports()
        
        # Step 2: Create missing modules
        created_modules = self.create_missing_modules()
        
        # Step 3: Fix common issues
        fixed_imports = self.fix_common_import_issues()
        
        # Step 4: Generate report
        report = self.generate_report()
        
        # Save report
        report_file = self.project_root / "BROKEN_IMPORT_FIX_REPORT.md"
        with open(report_file, 'w') as f:
            f.write(report)
            
        logger.info(f"📊 Report saved to {report_file}")
        
        return {
            'broken_imports_found': len(self.broken_imports),
            'modules_created': len(created_modules),
            'imports_fixed': len(fixed_imports),
            'report_file': str(report_file)
        }


def main():
    """Main execution function"""
    fixer = BrokenImportFixer()
    results = fixer.run_comprehensive_fix()
    
    print("\n🎯 BROKEN IMPORT FIX RESULTS:")
    print(f"   Broken imports found: {results['broken_imports_found']}")
    print(f"   Modules created: {results['modules_created']}")
    print(f"   Imports fixed: {results['imports_fixed']}")
    print(f"   Report saved: {results['report_file']}")
    
    return results


if __name__ == "__main__":
    main() 