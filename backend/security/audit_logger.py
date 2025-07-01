"""
Audit Logger for Sophia AI Platform

Implements comprehensive audit logging for security, compliance, and operational monitoring.
Provides structured logging with sensitive data protection and configurable output formats.

Key Features:
- Structured JSON logging for machine readability
- Sensitive data redaction and PII protection
- Configurable log levels and destinations
- User and session context tracking
- Compliance with security best practices
"""

import datetime
import json
import logging
import os
import re
import sys
import threading
import uuid
from enum import Enum
from functools import wraps
from typing import Any

# Configure base logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Create audit logger
audit_logger = logging.getLogger("sophia.audit")


class AuditEventType(Enum):
    """Audit event types for categorization and filtering"""

    # Authentication events
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    LOGIN_FAILURE = "user.login_failure"
    PASSWORD_CHANGE = "user.password_change"
    MFA_CHALLENGE = "user.mfa_challenge"

    # Authorization events
    ACCESS_GRANTED = "auth.access_granted"
    ACCESS_DENIED = "auth.access_denied"
    PERMISSION_CHANGE = "auth.permission_change"
    ROLE_CHANGE = "auth.role_change"

    # Data access events
    DATA_READ = "data.read"
    DATA_WRITE = "data.write"
    DATA_DELETE = "data.delete"
    DATA_EXPORT = "data.export"

    # AI operations
    LLM_REQUEST = "ai.llm_request"
    LLM_RESPONSE = "ai.llm_response"
    TOOL_EXECUTION = "ai.tool_execution"
    AGENT_ACTION = "ai.agent_action"

    # System events
    SYSTEM_START = "system.start"
    SYSTEM_STOP = "system.stop"
    CONFIG_CHANGE = "system.config_change"
    ERROR = "system.error"

    # Admin events
    ADMIN_ACTION = "admin.action"
    USER_CREATION = "admin.user_creation"
    USER_UPDATE = "admin.user_update"
    USER_DELETION = "admin.user_deletion"

    # Custom events
    CUSTOM = "custom"


class AuditLogLevel(Enum):
    """Audit log severity levels"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class SensitiveDataType(Enum):
    """Types of sensitive data for redaction"""

    API_KEY = "API_KEY"
    PASSWORD = "PASSWORD"
    PII = "PII"
    CREDIT_CARD = "CREDIT_CARD"
    SSN = "SSN"
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    ADDRESS = "ADDRESS"
    CUSTOM = "CUSTOM"


# Thread-local storage for request context
_thread_local = threading.local()


class AuditLogger:
    """
    Comprehensive audit logger for security, compliance, and operational monitoring.

    Features:
    - Structured JSON logging
    - Sensitive data redaction
    - User and session context tracking
    - Compliance with security best practices
    """

    def __init__(
        self,
        app_name: str = "sophia",
        log_level: AuditLogLevel = AuditLogLevel.INFO,
        enable_console: bool = True,
        enable_file: bool = True,
        file_path: str | None = None,
        enable_sentry: bool = False,
        sentry_dsn: str | None = None,
        redact_sensitive_data: bool = True,
        max_event_size_bytes: int = 10240,  # 10KB max event size
    ):
        self.app_name = app_name
        self.log_level = log_level
        self.enable_console = enable_console
        self.enable_file = enable_file
        self.file_path = file_path or os.path.join(
            os.getcwd(), "logs", f"{app_name}_audit.log"
        )
        self.enable_sentry = enable_sentry
        self.sentry_dsn = sentry_dsn
        self.redact_sensitive_data = redact_sensitive_data
        self.max_event_size_bytes = max_event_size_bytes

        # Ensure log directory exists
        if self.enable_file:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

        # Configure logger
        self._configure_logger()

        # Initialize Sentry if enabled
        if self.enable_sentry and self.sentry_dsn:
            self._initialize_sentry()

    def _configure_logger(self):
        """Configure the logger with appropriate handlers"""
        # Set log level
        audit_logger.setLevel(getattr(logging, self.log_level.value))

        # Remove existing handlers
        for handler in audit_logger.handlers[:]:
            audit_logger.removeHandler(handler)

        # Add console handler if enabled
        if self.enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(logging.Formatter("%(message)s"))
            audit_logger.addHandler(console_handler)

        # Add file handler if enabled
        if self.enable_file:
            try:
                file_handler = logging.FileHandler(self.file_path)
                file_handler.setFormatter(logging.Formatter("%(message)s"))
                audit_logger.addHandler(file_handler)
            except Exception as e:
                print(f"Failed to configure file logging: {e}")

    def _initialize_sentry(self):
        """Initialize Sentry integration"""
        try:
            import sentry_sdk

            sentry_sdk.init(
                dsn=self.sentry_dsn,
                traces_sample_rate=0.1,
                profiles_sample_rate=0.1,
            )

            # Add Sentry integration
            def before_send(event, hint):
                """Process events before sending to Sentry"""
                # Don't send DEBUG or INFO level events to Sentry
                if event.get("level") in ("debug", "info"):
                    return None

                # Redact sensitive data if enabled
                if self.redact_sensitive_data:
                    event = self._redact_sentry_event(event)

                return event

            sentry_sdk.init(
                dsn=self.sentry_dsn,
                before_send=before_send,
            )

        except ImportError:
            print("Sentry SDK not installed. Sentry integration disabled.")
            self.enable_sentry = False

    def _redact_sentry_event(self, event: dict[str, Any]) -> dict[str, Any]:
        """Redact sensitive data from Sentry events"""
        # Implementation depends on Sentry event structure
        return event

    def set_request_context(
        self,
        user_id: str | None = None,
        session_id: str | None = None,
        request_id: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        additional_context: dict[str, Any] | None = None,
    ):
        """
        Set context for the current request/thread.

        This context will be included in all audit logs for the current thread.
        """
        if not hasattr(_thread_local, "context"):
            _thread_local.context = {}

        _thread_local.context.update(
            {
                "user_id": user_id,
                "session_id": session_id,
                "request_id": request_id or str(uuid.uuid4()),
                "ip_address": ip_address,
                "user_agent": user_agent,
                **(additional_context or {}),
            }
        )

    def clear_request_context(self):
        """Clear the request context for the current thread"""
        if hasattr(_thread_local, "context"):
            delattr(_thread_local, "context")

    def get_request_context(self) -> dict[str, Any]:
        """Get the current request context"""
        if not hasattr(_thread_local, "context"):
            _thread_local.context = {
                "request_id": str(uuid.uuid4()),
            }

        return _thread_local.context

    def _redact_sensitive_data(self, data: Any) -> Any:
        """
        Redact sensitive data from logs.

        Handles nested dictionaries, lists, and strings.
        """
        if not self.redact_sensitive_data:
            return data

        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                # Check if key indicates sensitive data
                if any(
                    s in key.lower()
                    for s in (
                        "password",
                        "secret",
                        "token",
                        "key",
                        "auth",
                        "credential",
                        "ssn",
                        "credit",
                        "card",
                        "cvv",
                        "social",
                        "security",
                        "private",
                    )
                ):
                    result[key] = "[REDACTED]"
                else:
                    result[key] = self._redact_sensitive_data(value)
            return result

        elif isinstance(data, list):
            return [self._redact_sensitive_data(item) for item in data]

        elif isinstance(data, str):
            # Redact common sensitive patterns
            result = data

            # API Keys and Tokens
            result = re.sub(
                r"(api[_-]?key|token)[\"\':]?\s*[:=]\s*[\"\':]?([a-zA-Z0-9_\-\.]{20,})[\"\':]?",
                r"\1=[REDACTED]",
                result,
            )

            # Credit Card Numbers
            result = re.sub(
                r"\b(?:\d{4}[- ]?){3}\d{4}\b", "[CREDIT_CARD_REDACTED]", result
            )

            # Social Security Numbers
            result = re.sub(r"\b\d{3}[-]?\d{2}[-]?\d{4}\b", "[SSN_REDACTED]", result)

            # Email addresses in specific contexts
            result = re.sub(
                r"(email|e-mail|mail)[\"\':]?\s*[:=]\s*[\"\':]?([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)[\"\':]?",
                r"\1=[EMAIL_REDACTED]",
                result,
            )

            return result

        else:
            return data

    def _prepare_log_entry(
        self,
        event_type: AuditEventType,
        message: str,
        level: AuditLogLevel,
        details: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Prepare a structured log entry"""
        # Get request context
        context = self.get_request_context()

        # Create base log entry
        log_entry = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "app": self.app_name,
            "event_type": event_type.value,
            "level": level.value,
            "message": message,
            "request_id": context.get("request_id", str(uuid.uuid4())),
            "user_id": context.get("user_id", "anonymous"),
            "session_id": context.get("session_id"),
            "ip_address": context.get("ip_address"),
            "user_agent": context.get("user_agent"),
        }

        # Add details if provided
        if details:
            # Limit details size to prevent excessive logging
            serialized = json.dumps(details)
            if len(serialized) > self.max_event_size_bytes:
                log_entry["details"] = {
                    "error": f"Details exceeded maximum size of {self.max_event_size_bytes} bytes",
                    "truncated": True,
                }
            else:
                log_entry["details"] = details

        # Redact sensitive data if enabled
        if self.redact_sensitive_data:
            log_entry = self._redact_sensitive_data(log_entry)

        return log_entry

    def log(
        self,
        event_type: AuditEventType,
        message: str,
        level: AuditLogLevel = AuditLogLevel.INFO,
        details: dict[str, Any] | None = None,
    ):
        """
        Log an audit event.

        Args:
            event_type: Type of audit event
            message: Human-readable message
            level: Severity level
            details: Additional structured details
        """
        # Prepare log entry
        log_entry = self._prepare_log_entry(event_type, message, level, details)

        # Convert to JSON
        log_json = json.dumps(log_entry)

        # Log using appropriate level
        log_method = getattr(audit_logger, level.value.lower())
        log_method(log_json)

        # Send to Sentry if enabled and level is appropriate
        if self.enable_sentry and level in (
            AuditLogLevel.ERROR,
            AuditLogLevel.CRITICAL,
        ):
            try:
                import sentry_sdk

                with sentry_sdk.push_scope() as scope:
                    # Add context to Sentry event
                    for key, value in log_entry.items():
                        if key != "message":
                            scope.set_extra(key, value)

                    # Capture message or exception
                    if "exception" in log_entry.get("details", {}):
                        sentry_sdk.capture_exception()
                    else:
                        sentry_sdk.capture_message(
                            message,
                            level=level.value.lower(),
                        )
            except ImportError:
                pass

    def debug(
        self,
        event_type: AuditEventType,
        message: str,
        details: dict[str, Any] | None = None,
    ):
        """Log a DEBUG level audit event"""
        self.log(event_type, message, AuditLogLevel.DEBUG, details)

    def info(
        self,
        event_type: AuditEventType,
        message: str,
        details: dict[str, Any] | None = None,
    ):
        """Log an INFO level audit event"""
        self.log(event_type, message, AuditLogLevel.INFO, details)

    def warning(
        self,
        event_type: AuditEventType,
        message: str,
        details: dict[str, Any] | None = None,
    ):
        """Log a WARNING level audit event"""
        self.log(event_type, message, AuditLogLevel.WARNING, details)

    def error(
        self,
        event_type: AuditEventType,
        message: str,
        details: dict[str, Any] | None = None,
        exc_info: bool = True,
    ):
        """Log an ERROR level audit event"""
        if exc_info:
            import traceback

            if details is None:
                details = {}
            details["exception"] = traceback.format_exc()

        self.log(event_type, message, AuditLogLevel.ERROR, details)

    def critical(
        self,
        event_type: AuditEventType,
        message: str,
        details: dict[str, Any] | None = None,
        exc_info: bool = True,
    ):
        """Log a CRITICAL level audit event"""
        if exc_info:
            import traceback

            if details is None:
                details = {}
            details["exception"] = traceback.format_exc()

        self.log(event_type, message, AuditLogLevel.CRITICAL, details)

    def audit_decorator(
        self,
        event_type: AuditEventType,
        level: AuditLogLevel = AuditLogLevel.INFO,
        include_args: bool = False,
        include_result: bool = False,
        message_template: str = "{func_name} called",
    ):
        """
        Decorator to audit function calls.

        Args:
            event_type: Type of audit event
            level: Severity level
            include_args: Whether to include function arguments in the audit log
            include_result: Whether to include function result in the audit log
            message_template: Template for the audit message

        Returns:
            Decorated function
        """

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Prepare details
                details = {}

                # Include arguments if requested
                if include_args:
                    # Convert args to dict for better logging
                    arg_names = func.__code__.co_varnames[: func.__code__.co_argcount]
                    details["args"] = dict(zip(arg_names, args, strict=False))
                    details["kwargs"] = kwargs

                # Format message
                message = message_template.format(
                    func_name=func.__name__,
                    module=func.__module__,
                )

                start_time = datetime.datetime.now()

                try:
                    # Call the function
                    result = func(*args, **kwargs)

                    # Calculate duration
                    duration = (datetime.datetime.now() - start_time).total_seconds()
                    details["duration_seconds"] = duration

                    # Include result if requested
                    if include_result:
                        details["result"] = result

                    # Log successful call
                    self.log(event_type, message, level, details)

                    return result

                except Exception as e:
                    # Calculate duration
                    duration = (datetime.datetime.now() - start_time).total_seconds()
                    details["duration_seconds"] = duration
                    details["exception"] = str(e)

                    # Log error
                    self.error(
                        event_type,
                        f"{message} failed: {str(e)}",
                        details,
                    )

                    # Re-raise the exception
                    raise

            return wrapper

        return decorator


# Create default audit logger instance
default_audit_logger = AuditLogger(
    app_name="sophia",
    log_level=AuditLogLevel.INFO,
    enable_console=True,
    enable_file=True,
    file_path=os.path.join(os.getcwd(), "logs", "sophia_audit.log"),
    enable_sentry=False,
    redact_sensitive_data=True,
)


# Convenience functions using the default audit logger
def set_request_context(
    user_id: str | None = None,
    session_id: str | None = None,
    request_id: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    additional_context: dict[str, Any] | None = None,
):
    """Set context for the current request/thread"""
    default_audit_logger.set_request_context(
        user_id, session_id, request_id, ip_address, user_agent, additional_context
    )


def clear_request_context():
    """Clear the request context for the current thread"""
    default_audit_logger.clear_request_context()


def get_request_context() -> dict[str, Any]:
    """Get the current request context"""
    return default_audit_logger.get_request_context()


def log(
    event_type: AuditEventType,
    message: str,
    level: AuditLogLevel = AuditLogLevel.INFO,
    details: dict[str, Any] | None = None,
):
    """Log an audit event"""
    default_audit_logger.log(event_type, message, level, details)


def debug(
    event_type: AuditEventType,
    message: str,
    details: dict[str, Any] | None = None,
):
    """Log a DEBUG level audit event"""
    default_audit_logger.debug(event_type, message, details)


def info(
    event_type: AuditEventType,
    message: str,
    details: dict[str, Any] | None = None,
):
    """Log an INFO level audit event"""
    default_audit_logger.info(event_type, message, details)


def warning(
    event_type: AuditEventType,
    message: str,
    details: dict[str, Any] | None = None,
):
    """Log a WARNING level audit event"""
    default_audit_logger.warning(event_type, message, details)


def error(
    event_type: AuditEventType,
    message: str,
    details: dict[str, Any] | None = None,
    exc_info: bool = True,
):
    """Log an ERROR level audit event"""
    default_audit_logger.error(event_type, message, details, exc_info)


def critical(
    event_type: AuditEventType,
    message: str,
    details: dict[str, Any] | None = None,
    exc_info: bool = True,
):
    """Log a CRITICAL level audit event"""
    default_audit_logger.critical(event_type, message, details, exc_info)


def audit_decorator(
    event_type: AuditEventType,
    level: AuditLogLevel = AuditLogLevel.INFO,
    include_args: bool = False,
    include_result: bool = False,
    message_template: str = "{func_name} called",
):
    """Decorator to audit function calls"""
    return default_audit_logger.audit_decorator(
        event_type, level, include_args, include_result, message_template
    )


# Configure default audit logger based on environment variables
def configure_from_env():
    """Configure the default audit logger from environment variables"""
    # Get configuration from environment variables
    app_name = os.environ.get("SOPHIA_AUDIT_APP_NAME", "sophia")
    log_level = os.environ.get("SOPHIA_AUDIT_LOG_LEVEL", "INFO")
    enable_console = (
        os.environ.get("SOPHIA_AUDIT_ENABLE_CONSOLE", "true").lower() == "true"
    )
    enable_file = os.environ.get("SOPHIA_AUDIT_ENABLE_FILE", "true").lower() == "true"
    file_path = os.environ.get("SOPHIA_AUDIT_FILE_PATH")
    enable_sentry = (
        os.environ.get("SOPHIA_AUDIT_ENABLE_SENTRY", "false").lower() == "true"
    )
    sentry_dsn = os.environ.get("SOPHIA_AUDIT_SENTRY_DSN")
    redact_sensitive_data = (
        os.environ.get("SOPHIA_AUDIT_REDACT_SENSITIVE", "true").lower() == "true"
    )

    # Create new audit logger with environment configuration
    global default_audit_logger
    default_audit_logger = AuditLogger(
        app_name=app_name,
        log_level=AuditLogLevel[log_level],
        enable_console=enable_console,
        enable_file=enable_file,
        file_path=file_path,
        enable_sentry=enable_sentry,
        sentry_dsn=sentry_dsn,
        redact_sensitive_data=redact_sensitive_data,
    )


# Configure from environment if running as main module
if __name__ == "__main__":
    configure_from_env()
