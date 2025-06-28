#!/usr/bin/env python3
"""
Function Length Checker for Sophia AI
Monitors function length compliance and prevents regression
"""

import ast
import os
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class FunctionMetrics:
    """Metrics for a function"""
    name: str
    file_path: str
    start_line: int
    end_line: int
    line_count: int
    complexity: int = 0

class FunctionLengthChecker:
    """Checks function length compliance across the codebase"""
    
    def __init__(self, max_length: int = 50):
        self.max_length = max_length
        self.violations: List[FunctionMetrics] = []
        self.total_functions = 0
        
    def analyze_file(self, file_path: str) -> List[FunctionMetrics]:
        """Analyze a Python file for function metrics"""
        functions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if node.end_lineno is None or node.lineno is None:
                        continue
                    
                    line_count = node.end_lineno - node.lineno + 1
                    complexity = self._calculate_complexity(node)
                    
                    function_metrics = FunctionMetrics(
                        name=node.name,
                        file_path=file_path,
                        start_line=node.lineno,
                        end_line=node.end_lineno,
                        line_count=line_count,
                        complexity=complexity
                    )
                    
                    functions.append(function_metrics)
                    self.total_functions += 1
                    
                    if line_count > self.max_length:
                        self.violations.append(function_metrics)
        
        except SyntaxError as e:
            print(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
        
        return functions
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
        
        return complexity
    
    def scan_directory(self, directory: str, exclude_patterns: Optional[List[str]] = None) -> Dict[str, List[FunctionMetrics]]:
        """Scan directory for Python files and analyze functions"""
        if exclude_patterns is None:
            exclude_patterns = [
                '__pycache__',
                '.git',
                '.venv',
                'node_modules',
                '.backup',
                'migrations'
            ]
        
        results = {}
        
        for root, dirs, files in os.walk(directory):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if not any(pattern in d for pattern in exclude_patterns)]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    
                    # Skip if file path contains excluded patterns
                    if any(pattern in file_path for pattern in exclude_patterns):
                        continue
                    
                    functions = self.analyze_file(file_path)
                    if functions:
                        results[file_path] = functions
        
        return results
    
    def generate_report(self, results: Dict[str, List[FunctionMetrics]]) -> str:
        """Generate comprehensive function length report"""
        violation_count = len(self.violations)
        compliance_rate = ((self.total_functions - violation_count) / self.total_functions * 100) if self.total_functions > 0 else 100
        
        # Sort violations by line count (descending)
        sorted_violations = sorted(self.violations, key=lambda x: x.line_count, reverse=True)
        
        report = f"""# Function Length Compliance Report

## Summary
- **Total Functions Analyzed**: {self.total_functions:,}
- **Functions Exceeding {self.max_length} Lines**: {violation_count:,}
- **Compliance Rate**: {compliance_rate:.1f}%
- **Average Function Length**: {sum(f.line_count for funcs in results.values() for f in funcs) / self.total_functions:.1f} lines

## Top Violations (Longest Functions)

| Function | Lines | File | Complexity |
|----------|-------|------|------------|
"""
        
        # Add top 20 violations
        for violation in sorted_violations[:20]:
            report += f"| `{violation.name}` | {violation.line_count} | `{violation.file_path}` | {violation.complexity} |\n"
        
        if len(sorted_violations) > 20:
            report += f"\n... and {len(sorted_violations) - 20} more violations\n"
        
        # Compliance by file type
        report += "\n## Compliance by File Type\n\n"
        file_types = {}
        for file_path, functions in results.items():
            if 'backend/' in file_path:
                file_type = 'Backend'
            elif 'frontend/' in file_path:
                file_type = 'Frontend'
            elif 'scripts/' in file_path:
                file_type = 'Scripts'
            elif 'infrastructure/' in file_path:
                file_type = 'Infrastructure'
            elif 'mcp-servers/' in file_path:
                file_type = 'MCP Servers'
            else:
                file_type = 'Other'
            
            if file_type not in file_types:
                file_types[file_type] = {'total': 0, 'violations': 0}
            
            file_types[file_type]['total'] += len(functions)
            file_types[file_type]['violations'] += len([f for f in functions if f.line_count > self.max_length])
        
        for file_type, stats in file_types.items():
            compliance = ((stats['total'] - stats['violations']) / stats['total'] * 100) if stats['total'] > 0 else 100
            report += f"- **{file_type}**: {compliance:.1f}% ({stats['violations']}/{stats['total']} violations)\n"
        
        # Recommendations
        report += f"""
## Recommendations

### Immediate Actions (>100 lines)
"""
        critical_violations = [v for v in sorted_violations if v.line_count > 100]
        for violation in critical_violations[:10]:
            report += f"- Refactor `{violation.name}` in `{violation.file_path}` ({violation.line_count} lines)\n"
        
        report += f"""
### Refactoring Patterns
1. **Extract Method**: Break large functions into smaller, focused methods
2. **Template Method**: Use structured initialization for large `__init__` methods
3. **Builder Pattern**: For complex object construction
4. **Configuration Objects**: Replace long parameter lists

### Tools and Automation
1. **Pre-commit Hook**: Add this checker to prevent new violations
2. **IDE Integration**: Use "Extract Method" refactoring tools
3. **Regular Monitoring**: Run weekly compliance reports
4. **Team Training**: Share refactoring best practices

### Success Metrics
- Target: <5% violation rate (currently {violation_count/self.total_functions*100:.1f}%)
- Maximum function length: 75 lines
- Average function length: <30 lines
"""
        
        return report
    
    def check_compliance(self, directory: str = ".") -> bool:
        """Check compliance and return True if all functions are within limit"""
        results = self.scan_directory(directory)
        
        if self.violations:
            print(f"❌ Function length compliance check failed!")
            print(f"Found {len(self.violations)} functions exceeding {self.max_length} lines:")
            
            for violation in sorted(self.violations, key=lambda x: x.line_count, reverse=True)[:10]:
                print(f"  - {violation.name}: {violation.line_count} lines in {violation.file_path}")
            
            if len(self.violations) > 10:
                print(f"  ... and {len(self.violations) - 10} more violations")
            
            return False
        else:
            print(f"✅ All {self.total_functions} functions comply with {self.max_length}-line limit!")
            return True

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Check function length compliance")
    parser.add_argument("--max-length", type=int, default=50, help="Maximum function length (default: 50)")
    parser.add_argument("--directory", type=str, default=".", help="Directory to scan (default: current)")
    parser.add_argument("--report", action="store_true", help="Generate detailed report")
    parser.add_argument("--strict", action="store_true", help="Exit with error code if violations found")
    
    args = parser.parse_args()
    
    checker = FunctionLengthChecker(max_length=args.max_length)
    
    print(f"🔍 Scanning {args.directory} for functions exceeding {args.max_length} lines...")
    
    results = checker.scan_directory(args.directory)
    
    if args.report:
        report = checker.generate_report(results)
        report_file = "FUNCTION_LENGTH_COMPLIANCE_REPORT.md"
        with open(report_file, 'w') as f:
            f.write(report)
        print(f"📊 Detailed report saved to {report_file}")
    
    # Check compliance
    is_compliant = checker.check_compliance(args.directory)
    
    if args.strict and not is_compliant:
        sys.exit(1)
    
    return is_compliant

if __name__ == "__main__":
    main() 