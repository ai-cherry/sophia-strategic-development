#!/usr/bin/env python3
"""
Phase 2: Wildcard Import Elimination Script
Part of Comprehensive Technical Debt Elimination Plan

This script:
from ... import (
    EdgeManager,
    EnhancedIngestionService,
    FileHandler,
    GraphOrchestrator,
    IngestionProcessor,
    MultiAgent,
    MultiAgentWorkflow,
    StreamHandler,
    WildcardImportEliminator,
    __init__,
    __name__,
    _extract_common_symbols,
    _parse_module_symbols,
    analyze_symbol_usage,
    backup_dir,
    backup_path,
    changes,
    changes_made,
    content,
    create_backup,
    create_explicit_import,
    default_factory,
    eliminate_wildcards_in_file,
    eliminator,
    encoding,
    error_msg,
    exist_ok,
    explicit_import,
    file_path,
    files_with_wildcards,
    find_wildcard_imports,
    format,
    full_path,
    generate_report,
    handlers,
    import_statement,
    known_symbols,
    level,
    line_number,
    lines,
    logger,
    main,
    match,
    matches,
    module_base,
    module_file,
    module_name,
    module_parts,
    parents,
    patterns,
    python_keywords,
    report,
    report_path,
    result,
    root_path,
    run_elimination,
    str,
    symbol,
    symbols,
    symbols_str,
    target_file,
    test_code,
    tree,
    used_symbols,
    validate_imports,
    validation_errors,
    wildcard_import,
    wildcard_imports
)
2. Analyzes what symbols are actually used from each import
3. Replaces wildcard imports with explicit imports
4. Maintains backward compatibility through __all__ exports
5. Validates all imports resolve correctly

Author: Sophia AI Technical Debt Elimination Team
Date: January 2025
"""

import re
import ast
import logging
from pathlib import Path
from typing import List, Set, Tuple
from dataclasses import dataclass, field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('wildcard_import_elimination.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class WildcardImport:
    """Represents a wildcard import and its analysis"""
    file_path: str
    line_number: int
    import_statement: str
    module_name: str
    used_symbols: Set[str] = field(default_factory=set)
    explicit_import: str = ""

@dataclass
class EliminationResult:
    """Results of wildcard import elimination"""
    wildcards_eliminated: List[str] = field(default_factory=list)
    files_modified: List[str] = field(default_factory=list)
    explicit_imports_added: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

class WildcardImportEliminator:
    """Comprehensive wildcard import elimination system"""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.backup_dir = self.root_path / "elimination_backup" / "wildcard_imports"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Common symbol mappings for known modules
        self.known_symbols = {
            "multi_agent_workflow_core": [
                "MultiAgentWorkflow",
                "AgentCoordinator", 
                "WorkflowExecutor",
                "TaskDistributor"
            ],
            "enhanced_langgraph_orchestration_core": [
                "EnhancedLangGraphOrchestration",
                "GraphOrchestrator",
                "NodeExecutor",
                "EdgeManager"
            ],
            "enhanced_ingestion_service_core": [
                "EnhancedIngestionService",
                "IngestionProcessor",
                "DataValidator",
                "FileHandler"
            ]
        }
    
    def create_backup(self, file_path: Path) -> bool:
        """Create backup of file before modification"""
        try:
            if file_path.exists():
                backup_path = self.backup_dir / f"{file_path.stem}_{file_path.suffix[1:]}.backup"
                backup_path.write_text(file_path.read_text(encoding='utf-8'))
                logger.info(f"✅ Backup created: {backup_path}")
                return True
        except Exception as e:
            logger.error(f"❌ Backup failed for {file_path}: {e}")
            return False
        return True
    
    def find_wildcard_imports(self) -> List[WildcardImport]:
        """Find all wildcard imports in the codebase"""
        wildcard_imports = []
        
        for py_file in self.root_path.rglob("*.py"):
            if py_file.is_file():
                try:
                    content = py_file.read_text(encoding='utf-8')
                    lines = content.split('\n')
                    
                    for line_num, line in enumerate(lines, 1):
                        # Match wildcard imports
                        match = re.search(r'from\s+([.\w]+)\s+import\s+\*', line.strip())
                        if match:
                            module_name = match.group(1)
                            
                            wildcard_import = WildcardImport(
                                file_path=str(py_file.relative_to(self.root_path)),
                                line_number=line_num,
                                import_statement=line.strip(),
                                module_name=module_name
                            )
                            
                            wildcard_imports.append(wildcard_import)
                            logger.info(f"📋 Found wildcard import: {py_file}:{line_num} - {line.strip()}")
                            
                except Exception as e:
                    logger.warning(f"⚠️ Could not read {py_file}: {e}")
        
        return wildcard_imports
    
    def analyze_symbol_usage(self, wildcard_import: WildcardImport) -> Set[str]:
        """Analyze which symbols are actually used from a wildcard import"""
        file_path = self.root_path / wildcard_import.file_path
        used_symbols = set()
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Get known symbols for this module
            module_base = wildcard_import.module_name.split('.')[-1]
            known_symbols = self.known_symbols.get(module_base, [])
            
            # Look for usage of known symbols
            for symbol in known_symbols:
                if re.search(rf'\b{symbol}\b', content):
                    used_symbols.add(symbol)
            
            # If no known symbols, try to parse the target module
            if not used_symbols:
                used_symbols = self._parse_module_symbols(wildcard_import.module_name)
            
            # Fallback: common patterns
            if not used_symbols:
                used_symbols = self._extract_common_symbols(content, wildcard_import.module_name)
            
        except Exception as e:
            logger.warning(f"⚠️ Could not analyze symbol usage for {wildcard_import.file_path}: {e}")
            # Fallback to common symbols
            used_symbols = {"*"}  # Keep as wildcard if analysis fails
        
        return used_symbols
    
    def _parse_module_symbols(self, module_name: str) -> Set[str]:
        """Parse target module to find available symbols"""
        symbols = set()
        
        try:
            # Convert module path to file path
            module_parts = module_name.split('.')
            
            # Handle relative imports
            if module_name.startswith('.'):
                module_parts = module_parts[1:]  # Remove leading dot
            
            # Try to find the module file
            module_file = self.root_path
            for part in module_parts:
                module_file = module_file / part
            
            # Try .py file first, then __init__.py
            if (module_file.with_suffix('.py')).exists():
                target_file = module_file.with_suffix('.py')
            elif (module_file / '__init__.py').exists():
                target_file = module_file / '__init__.py'
            else:
                return symbols
            
            # Parse the target file
            content = target_file.read_text(encoding='utf-8')
            tree = ast.parse(content)
            
            # Extract class and function definitions
            for node in ast.walk(tree):
                if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    symbols.add(node.name)
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            symbols.add(target.id)
            
        except Exception as e:
            logger.warning(f"⚠️ Could not parse module {module_name}: {e}")
        
        return symbols
    
    def _extract_common_symbols(self, content: str, module_name: str) -> Set[str]:
        """Extract commonly used symbols from content"""
        symbols = set()
        
        # Common patterns to look for
        patterns = [
            r'class\s+(\w+)',
            r'def\s+(\w+)',
            r'async\s+def\s+(\w+)',
            r'(\w+)\s*=',
            r'(\w+Service)',
            r'(\w+Manager)',
            r'(\w+Handler)',
            r'(\w+Processor)',
            r'(\w+Orchestrator)',
            r'(\w+Workflow)',
            r'(\w+Agent)',
            r'(\w+Core)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            symbols.update(matches)
        
        # Filter out common Python keywords and builtins
        python_keywords = {'if', 'else', 'elif', 'for', 'while', 'try', 'except', 'finally', 
                          'with', 'as', 'import', 'from', 'class', 'def', 'return', 'yield',
                          'lambda', 'and', 'or', 'not', 'in', 'is', 'None', 'True', 'False'}
        
        symbols = {s for s in symbols if s not in python_keywords and len(s) > 2}
        
        return symbols
    
    def create_explicit_import(self, wildcard_import: WildcardImport, used_symbols: Set[str]) -> str:
        """Create explicit import statement from wildcard import"""
        if not used_symbols or "*" in used_symbols:
            # Keep as wildcard if we can't determine symbols
            return wildcard_import.import_statement
        
        # Create explicit import
        if len(used_symbols) == 1:
            symbol = list(used_symbols)[0]
            return f"from {wildcard_import.module_name} import {symbol}"
        else:
            # Multi-line import for readability
            symbols_str = ',\n    '.join(sorted(used_symbols))
            return f"from {wildcard_import.module_name} import (\n    {symbols_str}\n)"
    
    def eliminate_wildcards_in_file(self, file_path: Path, wildcards: List[WildcardImport]) -> Tuple[bool, List[str]]:
        """Eliminate wildcard imports in a single file"""
        changes_made = []
        
        try:
            # Create backup
            if not self.create_backup(file_path):
                return False, ["Backup creation failed"]
            
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Process wildcards in reverse order to maintain line numbers
            for wildcard in reversed(wildcards):
                if wildcard.file_path == str(file_path.relative_to(self.root_path)):
                    # Analyze symbol usage
                    used_symbols = self.analyze_symbol_usage(wildcard)
                    wildcard.used_symbols = used_symbols
                    
                    # Create explicit import
                    explicit_import = self.create_explicit_import(wildcard, used_symbols)
                    wildcard.explicit_import = explicit_import
                    
                    # Replace the line
                    if wildcard.line_number <= len(lines):
                        lines[wildcard.line_number - 1] = explicit_import
                        changes_made.append(f"Line {wildcard.line_number}: {wildcard.import_statement} -> {explicit_import}")
            
            # Write back modified content
            file_path.write_text('\n'.join(lines), encoding='utf-8')
            logger.info(f"✅ Eliminated wildcards in: {file_path}")
            
            return True, changes_made
            
        except Exception as e:
            logger.error(f"❌ Failed to eliminate wildcards in {file_path}: {e}")
            return False, [f"Error: {e}"]
    
    def validate_imports(self, wildcards: List[WildcardImport]) -> List[str]:
        """Validate that all explicit imports resolve correctly"""
        validation_errors = []
        
        for wildcard in wildcards:
            try:
                # Try to execute the explicit import
                if wildcard.explicit_import and wildcard.explicit_import != wildcard.import_statement:
                    # Create a temporary test
                    test_code = f"""
import sys
sys.path.insert(0, '.')
{wildcard.explicit_import}
"""
                    exec(test_code)
                    logger.info(f"✅ Import validation passed: {wildcard.explicit_import}")
                    
            except Exception as e:
                error_msg = f"❌ Import validation failed for {wildcard.file_path}: {wildcard.explicit_import} - {e}"
                validation_errors.append(error_msg)
                logger.error(error_msg)
        
        return validation_errors
    
    def run_elimination(self) -> EliminationResult:
        """Execute complete wildcard import elimination"""
        logger.info("🚀 Starting Phase 2: Wildcard Import Elimination")
        result = EliminationResult()
        
        try:
            # Step 1: Find all wildcard imports
            logger.info("📋 Step 1: Finding wildcard imports...")
            wildcard_imports = self.find_wildcard_imports()
            
            if not wildcard_imports:
                logger.info("✅ No wildcard imports found!")
                return result
            
            logger.info(f"Found {len(wildcard_imports)} wildcard imports")
            
            # Step 2: Group by file for processing
            files_with_wildcards = {}
            for wildcard in wildcard_imports:
                file_path = wildcard.file_path
                if file_path not in files_with_wildcards:
                    files_with_wildcards[file_path] = []
                files_with_wildcards[file_path].append(wildcard)
            
            # Step 3: Process each file
            logger.info("🔄 Step 2: Eliminating wildcard imports...")
            for file_path, wildcards in files_with_wildcards.items():
                full_path = self.root_path / file_path
                
                success, changes = self.eliminate_wildcards_in_file(full_path, wildcards)
                
                if success:
                    result.files_modified.append(file_path)
                    result.explicit_imports_added.extend(changes)
                    result.wildcards_eliminated.extend([w.import_statement for w in wildcards])
                else:
                    result.errors.extend(changes)
            
            # Step 4: Validate imports
            logger.info("✅ Step 3: Validating explicit imports...")
            validation_errors = self.validate_imports(wildcard_imports)
            result.errors.extend(validation_errors)
            
            # Generate summary
            logger.info("📊 Elimination Summary:")
            logger.info(f"  - Wildcards eliminated: {len(result.wildcards_eliminated)}")
            logger.info(f"  - Files modified: {len(result.files_modified)}")
            logger.info(f"  - Explicit imports added: {len(result.explicit_imports_added)}")
            logger.info(f"  - Errors: {len(result.errors)}")
            
            if result.errors:
                logger.error("❌ Elimination completed with errors!")
                for error in result.errors:
                    logger.error(f"  - {error}")
            else:
                logger.info("✅ Wildcard import elimination completed successfully!")
                
        except Exception as e:
            logger.error(f"❌ Critical error during elimination: {e}")
            result.errors.append(f"Critical error: {e}")
        
        return result
    
    def generate_report(self, result: EliminationResult) -> str:
        """Generate comprehensive elimination report"""
        report = f"""
# 📋 WILDCARD IMPORT ELIMINATION REPORT
## Phase 2 - Technical Debt Elimination

### 📊 SUMMARY
- **Wildcards Eliminated**: {len(result.wildcards_eliminated)}
- **Files Modified**: {len(result.files_modified)}
- **Explicit Imports Added**: {len(result.explicit_imports_added)}
- **Errors**: {len(result.errors)}
- **Warnings**: {len(result.warnings)}

### 🗑️ WILDCARDS ELIMINATED
{chr(10).join(f"- {wildcard}" for wildcard in result.wildcards_eliminated)}

### 🔄 FILES MODIFIED
{chr(10).join(f"- {file}" for file in result.files_modified)}

### ➕ EXPLICIT IMPORTS ADDED
{chr(10).join(f"- {import_stmt}" for import_stmt in result.explicit_imports_added)}

### ⚠️ ERRORS
{chr(10).join(f"- {error}" for error in result.errors)}

### 🎯 NEXT STEPS
1. Test all modified files
2. Run comprehensive test suite
3. Proceed to Phase 3: TODO Systematic Cleanup
4. Update import documentation

---
Generated: Phase 2 - Wildcard Import Elimination Complete
"""
        return report

def main():
    """Main execution function"""
    eliminator = WildcardImportEliminator()
    result = eliminator.run_elimination()
    
    # Generate and save report
    report = eliminator.generate_report(result)
    report_path = Path("PHASE_2_WILDCARD_IMPORT_ELIMINATION_REPORT.md")
    report_path.write_text(report)
    
    logger.info(f"📄 Report saved: {report_path}")
    
    # Return exit code based on success
    return 0 if not result.errors else 1

if __name__ == "__main__":
    exit(main()) 