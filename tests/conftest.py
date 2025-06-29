"""
Test configuration for Sophia AI platform.
"""

import pytest
import asyncio
from pathlib import Path

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def project_root():
    """Get project root directory."""
    return Path(__file__).parent.parent

@pytest.fixture
def test_config():
    """Test configuration."""
    return {
        'snowflake': {
            'account': 'test_account',
            'user': 'test_user',
            'password': 'test_password'
        },
        'testing': True
    }
