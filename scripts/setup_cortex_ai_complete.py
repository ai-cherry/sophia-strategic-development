#!/usr/bin/env python3
"""
Complete Cortex AI Setup and Testing
Ensures Cortex AI is properly configured for Sophia AI
"""

import json
import logging
from datetime import datetime

import snowflake.connector

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# CORRECT PRODUCTION CONFIGURATION
SNOWFLAKE_CONFIG = {
    "account": "UHDECNO-CVB64222",
    "user": "SCOOBYJAVA15",
    "password": "eyJraWQiOiI1MDg3NDc2OTQxMyIsImFsZyI6IkVTMjU2In0.eyJwIjoiMTk4NzI5NDc2OjUwODc0NzQ1NDc3IiwiaXNzIjoiU0Y6MTA0OSIsImV4cCI6MTc4MjI4MDQ3OH0.8m-fWI5rvCs6b8bvw1quiM-UzW9uPRxMUmE6VAgOFFylAhRkCzch7ojh7CRLeMdii6DD1Owqap0KoOmyxsW77A",
    "role": "ACCOUNTADMIN",
}


class CortexAISetup:
    def __init__(self):
        self.conn = None
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "connection": {},
            "warehouses": {},
            "cortex_functions": {},
            "embeddings": {},
            "search_services": {},
            "recommendations": [],
        }

    def connect(self):
        """Connect to Snowflake"""
        try:
            logger.info("🔗 Connecting to Snowflake...")
            self.conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)

            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT CURRENT_ACCOUNT(), CURRENT_USER(), CURRENT_ROLE(), CURRENT_VERSION()"
            )
            result = cursor.fetchone()

            logger.info("✅ Connected to Snowflake")
            logger.info(f"   Account: {result[0]}")
            logger.info(f"   User: {result[1]}")
            logger.info(f"   Role: {result[2]}")
            logger.info(f"   Version: {result[3]}")

            self.test_results["connection"] = {
                "account": result[0],
                "user": result[1],
                "role": result[2],
                "version": result[3],
                "status": "connected",
            }

            return True

        except Exception as e:
            logger.error(f"❌ Failed to connect: {e}")
            self.test_results["connection"]["error"] = str(e)
            return False

    def create_cortex_warehouse(self):
        """Create dedicated Cortex AI warehouse"""
        logger.info("\n🏭 Setting up Cortex AI warehouse...")

        cursor = self.conn.cursor()

        try:
            # Create Cortex warehouse
            cursor.execute(
                """
                CREATE WAREHOUSE IF NOT EXISTS SOPHIA_AI_CORTEX_WH
                WITH
                    WAREHOUSE_SIZE = 'LARGE'
                    AUTO_SUSPEND = 300
                    AUTO_RESUME = TRUE
                    MIN_CLUSTER_COUNT = 1
                    MAX_CLUSTER_COUNT = 5
                    SCALING_POLICY = 'ECONOMY'
                    COMMENT = 'Sophia AI Cortex AI Warehouse - Optimized for AI workloads'
            """
            )

            logger.info("✅ Created SOPHIA_AI_CORTEX_WH warehouse")

            # Use the warehouse
            cursor.execute("USE WAREHOUSE SOPHIA_AI_CORTEX_WH")
            logger.info("✅ Using SOPHIA_AI_CORTEX_WH for AI operations")

            self.test_results["warehouses"]["cortex_warehouse"] = "created"

        except Exception as e:
            logger.error(f"❌ Failed to create Cortex warehouse: {e}")
            self.test_results["warehouses"]["error"] = str(e)

    def test_cortex_functions(self):
        """Test all Cortex AI functions"""
        logger.info("\n🧠 Testing Cortex AI functions...")

        cursor = self.conn.cursor()

        # Use the production database
        cursor.execute("USE DATABASE SOPHIA_AI_PRODUCTION")
        cursor.execute("USE SCHEMA CORTEX_AI")

        # Test 1: COMPLETE function with different models
        models_to_test = ["mistral-7b", "mixtral-8x7b", "llama2-70b-chat", "gemma-7b"]

        for model in models_to_test:
            try:
                cursor.execute(
                    f"""
                    SELECT SNOWFLAKE.CORTEX.COMPLETE(
                        '{model}',
                        'What is Sophia AI and how does it help businesses?'
                    ) as response
                """
                )
                result = cursor.fetchone()

                if result and result[0]:
                    logger.info(f"✅ Model {model} working!")
                    logger.info(f"   Response preview: {result[0][:100]}...")
                    self.test_results["cortex_functions"][model] = "working"
                else:
                    logger.warning(f"⚠️  Model {model} returned empty response")
                    self.test_results["cortex_functions"][model] = "empty_response"

            except Exception as e:
                logger.error(f"❌ Model {model} failed: {e}")
                self.test_results["cortex_functions"][model] = str(e)

        # Test 2: SENTIMENT function
        try:
            cursor.execute(
                """
                SELECT SNOWFLAKE.CORTEX.SENTIMENT(
                    'This product is amazing! I love using Sophia AI for my business.'
                ) as sentiment
            """
            )
            result = cursor.fetchone()

            if result:
                logger.info(f"✅ SENTIMENT function working! Score: {result[0]}")
                self.test_results["cortex_functions"]["sentiment"] = result[0]

        except Exception as e:
            logger.error(f"❌ SENTIMENT function failed: {e}")
            self.test_results["cortex_functions"]["sentiment_error"] = str(e)

        # Test 3: SUMMARIZE function
        try:
            cursor.execute(
                """
                SELECT SNOWFLAKE.CORTEX.SUMMARIZE(
                    'Sophia AI is an advanced AI orchestrator designed for Pay Ready.
                    It integrates multiple AI agents, connects with business systems like
                    HubSpot and Gong, and provides executive-level insights. The platform
                    uses Snowflake as its central data warehouse and leverages Cortex AI
                    for native AI capabilities.'
                ) as summary
            """
            )
            result = cursor.fetchone()

            if result and result[0]:
                logger.info("✅ SUMMARIZE function working!")
                logger.info(f"   Summary: {result[0]}")
                self.test_results["cortex_functions"]["summarize"] = "working"

        except Exception as e:
            logger.error(f"❌ SUMMARIZE function failed: {e}")
            self.test_results["cortex_functions"]["summarize_error"] = str(e)

    def test_embeddings(self):
        """Test embedding generation"""
        logger.info("\n🔢 Testing embedding functions...")

        cursor = self.conn.cursor()

        # Test embedding models
        embedding_models = ["e5-base-v2", "multilingual-e5-large"]

        for model in embedding_models:
            try:
                cursor.execute(
                    f"""
                    SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768(
                        '{model}',
                        'Sophia AI provides intelligent business insights'
                    ) as embedding
                """
                )
                result = cursor.fetchone()

                if result and result[0]:
                    # Parse the embedding vector
                    embedding = json.loads(result[0])
                    logger.info(f"✅ Embedding model {model} working!")
                    logger.info(f"   Vector dimension: {len(embedding)}")
                    self.test_results["embeddings"][model] = {
                        "status": "working",
                        "dimension": len(embedding),
                    }

            except Exception as e:
                logger.error(f"❌ Embedding model {model} failed: {e}")
                self.test_results["embeddings"][model] = {"error": str(e)}

    def create_cortex_tables(self):
        """Create tables optimized for Cortex AI"""
        logger.info("\n📊 Creating Cortex-optimized tables...")

        cursor = self.conn.cursor()

        # Create AI Memory table with embeddings
        try:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS CORTEX_AI.AI_MEMORY_ENHANCED (
                    memory_id VARCHAR PRIMARY KEY,
                    content TEXT,
                    content_embedding VECTOR(FLOAT, 768),
                    sentiment_score FLOAT,
                    summary TEXT,
                    topics ARRAY,
                    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
                )
            """
            )
            logger.info("✅ Created AI_MEMORY_ENHANCED table")

        except Exception as e:
            logger.error(f"❌ Failed to create AI_MEMORY_ENHANCED: {e}")

        # Create Business Intelligence table
        try:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS CORTEX_AI.BUSINESS_INSIGHTS (
                    insight_id VARCHAR PRIMARY KEY,
                    source_type VARCHAR,  -- gong, hubspot, slack, etc.
                    source_id VARCHAR,
                    insight_text TEXT,
                    insight_embedding VECTOR(FLOAT, 768),
                    confidence_score FLOAT,
                    business_impact VARCHAR,
                    ai_recommendations TEXT,
                    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
                )
            """
            )
            logger.info("✅ Created BUSINESS_INSIGHTS table")

        except Exception as e:
            logger.error(f"❌ Failed to create BUSINESS_INSIGHTS: {e}")

    def create_cortex_procedures(self):
        """Create stored procedures for Cortex AI operations"""
        logger.info("\n🔧 Creating Cortex AI procedures...")

        cursor = self.conn.cursor()

        # Create procedure for AI-powered analysis
        try:
            cursor.execute(
                """
                CREATE OR REPLACE PROCEDURE CORTEX_AI.ANALYZE_BUSINESS_DATA(
                    data_source VARCHAR,
                    analysis_type VARCHAR
                )
                RETURNS VARCHAR
                LANGUAGE SQL
                AS
                $$
                DECLARE
                    result_summary VARCHAR;
                BEGIN
                    -- Placeholder for complex analysis logic
                    result_summary := 'Analysis completed for ' || data_source || ' with type ' || analysis_type;
                    RETURN result_summary;
                END;
                $$
            """
            )
            logger.info("✅ Created ANALYZE_BUSINESS_DATA procedure")

        except Exception as e:
            logger.error(f"❌ Failed to create procedure: {e}")

    def setup_cortex_search(self):
        """Set up Cortex Search Service"""
        logger.info("\n🔍 Setting up Cortex Search Service...")

        cursor = self.conn.cursor()

        try:
            # Create a sample search service
            cursor.execute(
                """
                CREATE OR REPLACE CORTEX SEARCH SERVICE SOPHIA_BUSINESS_SEARCH
                ON ai_memory_enhanced
                ATTRIBUTES content
                WAREHOUSE = SOPHIA_AI_CORTEX_WH
                TARGET_LAG = '1 minute'
                AS (
                    SELECT
                        memory_id,
                        content,
                        sentiment_score,
                        summary
                    FROM CORTEX_AI.AI_MEMORY_ENHANCED
                )
            """
            )
            logger.info("✅ Created SOPHIA_BUSINESS_SEARCH service")
            self.test_results["search_services"]["business_search"] = "created"

        except Exception as e:
            logger.error(f"❌ Failed to create search service: {e}")
            self.test_results["search_services"]["error"] = str(e)

    def generate_recommendations(self):
        """Generate recommendations based on test results"""
        logger.info("\n💡 Generating recommendations...")

        # Check if Cortex functions are working
        working_models = [
            m
            for m, status in self.test_results["cortex_functions"].items()
            if status == "working"
        ]

        if len(working_models) < 2:
            self.test_results["recommendations"].append(
                "Enable more Cortex AI models for better flexibility"
            )

        # Check embeddings
        if not any(self.test_results["embeddings"].values()):
            self.test_results["recommendations"].append(
                "Configure embedding models for vector search capabilities"
            )

        # Check search services
        if "error" in self.test_results["search_services"]:
            self.test_results["recommendations"].append(
                "Review Cortex Search Service syntax and permissions"
            )

    def save_configuration(self):
        """Save Cortex AI configuration for the codebase"""
        config_content = f'''"""
Cortex AI Configuration for Sophia AI
Generated: {datetime.now().isoformat()}
This configuration enables native AI capabilities in Snowflake
"""

CORTEX_CONFIG = {{
    "warehouse": "SOPHIA_AI_CORTEX_WH",
    "database": "SOPHIA_AI_PRODUCTION",
    "schema": "CORTEX_AI",

    "models": {{
        "completion": {{
            "primary": "mistral-7b",
            "alternatives": ["mixtral-8x7b", "llama2-70b-chat", "gemma-7b"]
        }},
        "embeddings": {{
            "primary": "e5-base-v2",
            "dimension": 768
        }}
    }},

    "functions": {{
        "complete": "SNOWFLAKE.CORTEX.COMPLETE",
        "sentiment": "SNOWFLAKE.CORTEX.SENTIMENT",
        "summarize": "SNOWFLAKE.CORTEX.SUMMARIZE",
        "embed": "SNOWFLAKE.CORTEX.EMBED_TEXT_768",
        "extract": "SNOWFLAKE.CORTEX.EXTRACT_ANSWER",
        "translate": "SNOWFLAKE.CORTEX.TRANSLATE"
    }},

    "tables": {{
        "ai_memory": "CORTEX_AI.AI_MEMORY_ENHANCED",
        "business_insights": "CORTEX_AI.BUSINESS_INSIGHTS"
    }},

    "search_services": {{
        "business_search": "SOPHIA_BUSINESS_SEARCH"
    }}
}}

# Test results from setup
TEST_RESULTS = {json.dumps(self.test_results, indent=2)}
'''

        with open("backend/core/cortex_ai_config.py", "w") as f:
            f.write(config_content)

        logger.info(
            "✅ Saved Cortex AI configuration to backend/core/cortex_ai_config.py"
        )

    def generate_report(self):
        """Generate setup report"""
        logger.info("\n" + "=" * 60)
        logger.info("📋 CORTEX AI SETUP REPORT")
        logger.info("=" * 60)

        logger.info("\n✅ Setup completed:")
        logger.info("   Warehouse: SOPHIA_AI_CORTEX_WH")
        logger.info("   Database: SOPHIA_AI_PRODUCTION")
        logger.info("   Schema: CORTEX_AI")

        logger.info("\n🧠 Cortex Functions:")
        for func, status in self.test_results["cortex_functions"].items():
            if status == "working":
                logger.info(f"   ✅ {func}")
            else:
                logger.info(f"   ❌ {func}")

        logger.info("\n🔢 Embeddings:")
        for model, info in self.test_results["embeddings"].items():
            if isinstance(info, dict) and info.get("status") == "working":
                logger.info(f"   ✅ {model} (dimension: {info['dimension']})")
            else:
                logger.info(f"   ❌ {model}")

        if self.test_results["recommendations"]:
            logger.info("\n💡 Recommendations:")
            for rec in self.test_results["recommendations"]:
                logger.info(f"   - {rec}")

    def run(self):
        """Run the complete Cortex AI setup"""
        logger.info("🚀 Starting Cortex AI setup for Sophia AI")
        logger.info("=" * 60)

        if not self.connect():
            return

        # Create warehouse
        self.create_cortex_warehouse()

        # Test functions
        self.test_cortex_functions()
        self.test_embeddings()

        # Create tables and procedures
        self.create_cortex_tables()
        self.create_cortex_procedures()

        # Set up search
        self.setup_cortex_search()

        # Generate recommendations
        self.generate_recommendations()

        # Save configuration
        self.save_configuration()

        # Generate report
        self.generate_report()

        # Close connection
        self.conn.close()

        logger.info("\n✅ Cortex AI setup complete!")


if __name__ == "__main__":
    setup = CortexAISetup()
    setup.run()
