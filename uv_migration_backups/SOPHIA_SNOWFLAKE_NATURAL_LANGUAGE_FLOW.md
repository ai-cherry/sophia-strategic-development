# How Natural Language Directs Agents in Sophia's Snowflake Integration

## Overview

The Sophia AI ecosystem uses a sophisticated natural language processing pipeline to direct agents through interactions with Snowflake. This document explains the complete flow from user input to Snowflake operations.

## Natural Language Processing Architecture

### 1. Entry Points for Natural Language Commands

#### A. MCP Servers as Primary Interface
The Model Context Protocol (MCP) servers serve as the primary interface for natural language commands:

```python
# From backend/mcp_servers/snowflake_admin_mcp_server.py
class SnowflakeAdminMCPServer(StandardizedMCPServer):
    def get_available_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "sync_schemas",
                "description": "Synchronize Snowflake schemas with GitHub codebase",
            },
            {
                "name": "execute_query",
                "description": "Execute a SQL query on Snowflake",
            }
        ]
```

#### B. Natural Language Examples
Users can issue commands like:
- "Show me Gong call insights for Acme Corp"
- "Analyze customer sentiment from the last 30 days"
- "Generate a sales performance report for Q4"
- "Find all Slack conversations about product issues"

### 2. Smart AI Service - The Intelligence Layer

The Smart AI Service (`backend/services/smart_ai_service.py`) acts as the intelligent routing layer that processes natural language:

```python
class SmartAIService:
    """
    Enterprise Smart AI Service with intelligent routing
    """
    
    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        # Select optimal strategy based on task type
        strategy = await self.select_strategy(request)
        
        # Route to appropriate LLM provider
        if strategy["provider"] == LLMProvider.PORTKEY:
            response = await self._call_portkey(request, strategy, request_id)
        elif strategy["provider"] == LLMProvider.OPENROUTER:
            response = await self._call_openrouter(request, strategy, request_id)
```

#### Task Type Routing
The service categorizes requests into task types:

```python
class TaskType(str, Enum):
    EXECUTIVE_INSIGHTS = "executive_insights"      # → High-performance models
    COMPETITIVE_ANALYSIS = "competitive_analysis"  # → Specialized analysis models
    FINANCIAL_ANALYSIS = "financial_analysis"      # → Financial-focused models
    CODE_GENERATION = "code_generation"           # → Code-specialized models
    DOCUMENT_ANALYSIS = "document_analysis"       # → Document processing models
```

### 3. Agent Base Classes - The Execution Layer

#### LangGraph Agent Base
The `LangGraphAgentBase` provides the foundation for all agents:

```python
class LangGraphAgentBase(ABC):
    async def process_request(
        self, request: Dict[str, Any], context: Optional[AgentContext] = None
    ) -> Dict[str, Any]:
        """
        Process a request through the agent with performance monitoring
        """
        # Validate and process request
        response = await self._process_request_internal(request, context)
        
        # Add metadata and metrics
        response["metadata"].update({
            "agent_name": self.name,
            "agent_type": self.agent_type.value,
            "capabilities_used": self.capabilities,
            "mcp_integrations": self.mcp_integrations,
        })
        
        return response
```

### 4. Cortex Agent Orchestrator - Multi-Agent Coordination

The `CortexAgentOrchestrator` coordinates multiple agents for complex queries:

```python
class CortexAgentOrchestrator:
    async def execute_complex_workflow(
        self, workflow_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        # Create task plan from natural language request
        task_plan = self._create_task_plan(workflow_request)
        
        # Execute tasks with appropriate agents
        for task in task_plan:
            capable_agents = self._find_capable_agents(task.required_capabilities)
            selected_agent = self._select_optimal_agent(capable_agents, task)
            
            # Execute with Snowflake Cortex capabilities
            task_result = await agent.execute_with_cortex(task)
```

## Natural Language to Snowflake Flow

### Step 1: User Input Processing
When a user asks "Show me customer health insights for Acme Corp":

1. **MCP Server receives command** → Parsed by Snowflake Admin MCP Server
2. **Smart AI Service analyzes intent** → Categorized as `EXECUTIVE_INSIGHTS`
3. **Agent selection** → Routes to appropriate specialized agent

### Step 2: Agent Task Decomposition
The orchestrator breaks down the request:

```python
def _create_task_plan(self, workflow_request: Dict[str, Any]) -> List[AgentTask]:
    if request_type == "customer_health_analysis":
        return [
            AgentTask(
                task_id="gather_customer_data",
                task_type="sql_analysis",
                required_capabilities=[AgentCapability.SQL_ANALYSIS],
            ),
            AgentTask(
                task_id="analyze_communication_sentiment",
                task_type="sentiment_analysis",
                required_capabilities=[AgentCapability.SENTIMENT_ANALYSIS],
            ),
            AgentTask(
                task_id="predict_churn_risk",
                task_type="predictive_modeling",
                required_capabilities=[AgentCapability.PREDICTIVE_MODELING],
            ),
        ]
```

### Step 3: Snowflake Cortex Integration
Agents use Snowflake Cortex functions for AI operations:

```python
# From backend/utils/optimized_snowflake_cortex_service.py
class SnowflakeCortexService:
    async def analyze_with_cortex(self, text: str, analysis_type: str):
        if analysis_type == "sentiment":
            query = f"SELECT SNOWFLAKE.CORTEX.SENTIMENT('{text}') as sentiment"
        elif analysis_type == "summarize":
            query = f"SELECT SNOWFLAKE.CORTEX.SUMMARIZE('{text}') as summary"
        elif analysis_type == "complete":
            query = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('claude-3-haiku', '{text}') as response"
        
        return await self.execute_query(query)
```

### Step 4: AI Memory Integration
The Enhanced AI Memory MCP Server stores and recalls context:

```python
class EnhancedAiMemoryMCPServer:
    async def recall_gong_call_insights(
        self,
        query: str,
        use_cortex_search: bool = True,
    ) -> List[Dict[str, Any]]:
        if use_cortex_search and self.cortex_service:
            # Use Snowflake Cortex vector search
            cortex_results = await self.cortex_service.search_gong_calls_with_ai_memory(
                query_text=query,
                similarity_threshold=0.7,
            )
```

## Natural Language Command Examples

### 1. Executive Query
**User:** "What's our customer churn risk for enterprise clients?"

**Flow:**
1. Smart AI Service → Routes to `EXECUTIVE_INSIGHTS` with GPT-4
2. Cortex Orchestrator → Creates multi-agent workflow
3. Agents execute:
   - SQL Agent: Query enterprise customer data from Snowflake
   - Sentiment Agent: Analyze communication sentiment using Cortex
   - Predictive Agent: Run churn prediction models
4. Results synthesized and returned in natural language

### 2. Sales Intelligence Query
**User:** "Show me all negative sentiment calls from last week"

**Flow:**
1. MCP Server → Interprets as Gong call analysis request
2. AI Memory → Searches stored call insights with sentiment filter
3. Snowflake Query:
```sql
SELECT * FROM STG_TRANSFORMED.STG_GONG_CALLS
WHERE SENTIMENT_SCORE < -0.3
AND CALL_DATETIME >= DATEADD('day', -7, CURRENT_DATE())
```
4. Results formatted with key insights highlighted

### 3. Slack Analysis Query
**User:** "Find customer feedback about our API from Slack"

**Flow:**
1. Smart AI Service → Routes to document analysis
2. AI Memory → Searches Slack conversation memories
3. Cortex Function → Uses SEARCH and SUMMARIZE functions
4. Returns categorized feedback with sentiment analysis

## Key Components in Natural Language Processing

### 1. Intent Recognition
The Smart AI Service uses LLM models to understand user intent:
- Task classification (executive insights, analysis, etc.)
- Entity extraction (customer names, time periods, metrics)
- Context awareness (previous queries, user role)

### 2. Query Translation
Agents translate natural language to Snowflake operations:
- SQL generation for data retrieval
- Cortex function calls for AI analysis
- Vector searches for semantic queries

### 3. Result Synthesis
Multiple agent results are combined:
- Data aggregation from different sources
- Natural language generation for responses
- Visualization recommendations

### 4. Context Persistence
AI Memory maintains conversation context:
- Stores query history and results
- Enables follow-up questions
- Learns from user preferences

## Advanced Natural Language Features

### 1. Multi-Turn Conversations
```python
# Users can have conversations like:
User: "Show me our top customers"
Sophia: "Here are your top 10 customers by revenue..."
User: "What's their sentiment trend?"
Sophia: "Analyzing sentiment trends for these customers..."
```

### 2. Contextual Understanding
The system maintains context across queries:
- References to "them", "it", "those" are resolved
- Time periods carry over ("same period", "compared to last time")
- Filters persist across related queries

### 3. Intelligent Routing
Based on query complexity:
- Simple queries → Direct SQL execution
- Complex analysis → Multi-agent orchestration
- Real-time needs → Optimized Cortex functions
- Historical analysis → AI Memory + Snowflake warehouse

## Performance Optimization

### 1. Caching Strategy
```python
# Agents cache common queries
if self.config["enable_caching"] and cache_key in self.cache:
    if self._is_cache_valid(cache_key):
        return cached_response
```

### 2. Parallel Execution
Multiple agents can work simultaneously:
- Data gathering agents run in parallel
- Analysis agents wait for dependencies
- Results aggregated asynchronously

### 3. Smart Model Selection
The system chooses models based on:
- Query complexity
- Required accuracy
- Cost considerations
- Response time requirements

## Security and Governance

### 1. Query Validation
All natural language queries are validated:
- SQL injection prevention
- Access control checks
- Data governance rules

### 2. Audit Trail
Every query is logged:
- User identity
- Query intent
- Data accessed
- Results returned

### 3. Privacy Protection
Sensitive data handling:
- PII masking in responses
- Role-based access control
- Encryption of cached results

## Future Enhancements

### 1. Advanced NLP Features
- Multi-language support
- Voice command integration
- Gesture and visual input processing

### 2. Predictive Queries
- Anticipate user needs
- Proactive insights
- Automated alert generation

### 3. Enhanced Learning
- Personalized query understanding
- Domain-specific language models
- Continuous improvement from feedback

## Conclusion

The Sophia AI ecosystem provides a sophisticated natural language interface to Snowflake through:

1. **Intelligent Routing**: Smart AI Service directs queries to appropriate models and agents
2. **Multi-Agent Orchestration**: Complex queries are decomposed into coordinated agent tasks
3. **Snowflake Cortex Integration**: Native AI functions provide in-database processing
4. **Context Awareness**: AI Memory maintains conversation state and learns from interactions
5. **Performance Optimization**: Caching, parallel execution, and smart model selection ensure fast responses

This architecture enables business users to interact with complex data using natural language, making advanced analytics accessible to everyone in the organization.
