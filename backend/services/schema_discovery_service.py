# File: backend/services/schema_discovery_service.py

import asyncio
import yaml
from pathlib import Path
from typing import Dict, Any, List
from jinja2 import Environment, FileSystemLoader

from backend.services.semantic_layer_service import SemanticLayerService
import logging

logger = logging.getLogger(__name__)

class SchemaDiscoveryService:
    """
    Dynamically discovers Snowflake schema and generates/updates the semantic layer.
    """
    def __init__(self, config_path: str = "config/semantic_layer_config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.semantic_service = SemanticLayerService()
        self.jinja_env = Environment(loader=FileSystemLoader('backend/snowflake_setup/templates/'))

    def _load_config(self) -> Dict[str, Any]:
        """Loads the semantic layer configuration from the YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load semantic layer config: {e}", exc_info=True)
            raise

    async def generate_semantic_views(self) -> List[str]:
        """
        Generates the SQL for all semantic views based on the configuration.
        """
        generated_sql_commands = []
        template = self.jinja_env.get_template('semantic_view_template.sql.j2')
        
        entities = self.config.get('entities', [])
        generation_config = self.config.get('generation_config', {})
        
        for entity in entities:
            view_name = f"{generation_config.get('target_schema', 'SOPHIA_SEMANTIC')}.{entity['name'].upper()}{generation_config.get('view_suffix', '_360')}"
            
            # Here you would add logic to query INFORMATION_SCHEMA to get columns, etc.
            # For now, we'll pass the entity config directly to the template.
            context = {
                "view_name": view_name,
                "base_table": entity['base_table'],
                "primary_key": entity['primary_key'],
                "enrichments": entity.get('enrichment_sources', [])
                # In a real scenario, you'd enrich this context with discovered columns
            }
            
            sql_command = template.render(context)
            generated_sql_commands.append(sql_command)
            logger.info(f"Generated SQL for semantic view: {view_name}")

        return generated_sql_commands

    async def apply_semantic_layer(self) -> bool:
        """
        Generates and applies the semantic layer views to Snowflake.
        """
        logger.info("Starting semantic layer application process...")
        try:
            sql_commands = await self.generate_semantic_views()
            
            # Using the existing service to execute the generated SQL
            conn = await self.semantic_service._get_connection()
            with conn.cursor() as cursor:
                for command in sql_commands:
                    logger.info(f"Executing SQL:\n{command}")
                    cursor.execute(command)
            
            conn.close()
            logger.info("Successfully applied semantic layer to Snowflake.")
            return True
        except Exception as e:
            logger.error(f"Failed to apply semantic layer: {e}", exc_info=True)
            return False

async def main():
    logger.info("Running Schema Discovery and Semantic Layer Generation...")
    discovery_service = SchemaDiscoveryService()
    await discovery_service.apply_semantic_layer()
    logger.info("Process completed.")

if __name__ == "__main__":
    asyncio.run(main()) 
