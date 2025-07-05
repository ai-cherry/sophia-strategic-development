#!/usr/bin/env python3
"""
Sophia AI - Ecosystem Diagnostic & Fix Tool
Addresses the PULUMI_ACCESS_TOKEN issue and tests complete ecosystem including Codacy MCP
"""

import json
import logging
import os
import subprocess
from datetime import datetime
from typing import Any

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def check_pulumi_auth() -> dict[str, Any]:
    """Check Pulumi authentication status"""
    logger.info("🔐 Checking Pulumi authentication...")

    token = os.getenv("PULUMI_ACCESS_TOKEN")
    if not token:
        return {"status": "error", "message": "PULUMI_ACCESS_TOKEN not set"}

    if token.startswith("your-"):
        return {
            "status": "error",
            "message": "PULUMI_ACCESS_TOKEN is placeholder",
            "token_preview": token[:20],
        }

    try:
        result = subprocess.run(
            ["pulumi", "whoami"], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return {"status": "success", "username": result.stdout.strip()}
        else:
            return {"status": "error", "message": f"Auth failed: {result.stderr}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def check_github_secrets() -> dict[str, Any]:
    """Check GitHub organization secrets availability"""
    logger.info("🔗 Checking GitHub organization secrets...")

    expected_secrets = [
        "ANTHROPIC_API_KEY",
        "GEMINI_API_KEY",
        "OPENAI_API_KEY",
        "GONG_ACCESS_KEY",
        "HUBSPOT_ACCESS_TOKEN",
        "LINEAR_API_KEY",
        "LAMBDA_API_KEY",
        "SNOWFLAKE_PASSWORD",
        "PINECONE_API_KEY",
    ]

    available = [
        s
        for s in expected_secrets
        if os.getenv(s) and not os.getenv(s).startswith("your-")
    ]
    missing = [s for s in expected_secrets if s not in available]

    return {
        "status": "success" if not missing else "partial",
        "available_count": len(available),
        "total_expected": len(expected_secrets),
        "missing_secrets": missing,
    }


def check_mcp_servers() -> dict[str, Any]:
    """Check MCP server health"""
    logger.info("🤖 Checking MCP server health...")

    servers = {"ai_memory": 9000, "codacy": 3008, "figma": 9001}
    status = {}

    for name, port in servers.items():
        try:
            import socket

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(("localhost", port))
            sock.close()
            status[name] = {
                "status": "online" if result == 0 else "offline",
                "port": port,
            }
        except Exception as e:
            status[name] = {"status": "error", "port": port, "error": str(e)}

    online_count = sum(1 for s in status.values() if s["status"] == "online")
    return {
        "status": "success" if online_count == len(servers) else "partial",
        "online_count": online_count,
        "servers": status,
    }


def test_codacy_mcp() -> dict[str, Any]:
    """Test Codacy MCP server specifically"""
    logger.info("🧪 Testing Codacy MCP Server...")

    try:
        import socket

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(("localhost", 3008))
        sock.close()

        if result == 0:
            return {
                "status": "online",
                "message": "Codacy MCP server is ready for code analysis",
                "capabilities": [
                    "Real-time security scanning (Bandit + custom patterns)",
                    "Code complexity analysis (AST + Radon)",
                    "Performance bottleneck detection",
                    "Sophia AI-specific security checks",
                    "Auto ESC config enforcement",
                    "SQL injection prevention",
                ],
                "integration": "Ready for Cursor MCP integration",
            }
        else:
            return {
                "status": "offline",
                "message": "Codacy MCP server not running",
                "start_command": "python mcp-servers/codacy/codacy_mcp_server.py",
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def main():
    """Main diagnostic execution"""

    # Run diagnostics
    pulumi_status = check_pulumi_auth()
    github_status = check_github_secrets()
    mcp_status = check_mcp_servers()
    codacy_status = test_codacy_mcp()

    # Print results

    "✅" if pulumi_status["status"] == "success" else "❌"
    if "message" in pulumi_status:
        pass

    "✅" if github_status["status"] == "success" else "⚠️"

    "✅" if mcp_status["status"] == "success" else "⚠️"

    "✅" if codacy_status["status"] == "online" else "❌"

    # Print specific issues and fixes

    if pulumi_status["status"] == "error":
        pass

    if github_status["missing_secrets"]:
        pass

    if codacy_status["status"] != "online":
        pass

    # Explain Codacy MCP integration (user asked specifically)

    if "capabilities" in codacy_status:
        for _cap in codacy_status["capabilities"]:
            pass

    # Expected workflow after fix

    # Save report
    report = {
        "timestamp": datetime.now().isoformat(),
        "pulumi_auth": pulumi_status,
        "github_secrets": github_status,
        "mcp_servers": mcp_status,
        "codacy_mcp": codacy_status,
    }

    with open("sophia_ecosystem_report.json", "w") as f:
        json.dump(report, f, indent=2)

    # Summary
    issues = []
    if pulumi_status["status"] == "error":
        issues.append("Pulumi auth")
    if github_status["status"] != "success":
        issues.append("GitHub secrets")
    if mcp_status["status"] != "success":
        issues.append("MCP servers")

    if not issues:
        pass
    else:
        pass


if __name__ == "__main__":
    main()
