#!/bin/bash
# Snowflake Schema Deployment Script
# Deploy all schemas to Snowflake in correct order

set -e

echo "🚀 Starting Snowflake Schema Deployment"

# Set environment variables
export SNOWFLAKE_ACCOUNT="${SNOWFLAKE_ACCOUNT}"
export SNOWFLAKE_USER="${SNOWFLAKE_USER}"
export SNOWFLAKE_PASSWORD="${SNOWFLAKE_PASSWORD}"
export SNOWFLAKE_DATABASE="SOPHIA_AI"
export SNOWFLAKE_WAREHOUSE="WH_SOPHIA_AI_PROCESSING"

# Schema deployment order (dependencies first)
SCHEMAS=(
    "foundational_knowledge_schema.sql"
    "config_schema.sql"
    "ops_monitoring_schema.sql"
    "ai_memory_schema.sql"
    "payready_core_sql_schema.sql"
    "netsuite_data_schema.sql"
    "property_assets_schema.sql"
    "ai_web_research_schema.sql"
    "gong_data_schema.sql"
    "slack_integration_schema.sql"
    "stg_transformed_schema.sql"
    "ceo_intelligence_schema.sql"
    "enhanced_security_roles.sql"
    "row_level_security.sql"
    "audit_framework.sql"
)

# Deploy each schema
for schema in "${SCHEMAS[@]}"; do
    echo "📊 Deploying $schema..."
    snowsql -f "backend/snowflake_setup/$schema" -o output_format=json
    if [ $? -eq 0 ]; then
        echo "✅ Successfully deployed $schema"
    else
        echo "❌ Failed to deploy $schema"
        exit 1
    fi
done

echo "🎉 All schemas deployed successfully!"
echo "📈 Database architecture is now 100% complete"
