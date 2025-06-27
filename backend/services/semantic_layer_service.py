# File: backend/services/semantic_layer_service.py

from typing import Dict, List, Any, Optional
from pathlib import Path
import snowflake.connector
from backend.utils.enhanced_snowflake_cortex_service import EnhancedSnowflakeCortexService
from backend.utils.logging import get_logger

logger = get_logger(__name__)

class SemanticLayerService:
    """
    Service for managing Snowflake semantic layer operations.
    Integrates with existing MCP server architecture and Cortex services.
    """
    
    def __init__(self):
        """Initializes the service and the connection to Snowflake."""
        self.snowflake_service = EnhancedSnowflakeCortexService()

    async def _get_connection(self):
        """Gets a snowflake connection."""
        return await self.snowflake_service.get_connection()

    async def _execute_sql_file(self, file_path: str) -> None:
        """Executes a SQL script file."""
        sql_script = Path(file_path).read_text()
        conn = await self._get_connection()
        try:
            with conn.cursor() as cursor:
                for statement in sql_script.split(';'):
                    if statement.strip():
                        cursor.execute(statement)
            logger.info(f"Successfully executed SQL script: {file_path}")
        except Exception as e:
            logger.error(f"Error executing SQL file {file_path}: {e}")
            raise
        finally:
            conn.close()

    async def _execute_query(self, query: str, params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        """Executes a SQL query and returns the results as a list of dicts."""
        conn = await self._get_connection()
        try:
            with conn.cursor(snowflake.connector.DictCursor) as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error executing query: {query} with params {params}: {e}")
            raise
        finally:
            conn.close()

    async def initialize_semantic_layer(self) -> bool:
        """Initialize semantic layer with business vocabulary"""
        try:
            # Execute semantic view creation scripts
            semantic_scripts = [
                'backend/snowflake_setup/semantic_layer_foundation.sql',
                'backend/snowflake_setup/business_vocabulary_definitions.sql',
                'backend/snowflake_setup/entity_relationships.sql'
            ]
            
            for script in semantic_scripts:
                # Check if file exists before trying to execute
                if Path(script).exists():
                    await self._execute_sql_file(script)
                else:
                    logger.warning(f"SQL script not found, skipping: {script}")

            logger.info("Semantic layer initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize semantic layer: {e}")
            return False
    
    async def get_business_entity(self, entity_type: str, entity_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve comprehensive business entity data"""
        entity_queries = {
            'customer': "SELECT * FROM SOPHIA_SEMANTIC.CUSTOMER_360 WHERE customer_id = %s",
            'employee': "SELECT * FROM SOPHIA_SEMANTIC.EMPLOYEE_360 WHERE employee_id = %s",
            'project': "SELECT * FROM SOPHIA_SEMANTIC.PROJECT_360 WHERE project_id = %s"
        }
        
        if entity_type not in entity_queries:
            logger.error(f"Unknown entity type requested: {entity_type}")
            raise ValueError(f"Unknown entity type: {entity_type}")
            
        query = entity_queries[entity_type]
        results = await self._execute_query(query, [entity_id])
        
        if results:
            logger.info(f"Retrieved {entity_type} entity with ID: {entity_id}")
            return results[0]
        else:
            logger.info(f"No {entity_type} entity found with ID: {entity_id}")
            return None
    
    async def search_entities_semantic(self, search_term: str, entity_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Semantic search across business entities"""
        # This will be enhanced with Cortex Search in Phase 2
        base_query = """
        SELECT 'customer' as entity_type, customer_id as id, company_name as name, 
               industry as category, 'Customer entity' as description
        FROM SOPHIA_SEMANTIC.CUSTOMER_360 
        WHERE company_name ILIKE %s OR industry ILIKE %s
        UNION ALL
        SELECT 'employee' as entity_type, employee_id as id, full_name as name,
               department as category, role as description
        FROM SOPHIA_SEMANTIC.EMPLOYEE_360
        WHERE full_name ILIKE %s OR department ILIKE %s OR role ILIKE %s
        """
        
        search_pattern = f"%{search_term}%"
        # The query has 5 placeholders for the search term
        params = [search_pattern] * 5
        results = await self._execute_query(base_query, params)
        
        logger.info(f"Found {len(results)} entities matching '{search_term}'")
        return results

    async def health_check(self) -> Dict[str, Any]:
        """Performs a health check on the semantic layer service."""
        try:
            conn = await self._get_connection()
            conn.close()
            return {"status": "healthy", "message": "Snowflake connection successful."}
        except Exception as e:
            return {"status": "unhealthy", "message": str(e)}

    async def get_dashboard_metrics(self, time_range: str, metrics: List[str]) -> Dict[str, Any]:
        """A placeholder method to get dashboard metrics."""
        # This is a placeholder. A full implementation would query BUSINESS_METRICS view
        # based on time_range and requested metrics.
        logger.info(f"Fetching dashboard metrics for time_range: {time_range} and metrics: {metrics}")
        return {
            "revenue": {"current": 500000, "previous": 450000},
            "satisfaction": {"current": 95, "previous": 92},
            "pipeline": {"current": 2500000, "previous": 2200000},
            "revenue_trend": [
                {"date": "2023-01-01", "value": 300000},
                {"date": "2023-02-01", "value": 350000},
                {"date": "2023-03-01", "value": 450000},
                {"date": "2023-04-01", "value": 500000},
            ]
        } 