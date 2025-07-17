#!/usr/bin/env python3
"""
Comprehensive Syntax Error Scanner for Sophia AI
Scans entire codebase for Python syntax errors using AST parsing
"""

import ast
import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any
import traceback

class SyntaxErrorScanner:
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.errors = []
        self.checked_files = 0
        self.error_files = 0
        
    def scan_file(self, file_path: Path) -> Dict[str, Any]:
        """Scan a single Python file for syntax errors"""
        result = {
            'file': str(file_path),
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try to parse with AST
            try:
                ast.parse(content, filename=str(file_path))
                result['valid'] = True
            except SyntaxError as e:
                result['valid'] = False
                result['errors'].append({
                    'type': 'SyntaxError',
                    'message': str(e),
                    'line': e.lineno,
                    'column': e.offset,
                    'text': e.text.strip() if e.text else None
                })
            except TabError as e:
                result['valid'] = False
                result['errors'].append({
                    'type': 'TabError',
                    'message': str(e),
                    'line': e.lineno,
                    'column': e.offset,
                    'text': e.text.strip() if e.text else None
                })
            except IndentationError as e:
                result['valid'] = False
                result['errors'].append({
                    'type': 'IndentationError',
                    'message': str(e),
                    'line': e.lineno,
                    'column': e.offset,
                    'text': e.text.strip() if e.text else None
                })
            except Exception as e:
                result['warnings'].append({
                    'type': 'ParseError',
                    'message': f"Unexpected parsing error: {str(e)}"
                })
            
            # Check for common problematic patterns
            self._check_common_issues(content, result)
            
        except UnicodeDecodeError as e:
            result['errors'].append({
                'type': 'UnicodeDecodeError',
                'message': f"File encoding issue: {str(e)}"
            })
        except Exception as e:
            result['errors'].append({
                'type': 'FileError',
                'message': f"Could not read file: {str(e)}"
            })
        
        return result
    
    def _check_common_issues(self, content: str, result: Dict[str, Any]) -> None:
        """Check for common syntax issues that might not be caught by AST"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Check for incomplete statements
            if line_stripped.endswith(':') and not any(keyword in line_stripped for keyword in [
                'def ', 'class ', 'if ', 'elif ', 'else:', 'for ', 'while ', 
                'try:', 'except', 'finally:', 'with ', 'async def'
            ]):
                result['warnings'].append({
                    'type': 'IncompleteStatement',
                    'message': 'Line ends with colon but may be incomplete',
                    'line': i,
                    'text': line_stripped
                })
            
            # Check for unmatched brackets/parentheses in single line
            if line_stripped and not line_stripped.startswith('#'):
                open_parens = line_stripped.count('(') - line_stripped.count(')')
                open_brackets = line_stripped.count('[') - line_stripped.count(']')
                open_braces = line_stripped.count('{') - line_stripped.count('}')
                
                if abs(open_parens) > 2 or abs(open_brackets) > 1 or abs(open_braces) > 1:
                    result['warnings'].append({
                        'type': 'UnmatchedBrackets',
                        'message': f'Possible unmatched brackets: () diff={open_parens}, [] diff={open_brackets}, {{}} diff={open_braces}',
                        'line': i,
                        'text': line_stripped
                    })
    
    def scan_directory(self, include_patterns: List[str] = None) -> Dict[str, Any]:
        """Scan all Python files in directory"""
        if include_patterns is None:
            include_patterns = ['*.py']
        
        results = {
            'summary': {
                'total_files': 0,
                'error_files': 0,
                'valid_files': 0,
                'warning_files': 0
            },
            'files': {},
            'errors_by_type': {},
            'critical_errors': []
        }
        
        # Find all Python files
        python_files = []
        for pattern in include_patterns:
            python_files.extend(self.root_dir.rglob(pattern))
        
        # Filter out certain directories
        exclude_dirs = {'.venv', 'venv', '__pycache__', '.git', 'node_modules', '.next', 'build', 'dist'}
        python_files = [f for f in python_files if not any(part in exclude_dirs for part in f.parts)]
        
        print(f"🔍 Scanning {len(python_files)} Python files for syntax errors...")
        
        for file_path in python_files:
            result = self.scan_file(file_path)
            results['files'][str(file_path)] = result
            
            results['summary']['total_files'] += 1
            
            if result['errors']:
                results['summary']['error_files'] += 1
                
                # Categorize errors
                for error in result['errors']:
                    error_type = error['type']
                    if error_type not in results['errors_by_type']:
                        results['errors_by_type'][error_type] = []
                    results['errors_by_type'][error_type].append({
                        'file': str(file_path),
                        'error': error
                    })
                    
                    # Critical errors that completely break syntax
                    if error_type in ['SyntaxError', 'IndentationError', 'TabError']:
                        results['critical_errors'].append({
                            'file': str(file_path),
                            'error': error
                        })
            else:
                results['summary']['valid_files'] += 1
            
            if result['warnings']:
                results['summary']['warning_files'] += 1
        
        return results
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate a comprehensive report"""
        report = ["=" * 80]
        report.append("🔍 COMPREHENSIVE SYNTAX ERROR SCAN REPORT")
        report.append("=" * 80)
        report.append(f"📊 SUMMARY:")
        report.append(f"  Total Files Scanned: {results['summary']['total_files']}")
        report.append(f"  Files with Errors: {results['summary']['error_files']}")
        report.append(f"  Valid Files: {results['summary']['valid_files']}")
        report.append(f"  Files with Warnings: {results['summary']['warning_files']}")
        
        # Success rate
        if results['summary']['total_files'] > 0:
            success_rate = (results['summary']['valid_files'] / results['summary']['total_files']) * 100
            report.append(f"  Success Rate: {success_rate:.1f}%")
        
        report.append("")
        
        # Critical errors (break compilation)
        if results['critical_errors']:
            report.append("🚨 CRITICAL SYNTAX ERRORS (MUST FIX):")
            report.append("-" * 50)
            for error_item in results['critical_errors']:
                error = error_item['error']
                report.append(f"❌ {error_item['file']}")
                report.append(f"   {error['type']}: {error['message']}")
                if 'line' in error:
                    report.append(f"   Line {error['line']}: {error.get('text', 'N/A')}")
                report.append("")
        else:
            report.append("✅ NO CRITICAL SYNTAX ERRORS FOUND!")
            report.append("")
        
        # Error breakdown by type
        if results['errors_by_type']:
            report.append("📊 ERRORS BY TYPE:")
            report.append("-" * 30)
            for error_type, errors in results['errors_by_type'].items():
                report.append(f"  {error_type}: {len(errors)} files")
            report.append("")
        
        # Top error files
        error_files = [(f, len(data['errors'])) for f, data in results['files'].items() if data['errors']]
        if error_files:
            error_files.sort(key=lambda x: x[1], reverse=True)
            report.append("📁 FILES WITH MOST ERRORS:")
            report.append("-" * 40)
            for file_path, error_count in error_files[:10]:
                report.append(f"  {error_count} errors: {file_path}")
            report.append("")
        
        # Files with warnings
        warning_files = [f for f, data in results['files'].items() if data['warnings']]
        if warning_files:
            report.append(f"⚠️  FILES WITH WARNINGS ({len(warning_files)}):")
            report.append("-" * 40)
            for file_path in warning_files[:10]:
                warnings = results['files'][file_path]['warnings']
                report.append(f"  {len(warnings)} warnings: {file_path}")
            if len(warning_files) > 10:
                report.append(f"  ... and {len(warning_files) - 10} more files")
            report.append("")
        
        # Recommendations
        report.append("💡 RECOMMENDATIONS:")
        report.append("-" * 20)
        if results['critical_errors']:
            report.append("  1. Fix all CRITICAL errors first - these prevent code from running")
            report.append("  2. Focus on SyntaxError and IndentationError types")
            report.append("  3. Use an IDE with syntax highlighting to catch errors early")
        else:
            report.append("  ✅ No critical syntax errors found!")
            if results['summary']['warning_files'] > 0:
                report.append("  • Review warning files for potential issues")
            report.append("  • Consider running additional linting tools (ruff, flake8)")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)

def main():
    scanner = SyntaxErrorScanner()
    
    print("🚀 Starting comprehensive syntax error scan...")
    results = scanner.scan_directory()
    
    # Generate report
    report = scanner.generate_report(results)
    print(report)
    
    # Save detailed results to JSON
    output_file = "SYNTAX_ERROR_SCAN_RESULTS.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {output_file}")
    
    # Save report to markdown
    report_file = "SYNTAX_ERROR_SCAN_REPORT.md"
    with open(report_file, 'w') as f:
        f.write("# Syntax Error Scan Report\n\n")
        f.write("```\n")
        f.write(report)
        f.write("\n```\n")
    
    print(f"📝 Report saved to: {report_file}")
    
    # Return appropriate exit code
    if results['critical_errors']:
        print(f"\n❌ Found {len(results['critical_errors'])} critical syntax errors!")
        return 1
    else:
        print(f"\n✅ No critical syntax errors found! Code is syntactically valid.")
        return 0

if __name__ == "__main__":
    sys.exit(main()) 