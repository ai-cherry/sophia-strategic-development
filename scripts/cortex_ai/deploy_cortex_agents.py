#!/usr/bin/env python3
"""
🧠 Cortex AI Agents Deployment Script
=====================================

Deploys and configures Cortex AI agents for business intelligence.
"""

import logging
import re

import snowflake.connector

logger = logging.getLogger(__name__)


class CortexAIDeployer:
    """Deploys Cortex AI agents and configurations."""

    def __init__(self, config: dict):
        self.config = config
        self.connection = None

    def connect(self):
        """Connect to Snowflake."""
        self.connection = snowflake.connector.connect(**self.config)
        logger.info("✅ Connected to Snowflake for Cortex AI deployment")

    def _validate_agent_name(self, agent_name: str) -> str:
        """Validate agent name to prevent SQL injection"""
        if not re.match(r'^[A-Z_][A-Z0-9_]*$', agent_name):
            raise ValueError(f"Invalid agent name: {agent_name}")
        return agent_name

    def deploy_business_intelligence_agents(self):
        """Deploy business intelligence Cortex AI agents."""
        cursor = self.connection.cursor()

        agents = [
            {
                "name": "CUSTOMER_INTELLIGENCE_AGENT",
                "description": "Analyzes customer data for insights and predictions",
                "tools": ["CORTEX_SEARCH", "CORTEX_ANALYST", "SQL_EXECUTION"],
            },
            {
                "name": "SALES_OPTIMIZATION_AGENT",
                "description": "Optimizes sales processes and identifies opportunities",
                "tools": ["CORTEX_SEARCH", "CORTEX_ANALYST", "SQL_EXECUTION"],
            },
            {
                "name": "COMPLIANCE_MONITORING_AGENT",
                "description": "Monitors compliance and regulatory requirements",
                "tools": ["CORTEX_SEARCH", "CORTEX_ANALYST", "SQL_EXECUTION"],
            },
        ]

        for agent in agents:
            try:
                # SECURITY FIX: Use validated agent name and parameterized query
                agent_name = self._validate_agent_name(agent['name'])
                cursor.execute(
                    """
                    CREATE OR REPLACE CORTEX AGENT %s
                    DESCRIPTION = %s
                    TOOLS = %s
                    WAREHOUSE = 'AI_COMPUTE_WH'
                    DATABASE = 'SOPHIA_AI_ADVANCED'
                    SCHEMA = 'PROCESSED_AI'
                """,
                    (agent_name, agent['description'], str(agent['tools']))
                )
                logger.info(f"✅ Deployed {agent['name']}")
            except Exception as e:
                logger.warning(f"Could not deploy {agent['name']}: {e}")

        cursor.close()

    def close(self):
        """Close connection."""
        if self.connection:
            self.connection.close()


def main():
    """Main deployment function."""
    config = {
        "account": "UHDECNO-CVB64222",
        "user": "SCOOBYJAVA15",
        "password": "your_password_here",
        "role": "ACCOUNTADMIN",
    }

    deployer = CortexAIDeployer(config)
    try:
        deployer.connect()
        deployer.deploy_business_intelligence_agents()
        logger.info("🎉 Cortex AI agents deployment complete!")
    finally:
        deployer.close()


if __name__ == "__main__":
    main()
