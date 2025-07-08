#!/usr/bin/env python3
"""
Test script for validating secret access after remediation
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from backend.core.auto_esc_config import get_config_value
    from backend.core.service_configs import ai_config, business_config, data_config

    def test_secret_access():
        """Test secret access through centralized configuration"""
        print("🔍 Testing secret access...")

        # Test individual secrets
        tests = [
            ("OpenAI API Key", get_config_value("openai_api_key")),
            ("Anthropic API Key", get_config_value("anthropic_api_key")),
            ("Snowflake Account", get_config_value("snowflake_account")),
            ("Gong Access Key", get_config_value("gong_access_key")),
            ("HubSpot Token", get_config_value("hubspot_access_token")),
        ]

        passed = 0
        total = len(tests)

        for name, value in tests:
            if value and len(str(value)) > 5:
                print(f"✅ {name}: Available")
                passed += 1
            else:
                print(f"❌ {name}: Missing or invalid")

        print(f"\n📊 Results: {passed}/{total} secrets accessible")

        # Test service configurations
        print("\n🔍 Testing service configurations...")

        service_tests = [
            ("AI Services", ai_config.validate()),
            ("Data Services", data_config.validate()),
            ("Business Services", business_config.validate()),
        ]

        service_passed = 0
        for name, valid in service_tests:
            if valid:
                print(f"✅ {name}: Valid configuration")
                service_passed += 1
            else:
                print(f"❌ {name}: Invalid configuration")

        print(
            f"\n📊 Service Results: {service_passed}/{len(service_tests)} configurations valid"
        )

        return passed == total and service_passed == len(service_tests)

    if __name__ == "__main__":
        success = test_secret_access()
        sys.exit(0 if success else 1)

except ImportError as e:
    print(f"❌ Import error: {e}")
    print(
        "Make sure backend directory structure is created and auto_esc_config is available"
    )
    sys.exit(1)
