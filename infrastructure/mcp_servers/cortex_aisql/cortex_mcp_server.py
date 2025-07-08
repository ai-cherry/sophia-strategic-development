import asyncio
import json
import logging
import time
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator, field_validator
from snowflake.connector.pool import SnowflakePool

from core.config_manager import get_config_value

# Structured logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Connection pool configuration
pool: Any | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize connection pool on startup, close on shutdown"""
    global pool
    try:
        # Create connection pool
        pool = SnowflakePool(
            name="cortex_pool",
            size=20,
            account=get_config_value("snowflake_account"),
            user=get_config_value("snowflake_user"),
            password=get_config_value("snowflake_password"),
            role=get_config_value("snowflake_role", "CORTEX_ROLE"),
            warehouse=get_config_value("snowflake_warehouse", "CORTEX_WH"),
            database=get_config_value("snowflake_database", "SOPHIA_AI"),
            schema=get_config_value("snowflake_schema", "AI_MEMORY"),
        )
        logger.info("Snowflake connection pool initialized")
        yield
    finally:
        if pool:
            pool.close()
            logger.info("Snowflake connection pool closed")


app = FastAPI(
    title="Cortex AISQL MCP Server",
    description="Lambda Labs-ready REST proxy to Snowflake Cortex AI",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Models
class AISQLQuery(BaseModel):
    query: str = Field(..., description="Natural language query")
    context: dict[str, Any] | None = Field(None, description="Additional context")
    model: str = Field("llama3.1-70b", description="Cortex model to use")
    temperature: float = Field(0.7, ge=0, le=1)
    max_tokens: int = Field(2000, ge=100, le=8000)

    @field_validator("query", mode="before")
    @classmethod
    def validate_query(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError("Query must be at least 3 characters")
        if len(v) > 5000:
            raise ValueError("Query too long (max 5000 chars)")
        return v.strip()


class EmbeddingRequest(BaseModel):
    text: str = Field(..., description="Text to embed")
    model: str = Field("e5-base-v2", description="Embedding model")


class RetryConfig:
    max_retries: int = 3
    initial_delay: float = 1.0
    max_delay: float = 10.0
    exponential_base: float = 2.0


@app.get("/health")
async def health() -> dict[str, Any]:
    """Health check endpoint with connection pool status"""
    pool_status = "healthy" if pool and pool._cnx_pool else "unhealthy"
    return {
        "status": "ok",
        "service": "cortex_aisql",
        "lambda_labs": True,
        "connection_pool": pool_status,
        "timestamp": time.time(),
    }


def execute_with_retry(func, *args, **kwargs):
    """Execute function with exponential backoff retry"""
    config = RetryConfig()
    last_exception: Exception | None = None

    for attempt in range(config.max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            if attempt < config.max_retries - 1:
                delay = min(
                    config.initial_delay * (config.exponential_base**attempt),
                    config.max_delay,
                )
                logger.warning(
                    f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s..."
                )
                time.sleep(delay)
            else:
                logger.error(f"All retry attempts failed: {e}")

    if last_exception:
        raise last_exception
    else:
        raise RuntimeError("Retry failed with no exception captured")


def _execute_cortex_complete_sync(
    query: str, model: str, temperature: float, max_tokens: int
) -> Any:
    """Execute Cortex COMPLETE function with connection from pool"""
    if not pool:
        raise RuntimeError("Connection pool not initialized")
    conn = pool.get_connection()
    cs = None
    try:
        cs = conn.cursor()

        # Use Cortex COMPLETE function for natural language to SQL
        cortex_query = f"""
        SELECT SNOWFLAKE.CORTEX.COMPLETE(
            '{model}',
            CONCAT(
                'You are an AI assistant that converts natural language queries to SQL. ',
                'Database: SOPHIA_AI. Schema: AI_MEMORY. ',
                'Available tables: ENRICHED_HUBSPOT_DEALS, ENRICHED_GONG_CALLS, MEMORY_RECORDS. ',
                'Generate only the SQL query, no explanations. ',
                'Query: ', %s
            ),
            {{
                'temperature': {temperature},
                'max_tokens': {max_tokens}
            }}
        ) as generated_sql
        """

        cs.execute(cortex_query, (query,))
        result = cs.fetchone()
        generated_sql = result[0] if result else None

        if not generated_sql:
            raise ValueError("Failed to generate SQL from query")

        # Parse the generated SQL (Cortex returns JSON)
        if isinstance(generated_sql, str):
            try:
                sql_response = json.loads(generated_sql)
                actual_sql = (
                    sql_response.get("choices", [{}])[0].get("text", "").strip()
                )
            except:
                actual_sql = generated_sql.strip()
        else:
            actual_sql = str(generated_sql).strip()

        # Validate generated SQL (basic checks)
        sql_upper = actual_sql.upper()
        if not any(sql_upper.startswith(cmd) for cmd in ["SELECT", "WITH"]):
            raise ValueError(f"Invalid SQL generated: {actual_sql}")

        # Execute the generated SQL
        logger.info(f"Executing generated SQL: {actual_sql}")
        cs.execute(actual_sql)

        cols = [c[0] for c in cs.description] if cs.description else []
        rows = cs.fetchall()

        return {
            "generated_sql": actual_sql,
            "columns": cols,
            "data": [dict(zip(cols, row, strict=False)) for row in rows],
            "row_count": len(rows),
        }

    finally:
        if cs:
            cs.close()
        conn.close()


def _execute_cortex_embedding_sync(text: str, model: str) -> list[float]:
    """Generate embeddings using Cortex EMBED_TEXT_768"""
    if not pool:
        raise RuntimeError("Connection pool not initialized")
    conn = pool.get_connection()
    cs = None
    try:
        cs = conn.cursor()

        # Use Cortex embedding function
        embed_query = f"""
        SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768(
            '{model}',
            %s
        ) as embedding
        """

        cs.execute(embed_query, (text,))
        result = cs.fetchone()

        if not result or not result[0]:
            raise ValueError("Failed to generate embedding")

        # Parse embedding (Cortex returns array as string)
        embedding = json.loads(result[0]) if isinstance(result[0], str) else result[0]

        return embedding

    finally:
        if cs:
            cs.close()
        conn.close()


@app.post("/natural_language_query")
async def natural_language_query(body: AISQLQuery) -> dict[str, Any]:
    """Convert natural language to SQL and execute using Cortex AI"""
    try:
        start_time = time.time()

        # Execute in thread pool with retry
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: execute_with_retry(
                _execute_cortex_complete_sync,
                body.query,
                body.model,
                body.temperature,
                body.max_tokens,
            ),
        )

        execution_time = time.time() - start_time
        logger.info(f"Query executed successfully in {execution_time:.2f}s")

        return {
            "success": True,
            "result": result,
            "execution_time": execution_time,
            "model": body.model,
        }

    except Exception as e:
        logger.error(f"Natural language query error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "type": type(e).__name__,
                "query": body.query[:100] + "..."
                if len(body.query) > 100
                else body.query,
            },
        )


@app.post("/embeddings")
async def generate_embeddings(body: EmbeddingRequest) -> dict[str, Any]:
    """Generate embeddings using Cortex AI"""
    try:
        start_time = time.time()

        # Execute in thread pool with retry
        embedding = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: execute_with_retry(
                _execute_cortex_embedding_sync, body.text, body.model
            ),
        )

        execution_time = time.time() - start_time

        return {
            "success": True,
            "embedding": embedding,
            "dimension": len(embedding),
            "model": body.model,
            "execution_time": execution_time,
        }

    except Exception as e:
        logger.error(f"Embedding generation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail={"error": str(e), "type": type(e).__name__}
        )


@app.get("/models")
async def list_models() -> dict[str, Any]:
    """List available Cortex AI models"""
    return {
        "language_models": [
            "llama3.1-70b",
            "llama3.1-8b",
            "mistral-large2",
            "mixtral-8x7b",
            "gemma-7b",
        ],
        "embedding_models": ["e5-base-v2", "multilingual-e5-large", "gte-large"],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app, host="127.0.0.1", port=8080
    )  # Changed from 0.0.0.0 for security. Use environment variable for production
