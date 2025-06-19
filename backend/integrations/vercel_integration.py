"""
Sophia AI - Complete Vercel Integration
Enhanced Vercel deployment integration with comprehensive functionality
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

class VercelIntegration(Integration):
    """Complete Vercel deployment integration with full API support"""
    
    def __init__(self, service_name: str = "vercel"):
        super().__init__(service_name)
        self.base_url = "https://api.vercel.com"
        self.session = None
        self.team_id = None
    
    async def _create_client(self, config: ServiceConfig) -> Optional[aiohttp.ClientSession]:
        """Create Vercel API client"""
        try:
            self.team_id = config.get_config("team_id")
            
            # Create session with authentication
            headers = {
                "Authorization": f"Bearer {config.get_secret('token')}",
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
            logger.error(f"Failed to create Vercel client: {e}")
            return None
    
    async def _perform_health_check(self) -> bool:
        """Perform Vercel health check"""
        try:
            async with self.session.get(f"{self.base_url}/v2/user") as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Vercel health check failed: {e}")
            return False
    
    async def get_projects(self) -> List[Dict[str, Any]]:
        """Get all projects"""
        try:
            params = {}
            if self.team_id:
                params["teamId"] = self.team_id
            
            async with self.session.get(f"{self.base_url}/v9/projects", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("projects", [])
                else:
                    logger.error(f"Failed to get projects: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error getting projects: {e}")
            return []
    
    async def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get specific project details"""
        try:
            params = {}
            if self.team_id:
                params["teamId"] = self.team_id
            
            async with self.session.get(f"{self.base_url}/v9/projects/{project_id}", params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Failed to get project: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error getting project: {e}")
            return None
    
    async def get_deployments(self, project_id: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Get deployments"""
        try:
            params = {"limit": limit}
            if self.team_id:
                params["teamId"] = self.team_id
            if project_id:
                params["projectId"] = project_id
            
            async with self.session.get(f"{self.base_url}/v6/deployments", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("deployments", [])
                else:
                    logger.error(f"Failed to get deployments: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error getting deployments: {e}")
            return []
    
    async def get_deployment(self, deployment_id: str) -> Optional[Dict[str, Any]]:
        """Get specific deployment details"""
        try:
            params = {}
            if self.team_id:
                params["teamId"] = self.team_id
            
            async with self.session.get(f"{self.base_url}/v13/deployments/{deployment_id}", params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Failed to get deployment: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error getting deployment: {e}")
            return None
    
    async def create_deployment(self, 
                               name: str,
                               files: Dict[str, str],
                               project_settings: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Create a new deployment"""
        try:
            payload = {
                "name": name,
                "files": [
                    {
                        "file": filename,
                        "data": content
                    }
                    for filename, content in files.items()
                ],
                "projectSettings": project_settings or {}
            }
            
            params = {}
            if self.team_id:
                params["teamId"] = self.team_id
            
            async with self.session.post(f"{self.base_url}/v13/deployments", 
                                       json=payload, 
                                       params=params) as response:
                if response.status in [200, 201]:
                    return await response.json()
                else:
                    logger.error(f"Failed to create deployment: {response.status}")
                    error_text = await response.text()
                    logger.error(f"Error details: {error_text}")
                    return None
        except Exception as e:
            logger.error(f"Error creating deployment: {e}")
            return None
    
    async def delete_deployment(self, deployment_id: str) -> bool:
        """Delete a deployment"""
        try:
            params = {}
            if self.team_id:
                params["teamId"] = self.team_id
            
            async with self.session.delete(f"{self.base_url}/v13/deployments/{deployment_id}", 
                                         params=params) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Error deleting deployment: {e}")
            return False
    
    async def get_domains(self, project_id: str = None) -> List[Dict[str, Any]]:
        """Get domains"""
        try:
            params = {}
            if self.team_id:
                params["teamId"] = self.team_id
            if project_id:
                params["projectId"] = project_id
            
            async with self.session.get(f"{self.base_url}/v5/domains", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("domains", [])
                else:
                    logger.error(f"Failed to get domains: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error getting domains: {e}")
            return []
    
    async def add_domain(self, name: str, project_id: str) -> Optional[Dict[str, Any]]:
        """Add a domain to a project"""
        try:
            payload = {
                "name": name,
                "projectId": project_id
            }
            
            params = {}
            if self.team_id:
                params["teamId"] = self.team_id
            
            async with self.session.post(f"{self.base_url}/v5/domains", 
                                       json=payload, 
                                       params=params) as response:
                if response.status in [200, 201]:
                    return await response.json()
                else:
                    logger.error(f"Failed to add domain: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error adding domain: {e}")
            return None
    
    async def get_environment_variables(self, project_id: str) -> List[Dict[str, Any]]:
        """Get environment variables for a project"""
        try:
            params = {}
            if self.team_id:
                params["teamId"] = self.team_id
            
            async with self.session.get(f"{self.base_url}/v9/projects/{project_id}/env", 
                                      params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("envs", [])
                else:
                    logger.error(f"Failed to get environment variables: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error getting environment variables: {e}")
            return []
    
    async def set_environment_variable(self, 
                                     project_id: str,
                                     key: str,
                                     value: str,
                                     target: List[str] = None) -> Optional[Dict[str, Any]]:
        """Set an environment variable"""
        try:
            payload = {
                "key": key,
                "value": value,
                "target": target or ["production", "preview", "development"],
                "type": "encrypted"
            }
            
            params = {}
            if self.team_id:
                params["teamId"] = self.team_id
            
            async with self.session.post(f"{self.base_url}/v9/projects/{project_id}/env", 
                                       json=payload, 
                                       params=params) as response:
                if response.status in [200, 201]:
                    return await response.json()
                else:
                    logger.error(f"Failed to set environment variable: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error setting environment variable: {e}")
            return None
    
    async def get_logs(self, deployment_id: str) -> List[Dict[str, Any]]:
        """Get deployment logs"""
        try:
            params = {}
            if self.team_id:
                params["teamId"] = self.team_id
            
            async with self.session.get(f"{self.base_url}/v2/deployments/{deployment_id}/events", 
                                      params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Failed to get logs: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error getting logs: {e}")
            return []
    
    async def close(self):
        """Close the client session"""
        if self.session:
            await self.session.close()

