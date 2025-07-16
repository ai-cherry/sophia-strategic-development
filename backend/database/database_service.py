"""
Database Service for PostgreSQL operations
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
import asyncpg
import json
from datetime import datetime

from backend.core.auto_esc_config import get_config_value

logger = logging.getLogger(__name__)

class DatabaseService:
    """Service for database operations"""
    
    def __init__(self):
        self.connection_pool = None
        self.database_url = get_config_value("postgresql_url", "postgresql://localhost:5432/sophia_ai")
    
    async def initialize_pool(self):
        """Initialize connection pool"""
        try:
            self.connection_pool = await asyncpg.create_pool(
                self.database_url,
                min_size=10,
                max_size=20,
                command_timeout=60
            )
            logger.info("Database connection pool initialized")
        except Exception as e:
            logger.error(f"Error initializing database pool: {e}")
            raise
    
    async def execute_query(self, query: str, params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        """Execute a query and return results"""
        if not self.connection_pool:
            await self.initialize_pool()
        
        try:
            async with self.connection_pool.acquire() as connection:
                if params:
                    rows = await connection.fetch(query, *params)
                else:
                    rows = await connection.fetch(query)
                
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise
    
    async def execute_insert(self, query: str, params: Optional[List[Any]] = None) -> str:
        """Execute an insert query and return the inserted ID"""
        if not self.connection_pool:
            await self.initialize_pool()
        
        try:
            async with self.connection_pool.acquire() as connection:
                if params:
                    result = await connection.fetchrow(query, *params)
                else:
                    result = await connection.fetchrow(query)
                
                return str(result[0]) if result else ""
        except Exception as e:
            logger.error(f"Error executing insert: {e}")
            raise
    
    async def execute_update(self, query: str, params: Optional[List[Any]] = None) -> int:
        """Execute an update query and return the number of affected rows"""
        if not self.connection_pool:
            await self.initialize_pool()
        
        try:
            async with self.connection_pool.acquire() as connection:
                if params:
                    result = await connection.execute(query, *params)
                else:
                    result = await connection.execute(query)
                
                # Extract row count from result string like "UPDATE 5"
                return int(result.split()[-1]) if result else 0
        except Exception as e:
            logger.error(f"Error executing update: {e}")
            raise
    
    async def close_pool(self):
        """Close the connection pool"""
        if self.connection_pool:
            await self.connection_pool.close()
            logger.info("Database connection pool closed")
