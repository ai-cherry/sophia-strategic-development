#!/usr/bin/env python3
"""
Sophia AI - Snowflake Configuration Management CLI Tool
Provides comprehensive Snowflake administration and configuration management
Designed for integration with LangChain agents and MCP architecture
"""

import os
import sys
import json
import argparse
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import snowflake.connector
from snowflake.connector import DictCursor

class SnowflakeConfigManager:
    """
    Comprehensive Snowflake configuration and management system.
    Integrates with Sophia AI's secure credential management via Pulumi ESC.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or os.path.join(project_root, "config", "snowflake_config.json")
        self.connection = None
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load Snowflake configuration from secure sources."""
        # Primary: Environment variables (populated by Pulumi ESC)
        config = {
            "account": os.getenv("SNOWFLAKE_ACCOUNT", "UHDECNO-CVB64222"),
            "user": os.getenv("SNOWFLAKE_USER", "SCOOBYJAVA15"),
            "password": os.getenv("SOPHIA_AI_TOKEN", 
                "eyJraWQiOiI1MDg3NDc2OTQxMyIsImFsZyI6IkVTMjU2In0.eyJwIjoiMTk4NzI5NDc2OjUwODc0NzQ1NDc3IiwiaXNzIjoiU0Y6MTA0OSIsImV4cCI6MTc4MjI4MDQ3OH0.8m-fWI5rvCs6b8bvw1quiM-UzW9uPRxMUmE6VAgOFFylAhRkCzch7ojh7CRLeMdii6DD1Owqap0KoOmyxsW77A"),
            "role": os.getenv("SNOWFLAKE_ROLE", "ACCOUNTADMIN"),
            "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE", "SOPHIA_AI_ANALYTICS_WH"),
            "database": os.getenv("SNOWFLAKE_DATABASE", "SOPHIA_AI_CORE")
        }
        
        # Fallback: Configuration file if exists
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                    # Environment variables take precedence
                    for key, value in file_config.items():
                        if key not in config or not config[key]:
                            config[key] = value
            except Exception as e:
                print(f"Warning: Could not load config file {self.config_file}: {e}")
        
        return config
    
    async def connect(self) -> bool:
        """Establish connection to Snowflake using secure credentials."""
        try:
            print("🔗 Connecting to Snowflake...")
            self.connection = snowflake.connector.connect(
                account=self.config["account"],
                user=self.config["user"],
                password=self.config["password"],
                role=self.config["role"],
                warehouse=self.config["warehouse"],
                database=self.config["database"]
            )
            print("✅ Successfully connected to Snowflake!")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to Snowflake: {e}")
            return False
    
    def execute_query(self, query: str, fetch_results: bool = True) -> Optional[List[Dict]]:
        """Execute a query and return results as dictionaries."""
        if not self.connection:
            raise ConnectionError("No active Snowflake connection")
        
        try:
            cursor = self.connection.cursor(DictCursor)
            
            # Handle multi-statement queries
            if ';' in query and not fetch_results:
                statements = [stmt.strip() for stmt in query.split(';') if stmt.strip()]
                for statement in statements:
                    if statement.upper().startswith(('CREATE', 'ALTER', 'INSERT', 'UPDATE', 'DELETE', 'DROP')):
                        cursor.execute(statement)
                cursor.close()
                return []
            else:
                cursor.execute(query)
                
                if fetch_results:
                    results = cursor.fetchall()
                    cursor.close()
                    return results
                else:
                    cursor.close()
                    return []
                
        except Exception as e:
            print(f"❌ Query execution failed: {e}")
            print(f"Query: {query}")
            raise
    
    async def sync_github_schemas(self) -> Dict[str, Any]:
        """Synchronize Snowflake schemas with GitHub codebase definitions."""
        print("🔄 Synchronizing Snowflake schemas with GitHub codebase...")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "schemas_created": [],
            "schemas_updated": [],
            "tables_created": [],
            "views_created": [],
            "errors": []
        }
        
        try:
            # Read schema definitions from GitHub codebase
            schema_file = os.path.join(project_root, "backend", "snowflake_setup", "ai_memory_schema.sql")
            
            if os.path.exists(schema_file):
                with open(schema_file, 'r') as f:
                    schema_sql = f.read()
                
                # Execute schema creation/updates - split by semicolon and execute separately
                print("📊 Executing schema updates...")
                sql_statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
                
                for i, statement in enumerate(sql_statements):
                    if statement.upper().startswith(('CREATE', 'ALTER', 'INSERT', 'UPDATE', 'DELETE')):
                        try:
                            self.execute_query(statement, fetch_results=False)
                            print(f"✅ Executed statement {i+1}/{len(sql_statements)}")
                        except Exception as e:
                            print(f"⚠️ Warning on statement {i+1}: {e}")
                            # Continue with other statements
                
                results["schemas_updated"].append("ai_memory_schema")
            
            # Create/update Gong and Slack schemas for Estuary integration
            await self._create_estuary_schemas(results)
            
            # Create/update memory system integration
            await self._create_memory_integration(results)
            
            # Create/update semantic layer
            await self._create_semantic_layer(results)
            
        except Exception as e:
            error_msg = f"Schema synchronization error: {str(e)}"
            results["errors"].append(error_msg)
            print(f"❌ {error_msg}")
        
        return results
    
    async def _create_estuary_schemas(self, results: Dict[str, Any]):
        """Create schemas and tables for Estuary data integration."""
        print("🔗 Creating Estuary integration schemas...")
        
        # Gong schema and tables
        gong_schema_sql = """
        CREATE SCHEMA IF NOT EXISTS SOPHIA_GONG_RAW;
        
        CREATE TABLE IF NOT EXISTS SOPHIA_GONG_RAW.gong_calls (
            call_id VARCHAR(255) PRIMARY KEY,
            title VARCHAR(500),
            scheduled_time TIMESTAMP,
            actual_start_time TIMESTAMP,
            actual_end_time TIMESTAMP,
            duration_seconds INTEGER,
            participants VARIANT,
            recording_url VARCHAR(1000),
            transcript_url VARCHAR(1000),
            metadata VARIANT,
            _estuary_ab_id VARCHAR(255),
            _estuary_emitted_at TIMESTAMP,
            _estuary_normalized_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
        );
        
        CREATE TABLE IF NOT EXISTS SOPHIA_GONG_RAW.gong_transcripts (
            transcript_id VARCHAR(255) PRIMARY KEY,
            call_id VARCHAR(255),
            speaker_name VARCHAR(255),
            speaker_role VARCHAR(100),
            text_content TEXT,
            start_time_seconds INTEGER,
            end_time_seconds INTEGER,
            sentiment_score FLOAT,
            keywords VARIANT,
            _estuary_ab_id VARCHAR(255),
            _estuary_emitted_at TIMESTAMP,
            _estuary_normalized_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
        );
        """
        
        # Slack schema and tables
        slack_schema_sql = """
        CREATE SCHEMA IF NOT EXISTS SOPHIA_SLACK_RAW;
        
        CREATE TABLE IF NOT EXISTS SOPHIA_SLACK_RAW.slack_messages (
            message_id VARCHAR(255) PRIMARY KEY,
            channel_id VARCHAR(255),
            channel_name VARCHAR(255),
            user_id VARCHAR(255),
            username VARCHAR(255),
            text_content TEXT,
            timestamp TIMESTAMP,
            thread_ts VARCHAR(255),
            reply_count INTEGER DEFAULT 0,
            reactions VARIANT,
            attachments VARIANT,
            metadata VARIANT,
            _estuary_ab_id VARCHAR(255),
            _estuary_emitted_at TIMESTAMP,
            _estuary_normalized_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
        );
        
        CREATE TABLE IF NOT EXISTS SOPHIA_SLACK_RAW.slack_channels (
            channel_id VARCHAR(255) PRIMARY KEY,
            channel_name VARCHAR(255),
            channel_type VARCHAR(50),
            is_private BOOLEAN,
            member_count INTEGER,
            purpose TEXT,
            topic TEXT,
            _estuary_ab_id VARCHAR(255),
            _estuary_emitted_at TIMESTAMP,
            _estuary_normalized_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
        );
        """
        
        try:
            self.execute_query(gong_schema_sql, fetch_results=False)
            results["schemas_created"].append("SOPHIA_GONG_RAW")
            results["tables_created"].extend(["gong_calls", "gong_transcripts"])
            
            self.execute_query(slack_schema_sql, fetch_results=False)
            results["schemas_created"].append("SOPHIA_SLACK_RAW")
            results["tables_created"].extend(["slack_messages", "slack_channels"])
            
            print("✅ Estuary schemas created successfully")
            
        except Exception as e:
            error_msg = f"Estuary schema creation error: {str(e)}"
            results["errors"].append(error_msg)
            print(f"❌ {error_msg}")
    
    async def _create_memory_integration(self, results: Dict[str, Any]):
        """Create memory system integration views and functions."""
        print("🧠 Creating memory system integration...")
        
        memory_integration_sql = """
        CREATE SCHEMA IF NOT EXISTS SOPHIA_AI_MEMORY;
        
        CREATE OR REPLACE VIEW SOPHIA_AI_MEMORY.unified_conversations AS
        SELECT 
            'gong' as source_type,
            call_id as conversation_id,
            title as conversation_title,
            actual_start_time as conversation_time,
            participants,
            NULL as channel_info,
            text_content as content,
            metadata,
            created_at
        FROM SOPHIA_GONG_RAW.gong_calls c
        LEFT JOIN SOPHIA_GONG_RAW.gong_transcripts t ON c.call_id = t.call_id
        
        UNION ALL
        
        SELECT 
            'slack' as source_type,
            message_id as conversation_id,
            CONCAT('Slack: ', channel_name) as conversation_title,
            timestamp as conversation_time,
            OBJECT_CONSTRUCT('user', username) as participants,
            OBJECT_CONSTRUCT('channel', channel_name, 'channel_id', channel_id) as channel_info,
            text_content as content,
            metadata,
            created_at
        FROM SOPHIA_SLACK_RAW.slack_messages;
        
        CREATE OR REPLACE FUNCTION SOPHIA_AI_MEMORY.extract_conversation_insights(content TEXT)
        RETURNS VARIANT
        LANGUAGE JAVASCRIPT
        AS $$
            // Extract key insights from conversation content
            var insights = {
                word_count: content.split(' ').length,
                has_questions: content.includes('?'),
                has_action_items: content.toLowerCase().includes('action') || content.toLowerCase().includes('todo'),
                sentiment_indicators: {
                    positive: (content.match(/good|great|excellent|amazing|perfect/gi) || []).length,
                    negative: (content.match(/bad|terrible|awful|problem|issue/gi) || []).length
                },
                extracted_at: new Date().toISOString()
            };
            return insights;
        $$;
        """
        
        try:
            self.execute_query(memory_integration_sql, fetch_results=False)
            results["schemas_created"].append("SOPHIA_AI_MEMORY")
            results["views_created"].append("unified_conversations")
            print("✅ Memory integration created successfully")
            
        except Exception as e:
            error_msg = f"Memory integration error: {str(e)}"
            results["errors"].append(error_msg)
            print(f"❌ {error_msg}")
    
    async def _create_semantic_layer(self, results: Dict[str, Any]):
        """Create semantic layer for business intelligence."""
        print("📊 Creating semantic layer...")
        
        semantic_sql = """
        CREATE SCHEMA IF NOT EXISTS SOPHIA_SEMANTIC;
        
        CREATE OR REPLACE VIEW SOPHIA_SEMANTIC.conversation_analytics AS
        SELECT 
            source_type,
            DATE_TRUNC('day', conversation_time) as conversation_date,
            COUNT(*) as conversation_count,
            COUNT(DISTINCT CASE WHEN source_type = 'gong' THEN conversation_id END) as gong_calls,
            COUNT(DISTINCT CASE WHEN source_type = 'slack' THEN conversation_id END) as slack_messages,
            AVG(LENGTH(content)) as avg_content_length
        FROM SOPHIA_AI_MEMORY.unified_conversations
        GROUP BY source_type, DATE_TRUNC('day', conversation_time);
        
        CREATE OR REPLACE VIEW SOPHIA_SEMANTIC.cross_platform_insights AS
        SELECT 
            DATE_TRUNC('week', conversation_time) as week,
            COUNT(DISTINCT CASE WHEN source_type = 'gong' THEN participants END) as unique_gong_participants,
            COUNT(DISTINCT CASE WHEN source_type = 'slack' THEN participants:user END) as unique_slack_users,
            SUM(CASE WHEN content ILIKE '%meeting%' OR content ILIKE '%call%' THEN 1 ELSE 0 END) as meeting_references,
            SUM(CASE WHEN content ILIKE '%action%' OR content ILIKE '%todo%' THEN 1 ELSE 0 END) as action_items
        FROM SOPHIA_AI_MEMORY.unified_conversations
        GROUP BY DATE_TRUNC('week', conversation_time);
        """
        
        try:
            self.execute_query(semantic_sql, fetch_results=False)
            results["schemas_created"].append("SOPHIA_SEMANTIC")
            results["views_created"].extend(["conversation_analytics", "cross_platform_insights"])
            print("✅ Semantic layer created successfully")
            
        except Exception as e:
            error_msg = f"Semantic layer error: {str(e)}"
            results["errors"].append(error_msg)
            print(f"❌ {error_msg}")
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive Snowflake system status."""
        print("📊 Gathering system status...")
        
        status = {
            "timestamp": datetime.now().isoformat(),
            "connection": "connected" if self.connection else "disconnected",
            "current_context": {},
            "databases": [],
            "schemas": [],
            "warehouses": [],
            "tables": [],
            "views": [],
            "functions": [],
            "data_stats": {}
        }
        
        try:
            # Current context
            context_queries = {
                "role": "SELECT CURRENT_ROLE()",
                "warehouse": "SELECT CURRENT_WAREHOUSE()",
                "database": "SELECT CURRENT_DATABASE()",
                "schema": "SELECT CURRENT_SCHEMA()"
            }
            
            for key, query in context_queries.items():
                result = self.execute_query(query)
                if result:
                    status["current_context"][key] = result[0][list(result[0].keys())[0]]
            
            # Databases
            db_result = self.execute_query("SHOW DATABASES")
            if db_result:
                status["databases"] = [row["name"] for row in db_result]
            
            # Schemas in current database
            schema_result = self.execute_query("SHOW SCHEMAS")
            if schema_result:
                status["schemas"] = [row["name"] for row in schema_result]
            
            # Warehouses
            wh_result = self.execute_query("SHOW WAREHOUSES")
            if wh_result:
                status["warehouses"] = [row["name"] for row in wh_result]
            
            # Tables in Sophia AI schemas
            for schema in ["SOPHIA_GONG_RAW", "SOPHIA_SLACK_RAW", "SOPHIA_AI_MEMORY", "SOPHIA_SEMANTIC"]:
                try:
                    table_result = self.execute_query(f"SHOW TABLES IN SCHEMA {schema}")
                    if table_result:
                        status["tables"].extend([f"{schema}.{row['name']}" for row in table_result])
                except:
                    pass  # Schema might not exist yet
            
            # Views
            try:
                view_result = self.execute_query("SHOW VIEWS")
                if view_result:
                    status["views"] = [row["name"] for row in view_result]
            except:
                pass
            
            # Data statistics
            await self._gather_data_stats(status)
            
        except Exception as e:
            print(f"⚠️ Error gathering system status: {e}")
        
        return status
    
    async def _gather_data_stats(self, status: Dict[str, Any]):
        """Gather data statistics for monitoring."""
        try:
            # Count records in key tables
            tables_to_check = [
                "SOPHIA_GONG_RAW.gong_calls",
                "SOPHIA_GONG_RAW.gong_transcripts", 
                "SOPHIA_SLACK_RAW.slack_messages",
                "SOPHIA_SLACK_RAW.slack_channels"
            ]
            
            for table in tables_to_check:
                try:
                    count_result = self.execute_query(f"SELECT COUNT(*) as count FROM {table}")
                    if count_result:
                        status["data_stats"][table] = count_result[0]["COUNT"]
                except:
                    status["data_stats"][table] = "N/A"
                    
        except Exception as e:
            print(f"⚠️ Error gathering data stats: {e}")
    
    async def optimize_performance(self) -> Dict[str, Any]:
        """Optimize Snowflake performance settings."""
        print("⚡ Optimizing Snowflake performance...")
        
        optimization_results = {
            "timestamp": datetime.now().isoformat(),
            "optimizations_applied": [],
            "recommendations": [],
            "errors": []
        }
        
        try:
            # Create clustering keys for large tables
            clustering_sql = """
            ALTER TABLE IF EXISTS SOPHIA_GONG_RAW.gong_calls 
            CLUSTER BY (actual_start_time, call_id);
            
            ALTER TABLE IF EXISTS SOPHIA_SLACK_RAW.slack_messages 
            CLUSTER BY (timestamp, channel_id);
            """
            
            self.execute_query(clustering_sql, fetch_results=False)
            optimization_results["optimizations_applied"].append("Clustering keys added")
            
            # Create search optimization
            search_opt_sql = """
            ALTER TABLE IF EXISTS SOPHIA_GONG_RAW.gong_transcripts
            ADD SEARCH OPTIMIZATION ON EQUALITY(speaker_name), SUBSTRING(text_content);
            
            ALTER TABLE IF EXISTS SOPHIA_SLACK_RAW.slack_messages
            ADD SEARCH OPTIMIZATION ON EQUALITY(username), SUBSTRING(text_content);
            """
            
            self.execute_query(search_opt_sql, fetch_results=False)
            optimization_results["optimizations_applied"].append("Search optimization enabled")
            
            # Warehouse auto-suspend settings
            warehouse_sql = """
            ALTER WAREHOUSE SOPHIA_AI_ANALYTICS_WH SET
            AUTO_SUSPEND = 300
            AUTO_RESUME = TRUE
            RESOURCE_MONITOR = NULL;
            """
            
            self.execute_query(warehouse_sql, fetch_results=False)
            optimization_results["optimizations_applied"].append("Warehouse auto-suspend configured")
            
        except Exception as e:
            error_msg = f"Performance optimization error: {str(e)}"
            optimization_results["errors"].append(error_msg)
            print(f"❌ {error_msg}")
        
        return optimization_results
    
    def close_connection(self):
        """Close Snowflake connection."""
        if self.connection:
            self.connection.close()
            print("🔒 Snowflake connection closed")

class SnowflakeCLI:
    """Command-line interface for Snowflake management."""
    
    def __init__(self):
        self.manager = SnowflakeConfigManager()
    
    async def run_command(self, command: str, **kwargs) -> Dict[str, Any]:
        """Execute a management command."""
        if not await self.manager.connect():
            return {"error": "Failed to connect to Snowflake"}
        
        try:
            if command == "sync":
                return await self.manager.sync_github_schemas()
            elif command == "status":
                return await self.manager.get_system_status()
            elif command == "optimize":
                return await self.manager.optimize_performance()
            else:
                return {"error": f"Unknown command: {command}"}
        finally:
            self.manager.close_connection()

async def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Sophia AI Snowflake Configuration Management")
    parser.add_argument("command", choices=["sync", "status", "optimize"], 
                       help="Command to execute")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--output", help="Output file for results")
    parser.add_argument("--format", choices=["json", "table"], default="json",
                       help="Output format")
    
    args = parser.parse_args()
    
    cli = SnowflakeCLI()
    if args.config:
        cli.manager.config_file = args.config
    
    print(f"🚀 Executing Snowflake {args.command} command...")
    result = await cli.run_command(args.command)
    
    # Output results
    if args.format == "json":
        output = json.dumps(result, indent=2)
    else:
        # Simple table format for status
        if args.command == "status" and "current_context" in result:
            output = f"""
Snowflake System Status
======================
Connection: {result['connection']}
Role: {result['current_context'].get('role', 'N/A')}
Warehouse: {result['current_context'].get('warehouse', 'N/A')}
Database: {result['current_context'].get('database', 'N/A')}

Databases: {len(result['databases'])}
Schemas: {len(result['schemas'])}
Tables: {len(result['tables'])}
Views: {len(result['views'])}

Data Statistics:
{json.dumps(result['data_stats'], indent=2)}
"""
        else:
            output = json.dumps(result, indent=2)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"📄 Results saved to {args.output}")
    else:
        print(output)

if __name__ == "__main__":
    asyncio.run(main())

