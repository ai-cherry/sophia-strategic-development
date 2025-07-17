"""
PostgreSQL Structured Data Store MCP Server Implementation
Relational data storage with separation between coding and business contexts
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import os
import sys

# Add backend to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.core.auto_esc_config import get_config_value

# Try to import asyncpg
try:
    import asyncpg
    from asyncpg import Pool
    ASYNCPG_AVAILABLE = True
except ImportError:
    ASYNCPG_AVAILABLE = False
    print("⚠️  asyncpg not installed. Install with: pip install asyncpg")


class DataSchema(Enum):
    """Data schema types"""
    CODING = "coding_data"
    BUSINESS = "business_data"


@dataclass
class QueryStats:
    """Statistics for query performance"""
    total_queries: int = 0
    total_inserts: int = 0
    total_updates: int = 0
    total_deletes: int = 0
    avg_query_time_ms: float = 0.0
    slow_queries: int = 0


class PostgreSQLMCPServer:
    """
    MCP Server for PostgreSQL structured data operations
    Tier 4 in the hybrid memory architecture
    """
    
    def __init__(self):
        self.name = "postgresql"
        self.version = "1.0.0"
        self.port = 9504  # PostgreSQL MCP server port
        
        # Connection pool
        self.pool: Optional[Pool] = None
        
        # Query statistics
        self.stats: Dict[DataSchema, QueryStats] = {
            schema: QueryStats() for schema in DataSchema
        }
        
        # Performance tracking
        self.query_times: List[float] = []
        self.max_query_history = 1000
        
    async def initialize(self):
        """Initialize PostgreSQL connection pool and schemas"""
        try:
            if not ASYNCPG_AVAILABLE:
                print("❌ asyncpg not available, running in mock mode")
                return
                
            # Get PostgreSQL configuration
            pg_host = get_config_value("postgres_host", "localhost")
            pg_port = int(get_config_value("postgres_port", "5432") or "5432")
            pg_user = get_config_value("postgres_user", "sophia")
            pg_password = get_config_value("postgres_password")
            pg_database = get_config_value("postgres_database", "sophia_memory")
            
            # Create connection pool
            self.pool = await asyncpg.create_pool(
                host=pg_host or "localhost",
                port=pg_port,
                user=pg_user or "sophia",
                password=pg_password,
                database=pg_database or "sophia_memory",
                min_size=10,
                max_size=20,
                timeout=60.0,
                command_timeout=30.0
            )
            
            # Initialize schemas
            await self._initialize_schemas()
            
            print(f"✅ PostgreSQL MCP Server initialized on port {self.port}")
            
        except Exception as e:
            print(f"❌ Failed to initialize PostgreSQL Server: {e}")
            raise
    
    async def _initialize_schemas(self):
        """Initialize database schemas and tables"""
        if not self.pool:
            return
            
        async with self.pool.acquire() as conn:
            # Create schemas
            await conn.execute('''
                CREATE SCHEMA IF NOT EXISTS coding_data;
                CREATE SCHEMA IF NOT EXISTS business_data;
            ''')
            
            # Create coding data tables
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS coding_data.repositories (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) UNIQUE NOT NULL,
                    language VARCHAR(50),
                    last_indexed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata JSONB DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS coding_data.code_patterns (
                    id SERIAL PRIMARY KEY,
                    repository_id INTEGER REFERENCES coding_data.repositories(id) ON DELETE CASCADE,
                    pattern_type VARCHAR(100) NOT NULL,
                    pattern_data JSONB NOT NULL,
                    frequency INTEGER DEFAULT 1,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS coding_data.dependencies (
                    id SERIAL PRIMARY KEY,
                    repository_id INTEGER REFERENCES coding_data.repositories(id) ON DELETE CASCADE,
                    dependency_name VARCHAR(255) NOT NULL,
                    version VARCHAR(50),
                    type VARCHAR(50),
                    metadata JSONB DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Indexes for coding data
                CREATE INDEX IF NOT EXISTS idx_repositories_name ON coding_data.repositories(name);
                CREATE INDEX IF NOT EXISTS idx_patterns_type ON coding_data.code_patterns(pattern_type);
                CREATE INDEX IF NOT EXISTS idx_dependencies_name ON coding_data.dependencies(dependency_name);
            ''')
            
            # Create business data tables
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS business_data.projects (
                    id SERIAL PRIMARY KEY,
                    project_id VARCHAR(100) UNIQUE NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    status VARCHAR(50),
                    priority VARCHAR(20),
                    metadata JSONB DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS business_data.insights (
                    id SERIAL PRIMARY KEY,
                    project_id INTEGER REFERENCES business_data.projects(id) ON DELETE CASCADE,
                    insight_type VARCHAR(100) NOT NULL,
                    content TEXT NOT NULL,
                    confidence_score FLOAT,
                    source VARCHAR(100),
                    metadata JSONB DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS business_data.metrics (
                    id SERIAL PRIMARY KEY,
                    project_id INTEGER REFERENCES business_data.projects(id) ON DELETE CASCADE,
                    metric_name VARCHAR(100) NOT NULL,
                    metric_value FLOAT NOT NULL,
                    unit VARCHAR(50),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata JSONB DEFAULT '{}'
                );
                
                CREATE TABLE IF NOT EXISTS business_data.relationships (
                    id SERIAL PRIMARY KEY,
                    source_type VARCHAR(50) NOT NULL,
                    source_id INTEGER NOT NULL,
                    target_type VARCHAR(50) NOT NULL,
                    target_id INTEGER NOT NULL,
                    relationship_type VARCHAR(100) NOT NULL,
                    strength FLOAT DEFAULT 1.0,
                    metadata JSONB DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Indexes for business data
                CREATE INDEX IF NOT EXISTS idx_projects_project_id ON business_data.projects(project_id);
                CREATE INDEX IF NOT EXISTS idx_insights_type ON business_data.insights(insight_type);
                CREATE INDEX IF NOT EXISTS idx_metrics_name ON business_data.metrics(metric_name);
                CREATE INDEX IF NOT EXISTS idx_relationships_types ON business_data.relationships(source_type, target_type);
            ''')
            
            print("✅ PostgreSQL schemas initialized")
    
    async def _track_query_time(self, time_seconds: float):
        """Track query execution times"""
        time_ms = time_seconds * 1000
        self.query_times.append(time_ms)
        
        if len(self.query_times) > self.max_query_history:
            self.query_times.pop(0)
            
        # Count slow queries (> 100ms)
        if time_ms > 100:
            for schema in DataSchema:
                self.stats[schema].slow_queries += 1
    
    # Coding Data Operations
    
    async def add_repository(self,
                           name: str,
                           language: str,
                           metadata: Optional[Dict[str, Any]] = None) -> int:
        """Add a new repository"""
        if not self.pool:
            return -1
            
        start_time = time.time()
        
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchval('''
                    INSERT INTO coding_data.repositories (name, language, metadata)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (name) DO UPDATE
                    SET language = $2, metadata = $3, updated_at = CURRENT_TIMESTAMP
                    RETURNING id
                ''', name, language, json.dumps(metadata or {}))
                
                self.stats[DataSchema.CODING].total_inserts += 1
                await self._track_query_time(time.time() - start_time)
                
                return result
                
        except Exception as e:
            print(f"❌ Error adding repository: {e}")
            return -1
    
    async def add_code_pattern(self,
                             repository_name: str,
                             pattern_type: str,
                             pattern_data: Dict[str, Any]) -> bool:
        """Add a code pattern"""
        if not self.pool:
            return False
            
        start_time = time.time()
        
        try:
            async with self.pool.acquire() as conn:
                # Get repository ID
                repo_id = await conn.fetchval(
                    'SELECT id FROM coding_data.repositories WHERE name = $1',
                    repository_name
                )
                
                if not repo_id:
                    return False
                
                await conn.execute('''
                    INSERT INTO coding_data.code_patterns 
                    (repository_id, pattern_type, pattern_data)
                    VALUES ($1, $2, $3)
                ''', repo_id, pattern_type, json.dumps(pattern_data))
                
                self.stats[DataSchema.CODING].total_inserts += 1
                await self._track_query_time(time.time() - start_time)
                
                return True
                
        except Exception as e:
            print(f"❌ Error adding code pattern: {e}")
            return False
    
    async def get_repository_patterns(self,
                                    repository_name: str,
                                    pattern_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get code patterns for a repository"""
        if not self.pool:
            return []
            
        start_time = time.time()
        
        try:
            async with self.pool.acquire() as conn:
                if pattern_type:
                    query = '''
                        SELECT cp.*, r.name as repository_name
                        FROM coding_data.code_patterns cp
                        JOIN coding_data.repositories r ON cp.repository_id = r.id
                        WHERE r.name = $1 AND cp.pattern_type = $2
                        ORDER BY cp.frequency DESC
                    '''
                    rows = await conn.fetch(query, repository_name, pattern_type)
                else:
                    query = '''
                        SELECT cp.*, r.name as repository_name
                        FROM coding_data.code_patterns cp
                        JOIN coding_data.repositories r ON cp.repository_id = r.id
                        WHERE r.name = $1
                        ORDER BY cp.frequency DESC
                    '''
                    rows = await conn.fetch(query, repository_name)
                
                self.stats[DataSchema.CODING].total_queries += 1
                await self._track_query_time(time.time() - start_time)
                
                return [dict(row) for row in rows]
                
        except Exception as e:
            print(f"❌ Error getting repository patterns: {e}")
            return []
    
    # Business Data Operations
    
    async def add_project(self,
                        project_id: str,
                        name: str,
                        status: str = "active",
                        priority: str = "normal",
                        metadata: Optional[Dict[str, Any]] = None) -> int:
        """Add a new project"""
        if not self.pool:
            return -1
            
        start_time = time.time()
        
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchval('''
                    INSERT INTO business_data.projects 
                    (project_id, name, status, priority, metadata)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (project_id) DO UPDATE
                    SET name = $2, status = $3, priority = $4, 
                        metadata = $5, updated_at = CURRENT_TIMESTAMP
                    RETURNING id
                ''', project_id, name, status, priority, json.dumps(metadata or {}))
                
                self.stats[DataSchema.BUSINESS].total_inserts += 1
                await self._track_query_time(time.time() - start_time)
                
                return result
                
        except Exception as e:
            print(f"❌ Error adding project: {e}")
            return -1
    
    async def add_insight(self,
                        project_id: str,
                        insight_type: str,
                        content: str,
                        confidence_score: float = 0.0,
                        source: str = "unknown",
                        metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Add a business insight"""
        if not self.pool:
            return False
            
        start_time = time.time()
        
        try:
            async with self.pool.acquire() as conn:
                # Get project ID
                proj_id = await conn.fetchval(
                    'SELECT id FROM business_data.projects WHERE project_id = $1',
                    project_id
                )
                
                if not proj_id:
                    return False
                
                await conn.execute('''
                    INSERT INTO business_data.insights 
                    (project_id, insight_type, content, confidence_score, source, metadata)
                    VALUES ($1, $2, $3, $4, $5, $6)
                ''', proj_id, insight_type, content, confidence_score, source, 
                    json.dumps(metadata or {}))
                
                self.stats[DataSchema.BUSINESS].total_inserts += 1
                await self._track_query_time(time.time() - start_time)
                
                return True
                
        except Exception as e:
            print(f"❌ Error adding insight: {e}")
            return False
    
    async def add_metric(self,
                       project_id: str,
                       metric_name: str,
                       metric_value: float,
                       unit: Optional[str] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Add a business metric"""
        if not self.pool:
            return False
            
        start_time = time.time()
        
        try:
            async with self.pool.acquire() as conn:
                # Get project ID
                proj_id = await conn.fetchval(
                    'SELECT id FROM business_data.projects WHERE project_id = $1',
                    project_id
                )
                
                if not proj_id:
                    return False
                
                await conn.execute('''
                    INSERT INTO business_data.metrics 
                    (project_id, metric_name, metric_value, unit, metadata)
                    VALUES ($1, $2, $3, $4, $5)
                ''', proj_id, metric_name, metric_value, unit, 
                    json.dumps(metadata or {}))
                
                self.stats[DataSchema.BUSINESS].total_inserts += 1
                await self._track_query_time(time.time() - start_time)
                
                return True
                
        except Exception as e:
            print(f"❌ Error adding metric: {e}")
            return False
    
    async def get_project_insights(self,
                                 project_id: str,
                                 insight_type: Optional[str] = None,
                                 limit: int = 50) -> List[Dict[str, Any]]:
        """Get insights for a project"""
        if not self.pool:
            return []
            
        start_time = time.time()
        
        try:
            async with self.pool.acquire() as conn:
                if insight_type:
                    query = '''
                        SELECT i.*, p.name as project_name
                        FROM business_data.insights i
                        JOIN business_data.projects p ON i.project_id = p.id
                        WHERE p.project_id = $1 AND i.insight_type = $2
                        ORDER BY i.created_at DESC
                        LIMIT $3
                    '''
                    rows = await conn.fetch(query, project_id, insight_type, limit)
                else:
                    query = '''
                        SELECT i.*, p.name as project_name
                        FROM business_data.insights i
                        JOIN business_data.projects p ON i.project_id = p.id
                        WHERE p.project_id = $1
                        ORDER BY i.created_at DESC
                        LIMIT $2
                    '''
                    rows = await conn.fetch(query, project_id, limit)
                
                self.stats[DataSchema.BUSINESS].total_queries += 1
                await self._track_query_time(time.time() - start_time)
                
                return [dict(row) for row in rows]
                
        except Exception as e:
            print(f"❌ Error getting project insights: {e}")
            return []
    
    async def get_project_metrics(self,
                                project_id: str,
                                metric_name: Optional[str] = None,
                                time_range: Optional[timedelta] = None) -> List[Dict[str, Any]]:
        """Get metrics for a project"""
        if not self.pool:
            return []
            
        start_time = time.time()
        
        try:
            async with self.pool.acquire() as conn:
                base_query = '''
                    SELECT m.*, p.name as project_name
                    FROM business_data.metrics m
                    JOIN business_data.projects p ON m.project_id = p.id
                    WHERE p.project_id = $1
                '''
                params = [project_id]
                
                if metric_name:
                    base_query += ' AND m.metric_name = $2'
                    params.append(metric_name)
                
                if time_range:
                    cutoff = datetime.utcnow() - time_range
                    param_num = len(params) + 1
                    base_query += f' AND m.timestamp > ${param_num}'
                    params.append(cutoff.isoformat())
                
                base_query += ' ORDER BY m.timestamp DESC'
                
                rows = await conn.fetch(base_query, *params)
                
                self.stats[DataSchema.BUSINESS].total_queries += 1
                await self._track_query_time(time.time() - start_time)
                
                return [dict(row) for row in rows]
                
        except Exception as e:
            print(f"❌ Error getting project metrics: {e}")
            return []
    
    async def add_relationship(self,
                             source_type: str,
                             source_id: int,
                             target_type: str,
                             target_id: int,
                             relationship_type: str,
                             strength: float = 1.0,
                             metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Add a relationship between entities"""
        if not self.pool:
            return False
            
        start_time = time.time()
        
        try:
            async with self.pool.acquire() as conn:
                await conn.execute('''
                    INSERT INTO business_data.relationships 
                    (source_type, source_id, target_type, target_id, 
                     relationship_type, strength, metadata)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                ''', source_type, source_id, target_type, target_id,
                    relationship_type, strength, json.dumps(metadata or {}))
                
                self.stats[DataSchema.BUSINESS].total_inserts += 1
                await self._track_query_time(time.time() - start_time)
                
                return True
                
        except Exception as e:
            print(f"❌ Error adding relationship: {e}")
            return False
    
    async def get_stats(self, schema: Optional[DataSchema] = None) -> Dict[str, Any]:
        """Get query statistics"""
        avg_query_time = (
            sum(self.query_times) / len(self.query_times)
            if self.query_times else 0.0
        )
        
        if schema:
            stats = self.stats[schema]
            return {
                "schema": schema.value,
                "total_queries": stats.total_queries,
                "total_inserts": stats.total_inserts,
                "total_updates": stats.total_updates,
                "total_deletes": stats.total_deletes,
                "slow_queries": stats.slow_queries,
                "avg_query_time_ms": avg_query_time
            }
        else:
            all_stats = {
                "avg_query_time_ms": avg_query_time,
                "schemas": {}
            }
            for s in DataSchema:
                all_stats["schemas"][s.value] = await self.get_stats(s)
            return all_stats
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check endpoint"""
        try:
            if self.pool:
                async with self.pool.acquire() as conn:
                    await conn.fetchval('SELECT 1')
                    pool_status = "connected"
            else:
                pool_status = "not_initialized"
                
            return {
                "status": "healthy" if self.pool else "mock_mode",
                "service": "postgresql",
                "version": self.version,
                "port": self.port,
                "pool_status": pool_status,
                "asyncpg_available": ASYNCPG_AVAILABLE
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "service": "postgresql",
                "version": self.version,
                "error": str(e)
            }
    
    # MCP Protocol Methods
    
    async def handle_call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP tool calls"""
        if name == "add_repository":
            repo_name = arguments.get("name", "")
            language = arguments.get("language", "")
            metadata = arguments.get("metadata", {})
            
            repo_id = await self.add_repository(repo_name, language, metadata)
            return {"repository_id": repo_id, "success": repo_id > 0}
            
        elif name == "add_code_pattern":
            repo_name = arguments.get("repository_name", "")
            pattern_type = arguments.get("pattern_type", "")
            pattern_data = arguments.get("pattern_data", {})
            
            success = await self.add_code_pattern(repo_name, pattern_type, pattern_data)
            return {"success": success}
            
        elif name == "get_repository_patterns":
            repo_name = arguments.get("repository_name", "")
            pattern_type = arguments.get("pattern_type")
            
            patterns = await self.get_repository_patterns(repo_name, pattern_type)
            return {"patterns": patterns, "count": len(patterns)}
            
        elif name == "add_project":
            project_id = arguments.get("project_id", "")
            project_name = arguments.get("name", "")
            status = arguments.get("status", "active")
            priority = arguments.get("priority", "normal")
            metadata = arguments.get("metadata", {})
            
            proj_id = await self.add_project(project_id, project_name, status, priority, metadata)
            return {"id": proj_id, "success": proj_id > 0}
            
        elif name == "add_insight":
            project_id = arguments.get("project_id", "")
            insight_type = arguments.get("insight_type", "")
            content = arguments.get("content", "")
            confidence = arguments.get("confidence_score", 0.0)
            source = arguments.get("source", "unknown")
            metadata = arguments.get("metadata", {})
            
            success = await self.add_insight(project_id, insight_type, content, 
                                           confidence, source, metadata)
            return {"success": success}
            
        elif name == "get_project_insights":
            project_id = arguments.get("project_id", "")
            insight_type = arguments.get("insight_type")
            limit = arguments.get("limit", 50)
            
            insights = await self.get_project_insights(project_id, insight_type, limit)
            return {"insights": insights, "count": len(insights)}
            
        elif name == "get_stats":
            schema_str = arguments.get("schema")
            schema = DataSchema[schema_str.upper()] if schema_str else None
            
            return await self.get_stats(schema)
            
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    def get_tool_descriptions(self) -> List[Dict[str, Any]]:
        """Get MCP tool descriptions"""
        return [
            {
                "name": "add_repository",
                "description": "Add a coding repository",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Repository name"},
                        "language": {"type": "string", "description": "Primary language"},
                        "metadata": {"type": "object", "description": "Additional metadata"}
                    },
                    "required": ["name", "language"]
                }
            },
            {
                "name": "add_code_pattern",
                "description": "Add a code pattern",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "repository_name": {"type": "string"},
                        "pattern_type": {"type": "string"},
                        "pattern_data": {"type": "object"}
                    },
                    "required": ["repository_name", "pattern_type", "pattern_data"]
                }
            },
            {
                "name": "add_project",
                "description": "Add a business project",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string"},
                        "name": {"type": "string"},
                        "status": {"type": "string", "default": "active"},
                        "priority": {"type": "string", "default": "normal"},
                        "metadata": {"type": "object"}
                    },
                    "required": ["project_id", "name"]
                }
            },
            {
                "name": "add_insight",
                "description": "Add a business insight",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string"},
                        "insight_type": {"type": "string"},
                        "content": {"type": "string"},
                        "confidence_score": {"type": "number", "default": 0.0},
                        "source": {"type": "string", "default": "unknown"},
                        "metadata": {"type": "object"}
                    },
                    "required": ["project_id", "insight_type", "content"]
                }
            }
        ]


# MCP Server entry point
async def main():
    """Main entry point for the MCP server"""
    server = PostgreSQLMCPServer()
    await server.initialize()
    
    # In real implementation, would start MCP protocol server
    print(f"🚀 PostgreSQL MCP Server running on port {server.port}")
    
    # Keep server running
    try:
        while True:
            await asyncio.sleep(3600)
            # Could add periodic maintenance here
    except KeyboardInterrupt:
        print("\n👋 Shutting down PostgreSQL Server")
        if server.pool:
            await server.pool.close()


if __name__ == "__main__":
    asyncio.run(main())
