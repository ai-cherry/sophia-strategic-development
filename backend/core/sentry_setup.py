"""
Sentry Setup for Sophia AI
Initializes Sentry SDK for error tracking
Uses Pulumi ESC for secure configuration management
"""

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
import logging
import os
from backend.core.auto_esc_config import config

logger = logging.getLogger(__name__)

def init_sentry():
    """Initialize Sentry SDK with proper configuration from Pulumi ESC."""
    
    # Get configuration from Pulumi ESC via auto_esc_config
    sentry_dsn = None
    environment = "development"
    
    # Try to get from observability config first
    if hasattr(config, 'observability') and config.observability:
        sentry_dsn = config.observability.sentry_dsn if hasattr(config.observability, 'sentry_dsn') else None
        environment = config.environment if hasattr(config, 'environment') else os.getenv("ENVIRONMENT", "development")
    
    # Fallback to direct config access
    if not sentry_dsn:
        sentry_dsn = config.sentry_dsn if hasattr(config, 'sentry_dsn') else os.getenv("SENTRY_DSN")
    
    if not sentry_dsn:
        logger.warning("SENTRY_DSN not configured in Pulumi ESC or environment, Sentry will not be initialized")
        return False
    
    try:
        # Configure Sentry
        sentry_sdk.init(
            dsn=sentry_dsn,
            environment=environment,
            
            # Performance Monitoring
            traces_sample_rate=1.0 if environment == "development" else 0.1,
            
            # Session tracking
            release=os.getenv("GIT_COMMIT_SHA", "unknown"),
            
            # Integrations
            integrations=[
                LoggingIntegration(
                    level=logging.INFO,        # Capture info and above as breadcrumbs
                    event_level=logging.ERROR   # Send errors as events
                ),
                FastApiIntegration(
                    transaction_style="endpoint",
                    failed_request_status_codes=[400, 401, 403, 404, 405, 500, 502, 503, 504]
                ),
                SqlalchemyIntegration(),
            ],
            
            # Options
            attach_stacktrace=True,
            send_default_pii=False,  # Don't send personally identifiable information
            
            # Before send hook for filtering
            before_send=before_send_filter,
            
            # Breadcrumbs
            max_breadcrumbs=50,
            
            # Debug mode
            debug=environment == "development",
        )
        
        logger.info(f"Sentry initialized successfully for environment: {environment}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}")
        return False

def before_send_filter(event, hint):
    """Filter events before sending to Sentry."""
    
    # Filter out certain errors
    if 'exc_info' in hint:
        exc_type, exc_value, tb = hint['exc_info']
        
        # Don't send certain expected errors
        if exc_type.__name__ in ['KeyboardInterrupt', 'SystemExit']:
            return None
            
        # Filter out 404 errors in production
        if os.getenv("ENVIRONMENT") == "production":
            if hasattr(exc_value, 'status_code') and exc_value.status_code == 404:
                return None
    
    # Add custom context
    event['contexts']['sophia_ai'] = {
        'version': os.getenv("SOPHIA_VERSION", "unknown"),
        'deployment': os.getenv("DEPLOYMENT_ID", "unknown"),
        'mcp_enabled': True,
    }
    
    return event

def capture_message(message: str, level: str = "info"):
    """Capture a message in Sentry."""
    sentry_sdk.capture_message(message, level=level)

def capture_exception(exception: Exception):
    """Capture an exception in Sentry."""
    sentry_sdk.capture_exception(exception)

def set_user_context(user_id: str, email: str = None, username: str = None):
    """Set user context for Sentry."""
    sentry_sdk.set_user({
        "id": user_id,
        "email": email,
        "username": username
    })

def set_tag(key: str, value: str):
    """Set a tag for the current scope."""
    sentry_sdk.set_tag(key, value)

def add_breadcrumb(message: str, category: str = "custom", level: str = "info", data: dict = None):
    """Add a breadcrumb to the current scope."""
    sentry_sdk.add_breadcrumb(
        message=message,
        category=category,
        level=level,
        data=data or {}
    )

# Test function to create an error
def create_test_error():
    """Create a test error for Sentry verification."""
    try:
        # This will create a ZeroDivisionError
        result = 1 / 0
    except Exception as e:
        # Capture the exception in Sentry
        sentry_sdk.capture_exception(e)
        raise
