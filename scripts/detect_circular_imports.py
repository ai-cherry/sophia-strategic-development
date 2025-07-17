#!/usr/bin/env python3
"""
Circular Import Detection Script - Phase 1 Priority
Detects and analyzes circular import chains in the Sophia AI codebase
"""

import ast
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict, deque
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImportGraph:
    """Build and analyze import dependency graph"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.graph: Dict[str, Set[str]] = defaultdict(set)
        self.module_to_file: Dict[str, str] = {}
        self.file_to_module: Dict[str, str] = {}
        
    def build_graph(self):
        """Build the complete import dependency graph"""
        logger.info("🔍 Building import dependency graph...")
        
        # First pass: Map files to modules
        for py_file in self.project_root.rglob("*.py"):
            if self._should_skip_file(py_file):
                continue
                
            module_name = self._file_to_module_name(py_file)
            self.module_to_file[module_name] = str(py_file)
            self.file_to_module[str(py_file)] = module_name
            
        # Second pass: Build import graph
        for py_file in self.project_root.rglob("*.py"):
            if self._should_skip_file(py_file):
                continue
                
            module_name = self.file_to_module[str(py_file)]
            imports = self._extract_imports(py_file)
            
            for imported_module in imports:
                if imported_module in self.module_to_file:
                    self.graph[module_name].add(imported_module)
                    
        logger.info(f"✅ Graph built: {len(self.graph)} modules, {sum(len(deps) for deps in self.graph.values())} dependencies")
        
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped"""
        skip_patterns = ['.venv', 'node_modules', '__pycache__', '.git', 'backup']
        return any(pattern in str(file_path) for pattern in skip_patterns)
        
    def _file_to_module_name(self, file_path: Path) -> str:
        """Convert file path to module name"""
        # Get relative path from project root
        try:
            rel_path = file_path.relative_to(self.project_root)
        except ValueError:
            rel_path = file_path
            
        # Convert to module name
        module_parts = []
        for part in rel_path.parts[:-1]:  # Exclude filename
            module_parts.append(part)
            
        # Add filename without .py extension
        if rel_path.name != "__init__.py":
            module_parts.append(rel_path.stem)
            
        return ".".join(module_parts)
        
    def _extract_imports(self, file_path: Path) -> List[str]:
        """Extract all imports from a Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        # Handle relative imports
                        if node.level > 0:
                            # Relative import - convert to absolute
                            current_module = self._file_to_module_name(file_path)
                            if "." in current_module:
                                parent_parts = current_module.split(".")[:-node.level]
                                if parent_parts and node.module:
                                    imports.append(".".join(parent_parts + [node.module]))
                        else:
                            imports.append(node.module)
                            
            return imports
            
        except Exception as e:
            logger.debug(f"Could not parse {file_path}: {e}")
            return []
            
    def detect_cycles(self) -> List[List[str]]:
        """Detect circular import cycles using DFS"""
        logger.info("🔍 Detecting circular import cycles...")
        
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs(node: str, path: List[str]) -> bool:
            """DFS to detect cycles"""
            if node in rec_stack:
                # Found cycle
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return True
                
            if node in visited:
                return False
                
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            # Visit all dependencies
            for dependency in self.graph.get(node, set()):
                if dfs(dependency, path):
                    # Continue searching for more cycles
                    pass
                    
            rec_stack.remove(node)
            path.pop()
            return False
            
        # Check all modules
        for module in self.graph:
            if module not in visited:
                dfs(module, [])
                
        # Remove duplicate cycles
        unique_cycles = []
        for cycle in cycles:
            # Normalize cycle (start from smallest element)
            if len(cycle) > 1:
                min_idx = cycle.index(min(cycle[:-1]))  # Exclude last element (duplicate)
                normalized = cycle[min_idx:-1] + cycle[:min_idx] + [cycle[min_idx]]
                if normalized not in unique_cycles:
                    unique_cycles.append(normalized)
                    
        logger.info(f"🎯 Found {len(unique_cycles)} circular import cycles")
        return unique_cycles
        
    def analyze_dependencies(self) -> Dict[str, int]:
        """Analyze dependency complexity"""
        complexity = {}
        
        for module, dependencies in self.graph.items():
            # Calculate complexity score
            direct_deps = len(dependencies)
            
            # Calculate transitive dependencies
            visited = set()
            queue = deque(dependencies)
            
            while queue:
                dep = queue.popleft()
                if dep not in visited:
                    visited.add(dep)
                    queue.extend(self.graph.get(dep, set()))
                    
            transitive_deps = len(visited)
            
            # Complexity score: direct + transitive/2
            complexity[module] = direct_deps + (transitive_deps / 2)
            
        return complexity
        
    def find_dependency_chains(self, max_depth: int = 5) -> List[List[str]]:
        """Find long dependency chains that could indicate issues"""
        chains = []
        
        def find_chains_from(module: str, current_chain: List[str], depth: int):
            if depth >= max_depth:
                if len(current_chain) >= 3:  # Only report chains of 3+ modules
                    chains.append(current_chain[:])
                return
                
            for dependency in self.graph.get(module, set()):
                if dependency not in current_chain:  # Avoid immediate cycles
                    current_chain.append(dependency)
                    find_chains_from(dependency, current_chain, depth + 1)
                    current_chain.pop()
                    
        # Start from modules with many dependencies
        high_dep_modules = sorted(
            self.graph.keys(), 
            key=lambda m: len(self.graph[m]), 
            reverse=True
        )[:10]  # Top 10 modules with most dependencies
        
        for module in high_dep_modules:
            find_chains_from(module, [module], 0)
            
        return chains[:20]  # Limit to first 20 chains
        
    def get_problematic_modules(self) -> Dict[str, Dict[str, any]]:
        """Identify modules that are likely causing issues"""
        complexity = self.analyze_dependencies()
        problematic = {}
        
        # Modules with high complexity
        high_complexity_threshold = 10
        for module, score in complexity.items():
            if score > high_complexity_threshold:
                file_path = self.module_to_file.get(module, "Unknown")
                problematic[module] = {
                    "complexity_score": score,
                    "direct_dependencies": len(self.graph[module]),
                    "file_path": file_path,
                    "issues": []
                }
                
                # Check for specific issues
                if score > 20:
                    problematic[module]["issues"].append("Very high complexity")
                if len(self.graph[module]) > 10:
                    problematic[module]["issues"].append("Too many direct dependencies")
                    
        return problematic


class CircularImportFixer:
    """Fix circular import issues"""
    
    def __init__(self, import_graph: ImportGraph):
        self.graph = import_graph
        
    def suggest_fixes(self, cycles: List[List[str]]) -> List[Dict[str, any]]:
        """Suggest fixes for circular import cycles"""
        fixes = []
        
        for cycle in cycles:
            fix = {
                "cycle": cycle,
                "severity": self._assess_severity(cycle),
                "suggestions": self._generate_suggestions(cycle)
            }
            fixes.append(fix)
            
        return fixes
        
    def _assess_severity(self, cycle: List[str]) -> str:
        """Assess the severity of a circular import"""
        if len(cycle) <= 3:
            return "HIGH"  # Short cycles are more serious
        elif len(cycle) <= 5:
            return "MEDIUM"
        else:
            return "LOW"  # Long cycles may be less problematic
            
    def _generate_suggestions(self, cycle: List[str]) -> List[str]:
        """Generate suggestions to fix a circular import"""
        suggestions = []
        
        # Common patterns and fixes
        if len(cycle) == 3:
            suggestions.append("Move shared functionality to a separate module")
            suggestions.append("Use dependency injection instead of direct imports")
            
        if any("config" in module.lower() for module in cycle):
            suggestions.append("Extract configuration to a dedicated config module")
            
        if any("service" in module.lower() for module in cycle):
            suggestions.append("Use service locator pattern or dependency injection")
            
        if any("model" in module.lower() or "entity" in module.lower() for module in cycle):
            suggestions.append("Move data models to a separate models module")
            
        # Always include generic suggestions
        suggestions.extend([
            "Use TYPE_CHECKING imports for type hints",
            "Move imports inside functions if possible",
            "Consider using factory pattern",
            "Split large modules into smaller focused modules"
        ])
        
        return suggestions


def main():
    """Main execution function"""
    logger.info("🚀 Starting circular import detection...")
    
    # Build import graph
    graph = ImportGraph()
    graph.build_graph()
    
    # Detect cycles
    cycles = graph.detect_cycles()
    
    # Analyze problematic modules
    problematic = graph.get_problematic_modules()
    
    # Find long dependency chains
    chains = graph.find_dependency_chains()
    
    # Generate fixes
    fixer = CircularImportFixer(graph)
    fixes = fixer.suggest_fixes(cycles)
    
    # Generate report
    report = f"""
# 🔍 CIRCULAR IMPORT ANALYSIS REPORT

## Summary
- **Modules analyzed**: {len(graph.graph)}
- **Circular import cycles found**: {len(cycles)}
- **Problematic modules**: {len(problematic)}
- **Long dependency chains**: {len(chains)}

## 🚨 Circular Import Cycles

"""
    
    if cycles:
        for i, cycle in enumerate(cycles, 1):
            fix_info = fixes[i-1] if i-1 < len(fixes) else {"severity": "UNKNOWN", "suggestions": []}
            report += f"""
### Cycle {i} (Severity: {fix_info['severity']})
**Modules**: {' → '.join(cycle)}

**Files involved**:
"""
            for module in cycle[:-1]:  # Exclude duplicate last element
                file_path = graph.module_to_file.get(module, "Unknown")
                report += f"- `{file_path}`\n"
                
            report += f"""
**Suggested fixes**:
"""
            for suggestion in fix_info.get('suggestions', [])[:3]:  # Top 3 suggestions
                report += f"- {suggestion}\n"
    else:
        report += "✅ No circular import cycles detected!\n"
        
    report += f"""

## ⚠️ Problematic Modules

"""
    
    if problematic:
        for module, info in list(problematic.items())[:10]:  # Top 10
            report += f"""
### {module}
- **File**: `{info['file_path']}`
- **Complexity Score**: {info['complexity_score']:.1f}
- **Direct Dependencies**: {info['direct_dependencies']}
- **Issues**: {', '.join(info['issues']) if info['issues'] else 'High complexity'}
"""
    else:
        report += "✅ No highly problematic modules detected!\n"
        
    report += f"""

## 🔗 Long Dependency Chains

"""
    
    if chains:
        for i, chain in enumerate(chains[:5], 1):  # Show first 5
            report += f"""
### Chain {i}
{' → '.join(chain)}
"""
    else:
        report += "✅ No excessively long dependency chains detected!\n"
        
    # Save report
    report_file = Path("CIRCULAR_IMPORT_ANALYSIS_REPORT.md")
    with open(report_file, 'w') as f:
        f.write(report)
        
    logger.info(f"📊 Report saved to {report_file}")
    
    # Print summary
    print("\n🎯 CIRCULAR IMPORT DETECTION RESULTS:")
    print(f"   Modules analyzed: {len(graph.graph)}")
    print(f"   Circular cycles found: {len(cycles)}")
    print(f"   Problematic modules: {len(problematic)}")
    print(f"   Long dependency chains: {len(chains)}")
    print(f"   Report saved: {report_file}")
    
    if cycles:
        print(f"\n⚠️  CRITICAL: {len(cycles)} circular import cycles need attention!")
        return 1
    else:
        print("\n✅ No circular import cycles detected - good architecture!")
        return 0


if __name__ == "__main__":
    import sys
    sys.exit(main()) 