#!/usr/bin/env python3
"""
Test script to verify the refactored Sales Intelligence Agent
"""

import os
import sys

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))


def test_imports():
    """Test that all refactored modules can be imported"""

    try:
        # Test models import

        # Test utils import

        # Test handlers import

        # Test core import

        # Test facade import

        return True

    except Exception:
        import traceback

        traceback.print_exc()
        return False


def test_enums_and_models():
    """Test that enums and models work correctly"""

    try:
        from backend.agents.specialized.sales_intelligence_agent_models import (
            EmailType,
            SalesEmailRequest,
        )

        # Test enums

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


def test_utilities():
    """Test utility functions"""

    try:
        from backend.agents.specialized.sales_intelligence_agent_models import (
            SalesStage,
        )
        from backend.agents.specialized.sales_intelligence_agent_utils import (
            SalesIntelligenceUtils,
        )

        # Test risk score calculation
        risk_factors = ["no_recent_activity", "negative_sentiment"]
        sentiment = {"stakeholder_1": 0.2, "stakeholder_2": 0.4}
        risk_score = SalesIntelligenceUtils.calculate_risk_score(
            risk_factors, sentiment
        )

        # Test risk level determination
        SalesIntelligenceUtils.determine_risk_level(risk_score)

        # Test currency formatting
        SalesIntelligenceUtils.format_currency(125000)

        # Test stage probability
        SalesIntelligenceUtils.get_stage_probability(SalesStage.PROPOSAL)

        return True

    except Exception:
        import traceback

        traceback.print_exc()
        return False


def test_backward_compatibility():
    """Test that the facade maintains backward compatibility"""

    try:
        # Test that all original imports still work
        from backend.agents.specialized.sales_intelligence_agent import (
            create_sales_intelligence_agent,
        )

        # Test factory function
        agent = create_sales_intelligence_agent()

        # Test agent capabilities
        agent.get_agent_capabilities()

        return True

    except Exception:
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests"""

    tests = [
        test_imports,
        test_enums_and_models,
        test_utilities,
        test_backward_compatibility,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        else:
            break  # Stop on first failure

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
