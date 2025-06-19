"""
Sophia AI - Complete Gong Integration
Enhanced Gong CRM integration with comprehensive functionality
"""

import os
import json
import logging
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from ..core.integration_config import Integration, ServiceConfig

logger = logging.getLogger(__name__)

class GongIntegration(Integration):
    """Complete Gong CRM integration with full API support"""
    
    def __init__(self, service_name: str = "gong"):
        super().__init__(service_name)
        self.base_url = None
        self.session = None
    
    async def _create_client(self, config: ServiceConfig) -> Optional[aiohttp.ClientSession]:
        """Create Gong API client"""
        try:
            self.base_url = config.get_config("base_url", "https://api.gong.io")
            
            # Create session with authentication
            headers = {
                "Authorization": f"Basic {config.get_secret('api_key')}",
                "Content-Type": "application/json"
            }
            
            connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
            timeout = aiohttp.ClientTimeout(total=30)
            
            self.session = aiohttp.ClientSession(
                headers=headers,
                connector=connector,
                timeout=timeout
            )
            
            return self.session
        except Exception as e:
            logger.error(f"Failed to create Gong client: {e}")
            return None
    
    async def _perform_health_check(self) -> bool:
        """Perform Gong health check"""
        try:
            async with self.session.get(f"{self.base_url}/v2/users") as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Gong health check failed: {e}")
            return False
    
    async def get_calls(self, 
                       from_date: datetime = None, 
                       to_date: datetime = None,
                       limit: int = 100) -> List[Dict[str, Any]]:
        """Get calls from Gong"""
        try:
            if not from_date:
                from_date = datetime.now() - timedelta(days=7)
            if not to_date:
                to_date = datetime.now()
            
            params = {
                "fromDateTime": from_date.isoformat(),
                "toDateTime": to_date.isoformat(),
                "limit": limit
            }
            
            async with self.session.get(f"{self.base_url}/v2/calls", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("calls", [])
                else:
                    logger.error(f"Failed to get calls: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error getting calls: {e}")
            return []
    
    async def get_call_details(self, call_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific call"""
        try:
            async with self.session.get(f"{self.base_url}/v2/calls/{call_id}") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Failed to get call details: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error getting call details: {e}")
            return None
    
    async def get_call_transcript(self, call_id: str) -> Optional[str]:
        """Get transcript for a specific call"""
        try:
            async with self.session.get(f"{self.base_url}/v2/calls/{call_id}/transcript") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("transcript", "")
                else:
                    logger.error(f"Failed to get call transcript: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error getting call transcript: {e}")
            return None
    
    async def get_users(self) -> List[Dict[str, Any]]:
        """Get all users from Gong"""
        try:
            async with self.session.get(f"{self.base_url}/v2/users") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("users", [])
                else:
                    logger.error(f"Failed to get users: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error getting users: {e}")
            return []
    
    async def get_deals(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get deals from Gong"""
        try:
            params = {"limit": limit}
            
            async with self.session.get(f"{self.base_url}/v2/deals", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("deals", [])
                else:
                    logger.error(f"Failed to get deals: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error getting deals: {e}")
            return []
    
    async def search_calls(self, 
                          query: str,
                          from_date: datetime = None,
                          to_date: datetime = None) -> List[Dict[str, Any]]:
        """Search calls by query"""
        try:
            if not from_date:
                from_date = datetime.now() - timedelta(days=30)
            if not to_date:
                to_date = datetime.now()
            
            payload = {
                "filter": {
                    "fromDateTime": from_date.isoformat(),
                    "toDateTime": to_date.isoformat(),
                    "contentSelector": {
                        "exposedFields": {
                            "content": {
                                "transcriptSelector": {
                                    "query": query
                                }
                            }
                        }
                    }
                }
            }
            
            async with self.session.post(f"{self.base_url}/v2/calls/search", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("calls", [])
                else:
                    logger.error(f"Failed to search calls: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error searching calls: {e}")
            return []
    
    async def close(self):
        """Close the client session"""
        if self.session:
            await self.session.close()

