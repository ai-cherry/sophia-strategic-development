#!/usr/bin/env python3
"""Identify all Python syntax and linting issues in the codebase."""

import ast
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

def check_python_file(filepath: Path) -> Dict[str, List[str]]:
    """Check a Python file for various issues.
    
    Args:
        filepath: Path to the Python file
        
    Returns:
        Dictionary of issue types and their descriptions
    """
    issues = {
        "syntax_errors": [],
        "docstring_issues": [],
        "import_issues": [],
        "indentation_issues": [],
        "other_issues": []
    }
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Try to parse the file
        try:
            tree = ast.parse(content)
            
            # Check for docstring issues
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                    docstring = ast.get_docstring(node)
                    if docstring:
                        lines = docstring.strip().split('\n')
                        if lines and lines[0].endswith(('.', ':', ';')):
                            issues["docstring_issues"].append(
                                f"Line {node.lineno}: Docstring first line ends with punctuation"
                            )
                            
        except SyntaxError as e:
            issues["syntax_errors"].append(f"Line {e.lineno}: {e.msg}")
            
        # Check for common patterns
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            # Check for incomplete try/except blocks
            if line.strip() == "except Exception:" and i < len(lines):
                next_line = lines[i] if i < len(lines) else ""
                if not next_line.strip() or (next_line and not next_line.startswith(' ' * 8)):
                    issues["syntax_errors"].append(
                        f"Line {i}: Incomplete exception block"
                    )
                    
            # Check for trailing whitespace
            if line.rstrip() != line:
                issues["other_issues"].append(
                    f"Line {i}: Trailing whitespace"
                )
                
    except Exception as e:
        issues["other_issues"].append(f"Error reading file: {str(e)}")
        
    return issues

def scan_directory(directory: Path) -> Dict[Path, Dict[str, List[str]]]:
    """Scan a directory for Python files with issues.
    
    Args:
        directory: Directory to scan
        
    Returns:
        Dictionary mapping file paths to their issues
    """
    all_issues = {}
    
    for py_file in directory.rglob("*.py"):
        # Skip virtual environments and node_modules
        if any(part in py_file.parts for part in ['venv', 'env', '.venv', 'node_modules', '__pycache__']):
            continue
            
        issues = check_python_file(py_file)
        if any(issue_list for issue_list in issues.values()):
            all_issues[py_file] = issues
            
    return all_issues

def generate_report(all_issues: Dict[Path, Dict[str, List[str]]]) -> str:
    """Generate a report of all issues found.
    
    Args:
        all_issues: Dictionary of file paths to issues
        
    Returns:
        Formatted report string
    """
    report = ["# Python Issues Report", ""]
    
    # Summary
    total_files = len(all_issues)
    total_issues = sum(
        len(issue)
        for file_issues in all_issues.values()
        for issue in file_issues.values()
    )
    
    report.append(f"## Summary")
    report.append(f"- Total files with issues: {total_files}")
    report.append(f"- Total issues found: {total_issues}")
    report.append("")
    
    # Group by issue type
    issue_types = {
        "syntax_errors": "Syntax Errors",
        "docstring_issues": "Docstring Issues",
        "import_issues": "Import Issues",
        "indentation_issues": "Indentation Issues",
        "other_issues": "Other Issues"
    }
    
    for issue_key, issue_name in issue_types.items():
        files_with_issue = [
            (path, issues[issue_key])
            for path, issues in all_issues.items()
            if issues[issue_key]
        ]
        
        if files_with_issue:
            report.append(f"## {issue_name}")
            report.append(f"Found in {len(files_with_issue)} files:")
            report.append("")
            
            for path, issues in sorted(files_with_issue):
                report.append(f"### {path}")
                for issue in issues:
                    report.append(f"- {issue}")
                report.append("")
                
    return "\n".join(report)

def main():
    """Main function to scan the repository and generate a report."""
    # Get the repository root
    repo_root = Path(__file__).parent.parent
    
    print("Scanning for Python issues...")
    all_issues = scan_directory(repo_root)
    
    if all_issues:
        report = generate_report(all_issues)
        
        # Save report
        report_path = repo_root / "python_issues_report.md"
        with open(report_path, 'w') as f:
            f.write(report)
            
        print(f"\nReport saved to: {report_path}")
        print(f"\nFound issues in {len(all_issues)} files")
        
        # Print summary to console
        for path, issues in list(all_issues.items())[:5]:
            print(f"\n{path}:")
            for issue_type, issue_list in issues.items():
                if issue_list:
                    print(f"  {issue_type}: {len(issue_list)} issues")
                    
        if len(all_issues) > 5:
            print(f"\n... and {len(all_issues) - 5} more files")
    else:
        print("No issues found!")

if __name__ == "__main__":
    main()
