"""
Configuration module for Sophia AI
Modular configuration management with dependency injection
"""

from .base_config import BaseConfig
from .secret_manager import SecretManager, get_config_value
from .service_configs import ServiceConfigs
from .config_container import ConfigContainer

# Backward compatibility
config = ServiceConfigs()

__all__ = [
    'BaseConfig',
    'SecretManager', 
    'ServiceConfigs',
    'ConfigContainer',
    'get_config_value',
    'config'
]
