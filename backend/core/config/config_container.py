"""
Configuration Container
Dependency injection for configuration management
"""

from typing import Optional
from .base_config import BaseConfig
from .secret_manager import SecretManager
from .service_configs import ServiceConfigs


class ConfigContainer:
    """Dependency injection container for configuration"""
    
    def __init__(self):
        self._base_config: Optional[BaseConfig] = None
        self._secret_manager: Optional[SecretManager] = None
        self._service_configs: Optional[ServiceConfigs] = None
        
    @property
    def base_config(self) -> BaseConfig:
        """Get or create base configuration"""
        if self._base_config is None:
            self._base_config = BaseConfig()
        return self._base_config
        
    @property
    def secret_manager(self) -> SecretManager:
        """Get or create secret manager"""
        if self._secret_manager is None:
            self._secret_manager = SecretManager(self.base_config)
        return self._secret_manager
        
    @property
    def service_configs(self) -> ServiceConfigs:
        """Get or create service configurations"""
        if self._service_configs is None:
            self._service_configs = ServiceConfigs(self.secret_manager)
        return self._service_configs
        
    def get_config_value(self, key: str, default: str = None) -> str:
        """Get configuration value through container"""
        return self.secret_manager.get_config_value(key, default)


# Global container instance
_container: Optional[ConfigContainer] = None


def get_config_container() -> ConfigContainer:
    """Get or create the global configuration container"""
    global _container
    
    if _container is None:
        _container = ConfigContainer()
        
    return _container
