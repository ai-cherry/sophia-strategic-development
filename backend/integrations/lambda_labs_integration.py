"""
Sophia AI - Complete Lambda Labs Integration
Enhanced Lambda Labs GPU cloud integration with comprehensive functionality
"""

import os
import json
import logging
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..core.integration_config import Integration, ServiceConfig

logger = logging.getLogger(__name__)

class LambdaLabsIntegration(Integration):
    """Complete Lambda Labs GPU cloud integration with full API support"""
    
    def __init__(self, service_name: str = "lambda_labs"):
        super().__init__(service_name)
        self.base_url = "https://cloud.lambdalabs.com/api/v1"
        self.session = None
    
    async def _create_client(self, config: ServiceConfig) -> Optional[aiohttp.ClientSession]:
        """Create Lambda Labs API client"""
        try:
            # Create session with authentication
            headers = {
                "Authorization": f"Bearer {config.get_secret('api_key')}",
                "Content-Type": "application/json"
            }
            
            connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
            timeout = aiohttp.ClientTimeout(total=60)
            
            self.session = aiohttp.ClientSession(
                headers=headers,
                connector=connector,
                timeout=timeout
            )
            
            return self.session
        except Exception as e:
            logger.error(f"Failed to create Lambda Labs client: {e}")
            return None
    
    async def _perform_health_check(self) -> bool:
        """Perform Lambda Labs health check"""
        try:
            async with self.session.get(f"{self.base_url}/instance-types") as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Lambda Labs health check failed: {e}")
            return False
    
    async def get_instance_types(self) -> List[Dict[str, Any]]:
        """Get available instance types"""
        try:
            async with self.session.get(f"{self.base_url}/instance-types") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", [])
                else:
                    logger.error(f"Failed to get instance types: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error getting instance types: {e}")
            return []
    
    async def get_instances(self) -> List[Dict[str, Any]]:
        """Get all instances"""
        try:
            async with self.session.get(f"{self.base_url}/instances") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", [])
                else:
                    logger.error(f"Failed to get instances: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error getting instances: {e}")
            return []
    
    async def get_instance(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """Get specific instance details"""
        try:
            async with self.session.get(f"{self.base_url}/instances/{instance_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data")
                else:
                    logger.error(f"Failed to get instance: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error getting instance: {e}")
            return None
    
    async def launch_instance(self, 
                             instance_type: str,
                             region: str,
                             ssh_key_names: List[str],
                             name: str = None) -> Optional[Dict[str, Any]]:
        """Launch a new instance"""
        try:
            payload = {
                "instance_type_name": instance_type,
                "region_name": region,
                "ssh_key_names": ssh_key_names
            }
            
            if name:
                payload["name"] = name
            
            async with self.session.post(f"{self.base_url}/instance-operations/launch", 
                                       json=payload) as response:
                if response.status in [200, 201]:
                    data = await response.json()
                    return data.get("data")
                else:
                    logger.error(f"Failed to launch instance: {response.status}")
                    error_text = await response.text()
                    logger.error(f"Error details: {error_text}")
                    return None
        except Exception as e:
            logger.error(f"Error launching instance: {e}")
            return None
    
    async def terminate_instance(self, instance_id: str) -> bool:
        """Terminate an instance"""
        try:
            payload = {"instance_ids": [instance_id]}
            
            async with self.session.post(f"{self.base_url}/instance-operations/terminate", 
                                       json=payload) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Error terminating instance: {e}")
            return False
    
    async def restart_instance(self, instance_id: str) -> bool:
        """Restart an instance"""
        try:
            payload = {"instance_ids": [instance_id]}
            
            async with self.session.post(f"{self.base_url}/instance-operations/restart", 
                                       json=payload) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Error restarting instance: {e}")
            return False
    
    async def get_ssh_keys(self) -> List[Dict[str, Any]]:
        """Get SSH keys"""
        try:
            async with self.session.get(f"{self.base_url}/ssh-keys") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", [])
                else:
                    logger.error(f"Failed to get SSH keys: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error getting SSH keys: {e}")
            return []
    
    async def add_ssh_key(self, name: str, public_key: str) -> Optional[Dict[str, Any]]:
        """Add an SSH key"""
        try:
            payload = {
                "name": name,
                "public_key": public_key
            }
            
            async with self.session.post(f"{self.base_url}/ssh-keys", 
                                       json=payload) as response:
                if response.status in [200, 201]:
                    data = await response.json()
                    return data.get("data")
                else:
                    logger.error(f"Failed to add SSH key: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error adding SSH key: {e}")
            return None
    
    async def delete_ssh_key(self, ssh_key_id: str) -> bool:
        """Delete an SSH key"""
        try:
            async with self.session.delete(f"{self.base_url}/ssh-keys/{ssh_key_id}") as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Error deleting SSH key: {e}")
            return False
    
    async def get_filesystems(self) -> List[Dict[str, Any]]:
        """Get persistent filesystems"""
        try:
            async with self.session.get(f"{self.base_url}/file-systems") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", [])
                else:
                    logger.error(f"Failed to get filesystems: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error getting filesystems: {e}")
            return []
    
    async def create_filesystem(self, name: str, region: str, size_gib: int) -> Optional[Dict[str, Any]]:
        """Create a persistent filesystem"""
        try:
            payload = {
                "name": name,
                "region_name": region,
                "size_gib": size_gib
            }
            
            async with self.session.post(f"{self.base_url}/file-systems", 
                                       json=payload) as response:
                if response.status in [200, 201]:
                    data = await response.json()
                    return data.get("data")
                else:
                    logger.error(f"Failed to create filesystem: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error creating filesystem: {e}")
            return None
    
    async def delete_filesystem(self, filesystem_id: str) -> bool:
        """Delete a persistent filesystem"""
        try:
            async with self.session.delete(f"{self.base_url}/file-systems/{filesystem_id}") as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Error deleting filesystem: {e}")
            return False
    
    async def get_regions(self) -> List[Dict[str, Any]]:
        """Get available regions"""
        try:
            async with self.session.get(f"{self.base_url}/regions") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", [])
                else:
                    logger.error(f"Failed to get regions: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error getting regions: {e}")
            return []
    
    async def close(self):
        """Close the client session"""
        if self.session:
            await self.session.close()

