#!/usr/bin/env python3
"""Deployment Health Gate
Runs in CI to validate that critical environment and service health checks pass.
Fails (exit 1) if any required check fails.
"""
import os
import sys
import json
import requests
from pathlib import Path

REQUIRED_SECRETS = [
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "PINECONE_API_KEY",
]

REPORT = {
    "missing_secrets": [],
    "health_checks": [],
}

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def check_secrets():
    for secret in REQUIRED_SECRETS:
        if not os.getenv(secret):
            REPORT["missing_secrets"].append(secret)


def check_backend_health():
    url = f"{BACKEND_URL}/health"
    try:
        r = requests.get(url, timeout=5)
        REPORT["health_checks"].append({"url": url, "status": r.status_code})
        return r.ok
    except Exception as e:
        REPORT["health_checks"].append({"url": url, "error": str(e)})
        return False


def main():
    check_secrets()
    backend_ok = check_backend_health()

    # Save report for artifact debugging
    out = Path("health_gate_report.json")
    out.write_text(json.dumps(REPORT, indent=2))

    if REPORT["missing_secrets"]:
        print("❌ Missing secrets:", REPORT["missing_secrets"])
    if not backend_ok:
        print("❌ Backend health check failed")

    if REPORT["missing_secrets"] or not backend_ok:
        print("Health gate failed")
        sys.exit(1)

    print("✅ Health gate passed")


if __name__ == "__main__":
    main() 