#!/usr/bin/env python3
"""
Cleanup Outdated Model References
Identifies and reports all outdated AI model references in the codebase
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set

# Define outdated models
OUTDATED_MODELS = {
    "claude-3-opus",
    "claude-3-opus-20240229",
    "anthropic/claude-3-opus",
    "gemini-1.5-pro",
    "gemini-1.5-pro-latest",
    "google/gemini-1.5-pro",
    "gpt-4-turbo",
    "gpt-4-turbo-preview",
    "openai/gpt-4-turbo",
    "openai/gpt-4-turbo-preview",
}

# Define modern replacements
MODEL_REPLACEMENTS = {
    # Claude replacements
    "claude-3-opus": "claude-3-5-sonnet-20241022",
    "claude-3-opus-20240229": "claude-3-5-sonnet-20241022",
    "anthropic/claude-3-opus": "anthropic/claude-3.5-sonnet",
    
    # Gemini replacements
    "gemini-1.5-pro": "gemini-2.0-flash-exp",
    "gemini-1.5-pro-latest": "gemini-2.0-flash-exp",
    "google/gemini-1.5-pro": "google/gemini-2.0-flash-exp",
    
    # GPT replacements
    "gpt-4-turbo": "gpt-4o",
    "gpt-4-turbo-preview": "gpt-4o",
    "openai/gpt-4-turbo": "openai/gpt-4o",
    "openai/gpt-4-turbo-preview": "openai/gpt-4o",
}

# File patterns to check
FILE_PATTERNS = [
    "**/*.py",
    "**/*.json",
    "**/*.yaml",
    "**/*.yml",
    "**/*.md",
    "**/*.ts",
    "**/*.tsx",
    "**/*.js",
    "**/*.jsx",
]

# Directories to skip
SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "archive",
    "external",
    "cleanup_backup*",
    "docs_backup*",
    "reports",
}


def find_outdated_references(root_path: Path) -> Dict[str, List[Dict]]:
    """Find all outdated model references in the codebase"""
    findings = {}
    
    for pattern in FILE_PATTERNS:
        for file_path in root_path.glob(pattern):
            # Skip directories
            if any(skip_dir in str(file_path) for skip_dir in SKIP_DIRS):
                continue
            
            try:
                content = file_path.read_text(encoding='utf-8')
                
                # Find all outdated model references
                for model in OUTDATED_MODELS:
                    # Create regex patterns for exact matches
                    patterns = [
                        rf'"{model}"',  # Quoted string
                        rf"'{model}'",  # Single quoted
                        rf'\b{re.escape(model)}\b',  # Word boundary
                    ]
                    
                    for pattern in patterns:
                        matches = list(re.finditer(pattern, content))
                        if matches:
                            if str(file_path) not in findings:
                                findings[str(file_path)] = []
                            
                            for match in matches:
                                line_num = content[:match.start()].count('\n') + 1
                                line = content.split('\n')[line_num - 1].strip()
                                
                                findings[str(file_path)].append({
                                    'model': model,
                                    'line': line_num,
                                    'content': line,
                                    'replacement': MODEL_REPLACEMENTS.get(model, "UNKNOWN"),
                                })
                                
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    
    return findings


def generate_report(findings: Dict[str, List[Dict]]) -> str:
    """Generate a detailed report of findings"""
    report = ["# Outdated Model References Report\n"]
    report.append(f"Total files with outdated references: {len(findings)}\n")
    
    # Count by model
    model_counts = {}
    for file_findings in findings.values():
        for finding in file_findings:
            model = finding['model']
            model_counts[model] = model_counts.get(model, 0) + 1
    
    report.append("\n## Summary by Model\n")
    for model, count in sorted(model_counts.items(), key=lambda x: x[1], reverse=True):
        replacement = MODEL_REPLACEMENTS.get(model, "UNKNOWN")
        report.append(f"- **{model}**: {count} references → replace with `{replacement}`")
    
    report.append("\n## Detailed Findings\n")
    
    # Group by file type
    by_type = {}
    for file_path, file_findings in findings.items():
        ext = Path(file_path).suffix
        if ext not in by_type:
            by_type[ext] = {}
        by_type[ext][file_path] = file_findings
    
    for ext, files in sorted(by_type.items()):
        report.append(f"\n### {ext} Files ({len(files)} files)\n")
        
        for file_path, file_findings in sorted(files.items()):
            report.append(f"\n#### {file_path}\n")
            for finding in file_findings:
                report.append(f"- Line {finding['line']}: `{finding['model']}` → `{finding['replacement']}`")
                report.append(f"  ```\n  {finding['content']}\n  ```")
    
    return "\n".join(report)


def check_airbyte_references(root_path: Path) -> Dict[str, List[Dict]]:
    """Check for Airbyte references that should be Estuary"""
    airbyte_findings = {}
    
    airbyte_patterns = [
        r'\bairbyte\b',
        r'\bAirbyte\b',
        r'\bAIRBYTE\b',
        r'RAW_AIRBYTE',
        r'STG_TRANSFORMED',
    ]
    
    for pattern in FILE_PATTERNS:
        for file_path in root_path.glob(pattern):
            if any(skip_dir in str(file_path) for skip_dir in SKIP_DIRS):
                continue
            
            try:
                content = file_path.read_text(encoding='utf-8')
                
                for airbyte_pattern in airbyte_patterns:
                    matches = list(re.finditer(airbyte_pattern, content, re.IGNORECASE))
                    if matches:
                        if str(file_path) not in airbyte_findings:
                            airbyte_findings[str(file_path)] = []
                        
                        for match in matches:
                            line_num = content[:match.start()].count('\n') + 1
                            line = content.split('\n')[line_num - 1].strip()
                            
                            airbyte_findings[str(file_path)].append({
                                'pattern': match.group(),
                                'line': line_num,
                                'content': line,
                            })
                            
            except Exception as e:
                pass
    
    return airbyte_findings


def main():
    """Main execution"""
    root_path = Path.cwd()
    
    print("🔍 Scanning for outdated model references...")
    model_findings = find_outdated_references(root_path)
    
    print("🔍 Scanning for Airbyte references...")
    airbyte_findings = check_airbyte_references(root_path)
    
    # Generate reports
    model_report = generate_report(model_findings)
    
    # Save model report
    report_path = root_path / "reports" / "outdated_models_report.md"
    report_path.parent.mkdir(exist_ok=True)
    report_path.write_text(model_report)
    print(f"\n✅ Model report saved to: {report_path}")
    
    # Generate Airbyte report
    if airbyte_findings:
        airbyte_report = ["# Airbyte References Report\n"]
        airbyte_report.append(f"Total files with Airbyte references: {len(airbyte_findings)}\n")
        
        for file_path, findings in sorted(airbyte_findings.items()):
            airbyte_report.append(f"\n## {file_path}\n")
            for finding in findings:
                airbyte_report.append(f"- Line {finding['line']}: `{finding['pattern']}`")
                airbyte_report.append(f"  ```\n  {finding['content']}\n  ```")
        
        airbyte_report_path = root_path / "reports" / "airbyte_references_report.md"
        airbyte_report_path.write_text("\n".join(airbyte_report))
        print(f"✅ Airbyte report saved to: {airbyte_report_path}")
    
    # Print summary
    print(f"\n📊 Summary:")
    print(f"- Files with outdated models: {len(model_findings)}")
    print(f"- Files with Airbyte references: {len(airbyte_findings)}")
    
    total_issues = sum(len(findings) for findings in model_findings.values())
    total_airbyte = sum(len(findings) for findings in airbyte_findings.values())
    
    print(f"- Total outdated model references: {total_issues}")
    print(f"- Total Airbyte references: {total_airbyte}")
    
    return len(model_findings) + len(airbyte_findings)


if __name__ == "__main__":
    exit_code = main()
    exit(0 if exit_code == 0 else 1) 