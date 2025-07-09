#!/usr/bin/env python3
"""
Cleanup Outdated Model References
Identifies and reports all outdated AI model references in the codebase
"""

import re
from pathlib import Path
from typing import Dict, List, Any

# Define outdated models
OUTDATED_MODELS = {
    "claude-3-5-sonnet-20241022",
    "claude-3-5-sonnet-20241022",
    "anthropic/claude-3.5-sonnet",
    "gemini-2.0-flash-exp",
    "gemini-2.0-flash-exp",
    "google/gemini-2.0-flash-exp",
    "gpt-4o",
    "gpt-4o",
    "openai/gpt-4o",
    "openai/gpt-4o",
}

# Define modern replacements
MODEL_REPLACEMENTS = {
    # Claude replacements
    "claude-3-5-sonnet-20241022": "claude-3-5-sonnet-20241022",
    "claude-3-5-sonnet-20241022": "claude-3-5-sonnet-20241022",
    "anthropic/claude-3.5-sonnet": "anthropic/claude-3.5-sonnet",
    # Gemini replacements
    "gemini-2.0-flash-exp": "gemini-2.0-flash-exp",
    "gemini-2.0-flash-exp": "gemini-2.0-flash-exp",
    "google/gemini-2.0-flash-exp": "google/gemini-2.0-flash-exp",
    # GPT replacements
    "gpt-4o": "gpt-4o",
    "gpt-4o": "gpt-4o",
    "openai/gpt-4o": "openai/gpt-4o",
    "openai/gpt-4o": "openai/gpt-4o",
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


def find_outdated_references(root_path: Path) -> dict[str, list[dict]]:
    """Find all outdated model references in the codebase"""
    findings = {}

    for pattern in FILE_PATTERNS:
        for file_path in root_path.glob(pattern):
            # Skip directories
            if any(skip_dir in str(file_path) for skip_dir in SKIP_DIRS):
                continue

            try:
                content = file_path.read_text(encoding="utf-8")

                # Find all outdated model references
                for model in OUTDATED_MODELS:
                    # Create regex patterns for exact matches
                    patterns = [
                        rf'"{model}"',  # Quoted string
                        rf"'{model}'",  # Single quoted
                        rf"\b{re.escape(model)}\b",  # Word boundary
                    ]

                    for pattern in patterns:
                        matches = list(re.finditer(pattern, content))
                        if matches:
                            if str(file_path) not in findings:
                                findings[str(file_path)] = []

                            for match in matches:
                                line_num = content[: match.start()].count("\n") + 1
                                line = content.split("\n")[line_num - 1].strip()

                                findings[str(file_path)].append(
                                    {
                                        "model": model,
                                        "line": line_num,
                                        "content": line,
                                        "replacement": MODEL_REPLACEMENTS.get(
                                            model, "UNKNOWN"
                                        ),
                                    }
                                )

            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    return findings


def generate_report(findings: dict[str, list[dict]]) -> str:
    """Generate a detailed report of findings"""
    report = ["# Outdated Model References Report\n"]
    report.append(f"Total files with outdated references: {len(findings)}\n")

    # Count by model
    model_counts = {}
    for file_findings in findings.values():
        for finding in file_findings:
            model = finding["model"]
            model_counts[model] = model_counts.get(model, 0) + 1

    report.append("\n## Summary by Model\n")
    for model, count in sorted(model_counts.items(), key=lambda x: x[1], reverse=True):
        replacement = MODEL_REPLACEMENTS.get(model, "UNKNOWN")
        report.append(
            f"- **{model}**: {count} references → replace with `{replacement}`"
        )

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
                report.append(
                    f"- Line {finding['line']}: `{finding['model']}` → `{finding['replacement']}`"
                )
                report.append(f"  ```\n  {finding['content']}\n  ```")

    return "\n".join(report)


def check_outdated_references(root_path: Path) -> Dict[str, List[Dict[str, Any]]]:
    """Check for outdated model and service references"""
    outdated_findings = {}
    
    outdated_patterns = [
        # Outdated models
        (r"text-davinci-00[0-3]", "gpt-3.5-turbo or gpt-4"),
        (r"code-davinci-00[0-2]", "gpt-3.5-turbo or gpt-4"),
        (r"text-curie-001", "gpt-3.5-turbo"),
        (r"text-babbage-001", "gpt-3.5-turbo"),
        (r"text-ada-001", "gpt-3.5-turbo"),
        # Add more outdated patterns as needed
    ]
    
    for pattern in FILE_PATTERNS:
        for file_path in root_path.glob(pattern):
            if any(skip_dir in str(file_path) for skip_dir in SKIP_DIRS):
                continue

            try:
                content = file_path.read_text(encoding="utf-8")

                for outdated_pattern in outdated_patterns:
                    pattern, replacement = outdated_pattern
                    matches = list(re.finditer(pattern, content, re.IGNORECASE))
                    if matches:
                        if str(file_path) not in outdated_findings:
                            outdated_findings[str(file_path)] = []

                        for match in matches:
                            line_num = content[: match.start()].count("\n") + 1
                            line = content.split("\n")[line_num - 1].strip()

                            outdated_findings[str(file_path)].append(
                                {
                                    "pattern": match.group(),
                                    "line": line_num,
                                    "content": line,
                                    "replacement": replacement,
                                }
                            )

            except Exception:
                pass

    return outdated_findings


def check_estuary_references(root_path: Path) -> Dict[str, List[Dict[str, Any]]]:
    """Check for Estuary Flow references"""
    estuary_findings = {}
    
    estuary_patterns = [
        r"\bestuary\b",
        r"\bEstuary\b",
        r"\bESTUARY\b",
    ]
    
    for pattern in FILE_PATTERNS:
        for file_path in root_path.glob(pattern):
            if any(skip_dir in str(file_path) for skip_dir in SKIP_DIRS):
                continue

            try:
                content = file_path.read_text(encoding="utf-8")

                for estuary_pattern in estuary_patterns:
                    matches = list(re.finditer(estuary_pattern, content, re.IGNORECASE))
                    if matches:
                        if str(file_path) not in estuary_findings:
                            estuary_findings[str(file_path)] = []

                        for match in matches:
                            line_num = content[: match.start()].count("\n") + 1
                            line = content.split("\n")[line_num - 1].strip()

                            estuary_findings[str(file_path)].append(
                                {
                                    "pattern": match.group(),
                                    "line": line_num,
                                    "content": line,
                                }
                            )

            except Exception:
                pass

    return estuary_findings


def main():
    """Main function to run all checks"""
    root_path = Path.cwd()
    
    print("🔍 Scanning codebase for outdated references...")
    print("=" * 60)
    
    # Check for outdated models
    model_findings = check_outdated_references(root_path)
    
    # Check for Estuary Flow references
    estuary_findings = check_estuary_references(root_path)
    
    # Generate reports
    model_report = generate_report(model_findings)

    # Save model report
    report_path = root_path / "reports" / "outdated_models_report.md"
    report_path.parent.mkdir(exist_ok=True)
    report_path.write_text(model_report)
    print(f"\n✅ Model report saved to: {report_path}")

    # Generate Estuary Flow report
    if estuary_findings:
        estuary_report = ["# Estuary Flow References Report\n"]
        estuary_report.append(
            f"Total files with Estuary Flow references: {len(estuary_findings)}\n"
        )

        for file_path, findings in sorted(estuary_findings.items()):
            estuary_report.append(f"\n## {file_path}\n")
            for finding in findings:
                estuary_report.append(
                    f"- Line {finding['line']}: `{finding['pattern']}`"
                )
                estuary_report.append(f"  ```\n  {finding['content']}\n  ```")

        estuary_report_path = root_path / "reports" / "estuary_references_report.md"
        estuary_report_path.write_text("\n".join(estuary_report))
        print(f"✅ Estuary Flow report saved to: {estuary_report_path}")

    # Print summary
    print("\n📊 Summary:")
    print(f"- Files with outdated models: {len(model_findings)}")
    print(f"- Files with Estuary Flow references: {len(estuary_findings)}")

    total_issues = sum(len(findings) for findings in model_findings.values())
    total_estuary = sum(len(findings) for findings in estuary_findings.values())

    print(f"- Total outdated model references: {total_issues}")
    print(f"- Total Estuary Flow references: {total_estuary}")

    return len(model_findings) + len(estuary_findings)


if __name__ == "__main__":
    exit_code = main()
    exit(0 if exit_code == 0 else 1)
