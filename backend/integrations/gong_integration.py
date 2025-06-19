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
from backend.analytics.gong_analytics import process_call_for_analytics
# In a real app, this would come from a central DB management module
# from ..database.connection import db_connection_pool 

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
    
    async def process_and_store_call(self, call_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetches a call, processes it for analytics, and stores the results.
        
        Args:
            call_id: The ID of the Gong call to process.
            
        Returns:
            A dictionary of the stored analytics data, or None on failure.
        """
        # 1. Fetch the detailed call data
        call_data = await self.get_call_details(call_id)
        if not call_data:
            logger.warning(f"Could not retrieve details for call {call_id}. Skipping.")
            return None
            
        # 2. Process the data using the analytics library
        analytics_results = process_call_for_analytics(call_data)
        
        # 3. Store the results in the database
        stored_data = await self.store_call_analytics(analytics_results)
        
        return stored_data

    async def store_call_analytics(self, analytics_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Stores the results of a call analysis in the database.
        This is a mock implementation. A real one would use a shared DB connection.
        
        Args:
            analytics_data: The processed analytics data to store.
            
        Returns:
            The data that was stored, or None on failure.
        """
        call_id = analytics_data.get("call_id")
        if not call_id:
            logger.error("Cannot store analytics without a call_id.")
            return None
            
        logger.info(f"Storing analytics for call_id: {call_id}")
        
        # MOCK DATABASE INTERACTION
        # In a real implementation, you would get a connection from a central pool
        # and execute asyncpg INSERT/UPDATE commands here.
        # e.g., conn = await db_connection_pool.acquire()
        #      await conn.execute("INSERT INTO ...", *analytics_data.values())
        #      await db_connection_pool.release(conn)
        
        print(f"--- MOCK DB STORE for call {call_id} ---")
        print(f"  Relevance Score: {analytics_data.get('apartment_relevance_score')}")
        print(f"  Deal Stage: {analytics_data.get('deal_signals', {}).get('deal_progression_stage')}")
        print(f"  Competitors: {analytics_data.get('competitive_intelligence', {}).get('competitors_mentioned')}")
        print("-----------------------------------------")
        
        # For now, just return the data as if it were successfully stored.
        return analytics_data

    async def close(self):
        """Close the client session"""
        if self.session:
            await self.session.close()

