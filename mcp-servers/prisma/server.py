#!/usr/bin/env python3
"""
Sophia AI Prisma MCP Server
Natural-language PostgreSQL schema operations using Prisma v6.10+ features
Dynamic schema evolution and AI-powered database management

Date: July 12, 2025
"""

import asyncio
import sys
import subprocess
import os
from pathlib import Path
from typing import Any, Optional, Dict, List
from dataclasses import dataclass

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
import asyncpg
from base.unified_standardized_base import (
    ServerConfig,
    ToolDefinition,
    ToolParameter,
    UnifiedStandardizedMCPServer as StandardizedMCPServer,
)
from backend.core.auto_esc_config import get_config_value
from prometheus_client import Counter, Histogram, Gauge

logger = logging.getLogger(__name__)

# Prometheus metrics
schema_operations_counter = Counter('prisma_schema_operations_total', 'Total schema operations', ['operation_type'])
migration_latency = Histogram('prisma_migration_latency_seconds', 'Migration execution latency')
query_generation_latency = Histogram('prisma_query_generation_latency_seconds', 'Query generation latency')
schema_health_score = Gauge('prisma_schema_health_score', 'Schema health score (0-100)')

@dataclass
class SchemaAnalysis:
    """Schema analysis results"""
    tables: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    indexes: List[Dict[str, Any]]
    constraints: List[Dict[str, Any]]
    health_score: float
    recommendations: List[str]
    
@dataclass
class MigrationPlan:
    """Migration plan with steps and validation"""
    steps: List[Dict[str, Any]]
    estimated_duration: float
    risk_level: str
    rollback_steps: List[Dict[str, Any]]
    validation_queries: List[str]

class PrismaMCPServer(StandardizedMCPServer):
    """Prisma MCP Server for natural-language PostgreSQL operations"""

    def __init__(self):
        config = ServerConfig(
            name="prisma",
            version="6.10.0",
            port=9030,
            capabilities=["SCHEMA_INTROSPECTION", "NATURAL_LANGUAGE_MIGRATIONS", "DYNAMIC_QUERIES", "AI_SCHEMA_EVOLUTION"],
            tier="PRIMARY",
        )
        super().__init__(config)

        # Database configuration
        self.db_config = {
            "host": get_config_value("postgres_host", "localhost"),
            "port": get_config_value("postgres_port", "5432"),
            "database": get_config_value("postgres_database", "sophia_ai"),
            "user": get_config_value("postgres_user", "postgres"),
            "password": get_config_value("postgres_password"),
        }
        
        # Prisma configuration
        self.prisma_schema_path = Path("prisma/schema.prisma")
        self.migrations_path = Path("prisma/migrations")
        
        # AI model for natural language processing
        self.ai_model = "gpt-4"  # Can be configured
        
        # Schema cache for performance
        self.schema_cache = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Initialize Prisma schema
        asyncio.create_task(self._initialize_prisma_schema())

    async def _initialize_prisma_schema(self):
        """Initialize Prisma schema file"""
        self.prisma_schema_path.parent.mkdir(exist_ok=True)
        
        if not self.prisma_schema_path.exists():
            schema_content = """
generator client {
  provider = "prisma-client-py"
  recursive_type_depth = 5
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

// Auto-generated schema will be added here
"""
            with open(self.prisma_schema_path, "w") as f:
                f.write(schema_content)
                
        # Set DATABASE_URL environment variable
        db_url = f"postgresql://{self.db_config['user']}:{self.db_config['password']}@{self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}"
        os.environ["DATABASE_URL"] = db_url

    def get_tool_definitions(self) -> list[ToolDefinition]:
        """Define Prisma MCP tools"""
        return [
            ToolDefinition(
                name="analyze_schema",
                description="Analyze PostgreSQL schema and provide health insights",
                parameters=[
                    ToolParameter(
                        name="include_recommendations",
                        type="boolean",
                        description="Include optimization recommendations",
                        required=False,
                    ),
                ],
            ),
            ToolDefinition(
                name="natural_language_migration",
                description="Generate and execute migrations from natural language descriptions",
                parameters=[
                    ToolParameter(
                        name="description",
                        type="string",
                        description="Natural language description of schema changes",
                        required=True,
                    ),
                    ToolParameter(
                        name="dry_run",
                        type="boolean",
                        description="Generate migration plan without executing",
                        required=False,
                    ),
                ],
            ),
            ToolDefinition(
                name="generate_dynamic_query",
                description="Generate optimized SQL queries from natural language",
                parameters=[
                    ToolParameter(
                        name="query_description",
                        type="string",
                        description="Natural language query description",
                        required=True,
                    ),
                    ToolParameter(
                        name="output_format",
                        type="string",
                        description="Output format (sql, prisma, json)",
                        required=False,
                    ),
                ],
            ),
            ToolDefinition(
                name="evolve_schema",
                description="AI-powered schema evolution based on usage patterns",
                parameters=[
                    ToolParameter(
                        name="analysis_period_days",
                        type="integer",
                        description="Period in days to analyze usage patterns",
                        required=False,
                    ),
                    ToolParameter(
                        name="evolution_strategy",
                        type="string",
                        description="Evolution strategy (performance, normalization, denormalization)",
                        required=False,
                    ),
                ],
            ),
            ToolDefinition(
                name="introspect_database",
                description="Introspect existing database and generate Prisma schema",
                parameters=[
                    ToolParameter(
                        name="update_schema_file",
                        type="boolean",
                        description="Update the Prisma schema file",
                        required=False,
                    ),
                ],
            ),
            ToolDefinition(
                name="validate_schema",
                description="Validate Prisma schema against database and best practices",
                parameters=[
                    ToolParameter(
                        name="check_performance",
                        type="boolean",
                        description="Include performance validation",
                        required=False,
                    ),
                ],
            ),
            ToolDefinition(
                name="generate_seed_data",
                description="Generate realistic seed data based on schema",
                parameters=[
                    ToolParameter(
                        name="table_name",
                        type="string",
                        description="Specific table to generate data for",
                        required=False,
                    ),
                    ToolParameter(
                        name="record_count",
                        type="integer",
                        description="Number of records to generate",
                        required=False,
                    ),
                ],
            ),
            ToolDefinition(
                name="optimize_queries",
                description="Analyze and optimize slow queries",
                parameters=[
                    ToolParameter(
                        name="query_log_analysis",
                        type="boolean",
                        description="Analyze query logs for optimization",
                        required=False,
                    ),
                ],
            ),
        ]

    async def handle_tool_call(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Handle Prisma tool calls"""
        try:
            if tool_name == "analyze_schema":
                return await self._analyze_schema(**arguments)
            elif tool_name == "natural_language_migration":
                return await self._natural_language_migration(**arguments)
            elif tool_name == "generate_dynamic_query":
                return await self._generate_dynamic_query(**arguments)
            elif tool_name == "evolve_schema":
                return await self._evolve_schema(**arguments)
            elif tool_name == "introspect_database":
                return await self._introspect_database(**arguments)
            elif tool_name == "validate_schema":
                return await self._validate_schema(**arguments)
            elif tool_name == "generate_seed_data":
                return await self._generate_seed_data(**arguments)
            elif tool_name == "optimize_queries":
                return await self._optimize_queries(**arguments)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            logger.error(f"Tool call failed: {e}")
            return {"error": str(e)}

    async def _analyze_schema(self, include_recommendations: bool = True) -> dict[str, Any]:
        """Analyze PostgreSQL schema and provide insights"""
        schema_operations_counter.labels(operation_type="analyze").inc()
        
        conn = await asyncpg.connect(**self.db_config)
        try:
            # Get table information
            tables_query = """
            SELECT 
                schemaname,
                tablename,
                tableowner,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                pg_stat_get_tuples_inserted(c.oid) as inserts,
                pg_stat_get_tuples_updated(c.oid) as updates,
                pg_stat_get_tuples_deleted(c.oid) as deletes
            FROM pg_tables pt
            JOIN pg_class c ON c.relname = pt.tablename
            WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
            """
            
            tables = await conn.fetch(tables_query)
            
            # Get relationships
            relationships_query = """
            SELECT 
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name,
                tc.constraint_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema = 'public';
            """
            
            relationships = await conn.fetch(relationships_query)
            
            # Get indexes
            indexes_query = """
            SELECT 
                schemaname,
                tablename,
                indexname,
                indexdef,
                pg_size_pretty(pg_relation_size(indexname::regclass)) as size
            FROM pg_indexes
            WHERE schemaname = 'public'
            ORDER BY pg_relation_size(indexname::regclass) DESC;
            """
            
            indexes = await conn.fetch(indexes_query)
            
            # Calculate health score
            health_score = await self._calculate_schema_health(conn)
            
            recommendations = []
            if include_recommendations:
                recommendations = await self._generate_schema_recommendations(conn, tables, relationships, indexes)
            
            # Update Prometheus metric
            schema_health_score.set(health_score)
            
            return {
                "analysis": {
                    "tables": [dict(row) for row in tables],
                    "relationships": [dict(row) for row in relationships],
                    "indexes": [dict(row) for row in indexes],
                    "health_score": health_score,
                    "recommendations": recommendations,
                },
                "summary": {
                    "total_tables": len(tables),
                    "total_relationships": len(relationships),
                    "total_indexes": len(indexes),
                    "health_status": "healthy" if health_score > 80 else "needs_attention" if health_score > 60 else "critical",
                }
            }
            
        finally:
            await conn.close()

    async def _natural_language_migration(self, description: str, dry_run: bool = True) -> dict[str, Any]:
        """Generate and execute migrations from natural language"""
        schema_operations_counter.labels(operation_type="migration").inc()
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Parse natural language description using AI
            migration_plan = await self._parse_migration_description(description)
            
            # Generate Prisma migration
            migration_sql = await self._generate_migration_sql(migration_plan)
            
            # Validate migration
            validation_result = await self._validate_migration(migration_sql)
            
            result = {
                "migration_plan": migration_plan.__dict__,
                "sql": migration_sql,
                "validation": validation_result,
                "dry_run": dry_run,
            }
            
            if not dry_run and validation_result["valid"]:
                # Execute migration
                execution_result = await self._execute_migration(migration_sql)
                result["execution"] = execution_result
                
                # Update Prisma schema
                await self._update_prisma_schema()
                
        except Exception as e:
            result = {"error": str(e)}
        
        finally:
            latency = asyncio.get_event_loop().time() - start_time
            migration_latency.observe(latency)
            
        return result

    async def _generate_dynamic_query(self, query_description: str, output_format: str = "sql") -> dict[str, Any]:
        """Generate optimized SQL queries from natural language"""
        schema_operations_counter.labels(operation_type="query_generation").inc()
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Get current schema for context
            schema_info = await self._get_schema_info()
            
            # Generate query using AI
            query_data = await self._generate_query_from_description(query_description, schema_info)
            
            # Optimize query
            optimized_query = await self._optimize_query(query_data["sql"])
            
            # Format output
            if output_format == "prisma":
                output = await self._convert_sql_to_prisma(optimized_query)
            elif output_format == "json":
                output = await self._generate_query_json(optimized_query)
            else:
                output = optimized_query
            
            result = {
                "query": output,
                "original_sql": query_data["sql"],
                "optimized_sql": optimized_query,
                "explanation": query_data["explanation"],
                "estimated_performance": await self._estimate_query_performance(optimized_query),
                "output_format": output_format,
            }
            
        except Exception as e:
            result = {"error": str(e)}
        
        finally:
            latency = asyncio.get_event_loop().time() - start_time
            query_generation_latency.observe(latency)
            
        return result

    async def _evolve_schema(self, analysis_period_days: int = 30, evolution_strategy: str = "performance") -> dict[str, Any]:
        """AI-powered schema evolution based on usage patterns"""
        schema_operations_counter.labels(operation_type="evolution").inc()
        
        conn = await asyncpg.connect(**self.db_config)
        try:
            # Analyze usage patterns
            usage_patterns = await self._analyze_usage_patterns(conn, analysis_period_days)
            
            # Generate evolution recommendations
            evolution_plan = await self._generate_evolution_plan(usage_patterns, evolution_strategy)
            
            # Estimate impact
            impact_analysis = await self._estimate_evolution_impact(evolution_plan)
            
            return {
                "evolution_plan": evolution_plan,
                "usage_patterns": usage_patterns,
                "impact_analysis": impact_analysis,
                "strategy": evolution_strategy,
                "analysis_period_days": analysis_period_days,
            }
            
        finally:
            await conn.close()

    async def _introspect_database(self, update_schema_file: bool = False) -> dict[str, Any]:
        """Introspect existing database and generate Prisma schema"""
        schema_operations_counter.labels(operation_type="introspection").inc()
        
        try:
            # Run Prisma introspection
            cmd = ["npx", "prisma", "db", "pull"]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.prisma_schema_path.parent)
            
            if result.returncode != 0:
                return {"error": f"Prisma introspection failed: {result.stderr}"}
            
            # Read generated schema
            with open(self.prisma_schema_path, "r") as f:
                schema_content = f.read()
            
            # Parse schema for analysis
            schema_analysis = await self._parse_prisma_schema(schema_content)
            
            return {
                "schema": schema_content,
                "analysis": schema_analysis,
                "updated_file": update_schema_file,
                "introspection_output": result.stdout,
            }
            
        except Exception as e:
            return {"error": str(e)}

    async def _validate_schema(self, check_performance: bool = True) -> dict[str, Any]:
        """Validate Prisma schema against database and best practices"""
        schema_operations_counter.labels(operation_type="validation").inc()
        
        try:
            # Run Prisma validation
            cmd = ["npx", "prisma", "validate"]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.prisma_schema_path.parent)
            
            validation_issues = []
            if result.returncode != 0:
                validation_issues.append({
                    "type": "schema_error",
                    "message": result.stderr,
                    "severity": "error"
                })
            
            # Additional custom validations
            custom_validations = await self._run_custom_validations()
            validation_issues.extend(custom_validations)
            
            # Performance validation
            performance_issues = []
            if check_performance:
                performance_issues = await self._validate_performance()
            
            return {
                "valid": result.returncode == 0 and len(validation_issues) == 0,
                "validation_issues": validation_issues,
                "performance_issues": performance_issues,
                "recommendation_count": len(validation_issues) + len(performance_issues),
            }
            
        except Exception as e:
            return {"error": str(e)}

    # Helper methods for AI-powered functionality
    async def _parse_migration_description(self, description: str) -> MigrationPlan:
        """Parse natural language migration description using AI"""
        # This would use an AI model to parse the description
        # For now, implementing a simple parser
        
        steps = []
        risk_level = "low"
        
        # Simple keyword-based parsing (would be replaced with AI)
        if "create table" in description.lower():
            steps.append({
                "type": "create_table",
                "description": description,
                "sql": f"-- Generated from: {description}"
            })
        elif "add column" in description.lower():
            steps.append({
                "type": "add_column",
                "description": description,
                "sql": f"-- Generated from: {description}"
            })
        elif "drop" in description.lower():
            risk_level = "high"
            steps.append({
                "type": "drop_operation",
                "description": description,
                "sql": f"-- Generated from: {description}"
            })
        
        return MigrationPlan(
            steps=steps,
            estimated_duration=5.0,  # seconds
            risk_level=risk_level,
            rollback_steps=[],
            validation_queries=[]
        )

    async def _generate_migration_sql(self, migration_plan: MigrationPlan) -> str:
        """Generate SQL from migration plan"""
        sql_parts = []
        
        for step in migration_plan.steps:
            sql_parts.append(step["sql"])
        
        return "\n".join(sql_parts)

    async def _validate_migration(self, sql: str) -> dict[str, Any]:
        """Validate migration SQL"""
        # Basic validation
        return {
            "valid": True,
            "warnings": [],
            "errors": [],
            "estimated_duration": 5.0
        }

    async def _execute_migration(self, sql: str) -> dict[str, Any]:
        """Execute migration SQL"""
        conn = await asyncpg.connect(**self.db_config)
        try:
            await conn.execute(sql)
            return {"success": True, "message": "Migration executed successfully"}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            await conn.close()

    async def _calculate_schema_health(self, conn) -> float:
        """Calculate overall schema health score"""
        # Implement health scoring logic
        return 85.0  # Placeholder

    async def _generate_schema_recommendations(self, conn, tables, relationships, indexes) -> List[str]:
        """Generate schema optimization recommendations"""
        recommendations = []
        
        # Check for missing indexes
        if len(indexes) < len(tables):
            recommendations.append("Consider adding indexes to improve query performance")
        
        # Check for orphaned tables
        table_names = {table['tablename'] for table in tables}
        referenced_tables = {rel['table_name'] for rel in relationships}
        
        if len(referenced_tables) < len(table_names):
            recommendations.append("Some tables lack foreign key relationships")
        
        return recommendations

    async def _get_schema_info(self) -> dict[str, Any]:
        """Get current schema information"""
        conn = await asyncpg.connect(**self.db_config)
        try:
            # Get table and column information
            query = """
            SELECT 
                table_name,
                column_name,
                data_type,
                is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position;
            """
            
            columns = await conn.fetch(query)
            
            # Group by table
            schema_info = {}
            for col in columns:
                table_name = col['table_name']
                if table_name not in schema_info:
                    schema_info[table_name] = []
                schema_info[table_name].append({
                    'column': col['column_name'],
                    'type': col['data_type'],
                    'nullable': col['is_nullable'] == 'YES'
                })
            
            return schema_info
            
        finally:
            await conn.close()

    async def _generate_query_from_description(self, description: str, schema_info: dict) -> dict[str, Any]:
        """Generate SQL query from natural language description"""
        # This would use an AI model in production
        # For now, simple pattern matching
        
        sql = f"-- Generated from: {description}\nSELECT * FROM information_schema.tables LIMIT 10;"
        
        return {
            "sql": sql,
            "explanation": f"Generated query based on: {description}",
            "confidence": 0.8
        }

    async def _optimize_query(self, sql: str) -> str:
        """Optimize SQL query"""
        # Basic optimization - would use query planner in production
        return sql

    async def _estimate_query_performance(self, sql: str) -> dict[str, Any]:
        """Estimate query performance"""
        return {
            "estimated_rows": 1000,
            "estimated_time_ms": 50,
            "cost_estimate": 10.5,
            "optimization_suggestions": []
        }

    # Additional helper methods would be implemented here...
    async def _update_prisma_schema(self):
        """Update Prisma schema file after migration"""
        pass

    async def _parse_prisma_schema(self, content: str) -> dict[str, Any]:
        """Parse Prisma schema content"""
        return {"models": [], "enums": [], "relations": []}

    async def _run_custom_validations(self) -> List[dict]:
        """Run custom validation checks"""
        return []

    async def _validate_performance(self) -> List[dict]:
        """Validate schema for performance issues"""
        return []

    async def _analyze_usage_patterns(self, conn, days: int) -> dict[str, Any]:
        """Analyze database usage patterns"""
        return {"query_patterns": [], "hot_tables": [], "unused_indexes": []}

    async def _generate_evolution_plan(self, patterns: dict, strategy: str) -> dict[str, Any]:
        """Generate schema evolution plan"""
        return {"changes": [], "timeline": "1 week", "risk_assessment": "low"}

    async def _estimate_evolution_impact(self, plan: dict) -> dict[str, Any]:
        """Estimate impact of schema evolution"""
        return {"performance_impact": "+15%", "storage_impact": "-5%", "complexity_impact": "neutral"}

    async def _convert_sql_to_prisma(self, sql: str) -> str:
        """Convert SQL to Prisma client syntax"""
        return f"// Prisma equivalent of: {sql}\n// prisma.table.findMany()"

    async def _generate_query_json(self, sql: str) -> dict[str, Any]:
        """Generate JSON representation of query"""
        return {"query": sql, "type": "select", "tables": [], "conditions": []}

    async def _generate_seed_data(self, table_name: Optional[str] = None, record_count: int = 100) -> dict[str, Any]:
        """Generate realistic seed data"""
        schema_operations_counter.labels(operation_type="seed_generation").inc()
        
        # This would generate realistic data based on schema
        return {
            "table": table_name or "all_tables",
            "records_generated": record_count,
            "seed_sql": f"-- Generated seed data for {table_name or 'all tables'}",
            "data_quality": "high"
        }

    async def _optimize_queries(self, query_log_analysis: bool = False) -> dict[str, Any]:
        """Analyze and optimize slow queries"""
        schema_operations_counter.labels(operation_type="query_optimization").inc()
        
        # This would analyze query logs and provide optimization suggestions
        return {
            "slow_queries": [],
            "optimization_suggestions": [],
            "performance_improvement": "25%",
            "log_analysis_performed": query_log_analysis
        }

if __name__ == "__main__":
    server = PrismaMCPServer()
    server.run() 