from datetime import UTC, datetime

"""
Lambda GPU Agent Service for Sophia AI
Manages AI agents with JWT authentication and tool execution
"""

import asyncio
import json
import logging
from collections.abc import AsyncGenerator
from datetime import timedelta
from pathlib import Path
from typing import Any

import jwt

# # REMOVED: ModernStack dependency
import yaml
from pydantic import BaseModel
# REMOVED: ModernStack dependency - use UnifiedMemoryServiceV3 import DictCursor

from core.config_manager import get_config_value, get_modern_stack_connection

logger = logging.getLogger(__name__)

# JWT Configuration
JWT_SECRET = get_config_value("jwt_secret", "sophia-ai-cortex-secret")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24


# Agent Request/Response Models
class AgentRequest(BaseModel):
    def _validate_warehouse(self, warehouse_name: str) -> str:
        """Validate warehouse name against whitelist"""
        safe_warehouses = {"AI_SOPHIA_AI_WH", "SOPHIA_AI_WH", "ANALYTICS_WH"}
        if warehouse_name not in safe_warehouses:
            raise ValueError(f"Invalid warehouse name: {warehouse_name}")
        return warehouse_name

    """Request model for agent invocation"""

    prompt: str
    context: dict[str, Any] | None = None
    tools: list[str] | None = None
    max_tokens: int | None = 4096
    temperature: float | None = 0.7
    stream: bool | None = False


class AgentResponse(BaseModel):
    """Response model for agent execution"""

    agent_name: str
    response: str
    tools_used: list[str] = []
    tokens_used: int
    execution_time: float
    metadata: dict[str, Any] = {}


class CortexTool(BaseModel):
    """Tool definition for Cortex agents"""

    name: str
    description: str
    parameters: dict[str, Any]
    handler: str | None = None


class CortexAgentConfig(BaseModel):
    """Configuration for a Cortex agent"""

    name: str
    model: str = "mistral-large"
    temperature: float = 0.7
    max_tokens: int = 4096
    tools: list[CortexTool] = []
    system_prompt: str | None = None
    jwt_required: bool = True


class CortexAgentService:
    """Service for managing Lambda GPU AI agents"""

    def __init__(self):
        self.agents: dict[str, CortexAgentConfig] = {}
        self.cortex_client = None
        self.# REMOVED: ModernStack dependency None
        self._load_agent_configs()

    def _load_agent_configs(self):
        """Load agent configurations from YAML file"""
        config_path = Path(__file__).parent.parent / "config" / "cortex_agents.yaml"

        if config_path.exists():
            with open(config_path) as f:
                configs = yaml.safe_load(f)

            for agent_name, config in configs.get("agents", {}).items():
                # Convert tool definitions
                tools = []
                for tool_dict in config.get("tools", []):
                    tools.append(CortexTool(**tool_dict))

                self.agents[agent_name] = CortexAgentConfig(
                    name=agent_name,
                    model=config.get("model", "mistral-large"),
                    temperature=config.get("temperature", 0.7),
                    max_tokens=config.get("max_tokens", 4096),
                    tools=tools,
                    system_prompt=config.get("system_prompt"),
                    jwt_required=config.get("jwt_required", True),
                )
        else:
            # Default agents if no config file
            self._create_default_agents()

    def _create_default_agents(self):
        """Create default agent configurations"""
        # ModernStack Operations Agent
# REMOVED: ModernStack dependency(
            name="modern_stack_ops",
            model="mistral-large",
            temperature=0.1,
            tools=[
                CortexTool(
                    name="execute_query",
                    description="Execute SQL query on ModernStack",
                    parameters={"query": "string", "warehouse": "string"},
                ),
                CortexTool(
                    name="optimize_query",
                    description="Analyze and optimize SQL query",
                    parameters={"query": "string"},
                ),
                CortexTool(
                    name="manage_schema",
                    description="Create or modify database schema",
                    parameters={"operation": "string", "schema": "object"},
                ),
            ],
            system_prompt="You are a ModernStack database expert. Help users with SQL queries, performance optimization, and schema management.",
        )

        # Semantic Memory Agent
        self.agents["semantic_memory"] = CortexAgentConfig(
            name="semantic_memory",
            model="mistral-7b",
            temperature=0.3,
            tools=[
                CortexTool(
                    name="store_memory",
                    description="Store information with embeddings",
                    parameters={"content": "string", "metadata": "object"},
                ),
                CortexTool(
                    name="recall_memory",
                    description="Retrieve similar memories",
                    parameters={"query": "string", "limit": "integer"},
                ),
                CortexTool(
                    name="search_context",
                    description="Semantic search across all data",
                    parameters={"query": "string", "filters": "object"},
                ),
            ],
            system_prompt="You are a memory management agent. Store and retrieve information using semantic search.",
        )

        # Business Intelligence Agent
        self.agents["business_intelligence"] = CortexAgentConfig(
            name="business_intelligence",
            model="mistral-large",
            temperature=0.2,
            tools=[
                CortexTool(
                    name="analyze_metrics",
                    description="Analyze business metrics",
                    parameters={"metric_type": "string", "time_range": "string"},
                ),
                CortexTool(
                    name="generate_insights",
                    description="Generate AI-powered business insights",
                    parameters={"data_source": "string", "focus_area": "string"},
                ),
                CortexTool(
                    name="forecast_trends",
                    description="Forecast business trends",
                    parameters={"metric": "string", "horizon": "integer"},
                ),
            ],
            system_prompt="You are a business intelligence expert. Analyze data, generate insights, and help with strategic decisions.",
        )

    async def initialize(self):
        """Initialize ModernStack connection and Cortex client"""
        try:
            # Get ModernStack connection
            self.# REMOVED: ModernStack dependency await get_modern_stack_connection()

            # Initialize Cortex client
            self.cortex_client = Cortex(self.modern_stack_conn)

            logger.info("✅ Cortex Agent Service initialized successfully")

        except Exception as e:
            logger.exception(f"❌ Failed to initialize Cortex Agent Service: {e}")
            raise

    def generate_jwt(self, user_id: str, agent_name: str) -> str:
        """Generate JWT token for agent access"""
        payload = {
            "user_id": user_id,
            "agent_name": agent_name,
            "exp": datetime.now(UTC) + timedelta(hours=JWT_EXPIRATION_HOURS),
            "iat": datetime.now(UTC),
        }

        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    def verify_jwt(self, token: str) -> dict[str, Any]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")

    async def invoke_agent(
        self, agent_name: str, request: AgentRequest, jwt_token: str | None = None
    ) -> AgentResponse:
        """Invoke a Cortex agent"""
        start_time = datetime.now()

        # Get agent configuration
        if agent_name not in self.agents:
            raise ValueError(f"Agent '{agent_name}' not found")

        agent_config = self.agents[agent_name]

        # Verify JWT if required
        if agent_config.jwt_required and not jwt_token:
            raise ValueError("JWT token required for this agent")

        if jwt_token:
            try:
                self.verify_jwt(jwt_token)
            except ValueError as e:
                raise ValueError(f"JWT verification failed: {e}")

        # Prepare the prompt with system context
        full_prompt = ""
        if agent_config.system_prompt:
            full_prompt += f"System: {agent_config.system_prompt}\n\n"

        if request.context:
            full_prompt += f"Context: {json.dumps(request.context)}\n\n"

        full_prompt += f"User: {request.prompt}"

        # Execute tools if requested
        tools_used = []
        tool_results = {}

        if request.tools:
            for tool_name in request.tools:
                tool = next(
                    (t for t in agent_config.tools if t.name == tool_name), None
                )
                if tool:
                    tool_result = await self._execute_tool(
                        agent_name, tool, request.context
                    )
                    tool_results[tool_name] = tool_result
                    tools_used.append(tool_name)

        # Add tool results to prompt
        if tool_results:
            full_prompt += f"\n\nTool Results: {json.dumps(tool_results)}"

        # Call Cortex model
        try:
            response = await self._call_cortex_model(
                model=agent_config.model,
                prompt=full_prompt,
                temperature=request.temperature or agent_config.temperature,
                max_tokens=request.max_tokens or agent_config.max_tokens,
                stream=request.stream,
            )

            execution_time = (datetime.now() - start_time).total_seconds()

            return AgentResponse(
                agent_name=agent_name,
                response=response["text"],
                tools_used=tools_used,
                tokens_used=response.get("tokens_used", 0),
                execution_time=execution_time,
                metadata={
                    "model": agent_config.model,
                    "temperature": request.temperature or agent_config.temperature,
                    "tool_results": tool_results,
                },
            )

        except Exception as e:
            logger.exception(f"Error invoking agent {agent_name}: {e}")
            raise

    async def _call_cortex_model(
        self,
        model: str,
        prompt: str,
        temperature: float,
        max_tokens: int,
        stream: bool = False,
    ) -> dict[str, Any]:
        """Call Lambda GPU model"""
        if not self.cortex_client:
            await self.initialize()

        try:
            # Use Cortex Complete function
            query = f"""
            SELECT self.modern_stack.await self.lambda_gpu.complete(
                '{model}',
                '{prompt.replace("'", "''")}',
                {{
                    'temperature': {temperature},
                    'max_tokens': {max_tokens}
                }}
            ) as response
            """

            cursor = self.modern_stack_conn.cursor(DictCursor)
            cursor.execute(query)
            result = cursor.fetchone()

            response_data = json.loads(result["RESPONSE"])

            return {
                "text": response_data.get("choices", [{}])[0].get("text", ""),
                "tokens_used": response_data.get("usage", {}).get("total_tokens", 0),
            }

        except Exception as e:
            logger.exception(f"Cortex model call failed: {e}")
            raise

    async def _execute_tool(
        self, agent_name: str, tool: CortexTool, context: dict[str, Any] | None
    ) -> Any:
        """Execute a tool for an agent"""
        # Tool handlers based on agent and tool name
        tool_handlers = {
            "modern_stack_ops": {
                "execute_query": self._execute_query_tool,
                "optimize_query": self._optimize_query_tool,
                "manage_schema": self._manage_schema_tool,
            },
            "semantic_memory": {
                "store_memory": self._store_memory_tool,
                "recall_memory": self._recall_memory_tool,
                "search_context": self._search_context_tool,
            },
            "business_intelligence": {
                "analyze_metrics": self._analyze_metrics_tool,
                "generate_insights": self._generate_insights_tool,
                "forecast_trends": self._forecast_trends_tool,
            },
        }

        handler = tool_handlers.get(agent_name, {}).get(tool.name)

        if handler:
            return await handler(tool.parameters, context)
        else:
            return f"Tool {tool.name} not implemented"

    # Tool implementations
    async def _execute_query_tool(self, params: dict, context: dict) -> Any:
        """Execute SQL query tool"""
        query = params.get("query", "")
        warehouse = params.get("warehouse", "SOPHIA_AI_WH")

        try:
            cursor = self.modern_stack_conn.cursor(DictCursor)
            cursor.execute("USE WAREHOUSE " + self._validate_warehouse(warehouse))
            cursor.execute(query)

            results = cursor.fetchall()
            return {
                "success": True,
                "row_count": len(results),
                "data": results[:100],  # Limit to 100 rows
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _store_memory_tool(self, params: dict, context: dict) -> Any:
        """Store memory with embeddings"""
        content = params.get("content", "")
        metadata = params.get("metadata", {})

        try:
            # Generate embedding using Cortex
            embedding_query = f"""
            SELECT await self.lambda_gpu.EMBED_TEXT(
                'e5-base-v2',
                '{content.replace("'", "''")}'
            ) as embedding
            """

            cursor = self.modern_stack_conn.cursor(DictCursor)
            cursor.execute(embedding_query, (model, text_content))
            result = cursor.fetchone()

            # Store in vector table
            insert_query = """
            INSERT INTO SOPHIA_AI.CORTEX_VECTORS.embeddings
            (id, source_type, content, embedding, metadata)
            VALUES (?, ?, ?, ?, ?)
            """

            import uuid

            cursor.execute(
                insert_query,
                (
                    str(uuid.uuid4()),
                    "cortex_agent",
                    content,
                    result["EMBEDDING"],
                    json.dumps(metadata),
                ),
            )

            return {"success": True, "message": "Memory stored successfully"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _recall_memory_tool(self, params: dict, context: dict) -> Any:
        """Recall similar memories using Cortex Search"""
        query = params.get("query", "")
        limit = params.get("limit", 10)

        try:
            # Use Cortex Search service
            search_query = f"""
            SELECT content, metadata,
                   VECTOR_DISTANCE(embedding,
                     await self.lambda_gpu.EMBED_TEXT('e5-base-v2', '{query.replace("'", "''")}')
                   ) as distance
            FROM SOPHIA_AI.CORTEX_VECTORS.embeddings
            ORDER BY distance ASC
            LIMIT {limit}
            """

            cursor = self.modern_stack_conn.cursor(DictCursor)
            cursor.execute(search_query, (query_embedding, similarity_threshold, top_k))
            results = cursor.fetchall()

            return {"success": True, "memories": results}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def handle_stream(
        self,
        websocket,
        agent_name: str,
        request: AgentRequest,
        jwt_token: str | None = None,
    ) -> AsyncGenerator[str, None]:
        """Handle streaming responses for WebSocket connections"""
        # Verify agent and JWT
        if agent_name not in self.agents:
            yield json.dumps({"error": f"Agent '{agent_name}' not found"})
            return

        agent_config = self.agents[agent_name]

        if agent_config.jwt_required and not jwt_token:
            yield json.dumps({"error": "JWT token required"})
            return

        # Stream response chunks
        try:
            # This would integrate with Cortex streaming API when available
            response = await self.invoke_agent(agent_name, request, jwt_token)

            # Simulate streaming by chunking response
            chunk_size = 50
            for i in range(0, len(response.response), chunk_size):
                chunk = response.response[i : i + chunk_size]
                yield json.dumps(
                    {"chunk": chunk, "done": i + chunk_size >= len(response.response)}
                )
                await asyncio.sleep(0.1)  # Simulate streaming delay

        except Exception as e:
            yield json.dumps({"error": str(e)})

    async def list_agents(self) -> list[dict[str, Any]]:
        """List all available agents"""
        agents_list = []

        for agent_name, config in self.agents.items():
            agents_list.append(
                {
                    "name": agent_name,
                    "model": config.model,
                    "description": config.system_prompt or "No description",
                    "tools": [
                        {"name": t.name, "description": t.description}
                        for t in config.tools
                    ],
                    "jwt_required": config.jwt_required,
                }
            )

        return agents_list

    # Additional tool implementations would go here...
    async def _optimize_query_tool(self, params: dict, context: dict) -> Any:
        """Optimize SQL query using Cortex"""
        return {"message": "Query optimization not yet implemented"}

    async def _manage_schema_tool(self, params: dict, context: dict) -> Any:
        """Manage database schema"""
        return {"message": "Schema management not yet implemented"}

    async def _search_context_tool(self, params: dict, context: dict) -> Any:
        """Search across all data sources"""
        return {"message": "Context search not yet implemented"}

    async def _analyze_metrics_tool(self, params: dict, context: dict) -> Any:
        """Analyze business metrics"""
        return {"message": "Metrics analysis not yet implemented"}

    async def _generate_insights_tool(self, params: dict, context: dict) -> Any:
        """Generate business insights"""
        return {"message": "Insights generation not yet implemented"}

    async def _forecast_trends_tool(self, params: dict, context: dict) -> Any:
        """Forecast business trends"""
        return {"message": "Trend forecasting not yet implemented"}


# Singleton instance
_cortex_service = None


def get_cortex_service() -> CortexAgentService:
    """Get or create Cortex Agent Service instance"""
    global _cortex_service
    if _cortex_service is None:
        _cortex_service = CortexAgentService()
    return _cortex_service


# FastAPI dependency
async def get_cortex_agent_service() -> CortexAgentService:
    """FastAPI dependency for Cortex Agent Service"""
    service = get_cortex_service()
    if not service.modern_stack_conn:
        await service.initialize()
    return service
