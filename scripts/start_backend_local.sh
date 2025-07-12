#!/bin/bash
# Start Sophia backend with GPU-accelerated memory stack

echo "🚀 Starting Sophia Backend with GPU-accelerated memory..."

# Set environment
export ENVIRONMENT=prod
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Dummy Snowflake credentials for local dev (not using Snowflake anymore)
export SNOWFLAKE_USER=dummy
export SNOWFLAKE_ACCOUNT=dummy
export SNOWFLAKE_PASSWORD=dummy

# Memory stack configuration
export WEAVIATE_URL=http://localhost:8080
export REDIS_URL=redis://localhost:6379
export POSTGRESQL_URL=postgresql://sophia:sophia@localhost:5432/sophia
export LAMBDA_INFERENCE_URL=http://localhost:8001

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Creating..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install missing dependencies
echo "📦 Checking dependencies..."
pip install asyncpg redis weaviate-client psycopg2-binary uvicorn fastapi pydantic langchain langgraph

# Check if backend can be imported
python -c "import backend" 2>/dev/null || {
    echo "⚠️ Backend import failed, fixing PYTHONPATH..."
    export PYTHONPATH="$(pwd):$PYTHONPATH"
}

# Display environment info
echo "Environment: $ENVIRONMENT"
echo "Weaviate: $WEAVIATE_URL"
echo "Redis: $REDIS_URL"
echo "PostgreSQL: $POSTGRESQL_URL"
echo "Lambda Inference: $LAMBDA_INFERENCE_URL"

# Start the backend
cd backend && uvicorn app.unified_chat_backend:app --host 0.0.0.0 --port 8000 --reload 