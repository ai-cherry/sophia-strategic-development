#!/usr/bin/env python3
"""Deployment Health Gate
Runs in CI to validate that critical environment and service health checks pass.
Fails (exit 1) if any required check fails.
"""
import json
import os
import sys
from pathlib import Path

import requests

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

try:
    from backend.core.auto_esc_config import get_config_value
    ESC_AVAILABLE = True
except ImportError:
    print("⚠️ Pulumi ESC integration not available, falling back to environment variables")
    ESC_AVAILABLE = False

    # Create a dummy function to avoid linter errors
    def get_config_value(key: str, default=None) -> str:
        return default or ""

REQUIRED_SECRETS = [
    "openai_api_key",
    "anthropic_api_key",
    "pinecone_api_key",
    "gong_access_key",
    "snowflake_password"
]

CRITICAL_SERVICES = [
    "snowflake",
    "openai",
    "anthropic",
    "pinecone"
]

REPORT = {
    "missing_secrets": [],
    "failed_services": [],
    "health_checks": [],
    "esc_status": "unknown"
}

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def check_secrets():
    """Check if critical secrets are available via Pulumi ESC or environment variables"""
    if ESC_AVAILABLE:
        try:
            # Test ESC connectivity
            get_config_value("openai_api_key")
            REPORT["esc_status"] = "connected"

            for secret in REQUIRED_SECRETS:
                try:
                    value = get_config_value(secret)
                    if not value or value.startswith("PLACEHOLDER") or value == "[secret]":
                        REPORT["missing_secrets"].append(secret)
                except Exception as e:
                    REPORT["missing_secrets"].append(f"{secret} (ESC error: {str(e)})")

        except Exception as e:
            REPORT["esc_status"] = f"failed: {str(e)}"
            # Fallback to environment variables
            for secret in REQUIRED_SECRETS:
                env_var = secret.upper()
                if not os.getenv(env_var):
                    REPORT["missing_secrets"].append(f"{secret} (ESC failed, env missing)")
    else:
        REPORT["esc_status"] = "not_available"
        # Use environment variables
        for secret in REQUIRED_SECRETS:
            env_var = secret.upper()
            if not os.getenv(env_var):
                REPORT["missing_secrets"].append(secret)


def check_service_health(service_name: str) -> bool:
    """Check if a service is healthy via configuration"""
    if not ESC_AVAILABLE:
        return False

    try:
        # Check if service configuration is available
        if service_name == "snowflake":
            account = get_config_value("snowflake_account")
            password = get_config_value("snowflake_password")
            return bool(account and password and not password.startswith("PLACEHOLDER") and password != "[secret]")
        elif service_name == "openai":
            key = get_config_value("openai_api_key")
            return bool(key and not key.startswith("PLACEHOLDER") and key != "[secret]")
        elif service_name == "anthropic":
            key = get_config_value("anthropic_api_key")
            return bool(key and not key.startswith("PLACEHOLDER") and key != "[secret]")
        elif service_name == "pinecone":
            key = get_config_value("pinecone_api_key")
            return bool(key and not key.startswith("PLACEHOLDER") and key != "[secret]")
        else:
            return False
    except Exception as e:
        REPORT["failed_services"].append(f"{service_name}: {str(e)}")
        return False


def check_backend_health():
    """Check if backend service is responsive"""
    url = f"{BACKEND_URL}/health"
    try:
        r = requests.get(url, timeout=10)
        REPORT["health_checks"].append({
            "service": "backend",
            "url": url,
            "status": r.status_code,
            "response_time_ms": r.elapsed.total_seconds() * 1000
        })
        return r.ok
    except Exception as e:
        REPORT["health_checks"].append({
            "service": "backend",
            "url": url,
            "error": str(e)
        })
        return False


def check_mcp_servers():
    """Check if critical MCP servers are accessible"""
    critical_mcp_servers = [
        ("ai_memory", 9000),
        ("snowflake_admin", 9011),
        ("ui_ux_agent", 9002)
    ]

    mcp_results = []
    for name, port in critical_mcp_servers:
        url = f"http://localhost:{port}/health"
        try:
            r = requests.get(url, timeout=5)
            mcp_results.append({
                "server": name,
                "port": port,
                "status": r.status_code,
                "healthy": r.ok
            })
        except Exception as e:
            mcp_results.append({
                "server": name,
                "port": port,
                "error": str(e),
                "healthy": False
            })

    REPORT["mcp_servers"] = mcp_results
    return all(result.get("healthy", False) for result in mcp_results)


def main():
    """Main health gate validation"""
    print("🏥 Running Deployment Health Gate...")

    # Check secrets
    check_secrets()

    # Check service configurations
    service_checks = []
    for service in CRITICAL_SERVICES:
        healthy = check_service_health(service)
        service_checks.append(healthy)
        if not healthy:
            REPORT["failed_services"].append(service)

    # Check backend health
    backend_ok = check_backend_health()

    # Check MCP servers (non-blocking for CI)
    mcp_ok = check_mcp_servers()

    # Save comprehensive report
    out = Path("health_gate_report.json")
    out.write_text(json.dumps(REPORT, indent=2))

    # Print results
    print(f"📊 ESC Status: {REPORT['esc_status']}")

    if REPORT["missing_secrets"]:
        print(f"❌ Missing secrets ({len(REPORT['missing_secrets'])}): {REPORT['missing_secrets']}")
    else:
        print("✅ All required secrets available")

    if REPORT["failed_services"]:
        print(f"❌ Failed services ({len(REPORT['failed_services'])}): {REPORT['failed_services']}")
    else:
        print("✅ All critical services configured")

    if not backend_ok:
        print("⚠️ Backend health check failed (may be expected in CI)")
    else:
        print("✅ Backend health check passed")

    if not mcp_ok:
        print("⚠️ Some MCP servers not accessible (may be expected in CI)")
    else:
        print("✅ All critical MCP servers accessible")

    # Determine overall status
    critical_failures = REPORT["missing_secrets"] or REPORT["failed_services"]

    if critical_failures:
        print("❌ Health gate failed - critical issues found")
        sys.exit(1)
    else:
        print("✅ Health gate passed - ready for deployment")


if __name__ == "__main__":
    main()
