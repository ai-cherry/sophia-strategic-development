#!/usr/bin/env python3
"""
Daily Technical Debt Scanner
Runs automated scans to detect technical debt accumulation
"""

import subprocess
import datetime
import json
from pathlib import Path

def scan_wildcard_imports():
    """Scan for wildcard imports"""
    result = subprocess.run(
        ["grep", "-r", "from .* import \*", "--include=*.py", "."],
        capture_output=True, text=True
    )
    return len(result.stdout.split('\n')) if result.stdout.strip() else 0

def scan_todos():
    """Scan for TODO items"""
    result = subprocess.run(
        ["grep", "-r", "TODO\|FIXME\|XXX\|HACK", "--include=*.py", "."],
        capture_output=True, text=True
    )
    return len(result.stdout.split('\n')) if result.stdout.strip() else 0

def scan_temporary_code():
    """Scan for temporary code"""
    patterns = ["placeholder", "temporary", "temp", "for now", "mock.*for now"]
    total = 0
    for pattern in patterns:
        result = subprocess.run(
            ["grep", "-r", pattern, "--include=*.py", "."],
            capture_output=True, text=True
        )
        total += len(result.stdout.split('\n')) if result.stdout.strip() else 0
    return total

def generate_report():
    """Generate daily technical debt report"""
    report = {
        "date": datetime.datetime.now().isoformat(),
        "wildcard_imports": scan_wildcard_imports(),
        "todos": scan_todos(),
        "temporary_code": scan_temporary_code()
    }
    
    # Save report
    report_file = Path("daily_tech_debt_report.json")
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
    
    # Check thresholds
    alerts = []
    if report["wildcard_imports"] > 5:
        alerts.append(f"HIGH: {report['wildcard_imports']} wildcard imports detected")
    if report["todos"] > 50:
        alerts.append(f"HIGH: {report['todos']} TODO items detected")
    if report["temporary_code"] > 10:
        alerts.append(f"MEDIUM: {report['temporary_code']} temporary code items detected")
    
    if alerts:
        print("🚨 TECHNICAL DEBT ALERTS:")
        for alert in alerts:
            print(f"  - {alert}")
    else:
        print("✅ Technical debt levels within acceptable limits")
    
    return report

if __name__ == "__main__":
    generate_report()
