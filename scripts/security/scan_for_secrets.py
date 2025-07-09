#!/usr/bin/env python3
"""
Comprehensive secret scanner for Sophia AI repository.
Detects exposed credentials, API keys, and sensitive information.
"""

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Patterns for detecting secrets
SECRET_PATTERNS = {
    "aws_access_key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "aws_secret_key": re.compile(
        r'(?i)aws(.{0,20})?(?-i)[\'"\s]?(?:secret|access)(.{0,20})?[\'"\s]?(?:key|token)(.{0,20})?[\'"\s]?[=:]\s*[\'"]?([A-Za-z0-9/+=]{40})[\'"]?'
    ),
    "github_token": re.compile(r"gh[ps]_[a-zA-Z0-9]{36,}"),
    "github_pat": re.compile(r"github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}"),
    "private_key": re.compile(
        r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"
    ),
    "api_key_generic": re.compile(
        r'(?i)(?:api[_\-\s]?key|apikey)[\'"\s]*[=:]\s*[\'"]?([a-zA-Z0-9_\-]{20,})[\'"]?'
    ),
    "secret_generic": re.compile(
        r'(?i)(?:secret|password|passwd|pwd)[\'"\s]*[=:]\s*[\'"]?([^\s\'"\n]{8,})[\'"]?'
    ),
    "bearer_token": re.compile(r"(?i)bearer\s+[a-zA-Z0-9_\-\.]+"),
    "basic_auth": re.compile(r"(?i)basic\s+[a-zA-Z0-9_\-\.=]+"),
    "slack_token": re.compile(r"xox[baprs]-[0-9A-Za-z\-]+"),
    "stripe_key": re.compile(r"(?:sk|pk)_(?:test|live)_[0-9a-zA-Z]{24,}"),
    "pypi_token": re.compile(r"pypi-[a-zA-Z0-9_\-]{40,}"),
    "npm_token": re.compile(r"npm_[a-zA-Z0-9]{36}"),
    "lambda_api_key": re.compile(r"secret_[a-zA-Z0-9]+_[a-f0-9]{32}\.[a-zA-Z0-9]{28}"),
    "snowflake_password": re.compile(
        r'(?i)snowflake[_\-]?(?:password|pwd|pass)[\'"\s]*[=:]\s*[\'"]?([^\s\'"\n]{8,})[\'"]?'
    ),
    "openai_key": re.compile(r"sk-[a-zA-Z0-9]{48}"),
    "anthropic_key": re.compile(r"sk-ant-[a-zA-Z0-9\-]{95}"),
    "ssh_key": re.compile(r"ssh-(?:rsa|ed25519|ecdsa|dsa)\s+[A-Za-z0-9+/]+[=]{0,2}"),
    "jwt_token": re.compile(r"eyJ[A-Za-z0-9_\-]+\.eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+"),
    "docker_token": re.compile(r"dckr_pat_[a-zA-Z0-9_\-]{20,}"),
    "pulumi_token": re.compile(r"pul-[a-f0-9]{40}"),
}

# File extensions to scan
SCAN_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".json",
    ".yaml",
    ".yml",
    ".env",
    ".sh",
    ".bash",
    ".zsh",
    ".fish",
    ".md",
    ".txt",
    ".conf",
    ".ini",
    ".cfg",
    ".toml",
    ".xml",
    ".sql",
    ".dockerfile",
    ".dockerignore",
}

# Paths to exclude from scanning
EXCLUDE_PATHS = {
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    "env",
    "dist",
    "build",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "coverage",
    ".next",
    ".vercel",
    "external",
}

# Known false positives (add patterns here)
FALSE_POSITIVES = {
    "example",
    "dummy",
    "placeholder",
    "your-",
    "xxx",
    "...",
    "test-key",
    "fake-key",
    "<your",
    "${",
    "{{",
    "sample",
}


class SecretScanner:
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.findings: list[dict] = []
        self.scanned_files = 0
        self.total_secrets = 0

    def should_scan_file(self, file_path: Path) -> bool:
        """Check if file should be scanned."""
        # Check if in excluded directory
        for part in file_path.parts:
            if part in EXCLUDE_PATHS:
                return False

        # Check extension
        if file_path.suffix.lower() not in SCAN_EXTENSIONS and file_path.name not in [
            ".env",
            "Dockerfile",
        ]:
            return False

        # Skip if file is too large (> 1MB)
        if file_path.stat().st_size > 1024 * 1024:
            return False

        return True

    def is_false_positive(self, secret: str, context: str) -> bool:
        """Check if the found secret is a false positive."""
        secret_lower = secret.lower()
        context_lower = context.lower()

        # Check for known false positive patterns
        for fp in FALSE_POSITIVES:
            if fp in secret_lower or fp in context_lower:
                return True

        # Check if it's a variable reference
        if secret.startswith("$") or secret.startswith("process.env"):
            return True

        # Check if it's too short or too repetitive
        if len(secret) < 8 or len(set(secret)) < 4:
            return True

        return False

    def scan_file(self, file_path: Path) -> list[dict]:
        """Scan a single file for secrets."""
        findings = []

        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()
                lines = content.splitlines()

            for pattern_name, pattern in SECRET_PATTERNS.items():
                for match in pattern.finditer(content):
                    # Get line number
                    line_start = content[: match.start()].count("\n") + 1

                    # Get the matched secret
                    if match.groups():
                        secret = (
                            match.group(1)
                            if len(match.groups()) >= 1
                            else match.group(0)
                        )
                    else:
                        secret = match.group(0)

                    # Get context (line containing the secret)
                    context_line = (
                        lines[line_start - 1] if line_start <= len(lines) else ""
                    )

                    # Check for false positives
                    if self.is_false_positive(secret, context_line):
                        continue

                    findings.append(
                        {
                            "file": str(file_path.relative_to(self.root_path)),
                            "line": line_start,
                            "type": pattern_name,
                            "secret": secret[:20] + "..."
                            if len(secret) > 20
                            else secret,
                            "context": context_line.strip()[:100],
                            "severity": self.get_severity(pattern_name),
                        }
                    )

        except Exception as e:
            print(f"Error scanning {file_path}: {e}")

        return findings

    def get_severity(self, pattern_type: str) -> str:
        """Determine severity of the secret type."""
        high_severity = {
            "private_key",
            "aws_secret_key",
            "github_token",
            "github_pat",
            "lambda_api_key",
            "stripe_key",
            "docker_token",
            "pulumi_token",
        }

        medium_severity = {
            "api_key_generic",
            "bearer_token",
            "slack_token",
            "openai_key",
            "anthropic_key",
            "snowflake_password",
            "jwt_token",
        }

        if pattern_type in high_severity:
            return "HIGH"
        elif pattern_type in medium_severity:
            return "MEDIUM"
        else:
            return "LOW"

    def scan_directory(self) -> None:
        """Scan entire directory for secrets."""
        print(f"🔍 Scanning directory: {self.root_path}")
        print("=" * 80)

        for file_path in self.root_path.rglob("*"):
            if file_path.is_file() and self.should_scan_file(file_path):
                self.scanned_files += 1
                findings = self.scan_file(file_path)

                if findings:
                    self.findings.extend(findings)
                    self.total_secrets += len(findings)

                # Progress indicator
                if self.scanned_files % 100 == 0:
                    print(f"Scanned {self.scanned_files} files...")

    def check_git_history(self) -> list[dict]:
        """Check git history for secrets (last 100 commits)."""
        print("\n🔍 Checking git history...")
        history_findings = []

        try:
            # Get list of commits
            result = subprocess.run(
                ["git", "log", "--oneline", "-n", "100"],
                capture_output=True,
                text=True,
                check=True,
            )

            commits = [line.split()[0] for line in result.stdout.strip().split("\n")]

            for i, commit in enumerate(commits):
                if i % 10 == 0:
                    print(f"Checking commit {i+1}/{len(commits)}...")

                # Get diff for commit
                diff_result = subprocess.run(
                    ["git", "show", commit], capture_output=True, text=True, check=True
                )

                # Check diff for secrets
                for pattern_name, pattern in SECRET_PATTERNS.items():
                    for match in pattern.finditer(diff_result.stdout):
                        if match.groups():
                            secret = (
                                match.group(1)
                                if len(match.groups()) >= 1
                                else match.group(0)
                            )
                        else:
                            secret = match.group(0)

                        # Get context
                        lines = diff_result.stdout.splitlines()
                        for j, line in enumerate(lines):
                            if secret in line and not self.is_false_positive(
                                secret, line
                            ):
                                history_findings.append(
                                    {
                                        "commit": commit,
                                        "type": pattern_name,
                                        "secret": secret[:20] + "..."
                                        if len(secret) > 20
                                        else secret,
                                        "context": line.strip()[:100],
                                        "severity": self.get_severity(pattern_name),
                                    }
                                )

        except subprocess.CalledProcessError:
            print("Warning: Could not check git history (not a git repository?)")

        return history_findings

    def generate_report(self) -> None:
        """Generate and display the security report."""
        print("\n" + "=" * 80)
        print("🔒 SECRET SCANNING REPORT")
        print("=" * 80)

        print("\n📊 Summary:")
        print(f"  Files scanned: {self.scanned_files}")
        print(f"  Total secrets found: {self.total_secrets}")

        if not self.findings:
            print("\n✅ No secrets found in current files!")
        else:
            # Group by severity
            high = [f for f in self.findings if f["severity"] == "HIGH"]
            medium = [f for f in self.findings if f["severity"] == "MEDIUM"]
            low = [f for f in self.findings if f["severity"] == "LOW"]

            print("\n🚨 Severity Breakdown:")
            print(f"  HIGH: {len(high)}")
            print(f"  MEDIUM: {len(medium)}")
            print(f"  LOW: {len(low)}")

            # Show high severity findings
            if high:
                print("\n🔴 HIGH SEVERITY FINDINGS:")
                for finding in high[:10]:  # Show first 10
                    print(f"\n  File: {finding['file']}")
                    print(f"  Line: {finding['line']}")
                    print(f"  Type: {finding['type']}")
                    print(f"  Secret: {finding['secret']}")
                    print(f"  Context: {finding['context']}")

                if len(high) > 10:
                    print(f"\n  ... and {len(high) - 10} more HIGH severity findings")

        # Check git history
        history_findings = self.check_git_history()
        if history_findings:
            print(f"\n⚠️  Found {len(history_findings)} secrets in git history!")
            print("  Run 'git filter-branch' or use BFG Repo-Cleaner to remove them")

        # Save detailed report
        self.save_report()

    def save_report(self) -> None:
        """Save detailed report to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"secret_scan_report_{timestamp}.json"

        report = {
            "timestamp": timestamp,
            "summary": {
                "files_scanned": self.scanned_files,
                "total_secrets": self.total_secrets,
                "high_severity": len(
                    [f for f in self.findings if f["severity"] == "HIGH"]
                ),
                "medium_severity": len(
                    [f for f in self.findings if f["severity"] == "MEDIUM"]
                ),
                "low_severity": len(
                    [f for f in self.findings if f["severity"] == "LOW"]
                ),
            },
            "findings": self.findings,
        }

        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Detailed report saved to: {report_file}")

    def run(self) -> int:
        """Run the complete scan."""
        self.scan_directory()
        self.generate_report()

        # Return exit code based on findings
        high_severity = [f for f in self.findings if f["severity"] == "HIGH"]
        return 1 if high_severity else 0


def main():
    """Main entry point."""
    scanner = SecretScanner()
    exit_code = scanner.run()

    if exit_code != 0:
        print("\n❌ High severity secrets found! Fix these before committing.")
    else:
        print("\n✅ No high severity secrets found.")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
