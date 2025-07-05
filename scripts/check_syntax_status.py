#!/usr/bin/env python3
"""
Quick script to check the current syntax validation status
"""

import json
from pathlib import Path


def check_status():
    """Check current syntax status from validation report"""
    try:
        with open("syntax_validation_report.json") as f:
            report = json.load(f)

        # Count errors by type
        error_types = {}
        for file, error in report["errors"].items():
            if "node_modules" in file:
                continue
            error_type = error.split(":")[0]
            error_types[error_type] = error_types.get(error_type, 0) + 1

        for error_type, _count in sorted(
            error_types.items(), key=lambda x: x[1], reverse=True
        ):
            pass

        # Check for AGNO files
        agno_files = [
            "backend/mcp/agno_bridge.py",
            "backend/mcp/agno_mcp_server.py",
            "backend/integrations/enhanced_agno_integration.py",
        ]

        for agno_file in agno_files:
            if agno_file in report["errors"] or Path(agno_file).exists():
                pass
            else:
                pass

    except Exception:
        pass


if __name__ == "__main__":
    check_status()
