#!/usr/bin/env python3
"""
Audit Logging Test Script

This script tests the audit logging system to verify that it's working correctly.
It simulates various events and checks that they are properly logged.

Usage:
    python test_audit_logging.py
"""

import asyncio
import logging
import os
import sys
import time

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import audit logger
from backend.security.audit_logger import (
    AuditEventType,
    AuditLogger,
    AuditLogLevel,
    audit_decorator,
    critical,
    debug,
    error,
    info,
    set_request_context,
    warning,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("audit_test")


@audit_decorator(
    event_type=AuditEventType.CUSTOM,
    level=AuditLogLevel.INFO,
    include_args=True,
    include_result=True,
    message_template="Test function {func_name} executed",
)
def test_function(a, b, c=None):
    """Test function for audit decorator"""
    logger.info(f"Test function called with {a}, {b}, {c}")
    return {"result": a + b}


@audit_decorator(
    event_type=AuditEventType.CUSTOM,
    level=AuditLogLevel.INFO,
)
async def test_async_function(a, b):
    """Test async function for audit decorator"""
    logger.info(f"Test async function called with {a}, {b}")
    await asyncio.sleep(0.1)
    return {"result": a * b}


def test_basic_logging():
    """Test basic logging functionality"""
    logger.info("Testing basic logging...")

    # Set request context
    set_request_context(
        user_id="test_user",
        session_id="test_session",
        request_id="test_request",
        ip_address="127.0.0.1",
        user_agent="Test Agent",
    )

    # Log events at different levels
    debug(AuditEventType.CUSTOM, "Debug test message", {"test": "debug"})
    info(AuditEventType.CUSTOM, "Info test message", {"test": "info"})
    warning(AuditEventType.CUSTOM, "Warning test message", {"test": "warning"})
    error(AuditEventType.CUSTOM, "Error test message", {"test": "error"})
    critical(AuditEventType.CUSTOM, "Critical test message", {"test": "critical"})

    logger.info("✅ Basic logging test completed")


def test_sensitive_data_redaction():
    """Test sensitive data redaction"""
    logger.info("Testing sensitive data redaction...")

    # Log events with sensitive data
    info(
        AuditEventType.CUSTOM,
        "Message with sensitive data",
        {
            "api_key": "sk-1234567890abcdef",
            "password": "supersecret",
            "credit_card": "4111-1111-1111-1111",
            "ssn": "123-45-6789",
            "email": "test@example.com",
            "safe_data": "This is safe",
        },
    )

    logger.info("✅ Sensitive data redaction test completed")


def test_audit_decorator():
    """Test audit decorator"""
    logger.info("Testing audit decorator...")

    # Call decorated function
    result = test_function(1, 2, c="test")
    logger.info(f"Function returned: {result}")

    logger.info("✅ Audit decorator test completed")


async def test_async_audit_decorator():
    """Test async audit decorator"""
    logger.info("Testing async audit decorator...")

    # Call decorated async function
    result = await test_async_function(3, 4)
    logger.info(f"Async function returned: {result}")

    logger.info("✅ Async audit decorator test completed")


def test_error_logging():
    """Test error logging"""
    logger.info("Testing error logging...")

    try:
        # Raise an exception
        raise ValueError("Test error")
    except Exception as e:
        error(
            AuditEventType.ERROR,
            f"Test error occurred: {str(e)}",
            {"error_type": "ValueError"},
        )

    logger.info("✅ Error logging test completed")


def test_custom_audit_logger():
    """Test custom audit logger instance"""
    logger.info("Testing custom audit logger...")

    # Create custom audit logger
    custom_logger = AuditLogger(
        app_name="test_app",
        log_level=AuditLogLevel.DEBUG,
        enable_console=True,
        enable_file=True,
        file_path="./logs/test_audit.log",
        enable_sentry=False,
        redact_sensitive_data=True,
    )

    # Log events with custom logger
    custom_logger.info(
        AuditEventType.CUSTOM,
        "Custom logger test message",
        {"test": "custom"},
    )

    logger.info("✅ Custom audit logger test completed")


def test_performance():
    """Test logging performance"""
    logger.info("Testing logging performance...")

    # Log multiple events and measure time
    count = 1000
    start_time = time.time()

    for i in range(count):
        info(
            AuditEventType.CUSTOM,
            f"Performance test message {i}",
            {"iteration": i},
        )

    duration = time.time() - start_time
    logger.info(f"Logged {count} events in {duration:.4f} seconds ({count/duration:.2f} events/sec)")

    logger.info("✅ Performance test completed")


async def main():
    """Main test function"""
    logger.info("Starting audit logging tests...")

    try:
        # Run tests
        test_basic_logging()
        test_sensitive_data_redaction()
        test_audit_decorator()
        await test_async_audit_decorator()
        test_error_logging()
        test_custom_audit_logger()
        test_performance()

        logger.info("✅ All tests completed successfully!")

    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)

    # Run tests
    asyncio.run(main())

