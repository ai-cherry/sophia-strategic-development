"""
Standardized logging configuration for Sophia AI platform.
Provides structured logging with context and metrics.
"""

import json
import logging
import sys

# Try to import structlog, fallback to standard logging if not available
try:
    import structlog

    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False
    structlog = None  # Define as None when not available


class SophiaAILogger:
    """Enhanced logger for Sophia AI with structured logging."""

    def __init__(self, name: str, level: int = logging.INFO):
        self.name = name
        self.level = level

        if STRUCTLOG_AVAILABLE and structlog is not None:
            self._setup_structlog()
            self.logger = structlog.get_logger(name)
        else:
            # Fallback to standard logging
            self.logger = logging.getLogger(name)
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(level)

    def _setup_structlog(self):
        """Configure structured logging."""
        if not STRUCTLOG_AVAILABLE or structlog is None:
            return

        processors = [
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ]

        # Add CallsiteParameterAdder if available (newer versions)
        if hasattr(structlog.processors, "CallsiteParameterAdder"):
            processors.insert(-1, structlog.processors.CallsiteParameterAdder())

        structlog.configure(
            processors=processors,
            wrapper_class=structlog.stdlib.BoundLogger,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

    def _format_message(self, message: str, **kwargs) -> str:
        """Format message with context for standard logging."""
        if kwargs:
            context = json.dumps(kwargs, default=str)
            return f"{message} | Context: {context}"
        return message

    def info(self, message: str, **kwargs):
        """Log info message with context."""
        if STRUCTLOG_AVAILABLE and hasattr(self.logger, "info"):
            self.logger.info(message, **kwargs)
        else:
            self.logger.info(self._format_message(message, **kwargs))

    def error(self, message: str, **kwargs):
        """Log error message with context."""
        if STRUCTLOG_AVAILABLE and hasattr(self.logger, "error"):
            self.logger.error(message, **kwargs)
        else:
            self.logger.error(self._format_message(message, **kwargs))

    def warning(self, message: str, **kwargs):
        """Log warning message with context."""
        if STRUCTLOG_AVAILABLE and hasattr(self.logger, "warning"):
            self.logger.warning(message, **kwargs)
        else:
            self.logger.warning(self._format_message(message, **kwargs))

    def debug(self, message: str, **kwargs):
        """Log debug message with context."""
        if STRUCTLOG_AVAILABLE and hasattr(self.logger, "debug"):
            self.logger.debug(message, **kwargs)
        else:
            self.logger.debug(self._format_message(message, **kwargs))

    def exception(self, message: str, **kwargs):
        """Log exception with traceback."""
        if STRUCTLOG_AVAILABLE and hasattr(self.logger, "exception"):
            self.logger.exception(message, **kwargs)
        else:
            self.logger.exception(self._format_message(message, **kwargs))


def setup_logger(name: str, level: int = logging.INFO) -> SophiaAILogger:
    """Setup standardized logger for Sophia AI."""
    return SophiaAILogger(name, level)


# Default logger instance
logger = setup_logger("sophia_ai")
