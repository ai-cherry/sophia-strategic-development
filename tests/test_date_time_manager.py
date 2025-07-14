"""
Unit tests for DateTimeManager
"""

import unittest
from datetime import datetime

from backend.core.date_time_manager import DateTimeManager, date_manager


class TestDateTimeManager(unittest.TestCase):
    """Test cases for DateTimeManager"""

    def test_now_returns_frozen_date(self):
        """Test that now() always returns the frozen date"""
        expected_date = datetime(2025, 7, 9)
        result = DateTimeManager.now()
        self.assertEqual(result, expected_date)

    def test_today_returns_frozen_date(self):
        """Test that today() returns the frozen date"""
        expected_date = datetime(2025, 7, 9).date()
        result = DateTimeManager.today()
        self.assertEqual(result, expected_date)

    def test_get_current_date_str_default_format(self):
        """Test get_current_date_str with default format"""
        expected = "2025-07-09"
        result = DateTimeManager.get_current_date_str()
        self.assertEqual(result, expected)

    def test_get_current_date_str_custom_format(self):
        """Test get_current_date_str with custom format"""
        expected = "July 9, 2025"
        result = DateTimeManager.get_current_date_str(fmt="%B %d, %Y")
        self.assertEqual(result, expected)

    def test_get_current_datetime(self):
        """Test that get_current_datetime returns the same as now()"""
        result1 = DateTimeManager.get_current_datetime()
        result2 = DateTimeManager.now()
        self.assertEqual(result1, result2)

    def test_get_current_timestamp(self):
        """Test get_current_timestamp returns correct timestamp"""
        expected = datetime(2025, 7, 9).timestamp()
        result = DateTimeManager.get_current_timestamp()
        self.assertEqual(result, expected)

    def test_get_current_isoformat(self):
        """Test get_current_isoformat returns ISO format with Z suffix"""
        expected = "2025-07-09T00:00:00Z"
        result = DateTimeManager.get_current_isoformat()
        self.assertEqual(result, expected)

    def test_inject_date_context(self):
        """Test inject_date_context adds date context to query"""
        query = "What is the weather?"
        expected = (
            "Current date: July 09, 2025. Today is July 09, 2025. What is the weather?"
        )
        result = DateTimeManager.inject_date_context(query)
        self.assertEqual(result, expected)

    def test_validate_system_date(self):
        """Test validate_system_date returns correct validation dict"""
        result = DateTimeManager.validate_system_date()
        self.assertIsInstance(result, dict)
        self.assertEqual(result["current_date"], "2025-07-09")
        self.assertEqual(result["timestamp"], "2025-07-09T00:00:00Z")
        self.assertTrue(result["validated"])
        self.assertTrue(result["system_aware"])

    def test_singleton_instance(self):
        """Test that date_manager singleton works correctly"""
        self.assertEqual(date_manager.now(), DateTimeManager.now())
        self.assertEqual(date_manager.today(), DateTimeManager.today())

    def test_consistency_across_methods(self):
        """Test that all methods return consistent date/time"""
        now = DateTimeManager.now()
        today = DateTimeManager.today()

        # Check that date components match
        self.assertEqual(now.date(), today)
        self.assertEqual(now.year, 2025)
        self.assertEqual(now.month, 7)
        self.assertEqual(now.day, 9)

    def test_no_time_component_in_frozen_date(self):
        """Test that the frozen date has no time component (midnight)"""
        now = DateTimeManager.now()
        self.assertEqual(now.hour, 0)
        self.assertEqual(now.minute, 0)
        self.assertEqual(now.second, 0)
        self.assertEqual(now.microsecond, 0)

    def test_immutability(self):
        """Test that the frozen date cannot be modified"""
        # Get the date twice and ensure they're the same object
        date1 = DateTimeManager.now()
        date2 = DateTimeManager.now()
        self.assertEqual(date1, date2)

        # Ensure modifying a returned date doesn't affect the manager
        date_copy = DateTimeManager.now()
        # datetime objects are immutable, so this test just confirms behavior
        self.assertEqual(DateTimeManager.now(), datetime(2025, 7, 9))


if __name__ == "__main__":
    unittest.main()
