"""
Simple logger module for Sophia AI backend
"""

import logging
import sys
from typing import Optional

def get_logger(name: str = __name__, level: Optional[str] = None) -> logging.Logger:
    """
    Get a configured logger instance
    
    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(handler)
        
        # Set level
        log_level = level or logging.INFO
        if isinstance(log_level, str):
            log_level = getattr(logging, log_level.upper(), logging.INFO)
        logger.setLevel(log_level)
    
    return logger 