"""
Legacy Auto ESC Config - REFACTORED
This file now delegates to the new modular configuration system
"""

import logging
from typing import Dict, Any, Optional

# Import from new modular system
from .config.config_container import get_config_container
from .config.secret_manager import get_config_value
from .config.service_configs import ServiceConfigs

logger = logging.getLogger(__name__)

# Get container instance
container = get_config_container()

# Backward compatibility functions
def get_qdrant_config() -> Dict[str, str]:
    """Get Qdrant configuration (delegated)"""
    return container.service_configs.get_qdrant_config()

def get_redis_config() -> Dict[str, Any]:
    """Get Redis configuration (delegated)"""
    return container.service_configs.get_redis_config()

def get_lambda_labs_config() -> Dict[str, Any]:
    """Get Lambda Labs configuration (delegated)"""
    return container.service_configs.get_lambda_labs_config()

def get_gong_config() -> Dict[str, Any]:
    """Get Gong configuration (delegated)"""
    return container.service_configs.get_gong_config()

def get_docker_hub_config() -> Dict[str, str]:
    """Get Docker Hub configuration (delegated)"""
    return container.service_configs.get_docker_hub_config()

def get_integration_config() -> Dict[str, Any]:
    """Get integration configuration (delegated)"""
    return container.service_configs.get_integration_config()

# Backward compatibility for config object
class ConfigObject:
    """Backward compatibility object"""
    
    def get(self, key: str, default: Any = None) -> Any:
        return get_config_value(key, default)

    def __getitem__(self, key: str) -> Any:
        return get_config_value(key)

    def __getattr__(self, name):
        return get_config_value(name)

# Create backward compatibility config object
config = ConfigObject()

# Common configuration values
ENVIRONMENT = container.base_config.environment
PULUMI_ORG = container.base_config.pulumi_org
PULUMI_STACK = container.base_config.pulumi_stack

logger.info("✅ Refactored configuration system loaded")
