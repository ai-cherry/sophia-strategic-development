#!/usr/bin/env python3
"""
Unit tests for Snowflake Connection Pool Health Check Worker
Tests the interruptible health check worker implementation
"""

import time
from unittest.mock import Mock, patch

import pytest

from backend.services.snowflake.connection_pool_manager import (
    PoolConfig,
    SnowflakeConnectionPool,
)


class TestHealthCheckWorkerInterruptibility:
    """Test suite for health check worker shutdown behavior"""

    def test_health_check_worker_shutdown_event(self):
        """Test that health check worker responds to shutdown event"""
        # Create pool with short health check interval for testing
        config = PoolConfig(health_check_interval=1)

        with patch(
            "backend.services.snowflake.connection_pool_manager.secure_snowflake_config"
        ) as mock_config:
            mock_config.get_connection_params.return_value = {
                "account": "test",
                "user": "test",
                "password": "test",
                "database": "test",
                "schema": "test",
                "warehouse": "test",
            }

            with patch("snowflake.connector.connect") as mock_connect:
                mock_conn = Mock()
                mock_cursor = Mock()
                mock_conn.cursor.return_value = mock_cursor
                mock_connect.return_value = mock_conn

                # Create pool (this starts the health check worker)
                pool = SnowflakeConnectionPool(config)

                # Verify worker thread is running
                assert pool._health_check_thread.is_alive()

                # Trigger shutdown
                start_time = time.time()
                pool.shutdown()

                # Verify worker thread stops within reasonable time (should be < 1 second)
                pool._health_check_thread.join(timeout=2)
                shutdown_time = time.time() - start_time

                # Assert thread stopped quickly (not waiting for full health check interval)
                assert not pool._health_check_thread.is_alive()
                assert (
                    shutdown_time < 2.0
                )  # Should be much faster than health_check_interval

                # Verify shutdown event was set
                assert pool._shutdown_event.is_set()


if __name__ == "__main__":
    pytest.main([__file__])
