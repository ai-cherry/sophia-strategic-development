import asyncio
import logging
import time
from contextlib import asynccontextmanager
from typing import Any, Optional

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator

from backend.core.config_manager import get_config_value

# Structured logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global httpx client with connection pooling
client: Optional[httpx.AsyncClient] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize httpx client pool on startup, close on shutdown"""
    global client
    try:
        # Create httpx client with connection pooling
        limits = httpx.Limits(max_keepalive_connections=20, max_connections=50)
        timeout = httpx.Timeout(30.0, connect=5.0)

        client = httpx.AsyncClient(
            limits=limits,
            timeout=timeout,
            http2=True,  # Enable HTTP/2 for better performance
        )
        logger.info("HTTP client pool initialized")
        yield
    finally:
        if client:
            await client.aclose()
            logger.info("HTTP client pool closed")


app = FastAPI(
    title="Mem0 OpenMemory MCP Server",
    description="Lambda Labs-ready, stateless, OpenMemory MCP server (REST proxy)",
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


class RetryConfig:
    max_retries: int = 3
    initial_delay: float = 1.0
    max_delay: float = 10.0
    exponential_base: float = 2.0


class Mem0RestClient:
    """REST client for Mem0 MCP server (Lambda Labs) with connection pooling"""

    def __init__(self):
        self.api_key = get_config_value("mem0_api_key")
        self.host = get_config_value("mem0_host", "mem0.sophia-lambda.svc")
        self.port = int(get_config_value("mem0_port", "8765"))
        self.base_url = f"http://{self.host}:{self.port}"
        self.headers = (
            {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        )

    async def _execute_with_retry(
        self, method: str, url: str, **kwargs
    ) -> httpx.Response:
        """Execute HTTP request with exponential backoff retry"""
        config = RetryConfig()
        last_exception: Optional[Exception] = None

        for attempt in range(config.max_retries):
            try:
                if not client:
                    raise RuntimeError("HTTP client not initialized")

                response = await client.request(
                    method, url, headers=self.headers, **kwargs
                )
                response.raise_for_status()
                return response

            except (httpx.HTTPStatusError, httpx.RequestError) as e:
                last_exception = e
                if attempt < config.max_retries - 1:
                    delay = min(
                        config.initial_delay * (config.exponential_base**attempt),
                        config.max_delay,
                    )
                    logger.warning(
                        f"Request failed (attempt {attempt + 1}): {e}. Retrying in {delay}s..."
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"All retry attempts failed: {e}")

        if last_exception:
            raise last_exception
        else:
            raise RuntimeError("Request failed with no exception captured")

    async def add_memories(
        self,
        messages: list[dict[str, Any]],
        user_id: str,
        memory_type: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        payload = {
            "user_id": user_id,
            "messages": messages,
            "memory_type": memory_type,
            "metadata": metadata or {},
        }

        start_time = time.time()
        response = await self._execute_with_retry(
            "POST", f"{self.base_url}/add_memories", json=payload
        )
        execution_time = time.time() - start_time

        result = response.json()
        result["execution_time"] = execution_time
        logger.info(f"Memories added for user {user_id} in {execution_time:.2f}s")
        return result

    async def search_memory(
        self, query: str, user_id: str, memory_types: list[str], limit: int = 10
    ) -> dict[str, Any]:
        payload = {
            "query": query,
            "user_id": user_id,
            "memory_types": memory_types,
            "limit": limit,
        }

        start_time = time.time()
        response = await self._execute_with_retry(
            "POST", f"{self.base_url}/search_memory", json=payload
        )
        execution_time = time.time() - start_time

        result = response.json()
        result["execution_time"] = execution_time
        logger.info(f"Memory search completed in {execution_time:.2f}s")
        return result

    async def list_memories(self, user_id: str) -> dict[str, Any]:
        start_time = time.time()
        response = await self._execute_with_retry(
            "GET", f"{self.base_url}/list_memories/{user_id}"
        )
        execution_time = time.time() - start_time

        result = response.json()
        result["execution_time"] = execution_time
        return result

    async def delete_all_memories(self, user_id: str) -> dict[str, Any]:
        start_time = time.time()
        response = await self._execute_with_retry(
            "DELETE", f"{self.base_url}/delete_all_memories/{user_id}"
        )
        execution_time = time.time() - start_time

        result = response.json()
        result["execution_time"] = execution_time
        logger.info(f"All memories deleted for user {user_id}")
        return result


# Initialize client once
mem0_client = Mem0RestClient()


# Models
class MemoryEntry(BaseModel):
    user_id: str = Field(..., description="User ID")
    messages: list[dict[str, Any]] = Field(..., description="Messages to store")
    memory_type: str = Field(
        ..., description="Memory type: working, episodic, semantic, factual"
    )
    metadata: Optional[dict[str, Any]] = Field(None, description="Additional metadata")

    @validator("memory_type")
    def validate_memory_type(cls, v):
        valid_types = ["working", "episodic", "semantic", "factual"]
        if v not in valid_types:
            raise ValueError(f"Memory type must be one of: {', '.join(valid_types)}")
        return v


class MemoryQuery(BaseModel):
    query: str = Field(..., description="Search query")
    user_id: str = Field(..., description="User ID")
    memory_types: Optional[list[str]] = Field(
        None, description="Memory types to search"
    )
    limit: Optional[int] = Field(10, ge=1, le=100, description="Max results")

    @validator("memory_types")
    def validate_memory_types(cls, v):
        if v:
            valid_types = ["working", "episodic", "semantic", "factual"]
            invalid = [t for t in v if t not in valid_types]
            if invalid:
                raise ValueError(f"Invalid memory types: {', '.join(invalid)}")
        return v


@app.get("/health")
async def health() -> dict[str, Any]:
    """Health check endpoint with client pool status"""
    client_status = "healthy" if client and not client.is_closed else "unhealthy"
    return {
        "status": "ok",
        "service": "mem0_openmemory",
        "lambda_labs": True,
        "http_client": client_status,
        "timestamp": time.time(),
    }


@app.post("/add_memories")
async def add_memories(entry: MemoryEntry) -> dict[str, Any]:
    try:
        result = await mem0_client.add_memories(
            messages=entry.messages,
            user_id=entry.user_id,
            memory_type=entry.memory_type,
            metadata=entry.metadata or {},
        )
        return {"success": True, "result": result}
    except httpx.HTTPStatusError as e:
        logger.error(
            f"HTTP error in add_memories: {e.response.status_code} - {e.response.text}"
        )
        raise HTTPException(
            status_code=e.response.status_code,
            detail={"error": str(e), "response": e.response.text},
        )
    except Exception as e:
        logger.error(f"add_memories error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail={"error": str(e), "type": type(e).__name__}
        )


@app.post("/search_memory")
async def search_memory(query: MemoryQuery) -> dict[str, Any]:
    try:
        result = await mem0_client.search_memory(
            query=query.query,
            user_id=query.user_id,
            memory_types=query.memory_types
            or ["working", "episodic", "semantic", "factual"],
            limit=query.limit or 10,
        )
        return {"success": True, "result": result}
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error in search_memory: {e.response.status_code}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail={"error": str(e), "response": e.response.text},
        )
    except Exception as e:
        logger.error(f"search_memory error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail={"error": str(e), "type": type(e).__name__}
        )


@app.get("/list_memories/{user_id}")
async def list_memories(user_id: str) -> dict[str, Any]:
    try:
        result = await mem0_client.list_memories(user_id=user_id)
        return {"success": True, "result": result}
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error in list_memories: {e.response.status_code}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail={"error": str(e), "response": e.response.text},
        )
    except Exception as e:
        logger.error(f"list_memories error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail={"error": str(e), "type": type(e).__name__}
        )


@app.delete("/delete_all_memories/{user_id}")
async def delete_all_memories(user_id: str) -> dict[str, Any]:
    try:
        result = await mem0_client.delete_all_memories(user_id=user_id)
        return {"success": True, "result": result}
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error in delete_all_memories: {e.response.status_code}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail={"error": str(e), "response": e.response.text},
        )
    except Exception as e:
        logger.error(f"delete_all_memories error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail={"error": str(e), "type": type(e).__name__}
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
