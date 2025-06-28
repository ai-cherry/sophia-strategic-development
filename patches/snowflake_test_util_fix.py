"""
Snowflake test_util module fix for Sophia AI
Provides missing test_util module to prevent import errors
"""

# Mock test_util constants that are imported by snowflake.connector.telemetry
ENABLE_TELEMETRY_LOG = False


# Mock logger for test_util
class MockLogger:
    def debug(self, *args, **kwargs):
        pass

    def info(self, *args, **kwargs):
        pass

    def warning(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass


rt_plain_logger = MockLogger()
