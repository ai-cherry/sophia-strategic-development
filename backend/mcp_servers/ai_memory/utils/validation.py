"""Validation utilities"""

from typing import Any, Dict, List
from ..core.exceptions import ConfigurationException

def validate_memory_content(content: str) -> bool:
    """Validate memory content"""
    if not content or not content.strip():
        raise ValueError("Memory content cannot be empty")
    if len(content) > 10000:  # 10KB limit
        raise ValueError("Memory content too large")
    return True

def validate_search_query(query: str) -> bool:
    """Validate search query"""
    if not query or not query.strip():
        raise ValueError("Search query cannot be empty")
    if len(query) > 1000:
        raise ValueError("Search query too long")
    return True

def validate_config(config: Dict[str, Any]) -> bool:
    """Validate configuration"""
    required_fields = ['database_url', 'vector_dimension']
    for field in required_fields:
        if field not in config:
            raise ConfigurationException(f"Missing required config field: {field}")
    return True
