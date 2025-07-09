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

        for _name, value in tests:
            if value and len(str(value)) > 5:
                passed += 1
            else:
                pass

        # Test service configurations

        service_tests = [
            ("AI Services", ai_config.validate()),
            ("Data Services", data_config.validate()),
            ("Business Services", business_config.validate()),
        ]

        service_passed = 0
        for _name, valid in service_tests:
            if valid:
                service_passed += 1
            else:
                pass

        return passed == total and service_passed == len(service_tests)

    if __name__ == "__main__":
        success = test_secret_access()
        sys.exit(0 if success else 1)

except ImportError:
    sys.exit(1)
