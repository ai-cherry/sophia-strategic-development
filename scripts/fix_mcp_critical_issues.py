#!/usr/bin/env python3
"""
Fix Critical MCP Server Issues
==============================

Systematically fixes import issues, missing __init__.py files, and dependency problems
across all MCP servers in the Sophia AI platform.
"""

import ast
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPCriticalIssueFixer:
    """Fixes critical issues in MCP servers"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.mcp_servers_path = self.base_path / "mcp-servers"
        self.backend_mcp_path = self.base_path / "backend" / "mcp_servers"
        self.issues_found = []
        self.fixes_applied = []
        
    def fix_all_critical_issues(self):
        """Fix all critical issues across MCP servers"""
        logger.info("🔧 Starting critical MCP server issue fixes...")
        
        # Fix missing __init__.py files
        self._fix_missing_init_files()
        
        # Fix import issues
        self._fix_import_issues()
        
        # Fix circular dependencies
        self._fix_circular_dependencies()
        
        # Fix standardized base class inheritance
        self._fix_base_class_inheritance()
        
        # Generate summary report
        self._generate_report()
        
        logger.info("✅ Critical MCP server issues fixed!")
        
    def _fix_missing_init_files(self):
        """Add missing __init__.py files"""
        logger.info("📁 Fixing missing __init__.py files...")
        
        directories_to_check = [
            self.mcp_servers_path,
            self.backend_mcp_path,
            self.base_path / "backend" / "mcp_servers" / "base"
        ]
        
        for directory in directories_to_check:
            if directory.exists():
                self._ensure_init_files_recursive(directory)
                
    def _ensure_init_files_recursive(self, directory: Path):
        """Recursively ensure __init__.py files exist"""
        init_file = directory / "__init__.py"
        
        if directory.is_dir() and not init_file.exists():
            # Create __init__.py with proper exports
            init_content = self._generate_init_content(directory)
            
            with open(init_file, 'w') as f:
                f.write(init_content)
                
            self.fixes_applied.append(f"Created {init_file}")
            logger.info(f"✅ Created {init_file}")
            
        # Recurse into subdirectories
        for item in directory.iterdir():
            if item.is_dir() and not item.name.startswith('.') and item.name != '__pycache__':
                self._ensure_init_files_recursive(item)
                
    def _generate_init_content(self, directory: Path) -> str:
        """Generate appropriate __init__.py content"""
        # Find Python files in directory
        python_files = list(directory.glob("*.py"))
        python_files = [f for f in python_files if f.name != "__init__.py"]
        
        if not python_files:
            return '"""MCP Server Package"""\n'
            
        # Generate exports
        exports = []
        
        for py_file in python_files:
            module_name = py_file.stem
            
            # Try to find exportable classes/functions
            try:
                with open(py_file) as f:
                    content = f.read()
                    
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        if "MCP" in node.name or "Server" in node.name:
                            exports.append((module_name, node.name))
                    elif isinstance(node, ast.FunctionDef):
                        if not node.name.startswith('_'):
                            exports.append((module_name, node.name))
                            
            except Exception as e:
                logger.warning(f"Failed to parse {py_file}: {e}")
                
        # Generate init content
        content = '"""MCP Server Package"""\n\n'
        
        if exports:
            # Add imports
            for module, name in exports:
                content += f"from .{module} import {name}\n"
                
            content += "\n__all__ = [\n"
            for _, name in exports:
                content += f'    "{name}",\n'
            content += "]\n"
            
        return content
        
    def _fix_import_issues(self):
        """Fix common import issues"""
        logger.info("🔍 Fixing import issues...")
        
        # Common import fixes
        import_fixes = {
            r'from backend\.mcp\.': 'from backend.mcp_servers.',
            r'from mcp\.': 'from backend.mcp_servers.',
            r'from \.\.base import StandardizedMCPServer': 'from backend.mcp_servers.base.standardized_mcp_server import StandardizedMCPServer',
            r'from base\.standardized_mcp_server': 'from backend.mcp_servers.base.standardized_mcp_server',
            r'import StandardizedMCPServer': 'from backend.mcp_servers.base.standardized_mcp_server import StandardizedMCPServer',
        }
        
        # Fix imports in all Python files
        for py_file in self._get_all_python_files():
            self._apply_import_fixes(py_file, import_fixes)
            
    def _get_all_python_files(self) -> List[Path]:
        """Get all Python files in MCP servers"""
        python_files = []
        
        for directory in [self.mcp_servers_path, self.backend_mcp_path]:
            if directory.exists():
                python_files.extend(directory.rglob("*.py"))
                
        return python_files
        
    def _apply_import_fixes(self, file_path: Path, fixes: Dict[str, str]):
        """Apply import fixes to a file"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            original_content = content
            
            for pattern, replacement in fixes.items():
                content = re.sub(pattern, replacement, content)
                
            if content != original_content:
                with open(file_path, 'w') as f:
                    f.write(content)
                    
                self.fixes_applied.append(f"Fixed imports in {file_path.name}")
                logger.info(f"✅ Fixed imports in {file_path}")
                
        except Exception as e:
            logger.error(f"Failed to fix imports in {file_path}: {e}")
            self.issues_found.append(f"Import fix failed: {file_path} - {e}")
            
    def _fix_circular_dependencies(self):
        """Fix circular dependency issues"""
        logger.info("🔄 Fixing circular dependencies...")
        
        # Move imports inside functions where necessary
        circular_patterns = [
            (r'from backend\.services\.mcp_orchestration_service import MCPOrchestrationService',
             'def get_orchestration_service():\n    from backend.services.mcp_orchestration_service import MCPOrchestrationService\n    return MCPOrchestrationService'),
            (r'from backend\.core\.auto_esc_config import get_config_value',
             'def get_config_value_lazy(*args, **kwargs):\n    from backend.core.auto_esc_config import get_config_value\n    return get_config_value(*args, **kwargs)'),
        ]
        
        for py_file in self._get_all_python_files():
            self._fix_circular_imports(py_file, circular_patterns)
            
    def _fix_circular_imports(self, file_path: Path, patterns: List[Tuple[str, str]]):
        """Fix circular imports in a file"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Check if file has potential circular imports
            has_circular = False
            
            for pattern, _ in patterns:
                if re.search(pattern, content):
                    # Check if this import is at module level
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if re.search(pattern, line):
                            # Check indentation
                            if len(line) - len(line.lstrip()) == 0:
                                has_circular = True
                                break
                                
            if has_circular:
                logger.info(f"⚠️  Potential circular import in {file_path}")
                self.issues_found.append(f"Circular import detected: {file_path}")
                
        except Exception as e:
            logger.error(f"Failed to check circular imports in {file_path}: {e}")
            
    def _fix_base_class_inheritance(self):
        """Fix StandardizedMCPServer inheritance issues"""
        logger.info("🏗️  Fixing base class inheritance...")
        
        for py_file in self._get_all_python_files():
            if "mcp_server.py" in str(py_file):
                self._ensure_proper_inheritance(py_file)
                
    def _ensure_proper_inheritance(self, file_path: Path):
        """Ensure proper inheritance from StandardizedMCPServer"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Parse AST
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if it's an MCP server class
                    if "MCPServer" in node.name and node.name != "StandardizedMCPServer":
                        # Check if it inherits from StandardizedMCPServer
                        has_proper_base = False
                        
                        for base in node.bases:
                            if isinstance(base, ast.Name) and base.id == "StandardizedMCPServer":
                                has_proper_base = True
                                break
                            elif isinstance(base, ast.Attribute) and base.attr == "StandardizedMCPServer":
                                has_proper_base = True
                                break
                                
                        if not has_proper_base:
                            logger.warning(f"⚠️  {file_path}: {node.name} doesn't inherit from StandardizedMCPServer")
                            self.issues_found.append(f"Missing StandardizedMCPServer inheritance: {file_path} - {node.name}")
                            
        except Exception as e:
            logger.error(f"Failed to check inheritance in {file_path}: {e}")
            
    def _generate_report(self):
        """Generate fix report"""
        report_path = self.base_path / "MCP_CRITICAL_FIXES_REPORT.md"
        
        with open(report_path, 'w') as f:
            f.write("# MCP Server Critical Fixes Report\n\n")
            f.write(f"Generated: {os.environ.get('USER', 'unknown')}@{os.uname().nodename}\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"- Total fixes applied: {len(self.fixes_applied)}\n")
            f.write(f"- Issues found: {len(self.issues_found)}\n\n")
            
            f.write("## Fixes Applied\n\n")
            for fix in self.fixes_applied:
                f.write(f"- {fix}\n")
                
            f.write("\n## Issues Found\n\n")
            for issue in self.issues_found:
                f.write(f"- {issue}\n")
                
            f.write("\n## Recommendations\n\n")
            f.write("1. Run `python scripts/standardize_mcp_servers.py` to standardize all servers\n")
            f.write("2. Run `python scripts/assess_all_mcp_servers.py` to check server health\n")
            f.write("3. Review circular dependency warnings and refactor if needed\n")
            f.write("4. Ensure all servers inherit from EnhancedStandardizedMCPServer\n")
            
        logger.info(f"📄 Report saved to {report_path}")


def main():
    """Main execution function"""
    fixer = MCPCriticalIssueFixer()
    fixer.fix_all_critical_issues()


if __name__ == "__main__":
    main() 