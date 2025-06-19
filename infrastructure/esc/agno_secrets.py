"""
Agno Secrets Manager
Manages secrets for Agno integration
"""

import asyncio
import json
import logging
import os
from typing import Dict, Any, Optional

from infrastructure.pulumi_esc import PulumiESCManager

logger = logging.getLogger(__name__)

class AgnoSecretManager:
    """
    Manages secrets for Agno integration.
    """
    
    def __init__(self):
        """Initialize the Agno secret manager."""
        self.esc_manager = PulumiESCManager()
        self.api_key = None
        self.config = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize the Agno secret manager."""
        if self.initialized:
            return
        
        try:
            # Initialize ESC manager
            await self.esc_manager.initialize()
            
            # Get API key
            self.api_key = await self.get_agno_api_key()
            
            # Get configuration
            self.config = await self.get_agno_config()
            
            self.initialized = True
            logger.info("Agno secret manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Agno secret manager: {e}")
            self.initialized = False
            raise
    
    async def get_agno_api_key(self) -> str:
        """
        Get the Agno API key.
        
        Returns:
            str: The Agno API key
        """
        try:
            # Try to get from ESC
            api_key = await self.esc_manager.get_secret("AGNO_API_KEY")
            if api_key:
                return api_key
            
            # Try to get from environment
            api_key = os.environ.get("AGNO_API_KEY")
            if api_key:
                return api_key
            
            # Use development key if available
            if os.environ.get("ENVIRONMENT") == "development":
                logger.warning("Using development API key for Agno")
                return "agno_dev_key_for_testing_only"
            
            # No API key found
            logger.error("No Agno API key found")
            return ""
        except Exception as e:
            logger.error(f"Failed to get Agno API key: {e}")
            return ""
    
    async def get_agno_config(self) -> Dict[str, Any]:
        """
        Get the Agno configuration.
        
        Returns:
            Dict[str, Any]: The Agno configuration
        """
        try:
            # Try to get from ESC
            config_json = await self.esc_manager.get_secret("AGNO_CONFIG")
            if config_json:
                return json.loads(config_json)
            
            # Try to get from environment
            config_json = os.environ.get("AGNO_CONFIG")
            if config_json:
                return json.loads(config_json)
            
            # Use default configuration
            logger.warning("Using default configuration for Agno")
            return {
                "default_model": "claude-sonnet-4-20250514",
                "agent_pool_size": 10,
                "cache_ttl": 3600,
                "api_base_url": "https://api.agno.dev/v1",
                "timeout": 60,
                "max_retries": 3
            }
        except Exception as e:
            logger.error(f"Failed to get Agno configuration: {e}")
            return {
                "default_model": "claude-sonnet-4-20250514",
                "agent_pool_size": 5,
                "cache_ttl": 3600,
                "api_base_url": "https://api.agno.dev/v1",
                "timeout": 30,
                "max_retries": 2
            }
    
    async def set_agno_api_key(self, api_key: str) -> bool:
        """
        Set the Agno API key.
        
        Args:
            api_key: The Agno API key
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Set in ESC
            success = await self.esc_manager.set_secret("AGNO_API_KEY", api_key)
            if success:
                self.api_key = api_key
                return True
            
            # Failed to set in ESC
            logger.error("Failed to set Agno API key in ESC")
            return False
        except Exception as e:
            logger.error(f"Failed to set Agno API key: {e}")
            return False
    
    async def set_agno_config(self, config: Dict[str, Any]) -> bool:
        """
        Set the Agno configuration.
        
        Args:
            config: The Agno configuration
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Convert to JSON
            config_json = json.dumps(config)
            
            # Set in ESC
            success = await self.esc_manager.set_secret("AGNO_CONFIG", config_json)
            if success:
                self.config = config
                return True
            
            # Failed to set in ESC
            logger.error("Failed to set Agno configuration in ESC")
            return False
        except Exception as e:
            logger.error(f"Failed to set Agno configuration: {e}")
            return False
    
    async def rotate_agno_api_key(self) -> bool:
        """
        Rotate the Agno API key.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # This is a placeholder for rotating the API key
            # In a real implementation, we would call the Agno API to rotate the key
            
            # For now, just log a warning
            logger.warning("Agno API key rotation not implemented")
            return False
        except Exception as e:
            logger.error(f"Failed to rotate Agno API key: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check.
        
        Returns:
            Dict[str, Any]: The health check result
        """
        try:
            # Check if we have an API key
            api_key = await self.get_agno_api_key()
            has_api_key = api_key is not None and len(api_key) > 0
            
            # Check if we have a configuration
            config = await self.get_agno_config()
            has_config = config is not None and len(config) > 0
            
            # Return health check result
            return {
                "status": "healthy" if has_api_key and has_config else "unhealthy",
                "has_api_key": has_api_key,
                "has_config": has_config,
                "initialized": self.initialized
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }


# Global instance
agno_secret_manager = AgnoSecretManager()
