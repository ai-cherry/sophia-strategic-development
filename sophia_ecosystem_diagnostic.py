#!/usr/bin/env python3
"""
Sophia AI - Ecosystem Diagnostic & Fix Tool
Addresses the PULUMI_ACCESS_TOKEN issue and tests complete ecosystem including Codacy MCP
"""

import os
import subprocess
import json
import logging
from datetime import datetime
from typing import Dict, Any

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def check_pulumi_auth() -> Dict[str, Any]:
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


def check_github_secrets() -> Dict[str, Any]:
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


def check_mcp_servers() -> Dict[str, Any]:
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


def test_codacy_mcp() -> Dict[str, Any]:
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
    print("🚀 Sophia AI Ecosystem Diagnostic Tool")
    print("Addressing PULUMI_ACCESS_TOKEN issue & testing complete ecosystem")
    print("=" * 70)

    # Run diagnostics
    pulumi_status = check_pulumi_auth()
    github_status = check_github_secrets()
    mcp_status = check_mcp_servers()
    codacy_status = test_codacy_mcp()

    # Print results
    print("\n📊 DIAGNOSTIC RESULTS:")
    print("-" * 30)

    status_emoji = "✅" if pulumi_status["status"] == "success" else "❌"
    print(f"{status_emoji} PULUMI AUTH: {pulumi_status['status']}")
    if "message" in pulumi_status:
        print(f"   └─ {pulumi_status['message']}")

    status_emoji = "✅" if github_status["status"] == "success" else "⚠️"
    print(
        f"{status_emoji} GITHUB SECRETS: {github_status['available_count']}/{github_status['total_expected']} available"
    )

    status_emoji = "✅" if mcp_status["status"] == "success" else "⚠️"
    print(f"{status_emoji} MCP SERVERS: {mcp_status['online_count']} online")

    status_emoji = "✅" if codacy_status["status"] == "online" else "❌"
    print(f"{status_emoji} CODACY MCP: {codacy_status['status']}")

    # Print specific issues and fixes
    print("\n🔧 KEY ISSUES & FIXES:")
    print("-" * 30)

    if pulumi_status["status"] == "error":
        print("❌ CRITICAL: PULUMI_ACCESS_TOKEN invalid")
        print("   💡 Fix: Update in GitHub Organization Secrets (ai-cherry org)")
        print("   🔄 Then run GitHub Action to sync to Pulumi ESC")

    if github_status["missing_secrets"]:
        print(f"⚠️  Missing {len(github_status['missing_secrets'])} GitHub secrets")
        print(f"   📝 Missing: {', '.join(github_status['missing_secrets'][:3])}...")

    if codacy_status["status"] != "online":
        print("❌ Codacy MCP server offline")
        print(
            f"   🚀 Start: {codacy_status.get('start_command', 'See mcp-servers/codacy/')}"
        )

    # Explain Codacy MCP integration (user asked specifically)
    print("\n🤖 CODACY MCP SERVER INTEGRATION:")
    print("-" * 40)
    print("The Codacy MCP server provides comprehensive code quality analysis:")

    if "capabilities" in codacy_status:
        for cap in codacy_status["capabilities"]:
            print(f"  • {cap}")

    print("\n🔗 Integration with Cursor IDE:")
    print("  1. Runs on port 3008 as MCP server")
    print("  2. Provides real-time code analysis tools")
    print("  3. Enforces Sophia AI-specific patterns")
    print("  4. Prevents security issues before commit")
    print("  5. Natural language commands: 'analyze code', 'check security', etc.")

    # Expected workflow after fix
    print("\n✅ EXPECTED WORKFLOW AFTER FIX:")
    print("-" * 35)
    print("GitHub Org Secrets (ai-cherry) → Pulumi ESC → Sophia AI Backend")
    print("  ↓")
    print("All MCP servers get secrets automatically")
    print("  ↓")
    print("Cursor IDE + MCP integration provides:")
    print("  • AI Memory (learning & context)")
    print("  • Codacy (code quality & security)")
    print("  • Business intelligence (Gong, HubSpot, Linear)")
    print("  • Infrastructure automation (Pulumi, Docker)")

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

    print("\n📄 Full report saved: sophia_ecosystem_report.json")

    # Summary
    issues = []
    if pulumi_status["status"] == "error":
        issues.append("Pulumi auth")
    if github_status["status"] != "success":
        issues.append("GitHub secrets")
    if mcp_status["status"] != "success":
        issues.append("MCP servers")

    if not issues:
        print("\n🎉 SUCCESS: Ecosystem is healthy!")
    else:
        print(f"\n⚠️  ACTION REQUIRED: Fix {', '.join(issues)}")
        print("💡 Most critical: Update PULUMI_ACCESS_TOKEN in GitHub Organization")


if __name__ == "__main__":
    main()
