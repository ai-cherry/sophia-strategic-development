#!/usr/bin/env python3
"""Simple check for Lambda Labs connectivity."""
import os
import requests

def main() -> None:
    api_key = os.getenv("LAMBDA_LABS_API_KEY")
    if not api_key:
        print("⚠️  LAMBDA_LABS_API_KEY not set; skipping connectivity test")
        return
    try:
        resp = requests.get("https://cloud.lambdalabs.com/api/v1/status", timeout=5)
        if resp.status_code == 200:
            print("✅ Lambda Labs API reachable")
        else:
            print(f"❌ Lambda Labs API returned {resp.status_code}")
    except Exception as exc:
        print(f"❌ Lambda Labs API check failed: {exc}")

if __name__ == "__main__":
    main()
