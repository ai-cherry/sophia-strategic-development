"""
Logging utilities for Sophia AI
Provides consistent logging configuration and helper functions
"""

import logging
import sys
import os
from datetime import datetime
from typing import Optional
from pathlib import Path

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Configure logging format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> None:
    """
    Setup logging configuration for the application
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create formatters
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Default file handler for application logs
    app_log_file = logs_dir / f"sophia_ai_{datetime.now().strftime('%Y%m%d')}.log"
    app_file_handler = logging.FileHandler(app_log_file)
    app_file_handler.setLevel(numeric_level)
    app_file_handler.setFormatter(formatter)
    root_logger.addHandler(app_file_handler)
    
    # Suppress verbose third-party logs
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with consistent configuration
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Ensure the logger inherits the root configuration
    if not logger.handlers and logger.parent == logging.getLogger():
        # If no handlers and parent is root, it will inherit root configuration
        pass
    
    return logger

def log_request(logger: logging.Logger, request_id: str, method: str, path: str, 
                user_id: Optional[str] = None, ip_address: Optional[str] = None) -> None:
    """
    Log an incoming request with consistent format
    
    Args:
        logger: Logger instance
        request_id: Unique request identifier
        method: HTTP method
        path: Request path
        user_id: Optional user ID
        ip_address: Optional client IP address
    """
    logger.info(
        f"REQUEST [{request_id}] {method} {path} "
        f"user={user_id or 'anonymous'} ip={ip_address or 'unknown'}"
    )

def log_response(logger: logging.Logger, request_id: str, status_code: int, 
                 duration_ms: float, response_size: Optional[int] = None) -> None:
    """
    Log a response with consistent format
    
    Args:
        logger: Logger instance
        request_id: Unique request identifier
        status_code: HTTP status code
        duration_ms: Request duration in milliseconds
        response_size: Optional response size in bytes
    """
    logger.info(
        f"RESPONSE [{request_id}] {status_code} {duration_ms:.2f}ms "
        f"size={response_size or 'unknown'}"
    )

def log_error(logger: logging.Logger, error: Exception, context: Optional[dict] = None) -> None:
    """
    Log an error with context information
    
    Args:
        logger: Logger instance
        error: Exception that occurred
        context: Optional context information
    """
    context_str = ""
    if context:
        context_items = [f"{k}={v}" for k, v in context.items()]
        context_str = f" context=[{', '.join(context_items)}]"
    
    logger.error(f"ERROR {type(error).__name__}: {str(error)}{context_str}", exc_info=True)

def log_performance(logger: logging.Logger, operation: str, duration_ms: float, 
                   success: bool = True, details: Optional[dict] = None) -> None:
    """
    Log performance metrics for operations
    
    Args:
        logger: Logger instance
        operation: Operation name
        duration_ms: Operation duration in milliseconds
        success: Whether operation was successful
        details: Optional additional details
    """
    status = "SUCCESS" if success else "FAILED"
    details_str = ""
    if details:
        details_items = [f"{k}={v}" for k, v in details.items()]
        details_str = f" details=[{', '.join(details_items)}]"
    
    logger.info(f"PERFORMANCE {operation} {status} {duration_ms:.2f}ms{details_str}")

def log_security_event(logger: logging.Logger, event_type: str, user_id: Optional[str] = None,
                      ip_address: Optional[str] = None, details: Optional[dict] = None) -> None:
    """
    Log security-related events
    
    Args:
        logger: Logger instance
        event_type: Type of security event
        user_id: Optional user ID
        ip_address: Optional IP address
        details: Optional additional details
    """
    details_str = ""
    if details:
        details_items = [f"{k}={v}" for k, v in details.items()]
        details_str = f" details=[{', '.join(details_items)}]"
    
    logger.warning(
        f"SECURITY {event_type} user={user_id or 'unknown'} "
        f"ip={ip_address or 'unknown'}{details_str}"
    )

class ContextLogger:
    """
    Logger with persistent context information
    """
    
    def __init__(self, logger: logging.Logger, context: dict):
        self.logger = logger
        self.context = context
    
    def _format_message(self, message: str) -> str:
        """Add context to log message"""
        context_items = [f"{k}={v}" for k, v in self.context.items()]
        context_str = " ".join(context_items)
        return f"{message} [{context_str}]"
    
    def debug(self, message: str) -> None:
        self.logger.debug(self._format_message(message))
    
    def info(self, message: str) -> None:
        self.logger.info(self._format_message(message))
    
    def warning(self, message: str) -> None:
        self.logger.warning(self._format_message(message))
    
    def error(self, message: str, exc_info: bool = False) -> None:
        self.logger.error(self._format_message(message), exc_info=exc_info)
    
    def critical(self, message: str) -> None:
        self.logger.critical(self._format_message(message))

def get_context_logger(name: str, context: dict) -> ContextLogger:
    """
    Get a context logger with persistent context information
    
    Args:
        name: Logger name
        context: Context dictionary to include in all log messages
        
    Returns:
        ContextLogger instance
    """
    logger = get_logger(name)
    return ContextLogger(logger, context)

# Initialize logging on import
if not logging.getLogger().handlers:
    log_level = os.getenv("LOG_LEVEL", "INFO")
    setup_logging(log_level) 