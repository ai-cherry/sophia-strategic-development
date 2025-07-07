#!/usr/bin/env python3
"""Test secret access through the unified pipeline"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.auto_esc_config import get_config_value

# Test critical secrets
test_secrets = [
    "openai_api_key",
    "anthropic_api_key",
    "snowflake_password",
    "lambda_labs_api_key",
    "vercel_api_token",
    "github_token",
]

print("🧪 Testing Secret Access\n")

passed = 0
failed = 0

for secret in test_secrets:
    value = get_config_value(secret)
    if value and value != secret and "PLACEHOLDER" not in str(value):
        print(f"✅ {secret}: {'*' * 10}")
        passed += 1
    else:
        print(f"❌ {secret}: NOT FOUND")
        failed += 1

print(f"\n📊 Results: {passed} passed, {failed} failed")

if failed > 0:
    print("\n⚠️  Some secrets are missing. Run the sync workflow:")
    print("   gh workflow run sync_secrets.yml")
    sys.exit(1)
else:
    print("\n✅ All secrets accessible!")
