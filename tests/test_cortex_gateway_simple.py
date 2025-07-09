"""
Simple test to validate CortexGateway singleton pattern and basic structure
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.infra.cortex_gateway import get_gateway


def test_singleton_pattern():
    """Test that CortexGateway follows singleton pattern"""
    gateway1 = get_gateway()
    gateway2 = get_gateway()
    assert gateway1 is gateway2
    print("✅ Singleton pattern working correctly")


def test_gateway_attributes():
    """Test that gateway has expected attributes"""
    gateway = get_gateway()

    # Check attributes exist
    assert hasattr(gateway, "_initialized")
    assert hasattr(gateway, "_daily_credit_limit")
    assert hasattr(gateway, "_credits_used_today")
    assert hasattr(gateway, "initialize")
    assert hasattr(gateway, "execute_sql")
    assert hasattr(gateway, "complete")
    assert hasattr(gateway, "embed")
    assert hasattr(gateway, "sentiment")
    assert hasattr(gateway, "health_check")

    # Check initial values
    assert gateway._daily_credit_limit == 100
    assert gateway._credits_used_today == 0

    print("✅ Gateway has all expected attributes")


def test_gateway_methods():
    """Test that gateway has all required methods"""
    gateway = get_gateway()

    methods = [
        "initialize",
        "execute_sql",
        "complete",
        "embed",
        "batch_embed",
        "sentiment",
        "search",
        "health_check",
        "close",
    ]

    for method in methods:
        assert hasattr(gateway, method)
        assert callable(getattr(gateway, method))

    print("✅ Gateway has all required methods")


if __name__ == "__main__":
    print("Testing CortexGateway...")
    test_singleton_pattern()
    test_gateway_attributes()
    test_gateway_methods()
    print("\n✅ All tests passed!")
