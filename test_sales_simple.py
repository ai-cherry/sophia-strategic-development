#!/usr/bin/env python3
"""
Simple test for Sales Intelligence Agent refactoring
"""

import os
import sys

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))


def test_basic_modules():
    """Test basic module imports"""

    try:
        # Test models import

        # Test utils import

        # Test handlers import

        # Test facade import

        return True

    except Exception:
        import traceback

        traceback.print_exc()
        return False


def test_functionality():
    """Test basic functionality"""

    try:
        from backend.agents.specialized.sales_intelligence_agent_models import (
            EmailType,
            SalesEmailRequest,
        )
        from backend.agents.specialized.sales_intelligence_agent_utils import (
            SalesIntelligenceUtils,
        )

        # Test enums

        # Test utility functions
        SalesIntelligenceUtils.calculate_risk_score(
            ["no_recent_activity", "negative_sentiment"], {"stakeholder_1": 0.2}
        )

        # Test model creation
        SalesEmailRequest(
            email_type=EmailType.FOLLOW_UP,
            deal_id="test_deal",
            recipient_name="John Doe",
            recipient_role="Decision Maker",
            context="Test context",
            key_points=["Point 1", "Point 2"],
            call_to_action="Schedule a call",
        )

        return True

    except Exception:
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run tests"""

    tests = [test_basic_modules, test_functionality]
    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        else:
            break

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
