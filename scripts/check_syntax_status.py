#!/usr/bin/env python3
"""
Quick script to check the current syntax validation status
"""

import json
from pathlib import Path


def check_status():
    """Check current syntax status from validation report"""
    try:
        with open("syntax_validation_report.json", "r") as f:
            report = json.load(f)

        print("🔍 Sophia AI Syntax Status Check")
        print("=" * 50)
        print(f"Total files: {report['total_files']}")
        print(f"Valid files: {report['valid_files']}")
        print(f"Files with errors: {report['error_count']}")
        print(f"Success rate: {report['success_rate']}")
        print(f"\nTimestamp: {report['timestamp']}")

        # Count errors by type
        error_types = {}
        for file, error in report["errors"].items():
            if "node_modules" in file:
                continue
            error_type = error.split(":")[0]
            error_types[error_type] = error_types.get(error_type, 0) + 1

        print("\nError types (excluding node_modules):")
        for error_type, count in sorted(
            error_types.items(), key=lambda x: x[1], reverse=True
        ):
            print(f"  {error_type}: {count}")

        # Check for AGNO files
        print("\nAGNO files status:")
        agno_files = [
            "backend/mcp/agno_bridge.py",
            "backend/mcp/agno_mcp_server.py",
            "backend/integrations/enhanced_agno_integration.py",
        ]

        for agno_file in agno_files:
            if agno_file in report["errors"]:
                print(f"  ❌ {agno_file} - HAS ERRORS")
            elif Path(agno_file).exists():
                print(f"  ✅ {agno_file} - EXISTS (no errors)")
            else:
                print(f"  ✓ {agno_file} - NOT FOUND (good, already removed)")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    check_status()
