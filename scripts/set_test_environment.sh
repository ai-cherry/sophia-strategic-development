#!/bin/bash
# Set test environment variables for Sophia AI
# This is for local development only - production uses Pulumi ESC

export ENVIRONMENT=prod
export PULUMI_ORG=scoobyjava-org

# Set placeholder Snowflake credentials for testing
# These will make the backend start but Snowflake features will be disabled
export SNOWFLAKE_ACCOUNT=test_account
export SNOWFLAKE_USER=test_user
export SNOWFLAKE_PASSWORD=test_password
export SNOWFLAKE_WAREHOUSE=test_warehouse
export SNOWFLAKE_DATABASE=test_database
export SNOWFLAKE_ROLE=test_role

# Other required environment variables
export OPENAI_API_KEY=${OPENAI_API_KEY:-placeholder}
export ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-placeholder}
export GONG_ACCESS_KEY=${GONG_ACCESS_KEY:-placeholder}
export PINECONE_API_KEY=${PINECONE_API_KEY:-placeholder}

echo "Test environment variables set!"
echo "Note: Snowflake features will be disabled with these test credentials"
echo ""
echo "To use real credentials, configure Pulumi ESC properly" 