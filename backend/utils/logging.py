"""Logging utilities for Sophia AI."""

import logging
import sys

def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Set up a logger with standard configuration."""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger

# Default logger instance
logger = setup_logger(__name__)
