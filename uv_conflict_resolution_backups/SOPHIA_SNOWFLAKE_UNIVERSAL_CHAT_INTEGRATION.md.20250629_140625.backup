# Sophia AI: Universal Chat Interface to Snowflake Integration

## Overview

The Sophia AI ecosystem provides a **Universal Chat Interface** that serves as the primary conversational gateway to all Snowflake data and operations. This document explains how the universal chat/search interface connects to and orchestrates Snowflake interactions.

## Universal Chat Service Architecture

### 1. The Universal Chat Service - Primary Entry Point

The Sophia Universal Chat Service (`backend/services/sophia_universal_chat_service.py`) is the central hub for all natural language interactions:

```python
class SophiaUniversalChatService:
    """
    The ultimate Sophia AI conversational platform
    
    Capabilities:
    - Dynamic personality adaptation
    - Blended internal/internet intelligence
    - CEO-level deep research and scraping
    - User-based access control
    - Real-time context awareness
    - Advanced web intelligence
    """
```

### 2. How Universal Chat Connects to Snowflake

#### A. Direct Snowflake Integration
The Universal Chat Service has direct integration with Snowflake through multiple layers:

```python
class SophiaUniversalChatService:
    def __init__(self):
        self.cortex_service = None  # Snowflake Cortex for AI operations
        self.ai_memory_service = None  # AI Memory with Snowflake storage
        self.smart_ai_service = None  # Smart routing for queries
        
        # Schema access mapping - defines which Snowflake schemas users can access
        self.schema_access_map = {
            UserAccessLevel.EMPLOYEE: ["FOUNDATIONAL_KNOWLEDGE", "SLACK_DATA"],
            UserAccessLevel.MANAGER: [
                "FOUNDATIONAL_KNOWLEDGE",
                "SLACK_DATA", 
                "HUBSPOT_DATA",
                "GONG_DATA",
            ],
            UserAccessLevel.EXECUTIVE: [
                "FOUNDATIONAL_KNOWLEDGE",
                "SLACK_DATA",
                "HUBSPOT_DATA",
                "GONG_DATA",
                "PAYREADY_CORE_SQL",
                "NETSUITE_DATA",
                "PROPERTY_ASSETS",
                "AI_WEB_RESEARCH",
            ],
            UserAccessLevel.CEO: [
                # All schemas including CEO_INTELLIGENCE
            ],
        }
```

#### B. Blended Search Architecture
The Universal Chat performs **blended searches** that combine Snowflake data with internet intelligence:

```python
async def _execute_blended_search(self, request: SearchRequest) -> SearchResult:
    """Execute blended search across internal and internet sources"""
    internal_results = []
    internet_results = []
    
    # Execute internal search (Snowflake)
    if request.search_context in [
        SearchContext.INTERNAL_ONLY,
        SearchContext.BLENDED_INTELLIGENCE,
        SearchContext.CEO_DEEP_RESEARCH,
    ]:
        internal_results = await self._execute_internal_search(request)
    
    # Execute internet search (External APIs)
    if request.search_context in [
        SearchContext.INTERNET_ONLY,
        SearchContext.BLENDED_INTELLIGENCE,
        SearchContext.CEO_DEEP_RESEARCH,
    ]:
        internet_results = await self._execute_internet_search(request)
    
    # Synthesize results
    synthesized_content = await self._synthesize_search_results(
        request, internal_results, internet_results
    )
```

### 3. API Routes and Access Points

The Universal Chat is exposed through multiple endpoints (`backend/api/sophia_universal_chat_routes.py`):

#### REST API Endpoints
```python
# Main chat endpoint
@router.post("/api/v1/sophia/chat/message", response_model=ChatMessageResponse)
async def send_chat_message(request: ChatMessageRequest):
    """Send a message to Sophia AI and get intelligent response"""
    
# WebSocket for real-time chat
@router.websocket("/api/v1/sophia/chat/ws/{connection_id}")
async def websocket_chat_endpoint(websocket: WebSocket, connection_id: str):
    """WebSocket endpoint for real-time chat with Sophia AI"""
```

## Natural Language to Snowflake Flow

### Step 1: User Enters Query in Universal Chat
When a user types in the chat interface: "Show me customer health insights for Acme Corp"

### Step 2: Universal Chat Service Processing
```python
async def process_chat_message(
    self, message: str, user_id: str = "ceo", context: Dict[str, Any] = None
) -> SearchResult:
    # 1. Get user profile and permissions
    user_profile = self.user_profiles.get(user_id)
    
    # 2. Determine search context (internal/internet/blended)
    search_context = await self._determine_search_context(message, user_profile)
    
    # 3. Create search request with accessible Snowflake schemas
    search_request = SearchRequest(
        query=message,
        user_profile=user_profile,
        search_context=search_context,
        internal_schemas=user_profile.accessible_schemas,  # Snowflake schemas
    )
    
    # 4. Execute blended search
    result = await self._execute_blended_search(search_request)
```

### Step 3: Snowflake Query Execution
```python
async def _execute_internal_search(self, request: SearchRequest) -> List[Dict[str, Any]]:
    """Execute search across internal Snowflake schemas"""
    results = []
    
    # Search across accessible schemas
    for schema in request.internal_schemas:
        # Use Snowflake Cortex for semantic search
        schema_results = await self.cortex_service.search_with_context(
            query=request.query,
            schema=schema,
            limit=5
        )
```

### Step 4: Snowflake Cortex AI Integration
The Universal Chat leverages Snowflake Cortex for AI operations:

```python
# From backend/utils/optimized_snowflake_cortex_service.py
class SnowflakeCortexService:
    async def search_with_context(self, query: str, schema: str, limit: int):
        # Use Cortex SEARCH function for semantic search
        sql = f"""
        SELECT 
            SNOWFLAKE.CORTEX.SEARCH(
                '{query}',
                content_column,
                'semantic'
            ) as relevance_score,
            *
        FROM {schema}.documents
        ORDER BY relevance_score DESC
        LIMIT {limit}
        """
        return await self.execute_query(sql)
```

## Key Integration Points

### 1. MCP Server Integration
While the Universal Chat is the primary interface, it also integrates with MCP servers for specialized operations:

```python
# Universal Chat can trigger MCP server operations
if "sync snowflake schemas" in message.lower():
    # Route to Snowflake Admin MCP Server
    mcp_result = await self.trigger_mcp_operation(
        server="snowflake_admin",
        tool="sync_schemas"
    )
```

### 2. Agent Orchestration
The Universal Chat orchestrates multiple agents for complex queries:

```python
# Universal Chat coordinates agents
if query_complexity == "high":
    # Use Cortex Agent Orchestrator
    orchestrator = CortexAgentOrchestrator()
    result = await orchestrator.execute_complex_workflow({
        "query": message,
        "user_context": user_profile,
        "data_sources": ["snowflake", "internet"],
    })
```

### 3. AI Memory Integration
The Universal Chat stores and recalls conversation context in Snowflake:

```python
# Store conversation in AI Memory (backed by Snowflake)
await self.ai_memory_service.store_conversation({
    "user_id": user_id,
    "message": message,
    "response": result.content,
    "context": {
        "schemas_accessed": search_request.internal_schemas,
        "search_type": search_context.value,
    }
})
```

## User Experience Flow

### 1. Chat Interface Entry Points

#### Web Application
- Main dashboard chat widget
- Full-screen chat interface
- Embedded chat in various dashboards

#### API Integration
- Slack integration (routes to Universal Chat)
- Mobile app integration
- Third-party tool integration

### 2. Natural Language Understanding

The Universal Chat automatically:
- Detects user intent
- Determines data sources needed
- Routes to appropriate Snowflake schemas
- Applies security/access controls
- Blends internal and external data

### 3. Intelligent Response Generation

```python
async def _synthesize_search_results(
    self,
    request: SearchRequest,
    internal_results: List[Dict[str, Any]],  # Snowflake data
    internet_results: List[Dict[str, Any]],  # External data
) -> str:
    """Synthesize internal and internet search results into coherent response"""
    
    # Create synthesis prompt
    prompt = f"""
As Sophia AI, synthesize the following search results to answer: "{request.query}"

INTERNAL DATA ({len(internal_results)} sources from Snowflake):
{self._format_results_for_synthesis(internal_results)}

INTERNET INTELLIGENCE ({len(internet_results)} sources):
{self._format_results_for_synthesis(internet_results)}

Provide a comprehensive response that:
1. Directly answers the user's question
2. Blends internal company data with external market intelligence
3. Highlights key insights and implications
4. Provides actionable recommendations
"""
    
    # Use SmartAI service for synthesis
    response = await self.smart_ai_service.generate_content(
        prompt=prompt,
        task_type="business_intelligence_synthesis",
    )
```

## Security and Access Control

### 1. User-Based Schema Access
The Universal Chat enforces strict access control to Snowflake schemas:

```python
# Only accessible schemas are queried
accessible_schemas = self.schema_access_map[user_profile.access_level]

# Queries are limited to permitted schemas
for schema in request.internal_schemas:
    if schema not in accessible_schemas:
        raise PermissionError(f"Access denied to schema: {schema}")
```

### 2. Query Validation
All queries are validated before execution:

```python
# SQL injection prevention
sanitized_query = self.sanitize_query(user_query)

# Access control validation
self.validate_user_permissions(user_id, requested_schemas)

# Rate limiting
self.check_rate_limits(user_id)
```

## Real-World Usage Examples

### 1. Executive Dashboard Query
**User:** "What's our revenue trend compared to competitors?"

**Universal Chat Flow:**
1. Detects executive-level query
2. Accesses `PAYREADY_CORE_SQL` schema for revenue data
3. Searches internet for competitor financial data
4. Uses Snowflake Cortex to analyze trends
5. Synthesizes comprehensive response with charts

### 2. Sales Team Query
**User:** "Show me all Gong calls with negative sentiment this week"

**Universal Chat Flow:**
1. Validates access to `GONG_DATA` schema
2. Executes Snowflake query with Cortex SENTIMENT function
3. Retrieves call transcripts and metadata
4. Formats results with actionable insights

### 3. Employee Self-Service Query
**User:** "What's our company vacation policy?"

**Universal Chat Flow:**
1. Searches `FOUNDATIONAL_KNOWLEDGE` schema
2. Retrieves relevant policy documents
3. Uses Cortex SUMMARIZE for concise response
4. Provides direct answer with source links

## WebSocket Real-Time Features

The Universal Chat supports real-time interactions through WebSocket:

```python
@router.websocket("/api/v1/sophia/chat/ws/{connection_id}")
async def websocket_chat_endpoint(websocket: WebSocket, connection_id: str):
    """
    WebSocket endpoint for real-time chat
    
    Features:
    - Typing indicators
    - Live search results
    - Progressive response streaming
    - Multi-user chat rooms
    """
```

This enables:
- Live typing indicators
- Streaming responses as data is retrieved
- Real-time collaboration features
- Push notifications for insights

## Conclusion

The Sophia AI Universal Chat Interface serves as the **primary gateway** to Snowflake data, providing:

1. **Unified Access Point**: Single conversational interface for all data needs
2. **Intelligent Routing**: Automatically determines which Snowflake schemas to query
3. **Blended Intelligence**: Seamlessly combines Snowflake data with internet sources
4. **Security Enforcement**: User-based access control to sensitive schemas
5. **Natural Language Processing**: Converts conversational queries to Snowflake operations
6. **Real-Time Interaction**: WebSocket support for live, streaming responses

The Universal Chat transforms complex Snowflake queries into simple conversations, making enterprise data accessible to users at all technical levels while maintaining security and governance.
