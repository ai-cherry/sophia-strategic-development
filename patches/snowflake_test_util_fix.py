import sys
from types import ModuleType
mock_test_util = ModuleType('snowflake.connector.test_util')
mock_test_util.ENABLE_TELEMETRY_LOG = False
mock_test_util.rt_plain_logger = None
sys.modules['snowflake.connector.test_util'] = mock_test_util
