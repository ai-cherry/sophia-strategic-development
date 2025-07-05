#!/usr/bin/env python3
"""
Test only the decomposed modules without configuration dependencies
"""

import os
import sys

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))


def test_individual_modules():
    """Test individual modules without dependencies"""

    try:
        # Test models import
        from backend.agents.specialized.sales_intelligence_agent_models import (
            EmailType,
            SalesEmailRequest,
            SalesStage,
        )

        # Test utils import
        from backend.agents.specialized.sales_intelligence_agent_utils import (
            SalesIntelligenceUtils,
        )

        # Test basic functionality

        # Test utility functions
        risk_score = SalesIntelligenceUtils.calculate_risk_score(
            ["no_recent_activity", "negative_sentiment"],
            {"stakeholder_1": 0.2, "stakeholder_2": 0.4},
        )

        SalesIntelligenceUtils.determine_risk_level(risk_score)

        SalesIntelligenceUtils.format_currency(125000)

        SalesIntelligenceUtils.get_stage_probability(SalesStage.PROPOSAL)

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
    """Run test"""

    if test_individual_modules():
        # Show decomposition metrics

        return True
    else:
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
