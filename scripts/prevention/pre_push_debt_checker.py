#!/usr/bin/env python3
"""
Pre-push Technical Debt Checker
Prevents pushing commits with high technical debt
"""

import subprocess
import sys

def check_debt_levels():
    """Check current technical debt levels"""
    # Run daily scanner
    result = subprocess.run([sys.executable, "scripts/prevention/daily_tech_debt_scanner.py"], 
                          capture_output=True, text=True)
    
    # Parse output for alerts
    if "🚨 TECHNICAL DEBT ALERTS:" in result.stdout:
        print("❌ PUSH BLOCKED: High technical debt detected!")
        print(result.stdout)
        return False
    
    print("✅ Technical debt levels acceptable for push")
    return True

if __name__ == "__main__":
    if not check_debt_levels():
        sys.exit(1)
